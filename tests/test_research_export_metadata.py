"""Archive receipts must have unambiguous keys and exact integer fields."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import export_research_package as exporter
sys.path.pop(0)


class ReceiptMetadataTests(unittest.TestCase):
    def receipt(self):
        return {'format': exporter.FORMAT, 'commit': 'a' * 40, 'package': 'research/fixture',
                'files': [{'path': 'research/fixture/VERIFY.json', 'mode': 0o644,
                           'size': 0, 'sha256': hashlib.sha256(b'').hexdigest()}]}

    def check(self, receipt, raw=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'bundle.tar'
            with tarfile.open(path, 'w') as archive:
                archive.addfile(*exporter.member('research/fixture/VERIFY.json', b''))
                archive.addfile(*exporter.member(exporter.RECEIPT,
                                raw if raw is not None else json.dumps(receipt).encode()))
            return exporter.check_bundle(path)

    def test_invalid_committed_manifest_fails_before_tree_inventory(self):
        for raw, message in ((b'[]', 'VERIFY.json must be an object'),
                             (b'{"inputs":[],"inputs":[]}', 'duplicate export JSON key')):
            rows = (row for row in [('b' * 40, raw)])
            with patch.object(exporter, 'git', return_value=b'a' * 40) as git, \
                 patch.object(exporter, 'git_blobs', return_value=rows):
                with self.assertRaisesRegex(ValueError, message):
                    exporter.inventory(Path('.'), 'research/fixture', 'HEAD')
            self.assertEqual(git.call_count, 1)

    def test_boolean_and_float_sizes_are_not_integer_receipts(self):
        for bad in (False, 0.0, '0', -1, None):
            with self.subTest(size=bad):
                receipt = self.receipt(); receipt['files'][0]['size'] = bad
                with self.assertRaisesRegex(ValueError, 'invalid receipt size'):
                    self.check(receipt)

    def test_float_mode_is_not_an_integer_mode(self):
        receipt = self.receipt(); receipt['files'][0]['mode'] = float(0o644)
        with self.assertRaisesRegex(ValueError, 'invalid receipt mode'):
            self.check(receipt)

    def test_only_actual_git_object_id_lengths_are_accepted(self):
        for length in (39, 41, 48, 63, 65):
            receipt = self.receipt(); receipt['commit'] = 'a' * length
            with self.subTest(length=length), self.assertRaisesRegex(ValueError, 'invalid commit label'):
                self.check(receipt)
        for length in (40, 64):
            receipt = self.receipt(); receipt['commit'] = 'a' * length
            self.assertEqual(self.check(receipt), receipt)

    def test_duplicate_top_level_and_nested_keys_are_rejected(self):
        receipt = self.receipt(); raw = json.dumps(receipt)
        variants = [raw[:-1] + ',"commit":"' + 'b' * 40 + '"}',
                    raw.replace('"size": 0', '"size": 99, "size": 0')]
        for text in variants:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'duplicate export JSON key'):
                self.check(receipt, text.encode())


if __name__ == '__main__':
    unittest.main()
