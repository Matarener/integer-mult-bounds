"""Construct two complete P104 words with certified amplification prices.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retain the P104, gauge, precision and source credits in README and the export.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile

HERE=Path(__file__).resolve().parent


def need(ok,reason):
    if not ok:raise ValueError(reason)


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


def floor_log(r):
    need(r>0,'positive exact logarithm input')
    k=r.numerator.bit_length()-r.denominator.bit_length()
    while Q(2)**k>r:k-=1
    need(Q(2)**k<=r<Q(2)**(k+1),'exact integer logarithm')
    return k


def norms(word,local,nodes=None,count=0):
    rows=[{i:Q(1)} for i in range(word['public']+word['owned_fields'])]
    levels=[Q(0)]*(count+1);peak=Q(1);witness=None
    if nodes:
        for a in nodes['initial'].values():levels[a]=Q(1)
    for i,e in enumerate(word['program']):
        op,r=e[:2]
        if op in ('INIT','CLEAR'):rows[r]={}
        elif op=='SCALE':rows[r]={j:Q(e[-2])*v for j,v in rows[r].items()}
        elif op=='COPY':rows[r]={j:Q(e[-2])*v for j,v in rows[e[2]].items()}
        elif op=='ADD':local.add(rows[r],rows[e[2]],Q(e[-2]))
        value=sum(map(abs,rows[r].values()),Q(0))
        if nodes:
            a=nodes['nodes'][i][0]
            if a:levels[a]=max(levels[a],value)
        if value>peak:
            peak=value;witness={'event':i,'role':r,'coefficients':[[j,str(v)] for j,v in sorted(rows[r].items())]}
    return levels,peak,witness


def verify_price(data,levels,cert):
    cap=Q(cert['peak_cap']);strict=cert.get('strict',False)
    need(cap>=2 and type(strict) is bool,'declared peak contract')
    upper={i:floor_log(cap/v)-int(strict and Q(2)**floor_log(cap/v)==cap/v)
           for i,v in enumerate(levels) if v}
    x,y,m=cert['potentials'],cert['original_dual'],cert['norm_dual']
    need(len(x)==data['count']+1 and x[0]==0 and all(type(v) is int and abs(v)<=128 for v in x),'integer potentials')
    need(cert['norm_nodes']==list(upper) and len(m)==len(upper) and all(type(v) is int and v>=0 for v in m),'nonnegative norm multipliers')
    need(len(y)==len(data['edges']) and all(type(v) is int for v in y),'complete original dual')
    need(all(x[i]<=u for i,u in upper.items()),'all exact epoch norm bounds')
    balance=[0]*len(x);primal=dual=0
    for (a,b,e,w),v in zip(data['edges'],y):
        need(abs(v)<=w,'original dual capacity')
        balance[a]+=v;balance[b]-=v
        primal+=w*abs(e+x[a]-x[b]);dual+=e*v
    for (node,u),v in zip(upper.items(),m):
        balance[node]+=v;balance[0]-=v;dual-=u*v
    need(not any(balance),'full dual conservation')
    need(type(cert['objective']) is int and primal==dual==cert['objective'],'matching constrained primal and dual')
    return primal


def run(emit):
    pin=json.loads((HERE/'SOURCES.json').read_text())['exports'][0]
    archive=HERE/pin['path'];need(sha256(archive.read_bytes()).hexdigest()==pin['sha256'],'exact committed parent export')
    with tempfile.TemporaryDirectory(prefix='p104-amplification-') as directory:
        with tarfile.open(archive) as stream:
            for member in stream.getmembers():
                need(member.isfile() and not member.name.startswith('/') and '..' not in Path(member.name).parts,'regular bounded export member')
            stream.extractall(directory,filter='data')
        parent=Path(directory)/'research/p104-complete-dyadic-gauges'
        for row in json.loads((parent/'SOURCES.json').read_text())['vendored_inputs']:
            need(sha256((parent/row['path']).read_bytes()).hexdigest()==row['sha256'],'retained source '+row['path'])
        c=load(parent/'construct.py','amplification_construct');local=load(parent/'local.py','amplification_local')
        source=json.loads(gzip.decompress((parent/'inputs/WORD.json.gz').read_bytes()))
        data=c.graph(source);levels,source_peak,_=norms(source,local,data,data['count'])
        previous=json.loads((parent/'CERTIFICATE.json').read_text());c.verify_dual(data,previous)
        old_peak=max(Q(2),max(v*Q(2)**x for v,x in zip(levels,previous['potentials'])))
        base=local.replay(source);baseline=sum(w*abs(e) for a,b,e,w in data['edges'])
        old_signs=sum(e[0]=='SCALE' and Q(e[-2])<0 for e in source['program'])
        minimal_signs=sum(data['signs'][a]<0 for a in data['final'].values())
        fixed=base['real_scalar_allowance']-2*baseline-2*old_signs+2*minimal_signs
        bundle=json.loads(gzip.decompress((HERE/'CERTIFICATES.json.gz').read_bytes()))
        need(bundle['schema']=='p104-priced-amplification/1','certificate bundle schema')
        curve=bundle['curve'];need([Q(x['peak_cap']) for x in curve]==[Q(2)**b for b in range(1,17)],'all sixteen declared caps')
        prices=[]
        for row in curve:
            need(row.get('strict',False) is False,'closed curve cap')
            prices.append({'peak':row['peak_cap'],'scalar_allowance':fixed+2*verify_price(data,levels,row)})
        budget=bundle['budget'];selected=budget['selected'];strict=budget['strict']
        selected_price=fixed+2*verify_price(data,levels,selected)
        strict_price=fixed+2*verify_price(data,levels,strict)
        need(selected['strict'] is False and strict['strict'] is True and selected['peak_cap']==strict['peak_cap'],'same strict threshold')
        need(budget['budget']==base['real_scalar_allowance'] and selected_price<=budget['budget']<strict_price,'sharp peak under original scalar budget')
        outputs={};receipts={}
        bound=len(source['program'])+2*source['public']+1
        for name,cert in [('BUDGET',selected),('MINIMUM',curve[0])]:
            word,edits,boundaries,native=c.build(source,data,cert['potentials'],local)
            lowered=[];program=[]
            for i,event in enumerate(word['program']):
                if event[0]=='SCALE' and abs(Q(event[-2]))+1>=2**16:
                    q=Q(event[-2]);need(q.denominator==1,'large scale is an integer unit')
                    power=abs(q.numerator).bit_length()-1
                    need(abs(q)==2**power,'large scale is a power of two')
                    factors=[];sign=-1 if q<0 else 1
                    while power:
                        take=min(15,power);factors.append(['SCALE',event[1],str(sign*2**take),event[-1]])
                        power-=take;sign=1
                    product=Q(1)
                    for factor in factors:product*=Q(factor[-2])
                    need(product==q,'exact legal scale factorization')
                    program.extend(factors);lowered.append([i,event,factors])
                else:program.append(event)
            word['program']=program
            actual=local.replay(word,operation_bound=bound);transpose=local.reverse_columns(word)
            _,peak,witness=norms(word,local)
            need(peak==Q(cert['peak_cap']),'actual attained amplification')
            need(actual['real_scalar_allowance']==fixed+2*cert['objective'],'all actual scalar and boundary charges')
            for key in ('paid','helpers','owned_fields','peak_owned_fields','public_inputs','paid_rank_mass'):
                need(actual[key]==base[key],'retained profile '+key)
            routes=(sum(actual['paid'].values())+2*sum(actual['helpers'].values())+2*len(source['live'])+4*104+4*actual['owned_lifetimes'])*1000
            need(actual['real_scalar_allowance']+routes<10**7,'retained complete local allowance')
            need(sum(abs(Q(v)) for j,v in witness['coefficients'])==peak,'literal attaining row')
            receipts[name]={'local':actual,'transpose':transpose,'instructions':len(word['program']),
                            'strict_operation_bound':bound,'peak':str(peak),'witness':witness,
                            'entry_scales':sum(t=='entry' for t,e in boundaries),'exit_scales':sum(t=='exit' for t,e in boundaries),
                            'lowered_scales':lowered,
                            'local_route_allowance':routes,'combined_allowance':routes+actual['real_scalar_allowance'],
                            'word_sha256':sha256(canonical(word)).hexdigest(),
                            'native_gauge_sha256':sha256(canonical(native)).hexdigest()}
            outputs[name+'-WORD.json.gz']=gzip.compress(canonical(word),mtime=0)
        controls=[]
        bad=deepcopy(selected);bad['objective']-=1
        try:verify_price(data,levels,bad)
        except ValueError as error:controls.append(['false price',str(error)])
        else:raise ValueError('false optimum accepted')
        bad=deepcopy(selected);bad['norm_dual'][0]=-1
        try:verify_price(data,levels,bad)
        except ValueError as error:controls.append(['negative norm multiplier',str(error)])
        else:raise ValueError('negative multiplier accepted')
        bad=deepcopy(selected);bad['peak_cap']='95'
        try:verify_price(data,levels,bad)
        except ValueError as error:controls.append(['unproved lower peak',str(error)])
        else:raise ValueError('lower peak accepted')
        result={'schema':'p104-priced-amplification/1','epoch_norms':[str(v) for v in levels],
                'source_peak':str(source_peak),'minimum_cost_word_peak':str(old_peak),
                'fixed_scalar_term':fixed,'curve':prices,'original_scalar_budget':budget['budget'],
                'strict_lower_peak_scalar_floor':strict_price,'words':receipts,'controls':controls}
        outputs['RESULT.json']=json.dumps(result,sort_keys=True,indent=1).encode()+b'\n'
        if emit:
            for name,raw in outputs.items():(emit/name).write_bytes(raw)
        else:
            for name,raw in outputs.items():
                retained=(HERE/name).read_bytes()
                need(gzip.decompress(retained)==gzip.decompress(raw) if name.endswith('.gz') else retained==raw,'complete retained '+name)
        print('PASS_P104_PRICED_AMPLIFICATION',selected['peak_cap'],selected_price,'absolute minimum',curve[0]['peak_cap'],prices[0]['scalar_allowance'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--emit',type=Path)
    run(p.parse_args().emit)
