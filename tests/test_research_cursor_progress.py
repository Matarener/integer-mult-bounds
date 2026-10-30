"""Incomplete GraphQL pages must terminate without replacing cached evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


def page(nodes=(), cursor=None, more=False):
    return {'nodes': list(nodes), 'pageInfo': {'hasNextPage': more, 'endCursor': cursor}}


def stalled(level, cursor):
    bad = page(cursor=cursor, more=True)
    comment = {'id': 'C', 'body': 'claim', 'url': 'https://example.invalid/C',
               'updatedAt': '2026-10-26T00:00:00Z', 'replies': bad if level == 'replies' else page()}
    comments = page([comment], cursor, level == 'comments')
    discussion = {'id': 'D', 'number': 1, 'title': 'claim', 'body': 'claim',
                  'url': 'https://example.invalid/D', 'updatedAt': comment['updatedAt'], 'comments': comments}
    calls = []
    def api(query, variables):
        calls.append(variables)
        if len(calls) > 4:
            raise AssertionError('unbounded pagination')
        if level == 'pullRequests':
            return {'repository': {'pullRequests': bad}}
        if 'id' not in variables:
            return {'repository': {'discussions': page([discussion], cursor, level == 'discussions')}}
        return {'node': {'comments': comments, 'replies': bad}}
    return api, calls


class CursorProgressTests(unittest.TestCase):
    def test_each_connection_rejects_missing_and_repeated_cursors(self):
        for level in ('pullRequests', 'discussions', 'comments', 'replies'):
            for cursor in (None, '', 'same', 42):
                with self.subTest(level=level, cursor=cursor):
                    api, calls = stalled(level, cursor)
                    with patch.object(overlap, 'graphql', side_effect=api):
                        with self.assertRaisesRegex(ValueError, 'pagination did not advance'):
                            (overlap.fetch_pr_files if level == 'pullRequests' else overlap.fetch_discussions)()
                    self.assertEqual(len(calls), 2 if cursor == 'same' else 1)

    def test_non_adjacent_cursor_cycle_is_rejected(self):
        pages = [page(cursor=c, more=True) for c in ('a', 'b', 'a')]
        with patch.object(overlap, 'graphql', side_effect=[{'repository': {'pullRequests': p}} for p in pages]) as api:
            with self.assertRaisesRegex(ValueError, 'pagination did not advance'):
                overlap.fetch_pr_files()
        self.assertEqual(api.call_count, 3)

    def test_stalled_refresh_keeps_previous_complete_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            old = {'fetched_at': overlap.now(), 'complete_pagination': True, 'records': []}
            cache.write_text(json.dumps({'schema_version': 1, 'repository': overlap.REPO,
                                         'sources': {'discussions': old}}))
            api, _ = stalled('replies', 'same')
            with patch.object(overlap, 'graphql', side_effect=api), patch.object(overlap, 'gh_json', return_value=[[]]):
                result, warnings = overlap.remote_snapshot(cache, refresh=True)
            self.assertEqual(result['sources']['discussions'], old)
            self.assertEqual(json.loads(cache.read_text())['sources']['discussions'], old)
            self.assertTrue(any('pagination did not advance' in w for w in warnings))


if __name__ == '__main__':
    unittest.main()
