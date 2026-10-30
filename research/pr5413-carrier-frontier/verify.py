#!/usr/bin/env python3
"""Complete caller replay and changed-tuple carrier application.

Apache-2.0. Richard Hoekstra, with substantial OpenAI Codex assistance.
The unchanged source engines retain Chris R/Clear1nsight and their full lineage.
"""
import argparse
import copy
import difflib
import shutil
import subprocess
import sys
import tempfile
import types
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT/'research/coupled-helper-neutral-completion'
BINDINGS_SHA = 'ea8ea2ff3db043d33ec3f4ea84f9ab760950eea1768f8a5ee9db91d0abb840e3'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def local_module(name):
    path = HERE/(name+'.py')
    module = types.ModuleType('_carrier_'+name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True, optimize=0), module.__dict__)
    return module


F, A = local_module('frontier'), local_module('application')


def input_hashes():
    need(A.sha(SRC/'SOURCE-BINDINGS.json') == BINDINGS_SHA, 'fixed PR5413 capsule manifest')
    result = {}
    for row in A.load(HERE/'SOURCES.json')['files']:
        if row['usage'] == 'input':
            need(A.sha(ROOT/row['path']) == row['sha256'], 'live input changed: '+row['path'])
            result[row['path']] = row['sha256']
    return result


def precision_run(ws, manifest_path, output):
    fixed = ws/F.PRECISION/'V16-SOURCES-v3.json'
    original = fixed.read_bytes()
    try:
        fixed.write_bytes(manifest_path.read_bytes())
        return A.run_engine(SRC, ws, F.PRECISION+'check_carrier_precision.py',
                            ['--root', '.', '--output', F.PRECISION+output])
    finally:
        fixed.write_bytes(original)


