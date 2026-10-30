"""Exact direct-delivery gate for the supplied P104 sixteen-mode family.

This does not establish that the family is complete: the all-hyperplane
classification is a separate obligation. Producer covectors must be extracted
independently from the word. This routine verifies their support geometry, the
supplied mixed-mode identities, and all eight quotient-space delivery tests.
"""
from fractions import Fraction as Q


def need(ok, why):
    if not ok:
        raise ValueError(why)


def rref(rows, width):
    a = [[Q(x) for x in row] for row in rows]
    need(all(len(row) == width for row in a), "matrix width")
    pivots = []
    for col in range(width):
        hit = next((j for j in range(len(pivots), len(a)) if a[j][col]), None)
        if hit is None:
            continue
        k = len(pivots)
        a[k], a[hit] = a[hit], a[k]
        v = a[k][col]
        a[k] = [x / v for x in a[k]]
        for j in range(len(a)):
            if j != k and a[j][col]:
                v = a[j][col]
                a[j] = [x - v * y for x, y in zip(a[j], a[k])]
        pivots.append(col)
        if len(pivots) == len(a):
            break
    return a, pivots


def rank(rows, width):
    return len(rref(rows, width)[1])


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q(0))


def parity_dot(a, b):
    return (a & b).bit_count() % 2


def binary_basis(vectors):
    basis = {}
    for x in vectors:
        x = int(x)
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return [basis[p] for p in sorted(basis, reverse=True)]


def sparse(row):
    return {int(i): Q(v) for i, v in row.items() if Q(v)}


def mix(coefficients, producers):
    out = {}
    for a, row in zip(coefficients, producers):
        for j, v in row.items():
            out[j] = out.get(j, Q(0)) + a * v
    return {j: v for j, v in out.items() if v}


def separator(rows, target, n):
    unit = [Q(int(j == target)) for j in range(n)]
    a, pivots = rref([list(row) + [Q(0)] for row in rows] + [unit + [Q(1)]], n + 1)
    need(n not in pivots, "target is in the alternate delivery span")
    answer = [Q(0)] * n
    for row, p in zip(a, pivots):
        answer[p] = row[-1]
    need(answer[target] == Q(1), "normalized separator")
    need(all(dot(row, answer) == Q(0) for row in rows), "separator annihilates alternates")
    return answer


def verify_delivery(word, exact_modes, producers):
    """Return an exact receipt or raise ValueError; no asserts or float arithmetic.

    Scope: unchanged final payloads in span(D), direct nested 8-to-1 deliveries
    starting at each payload's original-entry support, fixed final lines, and
    arbitrary free corrections from zero-entry-frame original inputs. Earlier
    owned preparation and intermediate components outside span(D) remain open.
    """
    n = len(producers)
    need(n == 8, "eight supplied source producers")
    need(len(exact_modes) == 16, "sixteen supplied projective modes")
    frames = word["frames"]
    initial = [frames[f] for f in word["initial"]]
    ninputs = word["public"]
    need(len(initial) == ninputs, "original public input frames")
    D = [sparse(p["initial_covector"]) for p in producers]
    need(all(0 <= j < ninputs for row in D for j in row), "producer input indices")
    nonzero_inputs = [j for j, frame in enumerate(initial) if frame]
    projected = [[row.get(j, Q(0)) for j in nonzero_inputs] for row in D]
    _, pivot_columns = rref(projected, len(nonzero_inputs))
    need(len(pivot_columns) == n, "producer independence modulo zero-entry inputs")
    pivot_inputs = [nonzero_inputs[k] for k in pivot_columns]
    minor = [[row.get(j, Q(0)) for j in pivot_inputs] for row in D]
    need(rank(minor, n) == n, "explicit quotient independence minor")

    def support(row):
        basis = binary_basis(v for j in row for v in initial[j])
        need(len(basis) == 8, "every tested payload has exact eight-dimensional entry support")
        normals = [h for h in range(1, 512) if all(parity_dot(h, v) == 0 for v in basis)]
        need(len(normals) == 1, "unique ambient-nine hyperplane normal")
        return basis, normals[0]

    family = []
    lines = []
    for i, (p, row) in enumerate(zip(producers, D)):
        event = word["program"][p["copy_event"]]
        need(event == ["COPY", p["owned"], p["source_role"], "1", p["copy_frame"]], "producer COPY metadata")
        final_basis = binary_basis(frames[p["clear_frame"]])
        need(len(final_basis) == 1, "fixed one-dimensional delivery frame")
        lines.append(final_basis[0])
        basis, normal = support(row)
        coeff = [Q(int(i == j)) for j in range(n)]
        family.append({"name": f"D{i}", "coefficients": coeff, "normal": normal, "basis": basis})
    seen_original = set()
    for m in exact_modes:
        coeff = [Q(a) for a in m["coefficients"]]
        need(len(coeff) == n and any(coeff), "mixed mode coefficient vector")
        row = mix(coeff, D)
        basis, normal = support(row)
        need(normal == m["normal"], "mixed mode's recomputed entry support normal")
        if "covector" in m:
            need(row == sparse(m["covector"]), "mixed mode's exact rational covector identity")
        original = next((i for i, f in enumerate(family[:n]) if f["coefficients"] == coeff), None)
        if original is not None:
            need(original not in seen_original, "unique original mode")
            need(normal == family[original]["normal"], "original mode support identity")
            seen_original.add(original)
        else:
            family.append({"name": f"E{normal}", "coefficients": coeff, "normal": normal, "basis": basis})
    need(len(seen_original) == n and len(family) == 16, "eight original and eight mixed modes")
    need(len({m["normal"] for m in family}) == 16, "sixteen distinct support hyperplanes")
    receipt = []
    for i, line in enumerate(lines):
        own = family[i]
        need(parity_dot(own["normal"], line) == 0, "original producer admits its direct nested delivery")
        alternate = [m for m in family if m["name"] != own["name"] and parity_dot(m["normal"], line) == 0]
        need(len(alternate) == 3 and all(m["name"].startswith("E") for m in alternate), "exactly three mixed admissible alternates")
        rows = [m["coefficients"] for m in alternate]
        need(rank(rows, n) == 3, "alternate coefficient rank three")
        y = separator(rows, i, n)
        unit = [Q(int(j == i)) for j in range(n)]
        need(rank(rows + [unit], n) == 4, "target raises admissible rank")
        receipt.append({"target": i, "delivery_line": line,
                        "admissible_alternates": [m["name"] for m in alternate],
                        "rank": 3, "target_in_span": False,
                        "separator": [str(v) for v in y]})
    return {"scope": "direct nested 8-to-1 sixteen-mode delivery, modulo zero-entry input corrections",
            "quotient_rank": n, "quotient_pivot_inputs": pivot_inputs,
            "quotient_minor": [[str(v) for v in row] for row in minor],
            "source_normals": [m["normal"] for m in family[:n]],
            "mixed_normals": [m["normal"] for m in family[n:]],
            "delivery_tests": receipt}


