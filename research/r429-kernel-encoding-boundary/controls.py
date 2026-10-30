#!/usr/bin/env python3
"""Small source, coverage and direct-loader controls for the fixed kerR probe."""
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
spec = importlib.util.spec_from_file_location('kerr_verify', ROOT / 'verify.py')
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
    with tempfile.TemporaryDirectory(prefix='kerr controls ') as directory:
        root = Path(directory) / 'relocated package'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('__pycache__'))
        p = verify.Portable(root)
        p.check_all()
        folder = root / 'frozen/changed/coded-bit-boundary'
        source = folder / 'ker_code_probe.py'
        saved = source.read_bytes()
        source.write_bytes(saved + b'\n# changed source\n')
        reject(p.check_all, 'frozen input changed')
        source.write_bytes(saved)
        receipt = folder / 'KER-CODE-NATIVE-REJECTION.json'
        raw = receipt.read_bytes()
        receipt.write_bytes(raw + b' ')
        reject(p.check_all, 'frozen input changed')
        receipt.write_bytes(raw)
        actual = json.loads(raw)
        verify.need(p.equal(receipt, actual), 'positive full receipt control')
        verify.need(actual['scalar_code']['independent_scalar_columns'] == 633
                    and len(actual['source_entrance_failure']['witnesses']) == 102
                    and len(actual['target_native_reconstruction']['last_MOVE_cuts']) == 9,
                    'complete coverage fixture')
        changed = copy.deepcopy(actual)
        changed['scalar_code']['independent_scalar_columns'] = 632
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['encoder_rows_102'].pop()
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['source_entrance_failure']['witnesses'].pop()
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['target_native_reconstruction']['last_MOVE_cuts'].popitem()
        reject(lambda: p.equal(receipt, changed), 'receipt mismatch')
        changed = copy.deepcopy(actual)
        changed['target_native_reconstruction']['rho_completed_cap_witnesses'].pop()
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

        # This producer has no scientific imports. Exercise its real direct
        # source loader with a cache that ordinary Python demonstrably admits.
        cache = Path(importlib.util.cache_from_source(str(source)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        poison = Path(directory) / 'poison.py'
        payload = b"raise RuntimeError('POISONED_KERR_CACHE')\n#"
        verify.need(len(payload) < len(saved), 'cache fixture source size')
        poison.write_bytes(payload + b' ' * (len(saved) - len(payload)))
        info = source.stat()
        os.utime(poison, ns=(info.st_atime_ns, info.st_mtime_ns))
        py_compile.compile(str(poison), cfile=str(cache), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        try:
            exec(importlib.machinery.SourceFileLoader('cache_probe', str(source)).get_code('cache_probe'), {})
        except RuntimeError as error:
            verify.need(str(error) == 'POISONED_KERR_CACHE', 'wrong cache fixture failure')
        else:
            raise ValueError('poisoned cache fixture was not admitted')
        p.install()
        module = p.load('frozen/changed/coded-bit-boundary/ker_code_probe.py')
        verify.need(module.rank2([1, 2, 3]) == 2, 'authenticated direct source execution')
        verify.need(p.executed == {'frozen/changed/coded-bit-boundary/ker_code_probe.py'},
                    'unexpected scientific import or missing direct compilation')
        p.check_all()
        cache.unlink()
    print('PASS_KERR_CONTROLS source receipt columns633 witnesses102 cuts9 scalar_types path_collisions direct_poisoned_cache')


if __name__ == '__main__':
    main()
