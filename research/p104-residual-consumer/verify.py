#!/usr/bin/env python3
"""Source-bound P104 query consumer and priced legacy return. Apache-2.0."""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MAIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PRED = '9d56eeedbed5e3e9bbbc8c189d66f14cf15b6067'
CUT = 3642
FULL = tuple(1 << i for i in range(9))
NAMES = [f'{p}{i}' for p,n in [('X',104),('Y',104),('Q',8),('G',32),('D',32)] for i in range(n)]
# Columns are the PR3882 pivots in ascending port order. Derived from the
# actual 416-event suffix, then frozen before the full splice experiment.
T = [[2,2,2,-2,0,0,0,0], [0,0,2,2,2,-2,0,0],
     [0,0,0,0,2,-2,-2,2], [2,2,2,2,0,0,0,0],
     [2,2,-2,-2,0,0,0,0], [0,-2,0,-2,2,0,-2,0],
     [-2,2,-2,2,0,0,0,0], [0,-2,2,0,-2,0,0,-2]]
PINS = {
 'inputs/PR3882_geometry.json':'8212331ef435650469b6fca71448bcc2915a0cab46562acc41c5fc2a3dfa56c7',
 'inputs/PR3882_RESULT.json':'33eaae6c77c10bed705d76b7950e7f8a6d5e09cd5727eadcde6f853c37be3f2b'}
LIVE = {
 'research/p104-native-channel/inputs/P104-FIXTURE.json':'516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4',
 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json':'0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e'}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def unique(pairs):
    d = {}
    for k,v in pairs:
        need(k not in d, 'duplicate JSON key')
        d[k] = v
    return d


def load(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',',':'))+'\n').encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def pinned(root, names):
    out = {}
    for path, digest in names.items():
        raw = (root/path).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == digest, 'source hash '+path)
        out[path] = json.loads(raw, object_pairs_hook=unique)
    return out


def geometry(data):
    removed = {tuple(v) for v in data['F0']+data['C']}
    roots = set()
    for a,b in itertools.combinations(range(8),2):
        for s in (-1,1):
            v = [0]*8
            v[a],v[b] = 2,2*s
            roots.add(tuple(v))
    for s in itertools.product((-1,1),repeat=7):
        if s.count(-1)%2 == 0:
            roots.add((1,)+s)
    need(len(roots)==120 and len(removed)==16 and removed<=roots, 'geometry domain')
    ports = sorted(roots-removed)
    J = [0,1,3,6,22,31,93,103]
    N = [i for i in range(104) if i not in J]
    A = [[F(sum(a*b for a,b in zip(u,v)),8) for v in ports] for u in ports]
    B = [[A[j][n] for n in N] for j in J]
    need(all(A[j][k]==(j==k) for j in J for k in J), 'pivot frame')
    need(all(A[n][m]==sum(B[j][a]*B[j][b] for j in range(8))
             for a,n in enumerate(N) for b,m in enumerate(N)), 'Gram block factor')
    need(sum(x!=0 for row in B for x in row)==384, 'B support')
    need(all(x in (0,F(1,2),F(-1,2)) for row in B for x in row), 'B coefficients')
    return A,B,J,N


def row_add(a,b,c):
    out = a.copy()
    for k,v in b.items():
        out[k] = out.get(k,F(0))+c*v
        if not out[k]: del out[k]
    return out


def expected_exit(A,B,J,N):
    s = {n:{i:F(1)} for i,n in enumerate(NAMES)}
    for i in range(104):
        s[f'Y{i}'] = {104+i:F(1), **{j:x for j,x in enumerate(A[i]) if x}}
    for b,j in enumerate(J):
        s[f'X{j}'] = {j:F(1), **{n:B[b][a] for a,n in enumerate(N) if B[b][a]}}
        s[f'Y{j}'] = {j:F(1),104+j:F(1)}
    for n in N: s[f'X{n}'] = {n:F(1),104+n:F(1)}
    return s


def expanded_cleanup(B,J,N,t=T):
    d = [[F(0)]*104 for _ in range(8)]
    for k in range(8):
        for b,j in enumerate(J): d[k][j] = F(t[k][b])
        for a,n in enumerate(N): d[k][n] = sum(F(t[k][b])*B[b][a] for b in range(8))
    need(all(x in (-2,0,2) for r in d for x in r), 'cleanup alphabet')
    need(all(sum(x!=0 for x in r)==52 for r in d), 'cleanup row supports')
    return d


