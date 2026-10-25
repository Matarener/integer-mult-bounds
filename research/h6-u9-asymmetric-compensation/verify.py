#!/usr/bin/env python3
"""Read-only replay of authenticated historical sources with explicit IO adapters."""
import argparse
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Portable:
    def __init__(self, root):
        self.root = root.resolve()
        self.hashes = json.loads((root / 'FROZEN-SHA256.json').read_text())
        self.patches = json.loads((root / 'ADAPTATIONS.json').read_text())
        self.executed = set()
        self.compared = set()
        old = '/Users/ross/git/math/'
        runs = old + '.research-automation/runs/'
        self.prefixes = {
            old + 'integer-mult-bounds/': self.root / 'source-context',
            runs + 'kappa-major-20261018T1330Z/': self.root,
            runs + 'kappa-changed-endpoints-20261019T0153Z/h6-fusion/': self.root / 'h6-fusion',
            runs + 'kappa-3605-successor-20261018T0940Z/major-frontier/complex-alternative/': self.root / 'legacy-budget',
        }

    def resolve(self, path):
        text = str(path)
        for prefix, replacement in self.prefixes.items():
            if text.startswith(prefix):
                return replacement / text[len(prefix):]
        return Path(path)

    def authenticate(self, path, raw=None):
        path = Path(path).resolve()
        name = path.relative_to(self.root).as_posix()
        need(name in self.hashes, 'unregistered frozen source: ' + name)
        if raw is None:
            raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == self.hashes[name], 'frozen source changed: ' + name)
        return raw

    def check_all(self):
        for name in self.hashes:
            self.authenticate(self.root / name)
        for name, edits in self.patches.items():
            text = self.authenticate(self.root / name).decode()
            for edit in edits:
                need(text.count(edit['old']) == 1, 'adaptation no longer unique: ' + name)
                text = text.replace(edit['old'], edit['new'])

    def code(self, path):
        path = Path(path).resolve()
        name = path.relative_to(self.root).as_posix()
        text = self.authenticate(path).decode()
        for edit in self.patches.get(name, []):
            need(text.count(edit['old']) == 1, 'adaptation no longer unique: ' + name)
            text = text.replace(edit['old'], edit['new'])
        self.executed.add(name)
        # Frozen mathematical assertions remain enabled even with an -O caller.
        return compile(text, str(path), 'exec', dont_inherit=True, optimize=0)

    def normalize(self, value):
        if isinstance(value, dict):
            return {str(self.resolve(k)): self.normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self.normalize(v) for v in value]
        return value

    def compare_json(self, path, value):
        path = Path(path)
        expected = json.loads(self.authenticate(path))
        actual = json.loads(json.dumps(value))
        name = path.relative_to(self.root).as_posix()
        # Only runtime observations vary. Every mathematical field is compared.
        ignored = {
            'partial-native/RESULT.json': ('elapsed_seconds', 'environment'),
            'partial-native/REPLAY-OPTIMIZED.json': ('elapsed_seconds', 'optimization_flag'),
        }.get(name, ())
        for key in ignored:
            need(key in actual and key in expected, 'missing runtime field: ' + key)
            del actual[key]
            del expected[key]
        actual, expected = self.normalize(actual), self.normalize(expected)
        if actual != expected:
            keys = sorted(k for k in set(actual) | set(expected) if actual.get(k) != expected.get(k))
            raise ValueError('receipt mismatch: ' + name + ' fields=' + repr(keys))
        self.compared.add(name)

    def compare_bytes(self, path, raw):
        need(self.authenticate(path) == raw, 'serialized recipe bytes differ: ' + str(path))
        self.compared.add(Path(path).relative_to(self.root).as_posix())

    def install(self):
        portable = self
        original_code = importlib.machinery.SourceFileLoader.get_code
        original_exec = importlib.machinery.SourceFileLoader.exec_module

        def get_code(loader, fullname):
            path = Path(loader.path).resolve()
            if path.is_relative_to(portable.root):
                return portable.code(path)
            return original_code(loader, fullname)

        def exec_module(loader, module):
            if Path(loader.path).resolve().is_relative_to(portable.root):
                module.PORTABLE = portable
            return original_exec(loader, module)

        importlib.machinery.SourceFileLoader.get_code = get_code
        importlib.machinery.SourceFileLoader.exec_module = exec_module

    def load(self, name):
        path = self.root / name
        spec = importlib.util.spec_from_file_location('portable_stage', path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module


STAGES = {
    'factor': ('bulk-partial/asymmetric.py', {'bulk-partial/ASYMMETRIC.json'}),
    'native': ('partial-native/audit.py', {'partial-native/RECIPES.json', 'partial-native/RESULT.json'}),
    'replay': ('partial-native/replay.py', {'partial-native/REPLAY-OPTIMIZED.json'}),
    'adapters': ('partial-native/adapter_work.py', {'partial-native/BASELINE-RECIPES.json', 'partial-native/ADAPTER-WORK.json'}),
    'precision': ('partial-native/precision.py', {'partial-native/PRECISION.json'}),
    'composition': ('h6-fusion/compose.py', {'h6-fusion/COMPOSITION.json'}),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=STAGES, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    portable = Portable(root)
    portable.check_all()
    portable.install()
    path, receipts = STAGES[args.stage]
    sys.argv = [str(root / path)]
    module = portable.load(path)
    module.main()
    need(portable.compared == receipts, 'incomplete receipt comparison')
    portable.check_all()
    print(json.dumps(dict(status='PASS_PORTABLE_C04', stage=args.stage,
                         caller_optimization=sys.flags.optimize, frozen_optimization=0,
                         receipts=sorted(portable.compared), executed_sources=sorted(portable.executed)), sort_keys=True))


if __name__ == '__main__':
    main()
