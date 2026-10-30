"""Exact one-cut delivery budget. zxv, with OpenAI Codex assistance. Apache-2.0."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
from copy import deepcopy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = 'research/p104-helper470-twin-rung-removal/RESULT.json'
WORD = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def log_bounds(q, terms=32):
    """2 atanh(z), with 0 <= z <= 1/3 and an exact geometric tail."""
    q = Q(q)
    need(1 <= q <= 2, 'range-reduced logarithm')
    z = (q-1)/(q+1)
    low = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
    tail = 2*z**(2*terms+1)/(Q(2*terms+1)*(1-z*z))
    return low, low+tail


def integer_log(r):
    k = r.bit_length()-1
    a, b = log_bounds(Q(r, 1 << k))
    c, d = log_bounds(2)
    return a+k*c, b+k*d


def p2(x):
    return 1-x+x*x/2


def p3(x):
    return p2(x)-x*x*x/6


def budget(record):
    c = record['complete_cost']
    target = {int(r): n for r, n in c['targets'].items()}
    paid = {int(r): n for r, n in c['paid'].items()}
    n = c['full_forward_calls']
    h = max(map(int, record['local']['helpers']))
    lo, hi = Q(c['kappa']), Q(c['ordinary_BIT']['admitted'])
    need(n == 18 and h == 9 and lo == Q(781451,250000000) and hi == Q(17,5000),
         'source-bound contract')
    need(sum(target.values()) == c['productive_fields'] == 13444 and
         sum(paid.values()) == c['paid_calls'] == 66834, 'complete inventory counts')
    need(sum(r*v for r,v in target.items())-sum(r*v for r,v in paid.items()) == 760,
         'complete rank-mass surplus')
    logs = {r: integer_log(r) for r in set(target)|set(paid)}
    need(all(0 <= hi*b < Q(1,50) for a,b in logs.values()), 'Taylor interval')
    old_upper = sum(v*r*p2(lo*logs[r][0]) for r,v in target.items()) - sum(
        v*r*p3(lo*logs[r][1]) for r,v in paid.items())
    derivative_upper = sum(v*r*logs[r][1] for r,v in paid.items()) - sum(
        v*r*logs[r][0]*(1-hi*logs[r][1]) for r,v in target.items())
    need(old_upper < Q(13,200), 'old raw margin upper bound')
    need(derivative_upper < -234000, 'whole-interval decreasing raw margin')
    need(log_bounds(2)[1] < Q(7,10), 'rational logarithm bound')
    per_coordinate = 2*n*h*(Q(7,10)*hi)/(1-Q(7,10)*hi)
    need(per_coordinate == Q(12852,16627) < Q(773,1000), 'two-channel credit envelope')
    final_upper = Q(13,200)+per_coordinate-1
    need(final_upper < -Q(162,1000), 'one charged coordinate fails at every allowed kappa')
    return dict(local_calls=n, max_helper_rank=h, admitted_bit=str(hi), current_kappa=str(lo),
                old_margin_upper='13/200', derivative_upper='-234000',
                credit_upper_per_added_coordinate=str(per_coordinate),
                charged_margin_upper_at_d_one=str(final_upper),
                interval=[str(lo), str(hi)], source_counts=[13444,66834])


def controls(record):
    count = 0
    for r in range(2,10):
        for a in range(1,r):
            need(4*a*(r-a) <= r*r, 'binary split Jensen control')
            count += 1
    need(5*1-(-2)*(-2) == 1, 'PR6064 sharp bordering fixture')
    need(Q(12852,16627) > 0, 'free-coordinate contract is not excluded')
    need(2*Q(12852,16627) > 1, 'shared delivery escapes this price screen')
    rejected = []
    for name, change in (
        ('extra_paid_job', lambda r: r['complete_cost']['paid'].__setitem__('1',41503)),
        ('new_rank_ten_target', lambda r: r['local']['helpers'].__setitem__('10',1)),
        ('changed_local_multiplicity', lambda r: r['complete_cost'].__setitem__('full_forward_calls',19)),
        ('changed_bit_cap', lambda r: r['complete_cost']['ordinary_BIT'].__setitem__('admitted','1/200'))):
        damaged = deepcopy(record)
        change(damaged)
        try:
            budget(damaged)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('changed contract accepted: '+name)
    return dict(binary_splits=count, sharp_two_channel_border=True,
                free_delivery_outside_exclusion=True, shared_delivery_outside_exclusion=True,
                rejected_contracts=rejected)


def calculate():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'],
                 'source bytes: '+pin['path'])
    old = json.loads((HERE/'PREDECESSOR.json').read_text())
    need(sha256((HERE/old['retained_path']).read_bytes()).hexdigest() == old['sha256'],
         'retained PR6064 bytes')
    record = json.loads((ROOT/RESULT).read_text())
    result = budget(record)
    path = ROOT/'research/p104-helper-split-exhaustion/splitcensus.py'
    spec = importlib.util.spec_from_file_location('retained_matarener_census', path)
    census = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(census)
    word = json.loads(gzip.decompress((ROOT/WORD).read_bytes()))
    receipts = {}
    for mode in ('group','boundary'):
        counts, records = census.census(word, in_support=mode, out_support=mode)
        need(counts['evaluations'] == 8734 and counts['groups'] == 69 and
             counts['helpers'] == 562 and counts['witnesses'] == 0, 'selected census contract')
        need(all(r['kind'] in ('F1zero','F2zero') for r in records), 'explicit orthogonality exclusions')
        receipts[mode] = dict(counts=counts, classes=len(records),
                              classes_sha256=sha256(json.dumps(records,sort_keys=True,
                                  separators=(',',':')).encode()).hexdigest())
    v = {0:Q(1)}
    need(census.decide([(v,v)],[(v,v)])[0] == 'witness', 'synthetic legal cut')
    need(census.decide([(v,v)],[({1:Q(1)},v)])[0] == 'F1zero', 'orthogonal cut')
    need(census.decide([(v,v)],[(v,{1:Q(1)})])[0] == 'F2zero', 'boundary mismatch')
    result.update(status='PASS_DYADIC_CUT_DELIVERY_BUDGET',
                  selected_full_chart_census=receipts, controls=controls(record))
    return result


def main():
    result = calculate()
    need(result == json.loads((HERE/'RESULT.json').read_text()), 'committed receipt')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
