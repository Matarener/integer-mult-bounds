#!/usr/bin/env python3
"""Exact caller-bound Gaussian commutation; no predecessor code is executed.

Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
The mathematical operators and port data are credited in README.md.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
import argparse
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASES = 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json'
COVER = 'research/kappa-rebuild/controller/P3-NATIVE-COVER.json.gz'
CANONICAL = 'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate():
    manifest = read(HERE / 'SOURCES.json')
    count = 0
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        need(path.resolve().is_relative_to(ROOT), 'Input escaped repository')
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'Changed source: ' + row['path'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'Changed source Git blob: ' + row['path'])
        count += 1
    for row in manifest['retained_external_artifacts']:
        raw = (HERE / row['local_path']).read_bytes()
        if row['local_path'].endswith('.gz'):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == row['sha256'], 'Changed retained artifact')
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'],
             'Changed retained artifact Git blob')
        count += 1
    return count


# A translation-invariant operator is its convolution kernel in Q(i)[F_2^9].
# Store Gaussian integer numerators and one common power-of-two denominator.
def normalized(entries, exponent):
    entries = {x: z for x, z in entries.items() if z != (0, 0)}
    while exponent and all(a % 2 == b % 2 == 0 for a, b in entries.values()):
        entries = {x: (a // 2, b // 2) for x, (a, b) in entries.items()}
        exponent -= 1
    return entries, exponent


def compose(left, right):
    a, da = left
    b, db = right
    result = {}
    for x, (ar, ai) in a.items():
        for y, (br, bi) in b.items():
            r, i = result.get(x ^ y, (0, 0))
            result[x ^ y] = r + ar * br - ai * bi, i + ar * bi + ai * br
    return normalized(result, da + db)


def gaussian(q, sign=1):
    need(0 < q < 512 and sign in (-1, 1), 'Nonzero nine-axis signed Gaussian')
    return {0: (1, sign), q: (1, -sign)}, 1


def gaussian_product(axes):
    result = ({0: (1, 0)}, 0)
    for axis in axes:
        result = compose(gaussian(axis), result)
    return result


def translate(kernel, shift):
    entries, exponent = kernel
    return {x ^ shift: z for x, z in entries.items()}, exponent


def conjugate(kernel):
    entries, exponent = kernel
    return {x: (a, -b) for x, (a, b) in entries.items()}, exponent


def character_on_column(kernel, axis):
    """Z_axis applied to this zero-input column; deliberately not convolution."""
    entries, exponent = kernel
    return {x: (-a, -b) if (axis & x).bit_count() % 2 else (a, b)
            for x, (a, b) in entries.items()}, exponent


def first_difference(left, right):
    a, da = left
    b, db = right
    common = max(da, db)
    for x in sorted(a.keys() | b.keys()):
        ar, ai = a.get(x, (0, 0))
        br, bi = b.get(x, (0, 0))
        delta = ((ar << (common-da)) - (br << (common-db)),
                 (ai << (common-da)) - (bi << (common-db)))
        if delta != (0, 0):
            return {'output_address': x, 'numerator_real_imag': list(delta),
                    'denominator_power_of_two': common}
    return None


def span(axes):
    values = {0}
    for axis in axes:
        values |= {x ^ axis for x in tuple(values)}
    return values


def validate_port(recipe, canonical):
    port, q = recipe['port'], recipe['q']
    child = recipe['idle_children'][0]
    basis = child['orthogonal_axes'][:8]
    shift = child['translation_after']
    need(canonical['ports'][port] == q, 'Port normal differs between native and phase data')
    need(canonical['frames'][canonical['start'][port]] == [q], 'Native X entrance line')
    need(canonical['start'][112+port] == 0, 'Native Y entrance identity')
    need(canonical['final'][port] == 1 and len(canonical['frames'][1]) == 9,
         'Native X full exit')
    need(q.bit_count() % 2 == 1 and len(basis) == 8, 'Odd query and eight complementary axes')
    need(all(0 < x < 512 for x in basis) and 0 <= shift < 512, 'Nine-axis support')
    need(all((x & y).bit_count() % 2 == int(i == j)
             for i, x in enumerate([q] + basis) for j, y in enumerate([q] + basis)),
         'Actual query and complement form an orthonormal basis')
    need(span(basis) == span(canonical['frames'][canonical['final'][112+port]]),
         'Native Y exit is the same complementary space')
    need(child['orthogonal_axes'][8:] == [1 << i for i in range(9, 17)] and child['rank'] == 16,
         'Removing D1 from the actual initial idle leaves these eight old axes')
    return q, basis, shift


def check_initial_contacts(cover):
    contacts = [r for r in cover['main_contacts'] if r['stage'] == 0]
    need([r['port'] for r in contacts] == list(range(112)), 'All 112 initial caller contacts')
    identity = [1 << i for i in range(73)]
    for row in contacts:
        need(row['pair'] == 0 and row['direction'] == 'forward' and row['common_spectator_frame'] == [],
             'Source initial forward call')
        need(set(row['maps']) == {'entry_X', 'entry_Y', 'exit_X', 'exit_Y'}, 'Four boundary maps')
        for rec in row['maps'].values():
            need(rec['owner_columns'] == rec['inverse_owner_columns'] == identity,
                 'Stage-zero coordinate map must be the identity')
            need(rec['physical_shift'] == rec['inverse_physical_shift'] == rec['global_phase_Z4'] == 0,
                 'Stage-zero contact has no omitted affine or global phase')
    return 4 * len(contacts)


def rejected(action):
    try:
        action()
    except ValueError:
        return True
    return False


def run():
    source_count = authenticate()
    phases, canonical, cover = read(ROOT / PHASES), read(ROOT / CANONICAL), read(ROOT / COVER)
    word = read(HERE / 'pr4440-COMPLEX-CONTROLLER.json.gz')
    need(len(phases['recipes']) == 112 and phases['m'] == 73, 'Actual phase packet')
    need([r['port'] for r in phases['recipes']] == list(range(112)), 'Ordered port census')
    need(word['pairs'] == 17 and word['ambient_rank'] == 153, 'Pinned p17 caller')
    calls = [r for r in word['physical_events'] if r[0] in ('LOCAL', 'QUERY_SHEAR')]
    need(calls[0] == ['LOCAL', 0, 0, False] and [r[1] for r in calls] == list(range(35)),
         'Exactly one initial call, followed by all 34 ordered stages')
    need(sum(r[0] == 'LOCAL' for r in calls) == 19 and sum(r[0] == 'QUERY_SHEAR' for r in calls) == 16,
         'Actual full/thin call partition')
    contacts = check_initial_contacts(cover)
    f9 = gaussian_product([1 << i for i in range(9)])
    weights, shift_weights = Counter(), Counter()
    omitted, wrong_inverse, noncommuting = [], [], []
    counts = 0
    example = None
    for recipe in phases['recipes']:
        q, basis, shift = validate_port(recipe, canonical)
        positive, inverse = gaussian(q), gaussian(q, -1)
        d0 = compose(f9, inverse)
        repaired = translate(gaussian_product(basis), shift)
        need(d0 == repaired, 'Exact D0 = translation times eight positive Gaussians')
        need(len(d0[0]) == 256 and all(256*(a*a+b*b) == 1 << (2*d0[1]) for a, b in d0[0].values()),
             'Every D0 column has 256 entries of squared modulus 1/256')
        for d, g, f in ((d0, positive, f9), (conjugate(d0), conjugate(positive), conjugate(f9))):
            need(compose(d, g) == compose(g, d) == f, 'All-column physical commutation, both conjugate orientations')
            counts += 512
        # Independent evaluation of every Fourier character binds the source
        # rank-16 idle's old part and its translation without a phase-polynomial helper.
        for xi in range(512):
            intended = (xi.bit_count() - ((xi & q).bit_count() % 2)) % 4
            supplied = (sum((xi & b).bit_count() % 2 for b in basis)
                        + 2*((xi & shift).bit_count() % 2)) % 4
            need(intended == supplied, 'Literal Fourier-character equality including phase')
        omitted.append(first_difference(d0, gaussian_product(basis)))
        wrong_inverse.append(first_difference(d0, compose(f9, positive)))
        # Put a nonconstant character in front of F9. This leaves the abelian
        # convolution algebra, and its D0 really fails to commute with Q.
        axis = q & -q
        left = character_on_column(f9, axis)  # (Z F9 Q^-1) Q delta_0
        right = compose(positive, character_on_column(d0, axis))
        noncommuting.append(first_difference(left, right))
        weights[q.bit_count()] += 1
        shift_weights[shift.bit_count()] += 1
        if example is None:
            example = {'port': recipe['port'], 'q': q, 'complement': basis, 'translation': shift,
                       'omitted_translation_witness': omitted[-1], 'noncommuting_character_witness': noncommuting[-1]}
    need(all(omitted) and all(wrong_inverse) and all(noncommuting), 'Every semantic control must expose a nonzero coefficient')
    bad_port = deepcopy(phases['recipes'][0]); bad_port['q'] = phases['recipes'][1]['q']
    need(rejected(lambda: validate_port(bad_port, canonical)), 'Wrong port normal rejected')
    bad_cover = deepcopy(cover)
    bad_cover['main_contacts'][0]['maps']['entry_X']['physical_shift'] ^= 1
    need(rejected(lambda: check_initial_contacts(bad_cover)), 'Wrong initial coordinate translation rejected')
    return {'status': 'PASS_STAGE_ZERO_GAUSSIAN_COMMUTATION', 'source_files_authenticated': source_count,
            'ports': 112, 'initial_boundary_maps': contacts, 'p17_full_calls': 19, 'p17_thin_calls': 16,
            'query_hamming_weights': {str(k): v for k, v in sorted(weights.items())},
            'translation_hamming_weights': {str(k): v for k, v in sorted(shift_weights.items())},
            'commutator_coefficients_checked_both_orientations': counts,
            'fourier_characters_checked': 112*512, 'rank_eight_support_per_column': 256,
            'controls': {'omitted_translation': len(omitted), 'wrong_Q_inverse': len(wrong_inverse),
                         'noncommuting_character': len(noncommuting), 'wrong_port': 1, 'wrong_initial_map': 1},
            'first_port': example, 'all_column_reason': 'Equality of convolution kernels proves every translated basis column.',
            'all_f_reason': 'The written tensor-product composition lemma applies for every positive integer f.',
            'scope': 'Source-specified complex caller commutation and stage-zero phase normalization; not native supplier admission or a new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='authoring only: save the deterministic result')
    args = parser.parse_args()
    result = run()
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8', newline='\n')
    else:
        need(result == read(HERE / 'RESULT.json'), 'Changed expected result')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
