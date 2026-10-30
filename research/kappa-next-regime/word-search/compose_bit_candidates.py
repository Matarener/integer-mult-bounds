#!/usr/bin/env python3
"""Price all nonempty compositions of the three successful last-use rewrites.

This is discovery only; the production artifact should use a fixed literal
applier after independent review, with no optimizer in its dependency path.
"""
from collections import Counter,defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,itertools,json
from bit_pair_search import read,canonical,load_checker,flatten,actual_profile,DEFAULT_SOURCE
from bit_joint_frames import Optimizer


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--candidates',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();w=read(args.word);module=load_checker(DEFAULT_SOURCE/'vendor/xcheck_p.py');checker=module.Word(w)
    optimizer=Optimizer(w,checker);sections=flatten(w)
    base_paid=actual_profile(w,checker);cs=[read(args.candidates/f'A-permanent-{i}.json') for i in (8,34,42)]
    args.out.mkdir(parents=True,exist_ok=True);results=[]
    for count in range(1,len(cs)+1):
        for subset in itertools.combinations(cs,count):
            inserts=defaultdict(list);drops=set();ids=[]
            for c in subset:
                inserts[c['lo']].append([0,c['a'],[c['b']]])
                ds={p['drop'] for p in c['chosen']};assert not drops&ds;drops|=ds;ids.append(c['index'])
            nw=deepcopy(w);nw['A']=[]
            for i in range(len(sections['A'])+1):
                nw['A'].extend(inserts[i])
                if i<len(sections['A']) and i not in drops:
                    e=sections['A'][i];nw['A'].append([e[-1],e[1],[e[2]]])
            nw['C']=[[1,d,list(ss)] for sec in ('A','B') for _,d,ss in nw[sec] if not w['v']<=d<2*w['v']][::-1]
            out,result=optimizer.optimize(nw)
            real=module.Word(out);columns=real.full();interface,conclusion,_=real.interface();assert all(interface.values())
            assert dict(actual_profile(out,real))==result['local_profile']
            expected=Counter()
            for c in subset:expected.update({int(r):n for r,n in c['optimization']['delta'].items()})
            payload=canonical(out);name='COMPOSED-'+'-'.join(map(str,ids))
            (args.out/(name+'.json.gz')).write_bytes(gzip.compress(payload,mtime=0))
            used={g[0] for sec in ('D','A','B','C') for g in out[sec]}|set(out['start'])|set(out['final'])
            rec=dict(ids=ids,word=name+'.json.gz',optimization=result,
                     additive_expected_delta={r:n for r,n in expected.items() if n},
                     additive=(result['delta']=={r:n for r,n in expected.items() if n}),
                     uses_added_frame_ids=sorted(f for f in used if f>=636),
                     canonical_sha256=sha256(payload).hexdigest(),
                     source_word_sha256=sha256(args.word.read_bytes()).hexdigest(),
                     arbitrary_columns=columns,interface=interface)
            (args.out/(name+'.json')).write_text(json.dumps(rec,sort_keys=True,indent=2)+'\n')
            results.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
    (args.out/'RESULT.json').write_text(json.dumps(dict(status='PASS_EXACT_COMPOSED_DIRTY_BIT_WORDS',results=results),sort_keys=True,indent=2)+'\n')


if __name__=='__main__':main()
