#!/usr/bin/env python3
"""Independent direct-symbol audit of the caller's H contact admission.

Apache-2.0. Substantial OpenAI assistance. This does not call the producer's
polynomial, move_frame, product, source_route, or contact checking functions.
Products of C_q gates have Z4 Fourier symbols of degree at most two; values on
zero, each unit address and every pair of unit addresses determine that symbol.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import json
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUT = HERE.parent/'controller/FRAME-EXCHANGE.json.gz'
AXES = tuple(1 << i for i in range(73))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def act(columns, vector):
    out = 0
    for i in range(73):
        if (vector >> i) & 1:
            out ^= columns[i]
    return out


def normalize(terms):
    counts = Counter()
    for axis, coefficient in terms:
        counts[axis] += coefficient
    return tuple(sorted((a, c % 4) for a, c in counts.items() if a and c % 4))


def evaluate(terms, address):
    return sum(coefficient*((axis & address).bit_count() & 1) for axis, coefficient in terms) % 4


def discrepancy(old, new, columns, shift):
    return normalize([(act(columns, a), c) for a, c in old]+[(shift, 2)]+[(a, -c) for a, c in new])


def main():
    started = time.monotonic()
    receipt = json.loads(gzip.decompress(INPUT.read_bytes()))
    source = HERE.parent/'controller/frame_exchange.py'
    need(digest(source) == receipt['generator_sha256'], 'Actual contact-generator source pin')
    for path, expected in receipt['dependency_hashes'].items():
        need(digest(ROOT/path) == expected, 'Actual contact dependency pin '+path)
    phase_path = ROOT/'research/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
    need(digest(phase_path) == receipt['immutable_source_pins']['DATA-PHASES.json'], 'Actual phase packet pin')
    phases = json.loads(phase_path.read_text())
    points = (0,)+AXES+tuple(a ^ b for a, b in combinations(AXES, 2))
    need(len(points) == 2702, 'Degree-two determining address set')
    phase_patterns = {}; count = 0; witnesses = []
    for stage in range(9):
        row = receipt['H_wrapper_contacts'][str(stage)]
        pre_common = () if stage == 0 else normalize([(a, 1) for a in AXES[9:9+8*(stage-1)]]+
                                                    [(a, 1) for a in AXES[9+8*(stage-1):9+8*stage]])
        post_common = normalize((a, 1) for a in AXES[:9+8*stage])
        need(normalize(row['preY_common']) == pre_common and normalize(row['postX_common']) == post_common,
             'Claimed common birth and completed frames')
        need(len(row['preY_views']) == len(row['postX_views']) == 112, 'Every port has both contacts')
        for kind in ('preY', 'postX'):
            for port, view in enumerate(row[kind+'_views']):
                g = tuple(view['owner_columns']); inv = tuple(view['inverse_owner_columns'])
                need(len(g) == len(inv) == 73 and all(0 <= x < (1 << 73) for x in g+inv), 'Actual73-axis owner maps')
                need(all(act(g, g[i]) == AXES[i] for i in range(73)), 'Each owner route is an involution')
                need(all(act(g, inv[i]) == act(inv, g[i]) == AXES[i] for i in range(73)), 'Serialized inverse owner')
                need(view['inverse_physical_shift'] == act(inv, view['physical_shift']), 'Inverse affine translation')
                if kind == 'preY':
                    old = () if stage == 0 else normalize([(a, 1) for a in AXES[:9+8*(stage-1)]]+
                                                         [(phases['recipes'][port]['q'], -1)])
                    new = pre_common
                else:
                    old = new = post_common
                delta = discrepancy(old, new, g, view['physical_shift'])
                if delta not in phase_patterns:
                    bad = next((address for address in points if evaluate(delta, address)), None)
                    need(bad is None, 'Direct Fourier-symbol phase mismatch '+repr((stage, kind, port, bad)))
                    phase_patterns[delta] = len(points)
                inverse_delta = discrepancy(new, old, inv, view['inverse_physical_shift'])
                if inverse_delta not in phase_patterns:
                    bad = next((address for address in points if evaluate(inverse_delta, address)), None)
                    need(bad is None, 'Inverse direct-symbol phase mismatch')
                    phase_patterns[inverse_delta] = len(points)
                need(view['global_phase_Z4'] == 0 and evaluate(delta, 0) == 0, 'Absolute zero-frequency phase')
                if not witnesses and stage == 1:
                    wrong = discrepancy(old, new, g, view['physical_shift'] ^ 1)
                    address = next(x for x in points if evaluate(wrong, x))
                    witnesses.append(dict(stage=stage, contact=kind, port=port, mutated_shift_xor=1,
                                          rejecting_address=address, nonzero_phase_Z4=evaluate(wrong, address)))
                count += 1
    need(count == 2016 and witnesses, 'Complete9-stage112-port two-contact inventory')
    result = dict(schema='independent-direct-symbol-H-contact-audit/1',
                  status='PASS_ALL_2016_CONTACTS_AND_INVERSES_WITH_GLOBAL_PHASE',
                  generator_sha256=digest(Path(__file__)), input_receipt_sha256=digest(INPUT),
                  input_generator_sha256=receipt['generator_sha256'], phase_packet_sha256=digest(phase_path),
                  contact_count=count, determining_addresses_per_unique_phase_pattern=len(points),
                  unique_phase_patterns=len(phase_patterns), all_owner_routes_involutive=True,
                  all_affine_maps_have_explicit_checked_inverses=True,
                  backward_orientation='The physical views are real permutations/translations; conjugating the checked identity proves the dual orientation.',
                  H_stage_identification='At both contacts the normalized logical map is D_s H D_s, with D_s diagonal in port index and each owner route squaring to identity.',
                  negative_control=witnesses[0], seconds=time.monotonic()-started,
                  proof_scope='Exact finite frame/phase contact admission only. It does not remove terminal monodromy or establish a complete caller.',
                  no_new_kappa_claimed=True)
    output = HERE/'FRAME-CONTACT-INDEPENDENT-AUDIT.json'
    output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
