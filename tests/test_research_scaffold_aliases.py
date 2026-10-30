"""The draft generator must not publish through a linked output directory."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import new_research_package as scaffold
sys.path.pop(0)


class ScaffoldAliasTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.root = self.base / 'repo'; self.root.mkdir()
        self.outside = self.base / 'outside'; self.outside.mkdir()
        (self.outside / 'keep.txt').write_text('keep this file')

    def link(self, path, target):
        try:path.symlink_to(target, target_is_directory=True)
        except OSError as exc:self.skipTest('symlinks unavailable: ' + str(exc))

    def test_linked_research_directory_is_rejected_before_git_or_writes(self):
        self.link(self.root / 'research', self.outside)
        with patch.object(scaffold, 'git', side_effect=AssertionError('Git must not run')):
            with self.assertRaisesRegex(ValueError, 'symlink in repository-relative path'):
                scaffold.create(self.root, 'new-result', 'task', 'author')
        self.assertEqual([p.name for p in self.outside.iterdir()], ['keep.txt'])
        self.assertEqual((self.outside / 'keep.txt').read_text(), 'keep this file')

    def test_dangling_package_alias_is_rejected_before_staging(self):
        (self.root / 'research').mkdir()
        destination = self.root / 'research/new-result'
        target = self.outside / 'missing'; self.link(destination, target)
        with patch.object(scaffold, 'git', side_effect=AssertionError('Git must not run')):
            with self.assertRaisesRegex(ValueError, 'symlink in repository-relative path'):
                scaffold.create(self.root, 'new-result', 'task', 'author')
        self.assertTrue(destination.is_symlink()); self.assertFalse(target.exists())
        self.assertEqual(len(list(destination.parent.iterdir())), 1)

    def test_ordinary_new_output_and_linked_checkout_root_reach_normal_validation(self):
        alias = self.base / 'checkout'; self.link(alias, self.root)
        for root in (self.root, alias):
            with self.subTest(root=root), patch.object(scaffold, 'git', side_effect=RuntimeError('normal source validation')):
                with self.assertRaisesRegex(RuntimeError, 'normal source validation'):
                    scaffold.create(root, 'new-result', 'task', 'author')
        self.assertFalse((self.root / 'research').exists())


if __name__ == '__main__':
    unittest.main()
