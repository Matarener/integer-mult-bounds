#!/usr/bin/env python3
"""An exact final-row prune for one bounded five-query tensor grammar.

No branch is rejected because of a sampled state or a floating computation.
The fifth query touches only bank0, so bank1 must already lie in the
accepted E3 times free-ADDRESS algebra.  This necessary condition rejects
all26 last choices together, separately for each chunk-size residue.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
from varied_reflection_screen import VariedBase
from unpaired_reflection_screen import need, rotate

HERE = Path(__file__).resolve().parent


class EnlargedBase(VariedBase):
    def __init__(self, dual):
        super().__init__()
        self.dual = []
        for p in (0, 2, 4):
            v = sum(1 << i for i in (1, 3, 5, p))
            self.dual.append(self.intern(tuple(w ^ (v if (w & v).bit_count() & 1 else 0)
                                              for w in range(64)), (0,) * 64))
        self.enlarged_generators = self.Rs + self.dual
        for a, b in ((0, 2), (0, 4), (1, 3), (1, 5)):
            perm = list(range(6))
            perm[a], perm[b] = perm[b], perm[a]
            self.enlarged_generators.append(self.intern(
                tuple(sum(((w >> j) & 1) << perm[j] for j in range(6)) for w in range(64)),
                (0,) * 64))
        if dual:
            free, todo = {self.identity}, [self.identity]
            for old in todo:
                for generator in self.enlarged_generators:
                    new = self.left(generator, old)
                    if new not in free:
                        free.add(new)
                        todo.append(new)
            need(len(free) == 576, 'the enlarged exact free ADDRESS group has order576')
            self.free = sorted(free)
            self.accept = {}
            for g in self.free:
                need(self.left(g, self.Ebase) == self.left(self.Ebase, g),
                     'every enlarged actual ADDRESS commutes exact E3')
                target = self.left(g, self.Ebase)
                ray, phase = self.rays[target]
                need(phase == 0 and ray not in self.accept,
                     'enlarged ADDRESS completions give distinct zero-phase tensor rays')
                self.accept[ray] = g
            self.accept_rays = set(self.accept)

    def folded(self, entry, residue):
        result = {}
        for op, z in entry.items():
            ray, phase = self.rays[op]
            a, b = rotate(z, phase * residue)
            c, d = result.get(ray, (0, 0))
            value = a + c, b + d
            if value == (0, 0):
                result.pop(ray, None)
            else:
                result[ray] = value
        return result

    def last_row_residues(self, matrix):
        # A singleton rejected tensor ray cannot cancel for any residue.
        if self.singleton_obstruction(matrix[2:]):
            return []
        return [s for s in range(4)
                if all(all(ray in self.accept for ray in self.folded(entry, s))
                       for entry in matrix[2:])]


def source_pins():
    native = HERE.parent / 'native-frames'
    files = [HERE / 'unpaired_reflection_screen.py', HERE / 'varied_reflection_screen.py']
    files += [native / name for name in
              ('native_model.py', 'conjugated_reflection.py', 'CONJUGATED-REFLECTION.json',
               'conjugated_factory.py', 'CONJUGATED-FACTORY.json')]
    return [dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in files]


def run(dual):
    A = EnlargedBase(dual)
    initial = ({A.identity: (1, 0)}, {}, {}, {A.identity: (1, 0)})
    banks = [0, 1, 0, 1, 0]
    routes = [A.Rs[0], A.dual[0], A.Rs[1], A.dual[1]] if dual else [A.Rs[i] for i in (0, 1, 2, 0)]
    counts = Counter()
    hits = {s: [] for s in range(4)}
    all_hits = []

    def visit(matrix, word, depth):
        if depth == 4:
            counts['four_query_prefixes'] += 1
            counts['covered_five_query_words'] += len(A.choices)
            possible = A.last_row_residues(matrix)
            if not possible:
                counts['all_last_queries_pruned_prefixes'] += 1
                # Deterministic controls cover actual full matrices from this
                # trace. They compare the prune against the unpruned test.
                if counts['pruned_controls'] < 16:
                    for choice in A.choices:
                        candidate = A.apply_query(matrix, 0, choice)
                        need(all(A.complete(candidate, s) is None for s in range(4)),
                             'last-row prune rejects only truly impossible completions')
                    counts['pruned_controls'] += 1
                return
            counts['tested_last_query_words'] += len(A.choices)
            for index, choice in enumerate(A.choices):
                candidate = A.apply_query(matrix, 0, choice)
                found = []
                for residue in possible:
                    completion = A.complete(candidate, residue)
                    if completion is not None:
                        counts['residue_completion_hits'] += 1
                        found.append(completion)
                        if len(hits[residue]) < 3:
                            hits[residue].append(dict(query_choice_indices=word + [index],
                                                      completion=completion))
                if len(found) == 4:
                    counts['all_residue_word_hits'] += 1
                    if len(all_hits) < 3:
                        all_hits.append(dict(query_choice_indices=word + [index], completions=found))
            return
        for index, choice in enumerate(A.choices):
            candidate = A.apply_query(matrix, banks[depth], choice)
            candidate = A.route(candidate, routes[depth])
            visit(candidate, word + [index], depth + 1)

    visit(initial, [], 0)
    need(counts['four_query_prefixes'] == 26 ** 4, 'all26^4 prefixes are covered')
    need(counts['covered_five_query_words'] == 26 ** 5, 'all26^5 words are covered')
    # A literal five-query positive control: with identity routes and five
    # identity native placeholders, the same completion test must accept E3.
    target = ({A.Ebase: (0, -16)}, {}, {}, {A.Ebase: (0, -16)})
    need(A.last_row_residues(target) == [0, 1, 2, 3],
         'a valid target is never rejected by the row prune')
    need(all(A.complete(target, s) is not None for s in range(4)),
         'full target control is accepted exactly in every chunk-size residue')
    orbits, pending = [], set(range(64))
    while pending:
        owner = min(pending)
        orbit = sorted({A.ops[g][0][owner] for g in A.free})
        orbits.append(orbit)
        pending.difference_update(orbit)
    return dict(status='PASS_EXACT_PRUNED_DUAL_ROUTE_SCREEN' if dual else 'PASS_EXACT_PRUNED_VARIED_ROUTE_REPLAY',
                no_new_kappa=True, target='diag(E3,E3), everyf>=1, arbitrary independent inputs',
                counts=dict(counts), hits_by_f_mod4=hits, all_residue_word_hits=all_hits,
                bank_pattern=banks,
                route_pattern=['R0', 'S0', 'R1', 'S1'] if dual else ['R0', 'R1', 'R2', 'R0'],
                query_alphabet=A.choices,
                exact_free_ADDRESS_group_order=len(A.free), X_character_orbits=orbits,
                ADDRESS_definition='Rj transvection vector allp+qj; Sj vector allq+pj. Both act bitwise at allf. Enlarged endpoints additionally admit independent S3 permutations ofp/q chunks.',
                all_f_binding='Ni,f=i*(-i*Ni,1)^tensorf. All ADDRESSs and admitted Ai/B queries tensor-lift their exact one-bit monomials. Gaussian proportional-ray phases are folded separately for all4 residues; no f1-only linear relation is used.',
                paid_native_tariff='Each Ni, Aij=NiRjNi^-1 and B=N0R0P2R0N0^-1 is one independently admitted rank2f child with its literal monomial adapters. No dual conjugate query is assumed.',
                prune_proof='Final query acts only onbank0. The two bank1 entries are unchanged, so their nonaccepted tensor rays cannot be repaired. Distinct base rays have independent sufficiently high tensor powers in each residue class. The row test is a necessary all-f condition, not a heuristic.',
                exact_scope='Five queries; fixed alternating banks and the displayed four W routes; query alphabet exactly the serialized26 signed choices; arbitrary outer GL2 over the displayed complete finite ADDRESS group. Additional internal scalar/Pauli/ADDRESS bridges and other bank/route patterns are untested.',
                controls=['Sixteen pruned actual prefixes checked against all26 unpruned last-query completions in all4 residues.',
                          'Exact target diag(E3,E3) accepted by row prune and full unitary endpoint test in all4 residues.'],
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), source_pins=source_pins())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dual', action='store_true')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run(args.dual)))
    path = HERE / ('DUAL-REFLECTION-SCREEN.json' if args.dual else 'PRUNED-VARIED-REPLAY.json')
    if args.write:
        path.write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved pruned route screen differs')
    print(out['status'], json.dumps(out['counts'], sort_keys=True))


if __name__ == '__main__':
    main()
