#!/usr/bin/env python3
"""Rebuild the known pre-retiming helper544 control, including its FULL repair.

This is a control for the candidate interpreter, not a new native supplier.
Apache-2.0; substantial OpenAI assistance; retained PR3734 attribution applies.
"""
from argparse import ArgumentParser
from fractions import Fraction as Q
from pathlib import Path
import json

import complete_candidate as c

HERE = Path(__file__).resolve().parent
DEFAULT_FOLLOWUP = HERE.parents[1]/'kappa-global-continuation/inputs/kappa-consumer-followup'


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--followup', type=Path, default=DEFAULT_FOLLOWUP)
    ap.add_argument('--out', type=Path, default=HERE)
    args = ap.parse_args()
    source = args.followup/'artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz'
    w = c.read(source)
    c.need(c.column(w, 544) == {544: {(): Q(1)}}, 'retained helper544 identity')
    c.need(c.profile(w)[0] == {1:2440,2:725,3:224,4:102,5:20,8:8}, 'retained local profile')
    w['B'] = w['B'][:43] + [['add',208,544,1,2,[51]]] + w['B'][43:692] + w['B'][694:]
    w['start_extra']['544'] = [51]
    for e in w['warps']:
        e[0] += 1 if 43 <= e[0] < 692 else -1 if e[0] >= 694 else 0
    c.need(c.column(w, 544) == {544:{():Q(1)},672:{():Q(-1,2)},676:{():Q(1,2)}}, 'known release dirt')
    receipt = c.complete(w, 544)
    c.need(receipt['local_profile'] == {1:2437,2:724,3:226,4:102,5:20,8:8}, 'known control profile')
    args.out.mkdir(parents=True, exist_ok=True)
    c.write(args.out/'UNRETIMED544-WORD.json.gz', w)
    c.write(args.out/'UNRETIMED544-BUILDER.json', receipt)
    print(json.dumps({'status':'PASS_KNOWN_HELPER544_CONTROL', 'repair_events':receipt['repair_events'], 'new_supplier':False}))


if __name__ == '__main__':
    main()
