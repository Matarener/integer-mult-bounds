"""Failed cache writes preserve the prior evidence and remove partial files."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


class CachePublicationTests(unittest.TestCase):
    def test_partial_serialization_and_write_failures_remove_temporary_files(self):
        for failure in (TypeError('bad value'), OSError('disk full')):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'cache.json'; path.write_bytes(b'old evidence\n')
                streams = []
                def fail(data, stream):
                    streams.append(stream); stream.write('{"partial":'); raise failure
                with patch.object(overlap.json, 'dump', side_effect=fail):
                    with self.assertRaises(type(failure)):overlap.atomic_json(path, {'new': True})
                self.assertEqual(path.read_bytes(), b'old evidence\n')
                self.assertEqual(list(Path(tmp).iterdir()), [path])
                self.assertTrue(streams[0].closed)

    def test_replace_failure_preserves_destination_and_cleans_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cache.json'; path.write_bytes(b'old')
            with patch.object(overlap.os, 'replace', side_effect=OSError('replace failed')):
                with self.assertRaisesRegex(OSError, 'replace failed'):overlap.atomic_json(path, {'new': 1})
            self.assertEqual(path.read_bytes(), b'old'); self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_success_publishes_one_complete_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nested/cache.json'
            overlap.atomic_json(path, {'evidence': ['κ', 1]})
            self.assertEqual(json.loads(path.read_text()), {'evidence': ['κ', 1]})
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_failed_persistence_keeps_old_source_in_memory_and_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            old = {'schema_version': 1, 'repository': overlap.REPO, 'sources': {
                name: {'fetched_at': overlap.now(), 'records': [], 'complete_pagination': True}
                for name in ('open_prs', 'discussions')}}
            raw = json.dumps(old); cache.write_text(raw)
            with patch.object(overlap, 'gh_json', return_value=[[]]), \
                 patch.object(overlap, 'pull_records', return_value=[{'number': 99}]), \
                 patch.object(overlap, 'fetch_discussions', return_value=[]), \
                 patch.object(overlap, 'atomic_json', side_effect=OSError('disk full')):
                result, warnings = overlap.remote_snapshot(cache, refresh=True)
            self.assertEqual(result, old); self.assertEqual(cache.read_text(), raw)
            self.assertEqual(sum('refresh failed' in w for w in warnings), 2)

    def test_first_write_failure_does_not_claim_a_saved_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            with patch.object(overlap, 'gh_json', return_value=[[]]), \
                 patch.object(overlap, 'fetch_discussions', return_value=[]), \
                 patch.object(overlap, 'atomic_json', side_effect=OSError('disk full')):
                result, warnings = overlap.remote_snapshot(cache)
            self.assertEqual(result['sources'], {}); self.assertFalse(cache.exists())
            self.assertEqual(sum('no usable remote snapshot' in w for w in warnings), 2)


if __name__ == '__main__':
    unittest.main()
