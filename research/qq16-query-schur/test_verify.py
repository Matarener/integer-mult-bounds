"""Boundary tests: minimal offline export, immutable sources and typed receipt."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

class Boundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='qq16-query-schur-')
        cls.root = Path(cls.tmp.name)
        cls.package = cls.root / 'research/qq16-query-schur'
        shutil.copytree(HERE, cls.package, ignore=shutil.ignore_patterns('__pycache__'))
        inputs = json.loads((HERE / 'VERIFY.json').read_text())['inputs']
        for name in inputs:
            dst = cls.root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dst)

    @classmethod
    def tearDownClass(cls):
        for p in cls.root.rglob('*'):
            p.chmod(0o755 if p.is_dir() else 0o644)
        cls.root.chmod(0o755)
        cls.tmp.cleanup()

    def run_check(self, options=(), tail=()):
        return subprocess.run([sys.executable, '-I', '-Werror', '-B', *options,
                               str(self.package / 'verify.py'), *tail],
                              cwd=self.root, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=180)

    def test_normal_optimized_readonly_export(self):
        files = [p for p in self.root.rglob('*') if p.is_file()]
        before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        for p in files:
            p.chmod(0o444)
        for p in sorted((p for p in self.root.rglob('*') if p.is_dir()), reverse=True):
            p.chmod(0o555)
        self.root.chmod(0o555)
        try:
            for opt in ((), ('-O',)):
                run = self.run_check(opt)
                self.assertEqual(run.returncode, 0, run.stdout)
                self.assertIn('PASS_QQ16_ORDERED_SCHUR_OBSTRUCTION', run.stdout)
            self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
        finally:
            self.root.chmod(0o755)
            for p in self.root.rglob('*'):
                p.chmod(0o755 if p.is_dir() else 0o644)

    def test_source_before_execution(self):
        p = self.root / 'research/qq16-line-normalized-decoder/verify.py'
        raw = p.read_bytes()
        try:
            p.write_bytes(b"raise RuntimeError('MUTATED_EXECUTED')\n" + raw)
            run = self.run_check(('-O',))
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('source SHA256:', run.stdout)
            self.assertNotIn('RuntimeError: MUTATED_EXECUTED', run.stdout)
        finally:
            p.write_bytes(raw)

    def test_complete_typed_receipt(self):
        path = self.package / 'RESULT.json'
        raw = path.read_bytes()
        try:
            value = json.loads(raw)
            value['response_injective'] = 1
            path.write_text(json.dumps(value))
            run = self.run_check(('-O',))
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('complete typed result mismatch', run.stdout)
        finally:
            path.write_bytes(raw)

    def test_manifest_reclassification(self):
        path = self.package / 'SOURCES.json'
        raw = path.read_bytes()
        try:
            value = json.loads(raw)
            next(x for x in value['files'] if x['usage'] == 'input')['usage'] = 'provenance'
            path.write_text(json.dumps(value))
            run = self.run_check(('-O',))
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('source manifest integrity', run.stdout)
        finally:
            path.write_bytes(raw)

    def test_generation_refuses_overwrite(self):
        raw = (self.package / 'RESULT.json').read_bytes()
        run = self.run_check(tail=('--write',))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('refuse overwrite', run.stdout)
        self.assertEqual(raw, (self.package / 'RESULT.json').read_bytes())

if __name__ == '__main__':
    unittest.main(verbosity=2)
