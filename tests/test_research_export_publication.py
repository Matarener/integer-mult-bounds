"""Publish complete exports without overwriting a destination that appears late.

Builds on Tekalign's exporter and the retained publication/portability controls.
Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance. Apache-2.0.
"""
from pathlib import Path
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import export_research_package as exporter


class ExportPublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = 'research/fixture'
        package = self.root / self.package
        package.mkdir(parents=True)
        (package / 'VERIFY.json').write_text(
            json.dumps({'inputs': ['input.bin']}), encoding='utf-8')
        (package / 'verify.py').write_bytes(b'print("PASS_FIXTURE")\n')
        (self.root / 'input.bin').write_bytes(b'\x00\xff\r\n')
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'core.autocrlf', 'false')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        self.commit = self.git('rev-parse', 'HEAD').decode('ascii').strip()
        self.output = self.root / 'complete export 雪.tar'
        self.operation = 'rename' if os.name == 'nt' else 'link'

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root,
                                       stderr=subprocess.PIPE, timeout=30)

    def export(self):
        return exporter.export(self.root, self.package, self.commit, self.output)

    def assert_no_staging(self):
        self.assertEqual(list(self.root.glob('.research-export-*')), [])

    @unittest.skipUnless(os.name == 'nt', 'native Windows rename contract')
    def test_export_succeeds_when_hard_links_are_unavailable(self):
        with patch.object(exporter.os, 'link', side_effect=PermissionError(
                'hard links unavailable')) as link:
            receipt = self.export()
            other = self.root / 'second.tar'
            exporter.export(self.root, self.package, self.commit, other)
        link.assert_not_called()
        self.assertEqual(self.output.read_bytes(), other.read_bytes())
        self.assertEqual(exporter.check_bundle(self.output), receipt)
        self.assertEqual(exporter.check_bundle(self.output, check_inputs=True)
                         ['declared_inputs_checked'], 1)
        self.assert_no_staging()

    def test_publication_sees_complete_closed_archive(self):
        publish = getattr(exporter.os, self.operation)
        receipts = []

        def inspect(source, destination):
            self.assertFalse(self.output.exists())
            self.assertEqual(Path(source).parent, self.output.parent)
            receipts.append(exporter.check_bundle(source))
            # Windows rename also requires the staging handle to be closed.
            return publish(source, destination)

        with patch.object(exporter.os, self.operation, side_effect=inspect):
            receipt = self.export()
        self.assertEqual(receipts, [receipt])
        self.assertEqual(exporter.check_bundle(self.output), receipt)
        self.assert_no_staging()

    def test_late_file_or_directory_is_not_overwritten(self):
        publish = getattr(exporter.os, self.operation)
        for kind in ('file', 'directory'):
            with self.subTest(kind=kind):
                self.output = self.root / (kind + '.tar')

                def compete(source, destination):
                    if kind == 'directory':
                        self.output.mkdir()
                        (self.output / 'keep').write_bytes(b'other publisher')
                    else:
                        self.output.write_bytes(b'other publisher')
                    return publish(source, destination)

                with patch.object(exporter.os, self.operation, side_effect=compete):
                    with self.assertRaises(FileExistsError):
                        self.export()
                kept = self.output / 'keep' if kind == 'directory' else self.output
                self.assertEqual(kept.read_bytes(), b'other publisher')
                self.assert_no_staging()

    def test_publication_failure_propagates_and_removes_staging(self):
        failure = PermissionError('publication denied')
        with patch.object(exporter.os, self.operation, side_effect=failure):
            with self.assertRaises(PermissionError) as caught:
                self.export()
        self.assertIs(caught.exception, failure)
        self.assertFalse(self.output.exists())
        self.assert_no_staging()

    def test_archive_close_failure_never_publishes(self):
        close = tarfile.TarFile.close
        failure = OSError('archive close failed')

        def fail_close(archive):
            was_open = not archive.closed
            close(archive)
            if was_open and archive.mode == 'w':
                raise failure

        with patch.object(tarfile.TarFile, 'close', fail_close), \
                patch.object(exporter.os, self.operation) as publish:
            with self.assertRaises(OSError) as caught:
                self.export()
        self.assertIs(caught.exception, failure)
        publish.assert_not_called()
        self.assertFalse(self.output.exists())
        self.assert_no_staging()


if __name__ == '__main__':
    unittest.main()
