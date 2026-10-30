#!/usr/bin/env python3
"""Small rejection controls for exact C511 source and receipt binding."""
import copy
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import tempfile


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('c511_verify', ROOT / 'verify.py')
verify = importlib.util.module_from_spec(spec)
exec(compile((ROOT / 'verify.py').read_bytes(), str(ROOT / 'verify.py'),
             'exec', dont_inherit=True, optimize=0), verify.__dict__)


def reject(action, marker):
    try:
        action()
    except ValueError as error:
        verify.need(marker in str(error), 'wrong rejection: ' + str(error))
    else:
        raise ValueError('mutation accepted: ' + marker)


def main():
    with tempfile.TemporaryDirectory(prefix='c511 controls ') as directory:
        root = Path(directory) / 'relocated package'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('__pycache__'))
        p = verify.Portable(root)
        p.check_all()
        folder = root / 'frozen/changed/bit-native-caller'
        source = folder / 'physical_code.py'
        saved = source.read_bytes()
        source.write_bytes(saved + b'\n# changed source\n')
        reject(p.check_all, 'frozen input changed')
        source.write_bytes(saved)
        receipt = folder / 'MUTABLE-SOURCE-FIVE.json'
        raw = receipt.read_bytes()
        receipt.write_bytes(raw + b' ')
        reject(p.check_all, 'frozen input changed')
        receipt.write_bytes(raw)
        actual = json.loads(raw)
        verify.need(p.equal(receipt, actual), 'positive receipt control')
        changed = copy.deepcopy(actual)
        changed['C_binary_rows'].pop()
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['C_binary_rows'][0] ^= 1
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['no_new_kappa'] = 1
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['limits'].pop()
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        old_key = next(iter(changed['sources']))
        mapped_key = p.normalize(old_key)
        verify.need(old_key != mapped_key, 'path alias fixture')
        original_hash = changed['sources'][old_key]
        changed['sources'][old_key] = 'MUTATED_PROVENANCE_HASH'
        changed['sources'][mapped_key] = original_hash
        reject(lambda: p.equal(receipt, changed), 'normalized key collision')
        quotient = folder / 'MUTABLE-ROLLING-QUOTIENT.json'
        value = json.loads(p.authenticate(quotient))
        verify.need(p.equal(quotient, value), 'positive quotient control')
        value['row_echelon_certificate'].pop()
        reject(lambda: p.equal(quotient, value), 'receipt mismatch')

        # First demonstrate that ordinary Python admits a matching poisoned
        # cache; then load the real nested dependency through Portable.
        cache = Path(importlib.util.cache_from_source(str(source)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        poison = Path(directory) / 'poison.py'
        payload = b"raise RuntimeError('POISONED_C511_CACHE')\n#"
        verify.need(len(payload) < len(saved), 'cache fixture source size')
        poison.write_bytes(payload + b' ' * (len(saved) - len(payload)))
        info = source.stat()
        os.utime(poison, ns=(info.st_atime_ns, info.st_mtime_ns))
        py_compile.compile(str(poison), cfile=str(cache), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        try:
            exec(importlib.machinery.SourceFileLoader('cache_probe', str(source)).get_code('cache_probe'), {})
        except RuntimeError as error:
            verify.need(str(error) == 'POISONED_C511_CACHE', 'wrong cache fixture failure')
        else:
            raise ValueError('poisoned cache fixture was not admitted')
        p.install()
        module = p.load('frozen/changed/bit-native-caller/mutable_source_caller.py')
        verify.need(module.rank2([1, 2, 3]) == 2, 'authenticated nested source execution')
        verify.need('frozen/changed/bit-native-caller/physical_code.py' in p.executed,
                    'nested source was not compiled')
        p.check_all()
        cache.unlink()
    print('PASS_C511_CONTROLS source receipt complete_columns complete_witnesses scalar_types scope_fields path_collisions poisoned_cache nested_imports')


if __name__ == '__main__':
    main()
