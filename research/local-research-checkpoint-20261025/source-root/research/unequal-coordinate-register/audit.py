#!/usr/bin/env python3
"""Exact admission audit. Douglas Colkitt / Codex, Apache-2.0.

Uses the standard library and a C++17 compiler, not an SMT solver.
The independent covering search is capped; UNKNOWN never passes this audit.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent


def lines():
    result=[]
    for v in itertools.product((-2,-1,0,1,2),repeat=3):
        nonzero=[x for x in v if x]
        if nonzero and nonzero[0]>0 and sum(x*x for x in v) in (1,2,3,6):
            result.append(v)
    assert len(result)==25
    return result


def matrix(v,alpha):
    norm=sum(x*x for x in v)
    assert 6%norm==0
    return tuple(6*alpha*x*y//norm for x in v for y in v)


def characters():
    return [q for q in itertools.product(range(4),repeat=6) if sum(q[:3])%2]


def cost(q,B):
    b=sum(x*y for x,y in zip(q,(B[0],B[4],B[8],B[1],B[2],B[5])))%4
    return min(b,4-b) # twice the Lee/second-order-rank cost


def table():
    raw_rows={}
    alphabet=[(v,alpha) for v in lines() for alpha in (1,2)]
    for q in characters():
        row=tuple(cost(q,matrix(v,alpha)) for v,alpha in alphabet)
        raw_rows.setdefault(row,q)
    rows=list(raw_rows)
    raw_columns=list(zip(*rows))
    columns=sorted(set(raw_columns)-{(0,)*len(rows)})
    assert len(rows)==108 and len(columns)==19
    compact=[tuple(col[r] for col in columns) for r in range(len(rows))]
    representatives=[]
    for col in columns:
        v,alpha=alphabet[raw_columns.index(col)]
        representatives.append({'line':list(v),'amplitude_residue':alpha})
    # All integer amplitudes are covered: odd residues have equal costs,
    # residue 2 is the second column, and residue 0 contributes nothing.
    for v in lines():
        for q in characters():
            assert cost(q,matrix(v,3))==cost(q,matrix(v,1))
            assert cost(q,matrix(v,4))==0
    return compact,representatives,list(raw_rows.values())


def encode(rows,budget,target):
    return (f'{len(rows)} {len(rows[0])} {budget} {target}\n'
            +'\n'.join(' '.join(map(str,row)) for row in rows)+'\n')


def solve(binary,rows,budget,target):
    proc=subprocess.run([str(binary)],input=encode(rows,budget,target),
                        text=True,capture_output=True,check=True,timeout=70)
    result=json.loads(proc.stdout)
    assert result['result'] in ('sat','unsat'),result
    if result['result']=='sat':
        counts=result['counts']
        assert len(counts)==len(rows[0]) and min(counts)>=0 and sum(counts)<=budget
        assert all(sum(x*y for x,y in zip(row,counts))>=target for row in rows)
    return result


def brute(rows,budget,target):
    C=len(rows[0])
    # Nonnegative scores allow padding a <=budget solution to exactly budget.
    for word in itertools.combinations_with_replacement(range(C),budget):
        if all(sum(row[j] for j in word)>=target for row in rows):return True
    return False


def controls(binary):
    rng=random.Random(109)
    cases=0
    for C in range(1,6):
        for budget in range(5):
            for trial in range(3):
                rows=[[rng.randrange(3) for j in range(C)] for r in range(4)]
                target=rng.randrange(7)
                result=solve(binary,rows,budget,target)
                assert (result['result']=='sat')==brute(rows,budget,target)
                cases+=1
    return cases


def larger_inventory():
    # Calibration only, not a search over larger circuits or a proposed word.
    # Each of four balanced classes contributes 4I; total is 16I.
    inventory=[]
    word=[]
    for v in lines():
        norm=sum(x*x for x in v)
        copies={1:4,2:2,3:1,6:1}[norm]
        alpha=3 if norm==3 else 1
        inventory.append({'line':list(v),'amplitude':alpha,'copies':copies})
        word.extend([matrix(v,alpha)]*copies)
    assert len(word)==40
    summed=tuple(sum(B[j] for B in word) for j in range(9))
    assert summed==(96,0,0,0,96,0,0,0,96)
    minimum=min(sum(cost(q,B) for B in word) for q in characters())
    assert minimum==32
    # Its hypothetical rank-one moment has generous target slack at 0.08.
    assert 40**25 * 3**2 < 48**25
    return {'W':16,'rank_one_calls':40,'inventory':inventory,
            'sum_of_six_times_frames':list(summed),'minimum_doubled_character_cost':minimum,
            'hypothetical_moment_below_one_at':'2/25',
            'status':'Passes determinant and scalar character counts only. No ordering, mixing matrices, second-order matrix identity, or uniform word is supplied.'}


def audit(write=False):
    rows,reps,queries=table()
    encoded=encode(rows,11,8)
    if write:(ROOT/'cover.txt').write_text(encoded)
    else:assert (ROOT/'cover.txt').read_text()==encoded
    with tempfile.TemporaryDirectory(prefix='integer-mult-unequal-') as tmp:
        binary=Path(tmp)/'cover'
        subprocess.run(['c++','-O3','-std=c++17',str(ROOT/'cover.cpp'),'-o',str(binary)],check=True)
        tested=controls(binary)
        negative=solve(binary,rows,11,8)
        positive=solve(binary,rows,12,8)
        assert negative['result']=='unsat'
        assert positive['result']=='sat'
    result={
        'status':'No new supplier or kappa. The specified W=4, <=11-call alphabet is excluded.',
        'model':'Common-target abelian rational shears, arbitrary scalar F2 rank-one idempotents, integer amplitudes of orthogonal projectors on the 25 norm-1/2/3/6 signed directions.',
        'characters':2048,'distinct_character_rows':108,'distinct_nonzero_call_profiles':19,
        'profile_representatives':reps,'row_representatives':[list(q) for q in queries],
        'cover_sha256':hashlib.sha256(encoded.encode()).hexdigest(),
        'independent_integer_exclusion':negative,'twelve_call_positive_control':positive,
        'brute_force_comparison_cases':tested,'larger_inventory_calibration':larger_inventory()}
    dest=ROOT/'certificate.json'
    if write:dest.write_text(json.dumps(result,indent=2)+'\n')
    else:assert json.loads(dest.read_text())==result,'certificate drift'
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true')
    args=ap.parse_args();out=audit(args.write)
    print(json.dumps({k:out[k] for k in ('status','independent_integer_exclusion',
          'twelve_call_positive_control','brute_force_comparison_cases')},indent=2))
