#!/usr/bin/env python3
"""Independent absolute-phase audit of all actual native monomial variants.

Native K_G conventions retain PR2226 and Cao Yifan/intqwq's PR4610 source.
The signed Clifford tableau/compiler and its absolute-phase anchor retain the
PR531/T74 native lineage. The conjugate backward convention retains Dugongue,
Cinna Davis and the source phase audit. The observer question retains zxv's
PR5419 and Mark/Matarener's PR5427. This checker corroborates the independently
implemented direct-Gram monomial tables; it does not prove an observer exists.

Prepared for THU New Media Research Center (@thu-nmrc), with substantial
OpenAI Codex assistance. Apache-2.0. Default operation writes no files.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import gzip
import json
import sys
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = ('research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py',
          '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962')
SOURCE = ('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
          '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run():
    for relative, expected in (ENGINE, SOURCE):
        need(sha256((ROOT/relative).read_bytes()).hexdigest() == expected,
             'phase-audit source bytes changed: '+relative)
    ce = load('physical_zqy_frozen_clifford_phase_audit', ROOT/ENGINE[0])
    candidate = load('physical_zqy_direct_gram_phase_audit', HERE/'monomial.py')
    canon = json.loads(gzip.decompress((ROOT/SOURCE[0]).read_bytes()))['canonical']
    need(len(canon['warps']) == 72 and
         {entry['op'] for entry in canon['warps']} == set(range(1, 73)),
         'all 72 pinned native operators')

    def reference(columns):
        # Retained phase-audit Kop convention, using frozen Clifford primitives.
        # Op.then is chronological: first perm(G), then diag(I+G^-T G^-1).
        rows = ce.transpose(tuple(columns), 9)
        inverse_rows = ce.inv(rows, 9)
        inverse_columns = ce.transpose(inverse_rows, 9)
        quadratic = tuple((1 << i) ^ sum(ce.parity(u & v) << j
            for j, v in enumerate(inverse_columns))
            for i, u in enumerate(inverse_columns))
        return ce.perm(9, rows).then(ce.diag(9, quadratic))

    def conjugate(operator):
        # Entrywise conjugation, preserving chronological circuit order.
        # K_G and its adjoint use only P/D here; the explicit gate cases also
        # retain the source convention for ordinary affine/phase gates.
        out = ce.ident(operator.n)
        for gate in operator.circuit:
            kind = gate[0]
            if kind == 'P':
                part = ce.perm(operator.n, gate[1])
            elif kind == 'D':
                part = ce.diag(operator.n, gate[1], tuple(-x % 4 for x in gate[2]))
            elif kind == 'X':
                part = ce.xgate(operator.n, gate[1])
            elif kind == 'C':
                part = ce.cgate(operator.n, gate[1], -gate[2])
            else:
                need(kind == 'phase', 'recognized frozen Clifford primitive')
                part = ce.Op(operator.n, ce.identity(operator.n), [('phase', -gate[1] % 4)])
            out = out.then(part)
        return out

    def checked_columns(operator):
        # The frozen compiler derives a monomial from the signed tableau.
        # An exact Gaussian-integer zero column fixes the remaining phase.
        need(ce.rank([x for x, z, p in operator.tab[9:]]) == 0, 'reference monomial')
        compiled, recipe = ce.monomial(operator)
        need(compiled.tab == operator.tab and
             compiled.zero_state() == operator.zero_state(),
             'frozen signed tableau and absolute phase')
        result = []
        for address in range(512):
            out = ce.mv(tuple(recipe['matrix_rows']), address) ^ recipe['offset']
            exponent = (ce.qvalue(tuple(recipe['quadratic_rows']),
                tuple(recipe['linear_Z4']), address, 9) + recipe['phase']) % 4
            result.append(4*out+exponent)
        return result

    actual, refs = {}, {}
    individual_columns = backward_differences = 0
    for entry in canon['warps']:
        op = entry['op']
        forward_ref = reference(entry['G_columns'])
        forward_table = candidate.native(entry['G_columns'])
        for sign in (1, -1):
            ref = forward_ref if sign == 1 else forward_ref.adjoint()
            table = forward_table if sign == 1 else candidate.inverse(forward_table)
            for backward in (False, True):
                tested = candidate.conjugate(table) if backward else table
                expected = conjugate(ref) if backward else ref
                need(list(candidate.decode(tested)) == checked_columns(expected),
                     'frozen Clifford mismatch for op/sign/backward '+str((op, sign, backward)))
                need(candidate.decode(tested)[0] == 0, 'zero-address phase gauge')
                actual[op, sign, backward], refs[op, sign, backward] = tested, expected
                individual_columns += 512
            backward_differences += int(candidate.conjugate(table) != table)
    need(individual_columns == 147456, 'complete individual-column census')
    need(backward_differences == 140, 'conjugate-direction discriminating control')
    phase_control = refs[1, 1, False].then(
        ce.Op(9, ce.identity(9), [('phase', 1)]))
    need(phase_control.tab == refs[1, 1, False].tab and
         phase_control.zero_state() != refs[1, 1, False].zero_state(),
         'a tableau-invisible global phase must change the absolute anchor')

    # Check multiplication order against frozen Op.then, including complex
    # phases and inverse signs, independently of the candidate inverse law.
    product_columns = 0
    for op in range(1, 73):
        left = (op, -1 if op % 2 else 1, bool(op % 3))
        right = (1 + op % 72, 1 if op % 2 else -1, bool(op % 5))
        table = candidate.multiply(actual[left], actual[right])
        expected = refs[right].then(refs[left])
        need(list(candidate.decode(table)) == checked_columns(expected), 'ordered product mismatch')
        product_columns += 512
    need(product_columns == 36864, 'complete ordered-product column census')
    return dict(status='PASS_INDEPENDENT_FROZEN_CLIFFORD_NATIVE_MAP_AUDIT',
        native_operators=72, signs=2, directions=2,
        exact_individual_columns=individual_columns,
        exact_ordered_product_columns=product_columns,
        backward_sign_cases_differing_from_forward=backward_differences,
        tableau_invisible_phase_control=True,
        every_reference_fixes_zero_with_zero_phase=True,
        frozen_engine_sha256=ENGINE[1], source_word_sha256=SOURCE[1],
        evaluator='frozen signed Clifford tableau, monomial compiler, exact Gaussian-integer phase anchor',
        no_formal_membership_rerun=True, observation_existence_proved=False,
        runtime_file_writes=0)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
