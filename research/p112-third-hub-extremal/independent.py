#!/usr/bin/env python3
"""Same census as verify.py, with integer elimination instead of Fraction.

This file does not import verify.py.
"""
import math

PASS = "PASS_THIRD_HUB_EXTREMAL_INDEPENDENT"


def bits(mask):
    out = []
    while mask:
        bit = mask & -mask
        out.append(bit.bit_length() - 1)
        mask ^= bit
    return out


def star(h):
    dim = 3 + h
    def unit(i):
        row = [0] * dim
        row[i] = 1
        return tuple(row)
    E, F, G = unit(0), unit(1), unit(2)
    names = ["g", "d", "t"]
    vecs = [
        G,
        tuple(E[i] + F[i] for i in range(dim)),
        tuple(E[i] + F[i] + G[i] for i in range(dim)),
    ]
    for j in range(h):
        V = unit(3 + j)
        names.extend([f"v{j}", f"x{j}", f"y{j}"])
        vecs.append(V)
        vecs.append(tuple(E[i] + G[i] - V[i] for i in range(dim)))
        vecs.append(tuple(F[i] + G[i] - V[i] for i in range(dim)))
    return names, vecs, E, F, dim


def rank(rows, dim):
    """Exact rank by integer cross-multiplication. No Fraction operations."""
    matrix = [list(map(int, row)) for row in rows if any(row)]
    height = len(matrix)
    used = 0
    column = 0
    while used < height and column < dim:
        pivot = next((i for i in range(used, height) if matrix[i][column] != 0), None)
        if pivot is None:
            column += 1
            continue
        matrix[used], matrix[pivot] = matrix[pivot], matrix[used]
        pivot_value = matrix[used][column]
        for i in range(height):
            if i == used or matrix[i][column] == 0:
                continue
            factor = matrix[i][column]
            for j in range(dim):
                matrix[i][j] = matrix[i][j] * pivot_value - factor * matrix[used][j]
            common = 0
            for value in matrix[i]:
                common = math.gcd(common, abs(value))
            if common > 1:
                for j in range(dim):
                    matrix[i][j] //= common
        used += 1
        column += 1
    return used


def contains(vecs, mask, target, dim, cache):
    key = (mask, target)
    if key not in cache:
        rows = [vecs[i] for i in bits(mask)]
        cache[key] = rank(rows + [target], dim) == rank(rows, dim)
    return cache[key]


def hub_index(h, j):
    base = 3 + 3 * j
    return base, base + 1, base + 2


def predicted(h):
    """Return (E readers, F readers, E sources, F sources) as sorted masks."""
    def mask(indices):
        value = 0
        for i in indices:
            value |= 1 << i
        return value

    def bundle(anchor, choices):
        indices = [anchor]
        for j, choice in enumerate(choices):
            v, x, y = hub_index(h, j)
            if anchor == 0 and choice == 0:
                indices.append(x)
            elif anchor == 0 and choice == 1:
                indices.extend([v, y])
            elif anchor == 2 and choice == 0:
                indices.extend([v, x])
            else:
                indices.append(y)
        return mask(indices)

    e_readers = []
    for j in range(h):
        v, x, y = hub_index(h, j)
        e_readers.extend([
            mask([0, v, x]),
            mask([1, 2, v, x]),
            mask([0, 1, v, y]),
            mask([2, v, y]),
            mask([1, x, y]),
            mask([0, 2, x, y]),
        ])
    for i in range(h):
        vi, xi, yi = hub_index(h, i)
        for j in range(i + 1, h):
            vj, xj, yj = hub_index(h, j)
            e_readers.extend([
                mask([1, vi, yi, vj, xj]),
                mask([2, xi, yi, vj, xj]),
                mask([1, vi, xi, vj, yj]),
                mask([0, xi, yi, vj, yj]),
                mask([2, vi, xi, xj, yj]),
                mask([0, vi, yi, xj, yj]),
            ])
    # F readers are the E readers with each hub's x and y exchanged.
    swap = {}
    for j in range(h):
        v, x, y = hub_index(h, j)
        swap[x] = y
        swap[y] = x
    f_readers = []
    for value in e_readers:
        flipped = 0
        for i in bits(value):
            flipped |= 1 << swap.get(i, i)
        f_readers.append(flipped)
    e_sources = []
    f_sources = []
    for code in range(1 << h):
        choices = [(code >> j) & 1 for j in range(h)]
        e_sources.append(bundle(0, choices))
        e_sources.append(bundle(2, choices))
    for value in e_sources:
        # Exchange g=0 with t=2.
        flipped = 0
        for i in bits(value):
            flipped |= 1 << (2 if i == 0 else 0 if i == 2 else i)
        f_sources.append(flipped)
    return tuple(sorted(set(group)) for group in (e_readers, f_readers, e_sources, f_sources))


