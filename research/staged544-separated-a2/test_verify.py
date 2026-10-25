#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded mutation controls for the fixed separated-A2 witnesses.

Uses the submitted verifier as the subject under test; it is not an independent
matrix or full-word semantics proof.  Every required check uses explicit errors,
so the same suite remains effective with Python's optimization enabled.
"""
import argparse
from copy import deepcopy
import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


class TestFailure(Exception):
    pass


def need(ok, message):
    if not ok:
        raise TestFailure(message)


def import_subject(root):
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location('separated_a2_subject', root / 'verify.py')
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    return subject


def writable_copy(source, destination):
    """Fresh files only; never relax permissions on a frozen source export."""
    shutil.copytree(source, destination, copy_function=shutil.copyfile)
    for path in destination.rglob('*'):
        path.chmod(0o755 if path.is_dir() else 0o644)
    destination.chmod(0o755)


def run_cli(root, provider='base'):
    command = [sys.executable, '-I', '-B']
    if not __debug__:
        command.append('-O')
    command.extend([str(root / 'verify.py'), '--provider', provider, '--quick'])
    return subprocess.run(command, cwd=root, capture_output=True, text=True)


class Controls:
    def __init__(self, errors):
        self.errors = errors
        self.rejected = []

    def rejects(self, name, action):
        try:
            action()
        except self.errors:
            self.rejected.append(name)
            return
        except Exception as error:
            raise TestFailure(name + ' crashed with ' + type(error).__name__ + ': ' + str(error)) from error
        raise TestFailure(name + ' was accepted')

    def cli_rejects(self, name, fixture):
        result = run_cli(fixture)
        need(result.returncode != 0, name + ' CLI accepted the altered fixture')
        need('FAIL' in result.stderr, name + ' CLI did not report an explicit validation failure: ' + result.stderr[-500:])
        self.rejected.append(name)


def tree_bytes(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.package.resolve()
    before = tree_bytes(root)
    subject = import_subject(root)
    core = subject.authenticate()
    controls = Controls((ValueError, core.AuditFailure))
    source = subject.load_word('base')
    sites = list(subject.SITES)
    separated = next(site for site in sites if not site['known'] and site['section'] == 'B')
    known = next(site for site in sites if site['known'])
    indices = separated['indices']
    gap = next(i for i in range(indices[0], indices[2]) if i not in indices)
    support = subject.certify_site(source, separated)['support']

    def site_control(name, mutate):
        word, site = deepcopy(source), deepcopy(separated)
        mutate(word, site)
        controls.rejects(name, lambda: subject.certify_site(word, site))

    def set_site(field, value):
        return lambda _word, site: site.__setitem__(field, value)

    site_control('duplicate selected index', set_site('indices', [indices[0], indices[0], indices[2]]))
    site_control('reversed selected indices', set_site('indices', list(reversed(indices))))
    site_control('boolean selected index', set_site('indices', [True, indices[1], indices[2]]))
    site_control('selected index outside section', set_site('indices', [indices[0], indices[1], len(source['B'])]))
    site_control('boolean removed position', set_site('removed_position', False))
    site_control('integer known-site flag', set_site('known', 0))
    site_control('unexpected site field', set_site('unproved', True))
    site_control('uncovered section', set_site('section', 'cut'))

    def alter_selected(word, site, position, action):
        action(word[site['section']][site['indices'][position]])

    site_control('wrong A2 sign', lambda w, s: alter_selected(w, s, 0, lambda g: g.__setitem__(3, -g[3])))
    site_control('wrong A2 product', lambda w, s: alter_selected(w, s, 2, lambda g: g.__setitem__(3, 2 * g[3])))
    site_control('boolean A2 coefficient', lambda w, s: alter_selected(w, s, 0, lambda g: g.__setitem__(3, True)))
    site_control('zero A2 denominator', lambda w, s: alter_selected(w, s, 0, lambda g: g.__setitem__(4, 0)))
    site_control('mismatched original frame', lambda w, s: alter_selected(w, s, 0, lambda g: g.__setitem__(-1, [512])))
    site_control('self ADD edge', lambda w, s: alter_selected(w, s, 0, lambda g: g.__setitem__(2, g[1])))
    site_control('unknown selected primitive', lambda w, s: alter_selected(w, s, 0, lambda g: g.__setitem__(0, 'copy')))
    site_control('unknown intervening primitive', lambda w, s: w['B'].__setitem__(gap, ['copy', 0, 1, 1, 1, []]))
    site_control('intervening support dependency', lambda w, s: w['B'].__setitem__(gap, ['scale', support[0], 2, 1, []]))
    site_control('native warp cut crossing', lambda w, s: w['warps'][0].__setitem__(0, indices[0] + 1))
    cut_word = deepcopy(source)
    cut_word['prelude_events'] = known['indices'][0] + 1
    controls.rejects('prelude cut crossing', lambda: subject.certify_site(cut_word, deepcopy(known)))
    controls.rejects('boolean include-known flag', lambda: subject.contract(source, 1))
    controls.rejects('unrecognized provider', lambda: subject.load_word('unproved'))

    positive = []
    changed_base = None
    for provider in ('base', 'extra'):
        original = subject.load_word(provider)
        changed = subject.contract(original)
        info = subject.inspect_word(core, changed)
        need(info['lengths'] == {'A': 4078, 'B': 1867, 'restore': 207, 'cleanup': 5218},
             'fixed contraction lengths changed for ' + provider)
        need(changed['cleanup'] == core.derive_cleanup(changed), 'positive cleanup not literal inverse')
        need(all(a[1:] == b[1:] for a, b in zip(original['warps'], changed['warps'])),
             'positive contraction changed native maps or frames')
        positive.append(provider + ' fixed contractions, literal cleanup, complete bill')
        if provider == 'base':
            changed_base = changed

    def word_control(name, mutate):
        word = deepcopy(changed_base)
        mutate(word)
        controls.rejects(name, lambda: subject.inspect_word(core, word))

    word_control('omitted inverse cleanup ADD', lambda w: w['cleanup'].pop())
    word_control('duplicated inverse cleanup ADD', lambda w: w['cleanup'].append(deepcopy(w['cleanup'][-1])))
    word_control('wrong inverse cleanup sign', lambda w: w['cleanup'][0].__setitem__(3, -w['cleanup'][0][3]))
    word_control('stale original inverse cleanup', lambda w: w.__setitem__('cleanup', deepcopy(source['cleanup'])))
    word_control('forged declared paid profile', lambda w: w['report']['local_profile'].__setitem__('1', 2439))

    certificate = subject.compute('base', False)
    subject.audit('base', False, certificate=certificate)
    positive.append('exact quick certificate accepted')

    def receipt_control(name, mutate):
        receipt = deepcopy(certificate)
        mutate(receipt)
        controls.rejects(name, lambda: subject.audit('base', False, certificate=receipt))

    receipt_control('forged forward saving', lambda r: r.__setitem__('additional_forward_add_saving', 8))
    receipt_control('forged cleanup saving', lambda r: r.__setitem__('additional_cleanup_add_saving', 6))
    receipt_control('integer false kappa flag', lambda r: r.__setitem__('new_kappa', 0))
    receipt_control('unsupported kappa claim', lambda r: r.__setitem__('new_kappa', True))
    receipt_control('unsupported native claim', lambda r: r.__setitem__('native_operators_changed', True))
    receipt_control('forged result hash', lambda r: r['words']['separated'].__setitem__('canonical_word_sha256', '0' * 64))
    receipt_control('forged helper inventory', lambda r: r['words']['separated']['helper_widths'].__setitem__(9, 214))
    receipt_control('extra unverified receipt field', lambda r: r.__setitem__('proved_by_assert', True))

    # CLI controls run against fresh writable copies; retained source bytes and
    # the package under test are never changed, even on a read-only export.
    with tempfile.TemporaryDirectory(prefix='separated-a2-negative-') as directory:
        fixture = Path(directory) / 'package'
        writable_copy(root, fixture)
        baseline = run_cli(fixture)
        need(baseline.returncode == 0 and 'PASS_STAGED544_SEPARATED_A2' in baseline.stdout,
             'unaltered CLI fixture failed: ' + baseline.stderr[-500:])
        positive.append('unaltered copied CLI fixture accepted')

        for relative in ('source/audit_core.py', 'inputs/BORROW-WORD-base.json.gz'):
            path = fixture / relative
            raw = path.read_bytes()
            path.write_bytes(raw + b'\n')
            controls.cli_rejects('CLI altered frozen ' + relative, fixture)
            path.write_bytes(raw)

        receipt_path = fixture / 'data.json'
        receipt_bytes = receipt_path.read_bytes()
        data = json.loads(receipt_bytes)
        forged = deepcopy(data)
        forged['providers']['base']['additional_cleanup_add_saving'] = 6
        receipt_path.write_text(json.dumps(forged) + '\n')
        controls.cli_rejects('CLI forged cleanup saving', fixture)
        forged = deepcopy(data)
        forged['schema_version'] = True
        receipt_path.write_text(json.dumps(forged) + '\n')
        controls.cli_rejects('CLI boolean root schema', fixture)
        receipt_path.write_text('{"schema_version":1,"schema_version":1,"providers":' + json.dumps(data['providers']) + '}\n')
        controls.cli_rejects('CLI duplicate JSON key', fixture)
        receipt_path.write_bytes(receipt_bytes)
        source_path = fixture / 'source/audit_core.py'
        source_bytes = source_path.read_bytes()
        sibling = Path(directory) / 'same-audit-core.py'
        sibling.write_bytes(source_bytes)
        source_path.unlink()
        source_path.symlink_to(sibling)
        controls.cli_rejects('CLI symlink source substitution', fixture)

    need(tree_bytes(root) == before, 'the package under test changed')
    print('PASS_SEPARATED_A2_NEGATIVE_CONTROLS ' + json.dumps(
        {'positive_controls': len(positive), 'expected_rejections': len(controls.rejected),
         'positive_names': positive, 'rejection_names': controls.rejected,
         'package_bytes_unchanged': True, 'optimized': not __debug__}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except TestFailure as error:
        raise SystemExit('FAIL: ' + str(error))
