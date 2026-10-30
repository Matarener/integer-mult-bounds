#!/usr/bin/env python3
"""Joint side/pair-total monotone DAG with a fully paid copied output interface.

The tensor recurrence and equal-support interning follow the pinned upstream
ternary_side.py / disjoint_tensor.py construction. The additional total query,
shared observation word, explicit enclosure frames and invoice are this probe.
No installed numerical packages and no external files are needed at replay.
"""
from array import array
from collections import Counter
from functools import cache
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from math import comb, exp, log
from pathlib import Path
import argparse
import json
import sys


def require(p, message):
    if not p:
        raise ValueError(message)


def mask(t):
    return sum(1 << i for i in t)


@cache
def subsets(points, size):
    return tuple(mask(t) for t in combinations(points, size))


@cache
def tensor_plan(n, a, b):
    require(0 <= a <= n and 0 <= b <= n, "Invalid tensor size")
    if a+b > n:
        return 0, "empty"
    if not a:
        return 0, "copy"
    if not b:
        return comb(n, a)-1, "sum"
    best = comb(n, b)*(comb(n-b, a)-1), "rows"
    for left in range(1, n//2+1):
        right = n-left
        cost = 0
        for j in range(max(0, b-right), min(left, b)+1):
            parts = 0
            for i in range(max(0, a-right), min(left, a)+1):
                if i+j > left or a-i+b-j > right:
                    continue
                A = tensor_plan(left, i, j)[0]
                B = tensor_plan(right, a-i, b-j)[0]
                cost += min(comb(right, a-i)*A+comb(left, j)*B,
                            comb(left, i)*B+comb(right, b-j)*A)
                parts += 1
            if parts:
                cost += comb(left, j)*comb(right, b-j)*(parts-1)
        if cost < best[0]:
            best = cost, left
    return best


class TripleTemplate:
    """Cancellation-free triple queries, augmented by the complete total."""
    def __init__(self, h):
        self.inputs = list(subsets(tuple(range(h)), 3))
        self.support = [0]+[1 << i for i in range(len(self.inputs))]
        self.args = [None]*len(self.support)
        self.lookup = {s: i for i, s in enumerate(self.support)}
        values = {s: i+1 for i, s in enumerate(self.inputs)}
        self.outputs = self.transform(tuple(range(h)), 3, 3, values)
        self.total_root = self.total(list(values.values()))
        self.active = set()
        todo = [*self.outputs.values(), self.total_root]
        while todo:
            node = todo.pop()
            if not node or node in self.active:
                continue
            self.active.add(node)
            if self.args[node]:
                todo.extend(self.args[node])
        for node in sorted(self.active):
            if self.args[node]:
                a, b = self.args[node]
                require(a < node and b < node, "Noncausal template edge")
                require(not self.support[a] & self.support[b], "Overlapping summands")
                require(self.support[node] == self.support[a] | self.support[b],
                        "Wrong template support")
        all_inputs = (1 << len(self.inputs))-1
        require(self.support[self.total_root] == all_inputs, "Wrong total query")
        for t, node in self.outputs.items():
            expected = sum(1 << i for i, s in enumerate(self.inputs) if not s & t)
            require(self.support[node] == expected, "Wrong disjoint-triple query")

    def add(self, a, b):
        if not a or not b:
            return a or b
        require(not self.support[a] & self.support[b], "Addition is not cancellation-free")
        s = self.support[a] | self.support[b]
        node = self.lookup.get(s)
        if node is None:
            node = len(self.support)
            self.lookup[s] = node
            self.support.append(s)
            self.args.append((a, b))
        return node

    def total(self, nodes):
        if not nodes:
            return 0
        if len(nodes) == 1:
            return nodes[0]
        m = len(nodes)//2
        return self.add(self.total(nodes[:m]), self.total(nodes[m:]))

    def transform(self, points, a, b, values):
        n = len(points)
        _, method = tensor_plan(n, a, b)
        outputs = subsets(points, b)
        if method == "empty":
            return {t: 0 for t in outputs}
        if method == "copy":
            return {t: values[0] for t in outputs}
        if method == "sum":
            return {0: self.total(list(values.values()))}
        if method == "rows":
            return {t: self.total([values[s] for s in subsets(points, a) if not s & t])
                    for t in outputs}
        left, right = points[:method], points[method:]
        l, r = len(left), len(right)
        terms = {t: [] for t in outputs}
        for j in range(max(0, b-r), min(l, b)+1):
            for i in range(max(0, a-r), min(l, a)+1):
                if i+j > l or a-i+b-j > r:
                    continue
                A = tensor_plan(l, i, j)[0]
                B = tensor_plan(r, a-i, b-j)[0]
                if comb(r, a-i)*A+comb(l, j)*B <= comb(l, i)*B+comb(r, b-j)*A:
                    middle = {s: self.transform(left, i, j,
                              {u: values[u | s] for u in subsets(left, i)})
                              for s in subsets(right, a-i)}
                    for t in subsets(left, j):
                        row = self.transform(right, a-i, b-j,
                                             {s: v[t] for s, v in middle.items()})
                        for u, node in row.items():
                            terms[t | u].append(node)
                else:
                    middle = {s: self.transform(right, a-i, b-j,
                              {u: values[u | s] for u in subsets(right, a-i)})
                              for s in subsets(left, i)}
                    for t in subsets(right, b-j):
                        row = self.transform(left, i, j,
                                             {s: v[t] for s, v in middle.items()})
                        for u, node in row.items():
                            terms[t | u].append(node)
        return {t: self.total(nodes) for t, nodes in terms.items()}


def array_digest(*arrays):
    out = sha256()
    for a in arrays:
        if a.itemsize > 1 and sys.byteorder != "little":
            a = array(a.typecode, a)
            a.byteswap()
        out.update(a.tobytes())
    return out.hexdigest()


def build(h, exact_support=False):
    require(type(h) is int and 8 <= h <= 24, "Probe budget is 8 <= h <= 24")
    require(not exact_support or h <= 9, "Dense coefficient certificate budget exceeded")
    template = TripleTemplate(h)
    triples = template.inputs
    pairs = list(subsets(tuple(range(h)), 2))
    labels = list(subsets(tuple(range(h)), 5))
    V, c = len(labels), len(pairs)
    source_id = {t: i+1 for i, t in enumerate(labels)}
    pair_id = {t: i for i, t in enumerate(pairs)}
    left = array("I", [0])*(V+1)
    right = array("I", [0])*(V+1)
    common = array("I", [0]+labels)
    union = array("I", [0]+labels)
    roots, targets = array("I"), array("I")
    centers = array("I")
    exact = [0]+[1 << i for i in range(V)] if exact_support else None
    table = {}
    nodes = sorted(template.active)

    def allocate(a, b):
        require(0 < a < len(left) and 0 < b < len(left) and a != b, "Invalid DAG input")
        node = len(left)
        require(node < 2**32, "DAG index overflow")
        left.append(a)
        right.append(b)
        common.append(common[a] & common[b])
        union.append(union[a] | union[b])
        require(common[node].bit_count() >= 2, "Source enclosure lost the common pair")
        if exact is not None:
            require(not exact[a] & exact[b], "Overlapping exact source supports")
            exact.append(exact[a] | exact[b])
        return node

    for pair in pairs:
        good = sum(1 << i for i, t in enumerate(triples) if not t & pair)
        image = array("I", [0])*len(template.args)
        inter = array("I", [0])*len(template.args)
        uni = array("I", [0])*len(template.args)
        within = {}
        for i, t in enumerate(triples):
            if not t & pair:
                image[i+1] = source_id[pair | t]
                inter[i+1] = uni[i+1] = t
        for x in nodes:
            if not template.args[x]:
                continue
            u, v = template.args[x]
            a, b = image[u], image[v]
            if not a or not b:
                image[x] = a or b
                inter[x] = inter[u] if a else inter[v]
                uni[x] = uni[u] if a else uni[v]
                continue
            I, U = inter[u] & inter[v], uni[u] | uni[v]
            inter[x], uni[x] = I, U
            support = template.support[x] & good
            require(I.bit_count() <= 2, "Two distinct triples have three common points")
            if not I:
                y = within.get(support)
                if y is None:
                    y = allocate(a, b)
                    within[support] = y
            else:
                if I.bit_count() == 1:
                    residual = 0
                    bits = support
                    while bits:
                        bit = bits & -bits
                        bits ^= bit
                        residual |= 1 << pair_id[triples[bit.bit_length()-1] ^ I]
                else:
                    residual = U ^ I
                key = ((pair | I) << c) | residual
                y = table.get(key)
                if y is None:
                    y = allocate(a, b)
                    table[key] = y
            require(common[y] == common[a] & common[b] and
                    union[y] == union[a] | union[b], "Interned enclosure mismatch")
            if exact is not None:
                require(exact[y] == exact[a] | exact[b] and not exact[a] & exact[b],
                        "Interned unequal formal source sums")
            image[x] = y
        for t, x in template.outputs.items():
            if t & pair:
                continue
            y = image[x]
            target = t | pair
            require(y != 0, "Empty side output")
            roots.append(y)
            targets.append(source_id[target]-1)
            if exact is not None:
                expected = sum(1 << i for i, s in enumerate(labels) if s & target == pair)
                require(exact[y] == expected, "Wrong complete side coefficient row")
        center = image[template.total_root]
        centers.append(center)
        require(common[center] == pair and union[center] == (1 << h)-1,
                "Pair total is not at its h-2 enclosure")
        if exact is not None:
            expected = sum(1 << i for i, s in enumerate(labels) if s & pair == pair)
            require(exact[center] == expected, "Wrong pair-total coefficient row")
    require(len(roots) == 10*V and len(centers) == c, "Missing query outputs")
    require(Counter(targets) == {i: 10 for i in range(V)}, "Wrong side target multiplicity")
    active = bytearray(len(left))
    for root in [*roots, *centers]:
        active[root] = 1
    additions = 0
    for node in range(len(left)-1, V, -1):
        if active[node]:
            additions += 1
            active[left[node]] = active[right[node]] = 1
    require(sum(active[1:V+1]) == V, "A source is missing")
    return dict(h=h, V=V, c=c, labels=labels, pairs=pairs, left=left, right=right,
                common=common, union=union, roots=roots, targets=targets, centers=centers,
                active=active, additions=additions, exact=exact,
                template_active_additions=sum(template.args[i] is not None for i in template.active),
                template_total_augmented=True)


def frame_rank(I, U):
    k = I.bit_count()
    require(I & ~U == 0 and 2 <= k <= 5, "Invalid enclosure")
    if k == 5:
        require(I == U, "A common five-subset can only be a singleton")
        return 1
    return U.bit_count()-k


def compile_native(g, retain=False):
    h, V, c = g["h"], g["V"], g["c"]
    L, R, active = g["left"], g["right"], g["active"]
    size = len(L)
    uses = array("I", [0])*size
    lo = array("I", [0])*size
    ro = array("I", [0])*size
    for node in range(V+1, size):
        if active[node]:
            lo[node] = uses[L[node]]
            uses[L[node]] += 1
            ro[node] = uses[R[node]]
            uses[R[node]] += 1
    query_roots = [*g["roots"], *g["centers"]]
    ordinals = array("I")
    for node in query_roots:
        ordinals.append(uses[node])
        uses[node] += 1
    pivot = array("I", [0])*size
    first = array("I", [0])*size
    frames = []
    hist = Counter()
    moves = 0
    scalar_L = [] if retain else None
    scalar_L_count = 0
    source_slots = []
    transition_hash = sha256()
    unique_enclosures = set()

    def slot(node, ordinal):
        return pivot[node] if ordinal == 0 else first[node]+ordinal-1

    def move(s, node):
        nonlocal moves
        old = frames[s]
        if old == node:
            return
        I, U = g["common"][node], g["union"][node]
        new_rank = frame_rank(I, U)
        if old:
            old_I, old_U = g["common"][old], g["union"][old]
            require(I & ~old_I == 0 and old_U & ~U == 0,
                    "Physical forward edge does not have nested enclosures")
            old_rank = frame_rank(old_I, old_U)
        else:
            old_rank = 0
        d = new_rank-old_rank
        require(d >= 0, "Negative monotone rank increment")
        if d:
            hist[d] += 1
            moves += 1
        frames[s] = node
        if retain:
            unique_enclosures.add((I, U))
        transition_hash.update(f"{s}:{old}>{node}:{d};".encode())

    for node in range(1, size):
        if not active[node]:
            continue
        require(uses[node] > 0, "Active node has no user")
        if node <= V:
            p = len(frames)
            frames.append(0)
            ins = [p]
            source_slots.append((node-1, p))
        else:
            ins = [slot(L[node], lo[node]), slot(R[node], ro[node])]
            p = ins[0]
        pivot[node] = p
        first[node] = len(frames)
        new_slots = range(len(frames), len(frames)+uses[node]-1)
        frames.extend([0]*(uses[node]-1))
        outs = [p, *new_slots]
        require(len(set(ins+outs)) == len(ins)+len(outs)-1, "Pivot aliasing error")
        for s in [*ins, *outs[1:]]:
            move(s, node)
        for s in ins[1:]:
            scalar_L_count += 1
            if retain:
                scalar_L.append((p, s, 1))
        for s in outs[1:]:
            scalar_L_count += 1
            if retain:
                scalar_L.append((s, p, 1))
    A = len(frames)
    require(A == g["additions"]+10*V+c, "Wrong reversible role count")
    output_slots = [slot(node, ordinal) for node, ordinal in zip(query_roots, ordinals)]
    require(len(set(output_slots)) == len(output_slots), "Query outputs share a physical slot")
    center_slots = output_slots[10*V:]
    side_slots = output_slots[:10*V]
    # Query reads happen after the producer and before any inverse update.
    # Center original streams stay put; each private copy is discarded after its read.
    for s, center in zip(center_slots, g["centers"]):
        require(frames[s] == center, "Center original was consumed before its read")
        r = frame_rank(g["common"][center], g["union"][center])
        require(r == h-2, "Center rank is not h-2")
        hist[r] += 1
        moves += 1
    # Side output uses meet the actual target at its fixed hyperplane.
    side_checks = 0
    for s, target in zip(side_slots, g["targets"]):
        node = frames[s]
        I, U = g["common"][node], g["union"][node]
        T = g["labels"][target]
        if I.bit_count() == 5:
            require((I & T).bit_count() == 2, "Singleton side is not orthogonal")
        else:
            # All coordinates on I equal a; total is 5a. Only a pair of I
            # occurs in the target; its other coordinates are outside U.
            require((I & T).bit_count() == 2 and (T & U) == (T & I),
                    "Output enclosure is not below the target hyperplane")
        d = h-1-frame_rank(I, U)
        require(d >= 0, "Side output rank exceeds its hyperplane")
        if d:
            hist[d] += 1
            moves += 1
        frames[s] = -1  # distinct actual target hyperplane, rank h-1
        side_checks += 1
    for node in frames:
        r = h-1 if node == -1 else frame_rank(g["common"][node], g["union"][node])
        d = h-r
        require(d >= 0, "Helper endpoint rank exceeds I")
        if d:
            hist[d] += 1
            moves += 1
    # Data source Pi -> I; data target 0 -> I-Pi.
    hist[h-1] += 2*V
    moves += 2*V
    mass = sum(r*n for r, n in hist.items())
    minimum = (2*V+A)*h-2*V
    require(mass == minimum+c*(h-2), "Joint native rank telescoping failed")
    global_hist = Counter({r: 3*n for r, n in hist.items()})
    global_hist[2] += 2*V
    W, m = 2*V+A, 3*h
    global_mass = sum(r*n for r, n in global_hist.items())
    delta = W*m-global_mass
    require(delta == 2*V-3*c*(h-2), "Padded cover saving failed")
    out = dict(persistent_auxiliaries=A, data_roles=2*V, W=W, m=m,
               local_profile=dict(sorted(hist.items())), local_rank_mass=mass,
               monotone_endpoint_minimum=minimum, local_excess=c*(h-2),
               physical_rank_moves=moves, forward_mixer_primitives=scalar_L_count,
               complete_scalar_primitives=4*scalar_L_count+42*V,
               side_output_inclusions_checked=side_checks,
               central_private_copies=c, central_copy_rank=h-2,
               global_profile=dict(sorted(global_hist.items())),
               global_rank_mass=global_mass, global_output_mass=W*m,
               global_rank_saving=delta,
               physical_transition_sha256=transition_hash.hexdigest())
    if retain:
        out["_program"] = dict(L=scalar_L, sources=source_slots, side=side_slots,
                               centers=center_slots, enclosures=sorted(unique_enclosures))
    return out


def f3add(a, b, coefficient=1):
    u, v = a
    x, y = b
    coefficient %= 3
    if coefficient == 0:
        return a
    if coefficient == 2:
        x, y = y, x
    return ((u & ~(x | y)) | (x & ~(u | v)) | (v & y),
            (v & ~(x | y)) | (y & ~(u | v)) | (u & x))


def scalar_certificate(g, ledger, sign=1, omit=None):
    p = ledger["_program"]
    V, A, W = g["V"], ledger["persistent_auxiliaries"], ledger["W"]
    values = [(1 << i, 0) for i in range(W)]
    operations = 0

    def add(dst, src, coefficient):
        nonlocal operations
        values[dst] = f3add(values[dst], values[src], coefficient)
        operations += 1

    def mixer(inverse=False):
        ops = reversed(p["L"]) if inverse else p["L"]
        for dst, src, coefficient in ops:
            add(2*V+dst, 2*V+src, -coefficient if inverse else coefficient)

    def observation(k, which):
        if omit != which+"_center":
            for pair, slot in zip(g["pairs"], p["centers"]):
                for i, label in enumerate(g["labels"]):
                    if label & pair == pair:
                        add(V+i, 2*V+slot, k)
        if omit != which+"_side":
            for i, slot in zip(g["targets"], p["side"]):
                add(V+i, 2*V+slot, -k)

    mixer()
    observation(-sign, "old")
    mixer(True)
    for i, s in p["sources"]:
        add(2*V+s, i, 1)
    mixer()
    observation(sign, "new")
    mixer(True)
    for i, s in reversed(p["sources"]):
        add(2*V+s, i, -1)
    expected = [(1 << i, 0) for i in range(W)]
    for i in range(V):
        expected[V+i] = f3add(expected[V+i], expected[i], sign)
    changed_rows = sum(a != b for a, b in zip(values, expected))
    changed_coefficients = 0
    for a, b in zip(values, expected):
        d = f3add(a, b, -1)
        changed_coefficients += (d[0] | d[1]).bit_count()
    helper_rows = sum(values[i] != expected[i] for i in range(2*V, W))
    if omit is None:
        require(changed_rows == 0, "Complete scalar operator failed")
        require(operations == ledger["complete_scalar_primitives"], "Scalar count mismatch")
    else:
        require(changed_coefficients > 0, "Negative control was not detected")
    return dict(sign=sign, independent_roles=W, all_operator_coefficients=W*W,
                scalar_primitives=operations, changed_rows=changed_rows,
                changed_coefficients=changed_coefficients, changed_helper_rows=helper_rows,
                arbitrary_dirty_helper_columns=True, omitted_phase=omit)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(A, B):
    return [[sum(a*b for a, b in zip(row, col)) for col in zip(*B)] for row in A]


def transpose(A):
    return [list(x) for x in zip(*A)]


def enclosure_projector(h, I, U):
    H = [[Q(i == j)-Q(2, 25) for j in range(h)] for i in range(h)]
    k = I.bit_count()
    if k == 5:
        basis = [[Q(bool(I >> i & 1))] for i in range(h)]
        inverse_gram = [[Q(1, 3)]]
    else:
        outside = [i for i in range(h) if U >> i & 1 and not I >> i & 1]
        basis = [[Q(i == j)+Q(bool(I >> i & 1), 5-k) for j in outside]
                 for i in range(h)]
        alpha = Q(k-2, (5-k)**2)
        n = len(outside)
        inverse_gram = [[Q(i == j)-alpha/(1+n*alpha) for j in range(n)] for i in range(n)]
    gram = mm(mm(transpose(basis), H), basis)
    require(mm(gram, inverse_gram) == eye(len(gram)), "Closed-form Gram inverse failed")
    E = mm(mm(mm(basis, inverse_gram), transpose(basis)), H)
    require(mm(E, E) == E and mm(transpose(E), H) == mm(H, E), "Invalid rational projector")
    require(sum(E[i][i] for i in range(h)) == frame_rank(I, U), "Projector rank mismatch")
    return E


def exact_enclosure_certificate(g, ledger):
    h = g["h"]
    enclosures = ledger["_program"]["enclosures"]
    digest = sha256()
    for I, U in enclosures:
        E = enclosure_projector(h, I, U)
        digest.update(json.dumps([[str(x) for x in row] for row in E],
                                 separators=(",", ":")).encode())
    return dict(h=h, distinct_enclosures=len(enclosures),
                exact_rational_projector_entries=len(enclosures)*h*h,
                idempotence_checked=True, H_self_adjointness_checked=True,
                closed_form_Gram_inverse_checked=True,
                projector_sha256=digest.hexdigest(),
                all_large_frame_inclusions="Checked as exact mask constraints; proved by the enclosure equations")


@cache
def log_interval(n, d=1, terms=50):
    """Rational bounds from atanh, reducing the argument to [1,2)."""
    x = Q(n, d)
    require(x >= 1, "Log interval currently expects x >= 1")
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def unit(y):
        z = (y-1)/(y+1)
        z2 = z*z
        term = z
        lower = Q(0)
        for j in range(terms):
            lower += 2*term/(2*j+1)
            term *= z2
        upper = lower+2*term/((2*terms+1)*(1-z2))
        return lower, upper

    a, b = unit(x)
    c, d2 = unit(Q(2))
    return dyadic_enclose(a+k*c, b+k*d2)


def dyadic_enclose(lo, hi, bits=128):
    scale = 1 << bits
    lower = (lo.numerator*scale)//lo.denominator
    upper = -((-hi.numerator*scale)//hi.denominator)
    return Q(lower, scale), Q(upper, scale)


def exp_interval(lo, hi, terms=20):
    require(0 <= lo <= hi < 1, "Exp argument outside the fixed probe interval")
    def partial(t):
        s = Q(1)
        term = Q(1)
        for k in range(1, terms+1):
            term *= t/k
            s += term
        return s, term*t/(terms+1)
    lower = partial(lo)[0]
    s, next_term = partial(hi)
    upper = s+next_term/(1-hi/(terms+2))
    return dyadic_enclose(lower, upper)


def moment_interval(ledger, a):
    require(0 <= a <= Q(1, 100), "Only small primitive exponents are screened")
    lo = hi = Q(0)
    W, m = ledger["W"], ledger["m"]
    for r, count in ledger["global_profile"].items():
        lower, upper = log_interval(m, r)
        lower, upper = exp_interval(a*lower, a*upper)
        weight = Q(count*r, W*m)
        lo += weight*lower
        hi += weight*upper
    return lo, hi


def quotient(x):
    return f"{x.numerator}/{x.denominator}"


def moment_gate(ledger):
    # Floating arithmetic locates a candidate only. Every pass/fail below is
    # proved independently by rational interval arithmetic.
    W, m = ledger["W"], ledger["m"]
    prof = ledger["global_profile"]
    f = lambda a: sum(count*r*exp(a*log(m/r)) for r, count in prof.items())/(W*m)
    if f(0) >= 1:
        candidate = Q(0)
    else:
        lo, hi = 0.0, 0.01
        for _ in range(64):
            mid = (lo+hi)/2
            if f(mid) < 1:
                lo = mid
            else:
                hi = mid
        candidate = Q(int(lo*10**9), 10**9)
    targets = sorted({candidate, candidate+Q(1, 10**9), Q(1, 1000), Q(1, 250)})
    gates = []
    for a in targets:
        lo, hi = moment_interval(ledger, a)
        gates.append(dict(a=quotient(a), moment_lower=float(lo), moment_upper=float(hi),
                          lower_exact=quotient(lo), upper_exact=quotient(hi),
                          strict_pass=hi < 1, strict_fail=lo > 1,
                          enclosure_method="Exact rational atanh/log and Taylor/exp tails"))
    if candidate > 0:
        require(gates[targets.index(candidate)]["strict_pass"], "Rounded candidate not certified")
        require(gates[targets.index(candidate+Q(1, 10**9))]["strict_fail"], "Endpoint bracket not certified")
    return dict(certified_primitive_a=quotient(candidate) if candidate > 0 else None,
                candidate_location_only="Float bisection; never used as certificate",
                targets=gates, multiplication_kappa_claim=False)


def summarize(g, ledger):
    return dict(h=g["h"], V=g["V"], c=g["c"],
                active_additions=g["additions"], allocated_additions=len(g["left"])-g["V"]-1,
                side_query_uses=len(g["roots"]), center_query_uses=len(g["centers"]),
                tensor_total_augmented=g["template_total_augmented"],
                template_active_additions=g["template_active_additions"],
                DAG_sha256=array_digest(g["left"], g["right"], g["common"], g["union"]),
                query_sha256=array_digest(g["roots"], g["targets"], g["centers"]),
                active_sha256=sha256(g["active"]).hexdigest(),
                exact_formal_supports_expanded=g["exact"] is not None,
                native={k: v for k, v in ledger.items() if not k.startswith("_")},
                primitive_moment=moment_gate(ledger))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h", type=int, nargs="+", default=[8, 14, 19])
    ap.add_argument("--receipt", type=Path, default=Path(__file__).with_name("JOINT-PAIR-DAG.json"))
    ap.add_argument("--skip-projector-matrices", action="store_true")
    args = ap.parse_args()
    result = dict(schema="joint-pair-total-monotone-native-DAG/1",
                  status="PASS_PAID_NATIVE_REFERENCE", new_admitted_kappa=False,
                  scalar_field="F3; rational geometry is separate",
                  geometry="H=I-(2/25)J, five-subset lines of norm 3",
                  word=["L@0", "-J@0", "L^-1@0", "V@P_i", "L@nested E(I,U)",
                        "J_center via immutable copies E_pair->0", "J_side@(I-P_i)",
                        "L^-1@I", "-V@I"],
                  upstream_algorithm_pin="12fa8c5c844be21bfefb38a19503fbd867a11244",
                  scalar_count_scope=("Counts pointwise scalar ADDs in the algebraic word. Complete stream "
                                      "copying, retirement, routing and tape work are additional linear work; "
                                      "recursive copy transforms are included in the rank profile."),
                  runtime_scope=("Native local/cover phase construction and exact moment gate under the "
                                 "retained complete-stream contract; no new outer arbitrary-precision "
                                 "engine or multiplication-runtime certificate is supplied."),
                  cases=[], scalar_checks=[], negative_controls=[], rational_projectors=[])
    for h in args.h:
        exact = h == 8
        g = build(h, exact_support=exact)
        ledger = compile_native(g, retain=exact)
        if exact:
            for sign in (1, -1):
                result["scalar_checks"].append(scalar_certificate(g, ledger, sign))
            for omit in ("old_center", "new_center", "old_side", "new_side"):
                result["negative_controls"].append(scalar_certificate(g, ledger, omit=omit))
            if not args.skip_projector_matrices:
                result["rational_projectors"].append(exact_enclosure_certificate(g, ledger))
        case = summarize(g, ledger)
        result["cases"].append(case)
        print(json.dumps({"h": h, "V": g["V"], "A": ledger["persistent_auxiliaries"],
                          "delta": ledger["global_rank_saving"],
                          "certified_a": case["primitive_moment"]["certified_primitive_a"]}), flush=True)
    result["program_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    result["scope"] = ("The paid local F3 word has standard data/helper endpoints. The global profile uses the "
                       "previously proved shared padded 3h cover. This is a large-state reference, not a new "
                       "selected primitive or multiplication record; no complex supplier claim is made.")
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"receipt": str(args.receipt), "status": result["status"]}))


if __name__ == "__main__":
    main()
