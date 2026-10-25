#!/usr/bin/env python3
"""Replay frozen recipes without invoking any Clifford lowering routine."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('partial_native_replay_interpreter', HERE/'audit.py')
a = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = a
spec.loader.exec_module(a)


def expected_new(rec, frames, I, F):
    U = frames[int(rec['bank'])]
    name = rec['name']
    if 'source_label' in rec:
        line = a.ce.cgate(a.N, int(rec['source_label']))
        return line.adjoint().then(U) if name.endswith('_to_U') else U.adjoint().then(line)
    if name.endswith('_ZERO_to_U'):
        return U
    if name.endswith('_U_to_ZERO'):
        return U.adjoint()
    if name.endswith('_U_to_FULL'):
        return U.adjoint().then(F)
    if name.endswith('_FULL_to_U'):
        return F.adjoint().then(U)
    raise ValueError(('unrecognized new recipe', name))


def main():
    started = time.perf_counter()
    source = a.validate_inputs()
    result = json.loads((HERE/'RESULT.json').read_text())
    raw = (HERE/'RECIPES.json').read_bytes()
    a.need(hashlib.sha256(raw).hexdigest() == result['recipe_sha256'], 'new recipe receipt hash')
    payload = json.loads(raw)
    frames = {b['bank']:a.ce.canonical_frame(a.N, tuple(b['geometry']['U'])) for b in source['banks']}
    I, F = a.ce.ident(a.N), a.ce.fourier(a.N)
    small = a.crosscheck_interpreters()
    checks = 0
    for rec in payload['recipes']:
        witness = a.check_recipe(rec, expected_new(rec, frames, I, F))
        a.need(witness == rec['independent_phase_witness'], 'new recipe exact state digest changed')
        checks += 1
    old = json.loads((HERE/'BASELINE-RECIPES.json').read_text())
    work = json.loads((HERE/'ADAPTER-WORK.json').read_text())
    a.need(hashlib.sha256((HERE/'BASELINE-RECIPES.json').read_bytes()).hexdigest() == work['baseline_recipe_sha256'], 'baseline recipe receipt hash')
    for rec in old['recipes']:
        if 'source_label' in rec:
            expected = a.ce.cgate(a.N,int(rec['source_label'])).adjoint().then(F)
        else:
            expected = F.adjoint() if rec['name'].endswith('FULL_to_ZERO') else F
        witness = a.check_recipe(rec, expected)
        a.need(witness == rec['independent_phase_witness'], 'baseline exact state digest changed')
        checks += 1
    # Corrupt fields in each recipe category, independent of receipt digests.
    rejected = []
    for target in (payload['recipes'][0],payload['recipes'][2],payload['recipes'][4]):
        mutant = copy.deepcopy(target)
        mutant['left']['phase'] = (mutant['left']['phase']+1)%4
        a.need(a.recipe_tableau(mutant,a.N) == a.recipe_tableau(target,a.N), 'phase corruption should preserve signed tableau')
        try:
            a.check_recipe(mutant,expected_new(target,frames,I,F))
        except ValueError:
            rejected.append(target['name'])
        else:
            raise ValueError('independent replay accepted phase corruption')
    a.need(checks == 820 and len(rejected) == 3, 'complete new-plus-baseline replay coverage')
    receipt = dict(status='PASS_FROZEN_RECIPE_REPLAY_WITHOUT_LOWERING',
                   optimization_flag=sys.flags.optimize, all_new_recipes=548, all_replaced_baselines=272,
                   total_exact_operator_checks=checks, signed_generators_per_operator=34,
                   complete_gaussian_state_coordinates_per_operator=a.SIZE,
                   independent_small_all_basis_interpreter_checks=small,
                   global_phase_corruptions_rejected=rejected,
                   new_recipe_sha256=result['recipe_sha256'], baseline_recipe_sha256=work['baseline_recipe_sha256'],
                   elapsed_seconds=time.perf_counter()-started,
                   mathematical_scope='Arbitrary complex input vectors for the finite indexed17-axis operators. This executes independent raw-field Gaussian and Pauli interpreters, without invoking lower_child or compile_transition. No formal kernel or all-size/tape admission.')
    destination = 'REPLAY-OPTIMIZED.json' if sys.flags.optimize else 'REPLAY.json'
    (HERE/destination).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
