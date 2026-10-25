#!/usr/bin/env python3
"""Independent exact price/census check for the mixed-width rehosting provider.

Reads only --provider. No producer imports, external paths, network or Git.
All mathematical decisions are exact; receipt intervals are rounded outward.
Validation uses explicit exceptions and remains effective under Python -O.
"""
from argparse import ArgumentParser
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import gzip
import hashlib
import json
import sys
import time

M, W, REPLICAS, CALLS = 64, 28416, 32, 288
LAMBDA = Q(32*M*M, 10**16)
INTERNAL_GRID = 1 << 320
OUTPUT_GRID = 10**72
BASELINE_WORD_SHA = 'fab5e51011239a13a79307f1d079551eef38387a45c9ab315ab6bc83aced8de2'
CANDIDATE_WORD_SHA = '5f301f0d668ded1028b7603c5ea9c88271e390fb9060ce8e118aad7d9927a7fd'
EXPECTED = {1:380448,2:400064,3:22752,4:24160,5:29376,6:17088,7:26784,14:32,42:608}
ROOT_LOWER = Q(1743059363170060183941, 10**24)
ROOT_UPPER = ROOT_LOWER + Q(1, 10**24)
PUBLIC_UPPER = Q(434407954621501888371, 25*10**22)
CHOSEN_B = Q(871, 500000)


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')


def read_bytes(provider, relative):
    path = provider / relative
    need(path.is_file(), 'missing provider file: '+relative)
    return path.read_bytes()


def read_json(provider, relative):
    try:
        return json.loads(read_bytes(provider, relative))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError('invalid JSON file: '+relative) from exc


def load_artifacts(provider, summary):
    need(isinstance(summary.get('artifacts'), dict), 'owner artifact metadata')
    data, pins = {}, {}
    names = ['CHARTS', 'DISPATCH', 'ORDER', 'REMAINDERS', 'SLOTS']
    if (provider/'new-owners/FILL.json.gz').is_file():
        names.append('FILL')
    for name in names:
        need(name in summary['artifacts'], 'artifact metadata: '+name)
        meta = summary['artifacts'][name]
        relative = 'new-owners/'+name+'.json.gz'
        raw = read_bytes(provider, relative)
        try:
            body = gzip.decompress(raw)
        except (OSError, EOFError) as exc:
            raise ValueError('invalid gzip artifact: '+name) from exc
        need(sha(raw) == meta.get('gzip_sha256'), 'gzip hash: '+name)
        need(sha(body) == meta.get('content_sha256'), 'decompressed content hash: '+name)
        need(len(body) == meta.get('uncompressed_bytes'), 'decompressed byte count: '+name)
        data[name] = json.loads(body)
        pins[relative] = dict(gzip_sha256=sha(raw), content_sha256=sha(body), bytes=len(body))
    return data, pins


def candidate_records(records):
    need(sha(canonical(records)) == BASELINE_WORD_SHA, 'frozen baseline literal word hash')
    need(records[23889] == [3,476,660,515,0,3], 'closed COPY edit anchor')
    need(records[33619] == [0,469,517,1,1,32], 'terminal MOVE edit anchor')
    retired = {53,20255,20256,23408,23409,33620}
    moved = {23405,23406,23407,23515,24189,24190,24515}
    out = []
    for i, row in enumerate(records):
        if i == 33619:
            out.append([0,469,0,517,7,32])
        if i not in retired | moved and not (row[0] == 1 and row[5] == 10 and row[2] == 469):
            out.append(row)
        if i == 23889:
            out.extend(records[j] for j in (24189,24190,24515))
            out.append([1,413,50,1,509,2])
            out.extend(records[j] for j in (23405,23406,23407,23515))
    need(sha(canonical(out)) == CANDIDATE_WORD_SHA, 'once-edited candidate literal word hash')
    return out


