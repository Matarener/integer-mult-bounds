#!/usr/bin/env python3
"""Exact late-FULL dirty-query delivery. Sparse evaluator adapted from #3965."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse, copy, hashlib, importlib.util, json
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
WIT='research/p104-native-channel/inputs/LOWRANK-WITNESS.json'
WIT_HASH='0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e'

def need(ok,msg):
    if not ok: raise ValueError(msg)

def load(path):
    def pairs(items):
        out={}
        for k,v in items:
            need(k not in out,'duplicate JSON key: '+k)
            out[k]=v
        return out
    return json.loads(path.read_text(),object_pairs_hook=pairs)

def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))

def span(vs):
    out={0}
    for v in vs: out |= {x^v for x in tuple(out)}
    return frozenset(out)

def add(a,b,c):
    out=dict(a)
    for k,v in b.items():
        out[k]=out.get(k,F(0))+c*v
        if not out[k]: del out[k]
    return out

def replay(word):
    rows={k:{k:F(1)} for k in word['initial_frames']}
    frames={k:span(v) for k,v in word['initial_frames'].items()}
    private=[]; paid=Counter(); counts=Counter(); snapshots={}
    for i,e in enumerate(word['program']):
        op,r=e[:2];counts[op]+=1
        if op=='transport':
            _,r,a,b,n=e;aa,bb=span(a),span(b)
            need(frames[r]==aa,'transport entrance')
            need(aa<=bb or bb<=aa,'non-nested transport')
            need(n==abs(len(a)-len(b)) and len(aa)==2**len(a) and len(bb)==2**len(b),'rank tariff')
            frames[r]=bb;paid[n]+=1
        elif op=='zero':
            need(r=='C' and r not in rows,'fresh owned private')
            rows[r]={};frames[r]=span(e[2]);private.append({'zero':i})
        elif op=='copy':
            _,r,s,f=e;need(r=='C' and not rows[r] and frames[r]==frames[s]==span(f),'copy ownership/zero/common chart')
            rows[r]=dict(rows[s]);private[-1].update(copy=i,source=s,copy_row=dict(rows[s]),frame=list(f))
        elif op=='erase':
            need(r=='C' and frames[r]==span(e[2]),'private erase owner/chart')
            private[-1].update(erase=i,erase_row=dict(rows[r]),end_frame=e[2]);del rows[r];del frames[r]
        elif op in ('half','double'):
            need(frames[r]==span([1<<j for j in range(9)]),'scalar FULL chart')
            c=F(1,2) if op=='half' else F(2)
            rows[r]={k:c*v for k,v in rows[r].items()}
        elif op=='add':
            _,r,s,c,f=e;need(r!=s and frames[r]==frames[s]==span(f),'common-chart addition')
            rows[r]=add(rows[r],rows[s],F(c))
        else:raise ValueError('unknown event')
        if i in (2460,2524,3641,4057):snapshots[i]=copy.deepcopy(rows)
    need(set(rows)==set(word['initial_frames']),'private owner leaked')
    need(all(frames[k]==span(f) for k,f in word['final_frames'].items()),'final frame')
    return rows,dict(paid),dict(counts),private,snapshots

def intervals(word):
    starts=[i for i,e in enumerate(word['program']) if e[0]=='zero']
    ans=[]
    for i in starts:
        j=next(k for k in range(i,len(word['program'])) if word['program'][k][0]=='erase')
        block=word['program'][i:j+1]
        need([e[0] for e in block[:3]]==['zero','copy','transport'],'copy prefix')
        need(all(e[0]=='add' and e[2]=='C' and e[3]==1 for e in block[3:-1]),'private donor only')
        ans.append((i,j,block))
    need(len(ans)==8,'eight intervals')
    return ans

FULL=[1<<i for i in range(9)]
CUT=3641

def sources():
    pins=load(P/'SOURCES.json')
    for row in pins['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'frozen input '+row['path'])
    row=pins['source_exports'][0];path=P/row['path']
    need(hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],'frozen tail export')
    spec=importlib.util.spec_from_file_location('frozen3882',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return load(ROOT/WIT),m

def compile_delivery(word,number=8,mode='good'):
    removed=set();records=[];reads={}
    for a,b,block in intervals(word)[:number]:
        q=block[1][2];ds={e[1] for e in block[3:-1]};u={};clean=[];actual=[]
        removed.update(range(a,b+1))
        for i,e in enumerate(word['program']):
            if e[0]=='add' and e[1] in ds and e[2]==q and i>b:
                need(e[3]==-1 and e[4]==FULL and i<=CUT,'fixed D cleanup');removed.add(i);clean.append(i)
            if e[0]=='add' and e[1].startswith('Y') and e[2] in ds and i>b:
                need(i<CUT,'consumer before delivery cut');u[e[1]]=u.get(e[1],F(0))+F(e[3]);actual.append(i)
        need(len(clean)==len(ds) and len(u)==52 and set(u.values())<={F(-1,4),F(1,4)},'literal cone')
        need(all(e[1]!=q for e in word['program'][b+1:CUT+1] if e[0]!='transport'),'query stays live')
        reads[q]=u;records.append({'query':q,'private_interval':[a,b],'delivery_helpers':sorted(ds),'cleanup_events':clean,'read_events':actual,'target_coefficients':{k:str(v) for k,v in u.items()}})
    out=copy.deepcopy(word);ops=[]
    def insert():
        for j in range(104):ops.append(['transport',f'Y{j}',word['final_frames'][f'Y{j}'],FULL,1])
        if mode=='missing_delivery':return
        for q,u in reads.items():
            ops.extend([['half',q],['half',q]])
            for y,c in u.items():
                if mode=='missing_target' and q=='Q0' and y==next(iter(u)):continue
                ops.append(['add',y,q,int(c*4),FULL])
            if mode!='no_donor_restore':ops.extend([['double',q],['double',q]])
    cut=len(word['program'])-1 if mode=='after_cleanup' else CUT
    for i,e in enumerate(word['program']):
        if i not in removed:ops.append(copy.deepcopy(e))
        if i==cut:insert()
    out['program']=ops
    for j in range(104):out['final_frames'][f'Y{j}']=FULL
    return out,records,sorted(removed)

def continuation(rows,mod,already_full):
    _,A,J,N,B=mod.geometry();ops=mod.program(J,N,B)
    names=[f'X{i}' for i in range(104)]+[f'Y{i}' for i in range(104)]+[f'Q{i}' for i in range(8)]+[f'G{i}' for i in range(32)]+[f'D{i}' for i in range(32)]
    out=[dict(rows[k]) for k in names];frames=[9]*104+([9] if already_full else [8])*104+[9]*72
    need(ops[:104]==[('lift',104+i) for i in range(104)],'tail lift prefix')
    if already_full:ops=ops[104:]
    counts=Counter()
    for e in ops:
        op,r=e[:2];counts[op]+=1
        if op in ('lift','drop'):
            need(frames[r]==(8 if op=='lift' else 9),'tail dimension');frames[r]=9 if op=='lift' else 8
        elif op=='add':
            s,c=e[2:];need(frames[r]==frames[s]==9,'tail common FULL');out[r]=add(out[r],out[s],F(c))
        else:
            need(op in ('half','double') and frames[r]==9,'tail scalar');c=F(1,2) if op=='half' else F(2);out[r]={k:c*v for k,v in out[r].items()}
    return dict(zip(names,out)),frames,dict(counts),J

def scalar_invoice(program):
    # Auditable deliberately unoptimized local lowering: unit ADDs plus paired
    # donor rescaling for each dyadic coefficient; new batched reads are explicit.
    c=Counter()
    for e in program:
        op=e[0]
        if op=='add':
            z=F(e[3]);n,d=abs(z.numerator),z.denominator
            need(d&(d-1)==0,'dyadic coefficient');c['unit_add']+=n;c['half']+=d.bit_length()-1;c['double']+=d.bit_length()-1
        elif op in ('half','double'):c[op]+=1
    return dict(c)

def calculate():
    w,m=sources();base,p0,c0,lives,_=replay(w);newword,records,removed=compile_delivery(w)
    new,p1,c1,l1,_=replay(newword)
    need(new==base and not l1,'all280 rows including72 dirty helpers')
    need(len(removed)==96 and len(records)==8,'eight actual cones')
    # The native event subsequence is literally unchanged except private C drops;
    # inserted lifts are exactly the old Y terminal frame to FULL at the same cut.
    native0=[e for e in w['program'] if e[0]=='transport' and e[1]!='C']
    native1=[e for e in newword['program'] if e[0]=='transport']
    cutindex=next(i for i,e in enumerate(native1) if e==['transport','Y0',w['final_frames']['Y0'],FULL,1])
    lifts=native1[cutindex:cutindex+104]
    need(lifts==[['transport',f'Y{i}',w['final_frames'][f'Y{i}'],FULL,1] for i in range(104)],'exact104 existing terminal lifts')
    need(native1[:cutindex]+native1[cutindex+104:]==native0,'retained native subsequence')
    need(all(e[0]=='add' and e[1].startswith('Q') and e[2].startswith('X') and e[4]==FULL for e in w['program'][CUT+1:]),'only Q/X cleanup after cut')
    need(p1==dict(Counter(p0)+Counter({1:104,7:-8})),'exact rank profile')
    mass0=sum(k*v for k,v in p0.items());mass1=sum(k*v for k,v in p1.items())
    need(mass0==2368 and mass1==2416,'native masses independently recounted')
    expected,fr0,t0,J=continuation(base,m,False);actual,fr1,t1,_=continuation(new,m,True)
    need(actual==expected and fr1==fr0,'exact old3882 endpoint encoding and frame dimensions')
    for i in range(104):
        s=f'Y{i}' if i in J else f'X{i}';need(actual[s]=={f'X{i}':F(1),f'Y{i}':F(1)},'old sum slot')
    need(all(actual[k]=={k:F(1)} for k in actual if k[0] in 'QGD'),'72 dirty returns')
    for life,r in zip(lives,records):
        q=r['query'];v=life['copy_row'];need(v.get(q)==1 and all(k==q or k.startswith('X') for k in v),'actual dirty query source')
        r['query_source_coefficients']={k:str(c) for k,c in v.items() if k!=q}
    need(t1=={'half':104,'add':1248,'double':104,'drop':104},'remaining actual tail invoice')
    combined=mass1+t1['drop'];gap=208*(combined-2312)-10816
    need(combined==2520 and gap==32448,'complete conditional caller gate')
    bscalar=scalar_invoice(w['program']);nscalar=scalar_invoice(newword['program'])
    need(nscalar['unit_add']-bscalar['unit_add']==352 and nscalar['half']-bscalar['half']==16 and nscalar['double']-bscalar['double']==16,'complete scalar difference')
    controls=[]
    for mode in ('missing_delivery','after_cleanup','missing_target','no_donor_restore'):
        bad=compile_delivery(w,mode=mode)[0]
        try:r=replay(bad)[0]
        except (ValueError,KeyError):controls.append(mode);continue
        need(r!=base,'semantic control accepted '+mode);controls.append(mode)
    one=compile_delivery(w,number=1)[0];oneout,onep,_,_,_=replay(one);need(oneout==base and sum(k*v for k,v in onep.items())+104==2569,'Q0 bounded pilot')
    return {'schema_version':1,'scope':'late FULL delivery, exact old endpoint; inherited3882 final physical admission unchanged','baseline_channel_mass':2368,'copy_free_channel_with_lifts_mass':2416,'combined3882_mass':2520,'native_mass_saved':56,'baseline_profile':p0,'replacement_profile_including104_lifts':p1,'replacement_events':len(newword['program']),'replacement_event_counts':c1,'baseline_scalar_lowering':bscalar,'replacement_scalar_lowering':nscalar,'unchanged_tail_except_lifts_counts':t1,'query_records':records,'removed_original_events':removed,'arbitrary_input_roles':280,'restored_dirty_helpers':72,'private_owners':0,'semantic_negative_controls':controls,'two_axis_calls':208,'old_two_axis_gap':44096,'new_two_axis_gap':gap,'new_two_axis_bill':2965248+gap,'two_axis_denominator':2965248,'selected_frontier_changed':False,'supplier_claimed':False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args();result=calculate()
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(encoded(result)==encoded(load(P/'RESULT.json')),'typed receipt mismatch')
    print('PASS_P104_LATE_FULL_DELIVERY inputs=280 dirty=72 copies=0 native_saved=56 combined_mass=2520 gap=32448 controls=4')
if __name__=='__main__':main()
