#!/usr/bin/env python3
"""Exact source-bound axis encoding audit; standard library, Apache-2.0."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def pairs(items):
        ans = {}
        for key, value in items:
            require(key not in ans, 'duplicate JSON key')
            ans[key] = value
        return ans
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def authenticate():
    for row in read(HERE / 'SOURCES.json')['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        require(not path.is_symlink(), 'source symlink')
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input hash: ' + row['path'])
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'], 'input blob')


def source_matrix():
    roots = []
    for a, b in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[b] = 2, 2 * sign
            roots.append(tuple(row))
    roots.extend((1,) + tail for tail in itertools.product((-1, 1), repeat=7) if tail.count(-1) % 2 == 0)
    fixture = read(ROOT / 'research/p104-native-channel/inputs/P104-FIXTURE.json')['section4_explicit_P104']
    removed = {tuple(row) for row in fixture['F0'] + fixture['C']}
    ports = sorted(set(roots) - removed)
    require(len(ports) == 104, 'P104 port count')
    order = list(PIVOTS) + [i for i in range(104) if i not in PIVOTS]
    ports = [ports[i] for i in order]
    gram = [[sum(x*y for x,y in zip(a,b)) for b in ports] for a in ports]
    require(all(gram[i][j] == 8*(i == j) for i in range(8) for j in range(8)), 'pivot Gram')
    b2 = [[gram[i][j] // 4 for j in range(8,104)] for i in range(8)]
    require(all(v in (-1,0,1) for row in b2 for v in row), 'signed half coefficients')
    require(all(sum(b2[i][k]*b2[j][k] for k in range(96)) == 48*(i == j) for i in range(8) for j in range(8)), 'BBt=12I')
    require(all(sum(b2[k][i]*b2[k][j] for k in range(8)) == gram[i+8][j+8]//2 for i in range(96) for j in range(96)), 'nonpivot Gram')
    return b2


def add_into(state, dest, src, coefficient):
    value = state.get(dest, 0) + coefficient * state.get(src, 0)
    if value:
        state[dest] = value
    else:
        state.pop(dest, None)


def fiber_word(state, axis, fixed, b2, inverse=False, reverse=False):
    """Literal encoding at T=I. Fractions allowed; no actual chart move claimed."""
    from fractions import Fraction
    n = len(b2) + len(b2[0]); p = len(b2)
    source, target = (1,0) if reverse else (0,1)
    def slot(bank, k):
        return (bank, k, fixed) if axis == 0 else (bank, fixed, k)
    def swap():
        for k in range(p,n):
            x,y=slot(source,k),slot(target,k)
            vx,vy=state.get(x,0),state.get(y,0)
            if vy: state[x]=vy
            else: state.pop(x,None)
            if vx: state[y]=vx
            else: state.pop(y,None)
    def scale_nonpivot():
        for k in range(p,n):
            s=slot(source,k)
            if s in state: state[s]=-state[s]
    def forward_b(sign):
        for j,row in enumerate(b2):
            for k,c in enumerate(row,p):
                if c: add_into(state,slot(source,j),slot(source,k),sign*Fraction(c,2))
    def transpose_b():
        for j,row in enumerate(b2):
            for k,c in enumerate(row,p):
                if c: add_into(state,slot(source,k),slot(source,j),Fraction(c,2))
    if inverse:
        swap()
        for k in range(p,n): add_into(state,slot(source,k),slot(target,k),-1)
        scale_nonpivot(); transpose_b(); forward_b(-1)
    else:
        forward_b(1); scale_nonpivot(); transpose_b()
        for k in range(p,n): add_into(state,slot(source,k),slot(target,k),1)
        swap()


def encode(state, axis, b2, inverse=False, reverse=False):
    out=dict(state)
    n=len(b2)+len(b2[0])
    for fixed in range(n): fiber_word(out,axis,fixed,b2,inverse,reverse)
    return out


def transition(state,b2):
    return encode(encode(state,0,b2,inverse=True),1,b2,reverse=True)


def result():
    authenticate(); b2=source_matrix()
    from fractions import Fraction
    # Actual port-gauge DC witness; physical C_U, F and E all act as identity here.
    seed={(0,0,0):Fraction(2)}
    row=encode(seed,0,b2); col=encode(seed,1,b2,reverse=True)
    leak={key:value for key,value in row.items() if key != (0,0,0)}
    require(col == seed, 'column opposite-orientation witness')
    require(len(leak)==48 and all(key[0]==1 and key[1]>=8 and key[2]==0 and abs(v)==1 for key,v in leak.items()), '48 physical slot leaks')
    require(transition(row,b2)==col, 'P104 transition witness')
    # Verify full inverse factor identities for all 208 local basis fields.
    # Different fibers are disjoint: this covers every data column of each global axis map.
    for bank in range(2):
        for k in range(104):
            x={(bank,k,0):Fraction(4)}
            y=dict(x); fiber_word(y,0,0,b2); fiber_word(y,0,0,b2,inverse=True)
            require(y==x, 'local inverse basis')
    # Independent all-grid-input checks on two small rational B fixtures.
    # These exercise both axes, the bank reversal, and all helper roles as untouched fields.
    fixture_columns=0
    for b in ([[1,0]], [[1,-1],[0,1]]):
        n=len(b)+len(b[0])
        for bank in range(2):
            for i in range(n):
                for j in range(n):
                    x={(bank,i,j):Fraction(4), (2,17,0):Fraction(7), (3,9,0):Fraction(-5)}
                    left=transition(encode(x,0,b),b)
                    right=encode(x,1,b,reverse=True)
                    require(left==right,'small full-grid intertwiner')
                    fixture_columns+=1
    require(row != col, 'identity handoff incorrectly accepted')
    # Explicit favorable complete gate inherited as named hypotheses, not supplier replay.
    n,h,m,local,progress=104,72,81,2576,2312
    width=2*n*n+2*n*h; capacity=m*width
    remaining=capacity-n*n-2*n*progress
    bill=2*n*local+remaining
    require(bill-capacity==44096,'unchanged-inventory gate')
    count=sum(c!=0 for r in b2 for c in r)
    return {'schema':'p104-encoded-boundary/1','ports':104,'pivot_ports':list(PIVOTS),
      'physical_dc_witness':{'input_slot':['X',0,0],'input_value':2,'row_extra_Y_slots':48,'column_extra_slots':0,
        'first_leak':list(min(leak.items())[0])+[int(leak[min(leak)])]},
      'local_inverse_basis_columns':208,'small_global_basis_columns':fixture_columns,
      'formal_transition_invoice':{'scope':'homogeneous common-chart factor word only; not physical upper bound',
        'unit_add_sub':2*n*(2*count+96),'halves':2*n*104,'restoring_doubles':2*n*104,
        'nonpivot_signs':2*n*96,'explicit_in_place_slot_swaps':2*n*96,
        'scratch_arrays':0,'full_grid_bank_swaps':0},
      'conditional_gate':{'width':width,'capacity':capacity,'remaining_rank_lower_bound':remaining,
        'rank_bill_lower_bound':bill,'excess':bill-capacity},
      'scope':'exact fixed-slot interface mismatch and formal transition; no actual global P104 pair, native supplier or frontier change'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--write-result',action='store_true');p.add_argument('--result',type=Path,default=HERE/'RESULT.json');a=p.parse_args()
    r=result()
    if a.write_result: a.result.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else: require(json.dumps(read(a.result),sort_keys=True)==json.dumps(r,sort_keys=True),'result mismatch')
    print('PASS_P104_ENCODED_BOUNDARY slots=21632 helpers=14976 dc_leaks=48 gate_excess=44096 no_new_kappa')

if __name__=='__main__': main()
