#!/usr/bin/env python3
"""Restrict the actual R438 owner allocation and return deleted helper work.

No new hosting optimum or terminal-child scratch allocation is asserted. The
old pending-projector audit is rerun on every surviving physical owner role.
Apache-2.0; substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bit_cap_copy_local as cap

HERE = Path(__file__).resolve().parent
REPO = Path('/Users/ross/git/math/integer-mult-bounds')
PROJECTOR = REPO/'research/r438-rehost-projectors/verify.py'
LAYOUT = REPO/'research/bit-r438-transport-rehost/verify_rehost.receipt.json'
CERTIFICATE = REPO/'research/r438-native-rehost/CERTIFICATE.json'
need = cap.need


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('retained_r438_projector',PROJECTOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.source_check()
    _,children,windows = module.chronology()
    layout = json.loads(LAYOUT.read_bytes())['placement']
    slots,old_remaining = module.expand(layout['selection'],children,windows,438)
    old,_,_ = module.audit(slots,children,windows,438)
    removed = [slot for slot in slots if 249 <= slot[5] <= 257]
    need(len(removed) == 81 and Counter(s[4] for s in removed) == Counter({s:9 for s in range(9)}),'removed owner-role coverage')
    new_slots = [slot[:5]+(slot[5]-(9 if slot[5] > 257 else 0),)
                 for slot in slots if not 249 <= slot[5] <= 257]
    new,_,complement = module.audit(new_slots,children,windows,429)
    old_hist = Counter(old['idle_per_replica_including_zero'])
    new_hist = Counter(new['idle_per_replica_including_zero'])
    need(sum(r*n for r,n in new_hist.items())-sum(r*n for r,n in old_hist.items()) == 648,
         'deleted helper work not returned')
    # Every removed whole helper contributes exactly eight previously hosted
    # axes to its same physical deadline remainder. Gaps are retained exactly;
    # no free repacking or changed owner coordinates are assumed.
    for c in children:
        for copy in range(222):
            freed = sum(slot[3] for slot in removed if slot[0] == c['idx'] and slot[1] == copy)
            need(complement[c['idx'],copy].bit_count() == old_remaining[c['idx'],copy]+freed,
                 'physical deadline remainder differs from removed slot width')
    certificate = json.loads(CERTIFICATE.read_bytes())
    baseline = Counter({int(r):n for r,n in certificate['pipeline']['candidate']['hosted']['invoice']['bit_profile'].items()})
    old_local = Counter({int(r):n for r,n in certificate['local']['candidate']['profile'].items()})
    new_local = Counter({1:1298,2:1342,3:79,4:44,5:93,6:11,7:9})
    full = Counter(baseline)
    full.subtract({r:288*n for r,n in old_local.items()})
    full.update({r:288*n for r,n in new_local.items()})
    full.subtract({r:32*n for r,n in old_hist.items() if r})
    full.update({r:32*n for r,n in new_hist.items() if r})
    need(all(n >= 0 for n in full.values()),'complete pruned profile negative')
    full = +full
    mass = lambda h:sum(r*n for r,n in h.items())
    need(mass(baseline)-mass(full) == 60*288,'global saving must include returned owner work')
    terminal = Counter(full)
    terminal[1] += 888*32
    need(mass(terminal)-mass(baseline) == (888-9*60)*32,'two-N wrapper mass invoice')
    data = {'status':'PASS_RESTRICTED429_OWNER_ALLOCATION_WITH648_RETURNED_IDLE_RANK',
            'sources':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest()
                       for p in (PROJECTOR,LAYOUT,CERTIFICATE)},
            'discarded_local_helper_numbers':list(range(249,258)),
            'discarded_old_physical_registers':list(range(471,480)),
            'deleted_slots_per_replica':[list(s) for s in removed],
            'retained_slots_per_replica':len(new_slots),
            'retained_slots_sha256':sha256(cap.canonical(new_slots)).hexdigest(),
            'old_projector_audit':old,'new_projector_audit':new,
            'old_idle_profile_per_replica':dict(sorted(old_hist.items())),
            'new_idle_profile_per_replica':dict(sorted(new_hist.items())),
            'returned_idle_rank_per_replica':648,
            'all32_replicas_owner_occurrences':32*9*429,
            'complete_pruned_local_and_idle_profile':dict(sorted(full.items())),
            'complete_pruned_mass':mass(full),
            'net_rank_mass_saving_per_local_call':60,
            'two_N_wrapper_extra_rank1_children_per_replica':888,
            'pruned_plus_two_N_profile':dict(sorted(terminal.items())),
            'pruned_plus_two_N_mass':mass(terminal),
            'zero_exponent_two_N_excess_over_baseline':mass(terminal)-mass(baseline),
            'omitted_return_control':'Omitting the648 returned idle rank per replica would falsely claim132 net units per local call; exact physical complements reject it.',
            'limits':['retained owner offsets and pending masks only; no free repacking or new hosting optimum',
                      'previous native early-preload/late-X code-window proof applies structurally to this restricted assignment',
                      'the terminal888 rank1 calls still need their own recursive scratch/owner/tape/precision admission',
                      'neither complete profile nor terminal addition alone is a restored supplier or kappa claim']}
    path = HERE/'BIT-OWNER-PRUNE.json'
    if args.write:
        path.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == json.loads(cap.canonical(data)),'complete owner restriction receipt differs')
    print(data['status'])
    print('returned648 per replica; netlocalmasssaving60; terminalextra888')


if __name__ == '__main__':
    main()
