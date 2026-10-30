"""Independent endpoint, footprint and invoice checks. Apache-2.0.
Dugongue, with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from itertools import product
import argparse
import ast
import hashlib
import json
from machine import compile_machine, invoice, tape_cost, encode, decode, run, need, SEP

ROOT = Path(__file__).resolve().parent


def authenticate():
    for name, digest in json.loads((ROOT/'INPUTS.json').read_text(encoding='utf8'))['sha256'].items():
        p = (ROOT/name).resolve()
        need(p.is_relative_to(ROOT) and p.is_file(), 'source path')
        need(hashlib.sha256(p.read_bytes()).hexdigest() == digest, 'source hash '+name)


def masks():
    tree = ast.parse((ROOT/'inputs/PR3480-verify.py').read_text(encoding='utf8'))
    found = [ast.literal_eval(x.value) for x in ast.walk(tree) if isinstance(x,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id == 'expected_deltas' for t in x.targets)]
    need(len(found) == 1 and len(found[0]) == 23, 'literal mask source')
    return found[0]


def check_result(machine, result, source, scratch, words, start, work, end, send, cost):
    got, finish = decode(result['tapes'][0], len(words), start)
    need(got == [words[j ^ machine.delta] for j in range(len(words))], 'XOR endpoint')
    need(finish == end, 'framing endpoint')
    need(result['tapes'][1] == scratch, 'dirty buffer restored')
    need(result['heads'] == (start,work), 'both heads restored')
    need(result['steps'] == cost and result['halted'], 'exact first halt')
    for tape, lo, hi in [(0,start,end),(1,work,send)]:
        need(result['minimum'][tape] >= lo and result['maximum'][tape] <= hi, 'scan footprint')
        need(all(lo <= x <= hi for x in result['writes'][tape]), 'write footprint')
    need(all(result['tapes'][0].get(x) == value for x,value in source.items()
             if x < start or x > end), 'arbitrary exterior frame')


def execute(h, delta, r, width, payload=None, dirty=None, start=-11, work=23):
    n, capacity = 1 << h, 1 << r
    words = payload if payload is not None else [tuple(((j*13+7) >> k)&1 for k in range(width)) for j in range(n)]
    dirt = dirty if dirty is not None else [tuple(((j*19+3) >> k)&1 for k in range(width)) for j in range(capacity)]
    source,end = encode(words,start); scratch,send = encode(dirt,work)
    source[start-1]=SEP; source[end+1]=1; source[end+7]=0
    scratch[work-1]=1; scratch[send+1]=SEP; scratch[send+7]=0
    original0,original1 = source.copy(),scratch.copy()
    m = compile_machine(h,delta,r)
    need(not any(q == m.halt for q,_,_ in m.table), 'genuine halt')
    for (q,a,b),(target,w0,w1,m0,m1) in m.table.items():
        need(0 <= q < m.halt and 0 <= target <= m.halt, 'state domain')
        need(a in range(4) and b in range(4), 'read alphabet')
        need(all(w is None or w in range(4) for w in (w0,w1)), 'write alphabet')
        need(m0 in (-1,0,1) and m1 in (-1,0,1), 'unit moves')
    cost = tape_cost(h,delta,r,width)
    result = run(m,source,scratch,start,work,limit=cost+1)
    check_result(m,result,source,scratch,words,start,work,end,send,cost)
    need(result['maximum'][1] <= work+invoice(h,delta,r)['used_records']*(width+1), 'tight dirty prefix')
    need(source == original0 and scratch == original1, 'caller storage unchanged')
    return result['steps']


def run_checks():
    authenticate()
    count = steps = basis = 0
    for h in range(6):
        for delta in range(1 << h):
            for r in range(h+1):
                # Three symbol widths include empty and longer-than-address payloads.
                for width in (0,1,h+2):
                    steps += execute(h,delta,r,width); count += 1
                # Independently count the three exchanges and literal head distances.
                n = 1 << h; swaps = travel = 0
                for k in range(h):
                    if not ((delta >> k)&1): continue
                    half,chunk = 1 << k, min(1 << r,1 << k)
                    previous = 0
                    for block in range(0,n,2*half):
                        for offset in range(0,half,chunk):
                            a = block+offset
                            travel += a-previous+2*half
                            previous = a
                            swaps += 6*chunk
                    travel += n-previous+n
                need(swaps+travel == invoice(h,delta,r)['time_factor'], 'independent route sum')
                need(invoice(h,delta,r)['states'] == 2*(swaps+travel)+1, 'finite control size')
    # Complete joint data/dirt state spaces, not just linear data basis vectors.
    for h in range(3):
        n = 1 << h
        for delta in range(n):
            for r in range(h+1):
                capacity = 1 << r
                if n+capacity > 6: continue
                for bits in product((0,1), repeat=n+capacity):
                    steps += execute(h,delta,r,1,[(x,) for x in bits[:n]],[(x,) for x in bits[n:]])
                    basis += 1
    rows=[]
    for r in range(9):
        factor=sum(invoice(9,d,r)['time_factor'] for d in masks())
        used=max(invoice(9,d,r)['used_records'] for d in masks())
        rows.append({'scratch_capacity_records':1 << r,'maximum_used_records':used,
                     'total_B_coefficient':factor,'total_constant':2*factor})
    # Distinct 9-bit payload labels expose every source address in the literal
    # production dimension. Smaller-buffer
    # production rows are proved formulas, not claimed full executions.
    for delta in masks():
        steps += execute(9,delta,8,9); count += 1
    result={'status':'PASS_DIRTY_BUFFER_XOR','parameter_cases':count,
            'joint_state_cases':basis,'executed_unit_transitions':steps,
            'literal_mask_count':len(masks()),'production_tradeoff':rows,
            'scope':'Exact finite-control replay and informal universal proof; no native ABI join or kappa claim.'}
    return result


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write',action='store_true'); args=parser.parse_args()
    result=run_checks(); path=ROOT/'RESULT.json'
    if args.write: path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    else: need(json.loads(path.read_text(encoding='utf8')) == result, 'frozen receipt')
    print(json.dumps(result))


if __name__ == '__main__': main()
