"""Materialization commands must treat option-like directory names as paths."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import research_baseline_sparse as sparse
sys.path.pop(0)


class SparseOptionPathTests(unittest.TestCase):
    def test_cone_command_materializes_option_like_directory_without_changing_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ('--no-cone', '--stdin', '-q')
            for name in (*names, 'keep'):
                folder = root / name; folder.mkdir(); (folder / 'input.txt').write_text(name)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE, timeout=10)
            git('init', '-q'); git('add', '.')
            git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid',
                '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', 'commit', '-qm', 'fixture')
            for name in names:
                with self.subTest(name=name):
                    git('sparse-checkout', 'set', '--cone', 'keep')
                    self.assertFalse((root / name / 'input.txt').exists())
                    command = sparse.materialize_command([name + '/input.txt'])
                    self.assertEqual(command[:4], ['git', 'sparse-checkout', 'add', '--'])
                    git(*command[1:])
                    self.assertEqual((root / name / 'input.txt').read_text(), name)
                    self.assertEqual(git('config', '--bool', 'core.sparseCheckoutCone').strip(), b'true')
                    self.assertTrue(all(not (root / other / 'input.txt').exists() for other in names if other != name))

    def test_non_cone_patterns_and_empty_input_keep_argument_boundary(self):
        self.assertEqual(sparse.materialize_command(['--stdin/file'], cone=False),
                         ['git', 'sparse-checkout', 'add', '--', '/--stdin/'])
        self.assertEqual(sparse.materialize_command([], cone=True), ['git', 'sparse-checkout', 'add', '--'])


if __name__ == '__main__':
    unittest.main()
