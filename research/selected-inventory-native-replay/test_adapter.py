"""An explicit alias reproducer and controls on the retained budget assertions."""
import importlib.util
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('native_replay', HERE / 'verify.py')
replay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(replay)


def budget_result(module):
    result = unittest.TestResult()
    module.SelectedInventoryControls('test_complete_inventory_and_entry_budget').run(result)
    return result


class FixtureAdapterControls(unittest.TestCase):
    def test_forced_alias_fails_before_and_passes_after(self):
        before, after = replay.archived_tests(False), replay.archived_tests(True)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            real, alias = root / 'real', root / 'alias'
            real.mkdir()
            alias.symlink_to(real, target_is_directory=True)
            self.assertNotEqual(alias, alias.resolve())
            with mock.patch.object(tempfile, 'tempdir', str(alias)):
                original = budget_result(before)
                self.assertEqual(original.testsRun, 1)
                self.assertEqual(len(original.errors), 1)
                self.assertFalse(original.failures)
                self.assertIn('ValueError: Package symlink escapes root', original.errors[0][1])
                repaired = budget_result(after)
                self.assertEqual(repaired.testsRun, 1)
                self.assertTrue(repaired.wasSuccessful(), repaired.errors + repaired.failures)
                self.assertFalse(repaired.skipped)
            with mock.patch.object(tempfile, 'tempdir', str(real)):
                for module in (before, after):
                    control = budget_result(module)
                    self.assertTrue(control.wasSuccessful(), control.errors + control.failures)

    def test_budget_assertions_still_reject_a_disabled_limit(self):
        module = replay.archived_tests(True)
        original = module.c.package_files

        def unbounded(package, *, max_entries=module.c.MAX_ENTRIES):
            return original(package, max_entries=module.c.MAX_ENTRIES)

        with mock.patch.object(module.c, 'package_files', unbounded):
            result = budget_result(module)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 1)
        self.assertIn('ValueError not raised', result.failures[0][1])

    def test_changed_or_already_adapted_source_is_rejected(self):
        adapter = replay.adapter()
        raw = replay.source('research/selected-inventory-fail-closed/test_inventory.py')
        for mutant in (raw + b'\n', adapter.repair_fixture(raw)):
            with self.subTest(mutant_sha=sha256(mutant).hexdigest()):
                with self.assertRaisesRegex(ValueError, 'fixture source differs'):
                    adapter.repair_fixture(mutant)

    def test_live_source_drift_is_rejected_before_compilation(self):
        original = Path.read_bytes
        target = replay.ARCHIVE / 'check.py'

        def corrupt(path):
            return original(path) + (b'\nraise RuntimeError("must not execute")\n' if path == target else b'')

        with mock.patch.object(Path, 'read_bytes', corrupt):
            with self.assertRaisesRegex(ValueError, 'live source differs'):
                replay.archived_tests(True)


    def test_incomplete_failed_or_skipped_suite_is_rejected(self):
        for count, skipped, failed in ((58, False, False), (60, False, False),
                                       (59, True, False), (59, False, True)):
            result = unittest.TestResult()
            result.testsRun = count
            if skipped:
                result.skipped.append((self, 'fixture unavailable'))
            if failed:
                result.failures.append((self, 'fixture failed'))
            with self.subTest(count=count, skipped=skipped, failed=failed):
                with self.assertRaisesRegex(ValueError, '59 groups'):
                    replay.require_complete(result)
        result = unittest.TestResult()
        result.testsRun = 59
        replay.require_complete(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
