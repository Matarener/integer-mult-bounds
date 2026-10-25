"""Semantic rejection controls; explicit checks also under python -O."""
import copy
from apply_terminal import apply, need
from verify import load


def reject(source, patch, expected):
    try:
        apply(source, patch)
    except ValueError as e:
        need(expected in str(e), 'wrong rejection: ' + str(e))
    else:
        raise ValueError('invalid construction accepted: ' + expected)


def main():
    _, source, patch, target = load()[0]
    need(apply(source, patch) == target, 'positive control')
    s = copy.deepcopy(source); s['ports'][0] ^= 1
    reject(s, patch, 'source canonical hash')
    p = copy.deepcopy(patch); p['terminal_edits'][0]['old'] = []
    reject(source, p, 'terminal preimage')
    p = copy.deepcopy(patch); p['declared_profile']['1'] -= 1
    reject(source, p, 'declared profile')
    p = copy.deepcopy(patch); p['old_warps'][0][3] = []
    reject(source, p, 'native warp preimage')
    p = copy.deepcopy(patch); p['target_canonical_sha256'] = '0' * 64
    reject(source, p, 'target canonical hash')
    p = copy.deepcopy(patch); p['sections']['A'][0]['old'] = []
    reject(source, p, 'scalar splice preimage')
    print('PASS_6_RECIPE_CONTROLS')


if __name__ == '__main__':
    main()
