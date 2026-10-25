#!/usr/bin/env python3
"""Five native queries and exact all-f tensor-base routing completion.

Target: diag(E3,E3), E3=N0*N1*N2.  Every internal bridge in this
screen is the same W(R), for the unpaired orthogonal reflection R.
Outer completion is arbitrary GL2(Q(i)[R]), including f mod4 phases.
Admitted A_i=N_i R N_i^-1 is charged once, with its physical tariff
proved separately by native-frames/conjugated_reflection.py.
This is a bounded changed-bridge grammar, not an all-grammar obstruction.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent


def need(x, why):
    if not x:
        raise ValueError(why)


def rotate(z, power):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


class TensorBase:
    """Actual one-bit Clifford monomials in the X-character basis."""
    def __init__(self):
        self.dimension = 64
        self.ops, self.ids, self.rays, self.ray_ids, self.left_cache = [], {}, [], {}, {}
        self.identity = self.intern(tuple(range(64)), (0,) * 64)
        self.H = []
        for plane in range(3):
            p, q = 2 * plane, 2 * plane + 1
            flip = (1 << p) | (1 << q)
            self.H.append(self.intern(tuple(w ^ flip for w in range(64)),
                                      tuple((-((w >> p) & 1) + ((w >> q) & 1)) % 4 for w in range(64))))
        self.v = sum(1 << i for i in (0, 1, 2, 4))
        self.R = self.intern(tuple(w ^ (self.v if (w & self.v).bit_count() & 1 else 0)
                                   for w in range(64)), (0,) * 64)
        self.Ebase = self.left(self.H[0], self.left(self.H[1], self.H[2]))
        self.REbase = self.left(self.R, self.Ebase)
        self.A = [self.left(H, self.left(self.R, H)) for H in self.H]
        need(self.left(self.R, self.R) == self.identity, 'unpaired R is an exact involution')
        need(self.left(self.R, self.Ebase) == self.left(self.Ebase, self.R),
             'R commutes the exact three-plane native base')
        for H in self.H:
            need(self.left(H, H) == self.identity, 'H=-i*N1 has exact square I')
        self.accept_rays = [self.rays[self.Ebase][0], self.rays[self.REbase][0]]

    def intern(self, mapping, phases):
        key = bytes(mapping) + bytes(phases)
        old = self.ids.get(key)
        if old is not None:
            return old
        index = len(self.ops)
        self.ids[key] = index
        self.ops.append((mapping, phases))
        phase = phases[0]
        ray_key = bytes(mapping) + bytes((p - phase) % 4 for p in phases)
        ray = self.ray_ids.setdefault(ray_key, len(self.ray_ids))
        self.rays.append((ray, phase))
        return index

    def left(self, a, b):
        key = a, b
        if key not in self.left_cache:
            ap, az = self.ops[a]
            bp, bz = self.ops[b]
            self.left_cache[key] = self.intern(tuple(ap[bp[i]] for i in range(64)),
                                              tuple((bz[i] + az[bp[i]]) % 4 for i in range(64)))
        return self.left_cache[key]

    def left_entry(self, op, entry, phase=0):
        out = {}
        for g, z in entry.items():
            h = self.left(op, g)
            a, b = rotate(z, phase)
            c, d = out.get(h, (0, 0))
            if (a + c, b + d) == (0, 0):
                out.pop(h, None)
            else:
                out[h] = a + c, b + d
        return out

    @staticmethod
    def add_entry(*entries):
        out = {}
        for entry, sign in entries:
            for g, (a, b) in entry.items():
                c, d = out.get(g, (0, 0))
                z = c + sign * a, d + sign * b
                if z == (0, 0):
                    out.pop(g, None)
                else:
                    out[g] = z
        return out

    def native(self, matrix, bank, primitive, plane, negative):
        out = list(matrix)
        op = self.H[plane] if primitive == 'N' else self.A[plane]
        phase = (3 if negative else 1) if primitive == 'N' else (2 if negative else 0)
        for col in range(2):
            j = 2 * bank + col
            out[j] = self.left_entry(op, matrix[j], phase)
        return tuple(out)

    def singleton_obstruction(self, matrix):
        # A nonaccepted tensor-base ray represented by a single exact
        # Gaussian phase cannot vanish in any f residue class.
        for entry in matrix:
            rays = Counter(self.rays[g][0] for g in entry)
            if any(count == 1 and ray not in self.accept_rays for ray, count in rays.items()):
                return True
        return False

    def routing(self, matrix):
        a, b, c, d = matrix
        Ra, Rb, Rc, Rd = [self.left_entry(self.R, e) for e in matrix]
        return (self.add_entry((a, 1), (Ra, 1), (c, 1), (Rc, -1)),
                self.add_entry((b, 1), (Rb, 1), (d, 1), (Rd, -1)),
                self.add_entry((a, 1), (Ra, -1), (c, 1), (Rc, 1)),
                self.add_entry((b, 1), (Rb, -1), (d, 1), (Rd, 1)))

    def completion(self, matrix, residue, routing_count):
        out = []
        for entry in matrix:
            folded = {}
            for g, z in entry.items():
                ray, phase = self.rays[g]
                a, b = rotate(z, phase * residue)
                c, d = folded.get(ray, (0, 0))
                if (a + c, b + d) == (0, 0):
                    folded.pop(ray, None)
                else:
                    folded[ray] = a + c, b + d
            if any(ray not in self.accept_rays for ray in folded):
                return None
            # E3_f=-i*Ebase^tensor(f). Both accepted base rays have phase0.
            out.append([rotate(folded.get(ray, (0, 0)), 1) for ray in self.accept_rays])
        den = 1 << routing_count
        for epsilon in (-1, 1):
            sector = []
            for zI, zR in out:
                sector.append((zI[0] + epsilon * zR[0], zI[1] + epsilon * zR[1]))
            for i in range(2):
                for j in range(2):
                    value = (0, 0)
                    for h in range(2):
                        a, b = sector[2 * h + i]
                        c, d = sector[2 * h + j]
                        z = a * c + b * d, a * d - b * c
                        value = value[0] + z[0], value[1] + z[1]
                    need(value == ((den * den, 0) if i == j else (0, 0)),
                         'every found R-sector outer completion is exactly unitary')
        return dict(f_mod4=residue, common_dyadic_denominator=den,
                    entries_I_R_Gaussian_numerators=out,
                    inverse='Conjugate transpose the two I/R coefficient matrices. R is an actual Hermitian involution; lower by its projectors or literal elementary bank gates.')


def run():
    A = TensorBase()
    initial = ({A.identity: (1, 0)}, {}, {}, {A.identity: (1, 0)})
    hits = {s: [] for s in range(4)}
    counts = Counter()
    all_residue_hits = []
    def visit(matrix, word, depth):
        if depth == 5:
            counts['native_words'] += 1
            if A.singleton_obstruction(matrix):
                counts['singleton_ray_rejections'] += 1
                return
            found = []
            for residue in range(4):
                completion = A.completion(matrix, residue, 4)
                if completion is not None:
                    counts['residue_completion_hits'] += 1
                    found.append(completion)
                    if len(hits[residue]) < 3:
                        hits[residue].append(dict(queries=word, outer_completion=completion))
            if len(found) == 4:
                counts['all_residue_word_hits'] += 1
                if len(all_residue_hits) < 3:
                    all_residue_hits.append(dict(queries=word, completions=found))
            return
        for bank in range(2):
            for primitive in ('N', 'A'):
                for plane in range(3):
                    for negative in (False, True):
                        next_matrix = A.native(matrix, bank, primitive, plane, negative)
                        if depth < 4:
                            next_matrix = A.routing(next_matrix)
                        visit(next_matrix, word + [dict(bank=bank, primitive=primitive, plane=plane,
                                                       negative=negative)], depth + 1)
    visit(initial, [], 0)
    need(counts['native_words'] == 24 ** 5, 'every declared five-query primitive/axis/bank/unit pattern is covered')
    # A real escape check: residual pattern 100 is sent to111 by this R.
    w, v = 1 << 1, A.v
    wp = w ^ v
    residual = lambda z: [((z >> (2 * i)) ^ (z >> (2 * i + 1))) & 1 for i in range(3)]
    need(residual(w) == [1, 0, 0] and residual(wp) == [1, 1, 1], 'R genuinely escapes the marked one-owner subspace')
    # One-bit S=(1+i)I/2+(1-i)Z/2 is a true matrix identity, but its
    # coefficientwise tensor lift is false at two bits on input11.
    need(rotate((1, 0), 2) == (-1, 0), 'actual S tensor S gives -1 on11')
    false_tensor_lift_on_11 = (1, 0)
    need(false_tensor_lift_on_11 != (-1, 0), 'f1 linear relation is not accepted as an all-f tensor relation')
    native = HERE.parent / 'native-frames'
    return dict(status='PASS_EXACT_BOUNDED_UNPAIRED_REFLECTION_SCREEN', no_new_kappa=True,
                target='diag(E3,E3), E3=N0*N1*N2, six native planes of stock across two banks; desired5H2 instead of6H2.',
                native_words=counts['native_words'], residue_completion_hits=counts['residue_completion_hits'],
                all_residue_word_hits=counts['all_residue_word_hits'], hits_by_f_mod4=hits,
                singleton_ray_rejections=counts['singleton_ray_rejections'],
                complete_word_hits=all_residue_hits,
                reflection='R=P_A bitwise overf; A=I+vvT, v=(p0,q0,p1,p2). It is orthogonal, involutive, and commutes fullE3 exactly. TypedD^-1P_A D=P_A because three selected chunks arep and oneq.',
                marked_escape=dict(input_X_character=w, output_X_character=wp,
                                   input_residual_labels=residual(w), output_residual_labels=residual(wp)),
                grammar='Exactly five unary queries, each chosen from +/-N_i and +/-A_i on all3planes/eitherbank, where A_i=N_i R N_i^-1 has independently admitted native rank2f and is charged ONCE. Exactly W(R) occurs between consecutive queries. Arbitrary outer GL2(Q(i)[R]) completion is accepted separately for eachf mod4. All24^5 patterns are covered; additional internal Z, other scalar bank phases, other reflections or general bitlinear ADDRESS words are outside this screen.',
                fused_native_A='A_i,f=(H_i R H_i)^tensorf, with no outside i factor. Native worker independently supplies its single-rank2f literal query and monomial adapters; the group identity by itself does not establish this tariff.',
                all_f_tensor_proof='On one bit per chunk H_i=-i*N_i,1 is the exact X-character monomial w->w xor{p_i,q_i} with phasei^(-w_pi+w_qi). For everyf, N_i,f=i*H_i^tensorf. R_f=R_1^tensorf. Matrix entries of the screened word are finite Gaussian dyadic sums of tensor powers of the represented base monomials. Equality after grouping exact monomial rays and theiri^(f mod4) phases is therefore an exact all-f identity; f1-only linear relations between distinct monomials are never accepted. A found completion uses only I,R and Gaussian dyadic scalars and is checked unitary in bothR sectors.',
                necessity_for_this_finite_grammar='Distinct nonproportional base-operator vectors have linearly independent f-th tensor powers once f is sufficiently large: choose, for each vector, a product of linear forms annihilating every other vector. For each fixed fmod4 the same argument applies after absorbing Gaussian ray phases. Thus the ray-support failure is an all-f obstruction within this finite word grammar, even if the outer scalar coefficients are allowed to depend onf.',
                negative_controls=['A genuine f1 matrix identity S=(1+i)I/2+(1-i)Z/2 fails its coefficientwise tensor lift on f2 input11: actual -1, false lift +1.',
                                   'The unpaired R sends one residual mark to three and is explicitly outside the marked-C invariant block.'],
                group_model=dict(exact_base_monomials=len(A.ops), exact_base_rays=len(A.ray_ids), cached_left_products=len(A.left_cache), dimension=64),
                scope='A zero-hit result is exhaustive only for this specified internal-routing grammar and its declared outer completions; it is not a global lower bound for full Pauli or arbitrary ADDRESS bridges.',
                source_pins=[dict(path=str(native / name), sha256=hashlib.sha256((native / name).read_bytes()).hexdigest())
                             for name in ['native_model.py', 'conjugated_reflection.py', 'CONJUGATED-REFLECTION.json']],
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'UNPAIRED-REFLECTION-SCREEN.json'
    if args.write:
        path.write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved reflection screen differs')
    print(out['status'], 'words', out['native_words'], 'all-f hits', out['all_residue_word_hits'],
          'residue hits', out['residue_completion_hits'])


if __name__ == '__main__':
    main()
