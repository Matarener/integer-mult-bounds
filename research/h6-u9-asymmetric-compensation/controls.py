#!/usr/bin/env python3
"""Defect-sensitive source/cache/assertion and receipt-comparison controls."""
import copy
import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import shutil
import struct
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
namespace = {'__name__': 'portable_controls', '__file__': str(ROOT / 'verify.py')}
exec(compile((ROOT / 'verify.py').read_bytes(), str(ROOT / 'verify.py'), 'exec'), namespace)
Portable, need = namespace['Portable'], namespace['need']


def reject(action, label):
    try:
        action()
    except ValueError:
        return
    raise ValueError('control accepted: ' + label)


def main():
    portable = Portable(ROOT)
    portable.check_all()
    source = ROOT / 'source-context/research/split-centres-global/vendor/clifford_exact.py'
    reject(lambda: portable.authenticate(source, source.read_bytes() + b'\n'), 'changed source')
    result = ROOT / 'partial-native/RESULT.json'
    original = json.loads(result.read_text())
    mutant = copy.deepcopy(original)
    mutant['rank_mass_change'] += 1
    reject(lambda: portable.compare_json(result, mutant), 'changed mathematical receipt')
    mutant = copy.deepcopy(original)
    del mutant['native_inverse_pair_checks']
    reject(lambda: portable.compare_json(result, mutant), 'missing coverage field')
    mutant = copy.deepcopy(original)
    mutant['elapsed_seconds'] += 1
    portable.compare_json(result, mutant)
    reject(lambda: portable.compare_bytes(ROOT / 'partial-native/RECIPES.json', b'{}\n'), 'changed recipe')
    # A valid timestamp/size-matching cache would raise if Python read it.
    # Load the real compiler, which reaches the poisoned vendor through a nested import.
    with tempfile.TemporaryDirectory(prefix='h6-u9-controls-') as directory:
        root = Path(directory)
        names = ['source-context/research/h6-compensation-network/physical_compiler/compile.py',
                 'source-context/research/split-centres-global/vendor/clifford_exact.py']
        hashes = {}
        for name in names:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
            hashes[name] = hashlib.sha256(target.read_bytes()).hexdigest()
            cache = Path(importlib.util.cache_from_source(str(target)))
            cache.parent.mkdir(parents=True, exist_ok=True)
            header = importlib.util.MAGIC_NUMBER + struct.pack('<III', 0, int(target.stat().st_mtime), target.stat().st_size)
            poison = compile("raise RuntimeError('unauthenticated cached code executed')", str(target), 'exec')
            cache.write_bytes(header + marshal.dumps(poison))
        (root / 'FROZEN-SHA256.json').write_text(json.dumps(hashes))
        (root / 'ADAPTATIONS.json').write_text('{}')
        isolated = Portable(root)
        isolated.check_all()
        isolated.install()
        compiler = isolated.load(names[0])
        try:
            compiler.ce.ident(1).then(compiler.ce.ident(2))
        except AssertionError:
            pass
        else:
            raise ValueError('retained operator-dimension assertion disabled')
        need(isolated.executed == set(names), 'nested authenticated source coverage')
    portable.check_all()
    print('PASS_PORTABLE_SOURCE_RECEIPT_CACHE_AND_ASSERTION_CONTROLS', sys.flags.optimize)


if __name__ == '__main__':
    main()
