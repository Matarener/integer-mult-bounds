#!/usr/bin/env python3
"""Replay exact frozen proofs with explicit path and receipt adapters only."""
import argparse
import hashlib
import gzip
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


class Portable:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.hashes = json.loads((self.root / 'FROZEN-SHA256.json').read_text())
        self.patches = json.loads((self.root / 'ADAPTATIONS.json').read_text())
        self.executed = set()
        self.compared = set()
        self.words_compared = set()
        old = '/Users/ross/git/math/'
        self.prefixes = {
            old + 'integer-mult-bounds/': self.root / 'frozen/upstream',
            old + '.research-automation/runs/kappa-changed-endpoints-20261019T0153Z/': self.root / 'frozen/changed',
            old + '.research-automation/runs/kappa-major-20261018T1330Z/': self.root / 'frozen/major',
            old + '.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/': self.root / 'frozen/old',
        }

    def authenticate(self, path):
        path = Path(path).resolve()
        name = path.relative_to(self.root).as_posix()
        need(name in self.hashes, 'unregistered frozen input: ' + name)
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == self.hashes[name], 'frozen input changed: ' + name)
        return raw

    def adapted(self, path):
        name = Path(path).resolve().relative_to(self.root).as_posix()
        source = self.authenticate(path).decode()
        for edit in self.patches.get(name, []):
            need(source.count(edit['old']) == 1, 'adaptation no longer unique: ' + name)
            source = source.replace(edit['old'], edit['new'])
        return source

    def check_all(self):
        need(set(self.patches) <= set(self.hashes), 'unbound adaptation')
        for name in self.hashes:
            self.authenticate(self.root / name)
        for name in self.patches:
            self.adapted(self.root / name)

    def code(self, path):
        path = Path(path).resolve()
        source = self.adapted(path)
        self.executed.add(path.relative_to(self.root).as_posix())
        return compile(source, str(path), 'exec', dont_inherit=True, optimize=0)

    def normalize(self, value):
        if isinstance(value, str):
            for prefix, target in self.prefixes.items():
                if value.startswith(prefix):
                    return str(target / value[len(prefix):])
            return value
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                normalized_key = self.normalize(key)
                need(normalized_key not in result, 'normalized key collision')
                result[normalized_key] = self.normalize(item)
            return result
        if isinstance(value, list):
            return [self.normalize(v) for v in value]
        return value

    def word_equal(self, path, body):
        path = Path(path).resolve()
        need(gzip.decompress(self.authenticate(path)) == body, 'complete word/geometry mismatch')
        self.words_compared.add(path.relative_to(self.root).as_posix())
        return True

    def equal(self, path, value):
        path = Path(path).resolve()
        expected = json.loads(self.authenticate(path))
        actual = json.loads(json.dumps(value))
        # Compare every field, preserving JSON scalar types. Only original
        # absolute provenance paths are mapped into this relocated package.
        need(canonical(self.normalize(actual)) == canonical(self.normalize(expected)),
             'receipt mismatch: ' + path.name)
        self.compared.add(path.relative_to(self.root).as_posix())
        return True

    def install(self):
        portable = self
        original_code = importlib.machinery.SourceFileLoader.get_code
        original_exec = importlib.machinery.SourceFileLoader.exec_module

        def frozen(loader):
            return Path(loader.path).resolve().is_relative_to(portable.root / 'frozen')

        def get_code(loader, fullname):
            if frozen(loader):
                return portable.code(loader.path)
            return original_code(loader, fullname)

        def exec_module(loader, module):
            if frozen(loader):
                module.PORTABLE = portable
            return original_exec(loader, module)

        importlib.machinery.SourceFileLoader.get_code = get_code
        importlib.machinery.SourceFileLoader.exec_module = exec_module
        sys.path.insert(0, str(self.root / 'frozen/changed/bit-native-caller'))

    def load(self, path):
        spec = importlib.util.spec_from_file_location('portable_stage', self.root / path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module


PRE = 'frozen/changed/bit-native-caller/'
STAGES = {
 'roots': (PRE+'selective_union_batch.py',[PRE+'SELECTIVE-UNION-ROOTS-L8.json'],[]),
 'frames': (PRE+'selective_union_batch.py',[PRE+'SELECTIVE-UNION-FRAMES-L8.json'],[]),
 'check-roots': (PRE+'verify_union_partition.py',[],[]),
 'check-frames': (PRE+'verify_union_partition.py',[],[]),
 'independent': ('frozen/reviews/exposure/independent_check.py',['frozen/reviews/exposure/INDEPENDENT-RESULT.json'],[]),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=STAGES, required=True)
    args = parser.parse_args()
    portable = Portable(Path(__file__).resolve().parent)
    portable.check_all()
    portable.install()
    source, receipts, words = STAGES[args.stage]
    sys.argv = [str(portable.root / source)]
    module = portable.load(source)
    if args.stage in ('roots','frames'):
        module.receipt(args.stage,8,False)
    elif args.stage.startswith('check-'):
        mode=args.stage.removeprefix('check-')
        count=module.verify(portable.root/PRE/('SELECTIVE-UNION-'+mode.upper()+'-L8.json'))
        need(count == (120 if mode=='roots' else 153), 'complete original checker coverage')
    else:
        module.main()
    need(portable.compared == set(receipts), 'incomplete receipt coverage')
    need(portable.words_compared == set(words), 'incomplete word/geometry coverage')
    portable.check_all()
    print(canonical({'status': 'PASS_FIXED_EXPOSURE_UNIONS', 'stage': args.stage,
                     'receipts': sorted(portable.compared), 'sources': sorted(portable.executed),
                     'no_new_kappa': True}))


if __name__ == '__main__':
    main()
