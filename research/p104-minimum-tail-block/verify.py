#!/usr/bin/env python3
"""Derive a new block threshold from retained, explicitly cited scalar premises."""

import argparse
import hashlib
import json
import platform
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ORIGINS_SHA256 = 'f3f7bf2007083de3cfd44850e9868ea46e8765c5b1d09bd6aed504b9be7711f5'
FILES = (
    'ORIGINS.json', 'PROOF.md', 'README.md', 'SOURCES.json', 'TASK.json',
    'VERIFY.json', 'premises/INVOICE.json', 'premises/PROOF.md',
    'premises/RESULT.json', 'verify.py',
)
RESERVE = Q(1, 16)
DECAY = Q(1951, 2000)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(name):
    with (PACKAGE / name).open('rb') as source:
        data = source.read(131073)
    need(len(data) <= 131072, 'source size')
    return data


def check_bytes(data, row):
    need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source hash')
    header = b'blob ' + str(len(data)).encode('ascii') + b'\0'
    need(hashlib.sha1(header + data).hexdigest() == row['git_blob'], 'source blob')


def cited_premises():
    raw = read_bytes('ORIGINS.json')
    need(hashlib.sha256(raw).hexdigest() == ORIGINS_SHA256, 'origins hash')
    origins = json.loads(raw)
    need(origins['repository'] == 'CrocSwap/integer-mult-bounds', 'repository')
    need(origins['head'] == '56dc0a9ec02020f5e035c7d83f078fb2b27ac76a', 'source head')
    need(origins['pull_request'] == 5775, 'source PR')
    expected = {'premises/INVOICE.json', 'premises/PROOF.md', 'premises/RESULT.json'}
    need(len(origins['files']) == 3, 'source count')
    need({row['retained_path'] for row in origins['files']} == expected, 'source paths')
    for row in origins['files']:
        check_bytes(read_bytes(row['retained_path']), row)
    result = json.loads(read_bytes('premises/RESULT.json'))
    invoice = json.loads(read_bytes('premises/INVOICE.json'))['complete_cost']
    strict = invoice['strictification']
    need(Q(strict['tested']) == Q(622627591, 200000000000), 'saving premise')
    need(0 < Q(strict['tested']) < Q(1, 2), 'completion monotonicity premise')
    need((strict['cutoff'], strict['floor'], Q(strict['tail_offset']))
         == (16, 17, Q(1, 7)), 'witness premise')
    return {
        'a15': Q(result['cutoff15_minimum']['lower']),
        'a16': Q(result['best_decay_infimum']['lower']),
        'd17': Q(result['cutoff17_completion_lower']['lower']),
        'd18': Q(result['floor18_completion_lower']['lower']),
        'gamma': Q(strict['gamma']['upper']),
        'delta': Q(strict['delta']['upper']),
        'bad_offset': Q(result['offset_one_fifth_gamma']['lower']),
    }, origins


def check_witness(length, cutoff, floor, decay, paid_upper, completion_upper):
    need(type(length) is int and 3 <= length <= 4096, 'length domain')
    need(type(cutoff) is int and type(floor) is int
         and 1 <= cutoff <= 4096 and 1 <= floor <= 4096, 'capacity domain')
    need(0 < decay < 1 and paid_upper > 0 and completion_upper > 0, 'tail domain')
    need(paid_upper < decay, 'paid tail')
    need(completion_upper < decay, 'completion tail')
    need(decay ** length < RESERVE, 'reserve')
    need(cutoff ** length < floor ** (length - 2), 'capacity')


def check_threshold(lower, length):
    need(type(length) is int and 3 <= length <= 4096, 'threshold domain')
    need(0 < lower < 1, 'lower domain')
    need(lower ** (length - 1) > RESERVE, 'lower boundary')


