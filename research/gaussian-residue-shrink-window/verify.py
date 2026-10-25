"""Sharp declared-width admission for PR3881. ToikY + OpenAI Codex; Apache-2.0."""
from pathlib import Path
from fractions import Fraction as F
import argparse
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    origin = json.loads((ROOT / 'ORIGINS.json').read_text())
    need(origin['source_head'] == '75e098dc12a2567e73a2858137408e08d31dbf84', 'source head')
    for row in origin['files']:
        path = (ROOT / row['path']).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'source path')
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == row['git_blob'], 'source blob ' + row['path'])


def child_bits(n, b, k):
    need(all(type(x) is int and x >= 1 for x in (n, b, k)) and k <= b, 'size domain')
    length = (n + b - 1) // b
    top = n - b * (length - 1)
    slot = 2 * k + (length - 1).bit_length()
    return min(k, top) + (length - 1) * slot


def largest_k(n, b=64):
    need(type(n) is int and type(b) is int and n >= 1 and b >= 1, 'width domain')
    length = (n + b - 1) // b
    if length == 1:
        return min(b, n - 1)
    h = (length - 1).bit_length()
    return min(b, max(0, (b - 1 - h) // 2,
                      (n - 1 - h * (length - 1)) // (2 * length - 1)))


def radius_constants():
    old = json.loads((ROOT / 'source/RESULT.json').read_text())
    row = old['precision_curve'][0]
    need((row['shape'], row['precision'], row['digit_bits'], row['working_bits']) ==
         ([5, 7, 13], 208, 64, 448), 'frozen geometry')
    scale = 455 ** 2 * 2 ** 132
    need(row['source_scale'] == scale, 'both source factors')
    slope = scale * (3 * 36 * 2 ** 50 + 2)
    remainder = F(*row['radius']) - F(slope, 2 ** 208)
    need(remainder >= 0, 'nonnegative enclosure remainder')
    return slope, remainder


def arithmetic():
    a, remainder = radius_constants()
    precision = []
    for k in range(65):
        p = 208 - k
        radius = F(a, 2 ** p) + remainder
        lower = F(a, 2 ** (p - 1)) + remainder
        need(2 * radius < 2 ** k <= 2 * lower, 'least precision')
        need(100 < p <= 256 and 25 < p and 448 > p + 82 and 66 <= p, 'precision domains')
        for s, t in ((5, 8), (7, 16), (13, 32)):
            need(F(t - s, s) > F(p, 625), 'theta domain')
        precision.append({'k': k, 'p': p, 'radius': [radius.numerator, radius.denominator]})
    rows = []
    differing = 0
    pairs = 0
    for n in range(1, 14593):
        admissible = [k for k in range(1, 65) if child_bits(n, 64, k) < n]
        best = max(admissible, default=0)
        need(best == largest_k(n), 'closed form admission')
        length = (n + 63) // 64
        for k in admissible:
            conservative = k + (length - 1) * (2 * k + (length - 1).bit_length())
            differing += conservative >= n
        pairs += len(admissible)
        rows.append(best)
    # General formula checked independently of the fixed-box finite scan.
    general = 0
    for b in range(1, 13):
        for n in range(1, 12 * b + 1):
            valid = [k for k in range(1, b + 1) if child_bits(n, b, k) < n]
            need(largest_k(n, b) == max(valid, default=0), 'general formula')
            general += 1
    for n, k in ((14592, 28), (14592, 29), (65, 29), (8220, 28), (8221, 28)):
        length = (n + 63) // 64
        slot = 2 * k + (length - 1).bit_length()
        mask = 2 ** k - 1
        x = 2 ** n - 1
        packed = sum(((x >> (64 * j)) & (2 ** 64 - 1) & mask) << (slot * j) for j in range(length))
        need(packed.bit_length() == child_bits(n, 64, k), 'attaining all-ones input')
    need(child_bits(14592, 64, 28) == 14556 < 14592 < child_bits(14592, 64, 29) == 15011, 'endpoint')
    need(child_bits(65, 64, 29) == 60 < 65 <= 88, 'partial-top control')
    need(not child_bits(8220, 64, 28) < 8220 and child_bits(8221, 64, 28) < 8221, 'strict boundary')
    need(all(child_bits(n, 64, 27) < n for n in range(28, 14593)), 'uniform tail k27')
    summary = {'widths': 14592, 'tested_pairs': 14592 * 64, 'admissible_pairs': pairs,
               'conservative_false_negatives': differing, 'general_width_cases': general,
               'max_k_at_capacity': rows[-1], 'capacity_child_bits': child_bits(14592, 64, 28),
               'next_k_child_bits': child_bits(14592, 64, 29),
               'best_k_vector_sha256': hashlib.sha256(bytes(rows)).hexdigest(),
               'largest_uniform_tail_k': 27, 'uniform_tail_first_width': 28}
    return {'status': 'PASS_SHARP_RESIDUE_WINDOW', 'summary': summary, 'precision': precision}


def backend(receipt):
    # Authentication occurs BEFORE executing predecessor code; suppress old pyc reads too.
    need(not any((ROOT / 'source').rglob('*.pyc')), 'untrusted predecessor bytecode')
    spec = importlib.util.spec_from_file_location('retained_hybrid', ROOT / 'source/hybrid.py')
    hybrid = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hybrid)
    seeds = hybrid.seed_lines()
    views = hybrid.precision_view(seeds, 180)
    cert = hybrid.certificate(views, 64, 28)
    need(cert['radius'] == receipt['precision'][28]['radius'], 'regenerated uniform radius')
    fresh = [hybrid.GaussianLine(s, t, 5, precision=180) for s, t in ((5, 8), (7, 16), (13, 32))]
    for line, view in zip(fresh, views):
        line.certify_operator()
        need(line.uniform_error == view.uniform_error and line.operator_error == view.operator_error,
             'fresh p180 operator certificate')
        need(line.expansion == view.expansion and line.compression == view.compression,
             'fresh p180 source matrices')
    cases = []
    for n, k in ((14592, 28), (65, 29)):
        lines = hybrid.precision_view(seeds, 208 - k)
        x = 2 ** n - 1
        answer, bill = hybrid.multiply(x, x, lines, digit_bits=64, k=k, input_bits=n)
        # The original-input exact product is a POSTCHECK, never supplies decoder data.
        need(answer == x * x, 'Gaussian returned product')
        lane = bill['exact_lane']
        need(lane['left_child_bits'] == lane['right_child_bits'] == child_bits(n, 64, k) < n,
             'actual sharp child')
        need(lane['exact_child_calls'] == 1, 'paid child')
        cases.append({'n': n, 'k': k, 'p': 208-k, 'bill': bill,
                      'answer_sha256': hashlib.sha256(answer.to_bytes((answer.bit_length()+7)//8, 'big')).hexdigest()})
    try:
        hybrid.certificate(hybrid.precision_view(seeds, 179), 64, 28)
    except ValueError as error:
        need('modular-recovery precision' in str(error), 'p179 failure reason')
    else:
        raise ValueError('p179 unexpectedly certified')
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arithmetic-only', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    authenticate()
    receipt = arithmetic()
    if not args.arithmetic_only:
        receipt['executed_gaussian_cases'] = backend(receipt)
    target = ROOT / 'RESULT.json'
    if args.write:
        need(not args.arithmetic_only, 'full result requires Gaussian execution')
        target.write_text(json.dumps(receipt, indent=2) + '\n')
    elif target.exists():
        expected = json.loads(target.read_text())
        if args.arithmetic_only:
            expected.pop('executed_gaussian_cases', None)
        need(receipt == expected, 'result mismatch')
    else:
        raise ValueError('result missing')
    print(json.dumps({'status': receipt['status'], 'summary': receipt['summary'],
                      'gaussian_cases': len(receipt.get('executed_gaussian_cases', []))}, sort_keys=True))


if __name__ == '__main__':
    main()
