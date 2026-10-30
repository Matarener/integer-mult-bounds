"""Local replacement refs must not redefine immutable research source pins."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_research_commit as publication
import export_research_package as exporter
import new_research_package as scaffold
import research_package as package
sys.path.pop(0)


class GitReplacementTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.raw_git('init', '-q')
        self.raw_git('config', 'user.name', 'Fixture')
        self.raw_git('config', 'user.email', 'fixture@example.invalid')
        self.raw_git('config', 'core.autocrlf', 'false')
        self.catalog_name = 'docs/research/agent-task-catalog.json'
        self.card = {'id': 'fixture', 'question': 'Authenticate the committed bytes'}
        self.original = b'authentic input\n'
        self.replacement = b'replacement input\n'
        files = {
            self.catalog_name: json.dumps({'priority_revision': 6,
                                          'tracks': [{'tasks': [self.card]}]}).encode(),
            'certificates/selected-result.json': b'{}',
            'input.txt': self.original,
        }
        if os.name != 'nt':
            files['line\nbreak'] = self.original
        for name, data in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.commit()
        self.base = self.raw_git('rev-parse', 'HEAD').decode().strip()
        self.oid = self.raw_git('rev-parse', 'HEAD:input.txt').decode().strip()
        self.other_oid = self.raw_git('hash-object', '-w', '--stdin', data=self.replacement).decode().strip()
        self.names = sorted(files)

    def raw_git(self, *args, data=None):
        # Fixture controls deliberately exercise Git's ordinary replacement behavior.
        env = os.environ.copy()
        env.pop('GIT_NO_REPLACE_OBJECTS', None)
        return subprocess.run(['git', *args], cwd=self.root, input=data, env=env,
                              capture_output=True, check=True).stdout

    def commit(self):
        self.raw_git('add', '.')
        self.raw_git('-c', 'maintenance.auto=false', '-c', 'gc.auto=0', 'commit', '-qm', 'fixture')

    def assert_original_readers(self, names):
        expected = [(self.oid, self.original)] * len(names)
        specs = [self.base + ':' + name for name in names]
        self.assertEqual(list(package.git_source_rows(self.root, self.base, names)), expected)
        self.assertEqual(list(package.git_blobs(self.root, specs)), expected)
        # Cover the legacy line protocol and its single-object CR/LF resolver too.
        self.assertEqual(list(package._git_blob_batch(self.root, specs, nul=False)), expected)
        self.assertEqual(list(package.git_blobs(self.root, [self.oid])), expected[:1])
        for spec in specs:
            self.assertEqual(package.git(self.root, 'show', spec), self.original)

    def test_blob_replacements_cannot_change_ids_or_bytes_in_any_reader(self):
        self.raw_git('replace', self.oid, self.other_oid)
        self.assertEqual(self.raw_git('show', self.base + ':input.txt'), self.replacement)
        names = ['input.txt'] + (['line\nbreak'] if os.name != 'nt' else [])
        self.assert_original_readers(names)

    def test_custom_replacement_namespace_does_not_change_parent_environment(self):
        namespace = 'refs/research-test-replacements/'
        self.raw_git('update-ref', namespace + self.oid, self.other_oid)
        for inherited in (None, ''):
            env = {**os.environ, 'GIT_REPLACE_REF_BASE': namespace}
            env.pop('GIT_NO_REPLACE_OBJECTS', None)
            if inherited is not None:
                env['GIT_NO_REPLACE_OBJECTS'] = inherited
            with self.subTest(inherited=inherited), patch.dict(os.environ, env, clear=True):
                self.assertEqual(self.raw_git('show', self.base + ':input.txt'), self.replacement)
                self.assert_original_readers(['input.txt'])
                self.assertEqual(os.environ.get('GIT_NO_REPLACE_OBJECTS'), inherited)

    def test_commit_replacement_cannot_change_tree_inventory_or_catalogue(self):
        (self.root / 'input.txt').write_bytes(self.replacement)
        (self.root / 'replacement-only.txt').write_bytes(b'not in original tree')
        altered = {'priority_revision': 6, 'tracks': [{'tasks': [
            {**self.card, 'question': 'Replacement catalogue'}]}]}
        (self.root / self.catalog_name).write_text(json.dumps(altered))
        self.commit()
        other = self.raw_git('rev-parse', 'HEAD').decode().strip()
        self.raw_git('reset', '--hard', self.base)
        self.raw_git('replace', self.base, other)
        self.assertEqual(self.raw_git('show', self.base + ':input.txt'), self.replacement)
        self.assert_original_readers(['input.txt'])
        self.assertEqual(package.tracked_input_paths(self.root), frozenset(self.names))
        target = scaffold.create(self.root, 'fixture', 'fixture', 'Fixture', ['input.txt'])
        self.assertEqual(json.loads((target / 'TASK.json').read_bytes())['original_card'], self.card)
        self.assertEqual(package.catalogue_card(self.root, 'research/fixture', 'fixture'), self.card)

    def ready_package(self):
        target = scaffold.create(self.root, 'fixture', 'fixture', 'Fixture', ['input.txt'])
        task = json.loads((target / 'TASK.json').read_bytes())
        task.update(bottleneck_link='Portable source checks', stop_rule='Bounded fixture',
                    outcome='completed', evidence='Synthetic Git replacement controls',
                    ai_assistance='OpenAI Codex', open_questions=[],
                    no_open_questions_reason='Only the scoped byte binding is checked')
        (target / 'TASK.json').write_text(json.dumps(task))
        manifest = json.loads((target / 'VERIFY.json').read_bytes())
        manifest['status'] = 'ready'
        manifest['commands'][0]['checks'] = 'Synthetic source binding'
        (target / 'VERIFY.json').write_text(json.dumps(manifest))
        return target

    def test_scaffold_and_validator_reject_replacement_only_live_bytes(self):
        self.raw_git('replace', self.oid, self.other_oid)
        (self.root / 'input.txt').write_bytes(self.replacement)
        with self.assertRaisesRegex(ValueError, 'source has uncommitted changes'):
            scaffold.create(self.root, 'bad', 'fixture', 'Fixture', ['input.txt'])
        self.assertFalse((self.root / 'research/bad').exists())
        (self.root / 'input.txt').write_bytes(self.original)
        target = self.ready_package()
        package.validate(self.root, 'research/fixture')
        (self.root / 'input.txt').write_bytes(self.replacement)
        with self.assertRaisesRegex(ValueError, 'working source drift'):
            package.validate(self.root, 'research/fixture')
        sources = json.loads((target / 'SOURCES.json').read_bytes())
        row = next(row for row in sources['files'] if row['path'] == 'input.txt')
        self.assertEqual(row['git_blob'], self.oid)
        row['sha256'] = hashlib.sha256(self.replacement).hexdigest()
        (target / 'SOURCES.json').write_text(json.dumps(sources))
        with self.assertRaisesRegex(ValueError, 'source SHA256 provenance mismatch'):
            package.validate(self.root, 'research/fixture')

    def test_publication_preflight_compares_actual_commit_bytes(self):
        self.ready_package()
        self.commit()
        self.raw_git('replace', self.oid, self.other_oid)
        publication.check(self.root, 'research/fixture')
        (self.root / 'input.txt').write_bytes(self.replacement)
        with self.assertRaisesRegex(ValueError, 'working/commit bytes differ: input.txt'):
            publication.check(self.root, 'research/fixture')

    def test_export_retains_original_payload_and_receipt_under_replacement(self):
        self.ready_package()
        self.commit()
        self.raw_git('replace', self.oid, self.other_oid)
        output = self.root / 'bundle.tar'
        receipt = exporter.export(self.root, 'research/fixture', 'HEAD', output)
        with tarfile.open(output) as archive:
            self.assertEqual(archive.extractfile('input.txt').read(), self.original)
        row = next(row for row in receipt['files'] if row['path'] == 'input.txt')
        self.assertEqual(row['sha256'], hashlib.sha256(self.original).hexdigest())
        self.assertEqual(exporter.check_bundle(output), receipt)


if __name__ == '__main__':
    unittest.main()
