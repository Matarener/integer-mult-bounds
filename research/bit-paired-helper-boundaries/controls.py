#!/usr/bin/env python3
"""Bounded source, complete ADDRESS-chart and whole-artifact controls."""
import copy
import gzip
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import tempfile


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('paired_verify', ROOT / 'verify.py')
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
    with tempfile.TemporaryDirectory(prefix='paired controls ') as directory:
        root = Path(directory) / 'relocated package'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('__pycache__'))
        p = verify.Portable(root)
        p.check_all()
        folder = root / 'frozen/changed/bit-native-caller'
        source = folder / 'cold_cosets.py'
        saved = source.read_bytes()
        source.write_bytes(saved + b'\n# changed source\n')
        reject(p.check_all, 'frozen input changed')
        source.write_bytes(saved)
        receipt = folder / 'KERNEL-ENTRANCES.json'
        raw = receipt.read_bytes()
        receipt.write_bytes(raw + b' ')
        reject(p.check_all, 'frozen input changed')
        receipt.write_bytes(raw)
        actual = json.loads(raw)
        verify.need(p.equal(receipt, actual), 'positive receipt control')
        changed = copy.deepcopy(actual)
        changed['compensation_kernel_witnesses'].pop()
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

        chart_path = folder / 'GLOBAL-KERNEL-E2.json'
        charts = json.loads(p.authenticate(chart_path))
        verify.need(p.equal(chart_path, charts), 'positive complete chart receipt')
        old_entry = charts['native_rational_ADDRESS_MOVE_charts'][0]['ADDRESS_C_inverse'][0][0]
        charts['native_rational_ADDRESS_MOVE_charts'][0]['ADDRESS_C_inverse'][0][0] = 'CORRUPTED_RATIONAL'
        reject(lambda: p.equal(chart_path, charts), 'receipt mismatch')
        charts['native_rational_ADDRESS_MOVE_charts'][0]['ADDRESS_C_inverse'][0][0] = old_entry
        charts['native_rational_ADDRESS_MOVE_charts'].pop()
        reject(lambda: p.equal(chart_path, charts), 'receipt mismatch')

        names = ['KERNEL-ENTRANCES-WORD.json.gz', 'GLOBAL-KERNEL-E2-WORD.json.gz',
                 'GLOBAL-KERNEL-E2-GEOMETRY.json.gz', 'OLD-KERNEL-E2-WORD.json.gz',
                 'OLD-KERNEL-E2-GEOMETRY.json.gz']
        for name in names:
            path = folder / name
            body = gzip.decompress(p.authenticate(path))
            p.word_equal(path, body)
            reject(lambda: p.word_equal(path, body[:-1]), 'complete word/geometry mismatch')
        verify.need(p.words_compared == {str((folder / n).relative_to(root)) for n in names},
                    'all five complete artifact comparisons')
        for name, field in [('GLOBAL-KERNEL-E2-WORD.json.gz', 'records'),
                            ('GLOBAL-KERNEL-E2-GEOMETRY.json.gz', 'frames')]:
            path = folder / name
            body = gzip.decompress(p.authenticate(path))
            # Regenerated compression choices do not enter the body comparison;
            # the frozen container itself remains authenticated by its hash.
            different_container = gzip.compress(body, compresslevel=1, mtime=123)
            verify.need(different_container != path.read_bytes(), 'different gzip fixture')
            p.word_equal(path, gzip.decompress(different_container))
            value = json.loads(body)
            value[field].pop()
            reject(lambda: p.word_equal(path, verify.canonical(value).encode()),
                   'complete word/geometry mismatch')

        cache = Path(importlib.util.cache_from_source(str(source)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        poison = Path(directory) / 'poison.py'
        payload = b"raise RuntimeError('POISONED_PAIRED_CACHE')\n#"
        verify.need(len(payload) < len(saved), 'cache fixture source size')
        poison.write_bytes(payload + b' ' * (len(saved) - len(payload)))
        info = source.stat()
        os.utime(poison, ns=(info.st_atime_ns, info.st_mtime_ns))
        py_compile.compile(str(poison), cfile=str(cache), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        try:
            exec(importlib.machinery.SourceFileLoader('cache_probe', str(source)).get_code('cache_probe'), {})
        except RuntimeError as error:
            verify.need(str(error) == 'POISONED_PAIRED_CACHE', 'wrong cache fixture failure')
        else:
            raise ValueError('poisoned cache fixture was not admitted')
        p.install()
        module = p.load('frozen/changed/bit-native-caller/global_kernel_boost.py')
        verify.need(list(module.bits(5)) == [0, 2], 'authenticated nested source execution')
        verify.need('frozen/changed/bit-native-caller/cold_cosets.py' in p.executed,
                    'nested source was not compiled')
        p.check_all()
        cache.unlink()
    print('PASS_PAIRED_CONTROLS source receipt complete_charts scalar_types path_collisions five_whole_artifacts compression_equivalence poisoned_cache nested_imports')


if __name__ == '__main__':
    main()
