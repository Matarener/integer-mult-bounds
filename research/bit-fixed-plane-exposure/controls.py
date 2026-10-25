#!/usr/bin/env python3
"""Bounded complete-plane, partition and authenticated-import controls."""
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
spec = importlib.util.spec_from_file_location('union_verify', ROOT / 'verify.py')
verify = importlib.util.module_from_spec(spec)
exec(compile((ROOT / 'verify.py').read_bytes(), str(ROOT / 'verify.py'),
             'exec', dont_inherit=True, optimize=0), verify.__dict__)


def reject(action, marker, error_type=ValueError):
    try:
        action()
    except error_type as error:
        verify.need(marker in str(error), 'wrong rejection: ' + str(error))
    else:
        raise ValueError('mutation accepted: ' + marker)


def main():
    with tempfile.TemporaryDirectory(prefix='union controls ') as directory:
        root = Path(directory) / 'relocated package'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('__pycache__'))
        p = verify.Portable(root)
        p.check_all()
        folder = root / 'frozen/changed/bit-native-caller'
        source = folder / 'selective_union_partition.py'
        saved = source.read_bytes()
        source.write_bytes(saved + b'\n# changed source\n')
        reject(p.check_all, 'frozen input changed')
        source.write_bytes(saved)
        roots_path = folder / 'SELECTIVE-UNION-ROOTS-L8.json'
        raw = roots_path.read_bytes()
        roots_path.write_bytes(raw + b' ')
        reject(p.check_all, 'frozen input changed')
        roots_path.write_bytes(raw)
        receipts = {}
        for mode, count in [('ROOTS', 120), ('FRAMES', 153)]:
            path = folder / ('SELECTIVE-UNION-' + mode + '-L8.json')
            actual = json.loads(p.authenticate(path))
            verify.need(len(actual['runs']) == count and actual['planes_tested'] == count,
                        'complete plane fixture')
            verify.need(all(len(run['exposure_masks']) == 438 for run in actual['runs']),
                        'complete helper-mask fixture')
            p.equal(path, actual)
            changed = copy.deepcopy(actual)
            changed['runs'].pop()
            reject(lambda: p.equal(path, changed), 'receipt mismatch')
            changed = copy.deepcopy(actual)
            changed['runs'][0]['exposure_masks'].pop()
            reject(lambda: p.equal(path, changed), 'receipt mismatch')
            changed = copy.deepcopy(actual)
            changed['runs'][0]['partition_D_colors'][0].pop()
            reject(lambda: p.equal(path, changed), 'receipt mismatch')
            changed = copy.deepcopy(actual)
            resource = next(iter(changed['runs'][0]['partition_resource_slots']))
            changed['runs'][0]['partition_resource_slots'].pop(resource)
            reject(lambda: p.equal(path, changed), 'receipt mismatch')
            changed = copy.deepcopy(actual)
            changed['no_new_kappa'] = 1
            reject(lambda: p.equal(path, changed), 'receipt mismatch')
            receipts[mode] = actual
        changed = copy.deepcopy(receipts['ROOTS'])
        old_key = next(iter(changed['source']))
        mapped_key = p.normalize(old_key)
        verify.need(old_key != mapped_key, 'path alias fixture')
        digest = changed['source'][old_key]
        changed['source'][old_key] = 'MUTATED_SOURCE_HASH'
        changed['source'][mapped_key] = digest
        reject(lambda: p.equal(roots_path, changed), 'normalized key collision')

        cache = Path(importlib.util.cache_from_source(str(source)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        poison = Path(directory) / 'poison.py'
        payload = b"raise RuntimeError('POISONED_UNION_CACHE')\n#"
        verify.need(len(payload) < len(saved), 'cache fixture source size')
        poison.write_bytes(payload + b' ' * (len(saved) - len(payload)))
        info = source.stat()
        os.utime(poison, ns=(info.st_atime_ns, info.st_mtime_ns))
        py_compile.compile(str(poison), cfile=str(cache), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        try:
            exec(importlib.machinery.SourceFileLoader('cache_probe', str(source)).get_code('cache_probe'), {})
        except RuntimeError as error:
            verify.need(str(error) == 'POISONED_UNION_CACHE', 'wrong cache fixture failure')
        else:
            raise ValueError('poisoned cache fixture was not admitted')
        p.install()
        batch = p.load('frozen/changed/bit-native-caller/selective_union_batch.py')
        tiny = batch.solve([1], [0], 1, 8)
        verify.need(tiny['assigned_color_copies'] == 1 and tiny['optimum_auxiliary_profit'] == 0,
                    'authenticated nested partition source execution')
        verify.need('frozen/changed/bit-native-caller/selective_union_partition.py' in p.executed,
                    'nested partition source not compiled')
        checker = p.load('frozen/changed/bit-native-caller/verify_union_partition.py')
        for actual in receipts.values():
            run = actual['runs'][0]
            columns = actual['semantic_dirty_columns']
            masks = list(map(int, run['exposure_masks']))
            verify.need(checker.primal(run, columns, masks) == 0, 'positive retained partition')
            changed = copy.deepcopy(run)
            changed['partition_D_colors'][0].pop()
            reject(lambda: checker.primal(changed, columns, masks),
                   'unassigned complement', RuntimeError)
            changed = copy.deepcopy(run)
            changed['partition_D_colors'][0].append(changed['partition_D_colors'][0][0])
            reject(lambda: checker.primal(changed, columns, masks),
                   'D partition repeated node', RuntimeError)
        # Exercise the adapted historical source-SHA loop before any geometry
        # work: a bad retained source digest must reject immediately.
        changed = copy.deepcopy(receipts['ROOTS'])
        changed['source'][old_key] = 'MUTATED_SOURCE_HASH'
        bad_path = Path(directory) / 'bad source digest.json'
        bad_path.write_text(json.dumps(changed))
        reject(lambda: checker.verify(bad_path), 'source hash ', RuntimeError)
        p.check_all()
        cache.unlink()
    print('PASS_UNION_CONTROLS source typed_receipts complete_planes masks partitions path_collisions historical_source_hash poisoned_nested_cache')


if __name__ == '__main__':
    main()