def cut_state(A,d):
    s = {n:{i:F(1)} for i,n in enumerate(NAMES)}
    for i in range(104):
        s[f'Y{i}'] = {104+i:F(1), **{j:x for j,x in enumerate(A[i]) if x}}
    for k in range(8):
        s[f'Q{k}'] = {208+k:F(1), **{j:-x for j,x in enumerate(d[k]) if x}}
    frames = {n:('H'+n[1:] if n.startswith('Y') else 'F') for n in NAMES}
    return s,frames


def tail(B,J,N):
    # Same literal tail as PR3882; its two streams must precede X_N overwrite.
    ops = [('up',f'Y{i}',i) for i in range(104)]
    for a,n in enumerate(N):
        ops.append(('scale',f'X{n}','1/2'))
        for b,j in enumerate(J):
            if B[b][a]:
                c = int(2*B[b][a])
                ops += [('add',f'X{j}',f'X{n}',c),('add',f'Y{j}',f'X{n}',-c)]
        ops.append(('scale',f'X{n}','2'))
    for b,j in enumerate(J):
        ops.append(('scale',f'X{j}','1/2'))
        for a,n in enumerate(N):
            if B[b][a]: ops.append(('add',f'X{n}',f'X{j}',-int(2*B[b][a])))
        ops.append(('scale',f'X{j}','2'))
    ops += [('add',f'X{n}',f'Y{n}',1) for n in N]
    ops += [('down',f'X{n}',n) for n in N]+[('down',f'Y{j}',j) for j in J]
    return ops


def consumer(J,t=T):
    # Read-only q donors. Each signed 2q is two unit ADDs, without scratch.
    return [('add',f'Q{k}',f'X{j}',int(c/abs(c)))
            for k,row in enumerate(t) for j,c in zip(J,row) if c for _ in range(abs(c))]


def return_adapter(B,J,N):
    ops = [('up',f'X{n}',n) for n in N]
    for b,j in enumerate(J):
        ops.append(('scale',f'X{j}','1/2'))
        for a,n in enumerate(N):
            if B[b][a]: ops.append(('add',f'Y{n}',f'X{j}',-int(2*B[b][a])))
        ops.append(('scale',f'X{j}','2'))
    for n in N:
        ops += [('add',f'X{n}',f'Y{n}',-1),('add',f'Y{n}',f'X{n}',1)]
    for a,n in enumerate(N):
        ops.append(('scale',f'X{n}','1/2'))
        for b,j in enumerate(J):
            if B[b][a]: ops.append(('add',f'X{j}',f'X{n}',-int(2*B[b][a])))
        ops.append(('scale',f'X{n}','2'))
    return ops+[('down',f'Y{n}',n) for n in N]


def run(s,frames,ops):
    s,frames = {k:v.copy() for k,v in s.items()},frames.copy()
    for op in ops:
        kind,r = op[:2]
        need(r in s, 'unknown register')
        if kind=='up':
            need(frames[r]=='H'+str(op[2]), 'wrong lift frame')
            frames[r] = 'F'
        elif kind=='down':
            need(frames[r]=='F', 'wrong descent frame')
            frames[r] = 'H'+str(op[2])
        else:
            need(frames[r]=='F', 'arithmetic target not FULL')
            if kind=='scale':
                c = F(op[2]); need(c in (F(1,2),F(2)), 'scale alphabet')
                s[r] = {i:c*x for i,x in s[r].items()}
            else:
                need(kind=='add' and r!=op[2] and frames.get(op[2])=='F', 'ADD source frame')
                need(type(op[3]) is int and op[3] in (-1,1), 'unit ADD alphabet')
                s[r] = row_add(s[r],s[op[2]],F(op[3]))
    return s,frames


def endpoint_digest(s):
    return sha([[str(s[n].get(i,F(0))) for i in range(280)] for n in NAMES])


def desired_frames(J):
    return {n:('H'+n[1:] if (n.startswith('Y') and int(n[1:]) in J)
                            or (n.startswith('X') and int(n[1:]) not in J) else 'F') for n in NAMES}


def span(vectors):
    out = {0}
    for x in vectors:
        need(type(x) is int and 0<x<512, 'binary label')
        out |= {a^x for a in tuple(out)}
    return frozenset(out)


