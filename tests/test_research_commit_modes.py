"""Optional mode checks detect byte-identical scripts that cannot launch alike."""
import os
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_research_commit as checker
sys.path.pop(0)


@unittest.skipUnless(os.name == 'posix', 'POSIX execute bits required')
class CommitModeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name); self.package = 'research/fixture'
        path = self.root / self.package; path.mkdir(parents=True)
        (path / 'VERIFY.json').write_text('{"inputs":["input.sh"]}')
        self.script = self.root / 'input.sh'; self.script.write_text('#!/bin/sh\nexit 0\n')
        self.script.chmod(0o644)
        self.git('init', '-q'); self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, stderr=subprocess.PIPE)

    def test_default_remains_byte_only_but_opt_in_detects_added_execute_bit(self):
        self.script.chmod(0o755)
        self.git('config', 'core.filemode', 'false')
        self.assertEqual(self.git('diff', '--name-only'), b'')
        checker.check(self.root, self.package)
        with self.assertRaisesRegex(ValueError, 'executable mode differs: input.sh'):
            checker.check(self.root, self.package, check_modes=True)

    def test_committed_executable_missing_local_bit_is_rejected(self):
        self.git('update-index', '--chmod=+x', 'input.sh')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'mode')
        with self.assertRaisesRegex(ValueError, 'executable mode differs'):
            checker.check(self.root, self.package, check_modes=True)
        self.script.chmod(0o755)
        self.assertTrue(checker.check(self.root, self.package, check_modes=True)['executable_modes_checked'])

    def test_cli_enables_the_mode_check(self):
        self.script.chmod(0o755)
        args = ['check_research_commit.py', '--package', self.package, '--check-modes']
        error = io.StringIO()
        with patch.object(checker, 'ROOT', self.root), patch.object(sys, 'argv', args), \
             contextlib.redirect_stderr(error), self.assertRaises(SystemExit) as stopped:
            checker.main()
        self.assertEqual(stopped.exception.code, 1)
        self.assertIn('executable mode differs', error.getvalue())

    def test_unrelated_permission_bits_are_outside_git_mode_contract(self):
        self.script.chmod(0o640)
        self.assertTrue(checker.check(self.root, self.package, check_modes=True)['executable_modes_checked'])
        self.assertNotIn('executable_modes_checked', checker.check(self.root, self.package))


if __name__ == '__main__':
    unittest.main()
