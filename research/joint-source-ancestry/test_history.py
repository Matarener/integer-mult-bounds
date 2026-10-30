"""The original source-history contract exercised through the opt-in adapter."""
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
import test_research_source_history as inherited
import preflight as checker

# The inherited fixture methods resolve this module variable at call time.
# The original test/source files remain untouched, including their CLI controls.
inherited.checker = checker


class JointSourceHistoryTests(inherited.SourceHistoryTests):
    def test_real_cli_is_read_only_and_reports_no_pass_on_history_failure(self):
        super().test_real_cli_is_read_only_and_reports_no_pass_on_history_failure()
        code = ('import sys; from pathlib import Path; '
                f'sys.path.insert(0, {str(Path(__file__).resolve().parent)!r}); '
                f'import preflight; preflight.ROOT = Path({str(self.root)!r}); '
                'preflight.main()')
        command = [sys.executable, '-W', 'error', '-B']
        if sys.flags.optimize:
            command.append('-O')
        command += ['-c', code, '--package', self.package, '--check-source-history']
        before = self.git('rev-parse', 'HEAD'), self.git('ls-files', '--stage', '-z')
        bad = subprocess.run(command, cwd=self.root, capture_output=True, timeout=30)
        self.assertEqual(bad.returncode, 1, bad.stderr)
        self.assertIn(b'not an ancestor', bad.stderr)
        self.assertNotIn(b'PASS_', bad.stdout)
        self.assertEqual(before, (self.git('rev-parse', 'HEAD'),
                                  self.git('ls-files', '--stage', '-z')))
        self.publish([self.row()])
        good = subprocess.run(command, cwd=self.root, capture_output=True, timeout=30)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn(b'PASS_RESEARCH_COMMIT_BYTES', good.stdout)

    def test_joint_walk_accepts_merged_incomparable_sources(self):
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        left = self.git('commit-tree', tree, '-p', self.base, data='left\n').strip()
        right = self.git('commit-tree', tree, '-p', self.base, data='right\n').strip()
        head = self.publish([self.row(left), self.row(right), self.row(left)])
        tree = self.git('rev-parse', head + '^{tree}').strip()
        merged = self.git('commit-tree', tree, '-p', head, '-p', left, '-p', right,
                          data='merged sources\n').strip()
        with patch.object(checker, 'history_git', wraps=checker.history_git) as calls:
            result = self.check(ref=merged)
        self.assertEqual(result['source_history_commits'], sorted([self.base, left, right]))
        commands = [call.args[1] for call in calls.call_args_list]
        self.assertEqual(commands.count('rev-list'), 1)
        self.assertNotIn('merge-base', commands)
        self.assertNotIn('rev-parse', commands[3:])
        self.assertEqual(len(commands), 5)

    def test_joint_walk_preserves_first_foreign_pin_diagnostic(self):
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        foreign = [self.git('commit-tree', tree, '-p', self.base,
                            data=f'foreign {index}\n').strip() for index in range(3)]
        self.publish([self.row(pin) for pin in foreign])
        with self.assertRaisesRegex(ValueError, 'not an ancestor.*' + min(foreign)):
            self.check()

    def test_joint_type_fallback_preserves_earlier_ancestry_error(self):
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        foreign = self.git('commit-tree', tree, '-p', self.base, data='foreign\n').strip()
        self.publish([self.row(foreign), self.row('f' * 40)])
        with self.assertRaisesRegex(ValueError, 'not an ancestor.*' + foreign):
            self.check()

    def test_joint_batch_rejects_tags_trees_blobs_and_missing_objects(self):
        tree = self.git('rev-parse', self.base + '^{tree}').strip()
        blob = self.git('rev-parse', self.base + ':research/fixture/input.txt').strip()
        tag = self.git('mktag', data=f'object {self.base}\ntype commit\ntag source\n'
                       'tagger Fixture <fixture@example.invalid> 1 +0000\n\ntag\n').strip()
        for pin in (tag, tree, blob, '1' * 40):
            with self.subTest(pin=pin):
                self.publish([self.row(pin)])
                with self.assertRaisesRegex(ValueError, 'unavailable source commit.*' + pin):
                    self.check()

    def test_joint_git_failures_and_malformed_responses_fail_closed(self):
        self.git('commit', '-qm', 'second source', '--allow-empty')
        second = self.git('rev-parse', 'HEAD').strip()
        self.publish([self.row(second)])
        original = checker.history_git
        for phase, code, output in (
                ('batch', 128, b''), ('batch', 0, b''),
                ('batch', 0, b'forged commit\n' * 2),
                ('walk', 128, b''), ('walk', 0, b'not a commit\n')):
            def broken(root, *args, input=None):
                selected = (args[0] == 'rev-list' if phase == 'walk'
                            else args[0] == 'cat-file' and args[1].startswith('--batch-check'))
                if selected:
                    return subprocess.CompletedProcess(args, code, output, b'fatal: injected failure')
                return original(root, *args, input=input)

            with self.subTest(phase=phase, code=code, output=output):
                with patch.object(checker, 'history_git', side_effect=broken):
                    with self.assertRaises(ValueError):
                        self.check()

        def timeout(root, *args, input=None):
            if args[0] == 'rev-list':
                raise subprocess.TimeoutExpired('git rev-list', 30)
            return original(root, *args, input=input)

        with patch.object(checker, 'history_git', side_effect=timeout):
            with self.assertRaises(subprocess.TimeoutExpired):
                self.check()



if __name__ == '__main__':
    unittest.main()
