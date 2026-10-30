#!/usr/bin/env python3
"""One native child for the common conjugate of an unpaired ADDRESS reflection.
Apache-2.0; substantial OpenAI Codex assistance. This is a local resource.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *
from orthogonal_source_normalizer import reflection
from lifted_algebra import Algebra

HERE = Path(__file__).resolve().parent


def tensor_monomial(recipe, f):
    """Lift every one-bit wire and phase bitwise, retaining its actual phase."""
    chunks = len(recipe['matrix_rows'])
    n = chunks * f
    def bitlift(mask, k):
        return sum(1 << (chunk * f + k) for chunk in range(chunks) if (mask >> chunk) & 1)
    rows = [bitlift(recipe['matrix_rows'][chunk], k) for chunk in range(chunks) for k in range(f)]
    quadratic = [bitlift(recipe['quadratic_rows'][chunk], k) for chunk in range(chunks) for k in range(f)]
    alpha = [recipe['linear_Z4'][chunk] for chunk in range(chunks) for k in range(f)]
    offset = sum(bitlift(recipe['offset'], k) for k in range(f))
    return mul(phase(n, f * recipe['phase']), ce.xgate(n, offset),
               ce.perm(n, rows), ce.diag(n, quadratic, alpha))


def run():
    z1 = Model(1, 3)
    R1, _ = reflection(z1, 3, (0, 1, 2, 4))
    base_native = [z1.N, z1.T[0], z1.T[1]]
    onebit_conjugates = [mul(Ni, R1, Ni.adjoint()) for Ni in base_native]
    recipes = []
    for A in onebit_conjugates:
        rec, compiled = ce.lower_child(A)
        need(rec['rank'] == 2, 'one-bit conjugate has native rank2')
        same(compiled, A, 'actual selected-native one-bit lowering')
        recipes.append(rec)
    A1, recipe = onebit_conjugates[0], recipes[0]
    checks = []
    for f in (1, 2, 3):
        z = Model(f, 3)
        R, _ = reflection(z, 3, (0, 1, 2, 4))
        for plane, (Ni, rec) in enumerate(zip([z.N, z.T[0], z.T[1]], recipes)):
            A = mul(Ni, R, Ni.adjoint())
            left = tensor_monomial(rec['left'], f)
            right = tensor_monomial(rec['right'], f)
            literal = mul(left, ce.fourier(z.n, range(2 * f)), right)
            same(literal, A, 'tensor-lifted native child actual phase')
            same(mul(A, A), z.I, 'conjugated reflection literal involution')
            need(b.native_rank(A) == 2 * f, 'conjugated reflection rank2f')
            need(b.native_rank(left) == b.native_rank(right) == 0, 'literal adapters monomial')
            checks.append({'f': f, 'conjugating_old_plane': plane,
                           'native_arity': 2 * f, 'inverse': 'same A',
                           'tensor_recipe_actual_Gaussian_phase': True})

    # Independently retain both bank columns over the exact all-f tensor algebra.
    a = Algebra(3)
    R, A = a.lift(R1), a.lift(A1)
    def shear(sign):
        out = a.mat_identity(2)
        out[0][1] = a.scale(a.one, sign)
        return out
    E, Ei = shear(1), shear(-1)
    BR = a.mat_product(a.mat_product(E, a.diagonal(2, 1, R)), Ei)
    conjugated = a.mat_product(a.mat_product(a.diagonal(2, 0, a.N), a.diagonal(2, 1, a.N)), BR)
    conjugated = a.mat_product(conjugated, a.mat_product(a.diagonal(2, 0, a.adjoint(a.N)), a.diagonal(2, 1, a.adjoint(a.N))))
    expected = a.mat_product(a.mat_product(E, a.diagonal(2, 1, A)), Ei)
    need(conjugated == expected, 'two independent bank-column conjugation identity')
    need(a.mat_product(expected, expected) == a.mat_identity(2), 'literal bank word inverse')
    return {'status': 'PASS_ALL_F_SINGLE_CHILD_CONJUGATED_UNPAIRED_REFLECTION',
            'scientific_pin': PIN,
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'reflection_source_sha256': hashlib.sha256((HERE/'orthogonal_source_normalizer.py').read_bytes()).hexdigest(),
            'native_model_sha256': hashlib.sha256((HERE/'native_model.py').read_bytes()).hexdigest(),
            'actual_operator': 'R=P_(I+vv^T), v=(1,1,1,0,1,0) on completed(p0,q0,p1,q1,p2,q2); A=N0 R N0^-1.',
            'all_f_tensor_identity': 'R_f is the bitwise tensor product of R_1. N_f=i^(1-f) N_1^tensor f after regrouping address coordinates. Its global unit cancels in conjugation, so A_f=A_1^tensor f literally, including phase. Tensoring the explicit one-bit monomial/native/monomial equality therefore gives A_f=L_f C_(2f) R_f_adapter. All three factors have fixed bitwise controllers; no f1 tableau-only inference is used.',
            'native_rank_proof': 'The binary B block of A_1 has rank2. Direct sums under bitwise tensor regrouping have rank2f, so A_f and its inverse have exact native arity2f for every f>=1. A_f^2=I by conjugation of R_f^2=I.',
            'one_bit_selected_native_recipe': recipe,
            'one_bit_selected_native_recipes_by_old_plane': recipes,
            'actual_tensor_recipe_checks': checks,
            'old_plane_extension': 'The same exact single-child admission holds for A_i=N_i R N_i^-1 on each i=0,1,2, with the three explicit recipes retained. Since N_i=i H_i and H_i=Hp_i Hq_i is involutive, this is also H_i R H_i without any external i. The tensor proof and all adapter phase powers apply separately to each saved recipe.',
            'single_unary_invoice': {'native_H2': 1, 'native_rank_mass': 2,
                                     'monomial_adapters': 2, 'ADDRESS_scans_at_most': 2,
                                     'Gaussian_quadratic_phase_scans_at_most': 2,
                                     'ordinary_helpers': 0, 'private_fields': 0},
            'two_bank_identity': 'For E12=I+e1e2^T and B_R=E12 diag(I,R) E12^-1, Ad_(diag(N,N))(B_R)=E12 diag(I,A) E12^-1. Both independent inputs are retained. Its literal inverse reverses the shears and applies A^-1=A; the entire displayed conjugated word is itself involutive.',
            'two_bank_invoice': {'native_H2': 1, 'native_rank_mass': 2,
                                 'scalar_ADD_scans': 2, 'monomial_adapters': 2,
                                 'ordinary_helpers': 0, 'private_fields': 0},
            'evidence_domain': 'Written all-f exact tensor proof and native B-rank proof; independent actual Gaussian compiled checks at f1/f2/f3; all-f two-bank polynomial coefficients checked in the phase-sensitive tensor algebra.',
            'limits': ['This is a changed legal local bridge, not a completed caller or shared-debt cancellation.',
                       'The source-kernel N0R is not assumed quadratic, and no old scalar caller is imported by that assumption.',
                       'All bank ADD, ADDRESS and phase scans are paid; no source access, owner, precision, all-size or tape gate is discharged.'],
            'no_new_kappa': True}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE/'CONJUGATED-REFLECTION.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved conjugated reflection differs')
    print(out['status'])
    print(out['single_unary_invoice'])
