"""Keep initial intake observations distinct from authenticated later heads."""
from copy import deepcopy
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
adapter = runpy.run_path(str(ROOT / 'scripts/pr_intake_initial_heads.py'))
initial_head = adapter['initial_head_for_decision']
INTAKE = adapter['INTAKE']


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InitialIntakeHeads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        numbers = set(adapter['REVISIONS'])
        cls.decisions = {row['number']: row for row in json.loads((ROOT / INTAKE).read_text())['pull_requests']
                         if row['number'] in numbers}
        cls.ledger = {row['number']: row for row in json.loads(
            (ROOT / 'docs/research/pr-ledger.json').read_text())['pull_requests'] if row['number'] in numbers}

    def test_exact_checkpoint_retains_initial_head_and_current_metadata(self):
        generator = load_script('reconcile_pr_queue')
        checker = load_script('verify_pr_reconciliation')
        for number, decision in self.decisions.items():
            original = deepcopy(decision)
            with self.subTest(number=number):
                self.assertNotEqual(self.ledger[number]['starting_head'], decision['metadata']['headRefOid'])
                for derive in (initial_head, generator.initial_head_for_decision,
                               checker.initial_head_for_decision):
                    self.assertEqual(derive(ROOT, INTAKE, decision), self.ledger[number]['starting_head'])
                self.assertEqual(decision, original)

    def test_actual_generator_preserves_initial_and_current_observations(self):
        generator = load_script('reconcile_pr_queue')
        outputs = {}
        allowed = {ROOT / 'docs/research/pr-ledger.json', ROOT / 'docs/research/pr-ledger.md'}

        def capture(path, text, *args, **kwargs):
            self.assertIn(path, allowed, 'Unexpected generator write')
            outputs[path.name] = text
            return len(text)

        with patch.object(Path, 'write_text', capture), contextlib.redirect_stdout(io.StringIO()):
            generator.build()
        self.assertEqual(set(outputs), {'pr-ledger.json', 'pr-ledger.md'})
        rows = {row['number']: row for row in json.loads(outputs['pr-ledger.json'])['pull_requests']}
        for number in self.decisions:
            for field in ('starting_head', 'current_head', 'reviewed_head', 'contributor'):
                with self.subTest(number=number, field=field):
                    self.assertEqual(rows[number][field], self.ledger[number][field])

    def test_unknown_future_heads_and_independent_metadata_mutations_fail(self):
        for number, decision in self.decisions.items():
            for field in ('metadata', 'current_head', 'reviewed_head', 'all_heads'):
                changed = deepcopy(decision)
                if field in ('metadata', 'all_heads'):
                    changed['metadata']['headRefOid'] = 'f' * 40
                if field in ('current_head', 'reviewed_head'):
                    changed[field] = 'f' * 40
                if field == 'all_heads':
                    changed['current_head'] = changed['reviewed_head'] = 'f' * 40
                with self.subTest(number=number, field=field), self.assertRaisesRegex(
                        ValueError, 'unrecorded intake revision'):
                    initial_head(ROOT, INTAKE, changed)

    def test_metadata_number_and_attribution_cannot_be_substituted(self):
        for number, decision in self.decisions.items():
            for field in ('number', 'author'):
                changed = deepcopy(decision)
                changed['metadata'][field] = number + 1 if field == 'number' else {'login': 'unrelated'}
                with self.subTest(number=number, field=field), self.assertRaises(ValueError):
                    initial_head(ROOT, INTAKE, changed)

    def test_receipt_byte_changes_and_forged_original_heads_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipts = root / 'docs/research/pr-intake-evidence'
            receipts.mkdir(parents=True)
            originals = {}
            for name in adapter['RECEIPTS']:
                data = (ROOT / 'docs/research/pr-intake-evidence' / (name + '.json')).read_bytes()
                originals[name] = data
                (receipts / (name + '.json')).write_bytes(data)
            for number, decision in self.decisions.items():
                old_name, field, current_name = adapter['REVISIONS'][number]
                for name in dict.fromkeys((old_name, current_name)):
                    path = receipts / (name + '.json')
                    for mutation in ('append', 'change_head'):
                        raw = originals[name]
                        if mutation == 'append':
                            changed = raw + b'\n'
                        else:
                            data = json.loads(raw)
                            row = next(row for row in data['contributions'] if row['number'] == number)
                            row[field if name == old_name else 'head'] = '0' * 40
                            changed = json.dumps(data).encode()
                        path.write_bytes(changed)
                        with self.subTest(number=number, name=name, mutation=mutation), self.assertRaisesRegex(
                                ValueError, 'Changed initial-head receipt'):
                            initial_head(root, INTAKE, decision)
                        path.write_bytes(raw)

    def test_other_families_and_new_prs_keep_original_metadata_rule(self):
        for decision in self.decisions.values():
            self.assertEqual(initial_head(ROOT, 'research/earlier/DISPOSITIONS.json', decision),
                             decision['metadata']['headRefOid'])
        decision = deepcopy(self.decisions[3107])
        decision['number'] = decision['metadata']['number'] = 99999
        self.assertEqual(initial_head(ROOT, INTAKE, decision), decision['metadata']['headRefOid'])

    def test_actual_entrypoint_rejects_forged_starting_head_and_attribution(self):
        """Exercise the metadata boundary, stopping before unrelated archive work."""
        checker = load_script('verify_pr_reconciliation')
        class ReachedArchive(Exception):
            pass
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in adapter['RECEIPTS']:
                relative = Path('docs/research/pr-intake-evidence') / (name + '.json')
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_bytes((ROOT / relative).read_bytes())
            decisions = deepcopy(list(self.decisions.values()))
            rows = deepcopy(list(self.ledger.values()))
            # This fixture isolates the starting-head boundary from the separate
            # incremental-closure compatibility change in PR3686.
            for row in decisions + rows:
                row.setdefault('closure', None)
            (root / INTAKE).write_text(json.dumps({'pull_requests': decisions}))
            audit = root / 'research/pr-reconciliation-20261012'
            audit.mkdir(parents=True)
            (audit / 'starting-snapshot.json').write_text('{"pull_requests": []}')
            package = root / 'research/coordinated-frames-and-entrance-banks'
            package.mkdir(parents=True)
            (package / 'BASELINE.json').write_text('{}')
            ledger_path = root / 'docs/research/pr-ledger.json'
            with patch.object(checker, 'ROOT', root), patch.object(checker, 'AUDIT', audit), \
                 patch.object(checker, 'decision_paths', return_value=[root / INTAKE]), \
                 patch.object(checker, 'archive_inventory', side_effect=ReachedArchive):
                ledger_path.write_text(json.dumps({'pull_requests': rows, 'source_sha256': {}}))
                with self.assertRaises(ReachedArchive):
                    checker.main()
                for number in self.decisions:
                    for field, value in [('starting_head', '0' * 40),
                                         ('starting_head', self.decisions[number]['current_head']),
                                         ('current_head', '0' * 40),
                                         ('contributor', {'login': 'unrelated'})]:
                        changed = deepcopy(rows)
                        next(row for row in changed if row['number'] == number)[field] = value
                        ledger_path.write_text(json.dumps({'pull_requests': changed, 'source_sha256': {}}))
                        with self.subTest(number=number, field=field, value=value), self.assertRaises(ValueError):
                            checker.main()


if __name__ == '__main__':
    unittest.main()
