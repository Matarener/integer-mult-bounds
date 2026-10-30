"""Git path queries keep case and spaces on every host."""
import contextlib
import io
import json
import ntpath
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


class PathQueryTests(unittest.TestCase):
    def test_globs_remain_case_sensitive_under_windows_normalization(self):
        rows = [{'number': 1, 'paths': ['research/A/check.py', 'research/a/check.py']}]
        with patch.object(overlap.fnmatch.os.path, 'normcase', side_effect=ntpath.normcase):
            match = overlap.path_report([], rows, ['research/A/*.py'])[0]
        self.assertEqual(match['matched_paths'], ['research/A/check.py'])

    def run_cli(self, patterns, paths):
        pull = {'kind': 'pr', 'number': 1, 'title': 'scope', 'body': '', 'url': 'https://example.invalid/1',
                'head': 'a'*40, 'base': 'b'*40, 'updated_at': '2026-10-26T00:00:00Z', 'state': 'open'}
        files = {'number': 1, 'paths': paths, 'head': pull['head'], 'base': pull['base']}
        snapshot = {'sources': {name: {'fetched_at': overlap.now(), 'complete_pagination': True, 'records': rows}
                    for name, rows in [('open_prs', [pull]), ('pr_files', [files]), ('discussions', [])]}}
        args = ['find_overlap.py', '--json']
        for pattern in patterns:args += ['--path', pattern]
        output = io.StringIO()
        with patch.object(sys, 'argv', args), patch.object(overlap, 'local_records', return_value=[]), \
             patch.object(overlap, 'local_coverage', return_value=({}, [])), \
             patch.object(overlap, 'remote_snapshot', return_value=(snapshot, [])), contextlib.redirect_stdout(output):
            overlap.main()
        return json.loads(output.getvalue())

    def test_space_only_pattern_searches_space_containing_names(self):
        report = self.run_cli([' '], ['a b.py', 'ab.py'])
        self.assertEqual(report['path_matches_total'], 1)
        self.assertEqual(report['path_matches'][0]['matched_paths'], ['a b.py'])

    def test_leading_and_trailing_pattern_spaces_are_preserved(self):
        for pattern, expected in [(' leading', 'x/ leading.py'), ('trailing ', 'x/trailing .py')]:
            with self.subTest(pattern=pattern):
                report = self.run_cli([pattern], ['x/ leading.py', 'x/leading.py', 'x/trailing .py', 'x/trailing.py'])
                self.assertEqual(report['path_matches'][0]['matched_paths'], [expected])

    def test_empty_pattern_fails_before_local_or_remote_search(self):
        args = ['find_overlap.py', '--path', '']
        with patch.object(sys, 'argv', args), patch.object(overlap, 'remote_snapshot') as remote, \
             patch.object(overlap, 'local_records') as local, contextlib.redirect_stderr(io.StringIO()), \
             self.assertRaises(SystemExit) as stopped:
            overlap.main()
        self.assertEqual(stopped.exception.code, 2); remote.assert_not_called(); local.assert_not_called()

    def test_literal_substrings_and_multiple_patterns_still_work(self):
        report = self.run_cli(['with space', 'research/*/check.py'], ['x/with space.txt', 'research/a/check.py', 'other'])
        self.assertEqual(report['path_matches'][0]['matched_paths'], ['x/with space.txt', 'research/a/check.py'])


if __name__ == '__main__':
    unittest.main()
