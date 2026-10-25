#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded API and CLI controls for the many-axis prime-supply package.

Exercises host-reference construction and the authenticated production predicate
adapter. It does not establish the external analytic prime estimate, formalize
the uniform tape construction, or claim encoded execution.
"""
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
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file()}


def load_subject(root):
    spec = importlib.util.spec_from_file_location('many_axis_prime_subject', root / 'verify.py')
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    return subject


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

    def cli_rejects(self, name, root, contains=None):
        result = run_cli(root)
        need(result.returncode != 0, name + ' CLI accepted the altered fixture')
        need('FAIL' in result.stderr, name + ' CLI did not report an explicit validation failure: ' + result.stderr[-500:])
        if contains is not None:
            need(contains in result.stderr, name + ' failed through the wrong validation path: ' + result.stderr[-500:])
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
    guard = subject.source_guard()
    need(guard.__code__.co_filename == 'authenticated TensorPlan.production_axis',
         'guard was not compiled from the authenticated selected source method')
    fixture = subject.supplies(12, (0, 1, 1), guard=guard)
    primes = list(fixture['primes'])
    need(fixture['D'] == 3 and fixture['d'] == 4 and fixture['source_guard_checks'] == 3,
         'actual source dimension d=D+1 was not used for all axes')
    need(fixture['source_bit_length'] == 36 and fixture['flag_bit_length'] == 2,
         'source words or implicit final full-axis flag count changed')
    need(3 * fixture['S'] > 2 * fixture['T'] and fixture['S'] < fixture['T'],
         'source product does not occupy the claimed target-volume fraction')
    need(fixture['encoded_execution'] is False and fixture['production_tensor_execution'] is False,
         'host reference incorrectly claimed encoded execution')
    positives.append('D=3 mixed-axis source words, final-axis flags, volume and authenticated source guard')

    def explicit_control(name, change_primes=None, flags=(0, 1, 1)):
        supplied = primes.copy()
        if change_primes is not None:
            change_primes(supplied)
        controls.rejects(name, lambda: subject.validate_supplied(12, flags, supplied, guard=guard))

    explicit_control('same-target duplicate primes', lambda p: p.__setitem__(2, p[1]))
    explicit_control('mixed-target duplicate primes', lambda p: p.__setitem__(0, p[1]))
    explicit_control('in-band odd composite 1881', lambda p: p.__setitem__(0, 1881))
    explicit_control('in-band even source 1880', lambda p: p.__setitem__(0, 1880))
    explicit_control('power-of-two source length', lambda p: p.__setitem__(0, 1024))
    explicit_control('source prime two', lambda p: p.__setitem__(0, 2))
    explicit_control('boolean source prime', lambda p: p.__setitem__(0, True))
    explicit_control('floating source prime', lambda p: p.__setitem__(0, float(p[0])))
    explicit_control('source axis order swapped', lambda p: p.__setitem__(slice(0, 2), [p[1], p[0]]))
    explicit_control('source flag order swapped', flags=(1, 0, 1))
    explicit_control('missing source axis', lambda p: p.pop())
    explicit_control('extra source axis', lambda p: p.append(p[-1]))
    explicit_control('missing final full target axis', flags=(0, 1, 0))
    explicit_control('boolean target flag', flags=(0, True, 1))
    explicit_control('target flag outside literal alphabet', flags=(0, 2, 1))

    for name, ell, flags in (
        ('boolean fixture exponent', True, (1,)),
        ('fixture exponent below domain', 2, (1,)),
        ('giant symbolic threshold sent to bounded constructor', subject.ELL0, (1,)),
        ('empty target flag stream', 12, ()),
    ):
        controls.rejects(name, lambda ell=ell, flags=flags: subject.supplies(ell, flags, guard=guard))
    controls.rejects('boolean target halo', lambda: subject.supplies(12, (0, 1, 1), True, 2, guard))
    controls.rejects('negative target halo', lambda: subject.supplies(12, (0, 1, 1), -1, 2, guard))
    controls.rejects('boolean period width', lambda: subject.supplies(12, (0, 1, 1), 16, False, guard))
    controls.rejects('boolean prime quota', lambda: subject.prime_queue(4096, 4, True))
    controls.rejects('boolean interval dimension', lambda: subject.interval(4096, True))
    controls.rejects('insufficient finite supply is not asymptotic admission',
                     lambda: subject.supplies(4, (0, 1, 1), guard=guard))

    # Equality must fail the literal source's strict predicates. These isolate
    # lower, upper and period comparisons with the other numeric guards slack.
    controls.rejects('strict lower source ratio at equality',
                     lambda: subject.check_source_axis(8, 9, 2, 0, 0, guard))
    controls.rejects('strict upper source ratio at equality',
                     lambda: subject.check_source_axis(3, 4, 2, 0, 0, guard))
    controls.rejects('strict source period at equality',
                     lambda: subject.check_source_axis(14, 16, 2, 3, 2, guard))
    need(subject.check_source_axis(1913, 2048, 4, guard=guard), 'valid d=D+1 source guard failed')
    controls.rejects('using D instead of D+1 fails an actual source ratio',
                     lambda: subject.check_source_axis(1913, 2048, 3, guard=guard))

    for name, args in (
        ('boolean source dimension before ownership allocation', (1913, 2048, True, 16, 2)),
        ('negative source period before ownership allocation', (1913, 2048, 4, 16, -1)),
    ):
        controls.rejects(name, lambda args=args: subject.check_source_axis(*args, guard=guard))
        need(not subject.Natural.live, 'invalid operand leaked modeled ownership')

    def corrupt_dimension(model, _s, _t):
        model.d.value += 1

    controls.rejects('modeled borrowed dimension changed by guard',
                     lambda: subject.check_source_axis(1913, 2048, 4, guard=corrupt_dimension))
    need(not subject.Natural.live, 'rejected guard left modeled scratch live')
    positives.append('literal strict source predicates and modeled ownership restoration')

    reordered = subject.supplies(12, (1, 0, 1), guard=guard)
    need(reordered['S'] == fixture['S'] and reordered['T'] == fixture['T']
         and reordered['flag_bits_sha256'] != fixture['flag_bits_sha256']
         and reordered['source_bits_sha256'] != fixture['source_bits_sha256'],
         'axis order was collapsed to unordered products')
    positives.append('ordered flag/source streams distinguish equal-product axis orders')

    threshold = subject.threshold_certificate()
    need(type(threshold['ell0']) is int and threshold['ell0'] == 1 << 32
         and threshold['dimension_power'] == 334 and threshold['giant_power_constructed'] is False,
         'symbolic threshold domain or no-giant-power scope changed')
    ell = threshold['ell0']
    maximal_d = ell ** threshold['dimension_power']
    need(ell < 8 * maximal_d, 'new many-axis domain unexpectedly implies obsolete log(t)>8d shortcut')
    need(threshold['analytic_input_imported'] is True and threshold['analytic_input_reproved'] is False,
         'external analytic input was represented as a finite proof')
    positives.append('symbolic cutoff without giant powers; obsolete HH shortcut fails at admitted maximal dimension')

    # A fresh copied fixture can be writable even when the submitted export is
    # read-only; no byte or permission of the package under test is changed.
    with tempfile.TemporaryDirectory(prefix='many-axis-prime-negative-') as directory:
        copied = Path(directory) / 'package'
        writable_copy(root, copied)
        baseline = run_cli(copied)
        need(baseline.returncode == 0 and 'PASS_MANY_AXIS_PRIME_SUPPLY' in baseline.stdout,
             'unaltered copied CLI fixture failed: ' + baseline.stderr[-500:])
        positives.append('unaltered complete typed CLI receipt accepted')

        source_path = copied / 'source/PR3935-tensor_plan.py'
        source_bytes = source_path.read_bytes()
        source_path.write_bytes(source_bytes + b'\ninvalid python !\n')
        controls.cli_rejects('source authentication precedes AST parsing', copied, 'source bytes:')
        source_path.write_bytes(source_bytes)
        sibling = Path(directory) / 'same-tensor-plan.py'
        sibling.write_bytes(source_bytes)
        source_path.unlink()
        source_path.symlink_to(sibling)
        controls.cli_rejects('source symlink substitution', copied, 'source symlink:')
        source_path.unlink()
        source_path.write_bytes(source_bytes)

        receipt_path = copied / 'RESULT.json'
        original_receipt = receipt_path.read_bytes()
        receipt = json.loads(original_receipt)

        def receipt_control(name, change):
            forged = deepcopy(receipt)
            change(forged)
            receipt_path.write_text(json.dumps(forged) + '\n')
            controls.cli_rejects(name, copied, 'complete typed receipt')

        receipt_control('boolean root schema', lambda r: r.__setitem__('schema_version', True))
        receipt_control('integer false encoded-execution flag', lambda r: r.__setitem__('encoded_execution', 0))
        receipt_control('wrong D instead of D+1 receipt', lambda r: r['cases'][1].__setitem__('d', 3))
        receipt_control('wrong spectator flag count', lambda r: r['cases'][1].__setitem__('flag_bit_length', 3))
        receipt_control('missing encoded source-word volume', lambda r: r['cases'][1].__setitem__('source_bit_length', 24))
        receipt_control('false full source product volume', lambda r: r['cases'][1].__setitem__('S', 1))
        receipt_control('wrong axis flag order hash', lambda r: r['cases'][1].__setitem__('flag_bits_sha256', '0' * 64))
        receipt_control('boolean symbolic cutoff', lambda r: r['threshold'].__setitem__('ell0', True))
        receipt_control('clamped symbolic cutoff outside proved domain', lambda r: r['threshold'].__setitem__('ell0', 20))
        receipt_control('changed symbolic dimension domain', lambda r: r['threshold'].__setitem__('dimension_power', 335))
        receipt_control('obsolete log-t-greater-than-8d analytic premise',
                        lambda r: r['threshold'].__setitem__('FKS_reference', 'HH log(t)>8d shortcut'))
        receipt_control('external analytic premise misreported as reproved',
                        lambda r: r['threshold'].__setitem__('analytic_input_reproved', True))
        receipt_control('giant threshold power misreported as constructed',
                        lambda r: r['threshold'].__setitem__('giant_power_constructed', True))
        receipt_control('unsupported new kappa claim', lambda r: r.__setitem__('new_kappa', True))
        receipt_control('unrecognized receipt key', lambda r: r.__setitem__('all_obligations_closed', True))
        serialized = json.dumps(receipt)
        receipt_path.write_text('{"schema_version":1,' + serialized[1:] + '\n')
        controls.cli_rejects('duplicate receipt JSON key', copied, 'duplicate JSON key')
        receipt_path.write_bytes(original_receipt)

    need(tree_bytes(root) == before, 'the package under test changed')
    print('PASS_MANY_AXIS_PRIME_SUPPLY_TESTS ' + json.dumps(
        {'positive_controls': len(positives), 'expected_rejections': len(controls.rejected),
         'positive_names': positives, 'rejection_names': controls.rejected,
         'package_bytes_unchanged': True, 'optimized': not __debug__}, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except TestFailure as error:
        raise SystemExit('FAIL_MANY_AXIS_PRIME_SUPPLY_TESTS ' + str(error))
