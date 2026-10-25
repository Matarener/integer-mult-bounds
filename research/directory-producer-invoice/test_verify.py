#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded behavioral and mutation controls for the directory component.

These tests exercise the submitted replay and package-local candidate. They do
not establish source-stock admission or recovery from malformed producer input.
"""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import importlib.util
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


def tree_bytes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def load_subject(root):
    spec = importlib.util.spec_from_file_location('directory_invoice_subject', root / 'verify.py')
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    return subject


@contextmanager
def candidate(subject, replacement):
    original = subject.high_power_shared
    subject.high_power_shared = replacement
    try:
        yield
    finally:
        subject.high_power_shared = original


def run_cli(root):
    command = [sys.executable, '-I', '-B']
    if not __debug__:
        command.append('-O')
    return subprocess.run(command + [str(root / 'verify.py')], cwd=root,
                          capture_output=True, text=True)


class Controls:
    def __init__(self):
        self.rejected = []

    def rejects(self, name, action):
        try:
            action()
        except ValueError:
            self.rejected.append(name)
            return
        except Exception as error:
            raise TestFailure(name + ' crashed with ' + type(error).__name__ + ': ' + str(error)) from error
        raise TestFailure(name + ' was accepted')

    def cli_rejects(self, name, root):
        result = run_cli(root)
        need(result.returncode != 0, name + ' CLI accepted the altered fixture')
        need('FAIL_DIRECTORY_PRODUCER_COMPONENT' in result.stderr,
             name + ' CLI did not report an explicit validation failure: ' + result.stderr[-500:])
        self.rejected.append(name)


def writable_copy(source, destination):
    shutil.copytree(source, destination, copy_function=shutil.copyfile)
    for path in destination.rglob('*'):
        path.chmod(0o755 if path.is_dir() else 0o644)
    destination.chmod(0o755)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.package.resolve()
    before = tree_bytes(root)
    subject = load_subject(root)
    controls = Controls()
    positives = []
    config = dict(name='test_d2', d=2, q=3, w=2, B=1, h=0, Q=4, I=3)

    # The first yield corresponds to the omitted leading radix digit. Every
    # later yield must contribute exactly d² ordered q multiplications, and the
    # iterator must be exhausted so its final validation runs.
    class Value:
        def __init__(self):
            self.factors = []

        def multiply_small(self, q):
            self.factors.append(q)

    calls = []
    completed = []

    def radix(_ring, q):
        calls.append(q)
        for _ in range(3):
            yield
        completed.append(True)

    value = Value()
    subject.high_power_shared(value, object(), 3, 2, radix)
    need(calls == [3] and completed == [True] and value.factors == [3] * 8,
         'shared candidate did not preserve one full traversal and ordered M(w-1) q multipliers')
    positives.append('one complete radix traversal and ordered M(w-1) multipliers')

    def late_failure(_ring, _q):
        yield
        yield
        raise ValueError('final radix validation sentinel')

    controls.rejects('omitted final radix validation',
                     lambda: subject.high_power_shared(Value(), object(), 3, 2, late_failure))

    def no_first_skip(value, ring, q, dimension, radix_power):
        for _ in radix_power(ring, q):
            for _ in range(dimension * dimension):
                value.multiply_small(q)

    def missed_M(value, ring, q, dimension, radix_power):
        first = True
        for _ in radix_power(ring, q):
            if first:
                first = False
            else:
                value.multiply_small(q)

    def wrong_multiplier(value, ring, q, dimension, radix_power):
        first = True
        for _ in radix_power(ring, q):
            if first:
                first = False
            else:
                for _ in range(dimension * dimension):
                    value.multiply_small(q + 1)

    def missing_one_coordinate(value, ring, q, dimension, radix_power):
        first = True
        for _ in radix_power(ring, q):
            if first:
                first = False
            else:
                for _ in range(dimension * dimension - 1):
                    value.multiply_small(q)

    for name, mutant in (
        ('missing first-yield skip', no_first_skip),
        ('missed d-squared multiplier count', missed_M),
        ('wrong q multiplier', wrong_multiplier),
        ('omitted one coordinate multiplier', missing_one_coordinate),
    ):
        with candidate(subject, mutant):
            controls.rejects(name, lambda: subject.run_case(config, candidate=True))

    cap_one = dict(name='test_complete_radix_cap1', d=2, q=3, w=1, B=1, h=0, Q=4, I=3)

    def no_radix(value, ring, q, dimension, radix_power):
        return

    def incomplete_radix(value, ring, q, dimension, radix_power):
        iterator = radix_power(ring, q)
        next(iterator)
        iterator.close()

    for name, mutant in (
        ('all radix validation skipped despite cap1 output match', no_radix),
        ('final radix validation skipped despite cap1 output match', incomplete_radix),
    ):
        with candidate(subject, mutant):
            controls.rejects(name, lambda: subject.run_case(cap_one, candidate=True))

    # Successful valid inputs contain physically repeated empty prefixes. B is
    # still a multiplicity even though the borrowed old tape has no body bytes.
    repeated = dict(name='duplicate_empty_prefix', d=1, q=3, w=2, B=3, h=0, Q=4, I=3)
    original = subject.run_case(repeated)
    shared = subject.run_case(repeated, candidate=True)
    need(original['geometry']['old_body'] == 0 and original['returned_prefix_count'] == 9,
         'empty-prefix physical multiplicity was collapsed')
    need(original['output_sha256'] == shared['output_sha256'] and shared['returned_prefix_count'] == 9,
         'candidate changed duplicate-empty-prefix enumeration')
    positives.append('B=3 empty-prefix physical multiplicity on original and shared producer')

    original_shared = subject.high_power_shared

    def corrupt_one(value, ring, q, dimension, radix_power):
        original_shared(value, ring, q, dimension, radix_power)
        ring.one.cells[1] ^= 1

    def move_one_head(value, ring, q, dimension, radix_power):
        original_shared(value, ring, q, dimension, radix_power)
        ring.one.head = 2

    def corrupt_modulus(value, ring, q, dimension, radix_power):
        original_shared(value, ring, q, dimension, radix_power)
        ring.modulus.cells[1] ^= 1

    for name, mutant in (
        ('borrowed ring-one bytes changed', corrupt_one),
        ('borrowed ring-one head changed', move_one_head),
        ('borrowed modulus bytes changed', corrupt_modulus),
    ):
        with candidate(subject, mutant):
            controls.rejects(name, lambda: subject.run_case(config, candidate=True))

    def corrupt_returned_borrowed(selector, change):
        def install(_old, sources):
            producer = sources.directory.produce

            def altered(old, fields, old_count, code, context):
                result = producer(old, fields, old_count, code, context)
                change(selector(fields, context))
                return result

            sources.directory.produce = altered
        return install

    def spectator(arena):
        words = [arena.words[slot] for slot in arena.live if arena.words[slot].head == 2]
        need(len(words) == 1, 'expected one protected unrelated spectator at head2')
        return words[0]

    for name, selector, change in (
        ('borrowed field-count bytes changed', lambda fields, context: fields,
         lambda word: word.cells.__setitem__(1, word.cells[1] ^ 1)),
        ('borrowed Context-highs bytes changed', lambda fields, context: context.highs.tape,
         lambda tape: tape.cells.__setitem__(1, tape.cells[1] ^ 1)),
        ('borrowed cap head changed', lambda fields, context: context.cap,
         lambda word: setattr(word, 'head', 2)),
        ('unrelated residue spectator bytes changed', lambda fields, context: spectator(context.arena),
         lambda word: word.cells.__setitem__(1, word.cells[1] ^ 1)),
        ('unrelated index spectator bytes changed', lambda fields, context: spectator(fields.arena),
         lambda word: word.cells.__setitem__(1, word.cells[1] ^ 1)),
        ('borrowed Context-highs head changed', lambda fields, context: context.highs.tape,
         lambda tape: setattr(tape, 'head', 2)),
        ('protected residue template head changed', lambda fields, context: context.arena.template,
         lambda word: setattr(word, 'head', 2)),
    ):
        controls.rejects(name, lambda selector=selector, change=change:
                         subject.run_case(config, candidate=True,
                                          alter_old=corrupt_returned_borrowed(selector, change)))

    controls.rejects('boolean candidate flag', lambda: subject.run_case(config, candidate=1))
    bad_config = deepcopy(config)
    bad_config['d'] = True
    controls.rejects('boolean dimension', lambda: subject.run_case(bad_config))

    # Receipt and byte-authentication checks use a fresh writable copy, so this
    # suite also runs against a read-only exported package.
    with tempfile.TemporaryDirectory(prefix='directory-invoice-negative-') as directory:
        fixture = Path(directory) / 'package'
        writable_copy(root, fixture)
        baseline = run_cli(fixture)
        need(baseline.returncode == 0 and 'PASS_DIRECTORY_PRODUCER_COMPONENT' in baseline.stdout,
             'unaltered copied CLI fixture failed: ' + baseline.stderr[-500:])
        positives.append('unaltered complete typed receipt accepted by copied CLI')
        marker = Path(directory) / 'source-was-executed'
        source = fixture / 'source/words.py'
        raw = source.read_bytes()
        source.write_bytes(raw + ('\nopen(' + repr(str(marker)) + ', "w").write("executed")\n').encode())
        controls.cli_rejects('source bytes authenticated before execution', fixture)
        need(not marker.exists(), 'tampered source was executed before authentication')
        source.write_bytes(raw)
        sibling = Path(directory) / 'same-words.py'
        sibling.write_bytes(raw)
        source.unlink()
        source.symlink_to(sibling)
        controls.cli_rejects('symlink source substitution', fixture)
        source.unlink()
        source.write_bytes(raw)

        receipt = fixture / 'RESULT.json'
        receipt_bytes = receipt.read_bytes()
        data = json.loads(receipt_bytes)
        forged = deepcopy(data)
        forged['schema_version'] = True
        receipt.write_text(json.dumps(forged) + '\n')
        controls.cli_rejects('boolean receipt schema', fixture)
        receipt.write_text('{"schema_version":1,"schema_version":1,"cases":' + json.dumps(data['cases'])
                           + ',"scope":' + json.dumps(data['scope']) + '}\n')
        controls.cli_rejects('duplicate receipt JSON key', fixture)
        forged = deepcopy(data)
        forged['cases'][1]['saved_residue_actions']['reads'] -= 1
        receipt.write_text(json.dumps(forged) + '\n')
        controls.cli_rejects('undercounted complete d-squared-minus-one saving', fixture)

    need(tree_bytes(root) == before, 'the package under test changed')
    print('PASS_DIRECTORY_INVOICE_TESTS ' + json.dumps(
        {'positive_controls': len(positives), 'expected_rejections': len(controls.rejected),
         'positive_names': positives, 'rejection_names': controls.rejected,
         'package_bytes_unchanged': True, 'optimized': not __debug__}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except TestFailure as error:
        raise SystemExit('FAIL_DIRECTORY_INVOICE_TESTS ' + str(error))
