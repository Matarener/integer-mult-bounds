#!/usr/bin/env python3
"""Bind the seeded BIT star to actual E8 dyadic ADDRESS operators.

All changed FULL-box scalar/native-frame records are replayed independently.
Old CLEAN boxes remain the explicitly named retained R438 interface premise.
No owners, rounded theorem, or physical all-size tape claim is supplied.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
BASE = Path('/Users/ross/git/math')
RAW = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
OLDER = BASE / '.research-automation/runs/kappa-major-20261018T1330Z'
WORD = OLDER / 'bit-endpoint/BIT-FULL-COMPENSATION-WORD.json.gz'
OLD_STAR = OLDER / 'shared-helper-algebra/BIT-SEEDED-STAR.json'
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
NEW_H = Counter({1:1406,2:1342,3:79,4:44,5:93,6:11,7:9})
OLD_H = Counter({1:1322,2:1342,3:79,4:44,5:102,6:11,7:18})

def need(x, message):
    if not x:
        raise ValueError(message)

def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]

def tr(a):
    return list(map(list, zip(*a)))

def mm(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]

def rank(rows):
    b = {}
    for row in rows:
        row = list(map(Q,row))
        for k,v in sorted(b.items()):
            c = row[k]
            row = [x-c*y for x,y in zip(row,v)]
        k = next((i for i,x in enumerate(row) if x), None)
        if k is not None:
            b[k] = [x/row[k] for x in row]
    return len(b)

def add(a,b,c=1):
    z = a.copy()
    for k,v in b.items():
        z[k] = z.get(k,0)+c*v
        if not z[k]:
            del z[k]
    return z

def replay(w, program, backward=False, initial=None, omit_lift=False):
    n = 651
    frames = (program['final'] if backward else program['start'])[:]
    out = [{i:1} for i in range(n)] if initial is None else [r.copy() for r in initial]
    dims = [rank(w['lines'][p] for p in f) for f in w['frames']]
    masks = [sum(1 << p for p in f) for f in w['frames']]
    H = Counter()
    adds = moves = 0
    peak = 1
    for op,d,s,c,f,phase in reversed(program['records']) if backward else program['records']:
        if omit_lift and op == 0 and d == 111 and phase == 42:
            continue
        if op == 0:
            old,new = (c,s) if backward else (s,c)
            lo,hi = (new,old) if backward else (old,new)
            need(frames[d] == old, 'actual MOVE entry frame')
            need(not masks[lo] & ~masks[hi] and dims[hi]-dims[lo] == f > 0,
                'actual MOVE containment/rank')
            frames[d] = new
            H[f] += 1
            moves += 1
        else:
            need(op == 1 and d != s and frames[d] == frames[s] == f,
                'actual common-frame ADD')
            out[d] = add(out[d],out[s],-c if backward else c)
            adds += 1
            peak = max(peak,sum(abs(v) for v in out[d].values()))
    need(frames == (program['start'] if backward else program['final']), 'actual final frames')
    need(H == NEW_H and (adds,moves) == (12932,2984), 'complete changed local profile')
    return out, {'ADD':adds,'MOVE':moves,'histogram':dict(sorted(H.items())),
        'mass':sum(r*n for r,n in H.items()),'signed_integer_prefix_L1':peak}

def port_identities(w):
    from physical_code import actual_routes
    rhos,projectors,_=actual_routes(w)
    I = eye(8)
    hashes = []
    for rho,P in zip(rhos,projectors):
        A = [row[8:] for row in rho[:8]]
        need(all(x.denominator & (x.denominator-1) == 0 for row in rho for x in row), 'dyadic chart')
        K = [[I[i][j]-P[i][j] for j in range(8)] for i in range(8)]
        need(mm(P,P) == P and rank(P) == 1 and rank(K) == 7, 'actual P/K projectors')
        need(mm(A,tr(A)) == K and mm(tr(A),A) == eye(7), 'actual cap isometry')
        need(not any(x for row in mm(P,A) for x in row), 'P A=0')
        # These checked block relations imply exactly, for this actual rho:
        # rho diag(K,0) rho=diag(0,I7),
        # rho diag(I8,0) rho=diag(P,I7).
        # Consequently the source and old cap target progress are G=D_E7;
        # the FULL target progress is G N, N=D_P. No scalar rank9 code is used.
        body=json.dumps([[str(x) for x in row] for row in rho],separators=(',',':')).encode()
        hashes.append(sha256(body).hexdigest())
    need(len(hashes) == 111, 'all111 actual ports')
    return hashes

def row_xor(a,b):
    return [x ^ y for x,y in zip(a,b)]

def left(row, generator_mask):
    return [{x ^ generator_mask for x in coefficient} for coefficient in row]

def native_star(L=9, omit_terminal=False, wrong_full_target=False):
    need(L >= 3, 'three seed stages')
    n = L-1
    rows = [[{0} if i == j else set() for j in range(n)] for i in range(n)]
    levels = [-1]*n
    events = []
    H_idle = Counter()
    def idle(bank, last):
        old = levels[bank]
        if last == old:
            return
        need(last > old, 'native idle chronology')
        mask = sum(1 << (s+1) for s in range(old+1,last+1))
        rows[bank] = left(rows[bank],mask)
        d = 7*(last-old)
        H_idle[d] += 111
        levels[bank] = last
        events.append({'kind':'native_idle','bank':bank,'old':old,'new':last,
            'children':111,'rank_each':d,'actual_projector':'orthogonal sum of listed G_s supports'})
    def call(stage, kind, source, target):
        idle(source,stage-1)
        idle(target,stage-1)
        g = 1 << (stage+1)
        x,y = rows[source],rows[target]
        if kind == 'OLD_F':
            rows[source] = left(x,g)
            rows[target] = row_xor(left(y,g),left(x,g|1))
        elif kind == 'OLD_B':
            rows[source] = row_xor(left(x,g),left(y,g|1))
            rows[target] = left(y,g)
        else:
            need(kind == 'NEW_F','actual declared local alphabet')
            rows[source] = left(x,g)
            rows[target] = row_xor(left(x,g),left(y,g if wrong_full_target else g|1))
        levels[source] = levels[target] = stage
        events.append({'kind':kind,'stage':stage,'source':source,'target':target,
            'source_progress_rank':7,'target_progress_rank':8 if kind == 'NEW_F' else 7,
            'cross':'G_s' if kind == 'NEW_F' else 'G_s N_p',
            'helpers':429 if kind == 'NEW_F' else 438,
            'literal_local_word':str(WORD) if kind == 'NEW_F' else str(RAW)})
    call(0,'OLD_F',0,1)
    call(1,'OLD_B',0,1)
    call(2,'OLD_F',0,1)
    rows[0],rows[1] = rows[1],rows[0]
    events.append({'kind':'whole_bank_SWAP','banks':[0,1],'field_SWAPS':111,
        'binary_VALUE_implementation_XOR_ADDs':333})
    for j in range(2,n):
        call(j+1,'NEW_F',0,j)
    for bank in range(n):
        idle(bank,L-1)
    for j in reversed(range(2,n)):
        if omit_terminal and j == 2:
            continue
        rows[j] = row_xor(rows[j],rows[0])
        events.append({'kind':'terminal_common_front_CNOT','source':0,'target':j,
            'ADDs':111,'native_children':0})
    final_mask = (1 << (L+1))-1
    expected = [[{final_mask} if i == j else set() for j in range(n)] for i in range(n)]
    return rows,expected,events,H_idle

def receipt():
    need(sha256(RAW.read_bytes()).hexdigest() == 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022','R438 raw pin')
    need(sha256(WORD.read_bytes()).hexdigest() == '0f461dbc7e82a02faedb4a5129103963507c9f063a0a3679ba5d20ad94df160e','changed word pin')
    w = json.loads(gzip.decompress(RAW.read_bytes()))
    program = json.loads(gzip.decompress(WORD.read_bytes()))
    need(len(program['start']) == len(program['final']) == 651,'all ordinary roles')
    need(all(f == 0 for f in program['start'][111:]), 'all target/helper entries atZERO')
    a,forward = replay(w,program)
    _,inverse = replay(w,program,True)
    need(all(a[p] == {p:1} for p in list(range(111))+list(range(222,651))),
        'all source and429 arbitrary helper columns restored exactly overZ')
    for p in range(111):
        parity = {k for k,v in a[111+p].items() if v & 1}
        need(parity == {p,111+p},'actual target y+x overF2')
    back,_ = replay(w,program,True,a)
    need(back == [{i:1} for i in range(651)],'literal full integer inverse all651 columns')
    try:
        replay(w,program,omit_lift=True)
    except ValueError as error:
        lift_control = str(error)
    else:
        raise ValueError('omitted actual target lift escaped')
    port_hashes = port_identities(w)
    rows,expected,events,H_idle = native_star()
    need(rows == expected,'actual native ADDRESS exchange group algebra all eight raw banks')
    bad,_,_,_ = native_star(omit_terminal=True)
    need(bad != expected,'missing common-front CNOT rejected')
    bad,_,_,_ = native_star(wrong_full_target=True)
    need(bad != expected,'dropping physical target common N rejected')
    for L in (3,5,7,11,13):
        z,e,_,_ = native_star(L)
        need(z == e,'native operator star all checked arities')
    local = Counter({r:3*OLD_H[r]+6*NEW_H[r] for r in set(OLD_H)|set(NEW_H)})
    return {'status':'PASS_NATIVE_E8_SEEDED_STAR_OPERATOR_BINDING_WITH_IMPORTED_OLD_CLEAN_INTERFACE',
        'scientific_pin':PIN,'no_new_kappa':True,
        'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in (RAW,WORD,OLD_STAR,HERE/'physical_code.py')},
        'changed_local_all651_Z_columns_replayed':True,
        'changed_local_forward':forward,'changed_local_literal_inverse':inverse,
        'changed_local_helpers_restored':429,'private_fields':0,
        'all111_actual_rho15_hashes':port_hashes,
        'actual_native_local_blocks':{
            'old_F':'[[G_s,0],[G_s N_p,G_s]]',
            'old_B':'[[G_s,G_s N_p],[0,G_s]] over binary VALUE',
            'new_F':'[[G_s,0],[G_s,G_s N_p]]',
            'N_p':'actual D_(q_p q_p^T/4) on the common8-space',
            'G_0':'D_(I8-q_p q_p^T/4), rank7',
            'G_s_s_positive':'D_(fresh E_s), rank7 after the actual rho15 chart',
            'full_parent':'N_p G_0 ... G_(L-1) = D_I_m, m=1+7L, on each physical port'},
        'word':events,
        'binary_VALUE_public_banks':8,
        'conditional_local_histogram_before_helpers_hosted':dict(sorted(local.items())),
        'public_idle_histogram_before_helpers_hosted':dict(sorted(H_idle.items())),
        'new_words_total_ADD':6*12932,
        'terminal_CNOT_ADD':6*111,'bank_SWAP_field_scans':111,
        'raw_deficit_if_all_owners_exact':2*111-3*63,
        'native_scope':'All111 actual E8 ports and exact dyadic rho block identities; literal changed651-role scalar/frame stream; native outer word in the group algebra of explicitly orthogonal ADDRESS exchanges, valid on all binary VALUE functions over every odd ADDRESS field. No scalar-rank9 replacement or dropped target lift is used.',
        'remaining_premises':[
            'The old CLEAN R438 F/B contract and its signed/native compiler remain imported, not newly independently compiled here.',
            'No chronological whole-helper owner allocation, complete hosted histogram, fallback or stock certificate.',
            'No rounded child-error/suffix weights, source-access/tape realization or all-size supplier admission.',
            'The root independently rejects this seeded profile at primitive exponent .002; this reusable binding is not a positive exponent claim.'],
        'executed_controls':{'omitted_target_lift':lift_control,
            'omitted_terminal_CNOT':True,'wrong_full_target_G_instead_of_GN':True}}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    out=json.loads(json.dumps(receipt()))
    path=HERE/'NATIVE-SEED-BINDING.json'
    if args.write:
        path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == out,'stored native binding differs')
    print(out['status'])
    print('111 actual rho charts;651 integer columns;8 native raw-input banks; all lifts paid')

if __name__=='__main__':
    main()