def case_application(ws, case, first, proof_output=None):
    pdir, idir = ws/F.PRECISION, ws/F.INVOICE
    (ws/'carrier-frontier').mkdir(exist_ok=True)
    shutil.copyfile(SRC/'reports/expected/funding.json', ws/F.TEMPLATE)
    shutil.copyfile(HERE/'frontier.py', idir/'carrier_frontier.py')
    funding = F.certify(ws, case)
    A.dump(idir/'CARRIER-FUNDING.json', funding)
    original_checker = (pdir/'check_v16_precision_v3.py').read_text()
    (pdir/'check_carrier_precision.py').write_text(A.precision_source(original_checker))
    original_manifest = A.load(pdir/'V16-SOURCES-v3.json')
    conservativity = None
    volatile = {'seconds', 'checker_sha256', 'input_manifest_sha256'}
    if first:
        path = pdir/'ORIGINAL-SOURCES.json'
        path.write_bytes((pdir/'V16-SOURCES-v3.json').read_bytes())
        code, error = precision_run(ws, path, 'CONSERVATIVE-PRECISION.json')
        need(code == 0, 'precision conservativity: '+error[-1200:])
        received = A.load(pdir/'CONSERVATIVE-PRECISION.json')
        expected = A.load(SRC/'reports/expected/precision.json')
        need({k: v for k, v in received.items() if k not in volatile} ==
             {k: v for k, v in expected.items() if k not in volatile}, 'original precision payload preserved')
        conservativity = True
    proof, substitutions = A.proof_instance((pdir/'V16-APPLICATION-PROOF-v3.md').read_text(), case, funding)
    (pdir/'CARRIER-APPLICATION.md').write_text(proof)
    proof_sha = A.sha(pdir/'CARRIER-APPLICATION.md')
    pman = A.manifest(original_manifest,
        {'funding': F.INVOICE+'CARRIER-FUNDING.json', 'application_proof': F.PRECISION+'CARRIER-APPLICATION.md'}, ws)
    pman_path = pdir/'CARRIER-SOURCES.json'
    A.dump(pman_path, pman)
    code, error = precision_run(ws, pman_path, 'CARRIER-PRECISION.json')
    need(code == 0, 'changed-tuple precision: '+error[-1600:])
    precision = A.load(pdir/'CARRIER-PRECISION.json')
    need(precision['carrier_H'] == case['H'] and precision['carrier_j'] == case['j'] and
         Q(precision['carrier_gap']) == Q(funding['gap']) and
         precision['expanded']['strictified_log_upper'] == 572*case['v']+29 and
         precision['expanded']['D0'] == '2^1048576' and
         precision['mathematical_application']['proof_sha256'] == proof_sha,
         'fresh precision bound to tuple, proof and carrier')
    expected = A.load(SRC/'reports/expected/precision.json')
    allowed = volatile | {'carrier_H', 'carrier_j', 'carrier_gap', 'expanded', 'mathematical_application'}
    need({k: v for k, v in precision.items() if k not in allowed} ==
         {k: v for k, v in expected.items() if k not in allowed}, 'unchanged raw physical precision census')
    text, unchanged = A.closure_source((idir/'check_neutral_closure.py').read_text(), case, funding, proof_sha)
    (idir/'check_carrier_closure.py').write_text(text)
    if proof_output is not None:
        proof_output.mkdir(parents=True, exist_ok=True)
        artifacts = {'application.md': proof,
            'precision.patch': ''.join(difflib.unified_diff(original_checker.splitlines(keepends=True),
                (pdir/'check_carrier_precision.py').read_text().splitlines(keepends=True),
                fromfile='PR5413/check_v16_precision_v3.py', tofile='frontier/check_carrier_precision.py')),
            'conjunction.patch': ''.join(difflib.unified_diff((idir/'check_neutral_closure.py').read_text().splitlines(keepends=True),
                text.splitlines(keepends=True), fromfile='PR5413/check_neutral_closure.py', tofile='frontier/check_carrier_closure.py'))}
        for suffix, content in artifacts.items():
            target = proof_output/(case['name']+'-'+suffix)
            need(not target.exists() or target.read_text() == content, 'review output already differs: '+str(target))
            target.write_text(content)
    cman = A.manifest(A.load(idir/'NEUTRAL-CLOSURE-INPUTS-v1.json'), {
        'funding': F.INVOICE+'CARRIER-FUNDING.json', 'precision': F.PRECISION+'CARRIER-PRECISION.json',
        'precision_manifest': F.PRECISION+'CARRIER-SOURCES.json',
        'precision_proof': F.PRECISION+'CARRIER-APPLICATION.md'}, ws)
    cman['rows'].append({'id': 'carrier_funding_verifier', 'path': F.INVOICE+'carrier_frontier.py',
                         'sha256': A.sha(idir/'carrier_frontier.py')})
    A.dump(idir/'CARRIER-CLOSURE-SOURCES.json', cman)
    code, error = A.run_engine(SRC, ws, F.INVOICE+'check_carrier_closure.py',
        ['--root', '.', '--manifest', F.INVOICE+'CARRIER-CLOSURE-SOURCES.json',
         '--output', F.INVOICE+'CARRIER-CONJUNCTION.json'])
    need(code == 0, 'changed-tuple conjunction: '+error[-1800:])
    conjunction = A.load(idir/'CARRIER-CONJUNCTION.json')
    need(conjunction['status'] == 'PASS_CONDITIONAL_MATHEMATICAL_KAPPA_CONJUNCTION' and
         conjunction['premise_count'] == 25 and all(conjunction['premises'].values()), '25 conditional premises')
    need(conjunction['assumptions'] == ['native_all_columns', 'owned_erasure', 'compiler',
                                       'precision_tape', 'analytic_recovery'], 'same five framework assumptions')
    controls = {}
    if first:
        fixed = pdir/'V16-SOURCES-v3.json'
        saved = fixed.read_bytes()
        try:
            fixed.write_bytes(pman_path.read_bytes())
            code, error = A.run_engine(SRC, ws, F.PRECISION+'check_v16_precision_v3.py',
                ['--root', '.', '--output', F.PRECISION+'REJECT-ORIGINAL-PRECISION.json'])
        finally:
            fixed.write_bytes(saved)
        controls['original_precision_rejects_changed_carrier'] = code != 0 and 'actual funded carrier rank' in error
        code, error = A.run_engine(SRC, ws, F.INVOICE+'check_neutral_closure.py',
            ['--root', '.', '--manifest', F.INVOICE+'CARRIER-CLOSURE-SOURCES.json',
             '--output', F.INVOICE+'REJECT-ORIGINAL-CONJUNCTION.json'])
        controls['original_conjunction_rejects_coarse_tail_application'] = code != 0 and 'closure premise failed' in error
        def bad_precision(name, patch):
            bad = copy.deepcopy(funding)
            patch(bad)
            A.dump(idir/(name+'.json'), bad)
            altered = A.manifest(pman, {'funding': F.INVOICE+name+'.json'}, ws)
            path = pdir/(name+'-SOURCES.json')
            A.dump(path, altered)
            return precision_run(ws, path, name+'-PRECISION.json')
        code, error = bad_precision('previous-grid', lambda x: x.update(
            j=x['j']-1, H=F.ceilq(Q(x['j']-1)/Q(x['gap']))))
        controls['preceding_grid_rejected'] = code != 0 and 'actual funded carrier rank' in error
        code, error = bad_precision('product-too-large', lambda x: x['tuple'].update(tensor_power=1025))
        controls['unfunded_product_domain_rejected'] = code != 0 and 'compiler product domain' in error
        for name, patch in [('missing-paid-job', lambda x: x['paid'].__setitem__('1', x['paid']['1']-1)),
                            ('free-completion', lambda x: x.update(completion_tail_upper='0'))]:
            bad = copy.deepcopy(funding)
            patch(bad)
            try:
                F.verify_funding(ws, bad)
            except ValueError:
                controls[name+'_rejected_by_complete_rebuild'] = True
            else:
                controls[name+'_rejected_by_complete_rebuild'] = False
        try:
            F.certify(ws, dict(case, u=Q(0)))
        except ValueError:
            controls['invalid_higher_moment_domain_rejected'] = True
        controls['coarse_.97_envelope_is_actually_exceeded'] = Q(funding['gamma_upper']) > Q(97, 100)
        need(all(controls.values()) and len(controls) == 8, 'semantic rejection controls: '+str(controls))
    return {'case': case['name'], 'funding': funding,
            'application_proof_sha256': proof_sha, 'proof_substitution_sites': len(substitutions),
            'precision': {k: precision[k] for k in ('status', 'carrier_H', 'carrier_j', 'carrier_gap', 'expanded')},
            'conjunction': {'status': conjunction['status'], 'premise_count': 25,
                'premise_names': sorted(conjunction['premises']), 'unchanged_source_gate_names': unchanged,
                'assumptions': conjunction['assumptions']},
            'precision_baseline_conservativity': conservativity, 'controls': controls}


