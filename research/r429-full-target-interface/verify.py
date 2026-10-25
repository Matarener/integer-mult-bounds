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
        legacy = json.loads(self.authenticate(self.root / 'frozen/major/bit-endpoint/BIT-FULL-COMPENSATION.json'))
        current = json.loads(self.authenticate(self.root / 'frozen/current/EXPECTED-COMPENSATION.json'))
        need(legacy.pop('allsize_lift') != current.pop('allsize_lift'), 'missing prose correction')
        need(canonical(legacy) == canonical(current), 'correction changed a scientific receipt field')

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

    def word_equal(self, path, compressed):
        path = Path(path).resolve()
        expected = gzip.decompress(self.authenticate(path))
        actual = gzip.decompress(compressed)
        need(actual == expected, 'complete regenerated word mismatch')
        # Container bytes are frozen provenance. Regenerated zlib headers or
        # compression choices are not a semantic acceptance criterion.
        self.words_compared.add(path.relative_to(self.root).as_posix())
        return len(compressed)

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
        sys.path.insert(0, str(self.root / 'frozen/major/bit-endpoint'))

    def load(self, path):
        spec = importlib.util.spec_from_file_location('portable_stage', self.root / path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module


STAGES = {
    'independent-caller': ('frozen/reviews/caller/independent_check.py', 'frozen/reviews/caller/INDEPENDENT-RESULT.json'),
    'independent-native': ('frozen/reviews/native/independent_check.py', 'frozen/reviews/native/RESULT.json'),
    'compensation': ('frozen/major/bit-endpoint/bit_full_compensation.py', 'frozen/current/EXPECTED-COMPENSATION.json'),
    'caller': ('frozen/major/shared-helper-algebra/bit_seeded_star.py', 'frozen/major/shared-helper-algebra/BIT-SEEDED-STAR.json'),
    'pressure': ('frozen/changed/budgets/seeded_star_pressure.py', 'frozen/changed/budgets/SEEDED-STAR-PRESSURE.json'),
}
INDEPENDENT = {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=STAGES, required=True)
    args = parser.parse_args()
    portable = Portable(Path(__file__).resolve().parent)
    portable.check_all()
    portable.install()
    source, receipt = STAGES[args.stage]
    stages = [(source, receipt)]
    if args.stage in INDEPENDENT:
        stages.append(INDEPENDENT[args.stage])
    for source, _ in stages:
        sys.argv = [str(portable.root / source)]
        portable.load(source).main()
    need(portable.compared == {receipt for _, receipt in stages}, 'incomplete receipt coverage')
    required_words = {'frozen/major/bit-endpoint/BIT-FULL-COMPENSATION-WORD.json.gz'} if args.stage == 'compensation' else set()
    need(portable.words_compared == required_words, 'incomplete regenerated word coverage')
    portable.check_all()
    print(canonical({'status': 'PASS_R429_FULL_TARGET_INTERFACE', 'stage': args.stage,
                     'receipts': sorted(portable.compared), 'sources': sorted(portable.executed),
                     'no_new_kappa': True}))


if __name__ == '__main__':
    main()
