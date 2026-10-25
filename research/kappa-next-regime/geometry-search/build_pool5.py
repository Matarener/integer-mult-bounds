#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Five-replica R437 packing blocks; complete finite template, no native admission.

R437/local words and slots: ai-nanachi, PR3647. Cross-replica owner pooling:
Rohan Arun, PR3939/3959. Slack-concentration proof: mightyOil, PR1281.
New five-replica construction and source-bound arithmetic: user-directed work
with substantial OpenAI assistance. See README.md for complete scope/credit.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / 'research/kappa-next-regime/sources'
TEMPLATE = SOURCE / 'PR3959/research/rank7-pooled-r437-bit/R437-GLOBAL-TEMPLATE.json.gz'
EXPECTED = SOURCE / 'PR3647/research/bit-p111-r437-gl464-470-20261018/EXPECTED.json'
PRIOR = SOURCE / 'PR3959/research/rank7-pooled-r437-bit/CLAIM.json'
ENGINE = REPO / 'research/native-complex-moment552/engines/moment.py'
PINS = {
    TEMPLATE: '6e03c76f5a4227394ea57e901eb7e93f4d1ee411ccfecd483fd44ea043550494',
    EXPECTED: '67d06bcb90d2307a11975d6b25107a695be477f168f2dc289b8484ba0b7e2de0',
    PRIOR: '496de468b69975ad5da003f32ffaa4e11289eb9df39cb81c4275c27679a2a390',
    ENGINE: '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
}
V, R, PER_REPLICA, STAGES = 111, 437, 888, 9
LOCAL = {1:1320, 2:1344, 3:77, 4:43, 5:102, 6:11, 7:18}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def histogram(value):
    return {int(r): n for r, n in sorted(value.items(), key=lambda x:int(x[0])) if n}