def census(h):
    names, vecs, E, F, dim = star(h)
    n = len(names)
    cache = {}
    readers = [[], []]
    sources = [[], []]
    marks = (E, F)
    for mask in range(1 << n):
        for m, mark in enumerate(marks):
            other = marks[1 - m]
            if contains(vecs, mask, mark, dim, cache):
                minimal = mask != 0 and all(
                    not contains(vecs, mask ^ (1 << i), mark, dim, cache) for i in bits(mask)
                )
                if minimal:
                    readers[m].append(mask)
            generators = [other] + [vecs[i] for i in bits(mask)]
            outside = rank(generators + [mark], dim) != rank(generators, dim)
            if outside:
                maximal = all(
                    not (
                        rank([other] + [vecs[i] for i in bits(mask | (1 << j))] + [mark], dim)
                        != rank([other] + [vecs[i] for i in bits(mask | (1 << j))], dim)
                    )
                    for j in range(n) if (mask >> j) & 1 == 0
                )
                if maximal:
                    sources[m].append(mask)
    return names, vecs, E, F, dim, [sorted(group) for group in readers], [sorted(group) for group in sources]


def spans(vecs, indices, target, dim):
    return rank([vecs[i] for i in indices] + [target], dim) == rank([vecs[i] for i in indices], dim)


def separated(vecs, killed, mark, other, dim):
    rows = [other] + [vecs[i] for i in killed]
    return rank(rows + [mark], dim) != rank(rows, dim)


def reader_cost(vecs, mask, mark, other, dim):
    indices = bits(mask)
    best = None
    width = len(indices)
    for support_code in range(1 << width):
        support = [indices[i] for i in range(width) if (support_code >> i) & 1]
        if not spans(vecs, support, mark, dim):
            continue
        for paid_code in range(1 << len(support)):
            paid = [support[i] for i in range(len(support)) if (paid_code >> i) & 1]
            if len(paid) > 2 and best is not None and best <= 2:
                continue
            killed = [i for i in support if i not in paid]
            if separated(vecs, killed, mark, other, dim):
                best = len(paid) if best is None else min(best, len(paid))
                if best == 1:
                    return 1
    if best is None:
        raise AssertionError("reader premise does not span its mark")
    return best


def source_cost(vecs, mask, reader_masks, mark, other, dim):
    premise = bits(mask)
    best = None
    for reader in reader_masks:
        allowed = bits(reader)
        width = len(allowed)
        for support_code in range(1 << width):
            support = [allowed[i] for i in range(width) if (support_code >> i) & 1]
            if not spans(vecs, support, mark, dim):
                continue
            for paid_code in range(1 << len(support)):
                paid = [support[i] for i in range(len(support)) if (paid_code >> i) & 1]
                if len(paid) > 1 and best == 1:
                    continue
                killed = premise + [i for i in support if i not in paid]
                if separated(vecs, killed, mark, other, dim):
                    best = len(paid) if best is None else min(best, len(paid))
                    if best == 1:
                        return 1
    if best is None:
        raise AssertionError("source row has no admissible reader")
    return best


def cost_two_masks(h):
    """Masks whose both mark-rows are forced to cost 2 by the written pairing."""
    def mask(indices):
        value = 0
        for i in indices:
            value |= 1 << i
        return value
    out = []
    for j in range(h):
        v, x, y = hub_index(h, j)
        out.append(mask([1, x, y]))
        out.append(mask([0, 2, x, y]))
    for i in range(h):
        vi, xi, yi = hub_index(h, i)
        for j in range(i + 1, h):
            vj, xj, yj = hub_index(h, j)
            out.append(mask([1, vi, yi, vj, xj]))
            out.append(mask([1, vi, xi, vj, yj]))
    return sorted(set(out))


