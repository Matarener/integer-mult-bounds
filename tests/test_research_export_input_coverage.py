"""Self-consistent bundle bytes can still omit a declared replay input."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import export_research_package as exporter
sys.path.pop(0)


class ExportInputCoverageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name); self.archive = self.root / 'bundle.tar'
        self.package = 'research/fixture'

    def bundle(self, inputs=(), payloads=None, raw_manifest=None):
        files = {self.package + '/VERIFY.json': raw_manifest if raw_manifest is not None else json.dumps({'inputs': list(inputs)}).encode(),
                 self.package + '/README.md': b'scope', **(payloads or {})}
        receipt = {'format': exporter.FORMAT, 'commit': 'a' * 40, 'package': self.package,
                   'files': [{'path': name, 'mode': 0o644, 'size': len(data), 'sha256': sha256(data).hexdigest()}
                             for name, data in files.items()]}
        with tarfile.open(self.archive, 'w') as archive:
            for name, data in files.items():archive.addfile(*exporter.member(name, data))
            archive.addfile(*exporter.member(exporter.RECEIPT, json.dumps(receipt).encode()))
        return receipt

    def test_valid_package_and_literal_external_inputs_pass(self):
        receipt = self.bundle(['inputs/a[b] κ.bin'], {'inputs/a[b] κ.bin': b'\0\xff'})
        self.assertEqual(exporter.check_bundle(self.archive), receipt)
        self.assertEqual(exporter.check_bundle(self.archive, check_inputs=True), {**receipt, 'declared_inputs_checked': 1})
        self.assertEqual([p.name for p in self.root.iterdir()], ['bundle.tar'])

    def test_missing_declared_file_is_detected_after_integrity_passes(self):
        self.bundle(['missing.bin'])
        exporter.check_bundle(self.archive)
        with self.assertRaisesRegex(ValueError, 'missing bundled declared input: missing.bin'):
            exporter.check_bundle(self.archive, check_inputs=True)

    def test_undeclared_external_file_is_rejected_but_package_files_are_allowed(self):
        self.bundle(payloads={'unrelated.bin': b'extra'})
        with self.assertRaisesRegex(ValueError, 'undeclared external bundle file'):
            exporter.check_bundle(self.archive, check_inputs=True)
        self.bundle()
        self.assertEqual(exporter.check_bundle(self.archive, check_inputs=True)['declared_inputs_checked'], 0)

    def test_ambiguous_invalid_or_excessive_declarations_fail(self):
        cases = [(b'[]', 'inputs list'), (b'{"inputs":42}', 'inputs list'),
                 (b'{"inputs":[],"inputs":[]}', 'duplicate bundled manifest key'),
                 (b'{"inputs":["x","x"]}', 'duplicate bundled input'),
                 (b'{"inputs":["../outside"]}', 'canonical repository-relative'),
                 (json.dumps({'inputs': [exporter.RECEIPT]}).encode(), 'reserved declared input'),
                 (json.dumps({'inputs': ['x'] * 100001}).encode(), 'input count exceeds')]
        for raw, message in cases:
            with self.subTest(message=message):
                self.bundle(raw_manifest=raw)
                with self.assertRaisesRegex(ValueError, message):exporter.check_bundle(self.archive, check_inputs=True)

    def test_second_read_is_bound_to_the_checked_manifest_bytes(self):
        receipt = self.bundle()
        seen = {row['path']: row for row in receipt['files']}
        self.bundle(['changed.bin'], {'changed.bin': b'new'})
        with self.assertRaisesRegex(ValueError, 'manifest changed during declaration check'):
            exporter.check_declared_inputs(self.archive, receipt, seen)

    def test_real_optimized_cli_checks_declarations_without_git(self):
        self.bundle(['input.bin'], {'input.bin': b'data'})
        env = dict(os.environ, PATH='')
        result = subprocess.run([sys.executable, '-O', '-B', str(ROOT / 'scripts/export_research_package.py'),
                                 'check', str(self.archive), '--check-inputs'], env=env, capture_output=True, text=True, check=True)
        prefix, payload = result.stdout.strip().split(' ', 1)
        self.assertEqual(prefix, 'PASS_RESEARCH_EXPORT')
        self.assertEqual(json.loads(payload)['declared_inputs_checked'], 1)


if __name__ == '__main__':
    unittest.main()