def source_audit(A,B,J,N,ops,expected):
    live = pinned(REPO,LIVE)
    w = live['research/p104-native-channel/inputs/LOWRANK-WITNESS.json']
    fixture = live['research/p104-native-channel/inputs/P104-FIXTURE.json']['section4_explicit_P104']
    g = load(HERE/'inputs/PR3882_geometry.json')
    need(fixture['F0']==g['F0'] and fixture['C']==g['C'], 'source geometry extraction')
    program = w['program']
    need(len(program)==4058, 'original word length')
    d = [[F(0)]*104 for _ in range(8)]
    for e in program[CUT:]:
        need(len(e)==5 and e[0]=='add' and e[1] in [f'Q{i}' for i in range(8)]
             and e[2] in [f'X{i}' for i in range(104)] and tuple(e[4])==FULL, 'cleanup suffix contract')
        d[int(e[1][1:])][int(e[2][1:])] += F(e[3])
    need(d==expanded_cleanup(B,J,N), 'actual cleanup factorisation')
    need([[r[j] for j in J] for r in d]==T, 'actual cleanup pivot block')
    s = {n:{i:F(1)} for i,n in enumerate(NAMES)}
    f = {n:tuple(w['initial_frames'][n]) for n in NAMES}
    # The archived native checker keys canonical charts by binary subspace,
    # not by a particular basis spelling. No free physical basis map is added.
    profile = Counter()
    kinds = Counter()
    for e in program[:CUT]:
        k,r = e[:2]; kinds[k]+=1
        if k=='add':
            need(span(f[r])==span(f[e[2]])==span(e[4]), 'prefix ADD frame')
            s[r] = row_add(s[r],s[e[2]],F(e[3]))
        elif k=='transport':
            before,after = tuple(e[2]),tuple(e[3])
            need(span(f[r])==span(before), 'prefix transport entrance')
            a,b = span(before),span(after)
            need(a<=b or b<=a, 'prefix transport nesting')
            need(e[4]==abs(len(before)-len(after))>0, 'prefix transport tariff')
            profile[e[4]]+=1; f[r]=after
        elif k=='zero':
            need(r=='C' and r not in s, 'private allocation')
            s[r]={}; f[r]=tuple(e[2])
        elif k=='copy':
            need(r=='C' and not s[r] and span(f[r])==span(f[e[2]])==span(e[3]), 'private copy')
            s[r]=s[e[2]].copy()
        else:
            need(k=='erase' and r=='C' and span(f[r])==span(e[2]), 'owned live-copy erase contract')
            del s[r]; del f[r]
    need(set(s)==set(NAMES), 'cut live registers')
    want,cutframes=cut_state(A,d)
    need(s==want, 'actual cut coefficients')
    need(all(span(f[n])==span(w['final_frames'][n]) for n in NAMES), 'cut exit frames')
    hs=[span(f[f'Y{i}']) for i in range(104)]
    need(all(len(h)==256 for h in hs) and len(set(hs))==104, 'distinct target hyperplanes')
    need(all(span(f[n])==span(FULL) for n in NAMES if not n.startswith('Y')), 'FULL consumers and sources')
    result,ff=run(s,cutframes,ops)
    need(result==expected and ff==desired_frames(J), 'actual source-bound splice endpoint')
    hist=[profile[r] for r in range(1,9)]
    need(hist==[1074,58,86,104,48,24,8,8], 'inherited profile recount')
    # Direct old cleanup is a control, not inferred from the new factor.
    old={n:r.copy() for n,r in s.items()}
    for e in program[CUT:]: old[e[1]]=row_add(old[e[1]],old[e[2]],F(e[3]))
    for i in range(208,280): need(old[NAMES[i]]=={i:F(1)}, 'old cleanup dirt control')
    return {'original_prefix_events':CUT,'actual_cleanup_events':len(program)-CUT,
            'original_native_profile':hist,'live_cut_registers':len(s),
            'distinct_output_hyperplanes':len(set(hs)), 'actual_endpoint_sha256':endpoint_digest(result),
            'original_cut_sha256':endpoint_digest(s),'prefix_operation_counts':dict(sorted(kinds.items()))}


def counts(ops):
    c=Counter(e[0] for e in ops)
    return {'unit_adds':c['add'],'halves':sum(e[0]=='scale' and e[2]=='1/2' for e in ops),
            'doubles':sum(e[0]=='scale' and e[2]=='2' for e in ops),'rank_one_transports':c['up']+c['down']}