def summarize(h):
    names, vecs, E, F, dim, readers, sources = census(h)
    expect = predicted(h)
    if (readers[0], readers[1], sources[0], sources[1]) != expect:
        raise AssertionError(f"h={h} extremal table does not match the predicted list")
    marks = (E, F)
    forced = set(cost_two_masks(h))
    total = 0
    forced_rows = 0
    for m, mark in enumerate(marks):
        other = marks[1 - m]
        for mask in readers[m]:
            cost = reader_cost(vecs, mask, mark, other, dim)
            if mask in forced:
                if cost != 2:
                    raise AssertionError(f"h={h} forced reader cost {cost}")
                forced_rows += 1
            elif cost != 1:
                raise AssertionError(f"h={h} unexpected reader cost {cost}")
            total += cost
        for mask in sources[m]:
            cost = source_cost(vecs, mask, readers[m], mark, other, dim)
            if cost != 1:
                raise AssertionError(f"h={h} source cost {cost}")
            total += cost
    rows = sum(len(group) for group in readers) + sum(len(group) for group in sources)
    charge = 2 * total
    baseline = 2 * rows
    return {
        "h": h,
        "rows": rows,
        "readers_per_mark": len(readers[0]),
        "sources_per_mark": len(sources[0]),
        "sum_cost": total,
        "charge": charge,
        "baseline": baseline,
        "excess": charge - baseline,
        "forced_rows": forced_rows,
        "names": names,
    }


def k32_charge():
    """The twenty-one PR3583 premises, not the full two-hub extremal table."""
    names, vecs, E, F, dim = star(2)
    index = {name: i for i, name in enumerate(names)}
    def mask(*labels):
        value = 0
        for label in labels:
            value |= 1 << index[label]
        return value
    readers = {
        E: [
            mask("g", "v0", "x0"), mask("g", "v1", "x1"), mask("t", "v0", "y0"),
            mask("t", "v1", "y1"), mask("d", "x0", "y0"), mask("d", "x1", "y1"),
            mask("g", "t", "x0", "y0"),
        ],
        F: [
            mask("g", "v0", "y0"), mask("g", "v1", "y1"), mask("t", "v0", "x0"),
            mask("t", "v1", "x1"), mask("d", "x0", "y0"), mask("d", "x1", "y1"),
            mask("g", "t", "x0", "y0"),
        ],
    }
    sources = {
        E: [mask("g", "v0", "v1"), mask("v0", "x0"), mask("g", "x0"), mask("g", "v0", "x1")],
        F: [mask("g", "v0", "v1"), mask("g", "y0"), mask("v0", "y0")],
    }
    total = 0
    count = 0
    for mark, other in ((E, F), (F, E)):
        for value in readers[mark]:
            total += reader_cost(vecs, value, mark, other, dim)
            count += 1
        for value in sources[mark]:
            total += source_cost(vecs, value, readers[mark], mark, other, dim)
            count += 1
    if count != 21:
        raise AssertionError(count)
    return 2 * total


def main():
    summaries = [summarize(h) for h in (1, 2, 3)]
    expected = {
        1: {"rows": 20, "readers_per_mark": 6, "sources_per_mark": 4, "charge": 48, "excess": 8, "forced_rows": 4},
        2: {"rows": 52, "readers_per_mark": 18, "sources_per_mark": 8, "charge": 128, "excess": 24, "forced_rows": 12},
        3: {"rows": 104, "readers_per_mark": 36, "sources_per_mark": 16, "charge": 256, "excess": 48, "forced_rows": 24},
    }
    for summary in summaries:
        h = summary["h"]
        for key, value in expected[h].items():
            if summary[key] != value:
                raise AssertionError(f"h={h} {key}={summary[key]} expected {value}")
        formula_rows = 2 * (3 * h * (h + 1) + 2 ** (h + 1))
        formula_excess = 4 * h * (h + 1)
        if summary["rows"] != formula_rows or summary["excess"] != formula_excess:
            raise AssertionError("closed form mismatch")
    certificate = k32_charge()
    if certificate != 54:
        raise AssertionError(certificate)
    third = summaries[2]
    print(
        PASS,
        f"h3_rows={third['rows']}",
        f"h3_charge={third['charge']}",
        f"h3_excess={third['excess']}",
        f"h2_excess={summaries[1]['excess']}",
        f"h1_charge={summaries[0]['charge']}",
        f"k32_charge={certificate}",
        f"two_bearing_h3={third['forced_rows']}",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
