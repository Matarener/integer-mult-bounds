"""Malformed cache sections must not hide missing overlap coverage."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


def source():
    return {'fetched_at': overlap.now(), 'records': [], 'complete_pagination': True}


class CacheShapeTests(unittest.TestCase):
    def read(self, value, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            raw = json.dumps(value)
            cache.write_text(raw, encoding='utf-8')
            with patch.object(overlap, 'gh_json', side_effect=AssertionError('network')):
                result = overlap.remote_snapshot(cache, offline=True, **kwargs)
            self.assertEqual(cache.read_text(encoding='utf-8'), raw)
            return result

    def test_bad_root_is_unknown_coverage_and_does_not_rewrite_cache(self):
        for value in (None, [], 42, 'text', {'schema_version': 1, 'repository': overlap.REPO, 'sources': []}):
            with self.subTest(value=value):
                snapshot, warnings = self.read(value)
                self.assertEqual(snapshot['sources'], {})
                self.assertTrue(any('unusable snapshot' in w for w in warnings))
                self.assertEqual(sum('no usable remote snapshot' in w for w in warnings), 2)

    def test_bad_source_keeps_other_usable_evidence(self):
        bad = [None, [], {}, dict(source(), records={}), dict(source(), records=[None]),
               dict(source(), records=[{'number': 1, 'title': []}]),
               dict(source(), fetched_at='2026-10-26'), dict(source(), complete_pagination='true')]
        for value in bad:
            with self.subTest(value=value):
                good = source()
                snapshot, warnings = self.read({'schema_version': 1, 'repository': overlap.REPO,
                                               'sources': {'open_prs': value, 'discussions': good}})
                self.assertEqual(snapshot['sources'], {'discussions': good})
                self.assertTrue(any('open_prs: no usable' in w for w in warnings))

    def test_invalid_path_records_are_not_searched(self):
        value = {'schema_version': 1, 'repository': overlap.REPO,
                 'sources': {'pr_files': dict(source(), records=[{'number': 1, 'paths': [None]}])}}
        snapshot, warnings = self.read(value, need_files=True)
        self.assertNotIn('pr_files', snapshot['sources'])
        self.assertTrue(any('pr_files: unusable cached source' in w for w in warnings))

    def test_legacy_optional_text_fields_remain_optional(self):
        good = dict(source(), records=[{'kind': 'pr', 'number': 1, 'title': 'prior claim'}])
        snapshot, warnings = self.read({'schema_version': 1, 'repository': overlap.REPO,
                                       'sources': {'open_prs': good, 'discussions': source()}})
        self.assertEqual(snapshot['sources']['open_prs'], good)
        self.assertFalse(any('unusable' in w for w in warnings))

    def test_online_refresh_replaces_invalid_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            cache.write_text('[]', encoding='utf-8')
            with patch.object(overlap, 'gh_json', return_value=[[]]), patch.object(overlap, 'fetch_discussions', return_value=[]):
                snapshot, warnings = overlap.remote_snapshot(cache)
            self.assertEqual(set(snapshot['sources']), {'open_prs', 'discussions'})
            self.assertEqual(json.loads(cache.read_text()), snapshot)
            self.assertTrue(all(s['complete_pagination'] for s in snapshot['sources'].values()))
            self.assertTrue(any('unusable snapshot' in w for w in warnings))


if __name__ == '__main__':
    unittest.main()