def census(provider, summary, artifacts):
    need(summary.get('W') == W, 'live W must exclude the nine private families')
    need(summary.get('physical') == W+9 and summary.get('private_reserve') == 9, 'physical/private stock')
    need(summary.get('stages') == 9 and summary.get('replicas') == REPLICAS, 'stage/replica stock')
    dispatch, order = artifacts['DISPATCH'], artifacts['ORDER']
    need(len(dispatch) == CALLS and len(order['calls']) == CALLS, 'complete 288 invocation census')
    expected_calls = {(s,r) for s in range(9) for r in range(REPLICAS)}
    need({(x['stage'],x['replica']) for x in dispatch} == expected_calls, 'all stage/replica dispatches')
    need({(x['stage'],x['replica']) for x in order['calls']} == expected_calls, 'all stage/replica order entries')
    raw_word = read_bytes(provider, 'inputs/WORD.json.gz')
    word = json.loads(gzip.decompress(raw_word))
    records = candidate_records(word['records'])
    need(len(word['start']) == 660 and len(word['final']) == 660, 'ordinary RAW inventory')
    local = Counter(x[4] for x in records if x[0] == 0)
    copies = sum(x[0] == 2 for x in records)
    need(copies == 9 and sum(x[0] == 3 for x in records) == 9, 'guarded COPY/ERASE census')
    local[7] += copies
    idle = Counter()
    keys = set()
    for child, family, axes in artifacts['REMAINDERS']:
        need(type(child) is int and 0 <= child < 10 and type(family) is int and 0 <= family < 222,
             'idle child/family range')
        need((child,family) not in keys, 'duplicate idle factor')
        keys.add((child,family))
        need(isinstance(axes,list) and len(set(axes)) == len(axes), 'distinct idle axes')
        need(all(type(a) is int and 0 <= a < M for a in axes), 'idle ADDRESS range')
        idle[len(axes)] += 1
    need(len(keys) == 2220, 'all 10 by 222 idle factors')
    profile = Counter({r:CALLS*n for r,n in local.items()})
    profile.update({r:REPLICAS*n for r,n in idle.items() if r})
    declared = {int(r):n for r,n in summary['actual_global_profile'].items()}
    need(dict(profile) == declared == EXPECTED, 'independent complete paid profile')
    need(dict(idle) == {int(r):n for r,n in summary['idle_per_replica_including_zero'].items()},
         'all idle heights, including zero returns')
    validate_invoice(profile, summary['W'], LAMBDA)
    return profile, dict(local), dict(idle), dict(
        local_events=len(records), local_opcodes=dict(Counter(x[0] for x in records)),
        canonical_paid_labels=sum(profile.values())//REPLICAS,
        baseline_literal_sha256=BASELINE_WORD_SHA, candidate_literal_sha256=CANDIDATE_WORD_SHA,
        word_container_sha256=sha(raw_word))


def validate_invoice(profile, live_w, fallback):
    need(live_w == W, 'wrong W: private streams are not profitable live stock')
    need(fallback == LAMBDA and fallback > 0, 'complete positive per-QUERY fallback is required')
    need(all(type(r) is int and 0 < r < M and type(n) is int and n > 0 for r,n in profile.items()),
         'proper positive integer paid queries')
    need(dict(profile) == EXPECTED, 'underpriced or changed complete QUERY profile')
    need(sum(profile.values()) == 901312, 'all paid QUERYs')
    need(sum(r*n for r,n in profile.items()) == 1808352, 'full completed rank mass')


