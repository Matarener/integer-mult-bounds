"""Queue scheduling must never turn cached triage into scientific approval."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('pr_intake', Path(__file__).resolve().parents[1] / 'scripts/pr_intake.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def live(n=1, head='a' * 40, draft=False):
    return dict(number=n, headRefOid=head, isDraft=draft, title='contribution')


def state(status='waiting_revision'):
    return dict(schema_version=1, pull_requests=[dict(number=1, head='a' * 40,
                status=status, reason='Concrete unresolved source obligation', evidence=['review.json'],
                policy_version=1, watch_paths={'review.json': 'b' * 40}, watch_prs={})])


class IntakeTests(unittest.TestCase):
    def run_plan(self, s=None, prs=None, tree=None, **kw):
        return m.plan(s or state(), prs if prs is not None else [live()],
                      tree if tree is not None else {'review.json': 'b' * 40}, **kw)

    def test_unchanged_hold_is_not_selected(self):
        s = state(); before = copy.deepcopy(s)
        r = self.run_plan(s)
        self.assertEqual(r['selected'], [])
        self.assertEqual(r['counts'], {'waiting_revision': 1})
        self.assertEqual(s, before)

    def test_head_evidence_and_policy_changes_reactivate(self):
        self.assertEqual(self.run_plan(prs=[live(head='c' * 40)])['selected'][0]['lane'], 'reactivated')
        self.assertEqual(self.run_plan(tree={})['selected'][0]['lane'], 'reactivated')
        s = state(); s['pull_requests'][0]['policy_version'] = 0
        self.assertEqual(self.run_plan(s)['selected'][0]['lane'], 'reactivated')

    def test_dependency_change_and_closure_reactivate(self):
        s = state(); s['pull_requests'][0]['watch_prs'] = {'2': 'd' * 40}
        self.assertEqual(self.run_plan(s, [live(), live(2, 'd' * 40)])['pull_requests'][0]['lane'], 'waiting_revision')
        self.assertEqual(self.run_plan(s, [live(), live(2, 'e' * 40)])['pull_requests'][0]['lane'], 'reactivated')
        self.assertEqual(self.run_plan(s)['selected'][0]['lane'], 'reactivated')

    def test_pending_work_never_becomes_dormant(self):
        self.assertEqual(len(self.run_plan(state('pending_review'))['selected']), 1)
        self.assertEqual(len(self.run_plan(state('ready_to_integrate'))['selected']), 1)

    def test_explicit_wake_but_no_automatic_replay(self):
        self.assertFalse(self.run_plan(state('deferred_replay'))['selected'])
        self.assertEqual(self.run_plan(state('deferred_replay'), wake=[1])['selected'][0]['lane'], 'reactivated')

    def test_drafts_closed_and_new(self):
        self.assertFalse(self.run_plan(prs=[live(draft=True)], wake=[1])['selected'])
        self.assertEqual(self.run_plan(prs=[])['no_longer_open'], [1])
        self.assertEqual(self.run_plan(prs=[live(2)])['selected'][0]['lane'], 'new')

    def test_chunk_limit_does_not_drop_queue(self):
        r = self.run_plan(prs=[live(n) for n in range(2, 203)])
        self.assertEqual(len(r['selected']), 100)
        self.assertEqual(r['remaining_actionable'], 101)
        self.assertEqual(r['open_count'], 201)

    def test_malformed_state_fails_closed(self):
        for change in ('status', 'head', 'reason', 'watch_paths'):
            s = state(); s['pull_requests'][0][change] = {'../bad': None} if change == 'watch_paths' else ''
            with self.assertRaises(ValueError): self.run_plan(s)
        with self.assertRaises(ValueError): self.run_plan(prs=[live(), live()])
        with self.assertRaises(ValueError): self.run_plan(limit=101)

    def test_mode_changes_reactivate_without_changing_blob_or_cached_state(self):
        s = state()
        s['pull_requests'][0]['watch_modes'] = {'review.json': '100644'}
        before = copy.deepcopy(s)
        self.assertFalse(self.run_plan(s, modes={'review.json': '100644'})['selected'])
        for mode in ('100755', '120000'):
            with self.subTest(mode=mode):
                row = self.run_plan(s, modes={'review.json': mode})['selected'][0]
                self.assertEqual(row['lane'], 'reactivated')
                self.assertEqual(row['changes'], ['main path mode changed: review.json'])
        self.assertEqual(s, before)

    def test_mode_aware_records_require_current_modes(self):
        s = state()
        s['pull_requests'][0]['watch_modes'] = {'review.json': '100644'}
        with self.assertRaisesRegex(ValueError, 'current tree modes required'):
            self.run_plan(s)
        self.assertEqual(self.run_plan(s, tree={})['selected'][0]['lane'], 'reactivated')


class IntakeModeCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        (self.repo / 'scripts').mkdir()
        self.script = self.repo / 'scripts/pr_intake.py'
        self.script.write_bytes(Path(m.__file__).read_bytes())
        self.path = 'replay[1].sh'
        (self.repo / self.path).write_bytes(b'#!/bin/sh\nexit 0\n')
        self.git('init')
        self.git('config', 'core.autocrlf', 'false')
        self.git('add', '--', self.path)
        self.git('update-index', '--chmod=-x', '--', self.path)
        self.git('commit', '-m', 'watched file')
        self.base = self.git('rev-parse', 'HEAD')
        self.oid = self.git('rev-parse', f'{self.base}:{self.path}')
        self.state_path = self.root / 'state.json'
        self.state_path.write_text(json.dumps({'schema_version': 1, 'pull_requests': []}))
        self.live_path = self.root / 'live.json'
        self.live_path.write_text(json.dumps([live(head=self.base)]))
        self.output = self.root / 'plan.json'

    def git(self, *args):
        return subprocess.check_output(
            ['git', '-C', str(self.repo), '-c', 'user.name=Fixture',
             '-c', 'user.email=fixture@example.invalid', *args],
            stderr=subprocess.DEVNULL, text=True).strip()

    def cli(self, action, *args):
        return subprocess.run(
            [sys.executable, '-B', str(self.script), action, '--state', str(self.state_path),
             '--live-json', str(self.live_path), *args],
            capture_output=True, text=True, timeout=30)

    def record(self, legacy=False):
        run = self.cli('record', '--base', self.base, '--number', '1', '--head', self.base,
                       '--status', 'waiting_revision', '--reason', 'Watched replay requires repair.',
                       '--evidence', 'https://example.invalid/review', '--watch-path', self.path)
        self.assertEqual(run.returncode, 0, run.stderr)
        if legacy:
            state = json.loads(self.state_path.read_text())
            state['pull_requests'][0].pop('watch_modes', None)
            self.state_path.write_text(json.dumps(state))

    def run_plan(self, base=None, *args):
        return self.cli('plan', '--base', base or self.git('rev-parse', 'HEAD'),
                        '--output', str(self.output), *args)

    def test_record_pins_blob_and_mode(self):
        self.record()
        row = json.loads(self.state_path.read_text())['pull_requests'][0]
        self.assertEqual(row['watch_paths'], {self.path: self.oid})
        self.assertEqual(row['watch_modes'], {self.path: '100644'})
        self.assertEqual(row['baseline'], self.base)

    def test_new_and_legacy_records_wake_for_chmod_and_symlink_same_blob(self):
        for legacy in (False, True):
            for mode in ('100755', '120000'):
                with self.subTest(legacy=legacy, mode=mode):
                    self.record(legacy=legacy)
                    before = self.state_path.read_bytes()
                    self.git('update-index', '--cacheinfo', f'{mode},{self.oid},{self.path}')
                    self.git('commit', '-m', f'watched mode {mode}')
                    self.assertEqual(self.git('rev-parse', f'HEAD:{self.path}'), self.oid)
                    run = self.run_plan()
                    self.assertEqual(run.returncode, 0, run.stderr)
                    result = json.loads(self.output.read_text())
                    self.assertEqual(result['actionable_count'], 1)
                    row = result['selected'][0]
                    self.assertEqual(row['head'], self.base, 'PR head must stay unchanged')
                    self.assertEqual(row['lane'], 'reactivated')
                    self.assertEqual(row['changes'], [f'main path mode changed: {self.path}'])
                    self.assertEqual(self.state_path.read_bytes(), before)

    def test_unchanged_and_unrelated_main_changes_preserve_new_and_legacy_holds(self):
        (self.repo / 'unrelated').write_bytes(b'unrelated')
        self.git('add', 'unrelated')
        self.git('commit', '-m', 'unrelated change')
        for legacy in (False, True):
            self.record(legacy=legacy)
            before = self.state_path.read_bytes()
            for base in (self.base, self.git('rev-parse', 'HEAD')):
                with self.subTest(legacy=legacy, base=base):
                    run = self.run_plan(base)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    result = json.loads(self.output.read_text())
                    self.assertEqual(result['selected'], [])
                    self.assertEqual(result['pull_requests'][0]['changes'], [])
                    self.assertEqual(result['counts'], {'waiting_revision': 1})
                    self.assertEqual(self.state_path.read_bytes(), before)

    def unavailable_baseline(self):
        state = json.loads(self.state_path.read_text())
        state['pull_requests'][0]['baseline'] = 'f' * 40
        self.state_path.write_text(json.dumps(state))

    def test_missing_legacy_history_reports_error_without_a_plan(self):
        for status in ('waiting_revision', 'deferred_replay', 'ready_to_integrate'):
            with self.subTest(status=status):
                self.record(legacy=True)
                self.unavailable_baseline()
                state = json.loads(self.state_path.read_text())
                state['pull_requests'][0]['status'] = status
                self.state_path.write_text(json.dumps(state))
                before = self.state_path.read_bytes()
                run = self.run_plan()
                self.assertNotEqual(run.returncode, 0)
                self.assertIn('cannot recover watched modes at baseline', run.stderr)
                self.assertIn('make recorded history available or refresh the intake record', run.stderr)
                self.assertFalse(self.output.exists())
                self.assertEqual(self.state_path.read_bytes(), before)

    def test_new_records_need_no_historical_lookup(self):
        self.record()
        self.unavailable_baseline()
        run = self.run_plan()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(self.output.read_text())['selected'], [])

    def test_inconsistent_available_baseline_reactivates_without_using_its_mode(self):
        for mismatch in ('different_blob', 'missing_file'):
            with self.subTest(mismatch=mismatch):
                self.record(legacy=True)
                state = json.loads(self.state_path.read_text())
                row = state['pull_requests'][0]
                if mismatch == 'different_blob':
                    (self.repo / self.path).write_bytes(b'updated cached dependency')
                    self.git('add', '--', self.path)
                    self.git('commit', '-m', 'updated dependency')
                    base = self.git('rev-parse', 'HEAD')
                    row['watch_paths'][self.path] = self.git('rev-parse', f'HEAD:{self.path}')
                else:
                    self.git('rm', '--', self.path)
                    self.git('commit', '-m', 'baseline without dependency')
                    row['baseline'] = self.git('rev-parse', 'HEAD')
                    base = self.base
                self.state_path.write_text(json.dumps(state))
                before = self.state_path.read_bytes()
                run = self.run_plan(base)
                self.assertEqual(run.returncode, 0, run.stderr)
                row = json.loads(self.output.read_text())['selected'][0]
                self.assertEqual(row['lane'], 'reactivated')
                self.assertEqual(row['changes'], [
                    f'watched file does not match recorded baseline: {self.path}'])
                self.assertEqual(self.state_path.read_bytes(), before)

    def test_closed_and_draft_legacy_rows_need_no_historical_lookup(self):
        self.record(legacy=True)
        self.unavailable_baseline()
        for prs in ([], [live(head=self.base, draft=True)]):
            with self.subTest(prs=prs):
                self.live_path.write_text(json.dumps(prs))
                run = self.run_plan()
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(json.loads(self.output.read_text())['selected'], [])

    def test_existing_wakes_and_pending_review_do_not_require_legacy_history(self):
        for reason in ('head', 'policy', 'dependency', 'wake', 'pending', 'path'):
            with self.subTest(reason=reason):
                self.live_path.write_text(json.dumps([live(head=self.base)]))
                self.record(legacy=True)
                self.unavailable_baseline()
                state = json.loads(self.state_path.read_text())
                row = state['pull_requests'][0]
                base, args = self.base, []
                if reason == 'head':
                    self.live_path.write_text(json.dumps([live(head='c' * 40)]))
                elif reason == 'policy':
                    row['policy_version'] = 0
                elif reason == 'dependency':
                    row['watch_prs'] = {'2': 'd' * 40}
                elif reason == 'wake':
                    args = ['--wake', '1']
                elif reason == 'pending':
                    row['status'] = 'pending_review'
                elif reason == 'path':
                    (self.repo / self.path).write_bytes(b'changed watched content')
                    self.git('add', '--', self.path)
                    self.git('commit', '-m', 'watched content changed')
                    base = self.git('rev-parse', 'HEAD')
                self.state_path.write_text(json.dumps(state))
                before = self.state_path.read_bytes()
                run = self.run_plan(base, *args)
                self.assertEqual(run.returncode, 0, run.stderr)
                row = json.loads(self.output.read_text())['selected'][0]
                self.assertEqual(row['lane'], 'pending_review' if reason == 'pending' else 'reactivated')
                self.assertEqual(self.state_path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