def engine():
    spec = importlib.util.spec_from_file_location('pool5_exact_moment', ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_sources():
    for path, pin in PINS.items():
        need(sha256(path.read_bytes()).hexdigest() == pin, 'source pin: '+str(path))
    raw = gzip.decompress(TEMPLATE.read_bytes())
    expected = json.loads(EXPECTED.read_bytes())
    need(sha256(raw).hexdigest() == expected['template_content_sha256'], 'template content pin')
    return json.loads(raw), expected, json.loads(PRIOR.read_bytes())


def replicate(original, replicas):
    need(replicas > 0 and replicas % 5 == 0, 'replica count positive and divisible by five')
    need((original['replicas'], original['live'], original['m'], original['stages']) == (32,28416,64,9),
         'exact predecessor dimensions')
    seeds = {c['stage']: c for c in original['calls'] if c['replica'] == 0}
    need(set(seeds) == set(range(STAGES)), 'one replica-zero seed per stage')
    # Establish the exact source's parametric symmetry before extending T.
    need(len(original['calls']) == 32*STAGES, 'source call count')
    for call in original['calls']:
        seed = seeds[call['stage']]
        need(call['orientation'] == seed['orientation'] and call['pair'] == seed['pair'], 'source recipe symmetry')
        need(len(call['owners']) == 222+R, 'actual source role count')
        expected = [[family+PER_REPLICA*call['replica'], route] for family, route in seed['owners']]
        need(call['owners'] == expected, 'source owners factor by replica')
    t = deepcopy(original)
    t['replicas'], t['live'] = replicas, PER_REPLICA*replicas
    t['version'] = 'r437-pool5-blocks-T'+str(replicas)
    t['calls'] = []
    for stage in range(STAGES):
        for rep in range(replicas):
            call = deepcopy(seeds[stage])
            call['replica'] = rep
            call['owners'] = [[family+PER_REPLICA*rep, route] for family, route in call['owners']]
            t['calls'].append(call)
    return t


def pool(t):
    occupied = defaultdict(list)
    for child, cp, off, width, stage, helper in t['hosting']['slots']:
        need(width == 8, 'unchanged all-width-eight stock')
        occupied[child, cp].append((off, stage, helper))
    partial = [cp for cp in range(222) if len(occupied[6,cp]) == 2]
    empty = [cp for cp in range(222) if not occupied[6,cp]]
    need(len(partial) == 1 and len(empty) == 12, 'one two-role and twelve empty window-six families')
    partial = partial[0]
    need(sorted(x[0] for x in occupied[6,partial]) == [0,8], 'source compact partial family')
    need(t['hosting']['windows']['6'] == [0,42,[3,4,5,6,7,8]], 'source long idle window')
    calls = {(c['stage'], c['replica']):c for c in t['calls']}
    moves = []
    for first in range(0,t['replicas'],5):
        donors = [(rep,off,stage,helper) for rep in range(first+1,first+5)
                  for off,stage,helper in sorted(occupied[6,partial])]
        destinations = [(partial, off) for off in (16,24,32)] + [(empty[0],off) for off in (0,8,16,24,32)]
        need(len(donors) == len(destinations) == 8, 'complete five-replica block')
        for (rep,off,stage,helper),(cpd,offd) in zip(donors,destinations):
            old = dict(family=PER_REPLICA*rep+partial, child=6, offset=off)
            new = dict(family=PER_REPLICA*first+cpd, child=6, offset=offd)
            owner = calls[stage,rep]['owners'][222+helper]
            need(owner == [old['family'],['hosted',6,off,8]], 'literal old owner matches')
            calls[stage,rep]['owners'][222+helper] = [new['family'],['hosted',6,offd,8]]
            moves.append(dict(stage=stage,call_replica=rep,helper=helper,old=old,new=new))
    t['hosting']['rule'] += '; absolute owners use disjoint five-replica pooling blocks; per-replica slots are predecessor metadata'
    # The old aggregate remainders remain explicit predecessor data, never consumed as the new bill.
    t['pooling'] = dict(block_size=5, block_count=t['replicas']//5, moves=moves,
                        predecessor_slot_metadata_only=True)
    return moves


def recount(t):
    windows = {int(i):value for i,value in t['hosting']['windows'].items()}
    cells = defaultdict(set)
    roles = []
    seen_calls = set()
    local_counts = {}
    for orientation, program in t['local_programs'].items():
        h = Counter()
        for event in program:
            if event[0] == 0 and event[4]: h[event[4]] += 1
            elif event[0] == 2: h[event[5]] += 1
        need(histogram(h) == LOCAL, 'actual '+orientation+' IR paid profile')
        local_counts[orientation] = h
    paid = Counter()
    for call in t['calls']:
        key = call['stage'],call['replica']
        need(key not in seen_calls, 'one stage-replica call')
        seen_calls.add(key)
        need(len(call['owners']) == 222+R, 'all actual local owners')
        paid.update(local_counts[call['orientation']])
        data = {family for family,route in call['owners'][:222]}
        for helper,(family,route) in enumerate(call['owners'][222:]):
            need(route[0] == 'hosted', 'all helpers remain hosted')
            _,child,offset,width = route
            pair,capacity,stages = windows[child]
            need(call['stage'] in stages and pair != call['pair'], 'literal inactive host window')
            need(0 <= family < t['live'] and (family % PER_REPLICA)//222 == pair, 'absolute family pair')
            need(family not in data, 'helper/data family nonaliasing')
            need(width == 8 and 0 <= offset and offset+width <= capacity, 'helper extent')
            new = set(range(offset,offset+width))
            need(not new.intersection(cells[child,family]), 'absolute owner disjoint cells')
            cells[child,family].update(new)
            roles.append([call['stage'],call['replica'],helper,family,child,offset,width])
    need(seen_calls == {(s,r) for s in range(STAGES) for r in range(t['replicas'])}, 'full call domain')
    need(len(roles) == t['replicas']*STAGES*R, 'each helper exactly once')
    idle = Counter()
    records = []
    for child,(pair,capacity,_) in sorted(windows.items()):
        for rep in range(t['replicas']):
            for cp in range(222):
                family = rep*PER_REPLICA+pair*222+cp
                used = cells[child,family]
                need(used == set(range(len(used))), 'compact pending-axis prefix')
                rank = capacity-len(used)
                need(rank > 0, 'nonzero idle remainder in this width-eight family')
                idle[rank] += 1
                records.append([child,rep,cp,family,len(used),rank])
    paid.update(idle)
    need(t['private_centre_reserve'] == 9 and t['bank_padding'] is None and
         t['banks_per_stage'] == t['hosting']['banks_per_stage'] == {str(s):0 for s in range(STAGES)},
         'unchanged nine private-center fields and zero additional banks')
    need(sum(r*n for r,n in paid.items()) == t['replicas']*56511, 'raw rank mass')
    need(64*t['live']-sum(r*n for r,n in paid.items()) == 321*t['replicas'], 'raw deficit')
    need(2*max(paid)**2 < 64**2, 'strict child-rank guard')
    return histogram(paid),histogram(idle),roles,records


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--replicas',type=int,default=35)
    parser.add_argument('--out',type=Path,default=HERE/'pool35')
    args = parser.parse_args()
    need(__debug__, 'assertions required by pinned arithmetic dependency')
    need(not args.out.exists(), 'fresh output directory required')
    original, expected, prior = read_sources()
    t = replicate(original,args.replicas)
    base,base_idle,_,_ = recount(t)
    need(all(n*32 == int(expected['profile'].get(str(r),0))*args.replicas for r,n in base.items()), 'scaled predecessor invoice')
    moves = pool(t)
    profile,idle,roles,records = recount(t)
    q = args.replicas//5
    delta = Counter(idle);delta.subtract(base_idle)
    need(histogram(delta) == {2:2*q,26:-5*q,42:3*q}, 'exact five-block idle delta')
    need(idle == {2:2157*q,4:2220*q,6:2220*q,7:3330*q,42:63*q}, 'complete all-slot optimum inventory')
    m = engine()
    price = m.certify(profile,64,t['live'],True)
    lower,upper = Q(price['lower']),Q(price['upper'])
    prior_lower = Q(prior['bit_pooled'])
    need(lower > prior_lower, 'strict gain over PR3959 pooled32 bit endpoint')
    proof_inputs = {str(path.relative_to(REPO)):pin for path,pin in PINS.items()}
    template_bytes = canonical(t)
    result = dict(status='PASS_POOL5_FINITE_TEMPLATE_AND_EXACT_PRICE', replicas=args.replicas,
        block_size=5, block_count=q, moves=len(moves), stages=9, calls=len(t['calls']),
        helpers_per_call=R, hosted_roles=len(roles), local_profile=LOCAL,
        live=t['live'],physical=t['live']+9,private_center_fields=9,
        productive_family_index_bits=(t['live']+8).bit_length(),
        profile=profile,idle_profile=idle,idle_delta=histogram(delta),
        rank_mass=sum(r*n for r,n in profile.items()),raw_deficit=321*args.replicas,
        paid_requests=sum(profile.values()),maximum_child_rank=max(profile),
        bit_endpoint_lower=str(lower),bit_endpoint_upper=str(upper),
        bit_endpoint_lower_decimal=m.decimal(lower),bit_endpoint_upper_decimal=m.decimal(upper),
        gain_over_PR3959_lower=str(lower-prior_lower),gain_over_PR3959_lower_decimal=m.decimal(lower-prior_lower),
        interval_price={k:v for k,v in price.items() if k in ('lower','upper','lower_endpoint_residual_upper','upper_endpoint_residual_lower','strict_rational_signs')},
        template_content_sha256=sha256(template_bytes).hexdigest(),
        owner_inventory_content_sha256=sha256(canonical(roles)).hexdigest(),
        idle_inventory_content_sha256=sha256(canonical(records)).hexdigest(),
        source_sha256=proof_inputs,
        scope='Complete finite R437 absolute-owner template and outward-rational invoice with inherited fallback envelope. Replica-aware physical CALL/RETURN, native compiler, full supplier and outer admission remain separate obligations. No new admitted kappa is asserted here.')
    args.out.mkdir(parents=True)
    for name,value in [('GLOBAL-TEMPLATE.json.gz',t),('OWNER-INVENTORY.json.gz',roles),('IDLE-INVENTORY.json.gz',records)]:
        (args.out/name).write_bytes(gzip.compress(canonical(value),mtime=0))
    (args.out/'POOL-MOVES.json').write_text(json.dumps(dict(replicas=args.replicas,block_size=5,moves=moves),indent=2,sort_keys=True)+'\n')
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])
    print(json.dumps({k:result[k] for k in ['replicas','moves','physical','paid_requests','bit_endpoint_lower_decimal','gain_over_PR3959_lower_decimal']},sort_keys=True))


if __name__ == '__main__':
    main()
