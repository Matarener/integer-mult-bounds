"""Exact corroboration of the quadratic-union reduction; Apache-2.0."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import platform

PACKAGE = Path(__file__).resolve().parent


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def parity(value):
    return value.bit_count() & 1


def binary_rank(rows):
    basis = [0] * 4
    for value in rows:
        for pivot in range(3, -1, -1):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(value != 0 for value in basis)


def planes(dimension):
    require(2 <= dimension <= 8, 'plane ambient dimension')
    return [(a, b, a ^ b) for a in range(1, 1 << dimension)
            for b in range(a + 1, 1 << dimension) if (a ^ b) > b]


def quadratic_values(dimension, polar, linear):
    edges = list(combinations(range(dimension), 2))
    return [parity(x & linear) ^ (sum(
        ((x >> a) & 1) * ((x >> b) & 1) * ((polar >> k) & 1)
        for k, (a, b) in enumerate(edges)) & 1)
        for x in range(1 << dimension)]


def offsets(plane, code):
    return dict(zip(plane, (code & 1, code >> 1, parity(code))))


def slice_size(gauss):
    return 32 - 2 * gauss


def check_bound(size_a, size_b, union, dimension, consistent):
    require(union <= 68, 'universal union bound')
    shape = (dimension == 3 and not consistent
             and sorted((size_a, size_b)) == [32, 36])
    require((union == 68) == shape, 'complete equality shape')
    require(union % 2 == 0, 'even union cardinality')
    if size_a == size_b == 36:
        require(union <= 66, 'two maximum slices bound')


def consistent_cases(dimension, polar, pairs, counts, maxima):
    for linear in range(1 << dimension):
        values = quadratic_values(dimension, polar, linear)
        gauss = {p: 1 + sum(1 - 2 * values[x] for x in p)
                 for pair in pairs for p in pair}
        whole = sum(1 - 2 * value for value in values)
        numerator = (1 << 8) - 16 * whole
        require(numerator % (1 << (dimension + 1)) == 0,
                'integral intersection count')
        intersection = numerator // (1 << (dimension + 1))
        for a, b in pairs:
            size_a, size_b = slice_size(gauss[a]), slice_size(gauss[b])
            union = size_a + size_b - intersection
            check_bound(size_a, size_b, union, dimension, True)
            counts['consistent'] += 1
            if size_a == size_b == 36:
                maxima[dimension] = max(maxima.get(dimension, 0), union)


def inconsistent_cases(dimension, polar, pairs, counts):
    if dimension == 4:
        return  # The constraint planes have trivial intersection.
    values = quadratic_values(dimension, polar, 0)
    for a, b in pairs:
        common = set(a) & set(b)
        for code_a in range(4):
            first = offsets(a, code_a)
            for code_b in range(4):
                second = offsets(b, code_b)
                if all(first[x] == second[x] for x in common):
                    continue
                ga = 1 + sum(1 - 2 * (values[x] ^ first[x]) for x in a)
                gb = 1 + sum(1 - 2 * (values[x] ^ second[x]) for x in b)
                size_a, size_b = slice_size(ga), slice_size(gb)
                check_bound(size_a, size_b, size_a + size_b, dimension, False)
                if size_a + size_b == 68:
                    symplectic = a if ga == -2 else b
                    isotropic = b if ga == -2 else a
                    require(len(common) == 1, 'one shared nonzero vector')
                    require(all(values[x] ^ values[y] ^ values[x ^ y] == 0
                                for x in isotropic for y in isotropic),
                            '32-point equality plane is isotropic')
                    x, y = symplectic[:2]
                    require(values[x] ^ values[y] ^ values[x ^ y] == 1,
                            '36-point equality plane is symplectic')
                    counts['maximum_shape'] += 1
                counts['inconsistent'] += 1


def check_relative_forms():
    counts, maxima = Counter(), {}
    for dimension in range(2, 5):
        all_planes = planes(dimension)
        pairs = [(a, b) for index, a in enumerate(all_planes)
                 for b in all_planes[index:]
                 if binary_rank(a + b) == dimension]
        for polar in range(1 << (dimension * (dimension - 1) // 2)):
            consistent_cases(dimension, polar, pairs, counts, maxima)
            inconsistent_cases(dimension, polar, pairs, counts)
    require(counts['consistent'] + counts['inconsistent'] == 289440,
            'complete relative-form domain')
    require(maxima == {2: 36, 3: 52, 4: 66}, 'two-36 branch maxima')
    return {'counts': dict(counts), 'two_36_maxima_by_span': maxima}


def canonical_q(value):
    return sum(((value >> (2 * k)) & 1)
               * ((value >> (2 * k + 1)) & 1) for k in range(4)) & 1


def canonical_b(left, right):
    return canonical_q(left ^ right) ^ canonical_q(left) ^ canonical_q(right)


def check_all_slices():
    roots = [x for x in range(256) if canonical_q(x)]
    full = (1 << len(roots)) - 1
    zero = [sum(1 << i for i, u in enumerate(roots)
                if canonical_b(u, a) == 0) for a in range(256)]
    histogram = Counter()
    for plane in planes(8):
        a, b, _ = plane
        for code in range(4):
            first = zero[a] if not (code & 1) else full ^ zero[a]
            second = zero[b] if not (code >> 1) else full ^ zero[b]
            actual = (first & second).bit_count()
            off = offsets(plane, code)
            gauss = 1 + sum(1 - 2 * (canonical_q(x) ^ off[x]) for x in plane)
            require(actual == slice_size(gauss), 'direct slice/Fourier equality')
            histogram[actual] += 1
    require(sum(histogram.values()) == 43180, 'all affine plane constraints')
    require(set(histogram) == {24, 28, 32, 36}, 'slice cardinality spectrum')
    return {'root_lines': len(roots), 'slice_histogram': dict(histogram)}


def check_attainment():
    roots = {x for x in range(256) if canonical_q(x)}
    first = {x for x in roots if x & 3 == 3}
    second = {x for x in roots if not (x & 2) and x & 8}
    third = {x for x in roots if x & 12 == 12}
    require((len(first), len(second), len(first & second), len(first | second))
            == (36, 32, 0, 68), '68-point attainment')
    require((len(third), len(first & third), len(first | third)) == (36, 6, 66),
            'two-36 sharpness')
    return {'maximum_fixture': [len(first), len(second), len(first | second)],
            'two_36_fixture': [len(first), len(third), len(first | third)]}


def check_plus_hypothesis():
    minus = {x for x in range(256)
             if canonical_q(x) ^ (x & 1) ^ ((x >> 1) & 1)}
    first = {x for x in minus if not (x & 32) and not (x & 128)}
    second = {x for x in minus if x & 32 and not (x & 128)}
    require((len(minus), len(first), len(second), len(first | second))
            == (136, 40, 32, 72), 'opposite-sign counterdomain')
    return {'minus_shell': len(minus), 'minus_union': len(first | second)}


def check_e8_link():
    rows = json.loads((PACKAGE / 'SOURCES.json').read_text())['files']
    root = PACKAGE.parent.parent
    for row in rows:
        if row['usage'] == 'input':
            require(sha256((root / row['path']).read_bytes()).hexdigest()
                    == row['sha256'], 'declared source bytes')
    even = [x for x in range(512) if parity(x) == 0]
    nonsingular = {x for x in even if (x.bit_count() // 2) & 1}
    labels = {511 ^ x for x in nonsingular}
    ports_path = root / 'research/p104-carrier-code-uniqueness/e8/ports.json'
    ports = json.loads(ports_path.read_text())
    require(len(ports) == len(set(ports)) == 104 and set(ports) <= labels,
            'P104 is the declared puncture of the quadratic root model')
    require(len(labels) == 120, 'complete E8 label shell')
    gauss = sum(1 - 2 * ((x.bit_count() // 2) & 1) for x in even)
    require(gauss == 16, 'plus-type quadratic normalization')
    return {'quadratic_gauss_sum': gauss, 'full_labels': len(labels),
            'punctured_labels': len(ports), 'removed_lines': len(labels-set(ports))}


def check_rejections():
    rejected = 0
    bad = [(36, 36, 68, 3, False), (36, 32, 70, 4, True),
           (36, 32, 68, 4, True), (36, 32, 68, 3, True),
           (32, 32, 68, 3, False), (36, 36, 65, 4, True)]
    for args in bad:
        try:
            check_bound(*args)
        except ValueError:
            rejected += 1
    require(rejected == len(bad), 'false-bound and equality controls')
    try:
        planes(9)
    except ValueError:
        rejected += 1
    require(rejected == 7, 'dimension-domain rejection')
    return rejected


def main():
    result = {'status': 'PASS_P104_QUADRATIC_UNION_REDUCTION',
              'claim_type': 'scoped proof with finite exact corroboration',
              'relative_forms': check_relative_forms(),
              'all_slices': check_all_slices(), 'attainment': check_attainment(),
              'plus_hypothesis_control': check_plus_hypothesis(),
              'e8_link': check_e8_link(), 'rejected_controls': check_rejections(),
              'python': platform.python_version()}
    result['package_sha256'] = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.iterdir()) if path.is_file()}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
