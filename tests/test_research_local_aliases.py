"""Local overlap records must come from regular files under the checkout."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import find_overlap as overlap
sys.path.pop(0)


class LocalAliasTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.package = self.root / 'research/kept'
        self.package.mkdir(parents=True)
        (self.package / 'README.md').write_text('real local evidence')
        self.outside = self.base / 'outside'
        self.outside.mkdir()
        (self.outside / 'README.md').write_text('external evidence')

    def link(self, link, target):
        try:
            link.symlink_to(target, target_is_directory=target.is_dir())
        except OSError as exc:
            self.skipTest('symlinks unavailable: ' + str(exc))

    def test_parent_and_leaf_aliases_are_not_local_records(self):
        self.link(self.root / 'research/alias', self.outside)
        self.link(self.package / 'TASK.json', self.outside / 'README.md')
        rows = overlap.local_records(self.root)
        self.assertEqual([r['path'] for r in rows], ['research/kept/README.md'])
        self.assertEqual(rows[0]['body'], 'real local evidence')

    def test_internal_alias_and_directory_note_are_not_counted_twice(self):
        self.link(self.root / 'research/alias', self.package)
        (self.package / 'TASK.json').mkdir()
        self.assertEqual(len(overlap.local_records(self.root)), 1)

    def test_checkout_root_alias_is_allowed_but_ledger_parent_alias_is_not(self):
        (self.outside / 'pr-ledger.md').write_text('external ledger')
        (self.root / 'docs').mkdir()
        self.link(self.root / 'docs/research', self.outside)
        alias = self.base / 'checkout'
        self.link(alias, self.root)
        self.assertEqual([r['path'] for r in overlap.local_records(alias)], ['research/kept/README.md'])

    def test_replaced_tracked_parent_leaves_an_explicit_coverage_gap(self):
        def git(*args):
            subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)
        git('init', '-q')
        git('add', '.')
        git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')
        moved = self.base / 'moved'
        self.package.rename(moved)
        self.link(self.package, moved)
        rows = overlap.local_records(self.root)
        coverage, warnings = overlap.local_coverage(self.root, rows)
        self.assertEqual(rows, [])
        self.assertFalse(coverage['complete_head_inventory'])
        self.assertEqual(coverage['unsearched_head_paths'], ['research/kept/README.md'])
        self.assertTrue(any('not searched' in warning for warning in warnings))


if __name__ == '__main__':
    unittest.main()
