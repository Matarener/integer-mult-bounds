#!/usr/bin/env python3
"""Source-preserving CLI replay of the selected-checker JSON locale failure.

Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance. Apache-2.0. Source-binding logic remains Douglas Colkitt's.
"""
from hashlib import sha256
import difflib
import json
import locale
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'scripts/verify_selected_result.py'
SOURCE_SHA256 = 'd6b305eac5b9bdb8172c469ad30a1655a60fa0aceac8b1bf610e1b73f51babd8'
FORCE_CP1252 = """
import io
import runpy
import sys
original = io.text_encoding
def text_encoding(encoding, stacklevel=2):
    if encoding is None:
        return 'utf-8' if sys.flags.utf8_mode else 'cp1252'
    if encoding == 'locale':
        return 'cp1252'
    return original(encoding, stacklevel)
io.text_encoding = text_encoding
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""


def source_bytes():
    raw = SOURCE.read_bytes()
    if sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('Pinned selected checker bytes changed')
    return raw


def proposed_repair(raw):
    """Apply the three-line candidate only to a private temporary source copy."""
    for name in (b'certificate_path', b'manifest_path', b'args.record'):
        old = name + b'.read_text()'
        if raw.count(old) != 1:
            raise ValueError('Candidate patch no longer matches its pinned source')
        raw = raw.replace(old, name + b".read_text(encoding='utf-8')")
    return raw


class SelectedJsonLocaleReplay(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ('scripts', 'certificates', 'supplier'):
            (self.root / name).mkdir()
        self.script = self.root / 'scripts/verify_selected_result.py'
        self.original = source_bytes()

    def fixture(self, unicode_at=None, malformed_at=None, unicode_path=False):
        proof = 'supplier/preuve-\u00e9.txt' if unicode_path else 'supplier/proof.txt'
        (self.root / proof).write_bytes(b'immutable proof\n')
        digest = sha256((self.root / proof).read_bytes()).hexdigest()
        claim = {'kappa': '1/1000'}
        manifest = {'format': 'repository-files-sha256-v1', 'files': {proof: digest}}
        record = {
            'kappa': '1/1000', 'decimal': '0.001',
            'certificate': 'certificate.json', 'source_manifest': 'manifest.json',
            'proof': proof, 'review': proof, 'validation': 'certificate.json',
            'proof_supplements': {proof: digest},
        }
        values = {'certificate': claim, 'manifest': manifest, 'record': record}
        paths = {'certificate': 'certificate.json', 'manifest': 'manifest.json',
                 'record': 'certificates/selected-result.json'}
        if unicode_at:
            # U+211D ends in UTF-8 byte 0x9d, which is undefined in cp1252.
            values[unicode_at]['description'] = 'Coefficient field \u211d'
        if malformed_at:
            values[malformed_at]['description'] = 'INVALID_UTF8'
        for key in ('certificate', 'manifest', 'record'):
            if key == 'record':
                record['certificate_sha256'] = sha256(
                    (self.root / 'certificate.json').read_bytes()).hexdigest()
            raw = (json.dumps(values[key], ensure_ascii=False) + '\n').encode('utf-8')
            if key == malformed_at:
                raw = raw.replace(b'INVALID_UTF8', b'\xff')
            (self.root / paths[key]).write_bytes(raw)
        return proof

    def replay(self, mode, native=False):
        raw = proposed_repair(self.original) if mode == 'patch' else self.original
        self.script.write_bytes(raw)
        flag = 'utf8' if mode == 'utf8' else 'utf8=0'
        argv = [sys.executable, '-I', '-X', flag, '-B']
        if not native:
            argv += ['-c', FORCE_CP1252]
        argv += [str(self.script)]
        result = subprocess.run(argv, cwd=self.root, capture_output=True, timeout=20)
        self.assertEqual(self.script.read_bytes(), raw)
        return result

    def assert_pass(self, result):
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
        self.assertIn(b'PASS selected record, exact kappa', result.stdout)
        self.assertIn(b'1/1000', result.stdout)

    def assert_rejected(self, result, diagnostic):
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(diagnostic, result.stderr)
        self.assertNotIn(b'PASS selected record', result.stdout)

    def test_ascii_control_all_modes(self):
        self.fixture()
        for mode in ('legacy', 'utf8', 'patch'):
            with self.subTest(mode=mode):
                self.assert_pass(self.replay(mode))

    def test_original_fails_at_each_utf8_json_boundary(self):
        for key in ('record', 'certificate', 'manifest'):
            with self.subTest(boundary=key):
                self.fixture(unicode_at=key)
                self.assert_rejected(self.replay('legacy'), b'UnicodeDecodeError')

    def test_utf8_mode_and_temporary_patch_repair_each_boundary(self):
        for mode in ('utf8', 'patch'):
            for key in ('record', 'certificate', 'manifest'):
                with self.subTest(mode=mode, boundary=key):
                    self.fixture(unicode_at=key)
                    self.assert_pass(self.replay(mode))

    def test_unicode_inventory_path_keeps_exact_spelling(self):
        self.fixture(unicode_path=True)
        self.assert_rejected(self.replay('legacy'), b'Invalid selected file')
        for mode in ('utf8', 'patch'):
            with self.subTest(mode=mode):
                self.assert_pass(self.replay(mode))

    def test_invalid_utf8_is_not_accepted_by_repairs(self):
        for key in ('record', 'certificate', 'manifest'):
            self.fixture(malformed_at=key)
            # The legacy codec accepts 0xff as U+00ff, even with a valid byte hash.
            with self.subTest(mode='legacy', boundary=key):
                self.assert_pass(self.replay('legacy'))
            for mode in ('utf8', 'patch'):
                with self.subTest(mode=mode, boundary=key):
                    self.assert_rejected(self.replay(mode), b'UnicodeDecodeError')

    def test_source_corruption_still_rejected(self):
        proof = self.fixture(unicode_path=True)
        (self.root / proof).write_bytes(b'changed proof\n')
        for mode in ('utf8', 'patch'):
            with self.subTest(mode=mode):
                self.assert_rejected(self.replay(mode), b'Selected package inventory or bytes changed')

    def test_certificate_hash_still_checks_raw_bytes(self):
        self.fixture(unicode_at='certificate')
        with (self.root / 'certificate.json').open('ab') as stream:
            stream.write(b' ')
        for mode in ('utf8', 'patch'):
            with self.subTest(mode=mode):
                self.assert_rejected(self.replay(mode), b'Selected certificate bytes changed')

    @unittest.skipUnless(locale.getencoding().lower() == 'cp1252',
                         'native cp1252 host required; portable codec cases still run')
    def test_native_cp1252_cli_without_encoding_mock(self):
        for key in ('record', 'certificate', 'manifest'):
            self.fixture(unicode_at=key, unicode_path=True)
            with self.subTest(mode='legacy', boundary=key):
                self.assert_rejected(self.replay('legacy', native=True), b'UnicodeDecodeError')
            for mode in ('utf8', 'patch'):
                with self.subTest(mode=mode, boundary=key):
                    self.assert_pass(self.replay(mode, native=True))


def main():
    raw = source_bytes()
    expected_patch = ''.join(difflib.unified_diff(
        raw.decode('utf-8').splitlines(keepends=True),
        proposed_repair(raw).decode('utf-8').splitlines(keepends=True),
        fromfile='a/scripts/verify_selected_result.py',
        tofile='b/scripts/verify_selected_result.py')).encode('utf-8')
    if (HERE / 'UTF8-READS.patch').read_bytes() != expected_patch:
        raise ValueError('Review patch differs from the tested temporary repair')
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SelectedJsonLocaleReplay))
    if not result.wasSuccessful():
        return 1
    print('PASS_SELECTED_JSON_UTF8_REPLAY tests=%d native_cp1252=%s no_new_kappa'
          % (result.testsRun, locale.getencoding().lower() == 'cp1252'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
