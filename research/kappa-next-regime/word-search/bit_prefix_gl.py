#!/usr/bin/env python3
"""Move a helper basis shear through an A prefix to open a nonzero entrance.

For T:q^=p, replace prefix P by T P T and append T, so the new A is A*T.
The D0 compensation is regenerated as D0*T and literal C restores all dirty
values. Equal old D0 columns p,q give a zero new p-column. Every nonzero start
tested is an actual root line from the pinned 111-label rational geometry.

This changes H2's zero-start interface; any positive needs generalized native
admission and a full altered-width owner invoice. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,time
from bit_pair_search import read,canonical,load_checker,flatten,actual_profile,DEFAULT_SOURCE
from bit_joint_frames import Optimizer


def conjugate(events,a,b):
    out=[]
    for e in events:
        d,s=e[1:3]
        if d==b and s==a:
            pairs=[(b,a),(a,b),(b,a)]
        elif s==a:
            pairs=[(d,a),(d,b)]
        elif d==b:
            pairs=[(b,s),(a,s)]
        else:
            pairs=[(d,s)]
        out.extend([['add',u,v,1,1,e[-1]] for u,v in pairs])
    return out


def simplify(events):
    """Cancel equal transvections across only exactly commuting interveners."""
    out=[]
    for e in events:
        d,s=e[1:3]
        cancel=None
        for j in range(len(out)-1,-1,-1):
            f=out[j]
            if f is None:continue
            u,v=f[1:3]
            if (u,v)==(d,s):
                cancel=j;break
            if d==v or s==u:break
        if cancel is None:out.append(e)
        else:out[cancel]=None
    return [e for e in out if e is not None]


def scalar(word,sections,values=None):
    v=word['v'];n=2*v+word['R']
    values=list(values) if values is not None else [1<<r for r in range(n)]
    for name in sections:
        if name=='scatter':
            copies=[values[r] for r in word['ret']]
            for t,row in enumerate(word['scatter']):
                for k in row:values[v+t]^=copies[k]
        else:
            for _,d,ss in word[name]:
                for s in ss:values[d]^=values[s]
    return values


def change(word,p,q,cut):
    es=flatten(word)['A']
    events=conjugate(es[:cut],q,p)+[['add',q,p,1,1,0]]+es[cut:]
    events=simplify(events)
    out=deepcopy(word)
    out['A']=[[e[-1],e[1],[e[2]]] for e in events]
    old_initial=[1<<r for r in range(2*word['v']+word['R'])]
    old_initial[q]^=old_initial[p]
    assert scalar(out,('A',))==scalar(word,('A',),old_initial)
    raw=scalar(out,('A','scatter','B'))
    out['D']=[[0,word['v']+t,[r for r in range(2*word['v'],len(raw)) if raw[word['v']+t]>>r&1]] for t in range(word['v'])]
    assert all(p not in ss for _,d,ss in out['D'])
    out['C']=[[1,d,list(ss)] for sec in ('A','B') for _,d,ss in out[sec] if not word['v']<=d<2*word['v']][::-1]
    wanted=[(1<<r)^(1<<(r-word['v'])) if word['v']<=r<2*word['v'] else 1<<r for r in range(len(raw))]
    assert scalar(out,('D','A','scatter','B','C'))==wanted
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--checker',type=Path,default=DEFAULT_SOURCE/'vendor/xcheck_p.py')
    args=ap.parse_args();word=read(args.word);module=load_checker(args.checker);checker=module.Word(word)
    optimizer=Optimizer(word,checker);flat=flatten(word)['A']
    args.out.mkdir(parents=True,exist_ok=True);stats=Counter();cases=[];found=[]
    original_profile=actual_profile(word,checker)
    for p,q in ((444,473),(473,444),(468,477),(477,468)):
        cuts=sorted({0,len(flat)}|{k for i,e in enumerate(flat) if p in e[1:3] or q in e[1:3] for k in (i,i+1)})
        for cut in cuts:
            nw=change(word,p,q,cut);stats['exact_scalar_prefixes']+=1
            case=dict(p=p,q=q,cut=cut,A_scalar_count=len(nw['A']))
            try:sections,nodes,frames,edges,domains,comps,owned=optimizer.graph(nw)
            except ValueError as exc:
                case['status']='INFEASIBLE_EVEN_WITH_ZERO_START';case['reason']=str(exc);cases.append(case);continue
            first=next((i for i,(sec,k) in enumerate(nodes) if p in sections[sec][k][1:3]),None)
            upper=optimizer.last_bounds[1][first] if first is not None else optimizer.masks[1]
            labels=[i for i in range(word['v']) if upper>>i&1]
            case['upper_root_labels']=labels;case['status']='NO_ROOT_LINE_ENTRANCE' if not labels else 'ROOT_LINES_PRICED'
            case['line_results']=[]
            for label in labels:
                line=next(f for f,ls in enumerate(nw['frames']) if ls==[label])
                tested=deepcopy(nw);tested['start'][p]=line;stats['root_line_tests']+=1
                try:optimized,result=optimizer.optimize(tested)
                except ValueError as exc:
                    case['line_results'].append(dict(label=label,status='INFEASIBLE',reason=str(exc)));continue
                # Geometry and scalar checks independently cover the changed
                # nonzero-start word without asserting the old H2 contract.
                independent=module.Word(optimized)
                paid=actual_profile(optimized,independent)
                assert dict(paid)==result['local_profile']
                assert scalar(optimized,('D','A','scatter','B','C'))==[(1<<r)^(1<<(r-word['v'])) if word['v']<=r<2*word['v'] else 1<<r for r in range(independent.n)]
                case['line_results'].append(dict(label=label,status='EXACT_LOCAL_WORD',optimization=result))
                if result['saving']>0.98:
                    ident=f'prefix-p{p}-q{q}-cut{cut}-line{label}';payload=canonical(optimized)
                    path=args.out/(ident+'.json.gz');path.write_bytes(gzip.compress(payload,mtime=0))
                    rec=dict(id=ident,p=p,q=q,cut=cut,start_line=label,word=path.name,
                             optimization=result,canonical_sha256=sha256(payload).hexdigest(),
                             scope='REQUIRES_GENERALIZED_NONZERO_START_H2_AND_CHANGED_WIDTH_HOSTED_ADMISSION')
                    found.append(rec);(args.out/(ident+'.json')).write_text(json.dumps(rec,sort_keys=True,indent=2)+'\n')
                    print('FOUND',json.dumps(rec,sort_keys=True),flush=True)
            cases.append(case)
            print('CASE',p,q,cut,case['status'],len(labels),flush=True)
    receipt=dict(status='BOUNDED_EQUAL_COMPENSATION_PAIR_PREFIX_CONJUGATION',
                 source_word_sha256=sha256(args.word.read_bytes()).hexdigest(),
                 stats=dict(stats),cases=cases,candidates=found)
    (args.out/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'positive',len(found),flush=True)


if __name__=='__main__':main()
