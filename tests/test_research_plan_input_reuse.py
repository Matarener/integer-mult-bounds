"""Shared inputs retain every consumer and are revalidated on each plan.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('input_reuse_runner', ROOT / 'scripts/research_package.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class PlanInputReuseTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write('inputs/shared.txt', 'shared')
        self.write('inputs/other.txt', 'other')
        self.manifests = {}
        for name in ('alpha', 'beta'):
            raw = json.dumps({'inputs': ['inputs/shared.txt', 'inputs/shared.txt',
                                         'inputs/other.txt']})
            self.write('research/' + name + '/VERIFY.json', raw)
            self.manifests[name] = raw.encode()
        self.git('init', '-q')
        self.commit()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True,
                              capture_output=True, timeout=15).stdout

    def commit(self):
        self.git('add', '--all')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'core.autocrlf=false', 'commit', '-qm', 'fixture')

    def test_each_shared_input_is_checked_once_without_losing_consumers_or_causes(self):
        changed = ['inputs/shared.txt', 'research/alpha/check.py', 'scripts/research_package.py']
        with patch.object(runner, 'symlink_free_relative_path',
                          wraps=runner.symlink_free_relative_path) as filesystem, \
                patch.object(runner, 'require_tracked_input', wraps=runner.require_tracked_input) as tracked:
            result = runner.plan_details(self.root, changed)
        for name in ('inputs/shared.txt', 'inputs/other.txt'):
            self.assertEqual(sum(call.args[1] == name for call in filesystem.call_args_list), 1)
            self.assertEqual(sum(call.args[0] == name for call in tracked.call_args_list), 1)
        self.assertEqual(result, [
            {'package': 'research/' + name,
             'causes': {'declared_inputs': ['inputs/shared.txt'],
                        'package_files': ['research/alpha/check.py'] if name == 'alpha' else [],
                        'shared_controls': ['scripts/research_package.py']},
             'manifest_sha256': hashlib.sha256(raw).hexdigest()}
            for name, raw in self.manifests.items()])

    def test_next_plan_rechecks_filesystem_and_propagates_lookup_failures(self):
        runner.plan_details(self.root, [])
        original = Path.lstat
        shared = self.root / 'inputs/shared.txt'

        def denied(path, *args, **kwargs):
            if path == shared:
                raise PermissionError('shared input lookup denied')
            return original(path, *args, **kwargs)

        with patch.object(Path, 'lstat', denied):
            with self.assertRaisesRegex(PermissionError, 'shared input lookup denied'):
                runner.plan_details(self.root, [])

    def test_next_plan_rejects_a_new_symlink_alias(self):
        runner.plan_details(self.root, [])
        shared = self.root / 'inputs/shared.txt'
        shared.unlink()
        try:
            shared.symlink_to('other.txt')
        except OSError as error:
            self.skipTest('symlink creation unavailable: ' + str(error))
        with self.assertRaisesRegex(ValueError, 'symlink in repository-relative path'):
            runner.plan_details(self.root, ['inputs/other.txt'])

    def test_next_plan_reloads_head_and_does_not_remember_deleted_diff_paths(self):
        runner.plan_details(self.root, [])
        (self.root / 'inputs/shared.txt').unlink()
        self.commit()
        rows = runner.plan_details(self.root, ['inputs/shared.txt'])
        self.assertEqual([row['package'] for row in rows], ['research/alpha', 'research/beta'])
        for row in rows:
            self.assertEqual(row['causes']['declared_inputs'], ['inputs/shared.txt'])
        with self.assertRaisesRegex(ValueError, 'exact Git-tracked input path'):
            runner.plan_details(self.root, [])

    def test_next_plan_reloads_manifest_and_preserves_exact_spelling(self):
        runner.plan_details(self.root, ['inputs/shared.txt'])
        for name in ('inputs/SHARED.txt', './inputs/shared.txt'):
            self.write('research/beta/VERIFY.json', json.dumps({'inputs': [name]}))
            with self.subTest(name=name), self.assertRaises(ValueError):
                runner.plan_details(self.root, ['inputs/shared.txt'])

    def test_nonstring_input_keeps_the_canonical_path_error(self):
        for name in ([], {}, None, 1):
            self.write('research/beta/VERIFY.json', json.dumps({'inputs': ['inputs/shared.txt', name]}))
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'canonical relative path must be a string'):
                runner.plan_details(self.root, ['inputs/shared.txt'])


if __name__ == '__main__':
    unittest.main()
