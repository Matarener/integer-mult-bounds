#!/usr/bin/env python3
"""Verify a strict rational reader-basis improvement. Nick Petalas. Apache-2.0."""
from fractions import Fraction
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import sys

from kernels import change_basis, require, supplied_factors

HERE = Path(__file__).resolve().parent


def support_bill(source, reader):
    return 2 * (sum(map(len, source)) + sum(map(len, reader)))


def metrics(source, reader):
    denominator = lcm(*(c.denominator for row in source + reader for c in row.values()))
    source_bound = max(sum(abs(row.get(port, 0)) for row in source) for port in range(112))
    reader_bound = max(sum(map(abs, row.values())) for row in reader)
    return dict(source_coefficients=sum(map(len, source)),
                reader_coefficients=sum(map(len, reader)),
                four_shear_coefficient_adds=support_bill(source, reader),
                common_denominator=denominator,
                maximum_coefficient=str(max(abs(c) for row in source + reader for c in row.values())),
                source_row_l1=str(source_bound), reader_row_l1=str(reader_bound))


def pair_product(source, reader, directions):
    result = {}
    for column in (4, 5):
        for output, coefficient in source[column].items():
            for packed, value in reader[column].items():
                port, shift = divmod(packed, 512)
                key = (output, port, shift ^ directions[output])
                result[key] = result.get(key, 0) + coefficient * value
    return {key: value for key, value in result.items() if value}


def apply_word(source, reader, directions, data, bank):
    """Execute all coefficients with one exact integer scale per shear."""
    require(len(data) == 112 and len(bank) == 30, 'payload dimensions')
    require(all(len(row) == 512 for row in data + bank), 'payload address width')
    denominator = lcm(*(c.denominator for row in source + reader for c in row.values()))
    centre, result = [row[:] for row in bank], [row[:] for row in data]
    count, scale = 0, 1
    for sign in (1, -1):
        gathered = [[denominator * value for value in row] for row in centre]
        for row in range(30):
            for packed, coefficient in reader[row].items():
                port, shift = divmod(packed, 512)
                numerator = coefficient * denominator
                require(numerator.denominator == 1, 'integer gather coefficient')
                numerator = sign * int(numerator)
                for address in range(512):
                    gathered[row][address] += numerator * result[port][address ^ shift]
                count += 1
        centre = gathered
        result = [[denominator * value for value in row] for row in result]
        scale *= denominator
        scattered = [[denominator * value for value in row] for row in result]
        for row in range(30):
            for port, coefficient in source[row].items():
                shift = directions[port]
                numerator = coefficient * denominator
                require(numerator.denominator == 1, 'integer scatter coefficient')
                numerator = sign * int(numerator)
                for address in range(512):
                    scattered[port][address] += numerator * centre[row][address ^ shift]
                count += 1
        result = scattered
        centre = [[denominator * value for value in row] for row in centre]
        scale *= denominator
    return result, centre, count, scale


def pair_controls(source, reader, directions, expected):
    rejected = 0
    for coefficient in (Fraction(1, 40), Fraction(-3, 40), Fraction(3, 20)):
        s, d = [row.copy() for row in source], [row.copy() for row in reader]
        change_basis(s, d, 4, 5, coefficient)
        require(support_bill(s, d) >= 20352, 'wrong coefficient must lose strict gain')
        rejected += 1
    s, d = [row.copy() for row in source], [row.copy() for row in reader]
    change_basis(s, d, 4, 5, Fraction(3, 40))
    s[4] = source[4].copy()
    require(pair_product(s, d, directions) != expected, 'missing inverse source update')
    rejected += 1
    d[5] = reader[5].copy()
    s[4] = source[4].copy()
    change_basis(s, d, 4, 5, Fraction(3, 40))
    key = min(d[5])
    d[5][key] += 1
    require(pair_product(s, d, directions) != expected, 'corrupted reader coefficient')
    return rejected + 1


def main():
    require(sys.version_info >= (3, 12), 'Python 3.12 or later')
    source, reader, directions = supplied_factors()
    before = metrics(source, reader)
    expected = pair_product(source, reader, directions)
    changed_s, changed_d = [row.copy() for row in source], [row.copy() for row in reader]
    change_basis(changed_s, changed_d, 4, 5, Fraction(3, 40))
    after = metrics(changed_s, changed_d)
    require(before['four_shear_coefficient_adds'] == 20352, 'supplied tariff')
    require(after['four_shear_coefficient_adds'] == 20344, 'strict new tariff')
    require((before['common_denominator'], after['common_denominator']) == (960, 1200),
            'changed common denominator')
    require(all(m['maximum_coefficient'] == '1' and m['source_row_l1'] == '9/4'
                and m['reader_row_l1'] == '1036/15' for m in (before, after)),
            'unchanged factor magnitude bounds')
    require((len(reader[5]), len(changed_d[5])) == (892, 888), 'four cancellations')
    require(pair_product(changed_s, changed_d, directions) == expected, 'all pair product coefficients')
    require(all(changed_s[j] == source[j] for j in range(30) if j != 4), 'untouched source columns')
    require(all(changed_d[j] == reader[j] for j in range(30) if j != 5), 'untouched reader rows')
    change_basis(changed_s, changed_d, 4, 5, Fraction(-3, 40))
    require(changed_s == source and changed_d == reader, 'literal inverse basis')
    controls = pair_controls(source, reader, directions, expected)
    # One finite payload checks literal instruction order; the written conjugacy
    # proof and coefficient identity cover arbitrary payloads and dirty banks.
    data = [[((port + 7) * (address + 11)) % 17 - 8
             for address in range(512)] for port in range(112)]
    bank = [[((row + 3) * (address + 5)) % 13 - 6
             for address in range(512)] for row in range(30)]
    old_output, old_bank, old_count, old_scale = apply_word(source, reader, directions, data, bank)
    change_basis(changed_s, changed_d, 4, 5, Fraction(3, 40))
    new_output, new_bank, new_count, new_scale = apply_word(changed_s, changed_d, directions, data, bank)
    require(all(new_scale * old_output[p][x] == old_scale * new_output[p][x]
                for p in range(112) for x in range(512)), 'literal data endpoints')
    require(all(old_bank[j][x] == old_scale * bank[j][x]
                and new_bank[j][x] == new_scale * bank[j][x]
                for j in range(30) for x in range(512)), 'literal dirty restoration')
    require((old_count, new_count) == (20352, 20344), 'executed instruction counts')
    hashes = {name: sha256((HERE / name).read_bytes()).hexdigest()
              for name in ('verify.py', 'kernels.py', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'README.md', 'PROOF.md')}
    receipt = dict(status='PASS_RATIONAL_READER_BASIS', before=before, after=after,
                   operation=[4, 5, '3/40'], address_count=512, dirty_fields=30,
                   compared_pair_product_coefficients=len(expected), rejection_controls=controls,
                   literal_payloads=1, package_sha256=hashes)
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