def build(proof_output=None):
    before = input_hashes()
    with tempfile.TemporaryDirectory(prefix='carrier-frontier-') as directory:
        scratch = Path(directory)
        baseline_path = scratch/'BASELINE.json'
        run = subprocess.run([sys.executable, '-I', '-B', str(SRC/'verify.py'),
                              '--output', str(baseline_path)], cwd=ROOT, capture_output=True, timeout=300)
        need(run.returncode == 0, 'unmodified PR5413 full replay: '+run.stderr.decode()[-1800:])
        baseline = A.load(baseline_path)
        need(baseline['status'] == 'PASS_CONDITIONAL_COMPLETE_NEUTRAL_CALLER_AND_FUNDED_KAPPA' and
             len(baseline['runs']) == 8 and all(r['returncode'] == 0 for r in baseline['runs']), 'fresh full caller replay')
        base_workspace = Path(baseline['scratch'])/'workspace'
        cases = []
        for index, case in enumerate(F.CASES):
            ws = scratch/case['name']
            shutil.copytree(base_workspace, ws)
            cases.append(case_application(ws, case, index == 0, proof_output))
            shutil.rmtree(ws)
        need(input_hashes() == before, 'frozen inputs unchanged during replays')
        return {'schema': 'pr5413-carrier-frontier/1',
                'scope': 'Conditional carrier size improvement at fixed or explicitly weaker saving. No raw profile/root improvement, global minimum, practical runtime or unconditional theorem.',
                'fresh_baseline': {'status': baseline['status'], 'engines': [r['name'] for r in baseline['runs']]},
                'cases': cases, 'source_count': len(before),
                'own_code_sha256': {name: A.sha(HERE/name) for name in ('frontier.py', 'application.py', 'verify.py')},
                'all_frozen_inputs_unchanged': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--proof-output', type=Path, help='retain generated proof instances and review diffs outside the package')
    args = parser.parse_args()
    result = build(args.proof_output)
    path = HERE/'RESULT.json'
    if args.write:
        A.dump(path, result)
    need(path.is_file() and A.load(path) == result, 'committed RESULT.json equals complete rebuild')
    print('PASS_PR5413_CARRIER_FRONTIER_WITH_CHANGED_TUPLE_PRECISION_AND_CONJUNCTION')


if __name__ == '__main__':
    main()
