"""Known file-inventory gaps must survive filtering and result limits."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/find_overlap.py'


class InventoryCoverageTests(unittest.TestCase):
    def run_cli(self, inventories, *arguments):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / 'overlap.json'
            bodies = [dict(kind='pr', number=row['number'], title='needle', body='',
                           head=row['head'], base=row['base'], state='open',
                           url=f"https://example.invalid/{row['number']}",
                           updated_at='2026-10-18T00:00:00Z') for row in inventories]
            fetched_at = datetime.now(timezone.utc).isoformat()
            sources = {name: dict(fetched_at=fetched_at, complete_pagination=True, records=rows)
                       for name, rows in [('open_prs', bodies), ('discussions', []),
                                          ('pr_files', inventories)]}
            original = json.dumps(dict(schema_version=1, repository='CrocSwap/integer-mult-bounds',
                                       sources=sources)).encode('utf-8')
            cache.write_bytes(original)
            # A fresh synthetic snapshot must not require gh or any network call.
            result = subprocess.run([sys.executable, '-B', str(SCRIPT), '--cache', str(cache),
                                     '--max-age', '3600', *arguments], capture_output=True,
                                    encoding='utf-8', timeout=30, env={**os.environ, 'PATH': ''})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(cache.read_bytes(), original)
            return result.stdout

    @staticmethod
    def row(number, paths, truncated):
        return dict(number=number, head='a' * 40, base='b' * 40,
                    paths=paths, truncated=truncated)

    def test_unavailable_and_short_inventories_warn_even_without_a_hit(self):
        rows = [self.row(376, [], True), self.row(377, ['elsewhere.py'], True)]
        for options in ([], ['--offline']):
            with self.subTest(options=options):
                report = json.loads(self.run_cli(rows, '--path', 'missing.py', '--json', *options))
                coverage = report['coverage']['pr_files']
                self.assertTrue(coverage['complete_pagination'])
                self.assertEqual(coverage['truncated_prs'], [376, 377])
                self.assertEqual(coverage['unverified_heads'], [])
                self.assertEqual(coverage['unverified_bases'], [])
                self.assertEqual(report['path_matches_total'], 0)
                self.assertTrue(any('incomplete file inventories for 2 PRs' in warning
                                    for warning in report['warnings']))

    def test_result_limit_does_not_hide_incomplete_inventories(self):
        rows = [self.row(98, ['elsewhere.py'], True), self.row(99, [], True),
                self.row(100, ['target.py'], True), self.row(101, ['target.py'], False),
                self.row(99, [], True)]
        report = json.loads(self.run_cli(rows, '--path', 'target.py', '--limit', '1', '--json'))
        self.assertEqual(report['path_matches_total'], 2)
        self.assertEqual([row['number'] for row in report['path_matches']], [101])
        self.assertFalse(report['path_matches'][0]['truncated'])
        self.assertEqual(report['coverage']['pr_files']['truncated_prs'], [98, 99, 100])
        self.assertTrue(any('incomplete file inventories for 3 PRs' in warning
                            for warning in report['warnings']))

    def test_combined_term_and_path_matches_preserve_truncation(self):
        rows = [self.row(100, ['target.py'], True), self.row(101, ['target.py'], False)]
        report = json.loads(self.run_cli(rows, 'needle', '--path', 'target.py', '--json'))
        self.assertEqual({row['number']: row['truncated'] for row in report['matches']},
                         {100: True, 101: False})

    def test_text_report_surfaces_unmatched_gaps_and_combined_match_flags(self):
        rows = [self.row(376, [], True)]
        output = self.run_cli(rows, '--path', 'missing.py')
        self.assertIn('"truncated_prs": [376]', output)
        self.assertIn('WARNING: pr_files: incomplete file inventories for 1 PRs', output)
        output = self.run_cli([self.row(100, ['target.py'], True)], 'needle', '--path', 'target.py')
        self.assertIn('[pr] needle (file list truncated)', output)

    def test_complete_empty_inventory_is_not_reported_as_a_gap(self):
        report = json.loads(self.run_cli([self.row(376, [], False)], '--path', 'missing.py', '--json'))
        self.assertEqual(report['coverage']['pr_files']['truncated_prs'], [])
        # PATH is empty in this CLI fixture, so Git inventory is unavailable.
        self.assertIsNone(report['coverage']['local']['complete_head_inventory'])
        self.assertEqual(len(report['warnings']), 1)
        self.assertTrue(report['warnings'][0].startswith('local: HEAD note inventory unavailable;'))
        self.assertEqual(report['path_matches_total'], 0)


if __name__ == '__main__':
    unittest.main()
