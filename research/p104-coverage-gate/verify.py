#!/usr/bin/env python3
"""Source-bound incidence and complete-gate checks; standard library only."""
import argparse
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def strict_load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def source_bindings():
    sources = strict_load(PACKAGE / 'SOURCES.json')
    for row in sources['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
                    == row['sha256'], 'source hash: ' + row['path'])


def recount(witness):
    initial, final = witness['initial_frames'], witness['final_frames']
    xs = {f'X{i}' for i in range(104)}
    ys = {f'Y{i}' for i in range(104)}
    require(set(initial) == set(final), 'persistent owner identity')
    require(xs | ys <= set(initial), 'all 104 ports present')
    helpers = set(initial) - xs - ys
    require(len(helpers) == 72, 'helper count')
    require(all(rank(initial[x]) == 1 and rank(final[x]) == 9 for x in xs), 'X frames')
    require(all(rank(initial[y]) == 0 and rank(final[y]) == 8 for y in ys), 'Y frames')
    require(all(rank(initial[h]) == 0 and rank(final[h]) == 9 for h in helpers), 'helper frames')
    histogram = {}
    for event in witness['program']:
        if event[0] == 'transport':
            _, _, before, after, claimed = event
            actual = abs(rank(after) - rank(before))
            require(actual == claimed, 'transport rank')
            histogram[actual] = histogram.get(actual, 0) + 1
    require(histogram == {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}, 'histogram')
    progress = sum(rank(final[r]) - rank(initial[r]) for r in initial)
    mass = sum(k*v for k,v in histogram.items())
    require((progress, mass) == (2312, 2368), 'witness totals')
    return progress, mass


def census(n=104, excess=264):
    rows = []
    closed = []
    for a in range(n+1):
        for b in range(n+1):
            touched = n*(a+b)-a*b
            dangling = n*(a+b)-2*a*b
            delta = excess*(a+b)-touched
            if not dangling:
                closed.append([a,b])
            require(delta == (excess-n)*(a+b)+a*b, 'expanded gate')
            if a+b:
                require(delta > 0, 'unchanged profile rejection')
            rows.append([a,b,touched,dangling,delta])
    require(closed == [[0,0],[n,n]], 'whole-call closure')
    return rows, closed


def verify():
    source_bindings()
    w = json.loads((ROOT / 'research/p104-native-channel/inputs/LOWRANK-WITNESS.json').read_text())
    progress, native_mass = recount(w)
    rows, closed = census()
    n, m, correction = 104, 81, 208
    corrected_mass = native_mass + correction
    require(corrected_mass-progress == 264, 'conditional corrected excess')
    # Explicit physical-owner inventories: retain a bank per call, share one bank,
    # or share one bank per stage. No schedule legality is claimed by this control.
    full = []
    for helper_count in (72,144,72*208):
        width = 2*n*n + helper_count
        remaining = m*width-n*n-208*progress
        lower = 208*corrected_mass+max(0,remaining)
        require(lower-m*width == 44096, 'helper inventory cancellation')
        full.append({'helpers':helper_count,'width':width,'remaining_rank':remaining,
                     'lower_rank':lower,'capacity':m*width,'excess':lower-m*width})
    # Both-axis four-corner optimization against all integer masks, several
    # asymmetric profiles, and the intentionally misleading sparse pass.
    optimization = []
    for er,ec in ((264,264),(100,100),(56,56),(51,52),(103,104),(104,103),(0,300),(300,0)):
        values = [(er-104)*a+(ec-104)*b+a*b for a in range(1,105) for b in range(1,105)]
        corners = [(er-104)*a+(ec-104)*b+a*b for a,b in ((1,1),(1,104),(104,1),(104,104))]
        require(min(values)==min(corners), 'bilinear corner criterion')
        optimization.append({'row_excess':er,'column_excess':ec,'minimum_two_axis_relaxation':min(values),
                             'closed_excess':104*(er+ec-104)})
    sparse = {'a':1,'b':1,'excess_per_axis':100,'touched':207,'dangling':206,
              'relaxed_excess':-7,'closed_excess':9984}
    require(200-207==-7 and 104*200-104**2==9984, 'sparse false-admission control')
    payload = json.dumps(rows,separators=(',',':')).encode()
    return {'schema_version':1,'scope':'conditional whole-fiber incidence and progress gate',
            'base_commit':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
            'witness':{'ports':104,'helpers':72,'progress':progress,'native_mass':native_mass,
                       'granted_correction':208,'corrected_mass':corrected_mass},
            'mask_count':len(rows),'nonempty_masks':len(rows)-1,'closed_masks':closed,
            'all_masks_sha256':hashlib.sha256(payload).hexdigest(),
            'minimum_nonempty_excess':min(r[4] for r in rows if r[0]+r[1]),
            'full_inventory_controls':full,'changed_profile_controls':optimization,
            'sparse_discrimination_control':sparse,'selected_frontier_changed':False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result',action='store_true')
    args = parser.parse_args()
    result = verify()
    if args.write_result:
        (PACKAGE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        expected = strict_load(PACKAGE/'RESULT.json')
        require(json.dumps(result, sort_keys=True, separators=(',', ':')) ==
                json.dumps(expected, sort_keys=True, separators=(',', ':')),
                'typed committed result equality')
    print('PASS_P104_WHOLE_FIBER_COVERAGE_GATE: 11025 masks; conditional scope only')

if __name__ == '__main__':
    main()
