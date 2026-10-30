#!/usr/bin/env python3
"""Replay the corrected continuation in a private, manifest-complete worktree.

The standard-library default freshly checks exact finite certificates and
authenticates source-bound expensive execution receipts. --full-native reruns
the native catalogue, complete symbolic word and controlled physical fixture.
Neither mode proves the inherited all-size theorem or executes a full GL64
payload. Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCOPE = HERE.relative_to(ROOT)
WORD = SCOPE/'bit-word/early-birth-prefixes/WORD.json.gz'
WORD_SHA = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'
RECORD_SHA = '91d74ab960e882aa7f5236265c3f4427735c4b8019f509758a33a238c05901fe'
LOCAL_PROFILE = {'1': 1330, '2': 1327, '3': 79, '4': 49, '5': 90, '6': 20, '7': 18}
GLOBAL_PROFILE = {'1': 418950, '2': 433104, '3': 24885, '4': 30975,
                  '5': 28350, '6': 21840, '7': 28980, '42': 441}
LOWER = '0.001738137188329345368427'
UPPER = '0.001738137188329345368428'
EXPENSIVE = ('FINAL-NATIVE-REVIEW.json', 'FINAL-WHOLE-WORD.json',
             'FINAL-PHYSICAL-BINDING.json', 'FINAL-PHYSICAL-PROBE.json',
             'FINAL-NATIVE-EXECUTION.json')


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    need(path.is_file() and not path.is_symlink(), 'regular file required: '+str(path))
    h = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def relative(name):
    need(isinstance(name, str) and name, 'nonempty relative filename')
    path = Path(name)
    need(not path.is_absolute() and '..' not in path.parts and path.as_posix() == name,
         'normalized relative filename: '+repr(name))
    return path


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')


def load_builder():
    spec = importlib.util.spec_from_file_location('corrected_release_manifest', HERE/'build_manifest.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def semantic(receipt, name):
    """Only these explicitly identified execution metadata are nonsemantic."""
    result = deepcopy(receipt)
    if name == 'FINAL-WHOLE-WORD.json':
        result.pop('elapsed_seconds', None)
    elif name == 'FINAL-NATIVE-EXECUTION.json':
        for step in result['steps']:
            for key in ('argv', 'elapsed_seconds', 'log', 'log_sha256'):
                step.pop(key, None)
    return result


class Replay:
    def __init__(self, output, manifest, mode):
        self.output = output
        self.work = output/'worktree'
        self.manifest = manifest
        self.mode = mode
        self.steps = []
        self.pins = {}
        self.expected = {}
        self.logs = output/'logs'
        self.logs.mkdir()
        self.work.mkdir()
        entries = {str(SCOPE/relative(name)): value for name, value in manifest['files'].items()}
        for name, value in manifest['repository_dependencies'].items():
            need(name not in entries, 'disjoint manifest entries')
            entries[str(relative(name))] = value
        self.declared = entries
        for name, expected in sorted(entries.items()):
            source, target = ROOT/relative(name), self.work/relative(name)
            need(source.stat().st_size == expected['bytes'] and digest(source) == expected['sha256'],
                 'authenticated copy input: '+name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            need(digest(target) == expected['sha256'], 'authenticated private copy: '+name)
        shutil.copyfile(HERE/'MANIFEST.json', self.work/SCOPE/'MANIFEST.json')
        self.pins.update({name: value['sha256'] for name, value in entries.items()})
        write(output/'SOURCE-PINS.json', {'scope': manifest['scope'], 'files': entries})
        for row in read(self.work/SCOPE/'bit-geometry/REPLAY-INPUTS.json')['input_files']:
            name = str(relative(row['path']))
            need(name in entries and entries[name] == {'bytes': row['bytes'], 'sha256': row['sha256']},
                 'declared geometry replay dependency: '+name)

    def source_pins(self, receipt):
        for key in ('source_sha256', 'dependency_sha256'):
            rows = receipt.get(key, {})
            need(isinstance(rows, dict), 'repository-relative receipt pin map: '+key)
            for name, expected in rows.items():
                name = str(relative(name))
                need(name in self.declared and digest(self.work/name) == expected,
                     'source-bound receipt pin: '+name)

    def run(self, label, script, args=(), receipts=()):
        script = relative(str(script))
        need(str(script) in self.declared, 'declared replay program: '+str(script))
        command = [sys.executable, '-B', str(self.work/script), *map(str, args)]
        log = self.logs/(label+'.log')
        started = time.monotonic()
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        environment.pop('PYTHONPATH', None)
        print('RUN '+label, flush=True)
        with log.open('wb') as stream:
            process = subprocess.run(command, cwd=self.work, env=environment, stdout=stream, stderr=subprocess.STDOUT)
        row = {'label': label, 'argv': command, 'script_sha256': digest(self.work/script),
               'exit_code': process.returncode, 'elapsed_seconds': time.monotonic()-started,
               'log': str(log.relative_to(self.output)), 'log_sha256': digest(log), 'receipts': []}
        self.steps.append(row)
        need(process.returncode == 0, label+' failed; see '+str(log))
        for current, original in receipts:
            current = Path(current)
            original = relative(str(original))
            expected = read(ROOT/original)
            actual = read(current)
            need(actual == expected, 'exact JSON receipt mismatch: '+str(original))
            row['receipts'].append({'path': str(current.relative_to(self.output)),
                                    'reference': str(original), 'sha256': digest(current),
                                    'comparison': 'exact JSON; no fields omitted'})
        return row

    def fixed(self, label, script, output, args=()):
        script, output = SCOPE/script, SCOPE/output
        return self.run(label, script, args, [(self.work/output, output)])

    def local(self):
        native = Path('research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018')
        word = self.work/WORD
        payload = json.loads(gzip.decompress(word.read_bytes()))
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
        need(sha256(canonical).hexdigest() == WORD_SHA, 'exact final canonical word')
        baseline = json.loads(gzip.decompress((self.work/'research/kappa-next-regime/word-search/candidate/WORD.json.gz').read_bytes()))
        for key in ('v', 'R', 'h', 'start', 'final', 'ret', 'scatter', 'coords', 'lines', 'ports_geom', 'form'):
            need(payload[key] == baseline[key], 'retained local interface: '+key)
        need((payload['v'], payload['R'], payload['h']) == (111, 437, 8), 'exact word inventory')
        self.run('final-local-word', native/'vendor/xcheck_p.py', [word])
        local = self.output/'native-local'
        local.mkdir()
        self.run('final-native-export', native/'vendor/export_records.py', [word, local/'records'])
        for name in ('249-records.bin', '249-states.json', 'frames.json'):
            reference = self.work/SCOPE/'bit-word/early-birth-prefixes/records'/name
            need((local/'records'/name).read_bytes() == reference.read_bytes(), 'native record equality: '+name)
        need(digest(local/'records/249-records.bin') == RECORD_SHA, 'final record binary pin')
        pairs = [(local/'cout'/name, SCOPE/'bit-word/early-birth-prefixes/cout'/name)
                 for name in ('columns.json', 'legality.json')]
        self.run('final-local-881-columns', native/'code/local_counter.py', [local], pairs)
        leg, col = read(local/'cout/legality.json'), read(local/'cout/columns.json')
        need(leg['paid_histogram'] == LOCAL_PROFILE and leg['records'] == 26711, 'actual final local profile')
        need(col['formal_columns_checked'] == 881 and col['forward_l1'] == 49281 and col['reverse_l1'] == 1052208,
             'actual arbitrary dirty columns and both prefix bounds')

    def core(self):
        self.local()
        for name, receipt in (
            ('geometry_budget.py', 'GEOMETRY-BUDGET.json'),
            ('verify_clock_reductions.py', 'CLOCK-REDUCTIONS-CHECK.json'),
            ('verify_packing_duals.py', 'PACKING-DUALS-CHECK.json'),
            ('review_bit_checkpoint.py', 'BIT-CHECKPOINT-INDEPENDENT-REVIEW.json'),
            ('review_retimed444.py', 'BIT-RETIMED444-INDEPENDENT-REVIEW.json'),
            ('review_final_bit_word.py', 'BIT-FINAL-INDEPENDENT-REVIEW.json'),
            ('reprice_achieved_clock.py', 'ACHIEVED-BIT-CLOCK-REPRICE.json'),
            ('final_entrance_closure.py', 'FINAL-ENTRANCE-CLOSURE.json'),
            ('larger_pair_budget.py', 'LARGER-PAIR-BUDGET.json')):
            self.fixed(Path(name).stem, Path('bit-geometry')/name, Path('bit-geometry')/receipt)
        for name, receipt in (('slot_projector_rigidity.py', 'SLOT-PROJECTOR-RIGIDITY.json'),
                              ('cellmap_invariance.py', 'CELLMAP-INVARIANCE.json')):
            destination = self.work/SCOPE/'complex'/receipt
            self.fixed(Path(name).stem, Path('complex')/name, Path('complex')/receipt,
                       ['--output', destination])
        self.fixed('independent-operator-witness', Path('operator-audit/independent_witness.py'),
                   Path('operator-audit/INDEPENDENT-WITNESS.json'))
        self.fixed('independent-slot-rigidity', Path('operator-audit/review_rigidity.py'),
                   Path('operator-audit/RIGIDITY-REVIEW.json'))
        witness = read(self.work/SCOPE/'operator-audit/INDEPENDENT-WITNESS.json')
        need(witness['status'] == 'PASS_INDEPENDENT_COUNTEREXAMPLE' and
             witness['prior_complex_claim_supported'] is False and witness['new_kappa'] is False,
             'corrected previous complex claim')

    def expensive(self, fresh):
        directory = SCOPE/'bit-integration'
        retained = {name: read(ROOT/directory/name) for name in EXPENSIVE}
        for receipt in retained.values():
            self.source_pins(receipt)
        if fresh:
            # These are the only deletions. Every target is under the private copy.
            copied_logs = self.work/directory/'final-native-logs'
            need(copied_logs.is_relative_to(self.work), 'private log deletion')
            if copied_logs.exists():
                shutil.rmtree(copied_logs)
            for name in (*EXPENSIVE, 'final_physical_probe.py'):
                target = self.work/directory/name
                need(target.is_relative_to(self.work), 'private generated receipt deletion')
                target.unlink()
            self.run('full-native-symbolic-and-controlled-physical', SCOPE/'run_final_native.py')
        observed = {name: read(self.work/directory/name) for name in EXPENSIVE}
        for name, receipt in observed.items():
            self.source_pins(receipt)
            need(semantic(receipt, name) == semantic(retained[name], name), 'expensive semantic receipt: '+name)
        native, whole, physical, execution = (observed[name] for name in (
            'FINAL-NATIVE-REVIEW.json', 'FINAL-WHOLE-WORD.json', 'FINAL-PHYSICAL-PROBE.json',
            'FINAL-NATIVE-EXECUTION.json'))
        need(native['status'] == 'PASS_REPLICA_INDEXED_NATIVE_REQUEST_CATALOGUE', 'native acceptance')
        need(whole['status'] == 'PASS_REPLICA_INDEXED_COMPLETE_SYMBOLIC_WORD', 'whole-word acceptance')
        need(physical['status'] == 'PASS_ACTUAL_T35_FINAL_EARLY_BIRTH_NESTED_PHYSICAL_PROTOCOL', 'physical fixture acceptance')
        need(execution['status'] == 'PASS_FINAL_NATIVE_SYMBOLIC_AND_CONTROLLED_PHYSICAL_EXECUTION', 'execution chain acceptance')
        need(native['actual_word_content_sha256'] == whole['native_binding']['actual_word_content_sha256'] ==
             physical['word_content_sha256'] == execution['word_content_sha256'] == WORD_SHA, 'all execution word bindings')
        need(native['binding_sha256'] == whole['native_binding']['binding_sha256'] ==
             physical['catalogue']['binding_sha256'] == execution['binding_sha256'], 'one catalogue binding')
        need(native['canonical_requests'] == whole['complete']['residuals'] == 987525, 'complete actual request count')
        need(native['rank_histogram'] == GLOBAL_PROFILE, 'complete native rank profile')
        need(whole['complete']['complete_xor_count'] == 7563465 and whole['complete']['checkpoints'] == 29,
             'complete symbolic execution scope')
        need(native['full_GL64_payload_executed'] is False and physical['complete_GL64_payload_executed'] is False,
             'explicit absence of full GL64 physical execution')
        need(physical['controlled_payload_bits'] == 46 and physical['stock_is_controlled_fixture'] is True,
             'controlled physical fixture scope')
        need(whole['physical_payload_executed'] is False and whole['primitive_contracts_proved'] is False,
             'symbolic execution and inherited primitive distinction')
        expected_scripts = {
            'native-catalogue': Path('research/kappa-next-regime/native-catalogue/review.py'),
            'complete-symbolic-word': Path('research/kappa-next-regime/native-catalogue/whole_word.py'),
            'bind-physical-fixture': SCOPE/'build_final_physical.py',
            'physical-fixture': directory/'final_physical_probe.py'}
        need(len(execution['steps']) == len(expected_scripts), 'complete four-step execution record')
        seen = set()
        for step in execution['steps']:
            label = step['label']
            need(label in expected_scripts and label not in seen and step['exit_code'] == 0, 'unique successful execution step')
            seen.add(label)
            need(digest(self.work/expected_scripts[label]) == step['script_sha256'], 'execution program pin: '+label)
            need(digest(self.work/relative(step['log'])) == step['log_sha256'], 'execution log pin: '+label)
        return {'mode': 'fresh full replay' if fresh else 'source-bound expensive receipt reuse; not freshly executed',
                'receipts': {name: digest(self.work/directory/name) for name in EXPENSIVE},
                'binding_sha256': native['binding_sha256'], 'requests': 987525,
                'complete_symbolic_XORs': 7563465, 'controlled_physical_payload_bits': 46,
                'complete_GL64_payload_executed': False,
                'semantic_comparison_omissions': {'FINAL-WHOLE-WORD.json': ['elapsed_seconds'],
                    'FINAL-NATIVE-EXECUTION.json': ['steps[*].argv', 'steps[*].elapsed_seconds',
                                                   'steps[*].log', 'steps[*].log_sha256']}}

    def public_operator_reuse(self):
        base = self.work/SCOPE/'operator-audit'
        receipt, stage = read(base/'FRESH-REPLAY.json'), read(base/'STAGE.json')
        need(receipt['status'] == 'PASS_FRESH_PUBLIC_OPERATOR_AUDIT' and receipt['exit_code'] == 0,
             'retained public operator audit execution')
        need(digest(base/'STAGE.json') == receipt['stage_receipt_sha256'], 'operator audit stage binding')
        verifier = base/'checkout/research/pr3934-pr3955-operator-replay/verify.py'
        need(digest(verifier) == receipt['verifier_sha256'], 'operator audit verifier binding')
        for row in stage['files']:
            filename = SCOPE/'operator-audit/checkout'/relative(row['path'])
            need(str(filename) in self.declared, 'declared staged operator source')
            path = self.work/filename
            need(path.stat().st_size == row['bytes'] and digest(path) == row['sha256'],
                 'staged operator source binding: '+row['path'])
        need('hosted_receiver_moves=2374 changed=2374' in receipt['stdout'] and
             'pr3955_owner0_identity_ports=55 changed=55' in receipt['stdout'], 'operator audit coverage')
        return {'mode': 'source-bound reuse of actual earlier-in-session unchanged public audit; not freshly executed',
                'receipt_sha256': digest(base/'FRESH-REPLAY.json'), 'stage_sha256': digest(base/'STAGE.json'),
                'verifier_sha256': digest(verifier), 'staged_files_checked': len(stage['files']),
                'hosted_receiver_moves_checked': 2374, 'owner_zero_identity_ports_checked': 55,
                'fresh_default_complement': 'independent dense Gaussian-integer witness against actual previous MOVES'}

    def claim(self):
        claim = read(self.work/SCOPE/'CLAIM.json')
        need(claim['target_reached'] is False and claim['prior_complex_claim']['supported'] is False,
             'corrected target and prior-complex claim status')
        bit = claim['bit_supplier']
        need(bit['word_content_sha256'] == WORD_SHA and bit['lower_decimal'] == LOWER and bit['upper_decimal'] == UPPER,
             'claim binds the exact final BIT bracket')
        invoice = read(self.work/SCOPE/'bit-integration/early-birth-prefixes/RESULT.json')
        self.source_pins(invoice)
        need(invoice['word_content_sha256'] == WORD_SHA and invoice['local_profile'] == LOCAL_PROFILE and
             invoice['profile'] == GLOBAL_PROFILE and invoice['paid_requests'] == 987525, 'complete final invoice profile')
        need(Fraction(invoice['bit_endpoint_lower']) == Fraction(LOWER) and
             Fraction(invoice['bit_endpoint_upper']) == Fraction(UPPER) < Fraction('0.001745'), 'exact final BIT endpoints')
        return claim


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='absolute, fresh directory outside the source repository')
    parser.add_argument('--full-native', action='store_true',
                        help='rerun full native catalogue, symbolic word and controlled physical fixture in the copy')
    parser.add_argument('--complex-controller-review', action='store_true',
                        help='also rerun the optional controller review; requires installed NumPy and SciPy')
    args = parser.parse_args()
    need(sys.version_info >= (3, 11) and __debug__, 'Python >=3.11 with assertions enabled')
    need(args.output.is_absolute(), '--output must be absolute')
    output = args.output.resolve()
    need(not output.exists() and not output.is_relative_to(ROOT) and not ROOT.is_relative_to(output),
         '--output must be fresh and outside the source repository')
    builder = load_builder()
    manifest_check = builder.check()
    manifest = read(HERE/'MANIFEST.json')
    mode = ('FRESH_CORE_AND_FULL_NATIVE_SYMBOLIC_CONTROLLED_PHYSICAL' if args.full_native else
            'FRESH_STDLIB_CORE_WITH_SOURCE_BOUND_EXPENSIVE_REUSE')
    output.mkdir(parents=True)
    replay = None
    result = {'status': 'RUNNING', 'mode': mode, **manifest_check,
              'python': sys.version, 'source_repository_read_only': True,
              'full_GL64_payload_executed': False, 'all_size_theorem_proved': False}
    try:
        replay = Replay(output, manifest, mode)
        replay.core()
        if args.complex_controller_review:
            destination = replay.work/SCOPE/'complex-controller/REVIEW.json'
            replay.fixed('optional-complex-controller-review', Path('complex-controller/review.py'),
                         Path('complex-controller/REVIEW.json'), ['--output', destination])
            optional = 'fresh exact receipt comparison; installed NumPy/SciPy imports required'
        else:
            controller = read(replay.work/SCOPE/'complex-controller/REVIEW.json')
            replay.source_pins(controller)
            need(controller['new_controller_admitted'] is False and controller['new_kappa_claimed'] is False,
                 'retained controller review admits no new construction')
            optional = 'source-bound retained review; optional NumPy/SciPy checker not executed'
        result['expensive_execution'] = replay.expensive(args.full_native)
        result['public_operator_audit'] = replay.public_operator_reuse()
        claim = replay.claim()
        need(builder.check() == manifest_check, 'source repository unchanged after isolated replay')
        result.update(status='PASS_CORRECTED_CONTINUATION_PORTABLE_REPLAY', steps=replay.steps,
                      claim_sha256=digest(HERE/'CLAIM.json'), claim=claim,
                      optional_complex_controller_review=optional,
                      discovery_searches_rerun=False,
                      archived_K4_orbit_census_rerun=False,
                      final_fixed_word_entrance_certificate_fresh=True,
                      exact_final_word_content_sha256=WORD_SHA,
                      final_local_profile=LOCAL_PROFILE, final_global_profile=GLOBAL_PROFILE,
                      source_pins='SOURCE-PINS.json',
                      scope='Fresh finite exact checks plus explicitly identified execution mode. Prior high complex claim rejected. Inherited primitive, source, precision and all-size assumptions remain; no full GL64 physical payload execution.')
    except Exception as error:
        result.update(status='FAIL_CORRECTED_CONTINUATION_PORTABLE_REPLAY', error=repr(error),
                      steps=[] if replay is None else replay.steps)
        write(output/'VALIDATION.json', result)
        raise
    write(output/'VALIDATION.json', result)
    print(json.dumps({'status': result['status'], 'mode': mode,
                      'validation': str(output/'VALIDATION.json'), **manifest_check}, sort_keys=True))


if __name__ == '__main__':
    main()