def calculate():
    inputs=pinned(HERE,PINS)
    A,B,J,N=geometry(inputs['inputs/PR3882_geometry.json'])
    pred=inputs['inputs/PR3882_RESULT.json']
    need(pred['pivots']==J and pred['nonpivots']==N and pred['combined_mass']==2576, 'predecessor receipt scope')
    d=expanded_cleanup(B,J,N)
    s,f=cut_state(A,d)
    ops=tail(B,J,N)+consumer(J)
    actual,ff=run(s,f,ops)
    expected=expected_exit(A,B,J,N)
    need(actual==expected and ff==desired_frames(J), 'new consumer endpoint')
    need(endpoint_digest(actual)==pred['endpoint_sha256'], 'unchanged predecessor endpoint digest')
    returned,rf=run(actual,ff,return_adapter(B,J,N))
    for i in range(104):
        need(returned[f'X{i}']=={i:F(1)}, 'legacy source return')
        need(returned[f'Y{i}']=={i:F(1),104+i:F(1)}, 'legacy corrected sum')
        need(rf[f'X{i}']=='F' and rf[f'Y{i}']=='H'+str(i), 'legacy endpoint frame')
    for i in range(208,280): need(returned[NAMES[i]]=={i:F(1)}, 'legacy dirty restoration')
    # Explicit separating family for every H_n: only w_n is initially nonzero,
    # while requested x_n at FULL must become nonzero. Proof supplies all lengths.
    for n in N:
        isolated={name:{} for name in NAMES}; isolated[f'X{n}']={0:F(1)}
        r,_=run(isolated,desired_frames(J),return_adapter(B,J,N))
        need(r[f'X{n}']=={0:F(1)}, 'return cut separating witness')
    mass=pred['combined_mass']; progress=104*8+104*8+72*9
    need(mass-progress==264, 'persistent progress invoice')
    # m=8s+1, W=104(s-1); all-p proof is in PROOF.md, not a sampled inference.
    budget=[]
    for stages in (3,5,9,17):
        width=8*stages+1; roles=104*(stages-1)
        owed=(width-1)*roles
        for extra in (0,192):
            paid=stages*(mass+extra)+max(0,owed-stages*progress)
            gap=(mass+extra-progress-104)*stages+104
            need(paid-width*roles>=gap>0, 'coverage-gap identity')
            budget.append({'stages':stages,'legacy_return':bool(extra),'width':width,'roles':roles,
                           'paid_mass_lower_bound':paid,'capacity':width*roles,'gap_lower_bound':gap})
    result={'schema_version':1,'scientific_base':MAIN,'predecessor':PRED,
            'cut':CUT,'pivots':J,'cleanup_factor':T,'old_cleanup_weighted_adds':416,
            'new_cleanup_weighted_adds':32,'old_readonly_unit_adds':832,'new_readonly_unit_adds':64,
            'readonly_unit_adds_saved':768,'real_component_adds_saved_at_512_complex_words':786432,
            'tail':counts(tail(B,J,N)),'consumer':counts(consumer(J)),
            'legacy_return_adapter':counts(return_adapter(B,J,N)),
            'legacy_return_minimum_rank_mass_in_stated_model':192,
            'original_prefix_events':CUT,'new_unit_suffix_events':len(ops),
            'new_joined_events':CUT+len(ops),'weighted_cleanup_joined_events':CUT+len(tail(B,J,N))+32,
            'consumer_program_sha256':sha(consumer(J)),
            'joined_suffix_program_sha256':sha(ops),
            'endpoint_sha256':endpoint_digest(actual),'legacy_endpoint_sha256':endpoint_digest(returned),
            'combined_profile':[1282,58,86,104,48,24,8,8],'combined_mass':mass,
            'legacy_combined_profile':[1474,58,86,104,48,24,8,8],'legacy_combined_mass':mass+192,
            'optimistic_progress_per_call':progress,'residual_gap_slope':160,'residual_gap_intercept':104,
            'legacy_gap_slope':352,'legacy_gap_intercept':104,'sample_budgets':budget,
            'new_native_recipe_replay':False,'affordable_supplier':False,'selected_frontier_changed':False}
    need(counts(tail(B,J,N))==dict(unit_adds=1248,halves=104,doubles=104,rank_one_transports=208), 'tail invoice')
    need(counts(return_adapter(B,J,N))==dict(unit_adds=960,halves=104,doubles=104,rank_one_transports=192), 'return invoice')
    return result,(A,B,J,N,ops,expected)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--algebra-only',action='store_true',help='Do not claim original-word or source-cut authentication.')
    parser.add_argument('--write-result',action='store_true',help='Explicitly regenerate only this package result.')
    args=parser.parse_args()
    result,context=calculate()
    if args.write_result:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(canonical(result)==canonical(load(HERE/'RESULT.json')), 'typed frozen result mismatch')
    if not args.algebra_only:
        print(json.dumps(source_audit(*context),sort_keys=True))
    mode='ALGEBRA_ONLY' if args.algebra_only else 'SOURCE_BOUND'
    print(f'PASS_P104_RESIDUAL_CONSUMER_{mode} cleanup=416_to_32 unit=832_to_64 legacy_rank=192 result={sha(result)}')

if __name__=='__main__': main()
