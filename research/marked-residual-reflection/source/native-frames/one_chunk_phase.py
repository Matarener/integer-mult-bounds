#!/usr/bin/env python3
"""Exact phase limits of a one-typed-chunk order-four native operator.
Apache-2.0; substantial OpenAI Codex assistance. Tag extension is separate.
"""
from pathlib import Path
import argparse
import hashlib
import json
from native_model import *

HERE = Path(__file__).resolve().parent


def run():
    checks = []
    for f in range(1, 6):
        z = Model(f, 1)
        for name, base, square in [('Hp', z.Hp(0), -f), ('Hq', z.Hq(0), f)]:
            B = mul(phase(z.n, 1), base)
            same(mul(B, B), phase(z.n, 2 + square), 'literal i typedchunk square')
            need(b.native_rank(B) == f, 'typedchunk native arity')
            if f % 2 == 0:
                gamma = f // 2 + 1 if name == 'Hp' else 1 - f // 2
                normalized = mul(phase(z.n, gamma), base)
                same(mul(normalized, normalized), phase(z.n, 2), 'even chunk Gaussian-unit normalization')
            checks.append({'f': f, 'type': name, 'native_arity': f,
                           'square_of_iH_as_i_exponent': (2 + square) % 4,
                           'Gaussian_scalar_normalization_to_minus_I': f % 2 == 0})
        # One tag BIT is an explicit extra coordinate. It is not part of
        # the claimed flat f-bit one-chunk domain.
        tag = f
        alpha = [0] * z.n
        alpha[tag] = (f + 2) % 4  # c=-i^f; M=[[0,1],[c,0]], M^2=cI.
        quadratic = [0] * z.n
        quadratic[tag] = (1 << tag) if alpha[tag] % 2 else 0
        M = mul(ce.diag(z.n, quadratic, alpha), ce.xgate(z.n, 1 << tag))
        same(mul(M, M), phase(z.n, f + 2), 'actual Gaussian ADDRESS-tag phase')
        tagged = mul(z.Hp(0), M)
        same(mul(tagged, tagged), phase(z.n, 2), 'tagged operator squares to minus identity')
        need(b.native_rank(tagged) == f, 'tag extension remains rankf')
        recipe = None
        if f == 1:
            recipe, compiled = ce.lower_child(tagged)
            same(tagged, compiled, 'literal tagged selected-native lowering')
        checks.append({'f': f, 'type': 'Hp_with_separate_tag_bit', 'native_arity': f,
                       'extra_ADDRESS_bit': tag, 'square': '-I',
                       'tag_diagonal_phase_exponent': (f + 2) % 4,
                       'selected_native_recipe': recipe})
    return {'status': 'PASS_ONE_CHUNK_PHASE_DOMAIN_AND_SEPARATE_TAG_RESOURCE',
            'scientific_pin': PIN,
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'native_model_sha256': hashlib.sha256((HERE/'native_model.py').read_bytes()).hexdigest(),
            'all_f_identity': 'Hp_f^2=(-i)^f I and Hq_f^2=i^f I, so (i Hp_f)^2=-(-i)^f I and (i Hq_f)^2=-i^f I. Literal iH squares to-I only when f=0 mod4.',
            'even_f_normalization': 'For even f, gamma_p=i^(f/2+1), gamma_q=i^(1-f/2) are Gaussian units and (gamma_p Hp_f)^2=(gamma_q Hq_f)^2=-I.',
            'odd_f_scalar_obstruction': 'For odd f a scalar normalization requires gamma^2=+i or-i. If gamma=a+bi is Gaussian rational then a^2=b^2 and2ab=+1 or-1, forcing a^2=1/2, impossible rational. Thus no Gaussian-dyadic scalar, unit or nonunit, normalizes the odd-f typed chunk to square-I.',
            'flat_unitary_obstruction_scope': 'More generally, a unitary B acting fully and flatly on exactly f address bits with B^2=-I is skew-Hermitian. Every diagonal is nonzero pure imaginary of magnitude2^(-f/2). Gaussian-dyadic entries cannot have that imaginary value for odd f. This covers unitary monomial left/right gauges of a full one-chunk native Fourier operator; it does not cover an enlarged ambient operator with zero diagonal, nonunitary gauges, arbitrary operators of rankf acting on more thanf bits, or a changed recursive datatype.',
            'tag_resource': 'A separate tag bit admits M_f=[[0,1],[-i^f,0]], an actual ADDRESS X plus Gaussian-unit phase, with M_f^2=-i^f I. Since it is disjoint from Hp_f, B_f=Hp_f tensor M_f has B_f^2=-I and exact nativearityf for every f. This is a changed f+1-bit domain, not a scalar normalization onf bits.',
            'tag_invoice': {'native_arity': 'f', 'extra_address_coordinates': 1,
                            'tag_ADDRESS_X_scans': 1, 'tag_phase_scans': 1,
                            'native_monomial_adapter_scans_at_most': 2,
                            'ordinary_helpers': 0, 'private_fields': 0},
            'tag_terminal_obligation': 'The extra tag bit remains monomial under this resource. A supplier requiring full native rank on its entire ambient address space must supply its missing tag Fourier progress, or prove a separately charged sector/dispatcher contract. That cost is not waived here. Sharing the tag among planes also changes their product and must be checked literally.',
            'actual_checks': checks,
            'evidence_domain': 'Written all-f scalar/flat-unitary proofs; actual exact Gaussian phase and arity checks for f1..5; one-bit selected-native lowering plus the explicit Hp tensor/native query and monomial tag implementation. No tableau-only extrapolation. Higher-f dense recipe expansion is unnecessary and is not claimed.',
            'no_new_kappa': True}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE/'ONE-CHUNK-PHASE.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text()) == out, 'stored one-chunk phase receipt differs')
    print(out['status'])
