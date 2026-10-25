#!/usr/bin/env python3
"""Behavioral and rejection controls for the correlated entrance certificate."""

import copy
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('correlated_entrance', PACKAGE / 'verify.py')
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('fixed local verifier loader')
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def rejected(call, label):
    try:
        call()
    except ValueError:
        return
    raise ValueError('accepted invalid control: ' + label)


def test_pairs():
    accepted, refused = 0, 0
    for ar in range(-3, 4):
        for ai in range(-3, 4):
            for br in range(-3, 4):
                for bi in range(-3, 4):
                    if ((ar - br) - (ai - bi)) % 2:
                        rejected(lambda a=(ar, ai), b=(br, bi): V.checked_pair(a, b), 'nonintegral ideal pair')
                        refused += 1
                    else:
                        left, right = V.checked_pair((ar, ai), (br, bi))
                        V.need(left[0] + right[0] == ar + br, 'real pair sum')
                        V.need(left[1] + right[1] == ai + bi, 'imaginary pair sum')
                        V.need(left[0] - right[0] == bi - ai, 'real rotated difference')
                        V.need(left[1] - right[1] == ar - br, 'imaginary rotated difference')
                        accepted += 1
    V.need(accepted + refused == 2401 and accepted > 0 and refused > 0, 'complete signed pair domain')
    return accepted, refused


def test_rows(word):
    changed = copy.deepcopy(word)
    changed['program'][1090][3] = '1/2'
    rejected(lambda: V.producer_rows(changed), 'wrong quarter')
    changed = copy.deepcopy(word)
    changed['program'][1129][2] = 'Y27'
    rejected(lambda: V.producer_rows(changed), 'lost independent source')
    changed = copy.deepcopy(word)
    changed['program'][1090][4] = []
    rejected(lambda: V.producer_rows(changed), 'wrong chronological frame')
    changed = copy.deepcopy(word)
    changed['program'][908][3] = '1'
    rejected(lambda: V.producer_rows(changed), 'wrong initial D sign')


def test_source_boundary(root):
    with tempfile.TemporaryDirectory(prefix='p104-correlated-controls-') as temporary:
        target = Path(temporary)
        inputs = target / 'research/p104-rounded-collector/inputs'
        inputs.mkdir(parents=True)
        for name in V.HASHES:
            shutil.copyfile(root / 'research/p104-rounded-collector/inputs' / name, inputs / name)
        word_path = inputs / 'WORD.json'
        word_path.write_bytes(word_path.read_bytes() + b' ')
        rejected(lambda: V.load_sources(target), 'changed source bytes')
        word_path.unlink()
        rejected(lambda: V.load_sources(target), 'missing source')


def test_lattice():
    values = [V.ZERO] * V.N
    values[0] = (64, 0)
    V.need(V.lattice_failure(values) is None, '64 impulse belongs to B9')
    V.need(V.lattice_failure(values, 4) is not None, '64 impulse is outside 4B9')
    values[0] = (256, 0)
    V.need(V.lattice_failure(values, 4) is None, '256 impulse belongs to 4B9')
    values = [V.ZERO] * V.N
    values[8] = (1, 0)
    V.need(V.lattice_failure(values) is not None, 'degree-one obstruction')
    values[8] = (1, 1)
    V.need(V.lattice_failure(values) is not None, 'higher mixed coefficient obstruction')
    V.need(V.lattice_failure([(1, 1)] * V.N) is None, 'constant Gaussian field')


def main():
    word, _ = V.load_sources(PACKAGE.parents[1])
    test_rows(word)
    test_source_boundary(PACKAGE.parents[1])
    test_lattice()
    counts = test_pairs()
    expected = json.loads((PACKAGE / 'RECEIPT.json').read_text())
    mutant = copy.deepcopy(expected)
    mutant['schema_version'] = True
    V.need(V.digest(mutant) != V.digest(expected), 'Boolean receipt type drift')
    print('PASS_P104_CORRELATED_CONTROLS groups=5 signed_pairs=' + str(counts))


if __name__ == '__main__':
    main()
