#!/usr/bin/env python3
"""Conjugate production and observation together by an explicit helper basis.

Credit: the retained adaptive/dataisfire supplier; PR4061's signed consumer
columns by Riquelme Soares; PR4045's paid interface gate by Chris R; the
continuation's exact free-warp checker. New changed-interface experiment,
with substantial OpenAI assistance. Apache-2.0.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, permutations
import gzip
import json
from pathlib import Path
import sys
from time import monotonic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / 'research/kappa-adaptive-continuation/native-alternatives'
PREVIOUS = ROOT / 'research/kappa-1745-continuation/complex-birth'
sys.path.insert(0, str(OLD))
sys.path.insert(0, str(PREVIOUS))
import fanout_search as F
import opt_frames as O
from exact_rows import replay, expected
from commute_birth import trace
F.phi = O.phi = lambda r: r ** (1 - 0.001745) if r else 0.0


def canonical(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def inverse(matrix):
    n = len(matrix)
    out = [[Q(x) for x in row] + [Q(i == j) for j in range(n)]
           for i, row in enumerate(matrix)]
    for j in range(n):
        p = next(i for i in range(j, n) if out[i][j])
        out[j], out[p] = out[p], out[j]
        v = out[j][j]
        out[j] = [x/v for x in out[j]]
        for i in range(n):
            if i != j:
                v = out[i][j]
                out[i] = [x-v*y for x, y in zip(out[i], out[j])]
    return [row[n:] for row in out]


def matrix_of(operations, n):
    matrix = [[Q(i == j) for j in range(n)] for i in range(n)]
    for kind, d, s, coefficient in operations:
        if kind == 'add':
            matrix[d] = [x+coefficient*y for x,y in zip(matrix[d],matrix[s])]
        else:
            matrix[d] = [coefficient*x for x in matrix[d]]
    return matrix


def choices(n):
    yield 'identity', []
    for d in range(n):
        for s in range(n):
            if d != s:
                for q in (Q(1),Q(-1),Q(1,2),Q(-1,2),Q(2),Q(-2)):
                    yield f'shear-{d}-{s}-{str(q).replace("/","_")}', [('add',d,s,q)]
    for a,b in combinations(range(n),2):
        for sign in (Q(1),Q(-1)):
            # Outputs (a+sign*b, a-sign*b), determinant -2*sign.
            yield f'hadamard-{a}-{b}-{sign}', [('add',a,b,sign),('scale',b,b,-2*sign),('add',b,a,Q(1))]
    if n == 4:
        seen=set()
        for p in permutations(range(4)):
            operations=[]
            for a,b in ((p[0],p[1]),(p[2],p[3]),(p[0],p[2]),(p[1],p[3])):
                operations += [('add',a,b,Q(1)),('scale',b,b,Q(-2)),('add',b,a,Q(1))]
            operations += [('scale',a,a,Q(1,2)) for a in range(4)]
            matrix=matrix_of(operations,n)
            # Signed row permutations only rename an equal-endpoint basis.
            key=tuple(sorted(min(tuple(row),tuple(-x for x in row)) for row in matrix))
            if key in seen:continue
            seen.add(key)
            yield 'walsh4-'+''.join(map(str,p)),operations


def coalesce(events):
    """Combine only adjacent commuting linear updates at a common frame."""
    out=[]; block=[]; destinations=set(); sources=set(); frame=None
    def flush():
        nonlocal block,destinations,sources,frame
        sums={}
        for e in block:
            key=(e[1],e[2]);sums[key]=sums.get(key,Q(0))+Q(e[3],e[4])
        for (d,s),coefficient in sums.items():
            if coefficient:
                out.append(['add',d,s,coefficient.numerator,coefficient.denominator,list(frame)])
        block=[];destinations=set();sources=set();frame=None
    for event in events:
        if event[0] != 'add':
            flush();out.append(event);continue
        d,s=event[1:3];f=tuple(event[-1])
        if block and (f != frame or d in sources or s in destinations):flush()
        frame=f;block.append(event);destinations.add(d);sources.add(s)
    flush()
    return out


def construct(word, group, operations):
    selected={r:i for i,r in enumerate(group)};n=len(group)
    frames=[F.basis(tuple(word['start_extra'].get(str(r),[]))) for r in group]
    assert len(set(frames)) == 1 and frames[0]
    assert all(str(r) not in word['helper_final'] and r not in word['centers'] for r in group)
    assert all(not set(F.regs(e)).intersection(group) for e in word['A'])
    M=matrix_of(operations,n);N=inverse(M)
    assert all(q.denominator & (q.denominator-1) == 0 for rows in (M,N) for row in rows for q in row)
    candidate=deepcopy(word)
    prep=[]
    for kind,d,s,q in operations:
        if kind=='add':prep.append(['add',group[d],group[s],q.numerator,q.denominator,list(frames[0])])
        else:prep.append(['scale',group[d],q.numerator,q.denominator,list(frames[0])])
    candidate['A'] += prep
    def convert(events):
        out=[]
        for event in events:
            kind,d=event[:2]
            if kind != 'add':
                assert d not in selected
                out.append(deepcopy(event));continue
            s=event[2];q=Q(event[3],event[4])
            assert not (d in selected and s in selected), 'internal selected-pair event needs a full matrix synthesis'
            dsts=[(group[i],M[i][selected[d]]) for i in range(n)] if d in selected else [(d,Q(1))]
            srcs=[(group[j],N[selected[s]][j]) for j in range(n)] if s in selected else [(s,Q(1))]
            for dd,a in dsts:
                for ss,b in srcs:
                    coefficient=q*a*b
                    if coefficient:out.append(['add',dd,ss,coefficient.numerator,coefficient.denominator,event[-1]])
        return coalesce(out)
    converted=convert(F.expand(word)['B']);candidate['B']=[]
    for event in converted:
        if event[0]=='warp':candidate['warps'][event[2]-1][0]=len(candidate['B'])
        else:candidate['B'].append(event)
    candidate['restore']=convert(word['restore'])
    F.derive_cleanup(candidate)
    return candidate, {'matrix':[[str(q) for q in row] for row in M],
                       'inverse':[[str(q) for q in row] for row in N],
                       'entrance_operations':prep}


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--variant',choices=('base','extra'),default='base')
    parser.add_argument('--group',type=int,nargs='+',default=[600,601,602,604])
    args=parser.parse_args()
    source=OLD/f'candidate/BORROW-WORD-43{args.variant}.json.gz'
    word=F.read(source);assert replay(word)[0] == expected(word)
    args.output.mkdir(parents=True,exist_ok=True)
    stats=Counter();cases=[];positives=[];started=monotonic()
    for name,operations in choices(len(args.group)):
        candidate,interface=construct(word,args.group,operations)
        stats['interfaces_constructed']+=1
        assert replay(candidate)[0]==expected(candidate), name
        stats['exact_all_dirty_operator_passed']+=1
        case={'name':name,'interface':interface,'exact_all_dirty_operator':True,
              'unoptimized_scalar_ADD_delta':sum(e[0]=='add' for sec in ('A','B','restore','cleanup') for e in candidate[sec])-
                                            sum(e[0]=='add' for sec in ('A','B','restore','cleanup') for e in word[sec])}
        try:
            candidate,optimization=O.optimize(candidate)
        except (ValueError,AssertionError) as exc:
            stats['frame_rejected']+=1;case['frame_rejection']=str(exc)
        else:
            stats['joint_frame_solved']+=1
            profile,_=trace(candidate)
            assert dict(profile)=={int(r):c for r,c in candidate['report']['local_profile'].items()}
            assert replay(candidate)[0]==expected(candidate)
            case['optimization']=optimization;case['profile']=dict(profile)
            case['all_independent_inputs']=632;case['zero_private_buffers']=91
            if optimization['saving']>1e-9:
                stats['positive_profile']+=1
                payload=canonical(candidate);filename=f'WORD-{name}.json.gz'
                (args.output/filename).write_bytes(gzip.compress(payload,mtime=0))
                case['word']=filename;case['payload_sha256']=sha256(payload).hexdigest()
                case['native_admission']=False;positives.append(case)
                print('POSITIVE',name,optimization,flush=True)
        cases.append(case)
        if len(cases)%10==0:print('PROGRESS',dict(stats),'seconds',monotonic()-started,flush=True)
    paths=[source,Path(__file__),OLD/'fanout_search.py',OLD/'opt_frames.py',PREVIOUS/'exact_rows.py',PREVIOUS/'commute_birth.py']
    result={'status':'MATCHED_COMPLEX_HELPER_BASIS_FINITE_SCREEN','group':args.group,'variant':args.variant,
            'stats':dict(stats),'cases':cases,'positives':positives,'new_kappa':False,
            'seconds':monotonic()-started,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'Full producer/consumer conjugation by an explicit common-entrance dyadic basis. '
                    'Arbitrary-dirty signed free-operator checks and joint-frame pricing. '
                    'No native physical or outer admission without further checks.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'seconds',monotonic()-started,flush=True)


if __name__=='__main__':main()
