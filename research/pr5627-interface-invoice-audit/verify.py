#!/usr/bin/env python3
"""Audit the emitted PR5627 word and its recursive invoice without source code imports.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def spans(vectors):
    values = {0}
    for v in vectors:
        need(type(v) is int and 0 < v < 512 and v not in values, 'binary basis')
        values |= {x ^ v for x in tuple(values)}
    return values


@lru_cache(None)
def coefficient(text):
    q = Fraction(text)
    need(q != 0 and q.denominator & (q.denominator-1) == 0, 'dyadic coefficient')
    return q.numerator, q.denominator.bit_length()-1


def replay(word):
    public, owned = word['public'], word['owned_fields']
    n = public+owned
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    powers = [0]*n
    frame = word['initial']+[None]*owned
    chart = [spans(b) for b in word['frames']]
    active = set(); peak = 0; births = 0; nonzero_clear = 0
    paid = Counter(); operations = Counter(); scalar = 0
    for pos, event in enumerate(word['program']):
        op, dst = event[:2]
        need(type(dst) is int and 0 <= dst < n, 'destination index')
        operations[op] += 1
        if op == 'MOVE':
            _, _, old, new, private = event
            need(frame[dst] == old and private == (dst in active), 'MOVE state')
            need(chart[new] < chart[old] if private else chart[old] < chart[new], 'MOVE nesting')
            paid[abs(len(word['frames'][new])-len(word['frames'][old]))] += 1
            frame[dst] = new
            continue
        if op in ('INIT', 'CLEAR'):
            need(dst >= public, 'public field erased')
            if op == 'INIT':
                need(dst not in active, 'duplicate INIT')
                active.add(dst); births += 1; peak = max(peak, len(active)); frame[dst] = event[2]
            else:
                need(dst in active and frame[dst] == event[2], 'CLEAR state')
                nonzero_clear += bool(any(rows[dst])); active.remove(dst); frame[dst] = None
            rows[dst] = [0]*n; powers[dst] = 0; scalar += 2
            continue
        num, exponent = coefficient(event[-2]); f = event[-1]
        need(frame[dst] == f, 'scalar destination chart')
        if op == 'SCALE':
            need(abs(num) & (abs(num)-1) == 0, 'SCALE unit')
            rows[dst] = [num*x for x in rows[dst]]; powers[dst] += exponent
            scalar += 2*(abs(abs(num).bit_length()-1-exponent)+int(num < 0))
        else:
            need(op in ('ADD', 'COPY'), 'opcode')
            src = event[2]
            need(type(src) is int and 0 <= src < n and src != dst and frame[src] == f, 'scalar source chart')
            if op == 'COPY':
                need(dst in active and not any(rows[dst]), 'COPY precondition')
                rows[dst] = [num*x for x in rows[src]]; powers[dst] = powers[src]+exponent
            else:
                level = max(powers[dst], powers[src]+exponent)
                left = 1 << (level-powers[dst]); right = num << (level-powers[src]-exponent)
                rows[dst] = [left*x+right*y for x, y in zip(rows[dst], rows[src])]; powers[dst] = level
            scalar += 2*(2+abs(num).bit_length()+abs(num).bit_count()+exponent)
        while powers[dst] and not any(x & 1 for x in rows[dst]):
            rows[dst] = [x//2 for x in rows[dst]]; powers[dst] -= 1
    need(not active and frame[:public] == word['final'], 'final charts and owned lifetimes')
    live = set(word['live']); main = live | {x+112 for x in live}
    need(len(live) == len(word['ports']) == 104 and len(main) == 208, 'main inventory')
    for i, row in enumerate(rows):
        expected = [0]*n
        if i < public:
            expected[i] = 1 << powers[i]
            if i-112 in live: expected[i-112] = 1 << powers[i]
        need(row == expected, f'endpoint row {i}')
    helpers = Counter()
    for i in range(public):
        if i not in main:
            a, b = word['initial'][i], word['final'][i]
            need(chart[a] < chart[b], 'strict helper target')
            helpers[len(word['frames'][b])-len(word['frames'][a])] += 1
    return dict(paid=dict(paid), helpers=dict(helpers), public_inputs=public, owned_fields=owned, owned_lifetimes=births, peak_owned_fields=peak, real_scalar_allowance=scalar, operations=dict(operations), endpoint_coefficients=n*n, nonzero_owned_clears=nonzero_clear, paid_rank_mass=sum(r*c for r,c in paid.items()))


def invoice(local, controller):
    targets = Counter(); paid = Counter(); events = Counter()
    for e in controller['physical_events']:
        events[e[0]] += 1
        if e[0] == 'LOCAL':
            need(e[3] is False, 'forward invocation')
            targets.update(local['helpers']); paid.update(local['paid'])
        elif e[0] == 'IDLE': paid[8*len(e[2])] += 208
        elif e[0] == 'QUERY_SHEAR': paid[1] += 104
    for t in controller['diagonal']:
        targets[1+8*sum(t[1:])] += 104
    need((events['LOCAL'],events['QUERY_SHEAR'],events['IDLE']) == (18,15,15), 'caller census')
    return dict(targets=dict(targets), paid=dict(paid), paid_calls=sum(paid.values()), productive_fields=sum(targets.values()), rank_mass_surplus=sum(r*c for r,c in targets.items())-sum(r*c for r,c in paid.items()))


def logarithm(x):
    exponent = x.bit_length()-1
    def series(y):
        total = 2*sum((y**(2*j+1)/ (2*j+1) for j in range(48)), Fraction(0))
        error = 2*y**97/(97*(1-y*y))
        return total, total+error
    a, b = series(Fraction(1,3))
    c, d = series(Fraction(x-(1 << exponent), x+(1 << exponent)))
    return exponent*a+c, exponent*b+d


@lru_cache(None)
def power(rank, kappa):
    loglo, loghi = logarithm(rank)
    def partial(x, degree):
        term = Fraction(1); total = term
        for i in range(1, degree+1):
            term *= -x/i; total += term
        return total
    need(0 <= kappa*loghi < 1, 'alternating exponential range')
    return rank*partial(kappa*loghi,17), rank*partial(kappa*loglo,16)


def margin(bill, kappa):
    lower = upper = Fraction(0)
    for rank in set(bill['targets']) | set(bill['paid']):
        count = bill['targets'].get(rank,0)-bill['paid'].get(rank,0)
        a,b = power(rank,kappa)
        lower += count*(a if count >= 0 else b); upper += count*(b if count >= 0 else a)
    need(lower <= upper, 'interval order')
    scale = 10**24
    lo = lower.numerator*scale//lower.denominator
    hi = -((-upper.numerator*scale)//upper.denominator)
    return {'lower_numerator':lo,'upper_numerator':hi,'denominator':scale}


def reject(action):
    try: action()
    except ValueError: return
    raise ValueError('invalid control accepted')


def run():
    for s in json.loads((HERE/'SOURCE-CONTEXT.json').read_text()):
        need(hashlib.sha256((HERE/s['file']).read_bytes()).hexdigest() == s['sha256'], 'source bytes')
    word = json.loads(gzip.decompress((HERE/'inputs/PR5627-WORD.json.gz').read_bytes()))
    source = json.loads((HERE/'inputs/PR5627-RESULT.json').read_text())
    controller = json.loads((ROOT/'research/p104-productive-controller/CONTROLLER.json').read_text())
    local = replay(word)
    for key, value in source['local'].items():
        actual = local[key]
        if isinstance(actual,dict): actual = {str(k):v for k,v in actual.items()}
        need(actual == value, 'source local result: '+key)
    bill = invoice(local,controller)
    for key,value in bill.items():
        if isinstance(value,dict): value = {str(k):v for k,v in value.items()}
        need(value == source['complete_cost'][key], 'source complete bill: '+key)
    intervals = {}
    for label, number, sign in [('claim','.00310440546',1),('tested','.003104405465',1),('root_lower','.00310440547057',1),('root_upper','.00310440547058',-1)]:
        interval = margin(bill,Fraction(number));need(interval['lower_numerator'] > 0 if sign == 1 else interval['upper_numerator'] < 0, 'raw crossing sign')
        intervals[label] = interval
    derivative_upper = Fraction(0)
    for rank in set(bill['targets']) | set(bill['paid']):
        count = bill['targets'].get(rank,0)-bill['paid'].get(rank,0)
        loglo, loghi = logarithm(rank)
        derivative_upper -= count*(power(rank,Fraction('.0034'))[0]*loglo if count >= 0 else rank*loghi)
    need(derivative_upper < 0, 'unique raw crossing on the BIT interval')
    derivative_bound = -((-derivative_upper.numerator*10**12)//derivative_upper.denominator)
    controls = 0
    for name in ['missing_input_basis','wrong_scale','public_erasure','lost_owned_clear']:
        bad = deepcopy(word)
        if name == 'missing_input_basis': bad['program'].pop(next(i for i,e in enumerate(bad['program']) if e[0] == 'ADD'))
        elif name == 'wrong_scale':
            i = next(i for i,e in enumerate(bad['program']) if e[0] == 'SCALE');bad['program'][i][-2] = '2'
        elif name == 'public_erasure': bad['program'].insert(0,['INIT',0,word['initial'][0]])
        else: bad['program'].pop(max(i for i,e in enumerate(bad['program']) if e[0] == 'CLEAR'))
        reject(lambda: replay(bad)); controls += 1
    bad = deepcopy(local);bad['helpers'][2] += 1
    reject(lambda: need(invoice(bad,controller) == bill,'unremoved H2 target'));controls += 1
    bad = deepcopy(controller);bad['physical_events'].pop(next(i for i,e in enumerate(bad['physical_events']) if e[0] == 'IDLE'))
    reject(lambda: invoice(local,bad));controls += 1
    return dict(status='PASS_PR5627_INTERFACE_INVOICE_AUDIT',local=local,complete_bill=bill,raw_intervals=intervals,raw_derivative_upper_numerator=derivative_bound,raw_derivative_denominator=10**12,rejection_controls=controls,source_code_imports=0,limits=['Native phases, physical caller execution, compiler and outer conditions are not replayed.','Owned CLEAR is the inherited erasure operation, not restoration of an arbitrary dirty input.','This is a separate implementation check, not independent human or formal acceptance.','No new kappa and no selected-frontier change.'])


if __name__ == '__main__':
    result = json.loads(json.dumps(run(),sort_keys=True))
    if '--write' in sys.argv: (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: need(result == json.loads((HERE/'RESULT.json').read_text()),'receipt mismatch')
    print(result['status'])
