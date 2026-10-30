#!/usr/bin/env python3
"""Small source-binding and receipt-coverage rejection controls."""
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
spec = importlib.util.spec_from_file_location('r429_verify', ROOT / 'verify.py')
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
    with tempfile.TemporaryDirectory(prefix='r429 controls ') as directory:
        root = Path(directory) / 'relocated package'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('__pycache__'))
        p = verify.Portable(root)
        p.check_all()
        source = root / 'frozen/changed/bit-native-caller/cold_cosets.py'
        saved = source.read_bytes()
        source.write_bytes(saved + b'\n# changed source\n')
        reject(p.check_all, 'frozen input changed')
        source.write_bytes(saved)
        receipt = root / 'frozen/changed/bit-native-caller/UNIT-COLD-EXTENSION.json'
        raw = receipt.read_bytes()
        receipt.write_bytes(raw + b' ')
        reject(p.check_all, 'frozen input changed')
        receipt.write_bytes(raw)
        actual = json.loads(raw)
        verify.need(p.equal(receipt, actual), 'positive receipt control')
        changed = copy.deepcopy(actual)
        changed['source_hyperplane_code_bases'].pop()
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['R'][0] ^= 1
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['no_new_kappa'] = 1
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        old_key = next(iter(changed['sources']))
        mapped_key = p.normalize(old_key)
        verify.need(old_key != mapped_key, 'path alias fixture')
        original_hash = changed['sources'][old_key]
        changed['sources'][old_key] = 'MUTATED_PROVENANCE_HASH'
        changed['sources'][mapped_key] = original_hash
        reject(lambda: p.equal(receipt, changed), 'normalized key collision')

        # Construct a timestamp/size-valid poisoned cache and first demonstrate
        # that Python's ordinary source loader would accept its wrong code.
        cache = Path(importlib.util.cache_from_source(str(source)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        poison = Path(directory) / 'poison.py'
        payload = b"raise RuntimeError('POISONED_R429_CACHE')\n#"
        verify.need(len(payload) < len(saved), 'cache fixture source size')
        poison.write_bytes(payload + b' ' * (len(saved) - len(payload)))
        info = source.stat()
        os.utime(poison, ns=(info.st_atime_ns, info.st_mtime_ns))
        py_compile.compile(str(poison), cfile=str(cache), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        try:
            exec(importlib.machinery.SourceFileLoader('cache_probe', str(source)).get_code('cache_probe'), {})
        except RuntimeError as error:
            verify.need(str(error) == 'POISONED_R429_CACHE', 'wrong cache fixture failure')
        else:
            raise ValueError('poisoned cache fixture was not admitted')
        p.install()
        module = p.load('frozen/changed/bit-native-caller/ten_factor_floor56.py')
        verify.need(module.rank2([1, 2, 3]) == 2, 'authenticated nested source execution')
        verify.need('frozen/changed/bit-native-caller/cold_cosets.py' in p.executed,
                    'nested source was not compiled')
        p.check_all()
        cache.unlink()
    print('PASS_R429_READER_CONTROLS source receipt coverage scalar_types path_collisions poisoned_cache nested_imports')


if __name__ == '__main__':
    main()