def ceildiv(a, b):
    return -((-a)//b)


def log_unit(y):
    need(1 <= y <= 2, 'range-reduced log domain')
    z = (y-1)/(y+1)
    term, total = z, Q(0)
    for j in range(110):
        total += 2*term/(2*j+1)
        term *= z*z
    return total, total+2*term/(221*(1-z*z))


@lru_cache(None)
def log_scaled(x):
    need(x >= 1, 'positive logarithm domain')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    lo, hi = log_unit(x)
    a, b = log_unit(Q(2))
    return ((lo+k*a)*INTERNAL_GRID).__floor__(), ((hi+k*b)*INTERNAL_GRID).__ceil__()


@lru_cache(None)
def power(exponent, base):
    a, b = log_scaled(base)
    xl, xh = (exponent*a).__floor__(), (exponent*b).__ceil__()
    need(0 <= xl <= xh < INTERNAL_GRID//10, 'small nonnegative exponential domain')
    tl = th = sl = sh = INTERNAL_GRID
    for j in range(1,49):
        tl = tl*xl//(j*INTERNAL_GRID)
        th = ceildiv(th*xh, j*INTERNAL_GRID)
        sl += tl
        sh += th
    tail = Q(th,INTERNAL_GRID)*Q(xh,INTERNAL_GRID)/49/(1-Q(xh,INTERNAL_GRID)/50)
    return Q(sl,INTERNAL_GRID), Q(sh,INTERNAL_GRID)+tail


def moment(profile, exponent, live_w=W, fallback=LAMBDA):
    lo = hi = Q(0)
    for r, count in sorted(profile.items()):
        a, b = power(exponent, Q(M,r))
        weight = Q(r*count, M*live_w)
        lo += weight*a
        hi += weight*b
    a, b = power(exponent, Q(M))
    weight = fallback*sum(profile.values())/(M*live_w)
    return lo+weight*a, hi+weight*b


def dec(value):
    with localcontext() as ctx:
        ctx.prec = 78
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def receipt_interval(lo, hi):
    # Internal decisions remain exact; only serialization is outward rounded.
    low = Q((lo*OUTPUT_GRID).__floor__(), OUTPUT_GRID)
    high = Q((hi*OUTPUT_GRID).__ceil__(), OUTPUT_GRID)
    return dict(lower=str(low), upper=str(high), decimal_lower=dec(low), decimal_upper=dec(high))


def rejected(action, label):
    try:
        action()
    except ValueError as exc:
        return str(exc)
    raise ValueError('negative control was accepted: '+label)


def verify(provider):
    started = time.process_time()
    summary = read_json(provider, 'OWNERS.json')
    artifacts, pins = load_artifacts(provider, summary)
    profile, local, idle, counts = census(provider, summary, artifacts)
    public_guard = PUBLIC_UPPER*Q(1001,1000)
    exponents = dict(zero=Q(0), root_lower=ROOT_LOWER, root_upper=ROOT_UPPER,
                     public_plus_point1=public_guard, logical_b=CHOSEN_B,
                     alternative_b=Q(1743,1000000))
    exact = {name:moment(profile,b) for name,b in exponents.items()}
    need(exact['root_lower'][1] < 1 < exact['root_upper'][0], 'strict adjacent root bracket')
    need(exact['public_plus_point1'][1] < 1 and CHOSEN_B > public_guard, 'latest plus .1 percent guard')
    need(exact['zero'][1] < Q(199,200), '200C linear prefactor')
    need(exact['logical_b'][1] < 1-Q(1,2400000), '2400000C precision prefactor')
    need(exact['alternative_b'][0] > 1-Q(1,2400000), 'alternative b cannot reuse old prefactor')
    need(exact['alternative_b'][1] < 1-Q(1,6000000), 'alternative b larger prefactor')
    bad_idle = dict(profile)
    bad_idle[42] -= REPLICAS  # One omitted rank42 remainder per replica.
    controls = []
    for label, p, w, fallback in [
            ('omitted_positive_fallback',profile,W,Q(0)),
            ('underpriced_idle',bad_idle,W,LAMBDA),
            ('private_families_credited_to_W',profile,W+9,LAMBDA)]:
        error = rejected(lambda:validate_invoice(p,w,fallback), label)
        a,b = moment(p,ROOT_UPPER,w,fallback)
        need(b < 1, 'control must falsely pass the certified excluded next tick: '+label)
        controls.append(dict(name=label,validation_rejected=True,reason=error,
                             underpriced_moment_at_excluded_tick=receipt_interval(a,b)))
    rates = {}
    for name, exponent in exponents.items():
        lo, hi = exact[name]
        rates[name] = dict(exponent=str(exponent),moment=receipt_interval(lo,hi),
                          residual=receipt_interval(lo-1,hi-1))
    return dict(status='PASS_PORTABLE_INDEPENDENT_PRICE_CENSUS_AND_SEPARATOR',
        optimized=not __debug__, at_utc=datetime.now(timezone.utc).isoformat(),
        profile=dict(sorted(profile.items())),local_profile=dict(sorted(local.items())),
        idle_per_replica_including_zero=dict(sorted(idle.items())),
        QUERYs=sum(profile.values()),rankmass=sum(r*n for r,n in profile.items()),
        live_W=W,physical=W+9,private_reserve=9,private_has_no_W_credit=True,
        lambda_per_QUERY=str(LAMBDA),fallback_total=str(LAMBDA*sum(profile.values())),
        literal_census=counts,verified_artifact_files=pins,
        optional_FILL_included='FILL' in artifacts,
        artifact_scope='All shipped price artifacts; FILL, when absent, is regenerated by the separate owner audit.',
        moments=rates,root_lower=str(ROOT_LOWER),root_upper=str(ROOT_UPPER),
        public_upper=str(PUBLIC_UPPER),public_plus_point1=str(public_guard),
        matched_root_relative_gain=receipt_interval(ROOT_LOWER/PUBLIC_UPPER-1,ROOT_UPPER/PUBLIC_UPPER-1),
        chosen_logical_b=str(CHOSEN_B),old_prefactors_200_and_2400000_pass=True,
        logical_b_relative_gain=str(CHOSEN_B/PUBLIC_UPPER-1),negative_controls=controls,
        output_interval_grid='10^-72 outward; internal exact rational decisions',
        mathematical_scope='Complete finite price and census only; owner/operator/all-size caller and physical/outer premises remain separate.',
        CPU_seconds=time.process_time()-started)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--provider',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    try:
        need(args.provider.is_dir(), 'provider directory does not exist')
        result = verify(args.provider)
    except (ValueError,KeyError,TypeError,OSError) as exc:
        result = dict(status='FAIL_PORTABLE_PRICE',error=str(exc),optimized=not __debug__)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result),file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],optimized=result['optimized'],
                         root_lower=result['root_lower'],chosen_b=result['chosen_logical_b'],
                         QUERYs=result['QUERYs'],controls=len(result['negative_controls']))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
