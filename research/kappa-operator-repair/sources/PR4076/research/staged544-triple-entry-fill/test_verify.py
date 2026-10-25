"""Recipe rejection controls; explicit checks also under python -O."""
import copy
from verify import load, need, S


def reject(source, record, expected):
    try: S.apply(source, record)
    except ValueError as e: need(expected in str(e), 'wrong rejection: ' + str(e))
    else: raise ValueError('invalid construction accepted: ' + expected)


def main():
    _, source, record, target = load()[0]
    need(S.apply(source, record) == target, 'positive control')
    s = copy.deepcopy(source); s['ports'][0] ^= 1
    reject(s, record, 'source canonical digest')
    r = copy.deepcopy(record); r['entrances'][0]['old'] = [46]
    reject(source, r, 'entrance preimage')
    r = copy.deepcopy(record); r['entrances'][0]['new'] = r['entrances'][0]['new'] + [1]
    reject(source, r, 'entrance raised by exactly one dimension')
    r = copy.deepcopy(record); r['warps'][0][1] += 1
    reject(source, r, 'native identities and maps preserved')
    r = copy.deepcopy(record); r['target_canonical_sha256'] = '0' * 64
    reject(source, r, 'target canonical digest')
    r = copy.deepcopy(record); r['sections']['B'][0]['old'] = []
    reject(source, r, 'literal scalar preimage')
    r = copy.deepcopy(record); r['report']['local_profile']['1'] += 1
    reject(source, r, 'target canonical digest')
    print('PASS_7_RECIPE_CONTROLS')


if __name__ == '__main__':
    main()
