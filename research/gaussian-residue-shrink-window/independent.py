"""Independent exact arithmetic for PR3881's strict residue-child window.

This checker imports neither the Gaussian backend nor the primary checker.
The source-certified 256-bit operator enclosure is an explicit inherited
premise; the p-dependent coefficient and child lengths are rederived here.
Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


HEAD = '75e098dc12a2567e73a2858137408e08d31dbf84'
CORE = {
    'source/RESULT.json': '2234d2123d192ffa3288ca8010a677436e79b638',
    'source/hybrid.py': '4015d0195c1c5e381f0069cd073dff51089d930a',
    'source/vendor/gaussian.py': 'ac444a242caba128754615227ad6057545822a34',
}


def require(ok, label):
    if not ok:
        raise ValueError(label)


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def authenticated(package):
    origin = json.loads((package / 'ORIGINS.json').read_text(encoding='utf-8'))
    require(origin['source_head'] == HEAD, 'source head')
    seen = set()
    raw = {}
    for row in origin['files']:
        relative = row['path']
        require(relative not in seen, 'duplicate source path')
        seen.add(relative)
        path = (package / relative).resolve()
        require(path.is_relative_to(package.resolve()) and path.is_file(), 'source path')
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256')
        require(blob(data) == row['git_blob'], 'source Git blob')
        if relative in CORE:
            require(row['git_blob'] == CORE[relative], 'immutable core pin')
        raw[relative] = data
    require(CORE.keys() <= raw.keys(), 'missing core source')
    return raw


def pair(value):
    return [value.numerator, value.denominator]


def width(length, k, top):
    """Bitlength of packed maximal digits; top has `top` available bits."""
    require(type(length) is int and length >= 1, 'positive digit count')
    require(type(k) is int and 1 <= k <= 64, 'residue domain')
    require(type(top) is int and 1 <= top <= 64, 'top digit domain')
    slots = 2*k + (length-1).bit_length()
    return (length-1)*slots + min(top, k)


def actual_packed(n, k):
    """Independent literal digit decomposition, used only on witness cases."""
    value = (1 << n)-1
    length = (n+63)//64
    step = 2*k + (length-1).bit_length()
    mask = (1 << k)-1
    result = 0
    place = 0
    while value:
        digit = value & ((1 << 64)-1)
        result |= (digit & mask) << place
        value >>= 64
        place += step
    return result.bit_length()


def compute(package):
    raw = authenticated(package)
    predecessor = json.loads(raw['source/RESULT.json'])
    first = predecessor['precision_curve'][0]
    require(first['precision'] == 208 and first['residue_bits'] == 0, 'ordinary source row')
    require(first['shape'] == [5, 7, 13] and first['digit_bits'] == 64, 'source box')
    require(first['working_bits'] == 448 and first['maximum_input_digits'] == 228, 'source domain')
    require(all(type(v) is int for v in first['radius']), 'exact source radius')
    scale = (5*7*13)**2 * (1 << 132)
    require(first['source_scale'] == scale, 'both source factors')
    # Each source line performs two matrix extractions and log2(t)
    # butterfly levels, each with coefficient 2*2^-p, then scales by 2^50.
    line_slope = sum(2*(t.bit_length()+1)*(1 << 50) for t in (8, 16, 32))
    require(line_slope == 36*(1 << 50), 'independent line coefficient')
    slope = scale*(3*line_slope + 2)
    remainder = Fraction(*first['radius']) - Fraction(slope, 1 << 208)
    require(remainder >= 0, 'nonnegative fixed enclosure remainder')
    def radius(p):
        return Fraction(slope, 1 << p) + remainder
    # Rejecting p=207 even without the fixed remainder is enough to prove
    # rejection at every shifted boundary. Positive slope proves monotonicity.
    require(radius(208) < Fraction(1, 2), 'ordinary admission')
    require(Fraction(slope, 1 << 207) >= Fraction(1, 2), 'uniform shifted rejection')
    precision = []
    for k in range(65):
        p = 208-k
        threshold = Fraction(1 << k, 2)
        require(radius(p) < threshold and radius(p-1) >= threshold, 'least precision')
        # All source integer, alpha/theta, input grid and enclosure guards.
        for s, t in ((5, 8), (7, 16), (13, 32)):
            require(100 < p <= 256 and 25 < p and 2 <= s < t < (1 << p), 'p integer domain')
            require(Fraction(t-s, s) > Fraction(p, 625), 'theta domain')
        require(448 > p+50+32 and 66 <= p, 'grid and embedding domain')
        require((radius(p)/scale) < Fraction(1, 100), 'forward error sufficient margin')
        precision.append({'k': k, 'least_precision': p, 'radius': pair(radius(p)),
                          'one_bit_lower_radius': pair(radius(p-1))})
    for row in predecessor['precision_curve']:
        require(radius(row['precision']) == Fraction(*row['radius']), 'all retained precision rows')
    digest = hashlib.sha256()
    domains = []
    best = [0]*14592
    false_negatives = 0
    for k in range(1, 65):
        intervals = []
        first_n = None
        previous = None
        count = 0
        for n in range(1, 14593):
            length, rem = divmod(n-1, 64)
            child = width(length+1, k, rem+1)
            ok = child < n
            conservative = k + length*(2*k + length.bit_length())
            if ok and conservative >= n:
                false_negatives += 1
            digest.update(f'{k},{n},{child},{int(ok)}\n'.encode('ascii'))
            if ok:
                count += 1
                best[n-1] = k
                if first_n is None:
                    first_n = n
                previous = n
            elif first_n is not None:
                intervals.append([first_n, previous])
                first_n = None
        if first_n is not None:
            intervals.append([first_n, previous])
        domains.append({'k': k, 'strict_actual_width_count': count, 'intervals': intervals})
    witnesses = []
    for n in (1, 16, 28, 29, 63, 64, 65, 127, 128, 129, 14528, 14529, 14591, 14592):
        for k in (1, 16, 28, 29, 64):
            length, rem = divmod(n-1, 64)
            derived = width(length+1, k, rem+1)
            measured = actual_packed(n, k)
            require(derived == measured, 'literal maximum-word attainment')
            witnesses.append([n, k, measured])
    require(width(228, 28, 64) == 14556 < 14592, 'sharp admitted endpoint')
    require(width(228, 29, 64) == 15011 > 14592, 'sharp excluded endpoint')
    controls = []
    for args in ((0, 16, 64), (228, 0, 64), (228, True, 64), (228, 16, 0)):
        try:
            width(*args)
        except ValueError:
            controls.append('domain_rejected_' + repr(args))
        else:
            raise ValueError('domain control accepted')
    require(actual_packed(64, 64) == 64, 'equality is not strict shrinkage')
    controls.append('equal_child_rejected_by_strict_comparison')
    require(actual_packed(65, 16) == 34 and width(2, 16, 64) == 49, 'partial top affects exact maximum')
    controls.append('full_top_substitution_detected')
    require(228*((1 << 16)-1)**2 >= (1 << 39), 'one-bit slot reduction spills')
    controls.append('reduced_slot_capacity_rejected')
    require(blob(raw['source/RESULT.json'] + b' ') != CORE['source/RESULT.json'], 'source corruption control')
    controls.append('changed_source_bytes_fail_immutable_pin')
    tails = [row['k'] for row in domains
             if row['intervals'] == [[row['k']+1, 14592]]]
    require(tails and max(tails) == 27, 'largest uninterrupted actual-width tail')
    summary = {
        'widths': 14592,
        'tested_pairs': 64*14592,
        'admissible_pairs': sum(row['strict_actual_width_count'] for row in domains),
        'conservative_false_negatives': false_negatives,
        'max_k_at_capacity': best[-1],
        'capacity_child_bits': width(228, 28, 64),
        'next_k_child_bits': width(228, 29, 64),
        'largest_uniform_tail_k': max(tails),
        'uniform_tail_first_width': max(tails)+1,
        'best_k_vector_sha256': hashlib.sha256(bytes(best)).hexdigest(),
    }
    return {
        'status': 'PASS_INDEPENDENT_GAUSSIAN_RESIDUE_WINDOW',
        'source_head': HEAD,
        'slope': slope,
        'fixed_remainder': pair(remainder),
        'summary': summary,
        'precision_rows': precision,
        'strict_full_box_endpoint': {'k': 28, 'precision': 180, 'child_bits': 14556,
                                     'next_k': 29, 'next_child_bits': 15011, 'outer_bits': 14592},
        'actual_width_pairs_checked': 64*14592,
        'actual_width_digest_sha256': digest.hexdigest(),
        'actual_width_domains': domains,
        'literal_attainment_witnesses': witnesses,
        'semantic_controls': controls,
        'inherited_premise': 'Authenticated source-certified p=256 Gaussian operators; no backend imported or rerun.',
        'scope': 'Exact fixed-box precision and actual-width child feasibility only; no physical cost, all-size recurrence, or kappa claim.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = compute(args.package)
    candidate_path = args.candidate if args.candidate is not None else args.package/'RESULT.json'
    if candidate_path.is_file():
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        expected_precision = [{'k': row['k'], 'p': row['least_precision'], 'radius': row['radius']}
                              for row in result['precision_rows']]
        encode = lambda obj: json.dumps(obj, sort_keys=True, separators=(',', ':'))
        require(encode(candidate['precision']) == encode(expected_precision), 'candidate precision contract')
        for key, value in result['summary'].items():
            require(encode(candidate['summary'][key]) == encode(value), 'candidate summary '+key)
        result['candidate_contract_checked'] = True
    else:
        raise ValueError('candidate result missing')
    expected = args.package/'INDEPENDENT-RESULT.json'
    if args.write:
        with expected.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        saved = json.loads(expected.read_text(encoding='utf-8'))
        require(encode(saved) == encode(result), 'independent complete receipt')
    print(result['status'] + ' ' + json.dumps(result['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