def derive(bounds):
    need(0 < bounds['a16'] < bounds['a15'] < bounds['d17'] < 1, 'lower ordering')
    need(bounds['a15'] < bounds['d18'] < 1, 'floor ordering')
    need(bounds['gamma'] < Q(975485, 1000000), 'displayed paid upper bound')
    need(bounds['delta'] < Q(945, 1000), 'displayed completion upper bound')
    length = 112
    check_threshold(bounds['a16'], length)
    check_witness(length, 16, 17, DECAY, bounds['gamma'], bounds['delta'])
    need(bounds['a15'] ** length > RESERVE, 'other cutoffs at minimum')
    need(bounds['d17'] ** length > RESERVE, 'large cutoffs at minimum')
    need(bounds['d18'] ** length > RESERVE, 'large floors at minimum')
    excluded = 0
    for candidate in range(3, length):
        need(bounds['a16'] ** candidate > RESERVE, 'finite length corroboration')
        excluded += 1
    return {
        'claim_type': 'scoped proof using cited predecessor scalar premises',
        'minimum_block_length': length,
        'unique_cutoff_floor_at_minimum': [16, 17],
        'witness': {'offset': '1/7', 'decay': str(DECAY)},
        'excluded_integer_lengths_enumerated': excluded,
        'new_reserve_slack': str(RESERVE - DECAY ** length),
        'shortening_from_128': str(Q(128 - length, 128)),
    }


def controls(bounds, origins):
    cases = (
        (111, 16, 17, DECAY, bounds['gamma'], bounds['delta'], 'reserve'),
        (112, 16, 17, Q(125, 128), bounds['gamma'], bounds['delta'], 'reserve'),
        (112, 16, 17, DECAY, bounds['bad_offset'], bounds['delta'], 'paid tail'),
        (112, 16, 18, DECAY, bounds['gamma'], bounds['d18'], 'completion tail'),
        (2, 16, 17, DECAY, bounds['gamma'], bounds['delta'], 'length domain'),
        (4, 1, 2, Q(1, 2), Q(1, 3), Q(1, 3), 'reserve'),
        (4, 1, 1, Q(1, 3), Q(1, 4), Q(1, 4), 'capacity'),
    )
    rejected = 0
    for length, cutoff, floor, decay, paid, completion, reason in cases:
        try:
            check_witness(length, cutoff, floor, decay, paid, completion)
        except ValueError as exc:
            need(str(exc) == reason, 'wrong witness rejection')
            rejected += 1
        else:
            raise ValueError('accepted invalid witness')
    for lower, length in ((Q(97, 100), 112), (bounds['a16'], 113)):
        try:
            check_threshold(lower, length)
        except ValueError as exc:
            need(str(exc) == 'lower boundary', 'wrong threshold rejection')
            rejected += 1
        else:
            raise ValueError('accepted unsupported threshold')
    row = origins['files'][0]
    try:
        check_bytes(read_bytes(row['retained_path']) + b' ', row)
    except ValueError as exc:
        need(str(exc) == 'source hash', 'wrong corruption rejection')
        rejected += 1
    else:
        raise ValueError('accepted corrupt source')
    need(rejected == 10, 'control coverage')
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, help='write a hash-bound receipt outside the package')
    args = parser.parse_args()
    bounds, origins = cited_premises()
    result = derive(bounds)
    result['controls'] = controls(bounds, origins)
    if args.receipt is not None:
        destination = args.receipt.resolve()
        need(not destination.is_relative_to(PACKAGE), 'receipt must be outside the package')
        receipt = {
            'result': result,
            'source_status': 'Cited bounds authenticated, not independently replayed.',
            'python': platform.python_version(),
            'files': {name: hashlib.sha256(read_bytes(name)).hexdigest() for name in FILES},
        }
        destination.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print('PASS_MINIMUM_TAIL_BLOCK minimum=112 cutoff=16 floor=17'
          f" excluded_lengths={result['excluded_integer_lengths_enumerated']}"
          f" controls={result['controls']}")


if __name__ == '__main__':
    main()
