"""Exact finite Boolean/bitvector model for normalized paid-factor words.

Brian Ross, with substantial OpenAI Codex assistance. Apache-2.0.
Packed group convention follows the credited seed18/length10 predecessors.
"""
import functools
import operator

ID = 273
PAIRS = [(i, j) for i in range(3) for j in range(3) if i != j]
LABELS = [ID ^ (1 << (3 * i + j)) for i, j in PAIRS]
TARGET = (225, 226, ID)


def multiply(a, b):
    out = 0
    for r in range(3):
        row = 0
        for c in range(3):
            if a & (1 << (3 * r + c)):
                row ^= (b >> (3 * c)) & 7
        out |= row << (3 * r)
    return out


class Algebra:
    def __init__(self):
        paths = {ID: []}
        queue = [ID]
        for state in queue:
            for k, label in enumerate(LABELS):
                image = multiply(label, state)
                if image not in paths:
                    paths[image] = paths[state] + [k]
                    queue.append(image)
        assert len(queue) == 168
        self.group = sorted(queue)
        self.index = {x: k for k, x in enumerate(self.group)}
        self.paths = paths
        self.permutations = [[self.index[multiply(g, x)] for x in self.group]
                             for g in LABELS]
        # All six g are involutions: pullback and pushforward coincide.
        assert all(all(p[p[k]] == k for k in range(168))
                   for p in self.permutations)
        self.generators = [(u, v, i, j) for u in range(1, 8)
                           for v in range(1, 8) if (u & v).bit_count() % 2
                           for i, j in PAIRS]
        assert len(self.generators) == 168

    def endpoint(self, target=TARGET):
        return tuple((1 << self.index[target[r]]) if r == c else 0
                     for r in range(3) for c in range(3))

    def translate(self, poly, label):
        answer = 0
        p = self.permutations[label]
        while poly:
            bit = poly & -poly
            poly ^= bit
            answer ^= 1 << p[bit.bit_length() - 1]
        return answer

    def step(self, state, gate):
        u, v, i, j = gate
        label = PAIRS.index((i, j))
        out = list(state)
        for c in range(3):
            source = functools.reduce(operator.xor,
                      (state[3 * k + c] for k in range(3) if v & (1 << k)), 0)
            delta = source ^ self.translate(source, label)
            for r in range(3):
                if u & (1 << r):
                    out[3 * r + c] ^= delta
        return tuple(out)

    def replay(self, word):
        state = self.endpoint((ID, ID, ID))
        for gate in word:
            state = self.step(state, gate)
        return state

    def direct_word(self, target=TARGET):
        return [(1 << r, 1 << r, *PAIRS[k]) for r in range(3)
                for k in self.paths[target[r]]]


def support_masks(algebra, length, target=TARGET):
    """Necessary coefficient supports, proved in README; no word is discarded."""
    return [[sum(1 << k for k, g in enumerate(algebra.group)
                 if len(algebra.paths[g]) <= t and
                 g in {multiply(h, target[c]) for h in algebra.group
                       if len(algebra.paths[h]) <= length - t})
             for c in range(3)] for t in range(length + 1)]


def build(length=8, target=TARGET, fixed_word=None, support_bounds=False,
          expected_state=None, engine="qfbv"):
    import z3
    a = Algebra()
    zero = z3.BitVecVal(0, 168)
    if engine == "qfbv":
        solver = z3.SolverFor("QF_BV")
    elif engine == "bitblast":
        # Retain explicit intermediate state equalities, avoiding solve-eqs
        # substitution before bit-blasting. Formula/domain are unchanged.
        solver = z3.Then("simplify", "bit-blast", "sat").solver()
    else:
        raise ValueError("unknown engine")
    states = [[z3.BitVec(f"s_{t}_{r}_{c}", 168)
               for r in range(3) for c in range(3)] for t in range(length + 1)]
    controls = []
    for x, value in zip(states[0], a.endpoint((ID, ID, ID))):
        solver.add(x == z3.BitVecVal(value, 168))
    for t in range(length):
        u = [z3.Bool(f"u_{t}_{k}") for k in range(3)]
        v = [z3.Bool(f"v_{t}_{k}") for k in range(3)]
        label = z3.BitVec(f"g_{t}", 3)
        controls.append((u, v, label))
        solver.add(z3.Xor(z3.Xor(z3.And(u[0], v[0]), z3.And(u[1], v[1])),
                         z3.And(u[2], v[2])))
        solver.add(z3.ULT(label, z3.BitVecVal(6, 3)))
        for c in range(3):
            source = z3.BitVec(f"q_{t}_{c}", 168)
            solver.add(source == functools.reduce(operator.xor,
                       [z3.If(v[k], states[t][3 * k + c], zero)
                        for k in range(3)]))
            translations = [z3.Concat(*[z3.Extract(p[k], p[k], source)
                                         for k in reversed(range(168))])
                            for p in a.permutations]
            shifted = translations[5]
            for k in reversed(range(5)):
                shifted = z3.If(label == k, translations[k], shifted)
            delta = source ^ shifted
            for r in range(3):
                solver.add(states[t + 1][3 * r + c] ==
                           states[t][3 * r + c] ^ z3.If(u[r], delta, zero))
        if fixed_word is not None:
            fu, fv, fi, fj = fixed_word[t]
            for k in range(3):
                solver.add(u[k] == bool(fu & (1 << k)))
                solver.add(v[k] == bool(fv & (1 << k)))
            solver.add(label == PAIRS.index((fi, fj)))
    endpoint = a.endpoint(target) if expected_state is None else expected_state
    for x, value in zip(states[-1], endpoint):
        solver.add(x == z3.BitVecVal(value, 168))
    if support_bounds:
        if expected_state is not None:
            raise ValueError("support bounds only implemented for monomial diagonal endpoints")
        masks = support_masks(a, length, target)
        for t in range(length + 1):
            for r in range(3):
                for c in range(3):
                    solver.add(states[t][3 * r + c] &
                               z3.BitVecVal(((1 << 168) - 1) ^ masks[t][c], 168) == zero)
    metadata = {
        "length": length, "group_order": 168, "paid_factor_alphabet": 168,
        "state_bitvectors": 9 * (length + 1), "source_bitvectors": 3 * length,
        "bitvector_width": 168, "choice_boolean_bits": 9 * length,
        "explicit_bits_before_simplification": 168 * (12 * length + 9) + 9 * length,
        "assertions": len(solver.assertions()), "symmetry_reductions": [],
        "domain_restrictions_beyond_claim": [],
        "engine": engine,
        "admissible_pruning": ["forward_backward_coefficient_support"] if support_bounds else [],
    }
    if support_bounds:
        metadata["support_bits_per_column_by_time"] = [
            [x.bit_count() for x in row] for row in masks]
        metadata["potentially_nonzero_state_bits"] = 3 * sum(
            x.bit_count() for row in masks for x in row)
    return solver, controls, metadata


def extract_word(model, controls):
    import z3
    result = []
    for u, v, label in controls:
        ui = sum(int(z3.is_true(model.eval(u[k], model_completion=True))) << k
                 for k in range(3))
        vi = sum(int(z3.is_true(model.eval(v[k], model_completion=True))) << k
                 for k in range(3))
        result.append([ui, vi, *PAIRS[model.eval(label).as_long()]])
    return result
