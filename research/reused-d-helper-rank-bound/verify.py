#!/usr/bin/env python3
"""Check shared-D rank-bound fixtures and the retained compact BIT invoice.

Ali Romman, substantial OpenAI Codex assistance; Apache-2.0.
The all-size result is the written rank proof, not a finite search conclusion.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for record in manifest['files']:
        if record['usage'] == 'input':
            need(sha256((ROOT / record['path']).read_bytes()).hexdigest() == record['sha256'],
                 'Changed live source: ' + record['path'])


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            row ^= bit
            value ^= b[bit.bit_length() - 1]
        out.append(value)
    return out


def plus(a, b):
    return [x ^ y for x, y in zip(a, b)]


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            key = row.bit_length() - 1
            if key in pivots:
                row ^= pivots[key]
            else:
                pivots[key] = row
                break
    return len(pivots)


def product(a, b):
    # Support masks 0,1,2,3 denote I,q,d,qd. Repeated q or d gives zero.
    n = len(a[0])
    out = [[0] * n for _ in range(4)]
    for i in range(4):
        for j in range(4):
            if not i & j:
                out[i | j] = plus(out[i | j], multiply(a[i], b[j]))
    return out


def source_profile():
    source = json.loads((ROOT / 'research/bit-compact-productive-controller/RESULT.json').read_text())
    local, invoice = source['local']['forward'], source['invoice']
    paid = Counter({int(r): count for r, count in local['paid'].items()})
    helpers = Counter({int(r): count for r, count in local['helper_ranks'].items()})
    need(paid == {1:1319, 2:1342, 3:78, 4:39, 5:102, 6:10, 7:18}, 'Retained compact paid profile')
    need(helpers == {4:4, 8:432}, 'Retained compact helper profile')
    need(invoice['thick_calls'] == 18 and invoice['thin_queries'] == 15 * 111, 'Retained caller counts')
    expected = Counter({r: 18 * count for r, count in paid.items()})
    expected[1] += invoice['thin_queries']
    for width, count in ((14,444),(21,444),(28,444),(35,444),(42,444),(49,444),(56,444),(63,222)):
        expected[width] += count
    need(expected == {int(r): count for r, count in invoice['paid'].items()}, 'Join to complete retained paid invoice')
    targets = Counter({int(r): count for r, count in invoice['targets'].items()})
    need(targets[4] == 18 * helpers[4] and targets[8] == 18 * helpers[8], 'Join every retained helper target')
    mass = lambda values: sum(r * count for r, count in values.items())
    need(mass(targets) - mass(expected) == invoice['rank_surplus'] == 753, 'Distinct-fresh-D source positive control')
    gap = mass(paid) - mass(helpers)
    need(gap == 2 * 111 * 7 + 63, 'Source centre debt after all helper credits')
    need(max(paid) == 7 and set(helpers) == {4,8}, 'Power-moment rank bounds')
    return paid, helpers, {'paid_rank_mass': mass(paid), 'helper_rank_mass': mass(helpers),
                           'gap': gap, 'centre_debt': 63, 'source_distinct_D_surplus': 753}


def word(reused):
    n = sum(r + 2 for r in reused)
    eye, zero = [1 << i for i in range(n)], [0] * n
    letters, start = [], 0
    for r in reused:
        need(type(r) is int and 0 <= r <= 3, 'Available full-rank helper banks')
        e, query = list(zero), list(zero)
        for j in range(start, start + r + 2):
            e[j] = 1 << j
        query[start] = 1 << (start + 1)
        for j in range(start + 2, start + r + 2):
            query[j] = 1 << j
        first, second = list(zero), list(zero)
        first[start + 1] = 1 << start
        second[start] = second[start + 1] = (1 << start) | (1 << (start + 1))
        need(multiply(e,e) == e and rank(e) == r + 2, 'FULL projector')
        need(multiply(e,query) == multiply(query,e) == query, 'FULL support')
        need(rank(plus(e,query)) == 2, 'FULL defect rank')
        for thin in (first, second):
            need(rank(thin) == 1 and not any(multiply(thin,thin)), 'THIN rank-one nilpotent')
        letters += [[eye,query,e,query], [eye,first,zero,zero], [eye,second,zero,zero]]
        start += r + 2
    return letters, eye, zero


def evaluate(letters, eye, zero):
    value = [eye,zero,zero,zero]
    for letter in letters:
        value = product(letter,value)
    return value


def invoice(n, reused, thin, paid, helpers):
    f = len(reused)
    need(all(111 * r <= helpers[8] for r in reused), 'Per-call productive helper debit')
    children = Counter({r: f * count for r, count in paid.items()})
    children[1] += 111 * thin
    targets = Counter({r: f * count for r, count in helpers.items()})
    targets[8] += 111 * (n - sum(reused))
    contract = {'model':'mixed-target-unnormalized-power-v1',
                'rank_semantics':'H_r costs r^(1-C); every recycled rank-eight helper is debited once',
                'ambient_rank':8,
                'boundary':'Complete formal shared-D FULL/THIN unit on all original fields; independent direct Gaussian evaluation is the comparison'}
    return {'schema':'integer-mult-recursive-invoice/v1', 'contract':contract,
            'paid':dict(sorted((str(r),count) for r,count in children.items())),
            'targets':dict(sorted((str(r),count) for r,count in targets.items()))}


def comparator():
    path = ROOT / 'scripts/compare_recursive_invoices.py'
    spec = importlib.util.spec_from_file_location('shared_d_invoice',path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    exec(compile(path.read_bytes(),str(path),'exec',optimize=0),module.__dict__)
    return module


def produce():
    authenticate()
    paid, helpers, source = source_profile()
    compare = comparator()
    examples = []
    families = [[0] * (n // 2) for n in (2,4,8,16,32,64,128,256)]
    families += [[1],[2],[3],[0,1,3],[3,2,1,0]]
    for reused in families:
        letters, eye, zero = word(reused)
        n, f, h = len(eye), len(reused), 2 * len(reused)
        need(evaluate(letters,eye,zero) == [eye,eye,eye,eye], 'Complete four-coefficient endpoint')
        total_width = sum(r + 2 for r in reused)
        need(total_width == n and h == 2*n - 2*sum(r+1 for r in reused), 'Attained rank inequalities')
        bill = invoice(n,reused,h,paid,helpers)
        mass = lambda side: sum(int(r)*count for r,count in bill[side].items())
        need(mass('targets') - mass('paid') == -63 * f, 'Sharp complete rank-mass loss')
        direct = dict(bill,paid=dict(bill['targets']))
        comparison = compare.compare_invoices(direct,bill)
        need(comparison['classification'] == 'uniformly_worse', 'Direct evaluation costs less at every concave tariff')
        examples.append({'streams_per_port':n, 'main_fields':111*n, 'full_calls':f, 'thin_packets':h,
                         'thin_H1_calls':111*h, 'recycled_H8_fields':111*sum(reused), 'reused_helpers_per_port':reused,
                         'endpoint':'I+qI+dI+qdI', 'rank_mass_surplus':-63*f,
                         'signed_invoice_preflight':comparison['classification']})
    controls = []
    letters, eye, zero = word([1])
    for omitted in (0,1,2):
        need(evaluate([letter for i,letter in enumerate(letters) if i != omitted],eye,zero) != [eye,eye,eye,eye],
             'Omitted call control must fail')
        controls.append({'mutation':'omit_call_'+str(omitted), 'result':'REJECT_ENDPOINT'})
    bad = [[list(row) for row in letter] for letter in letters]
    bad[0][3] = list(zero)
    need(evaluate(bad,eye,zero) != [eye,eye,eye,eye], 'Missing mixed coefficient control')
    controls.append({'mutation':'omit_full_qd_coefficient', 'result':'REJECT_ENDPOINT'})
    honest = invoice(3,[1],2,paid,helpers)
    false_targets = dict(honest['targets']); false_targets['8'] += 111
    false_surplus = sum(int(r)*c for r,c in false_targets.items()) - sum(int(r)*c for r,c in honest['paid'].items())
    need(false_surplus == 825 and examples[8]['rank_mass_surplus'] == -63, 'Missing debit creates a false positive')
    debit_counterfactual = {'omitted_recycled_H8_debits':111,
                            'honest_rank_surplus':-63, 'false_rank_surplus':false_surplus}
    relaxation_checks = 0
    for f in range(1,5):
        for each in (0,1,431,432):
            recycled = f * each
            width = 222 * f + recycled
            for n in sorted({1,111*f,222*f,width-1,width}):
                thin = max(0,2*n-222*f-2*recycled)
                surplus = 8*n - 1617*f - 8*recycled - thin
                upper = 6*(n-width)-63*f
                need(surplus <= upper <= -63*f, 'Arbitrary helper-count rank-mass relaxation')
                relaxation_checks += 1
    # The all-moment proof uses 2**(-t)<=1, not floating-point root samples.
    coefficient = source['centre_debt'] + 4 * helpers[4] - 8 * helpers[4]
    need(coefficient == 47 > 0, 'Positive exact all-power loss coefficient')
    return {'status':'PASS_SHARED_D_HELPER_REUSE_RANK_BOUND', 'source':source,
            'theorem':{'total_width':'M=2*v*f+s>=n', 'thin_bound':'h>=2*n-2*v*f-2*s',
                       'rank_mass_bound':'Delta_1<=(a-1)*(n-M)-delta*f<=-delta*f',
                       'compact_power_bound':'Delta_t<=-f*8^(t-1)*(79-32*2^(-t))<=-47*f*8^(t-1)<0 for 0<=t<=1'},
            'attaining_examples':examples, 'controls':controls, 'debit_counterfactual':debit_counterfactual,
            'integer_relaxations_checked':relaxation_checks,
            'scope':'Characteristic-two common-D formal FULL/THIN alphabet; ordinary constant scalar bases; recycle only autonomous H8 helpers. Distinct D blocks, changed native operations and general callers are outside this result.',
            'new_supplier':False, 'new_kappa':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true',help='Write the result for package authors.')
    args = parser.parse_args()
    result = produce()
    payload = json.dumps(result,sort_keys=True,indent=2)+'\n'
    target = HERE/'RESULT.json'
    if args.emit:
        target.write_text(payload)
    else:
        expected = json.dumps(json.loads(target.read_text()),sort_keys=True,indent=2)+'\n'
        need(payload == expected,'Saved typed mathematical receipt differs')
    print(result['status'],json.dumps({'attaining_examples':len(result['attaining_examples']),
                                     'controls':len(result['controls']), 'source_gap':result['source']['gap']},sort_keys=True))


if __name__ == '__main__':
    main()
