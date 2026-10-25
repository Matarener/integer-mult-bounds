#!/usr/bin/env python3
"""Gaussian-typed binary orthogonal normalizers at a full source cut.

This is a genuine bit-linear ADDRESS extension beyond plane permutations
and X translations. It is not itself a completed caller construction.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
from native_model import *

HERE = Path(__file__).resolve().parent


def typed_D(model, oldplanes):
    alpha, quadratic = [0] * model.n, [0] * model.n
    for chunk in range(2 * oldplanes):
        for bit in range(model.f):
            k = chunk * model.f + bit
            alpha[k] = 1 if chunk % 2 == 0 else 3
            quadratic[k] = 1 << k
    return ce.diag(model.n, quadratic, alpha)


def reflection(model, oldplanes=2, support=(0, 1, 2, 3)):
    need(len(support) % 2 == 0 and len(support) > 0, 'even nonempty reflection support')
    need(max(support) < 2 * oldplanes, 'reflection uses only completed old chunks')
    rows = [1 << j for j in range(model.n)]
    for out in support:
        for bit in range(model.f):
            rows[out * model.f + bit] ^= sum(1 << (src * model.f + bit)
                                            for src in support)
    D = typed_D(model, oldplanes)
    P = ce.perm(model.n, rows)
    return mul(D.adjoint(), P, D), rows


def gaussian_add(a, c):
    return a[0] + c[0], a[1] + c[1]


def unit(power):
    return ((1, 0), (0, 1), (-1, 0), (0, -1))[power % 4]


def marked_character_checks():
    # Actual 64-point Fourier character sum, independent of Clifford tableaux.
    def residual(w):
        return tuple(((w >> (2 * k)) ^ (w >> (2 * k + 1))) & 1 for k in range(3))

    def character_coefficient(w, wp, support):
        v = sum(1 << k for k in support)
        coefficient = (0, 0)
        for x in range(64):
            Ax = x ^ (v if (x & v).bit_count() % 2 else 0)
            dx = sum((1 if k % 2 == 0 else -1) * ((x >> k) & 1) for k in range(6))
            dAx = sum((1 if k % 2 == 0 else -1) * ((Ax >> k) & 1) for k in range(6))
            sign = 2 * (((w & x).bit_count() + (wp & Ax).bit_count()) % 2)
            coefficient = gaussian_add(coefficient, unit(dx - dAx + sign))
        return [Fraction(a, 64) for a in coefficient]

    # The initially proposed balanced reflection is NOT an escape. It maps
    # w to w+(v.w+1)v and preserves both the unique mark and its virtual bit.
    v = 15
    paired_checked = 0
    for w in range(64):
        marks = residual(w)
        if sum(marks) != 1:
            continue
        wp = w ^ (v if ((w & v).bit_count() + 1) % 2 else 0)
        owner = marks.index(1)
        need(character_coefficient(w, wp, (0, 1, 2, 3)) == [1, 0], 'paired exact character map')
        need(residual(wp) == marks and ((w >> (2 * owner)) & 1) == ((wp >> (2 * owner)) & 1), 'paired reflection commutes marked C')
        paired_checked += 1
    # Unpaired three-p/one-q reflection is bare ADDRESS, sending q0 to p0+p1+p2.
    w, wp = 2, 21
    coefficient = character_coefficient(w, wp, (0, 1, 2, 4))
    need(coefficient == [1, 0], 'unpaired actual character coefficient')
    need(residual(w) == (1, 0, 0) and residual(wp) == (1, 1, 1), 'genuine marked-subspace leakage')
    return {'paired_negative_control': {'one_mark_characters_checked': paired_checked,
                                        'marked_C_commutes': True,
                                        'all_f_lift': 'The map is bitwise. With one residual mark r=(p0,q1^f), its owner inside the balanced support makes v.w=1 at every position and R fixes the character. An owner outside makes R complement only unmarked virtual bits. The marked owner bit is unchanged.'},
            'unpaired_escape': {'input_X_character': w, 'input_residual_marks': residual(w),
                                'output_X_character': wp, 'output_residual_marks': residual(wp),
                                'actual_character_matrix_coefficient': [str(x) for x in coefficient],
                                'all_f_lift': 'Put ones on all f q0 positions and zeros elsewhere. Bare bitwise ADDRESS sends this X character to ones on all p0,p1,p2 positions, changing exactly one residual mark into three for every f>=1. No diagonal pair gauge can remove this nonzero leakage.'}}


def run():
    checks = []
    onebit_recipe = None
    for f in (1, 2, 3):
        z = Model(f, 2)
        R, rows = reflection(z)
        oldG = mul(z.N, z.T[0])
        same(mul(R, R), z.I, 'actual orthogonal normalizer involution')
        same(mul(R, oldG), mul(oldG, R), 'actual full-source normalizer phase')
        need(b.native_rank(R) == 0, 'orthogonal typed reflection is monomial')
        # Literal two-bank source insertion, with oldfresh=N1 and newfresh=N2.
        actual_source = mul(z.P[1], R.adjoint(), R, z.N, z.T[0])
        actual_cross = mul(z.T[1], R, z.N, z.T[0])
        desired_source = mul(z.T[1], z.T[0], z.P[1])
        desired_cross = mul(z.T[1], z.T[0], z.N, R)
        same(actual_source, desired_source, 'unchanged sourcecode and fresh coverage')
        same(actual_cross, desired_cross, 'changed delivery N0R on arbitrary source column')
        # The raw target coefficient is N2 N1 and is independent of source.
        K = mul(z.N, R)
        power = z.I
        ranks = []
        for exponent in range(1, 5):
            power = mul(K, power)
            ranks.append(b.native_rank(power))
        same(power, z.I, 'exact quartic phase of this reflection kernel')
        need(ranks == [2 * f, 2 * f, 2 * f, 0], 'kernel power is not an unproved full-native completion')
        if f == 1:
            compiled, onebit_recipe = ce.monomial(R)
            same(R, compiled, 'actual literal Gaussian monomial recipe')
        checks.append({'f': f, 'native_R': 0, 'source_old_native_planes': [0, 1],
                       'new_fresh_plane': 2, 'source_frame_commutes_actual_phase': True,
                       'kernel_power_native_arities': ranks, 'kernel_fourth_power': 'I'})
    unpaired_checks = []
    for f in (1, 2):
        z = Model(f, 3)
        R, rows = reflection(z, 3, (0, 1, 2, 4))
        bare = ce.perm(z.n, rows)
        oldG = mul(z.N, z.T[0], z.T[1])
        same(R, bare, 'unpaired typed normalizer is literally bare ADDRESS')
        same(mul(R, R), z.I, 'unpaired reflection literal involution')
        same(mul(R, oldG), mul(oldG, R), 'unpaired full-source Gaussian phase')
        need(b.native_rank(R) == 0, 'unpaired ADDRESS is nativezero')
        actual_source = mul(z.P[2], R.adjoint(), R, z.N, z.T[0], z.T[1])
        actual_cross = mul(z.T[2], R, z.N, z.T[0], z.T[1])
        same(actual_source, mul(z.T[2], z.T[0], z.T[1], z.P[2]), 'unpaired unchanged source column')
        same(actual_cross, mul(z.T[2], z.T[0], z.T[1], z.N, R), 'unpaired changed cross column phase')
        need(b.native_rank(mul(z.N, R)) == 2 * f, 'changed cross native arity')
        unpaired_checks.append({'f': f, 'old_native_planes': [0, 1, 2], 'new_fresh_plane': 3,
                                'actual_typed_R_equals_bare_ADDRESS': True, 'native_R': 0,
                                'source_and_cross_columns_actual_phase': True,
                                'kernel_native_arity': 2 * f})
    characters = marked_character_checks()
    return {'status': 'PASS_ALL_F_ORTHOGONAL_TYPED_SOURCE_NORMALIZER',
            'scientific_pin': PIN,
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'native_model_sha256': hashlib.sha256((HERE/'native_model.py').read_bytes()).hexdigest(),
            'all_parameter_schema': 'For j old native planes (2j chunks), put D=diag phasei on everyoldp bit and-i on everyoldq bit. Exact G_old=product(N_i)=i^j D^-1 H_all D. If binaryA is orthogonal,A^T A=I, then its literal ADDRESS permutation P_A commutes ordinary WalshH_all. Hence R_A=D^-1 P_A D is monomial and commutesG_old, including all global phases, for every f>=1.',
            'paired_reflection_negative_control': 'On two complete oldplanes v=1111 gives a legal typed R, but it COMMUTES with the marked-residual C. It is not an escape from that grammar floor. Its kernel K=N0R has exact K^4=I and nativearities2f,2f,2f,0 for its first four powers.',
            'explicit_unpaired_reflection': 'On three complete oldplanes ordered(p0,q0,p1,q1,p2,q2), take v=(1,1,1,0,1,0), A=I+vv^T. Its support has three p chunks and one q. v^Tv=0, so A^2=A^T A=I. Apply it bitwise at all f positions. Writing d(x)=sum pbits-sum qbits, if v.x is odd then d(x)-d(Ax)=2 d_v(x)-2=0 mod4; otherwise zero. Thus R_A=D^-1 P_A D=P_A literally, with no extra Gaussian phase.',
            'literal_gaussian_chart': 'Ononebit Hp=e^(-i pi/4) S^-1 H S and Hq=e^(+i pi/4) S H S^-1, S=diag(1,i). Their scalar factors cancel within each actual pairN=i Hp Hq, giving the exact i^j formula above. This is a conjugation identity in Gaussian operators; no irrational phase is introduced by the implementedR, which usesonly D/P_A/D^-1 with Gaussian-unit entries.',
            'source_cut_binding': 'At stagej with oldF=productfresh1..j-1, source N0oldF is full G_old. Insert R before the source delivery and R^-1 immediately after. Then sourcePj and targetNj give boundary Fnew[[Pj,0],[N0R,I]]. The sourceoriginal column, targetoriginal column, arbitrary source crosscolumn and literal inverse all retain their phases. This doesnot assert(N0R)^2=-I.',
            'per_pair_invoice': {'native_H2': 2, 'native_rank_mass': 4,
                                 'delivery_ADD_scans': 1,
                                 'existing_source_ADDRESS_scans': 1,
                                 'new_R_ADDRESS_scans': 2,
                                 'new_R_diagonal_phase_scans': 0,
                                 'ordinary_helpers': 0, 'private_fields': 0},
            'native_zero_lowering': 'The useful unpaired R is the explicit bitwise binary ADDRESS map A=I+vv^T itself. Its inverse is the same literal scan. Both new scans use only completed old chunks. The fixed binary controller and all address/source work remain paid.',
            'paired_one_bit_monomial_recipe': onebit_recipe,
            'paired_actual_checks': checks,
            'unpaired_actual_checks': unpaired_checks,
            'marked_character_checks': characters,
            'evidence_domain': 'Written all-j/all-f orthogonal conjugation proof and explicit all-f bare-phase/leakage proof; actual Gaussian phase/source-column checks for pairedj2 f1/f2/f3 and unpairedj3 f1/f2; independent64-point actual Fourier-character sums. The paired candidate is correctly rejected as a marked-C escape. No f1-only native admission is extrapolated.',
            'limits': ['A complete caller must retain the changed noncommuting kernelsN0R and their independent-input sourcecodes, all public couplings and the literal inverse.',
                       'The old scalar quadratic caller cannot be reused by pretendingK^2=-I.',
                       'No full exponent, stock/owner, all-size, precision or tape claim is made.'],
            'no_new_kappa': True}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE/'ORTHOGONAL-SOURCE-NORMALIZER.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved orthogonal normalizer differs')
    print(out['status'])
    print(out['marked_character_checks']['unpaired_escape'])
