"""Exact completed-downset and active-fragment checks for the full schedule.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from fractions import Fraction as Q

from exact import C, Mat, eye, multiply, need, upper, vector_hash
from verify import operator
from verify_triangle import eliminate


def blockdiag(left, right):
    a, b = len(left), len(right)
    return Mat([[left[i][j] if i < a and j < a
                 else right[i - a][j - a] if i >= a and j >= a else C()
                 for j in range(a + b)] for i in range(a + b)])


def shear(matrix, upper_bank=False):
    m = len(matrix)
    result = eye(2 * m)
    for i in range(m):
        for j in range(m):
            result[i if upper_bank else m + i][m + j if upper_bank else j] = matrix[i][j]
    return result


def embed(matrix, indices, n):
    result = eye(n)
    for i, row in enumerate(indices):
        for j, column in enumerate(indices):
            result[row][column] = matrix[i][j]
    return result


def frobenius2(matrix):
    return sum((x.norm2() for row in matrix for x in row), Q(0))


class Frontier:
    def __init__(self, builder, plan):
        self.builder, self.plan, self.n = builder, plan, builder.bound["n"]
        self.atoms = {a["id"]: a for a in plan.atoms}
        self.subsets, self.factors, self.actual_atoms = {}, {}, {}
        self._factor(0, self.n)

    def _factor(self, a, b):
        k = b - a
        ids = {key for key, atom in self.atoms.items()
               if a <= atom["interval"][0] and atom["interval"][1] <= b}
        self.subsets[a, b] = ids
        if k == 1:
            need(ids == {f"D:{a}"}, "one scalar leaf call")
            factors = (eye(1), self.atoms[f"D:{a}"]["ideal"], eye(1))
        else:
            c = (a + b) // 2
            left, right = self._factor(a, c), self._factor(c, b)
            need({f"R:{a}:{b}", f"L:{a}:{b}"}.issubset(ids), "two full node shears")
            lower = shear(self.atoms[f"L:{a}:{b}"]["ideal"])
            upper_bank = shear(self.atoms[f"R:{a}:{b}"]["ideal"], True)
            factors = (multiply(lower, blockdiag(left[0], right[0])),
                       blockdiag(left[1], right[1]),
                       multiply(blockdiag(left[2], right[2]), upper_bank))
        need(multiply(multiply(factors[0], factors[1]), factors[2])
             == self.builder.nodes[a, b]["matrix"], "exact scalar LDU factorization")
        chi = self.builder.bound["conditioning"]
        w, v = 3 * self.n * chi ** 2, 6 * self.n * chi ** 4
        for factor in (factors[0], factors[2]):
            need(frobenius2(factor) <= k * w ** 2
                 and frobenius2(eliminate(factor)) <= k * v ** 2,
                 "scalar LDU norm consequences")
        self.factors[a, b] = factors
        return factors

    def endpoints(self, a, b):
        if b - a == 1:
            atom = self.atoms[f"D:{a}"]
            return atom["start"], atom["stop"]
        return self.atoms[f"R:{a}:{b}"]["start"], self.atoms[f"L:{a}:{b}"]["stop"]

    def schedule(self):
        n = self.n
        need(len(self.plan.atoms) == 3 * n - 2 and len(self.atoms) == 3 * n - 2,
             "full atomic call inventory")
        for (a, b), node in self.builder.nodes.items():
            if b - a == 1:
                start, stop = self.endpoints(a, b)
                need(stop == start + 1, "one full scalar layer")
                continue
            c = (a + b) // 2
            right, left = self.atoms[f"R:{a}:{b}"], self.atoms[f"L:{a}:{b}"]
            lstart, lend = self.endpoints(a, c)
            rstart, rend = self.endpoints(c, b)
            need(lstart == rstart == right["stop"] and left["start"] == max(lend, rend),
                 "literal full parallel timing")
            need(left["stop"] - right["start"] == node["layers"], "source node layer count")
        max_active, multi_nonempty = 0, False
        for cut in range(len(self.plan) + 1):
            completed = {a["id"] for a in self.plan.atoms if a["stop"] <= cut}
            active = [a for a in self.plan.atoms if a["start"] <= cut < a["stop"]]
            used = set()
            for atom in active:
                need(not used.intersection(atom["indices"]), "disjoint active full calls")
                used.update(atom["indices"])
            max_active = max(max_active, len(active))
            multi_nonempty |= sum(a["start"] < cut for a in active) >= 2
            # Parent upper calls precede a completed or active descendant.
            for atom in active + [self.atoms[x] for x in completed]:
                a, b = atom["interval"]
                for x, y in self.builder.nodes:
                    if x <= a and b <= y and (x, y) != (a, b):
                        need(f"R:{x}:{y}" in completed, "completed ancestor upper call")
                if atom["kind"] == "lower":
                    need(self.subsets[a, b] - {atom["id"]} <= completed,
                         "lower call waits for its subtree")
        unequal = sum(self.endpoints(a, (a + b) // 2)[1] - self.endpoints(a, (a + b) // 2)[0]
                      != self.endpoints((a + b) // 2, b)[1] - self.endpoints((a + b) // 2, b)[0]
                      for a, b in self.builder.nodes if b - a > 1)
        return dict(max_active_calls=max_active, simultaneous_nonempty_fragments=multi_nonempty,
                    unequal_sibling_nodes=unequal,
                    zero_layer_calls=sum(a["start"] == a["stop"] for a in self.plan.atoms))

    def downsets(self, a=0, b=None):
        b = self.n if b is None else b
        if b - a == 1:
            return [set(), {f"D:{a}"}]
        c = (a + b) // 2
        return [set()] + [
            left | right | {f"R:{a}:{b}"}
            for left in self.downsets(a, c) for right in self.downsets(c, b)
        ] + [self.subsets[a, b].copy()]

    def _partial(self, completed, a, b):
        ids = self.subsets[a, b] & completed
        if not ids:
            return eye(b - a), eye(b - a), eye(b - a), [(a, b)]
        if b - a == 1:
            need(ids == {f"D:{a}"}, "legal leaf downset")
            return eye(1), self.atoms[f"D:{a}"]["ideal"], eye(1), [(a, b)]
        need(f"R:{a}:{b}" in ids, "downset includes upper predecessor")
        c = (a + b) // 2
        l = self._partial(completed, a, c)
        r = self._partial(completed, c, b)
        low = blockdiag(l[0], r[0])
        if f"L:{a}:{b}" in ids:
            need(ids == self.subsets[a, b], "completed lower closes its subtree")
            low = multiply(shear(self.atoms[f"L:{a}:{b}"]["ideal"]), low)
        return (low, blockdiag(l[1], r[1]),
                multiply(blockdiag(l[2], r[2]), shear(self.atoms[f"R:{a}:{b}"]["ideal"], True)),
                l[3] + r[3])

    def check_downset(self, completed):
        need(completed <= self.atoms.keys(), "known downset calls")
        low, diagonal, up, frontier = self._partial(completed, 0, self.n)
        product = eye(self.n)
        for atom in self.plan.atoms:
            if atom["id"] in completed:
                local = atom["ideal"] if atom["kind"] == "leaf" else shear(atom["ideal"])
                ids = [self.builder.positions[i] for i in atom["indices"]]
                product = multiply(embed(local, ids, self.n), product)
        need(multiply(multiply(low, diagonal), up) == product, "exact downset LDU identity")
        front = eye(self.n)
        for a, b in frontier:
            part = self.factors[a, b][2]
            for i in range(a, b):
                for j in range(a, b):
                    front[i][j] = part[i - a][j - a]
        need(multiply(front, up) == self.factors[0, self.n][2], "exact upper frontier identity")
        bound = self.builder.bound["completed_prefix_bound"]
        need(max(frobenius2(product), frobenius2(eliminate(product))) <= self.n * bound ** 2,
             "polynomial completed-prefix consequence")
        return dict(completed=sorted(completed), frontier=[list(x) for x in frontier],
                    prefix_sha256=vector_hash([x for row in product for x in row]))

    def actual_endpoint(self, atom):
        if atom["id"] not in self.actual_atoms:
            local = operator(atom["local_plan"], len(atom["indices"]))
            self.actual_atoms[atom["id"]] = embed(local, atom["indices"], self.n)
        return self.actual_atoms[atom["id"]]

    def physical_cut(self, cut):
        completed = {a["id"] for a in self.plan.atoms if a["stop"] <= cut}
        active = [a for a in self.plan.atoms if a["start"] <= cut < a["stop"]]
        active_ids = {a["id"] for a in active}
        done, remaining = eye(self.n), eye(self.n)
        for atom in self.plan.atoms:
            if atom["id"] in completed:
                done = multiply(self.actual_endpoint(atom), done)
            elif atom["id"] not in active_ids:
                remaining = multiply(self.actual_endpoint(atom), remaining)
        fragments, tails = eye(self.n), eye(self.n)
        for atom in active:
            offset, k = cut - atom["start"], len(atom["indices"])
            front = operator(atom["local_plan"][:offset], k)
            tail = operator(atom["local_plan"][offset:], k)
            fragments = multiply(embed(front, atom["indices"], self.n), fragments)
            tails = multiply(embed(tail, atom["indices"], self.n), tails)
        prefix, suffix = operator(self.plan[:cut], self.n), operator(self.plan[cut:], self.n)
        need(prefix == multiply(fragments, done), "exact active-prefix factorization")
        need(suffix == multiply(remaining, tails), "exact active-suffix factorization")
        bound = self.builder.bound["execution_bound"]
        peak = max(frobenius2(x) for x in (prefix, suffix, eliminate(prefix), eliminate(suffix)))
        need(peak <= self.n * bound ** 2, "physical prefix/suffix norm consequences")
        return dict(cut=cut, completed=len(completed), active=sorted(active_ids),
                    nonempty_active_prefixes=sum(a["start"] < cut for a in active),
                    max_frobenius_squared_upper=str(upper(peak)))
