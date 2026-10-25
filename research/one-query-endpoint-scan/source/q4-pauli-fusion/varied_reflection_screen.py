#!/usr/bin/env python3
"""A varied-route five-query all-f tensor screen, with fused native queries.

Fixed banks alternate0,1,0,1,0. Routes are R0,R1,R2,R0, and query
choices include all nine Ad_Ni(Rj), each priced as one admitted H2.
The added full conjugate N0(R0 P2 R0)N0^-1 is also priced once.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
from unpaired_reflection_screen import TensorBase, rotate, need

HERE = Path(__file__).resolve().parent


class VariedBase(TensorBase):
    def __init__(self):
        super().__init__()
        self.Rs = []
        for q in (1, 3, 5):
            v = sum(1 << i for i in (0, 2, 4, q))
            self.Rs.append(self.intern(tuple(w ^ (v if (w & v).bit_count() & 1 else 0)
                                            for w in range(64)), (0,) * 64))
        self.Ps = []
        for plane in (1, 2):
            p = list(range(6))
            for j in range(2):
                p[j], p[2 * plane + j] = p[2 * plane + j], p[j]
            self.Ps.append(self.intern(tuple(sum(((w >> j) & 1) << p[j] for j in range(6))
                                            for w in range(64)), (0,) * 64))
        self.free = {self.identity}
        todo = [self.identity]
        generators = self.Rs + self.Ps
        for old in todo:
            for g in generators:
                new = self.left(g, old)
                if new not in self.free:
                    self.free.add(new)
                    todo.append(new)
        need(len(self.free) < 10000, 'declared free group stays inside the bounded screen')
        for g in self.free:
            need(self.left(g, self.Ebase) == self.left(self.Ebase, g),
                 'every accepted outer ADDRESS commutes full E3 exactly')
        self.free = sorted(self.free)
        self.accept = {}
        for g in self.free:
            target = self.left(g, self.Ebase)
            ray, phase = self.rays[target]
            need(phase == 0, 'accepted full-native ADDRESS rays have exact zero base phase')
            need(ray not in self.accept, 'distinct ADDRESS completions remain distinct tensor rays')
            self.accept[ray] = g
        self.accept_rays = set(self.accept)
        self.choices = []
        for i, H in enumerate(self.H):
            for negative in (False, True):
                self.choices.append(dict(kind='N', plane=i, negative=negative, operator=H,
                                         scalar_phase=3 if negative else 1))
        for j, R in enumerate(self.Rs):
            for i, H in enumerate(self.H):
                A = self.left(H, self.left(R, H))
                for negative in (False, True):
                    self.choices.append(dict(kind='A', plane=i, reflection=j, negative=negative,
                                             operator=A, scalar_phase=2 if negative else 0))
        RpR = self.left(self.Rs[0], self.left(self.Ps[1], self.Rs[0]))
        B = self.left(self.H[0], self.left(RpR, self.H[0]))
        for negative in (False, True):
            self.choices.append(dict(kind='B_full_conjugate', plane=0, reflection=0,
                                     ADDRESS_plane_swap=2, negative=negative, operator=B,
                                     scalar_phase=2 if negative else 0))
        need(len(self.choices) == 26, 'the declared fused native alphabet has26 choices per fixed bank')

    def apply_query(self, matrix, bank, choice):
        out = list(matrix)
        for col in range(2):
            j = 2 * bank + col
            out[j] = self.left_entry(choice['operator'], matrix[j], choice['scalar_phase'])
        return tuple(out)

    def route(self, matrix, R):
        a, b, c, d = matrix
        Ra, Rb, Rc, Rd = [self.left_entry(R, e) for e in matrix]
        return (self.add_entry((a, 1), (Ra, 1), (c, 1), (Rc, -1)),
                self.add_entry((b, 1), (Rb, 1), (d, 1), (Rd, -1)),
                self.add_entry((a, 1), (Ra, -1), (c, 1), (Rc, 1)),
                self.add_entry((b, 1), (Rb, -1), (d, 1), (Rd, 1)))

    def complete(self, matrix, residue):
        entries = []
        for entry in matrix:
            folded = {}
            for g, z in entry.items():
                ray, phase = self.rays[g]
                a, b = rotate(z, phase * residue)
                c, d = folded.get(ray, (0, 0))
                value = a + c, b + d
                if value == (0, 0):
                    folded.pop(ray, None)
                else:
                    folded[ray] = value
            if any(ray not in self.accept for ray in folded):
                return None
            entries.append({self.accept[ray]: rotate(z, 1) for ray, z in folded.items()})
        # B=E3^-1*candidate has dyadic Gaussian coefficients. The complete
        # candidate and E3 are unitary, so B^-1=B^dagger. Verify that exact
        # group-algebra identity, not merely one finite-dimensional image.
        def inverse(g):
            mapping, phase = self.ops[g]
            need(not any(phase), 'free completion words are literal ADDRESS permutations')
            p = [None] * 64
            for i, j in enumerate(mapping):
                p[j] = i
            return self.intern(tuple(p), (0,) * 64)
        for i in range(2):
            for j in range(2):
                product = {}
                for h in range(2):
                    for g, (a, b) in entries[2 * h + i].items():
                        for k, (c, d) in entries[2 * h + j].items():
                            op = self.left(inverse(g), k)
                            z = a * c + b * d, a * d - b * c
                            e, f = product.get(op, (0, 0))
                            value = e + z[0], f + z[1]
                            if value == (0, 0):
                                product.pop(op, None)
                            else:
                                product[op] = value
                need(product == ({self.identity: (256, 0)} if i == j else {}),
                     'found full ADDRESS-group outer completion is unitary in the exact tensor group algebra')
        return dict(f_mod4=residue, common_denominator=16,
                    entries=[[[g, list(z)] for g, z in sorted(entry.items())] for entry in entries],
                    inverse='Conjugate transpose and invert each displayed literal ADDRESS word.')


def run():
    A = VariedBase()
    initial = ({A.identity: (1, 0)}, {}, {}, {A.identity: (1, 0)})
    routes = [0, 1, 2, 0]
    banks = [0, 1, 0, 1, 0]
    counts = Counter()
    hits = {s: [] for s in range(4)}
    all_hits = []
    def visit(matrix, word, depth):
        if depth == 5:
            counts['words'] += 1
            if A.singleton_obstruction(matrix):
                counts['singleton_ray_rejections'] += 1
                return
            found = []
            for residue in range(4):
                completion = A.complete(matrix, residue)
                if completion is not None:
                    counts['residue_hits'] += 1
                    found.append(completion)
                    if len(hits[residue]) < 3:
                        hits[residue].append(dict(query_choice_indices=word, completion=completion))
            if len(found) == 4:
                counts['all_residue_hits'] += 1
                if len(all_hits) < 3:
                    all_hits.append(dict(query_choice_indices=word, completions=found))
            return
        for index, choice in enumerate(A.choices):
            next_matrix = A.apply_query(matrix, banks[depth], choice)
            if depth < 4:
                next_matrix = A.route(next_matrix, A.Rs[routes[depth]])
            visit(next_matrix, word + [index], depth + 1)
    visit(initial, [], 0)
    need(counts['words'] == 26 ** 5, 'every declared varied-route fused-native word is covered')
    return dict(status='PASS_EXACT_BOUNDED_VARIED_REFLECTION_SCREEN', no_new_kappa=True,
                words=counts['words'], singleton_ray_rejections=counts['singleton_ray_rejections'],
                residue_completion_hits=counts['residue_hits'], all_residue_word_hits=counts['all_residue_hits'],
                hits_by_f_mod4=hits, complete_word_hits=all_hits,
                target='diag(E3,E3), E3=N0*N1*N2; five rank2f native queries versus stock6 rank2f.',
                bank_pattern=banks, routing_reflection_pattern=routes,
                query_alphabet=A.choices,
                exact_free_outer_ADDRESS_group_order=len(A.free),
                free_outer_group_generators='Whole-plane swaps P01/P02 and the3 unpaired reflections Rj withvj=p0+p1+p2+qj.',
                free_outer_group_operators=[dict(index=g, X_character_permutation=list(A.ops[g][0])) for g in A.free],
                tensor_model=dict(base_dimension=64, exact_monomials=len(A.ops), exact_rays=len(A.ray_ids)),
                all_f_proof='Uses the exact tensor-base and Gaussian phase folding of unpaired_reflection_screen.py. Every accepted endpoint is over the complete generated native-zero ADDRESS group, not a short palette. E3 commutes that group, so arbitrary left/right GL2 endpoints reduce to the tested right completion. Distinct tensor rays are not identified using f1 linear relations. Every admitted Aij and the full conjugateB is charged once using its independent physical native recipe.',
                limits=['Fixed alternating bank pattern and fixed four-route sequence only; this is not all possible five-query words.',
                        'Extra internal scalar bank phases, PauliZ routes, other ADDRESSs or additional route slots are outside the declared grammar.',
                        'A positive group-algebra endpoint still needs its complete literal dyadic ADD/ADDRESS factorization before being priced as a caller.'],
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_pins=[dict(path=str(HERE / 'unpaired_reflection_screen.py'),
                                 sha256=hashlib.sha256((HERE / 'unpaired_reflection_screen.py').read_bytes()).hexdigest())])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'VARIED-REFLECTION-SCREEN.json'
    if args.write:
        path.write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved varied reflection screen differs')
    print(out['status'], 'words', out['words'], 'all-f hits', out['all_residue_word_hits'],
          'residue hits', out['residue_completion_hits'])


if __name__ == '__main__':
    main()
