#!/usr/bin/env python3
"""Independent compact658 price/census audit: standard library, read-only inputs.

Usage: python -B portable_price.py --provider PATH --output PATH
All decisions are exact rationals. Receipt intervals are rounded outward.
The checker imports neither the provider nor any other project module.
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
import time

M, W, PRIVATE, CALLS, REPLICAS = 64, 28416, 9, 288, 32
FALLBACK = Q(32*M*M, 10**16)
GRID = 1 << 320
OUT_GRID = 10**72
ROOT_LOWER = Q(1744853764761145849274, 10**24)
ROOT_UPPER = ROOT_LOWER + Q(1, 10**24)
CURRENT_UPPER = Q(1743059363170060183942, 10**24)
LOGICAL_B = Q(174481, 10**8)
RECORD_SHA = 'a9507403c2b03c4c6295248da2538909938744683b8c5c771cd3efb6b19f5ced'
EXPECTED_LOCAL = {1:1319, 2:1342, 3:78, 4:39, 5:102, 6:10, 7:18}
EXPECTED = {1:379872, 2:400000, 3:22464, 4:24416, 5:29376,
            6:17088, 7:26496, 10:32, 42:672}
PINS = {
    'inputs/WORD.json.gz': (
        '69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b',
        '99c24c54ca211bd194e1ec668d0fc9e396db323fc2750f6c098e352108499af4', 424692),
    'inputs/GEOMETRY.json.gz': (
        'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022',
        '7aad486877b8c03866b8f1e6f909d12085da347d86aaae891f86f4e2dbc550d1', 200598),
    'new-owners/CHARTS.json.gz': (
        '1fed568d534f901c83bc2e2465afdd714d02b12c5329745c84f3d6112ec7f722',
        '526215f0a0ec56588ba46be3acae60a4e23a157656eaf5f82ec0caab8431a06f', 567881),
    'new-owners/DISPATCH.json.gz': (
        '6e277a656954efc2e50e7e7265bff8fe074603ff5575c892602900ee60097067',
        '626662819f795e0031cdc2083282f93959fa2649d1e416e827733e6315d2eb8f', 4858353),
    'new-owners/ORDER.json.gz': (
        '8a153e3c5086e67735310bc47b2a83a41b55ba8ce102eb9a90e960d49328bbe4',
        '86a35f173d20e9a66af79eaa777ae415141ab99363603f3d5f7a0491070cfb23', 13184),
    'new-owners/REMAINDERS.json.gz': (
        '0f96c293a3cfa5a95d516e2756fc55ba4215ff6bacb48e1346a407eaea0c8550',
        'a3b987752e3e08ea946e4eccf2697f9e12dbbc117ff98a3bdb158a57421c9626', 53263),
    'new-owners/SLOTS.json.gz': (
        'af94b7a3f9cf1956de4c01692e1bb6f119c6af6ef1433dbd9a2382abe9c3778d',
        '7cdca372e32fa60bdcb08476d106a2f5b09762120304be697c6b2ddd504120bb', 69357),
}

def need(value, message):
    if not value:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')

def sha(value):
    return hashlib.sha256(value).hexdigest()

def json_object(raw, label):
    try:
        return json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ValueError('invalid JSON: '+label) from exc

def load_inputs(provider):
    data, receipts = {}, {}
    for relative, (compressed_sha, content_sha, length) in PINS.items():
        path = provider/relative
        need(path.is_file(), 'missing input: '+relative)
        raw = path.read_bytes()
        need(sha(raw) == compressed_sha, 'compressed input hash: '+relative)
        try:
            body = gzip.decompress(raw)
        except (OSError, EOFError) as exc:
            raise ValueError('invalid gzip: '+relative) from exc
        need(sha(body) == content_sha and len(body) == length,
             'decompressed input content/length: '+relative)
        data[relative] = json_object(body, relative)
        receipts[relative] = dict(gzip_sha256=sha(raw), content_sha256=sha(body), bytes=len(body))
    raw = (provider/'OWNERS.json').read_bytes()
    data['OWNERS'] = json_object(raw, 'OWNERS.json')
    receipts['OWNERS.json'] = dict(sha256=sha(raw), bytes=len(raw))
    return data, receipts

def row_rank(rows):
    # Exact SOURCE-frame rank rederived from the original pinned root vectors.
    pivots = {}
    for row in rows:
        values = list(map(Q, row))
        for p, base in sorted(pivots.items()):
            coefficient = values[p]
            if coefficient:
                values = [x-coefficient*y for x,y in zip(values, base)]
        p = next((j for j,x in enumerate(values) if x), None)
        if p is not None:
            coefficient = values[p]
            pivots[p] = [x/coefficient for x in values]
    return len(pivots)

def complete_profile(local, remainders):
    idle, seen = Counter(), set()
    for child, family, axes in remainders:
        need(type(child) is int and 0 <= child < 10 and type(family) is int and 0 <= family < 222,
             'idle child/family range')
        need((child,family) not in seen, 'duplicate idle factor')
        seen.add((child,family))
        need(isinstance(axes,list) and len(set(axes)) == len(axes), 'duplicate idle ADDRESS axis')
        need(all(type(a) is int and 0 <= a < M for a in axes), 'idle ADDRESS axis range')
        idle[len(axes)] += 1
    need(len(seen) == 2220, 'all ten by222 idle factors including zero returns')
    profile = Counter({r:CALLS*n for r,n in local.items()})
    profile.update({r:REPLICAS*n for r,n in idle.items() if r})
    return profile, idle

def validate_invoice(profile, live_w, fallback):
    need(live_w == W, 'nine private families receive no profitable DATA credit')
    need(fallback == FALLBACK and fallback > 0, 'complete positive per-QUERY fallback')
    need(all(type(r) is int and 0 < r < M and type(n) is int and n > 0 for r,n in profile.items()),
         'proper positive integer QUERY invoice')
    need(dict(profile) == EXPECTED, 'complete literal QUERY/idle histogram')

def census(data):
    word, geo, summary = data['inputs/WORD.json.gz'], data['inputs/GEOMETRY.json.gz'], data['OWNERS']
    records = word['records']
    need(sha(canonical(records)) == RECORD_SHA, 'direct compact658 record stream; no old edit replay')
    need(len(word['start']) == len(word['final']) == 658 and word.get('namespace') == 658,
         'actual compact ordinary RAW namespace')
    need(len(records) == 21988 and geo['h'] == 8 and geo['v'] == 111, 'literal geometry/word size')
    need(word['start'][222:] == [0]*436, 'all436 arbitrary dirty helpers begin at zero FRAME')
    state = word['start'][:]+[None]
    local, opcodes, copies, original, frame_ranks = Counter(), Counter(), [], None, {}
    for index, row in enumerate(records):
        need(isinstance(row,list) and len(row) == 6, 'six-field literal record')
        op,d,s,c,f,section = row
        need(type(d) is int and 0 <= d < 658, 'ordinary destination index')
        opcodes[op] += 1
        if op == 0:
            need(original is None and state[d] == s and 0 < f < 8, 'proper MOVE and COPY lifetime')
            state[d] = c
            local[f] += 1
        elif op == 1:
            need(0 <= s <= 658 and d != s and c in (-1,1), 'literal ADD operands/sign')
            need(state[d] == state[s] == f and d != original and (s != 658 or original is not None),
                 'ADD coframe/immutable COPY guard')
        elif op == 2:
            need(s == 658 and original is None and state[658] is None and f == 0 and state[d] == c,
                 'actual clean private COPY lifecycle')
            if c not in frame_ranks:
                need(type(c) is int and 0 <= c < len(geo['frames']), 'COPY SOURCE frame label')
                frame_ranks[c] = row_rank([geo['lines'][j] for j in geo['frames'][c]])
            rank = frame_ranks[c]
            need(rank == 7, 'actual COPY rank from pinned rational SOURCE geometry')
            copies.append(dict(record=index, original=d, SOURCE_frame=c, rank=rank, private=658))
            original, state[658] = d, f
            local[rank] += 1
        else:
            need(op == 3 and s == 658 and original == d and state[d] == c and state[658] == f,
                 'matching ERASE/coframe')
            original, state[658] = None, None
    need(original is None and state == word['final']+[None], 'complete native endpoint frame labels')
    need(len(copies) == opcodes[3] == 9 and dict(local) == EXPECTED_LOCAL, 'all actual paid COPY and MOVE ranks')
    need(opcodes == {0:2899,1:19071,2:9,3:9}, 'complete literal opcode census')
    endpoints = Counter()
    for f in word['final'][222:]:
        if f not in frame_ranks:
            frame_ranks[f] = row_rank([geo['lines'][j] for j in geo['frames'][f]])
        endpoints[frame_ranks[f]] += 1
    need(endpoints == {8:432,4:4}, 'actual ordered helper terminal widths')
    dispatch, order, slots = (data['new-owners/'+n+'.json.gz'] for n in ['DISPATCH','ORDER','SLOTS'])
    expected = {(s,r) for s in range(9) for r in range(REPLICAS)}
    need(len(dispatch) == len(order['calls']) == CALLS and
         {(x['stage'],x['replica']) for x in dispatch} == expected and
         {(x['stage'],x['replica']) for x in order['calls']} == expected, 'all actual invocation descriptors')
    need(len(slots) == 436*9 and {(row[4],row[5]) for row in slots} ==
         {(s,h) for s in range(9) for h in range(436)}, 'all436 helper stage occurrences')
    profile, idle = complete_profile(local, data['new-owners/REMAINDERS.json.gz'])
    need(dict(idle) == {int(r):n for r,n in summary['idle_per_replica_including_zero'].items()}, 'all declared idle returns')
    need(summary['W'] == W and summary['private_family_reserve'] == PRIVATE and
         summary['ordinaryRAW'] == 658 and summary['helpers'] == 436, 'actual stock inventory')
    declared = summary.get('actual_global_profile', summary.get('global_profile'))
    need(isinstance(declared,dict) and dict(profile) == {int(r):n for r,n in declared.items()}, 'owner-summary paid histogram')
    validate_invoice(profile, summary['W'], FALLBACK)
    need(sum(profile.values()) == 900416 and sum(r*n for r,n in profile.items()) == 1808352, 'total QUERY count/rankmass')
    return profile, local, idle, dict(records=len(records),opcodes=dict(opcodes),actual_COPYs=copies,
        canonical_paid_labels=sum(profile.values())//REPLICAS,record_sha256=RECORD_SHA,frame_rank_source='original pinned root vectors',helper_terminal_widths=dict(endpoints))

def ceildiv(a,b):
    return -((-a)//b)

def log_unit(y):
    need(1 <= y <= 2, 'positive log-series domain')
    z = (y-1)/(y+1)
    term, total = z, Q(0)
    for j in range(110):
        total += 2*term/(2*j+1)
        term *= z*z
    return total, total+2*term/(221*(1-z*z))

@lru_cache(None)
def log_scaled(x):
    need(x >= 1, 'log range domain')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    lo, hi = log_unit(x)
    a, b = log_unit(Q(2))
    return ((lo+k*a)*GRID).__floor__(), ((hi+k*b)*GRID).__ceil__()

@lru_cache(None)
def power(exponent, base):
    a, b = log_scaled(base)
    xl, xh = (exponent*a).__floor__(), (exponent*b).__ceil__()
    need(0 <= xl <= xh < GRID//10, 'small positive exponential domain')
    tl = th = sl = sh = GRID
    for j in range(1,49):
        tl = tl*xl//(j*GRID)
        th = ceildiv(th*xh, j*GRID)
        sl += tl
        sh += th
    tail = Q(th,GRID)*Q(xh,GRID)/49/(1-Q(xh,GRID)/50)
    return Q(sl,GRID), Q(sh,GRID)+tail

def moment(profile, exponent, live_w=W, fallback=FALLBACK):
    lo = hi = Q(0)
    for r,count in sorted(profile.items()):
        a,b = power(exponent, Q(M,r))
        weight = Q(r*count, M*live_w)
        lo += weight*a
        hi += weight*b
    a,b = power(exponent,Q(M))
    weight = fallback*sum(profile.values())/(M*live_w)
    return lo+weight*a, hi+weight*b

def decimal(value):
    with localcontext() as context:
        context.prec = 78
        return str(Decimal(value.numerator)/Decimal(value.denominator))

def interval(lo,hi):
    low, high = Q((lo*OUT_GRID).__floor__(),OUT_GRID), Q((hi*OUT_GRID).__ceil__(),OUT_GRID)
    return dict(lower=str(low),upper=str(high),decimal_lower=decimal(low),decimal_upper=decimal(high))

def verify(provider):
    started = time.process_time()
    data,pins = load_inputs(provider)
    profile,local,idle,counts = census(data)
    guard = CURRENT_UPPER*Q(1001,1000)
    cases = dict(zero=Q(0),root_lower=ROOT_LOWER,root_upper=ROOT_UPPER,
                 current_plus_point1=guard,logical_b=LOGICAL_B,smaller_b=Q(218,125000))
    exact = {name:moment(profile,b) for name,b in cases.items()}
    need(exact['root_lower'][1] < 1 < exact['root_upper'][0], 'strict adjacent complete-root bracket')
    need(exact['current_plus_point1'][1] < 1 and LOGICAL_B > guard, 'matched root and actual b clear current upper plus .1 percent')
    need(exact['zero'][1] < Q(199,200), '200C linear induction prefactor')
    need(exact['logical_b'][1] < 1-Q(1,10000000), '10000000C precision induction prefactor')
    need(exact['logical_b'][0] > 1-Q(1,2400000), 'old2400000C does not suffice at chosen logical b')
    need(exact['smaller_b'][1] < 1-Q(1,2400000) and cases['smaller_b'] < guard,
         'smaller old-prefactor exponent does not itself clear .1 percent')
    bad_remainders = [[a,b,list(c)] for a,b,c in data['new-owners/REMAINDERS.json.gz']]
    old = next(row for row in bad_remainders if len(row[2]) == 42)
    old[2] = []  # Retain the factor key: actually omit one full42 idle request per replica.
    bad_idle,_ = complete_profile(local,bad_remainders)
    need(bad_idle[42] == profile[42]-REPLICAS, 'live idle-omission control')
    controls = []
    for label,p,w,fee in [('omit_positive_fallback',profile,W,Q(0)),
                          ('credit_nine_private_families',profile,W+PRIVATE,FALLBACK),
                          ('omit_one_actual_idle42_per_replica',bad_idle,W,FALLBACK)]:
        a,b = moment(p,ROOT_UPPER,w,fee)
        need(b < 1, 'control must falsely accept the certified excluded next tick: '+label)
        try:
            validate_invoice(p,w,fee)
        except ValueError as exc:
            reason = str(exc)
        else:
            raise ValueError('negative control accepted: '+label)
        controls.append(dict(name=label,validation_rejected=True,reason=reason,
            underpriced_moment_at_excluded_next_tick=interval(a,b)))
    for relative,metadata in pins.items():
        raw = (provider/relative).read_bytes()
        need(sha(raw) == metadata.get('gzip_sha256',metadata.get('sha256')), 'input changed during audit: '+relative)
    return dict(status='PASS_PORTABLE_INDEPENDENT_COMPACT658_PRICE',optimized=not __debug__,
        at_utc=datetime.now(timezone.utc).isoformat(),profile=dict(sorted(profile.items())),
        local_profile=dict(sorted(local.items())),idle_per_replica_includingzero=dict(sorted(idle.items())),
        QUERYs=sum(profile.values()),rankmass=sum(r*n for r,n in profile.items()),live_W=W,
        private_reserve=PRIVATE,physical=W+PRIVATE,private_has_no_W_credit=True,
        lambda_per_QUERY=str(FALLBACK),total_fallback=str(FALLBACK*sum(profile.values())),
        literal_census=counts,verified_inputs=pins,root_lower=str(ROOT_LOWER),root_upper=str(ROOT_UPPER),
        current_public_upper=str(CURRENT_UPPER),current_plus_point1=str(guard),
        matched_root_relative_gain=interval(ROOT_LOWER/CURRENT_UPPER-1,ROOT_UPPER/CURRENT_UPPER-1),
        logical_b=str(LOGICAL_B),logical_b_relative_gain=str(LOGICAL_B/CURRENT_UPPER-1),
        induction_prefactors=dict(linear_C=200,precision_C=10000000,old2400000C_at_chosen_b_fails=True),
        moments={name:dict(exponent=str(cases[name]),moment=interval(a,b),residual=interval(a-1,b-1))
                 for name,(a,b) in exact.items()},negative_controls=controls,
        output_rounding='10^-72 outward; exact internal2^-320 interval decisions',
        scope='Finite literal census/complete price and scalar induction constants. Separate native all-RAW, owner, SOURCE/caller, ROW, exact callee and physical/outer contracts are not established by price alone. No whole-kappa claim.',
        CPU_seconds=time.process_time()-started)

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--provider',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    need(args.provider.is_dir(),'provider directory')
    need(args.output.resolve() not in {(args.provider/relative).resolve() for relative in PINS},
         'output must not overwrite an input artifact')
    need(args.output.resolve() != (args.provider/'OWNERS.json').resolve(), 'output must not overwrite owner summary')
    result = verify(args.provider)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],optimized=result['optimized'],QUERYs=result['QUERYs'],
                         logical_b=result['logical_b'],CPU_seconds=result['CPU_seconds'])))

if __name__ == '__main__':
    main()
