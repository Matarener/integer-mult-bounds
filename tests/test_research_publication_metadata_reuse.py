"""Actual-publication controls for reusing authenticated source metadata."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_research_commit as checker
sys.path.pop(0)


class PublicationMetadataReuseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = 'research/fixture'
        self.path = self.root / self.package
        self.path.mkdir(parents=True)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.path / 'VERIFY.json').write_text('{"inputs":[]}\n', encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture base')
        self.base = self.git('rev-parse', 'HEAD').strip()
        self.publish({'base_commit': self.base, 'files': []})

    def git(self, *args):
        return subprocess.run(
            ['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', *args],
            cwd=self.root, capture_output=True, text=True, check=True, timeout=30).stdout

    def publish(self, sources):
        raw = json.dumps(sources).encode('utf-8')
        (self.path / 'SOURCES.json').write_bytes(raw)
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture publication')
        return self.git('rev-parse', 'HEAD').strip()

    def check(self, ref='HEAD', history=True):
        return checker.check(self.root, self.package, ref, check_source_history=history)

    def test_complete_check_avoids_metadata_refetch_and_preserves_receipt(self):
        head = self.git('rev-parse', 'HEAD').strip()
        expected = checker.source_history(self.root, self.package, head)
        with patch.object(checker, 'publication_sources', side_effect=AssertionError('refetch')):
            result = self.check()
        self.assertEqual(result, {'commit': head, 'files': 2, 'package': self.package,
                                  'source_history_commits': expected})

    def test_standalone_reader_keeps_its_original_boundary(self):
        head = self.git('rev-parse', 'HEAD').strip()
        with patch.object(checker, 'history_git', wraps=checker.history_git) as calls:
            self.assertEqual(checker.source_history(self.root, self.package, head), [self.base])
        self.assertEqual([c.args[1:3] for c in calls.call_args_list[:2]],
                         [('cat-file', '-s'), ('cat-file', 'blob')])
        with patch.object(checker, 'history_git', wraps=checker.history_git) as calls:
            self.check()
        self.assertTrue(calls.call_args_list)
        self.assertNotIn('cat-file', [c.args[1] for c in calls.call_args_list])

    def test_working_drift_is_rejected_before_metadata_parsing(self):
        (self.path / 'SOURCES.json').write_bytes(b'{invalid')
        with self.assertRaisesRegex(ValueError, 'bytes differ.*SOURCES.json'):
            self.check()

    def test_malformed_committed_json_is_only_parsed_when_requested(self):
        (self.path / 'SOURCES.json').write_bytes(b'{invalid')
        self.git('add', '.')
        self.git('commit', '-qm', 'malformed fixture')
        self.assertEqual(self.check(history=False)['files'], 2)
        with self.assertRaises(json.JSONDecodeError):
            self.check()

    def test_reader_final_failure_precedes_parsing_of_captured_metadata(self):
        self.publish(None)
        original = checker.git_blobs

        def fail_after_payloads(root, specs):
            yield from original(root, specs)
            raise ValueError('final blob-reader failure')

        with patch.object(checker, 'git_blobs', side_effect=fail_after_payloads):
            with self.assertRaisesRegex(ValueError, '^final blob-reader failure$'):
                self.check()

    def test_retained_metadata_is_committed_not_a_later_working_read(self):
        original = checker.git_blobs
        sources = self.path / 'SOURCES.json'
        before = sources.read_bytes()

        def change_after_comparison(root, specs):
            yield from original(root, specs)
            sources.write_text('{"base_commit":"' + '1' * 40 + '","files":[]}',
                               encoding='utf-8')

        try:
            with patch.object(checker, 'git_blobs', side_effect=change_after_comparison):
                self.assertEqual(self.check()['source_history_commits'], [self.base])
        finally:
            sources.write_bytes(before)
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_exact_metadata_size_limit_and_final_reader_completion(self):
        size = (self.path / 'SOURCES.json').stat().st_size
        with patch.object(checker, 'MAX_SOURCE_METADATA_BYTES', size):
            self.assertEqual(self.check()['source_history_commits'], [self.base])
        original = checker.git_blobs
        completed = []

        def mark_completion(root, specs):
            yield from original(root, specs)
            completed.append(True)

        with patch.object(checker, 'git_blobs', side_effect=mark_completion):
            with patch.object(checker, 'MAX_SOURCE_METADATA_BYTES', size - 1):
                with self.assertRaisesRegex(ValueError, 'source metadata byte limit'):
                    self.check()
        self.assertEqual(completed, [True])

    def test_no_cross_call_cache_and_explicit_older_publication(self):
        old = self.git('rev-parse', 'HEAD').strip()
        raw = (self.path / 'SOURCES.json').read_bytes()
        self.check()
        self.publish({'base_commit': '1' * 40, 'files': []})
        with self.assertRaisesRegex(ValueError, 'unavailable source commit'):
            self.check()
        (self.path / 'SOURCES.json').write_bytes(raw)
        self.assertEqual(self.check(old)['source_history_commits'], [self.base])
        with self.assertRaisesRegex(ValueError, 'bytes differ.*SOURCES.json'):
            self.check()


if __name__ == '__main__':
    unittest.main()
