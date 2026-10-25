#!/usr/bin/env python3
"""A full-native product path in the admitted normalized OPEN network.

No complete clearing caller is claimed. Apache-2.0; OpenAI Codex assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import full_stabilizer_bound as bound


def run():
    old = bound.canonical_predecessor()
    ce = old.ce
    records = []
    for group in range(3):
        for coordinate, p in enumerate(old.bus['groups7'][group]):
            q = old.bus['groups7'][(group + 1) % 3][coordinate]
            r = old.bus['groups7'][(group + 2) % 3][coordinate]
            chart = ce.perm(7, ce.transpose(old.completion(p, q), 7))
            if group == 2:
                raw_pre = old.build(7, old.winner[p]['pre_events'])
            else:
                v = q ^ r
                raw_pre = ce.perm(7, [(1 << i) ^ (v if v >> i & 1 else 0) for i in range(7)])
            pre, _ = ce.monomial(chart.then(raw_pre).then(chart.adjoint()))
            cases = []
            for length in (1, 3, 5, 9):
                n = 2 + 5 * length
                cp, cq = ce.cgate(n, 1), ce.cgate(n, 2)
                actual_pre = old.embed(n, pre.circuit, list(range(7)))
                k0 = bound.standard_product(ce, cq, cp.adjoint(), actual_pre)
                all_fresh = ce.fourier(n, range(2, n))
                # This is one actual coefficient path: take the normalized
                # forward cross at stage0, and every later diagonal T_s.
                path = bound.standard_product(ce, all_fresh, k0)
                expected = bound.standard_product(ce, ce.fourier(n), ce.xgate(n, 1), actual_pre)
                bound.need(path.tab == expected.tab, 'exact signed tableau of admitted full-rank forward path')
                bound.need(bound.native_rank(path) == n, 'normalized OPEN forward path has full native rank')
                # Full actual Gaussian column fixes phase at B1 size17.
                if length == 3 and coordinate == 0 and group in (0, 2):
                    bound.need(bound.sparse_column(path) == bound.sparse_column(expected), 'independent full-native path phase')
                cases.append({'L': length, 'm': n, 'path_native_rank': bound.native_rank(path)})
            records.append({'group': group, 'coordinate': coordinate, 'p': p, 'q': q, 'cases': cases})
    return {
        'status': 'PASS_NORMALIZED_OPEN_FULL_NATIVE_FORWARD_PATH_NO_CLEARING_WORD',
        'scientific_pin': bound.PIN,
        'sources_sha256': bound.PINS,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'identity': '(prod_s F_s) K_0 = (prod_s F_s) Cq Cp^-1 pre_0 = F_global Xp pre_0',
        'all_size_proof': 'C gates in distinct translation directions commute exactly; F_global=Cp Cq prod_s F_s, Cp^-2=Xp. Thus the identity holds including global phase for all tensor chunks f. The right factor pre_0 is monomial, so the product has native rankm, or rankmf on f tensor columns.',
        'finite_path_lemma': 'A sum of K operator paths each with row support <=2^((m-d)f) has support <=K*2^((m-d)f). A full native rankmf output requires K>=2^(df). For any finite topology whose K is independent of f, same-deficit paths cannot fill the gap for all f. The lemma does not apply when a path such as the one here already has full rank.',
        'records': records,
        'caller_boundary': ['This is a single admitted coefficient path, not a complete all-input diagonal operator.', 'An initial paid bank exchange can put an original target input on the forward source lineage, while its noncommon logical code is retained explicitly. It does not magically change that input frame or solve cleanup.', 'All unwanted cross terms, source and target code endpoints, idle windows, stock, precision and tape work remain to be supplied by any changed caller.', 'The path uses normalized OPEN forward cross T K, whose operator is source-bound in the frozen local alphabet. No analogous full-rank statement for a raw reverse J crossing is inferred.'],
        'attribution': 'Frozen complex/root normalization supplies K=Cq Cp^-1 pre and the all-input OPEN block. This lane supplies the exact full-native path identity and the finite-path support threshold; no new local supplier is asserted.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    output = json.loads(json.dumps(run()))
    target = Path(__file__).resolve().parent / 'FULL-NATIVE-PATH.json'
    if args.write:
        target.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    else:
        bound.need(json.loads(target.read_bytes()) == output, 'stored path witness differs')
    print(output['status'])
    print('12 ports x L1/3/5/9;2 n17 exact Gaussian phase checks;all-f identity proved')


if __name__ == '__main__':
    main()
