"""Ring arithmetic oracles and real optimized Git-free CLI controls. Apache-2.0."""

import json
import shutil
import subprocess
import sys
import tempfile
from itertools import product
from pathlib import Path

from engine import HERE, need, pair
from independent import group_index
from module import image_index


def ring_oracle():
    for entries in product(range(4), repeat=4):
        dense = [entries[:2], entries[2:]]
        rows = [(sum((v & 1) << j for j, v in enumerate(row)),
                 sum(((v >> 1) & 1) << j for j, v in enumerate(row))) for row in dense]
        kernel = sum(all(sum(a * b for a, b in zip(row, x, strict=True)) % 4 == 0
                         for row in dense) for x in product(range(4), repeat=2))
        expected = (16 // kernel).bit_length() - 1
        need(image_index(rows, 2)['index_log2'] == expected, 'primary Z4 brute oracle')
        need(group_index(rows) == expected, 'separate Z4 brute oracle')
    return 256


def pair_oracle():
    for real_a, imag_a, real_b, imag_b in product(range(4), repeat=4):
        admitted = (real_a + imag_a - real_b - imag_b) % 2 == 0
        try:
            pair((real_a, imag_a), (real_b, imag_b))
        except ValueError:
            need(not admitted, 'rejected integral pair')
        else:
            need(admitted, 'accepted nonintegral pair')
    return 256


def cli(path, expected, label):
    result = subprocess.run([sys.executable, '-O', '-W', 'error', '-B', str(path)],
                            capture_output=True, text=True, timeout=180, check=False)
    need((result.returncode == 0) == expected, label + ' CLI status')
    need(len(result.stdout) + len(result.stderr) < 8192, 'bounded CLI diagnostics')
    return result


def relocated_controls():
    need(sys.argv[1:] == [], 'usage: test_controls.py')
    with tempfile.TemporaryDirectory(prefix='p104-full-prefix-') as directory:
        root = Path(directory)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        source = HERE.parents[1] / 'research/p104-rounded-collector/inputs'
        target = root / 'research/p104-rounded-collector/inputs'
        target.mkdir(parents=True)
        for name in ('WORD.json', 'NATIVE.json.gz'):
            shutil.copyfile(source / name, target / name)
        script = package / 'verify.py'
        accepted = cli(script, True, 'canonical Git-free')
        need('PASS_P104_CORRELATED_FULL_PREFIX' in accepted.stdout, 'real acceptance marker')
        receipt_path = package / 'RESULT.json'
        original = receipt_path.read_bytes()
        receipt = json.loads(original)
        receipt['maximal_full_prefix_module']['index_B9_log2'] = True
        receipt_path.write_text(json.dumps(receipt))
        rejected = cli(script, False, 'Boolean receipt')
        need('complete receipt mismatch' in rejected.stderr, 'typed receipt rejection')
        receipt_path.write_bytes(original)
        word = target / 'WORD.json'
        word.write_bytes(word.read_bytes() + b' ')
        need('source digest' in cli(script, False, 'source drift').stderr, 'source rejection')
        shutil.copyfile(source / 'WORD.json', word)
        (target / 'NATIVE.json.gz').unlink()
        need('regular source' in cli(script, False, 'missing source').stderr,
             'missing-source rejection')
    return 4


def main():
    ring, pairs, controls = ring_oracle(), pair_oracle(), relocated_controls()
    print(f'PASS_P104_FULL_PREFIX_CONTROLS ring_matrices={ring} pairs={pairs} CLIs={controls}')


if __name__ == '__main__':
    main()
