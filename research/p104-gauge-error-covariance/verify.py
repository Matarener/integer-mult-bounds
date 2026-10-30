#!/usr/bin/env python3
"""Bind homogeneous error covariance to the complete emitted gauge word."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

P=Path(__file__).resolve().parent


def need(ok,message):
    if not ok:raise ValueError(message)


def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m


def authenticate():
    for r in json.loads((P/'SOURCES.json').read_text())['files']:
        if r['usage']=='input':need(sha256((P.parent.parent/r['path']).read_bytes()).hexdigest()==r['sha256'],'source hash')


def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x


def canonical(x):return json.dumps(encode(x),sort_keys=True,separators=(',',':')).encode()


def timeline(base,data,powers,actual):
    gauge={n:F(sign)*F(2)**powers[n] for n,sign in data['signs'].items()}
    normalized=deepcopy(base);physical=deepcopy(base);normalized['program']=[];physical['program']=[]
    emitted=[];sites=set();scales=[];records=[];current=[F(1)]*(base['public']+base['owned_fields'])
    def push(old,new,g,noisy,present,kind,index):
        j=len(scales);normalized['program'].append(old);physical['program'].append(new);scales.append(g)
        if present:emitted.append(new)
        if noisy:need(present,'virtual operation has no physical defect');sites.add(j)
        records.append([kind,index,present,noisy,str(g)])
    entries=exits=omitted=0
    for r,a in data['initial'].items():
        g=gauge[a];current[r]=g
        if g!=1:
            push(['SCALE',r,'1',base['initial'][r]],['SCALE',r,str(g),base['initial'][r]],g,True,True,'entry',r);entries+=1
    for i,(old,(a,b)) in enumerate(zip(base['program'],data['nodes'])):
        op,r=old[:2];new=list(old);present=True;noisy=op in ('MOVE','ADD','SCALE')
        if op=='INIT':current[r]=gauge[a]
        elif op=='CLEAR':current[r]=F(1)
        elif op=='MOVE':need(current[r]==gauge[a],'constant gauge across native map')
        else:
            q=F(old[-2]);ga,gb=gauge[a],gauge[b]
            need(current[r]==(gb if op=='SCALE' else ga),'destination gauge at input')
            if op in ('ADD','COPY'):need(current[old[2]]==gb,'source gauge at input')
            adjusted=q*ga/gb;new[-2]=str(adjusted);current[r]=ga
            need(adjusted*gb==q*ga,'exact local covariance')
            if op=='SCALE' and adjusted==1:present=False;noisy=False;omitted+=1
        push(old,new,current[r],noisy,present,'source',i)
    for r,a in data['final'].items():
        g=gauge[a];need(current[r]==g,'public exit gauge');current[r]=F(1)
        if g!=1:
            push(['SCALE',r,'1',base['final'][r]],['SCALE',r,str(1/g),base['final'][r]],F(1),True,True,'exit',r);exits+=1
    need(all(g==1 for g in current),'unscaled final public and reset-owned fields')
    need(emitted==actual['program'],'all physical source instructions and boundary conversions')
    need(all(physical['program'][j][0]=='SCALE' and F(physical['program'][j][-2])==1 and j not in sites for j,r in enumerate(records) if not r[2]),'only exact identity virtual operations')
    return normalized,physical,sites,scales,records,dict(entry_scales=entries,exit_scales=exits,omitted_physical_scales=omitted)


def rejection(label,fn):
    try:fn()
    except ValueError:return label
    raise ValueError('accepted control: '+label)


def calculate():
    authenticate();source=load('gauge_source',P/'inputs/source-construct.py');local=load('gauge_local',P/'inputs/source-local.py');tr=load('covariant_transfer',P/'transfer.py')
    base=json.loads(gzip.decompress((P/'inputs/base-WORD.json.gz').read_bytes()));actual=json.loads(gzip.decompress((P/'inputs/WORD.json.gz').read_bytes()))
    cert=json.loads((P/'inputs/GAUGES.json').read_text());source_result=json.loads((P/'inputs/source-RESULT.json').read_text());data=source.graph(base)
    need(sha256(source.canonical(data)).hexdigest()==source_result['graph_sha256'],'source graph binding')
    need(sha256(source.canonical(actual)).hexdigest()==source_result['word_sha256'],'source word binding')
    powers,optimum=source.verify_dual(data,cert)
    normal,physical,sites,g,records,counts=timeline(base,data,powers,actual)
    bill=local.replay(actual,operation_bound=len(base['program'])+2*base['public']+1)
    need(encode(bill)==source_result['after'],'full retained local invoice and frame/ownership checks')
    wn,peakn=tr.ideal(normal,sites);wp,peakp=tr.ideal(physical,sites)
    for j in sites:need(wp[j][0]==abs(g[j])*wn[j][0],'local defect magnitude covariance')
    normalized,nw=tr.trace(normal,wn,sites)
    covariant,cw=tr.trace(physical,wn,sites,injections=g,scales=g)
    need(covariant==normalized and cw==nw,'every normalized score, final signed coefficient and witness')
    scores,hashes=tr.transpose(physical,wn,sites,injections=g)
    need(scores==normalized['final_scores'] and hashes==normalized['hashes'],'independent physical transpose')
    ordinary,_=tr.trace(physical,wp,sites)
    need(all(a[0]==b[0] for a,b in zip(ordinary['final_scores'],normalized['final_scores'])),'gauge-invariant final first-order score')
    for row in normalized['final_scores'][base['public']:]:need(row==[0,0,0],'exact reset-owned error return')
    weighted_guards=tr.guards(normalized,base['public']);ordinary_guards=tr.guards(ordinary,base['public'])
    causal=load('causal_bounds',P/'causal.py');causal_cases=[]
    for guard in range(ordinary_guards['final_public'],0,-1):
        case=causal.bound(physical,wp,sites,guard);causal_cases.append(case)
        if max(case['final'][:base['public']])>=1:break
    need(len(causal_cases)>=2 and max(causal_cases[-2]['final'][:base['public']])<1,'least accepted causal guard bracket')
    causal_guard=causal_cases[-2]['guard']
    adversary=load('actual_adversary',P/'adversary.py');adversary_certificate=json.loads((P/'ADVERSARY.json').read_text())
    failures=[adversary.replay(physical,sites,adversary_certificate,causal,t) for t in (0,32)]
    need(all(case['scaled_error']>F(179,100) for case in failures),'displayed sharp-contract failure')
    family_certificate=json.loads((P/'FAMILY-ADVERSARY.json').read_text());family_sites={i for i,e in enumerate(base['program']) if e[0] in ('MOVE','ADD')}
    family=[]
    for extra in (0,32):
        case,defects=adversary.replay(base,family_sites,family_certificate,causal,extra,True);family.append(case)
        values,transport_checks=adversary.transported(physical,records,g,family_certificate['initial'],defects,19+extra)
        ideal_final=tr.execute(base,dict(enumerate(family_certificate['initial'])),{},len(base['program']))
        need(values[family_certificate['target']]-ideal_final[family_certificate['target']]==case['error'],'literal family witness transport')
        need(case['scaled_error']>F(170,100),'invariant family floor')
        case['transported_nonzero_defects']=transport_checks
    need(peakp+causal_cases[-2]['peak']<2**17,'actual field norm plus causal error headroom')
    need(max(causal_cases[-2]['final'][:base['public']])<F(978,1000) and causal_cases[-2]['peak']<27,'displayed exact causal bounds')
    toy_checks=0
    for q in ['1/2','-3/8','2','-1']:
        toyword={'public':2,'owned_fields':1,'program':[['MOVE',0,0,0,False],['ADD',1,0,q,0],['ADD',1,0,str(-F(q)),0],['SCALE',1,'1/2',0],['COPY',2,1,'-1/8',0],['CLEAR',2,0]]}
        tw=[(F(i+1,4),F(1)) for i in range(6)];ts={0,1,2,3}
        for bits in [8,16,32]:
            for guard in [3,7,12]:
                upper=causal.bound(toyword,tw,ts,guard,bits);exact=causal.rational_oracle(toyword,tw,ts,guard)
                need(all(a>=b for a,b in zip(upper['final'],exact)),'causal bound above independent exact oracle');toy_checks+=1
    peak=normalized['peaks'][2];row=nw[2];errors={j:F(1 if v>0 else -1) for j,v in row.items()}
    nv=tr.execute(normal,{},errors,peak['cut'])[peak['role']]
    pv=tr.execute(physical,{},{j:g[j]*v for j,v in errors.items()},peak['cut'])[peak['role']]
    need(nv==peak['value'] and pv/g[peak['cut']-1]==nv,'literal attaining normalized defect fixture')
    controls=[]
    repeated={'public':1,'owned_fields':0,'program':[['MOVE',0,0,0,False],['MOVE',0,0,0,False]]}
    ru=F(1,8);actual_feedback=causal.rational_oracle(repeated,[(F(1),F(1))]*2,{0,1},3)[0]
    need(actual_feedback==2*ru+ru*ru,'two-step actual-input feedback fixture')
    controls.append(rejection('omit local actual-input error feedback',lambda:need(2*ru>=actual_feedback,'feedback is positive')))
    controls.append(rejection('round a defect bound down',lambda:need(F(causal.ceil_fraction(F(1,3))-1)>=F(1,3),'directed bound required')))
    first_entry=next(j for j,r in enumerate(records) if r[0]=='entry')
    response=tr.execute(normal,{},{first_entry:F(1)},len(records))
    controls.append(rejection('omit a charged entry conversion defect',lambda:need(not any(response),'entry error reaches output')))
    omitted=next(j for j,r in enumerate(records) if not r[2] and F(normal['program'][j][-2])!=1)
    q=F(normal['program'][omitted][-2])
    controls.append(rejection('drop the exact normalized SCALE transition',lambda:need(q==1,'changed normalized state')))
    changed=deepcopy(actual);changed['program'].pop(0)
    controls.append(rejection('omit a physical public conversion',lambda:timeline(base,data,powers,changed)))
    U=((F(3,5),F(4,5)),(F(-4,5),F(3,5)));x=(F(0),F(1))
    ux=tuple(sum(a*b for a,b in zip(row,x)) for row in U)
    udx=tuple(sum(a*b for a,b in zip(row,(2*x[0],x[1]))) for row in U)
    controls.append(rejection('nonuniform diagonal need not commute with a unitary native map',
        lambda:need(udx==(2*ux[0],ux[1]),'nonuniform gauge counterexample')))
    weighted_J=normalized['peaks'][0]['value'];weighted_K=normalized['peaks'][1]['value'];guard=weighted_guards['prefix']
    controls.append(rejection('one fewer weighted uniform guard bit',lambda:need(weighted_J+weighted_K<2**(guard-1),'strict guard fails')))
    # A scaled COPY must propagate the source error with its actual coefficient.
    toy={'public':2,'owned_fields':1,'program':[['MOVE',0,0,0,False],['INIT',2,0],['COPY',2,0,'-1/8',0]]}
    need(tr.execute(toy,{},{0:F(2)},3)[2]==F(-1,4),'scaled COPY error fixture')
    controls.append(rejection('unscaled COPY error transition',lambda:need(F(2)==F(-1,4),'scaled copy required')))
    return encode(dict(source_pr=5830,source_head='dd3ffe4c1b391b8d757969a9aa9b2f7c02a32117',counts=counts,
        physical_events=len(actual['program']),normalized_events=len(records),defect_sites=len(sites),coordinates=base['public']+base['owned_fields'],
        timeline_sha256=sha256(canonical(records)).hexdigest(),normalized=normalized,ordinary=ordinary,
        weighted_guards=weighted_guards,ordinary_guards=ordinary_guards,
        causal_final_guard=causal_guard,causal_cases=causal_cases,causal_exact_oracle_checks=toy_checks,
        admissible_19_bit_counterexamples=failures,family_19_bit_counterexamples=family,
        source_scalar_allowance=bill['real_scalar_allowance'],source_exponent_optimum=optimum,
        ideal_peak_for_bounds=dict(normalized=peakn,physical=peakp),rejected_controls=controls,
        limits=['Exact COPY, INIT and CLEAR are premises of this contract.','Completed native maps and gauges are unitary premises.','No norm/cost optimum or new gauge word is claimed.','No physical rounded child or full compiler admission.']))


if __name__=='__main__':
    result=calculate()
    if sys.argv[1:]==['--write']:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(not sys.argv[1:] and result==json.loads((P/'RESULT.json').read_text()),'recorded result')
    print('PASS_P104_GAUGE_ERROR_COVARIANCE')
    print(json.dumps({k:result[k] for k in ['physical_events','normalized_events','defect_sites','weighted_guards','ordinary_guards','causal_final_guard','counts']},sort_keys=True))
