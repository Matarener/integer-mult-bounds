"""Bounded scalar-cone refits, Chris R with substantial OpenAI Codex, Apache-2.0.
Trace/bitset helpers are credited frozen code; this is not an independent audit.
"""
from pathlib import Path
from collections import Counter
import sys,json,gzip,copy,hashlib,argparse
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'frozen'))
import retiming as t
import audit_core as audit
import tariff as v
need=v.need

def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def canonical(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def hyperplanes(mask):
    bs=t.basis(mask)
    for linear in range(1,1<<len(bs)):
        pivot=(linear&-linear).bit_length()-1
        yield t.span(tuple(bs[j]^(bs[pivot] if linear>>j&1 else 0) for j in range(len(bs)) if j!=pivot))

def prepare(w):
    nodes,where,bill=t.tracing(w);gates={};preds={};fixed=set();edges=[]
    for r,seq in nodes.items():
        before=None
        for addr,kind,p,u in seq:
            scalar=addr[0] in ('A','B','restore') and kind=='climb'
            key=addr if scalar else ('terminal',r) if addr==('end',) else None
            if scalar:gates[key]=u;preds.setdefault(key,[]).append((before,p))
            if kind=='check' and before is not None:fixed.add(before)
            if kind=='climb':edges.append((before,p,key,u))
            before=key
    return nodes,gates,preds,fixed,edges,bill

def cone(gates,preds,fixed,targetkey,target):
    changes={targetkey:target};queue=[targetkey]
    while queue:
        key=queue.pop();cap=changes[key]
        if key in fixed:return None,'fixed-check'
        for pred,mask in preds[key]:
            pmask=changes.get(pred,mask)
            if t.contained(pmask,cap):continue
            if pred is None:return None,'fixed-entrance/native'
            changes[pred]=pmask&cap;queue.append(pred)
    return changes,None

def census(w):
    nodes,gates,preds,fixed,edges,bill=prepare(w);out=[];reject=Counter();total=0
    need(bill==audit.frame_bill(w)[0],'trace versus source auditor')
    for sr,fr in sorted(w['helper_final'].items(),key=lambda x:int(x[0])):
        r=int(sr);seq=nodes[r];last=seq[-2][0];old=t.span(tuple(fr));width=t.rank(old)-t.rank(seq[0][2])
        need(last in gates,'protected last event is not scalar')
        seen=set()
        for new in hyperplanes(old):
            need(new not in seen,'duplicate hyperplane');seen.add(new);total+=1
            need(t.rank(new)==t.rank(old)-1 and t.contained(new,old),'invalid hyperplane')
            if not t.contained(seq[0][2],new):reject['start-terminal']+=1;continue
            if t.contained(gates[last],new):reject['credited-direct-refund']+=1;continue
            changes,reason=cone(gates,preds,fixed,last,gates[last]&new)
            if changes is None:reject[reason]+=1;continue
            changes[('terminal',r)]=new;delta=Counter()
            for pred,p,key,u in edges:
                if pred not in changes and key not in changes:continue
                a=changes.get(pred,p);b=changes.get(key,u)
                need(t.contained(a,b),'propagation lost containment')
                delta[t.rank(u)-t.rank(p)]-=1;delta[t.rank(b)-t.rank(a)]+=1
            delta={str(r):n for r,n in delta.items() if r and n}
            need(width==5 and delta=={'1':-1},'unpriced feasible cone')
            edits=[{'section':k[0],'index':k[1],'old':list(w[k[0]][k[1]][-1]),'new':list(t.basis(m))} for k,m in sorted(changes.items()) if k[0]!='terminal' and gates[k]!=m]
            out.append({'register':r,'old_terminal':fr,'new_terminal':list(t.basis(new)),'edits':edits,'width_before':5,'width_after':4,'local_delta':delta,'owner_debit':{'1':1},'optimistic_complete_delta':{}})
        need(len(seen)==(1<<t.rank(old))-1,'hyperplane completeness')
    return {'total_hyperplanes':total,'rejected':dict(sorted(reject.items())),'candidates':out}

def apply(w,row):
    x=copy.deepcopy(w);r=str(row['register'])
    need(x['helper_final'][r]==row['old_terminal'],'terminal preimage')
    for e in row['edits']:
        need(x[e['section']][e['index']][-1]==e['old'],'scalar frame preimage')
        x[e['section']][e['index']][-1]=e['new']
    x['helper_final'][r]=row['new_terminal'];x['cleanup']=audit.derive_cleanup(x)
    audit.hygiene(x);bill,inventory,*_=audit.frame_bill(x,lagrangian=True)
    need(bill=={1:2481,2:712,3:218,4:109,5:20,8:8},'literal profile')
    need(inventory=={4:1,5:27,6:18,7:53,8:96,9:213},'literal inventory')
    need(x['warps']==w['warps'] and x['cleanup']==w['cleanup'],'native/cleanup preservation')
    return x

def semantics(x):
    need(audit.endpoint_defects(x,audit.forward_rows(x,symbolic_buffers=True))==([],[],[],True),'arbitrary-dirty forward')
    need(audit.endpoint_defects(x,audit.forward_rows(x,dual=True,symbolic_buffers=True),dual=True)==([],[],[],True),'arbitrary-dirty dual')
    need(not audit.boundary_defects(x,audit.transpose(audit.reverse_columns(x,upto_cleanup=True))),'cleanup boundary')

def tariff_check():
    q,pi,mu=v.dual();pi[4]=v.add((1,v.h(1)),(-1,v.h(5)));tight=strict=0
    for cap in (8,16,32,48):
        def rec(w,ns,left):
            if w==10:yield ns,left;return
            for n in range(left//w+1):yield from rec(w+1,ns+[n],left-w*n)
        for ns,left in rec(4,[],cap):
            row=v.add((1,v.h(left)),(-1,mu[cap]),*((-n,pi[w]) for w,n in zip(range(4,10),ns)))
            if row:need(v.interval(row)[0]>0,'tariff dual infeasible');strict+=1
            else:tight+=1
    need((tight,strict)==(12,2539),'tariff domain')
    need(not v.add((1,pi[4]),(-1,pi[5]),(-1,v.h(1))),'exact refund tariff')
    # Frozen aggregate incumbent is dual-tight. Full owner chronology is inherited.
    receipt=read(ROOT/'OWNER-PATTERNS.json');count=0;demand=Counter();bins=Counter()
    for cap,ns,left,n in receipt['patterns']:
        need(sum(w*c for w,c in zip(range(5,10),ns))+left==cap,'incumbent capacity')
        need(not v.reduced(cap,ns,left,pi,mu),'incumbent attainment');count+=n;bins[cap]+=n
        for width,c in zip(range(5,10),ns):demand[width]+=n*c
    need(count==725760 and bins=={8:241920,16:161280,32:161280,48:161280},'incumbent bins')
    need(demand=={5:90720,6:58320,7:171720,8:311040,9:690120},'incumbent demand')
    return {'patterns':tight+strict,'tight':tight,'strict':strict,'refund_debit':'H1 exactly','incumbent_bins':count}

def main():
    p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');p.add_argument('--record',action='store_true');a=p.parse_args()
    for name,digest in read(ROOT/'FROZEN.json').items():need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'frozen source hash')
    result={'tariff':tariff_check(),'providers':{}};witnesses=[]
    for tag in ('base','extra'):
        w=read(ROOT/f'frozen/WORD-{tag}.json.gz');result['providers'][tag]=census(w)
        for row in result['providers'][tag]['candidates']:
            x=apply(w,row)
            if not a.quick:semantics(x)
            witnesses.append({'provider':tag,'register':row['register'],'canonical_sha256':canonical(x)})
    result['witnesses']=witnesses
    if a.record:(ROOT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==read(ROOT/'RESULT.json'),'result mismatch')
    print(json.dumps({'status':'PASS_SCALAR_CONE_BUDGET','hyperplanes_each':13285,'literal_witnesses':len(witnesses),'exact_dirty_replayed':not a.quick,'complete_gain':0},sort_keys=True))
if __name__=='__main__':main()
