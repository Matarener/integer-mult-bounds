#!/usr/bin/env python3
"""Invoice one moved-ADD pair with two illegal direct intermediates.

The frame predicate is the containment rule used by the staged544 retiming
trace: a gate frame must contain each operand's current frame, and the rank
gap is the charged child. Terminal frames are fixed. This file does not import
the unmerged predecessor.
"""
from collections import Counter
from fractions import Fraction

X, Y, Z = 0, 1, 2
REGISTERS = (X, Y, Z)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def span(vectors):
    points = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, "bad frame vector")
        points |= {point ^ vector for point in tuple(points)}
    return sum(1 << point for point in points)


def rank(mask):
    size = mask.bit_count()
    require(size and size & (size - 1) == 0, "not a subspace")
    return size.bit_length() - 1


def contained(inner, outer):
    return not inner & ~outer


def crosses(left, right):
    """Predecessor sufficient reorder test: targets are not each other's sources."""
    require(left[0] == "add" and right[0] == "add", "reorder test is for ADDs")
    return left[1] != right[2] and right[1] != left[2]


def histogram(gates, ends):
    current = {register: span(()) for register in REGISTERS}
    paid = Counter()

    def visit(register, frame):
        require(contained(current[register], frame), "frame containment")
        gap = rank(frame) - rank(current[register])
        if gap:
            paid[gap] += 1
        current[register] = frame

    for gate in gates:
        require(gate[0] == "add" and gate[1] != gate[2], "binary ADD")
        for register in gate[1:3]:
            visit(register, gate[5])
    for register in REGISTERS:
        visit(register, ends[register])
    return tuple(paid[rank_index] for rank_index in range(10))


def legal(gates, ends):
    try:
        histogram(gates, ends)
    except ValueError:
        return False
    return True


def execute(gates, state):
    values = [row[:] for row in state]
    for gate in gates:
        target, source = gate[1], gate[2]
        coefficient = Fraction(gate[3], gate[4])
        values[target] = [
            left + coefficient * right
            for left, right in zip(values[target], values[source])
        ]
    return values


def identity():
    return [[Fraction(i == j) for j in range(3)] for i in range(3)]


def add(target, source, numerator, frame):
    return ("add", target, source, numerator, 1, frame)


def cleanup(frame):
    return [add(Y, Z, -1, frame), add(Y, X, -1, frame)]


def moment_sign_known(delta):
    """Exact sign of sum delta_r r^a is not needed when the histogram is zero."""
    return sum(delta) == 0 and all(entry == 0 for entry in delta)


def main():
    zero, line_a, line_b = span(()), span((1,)), span((2,))
    plane = span((1, 2))
    require(rank(line_a) == rank(line_b) == 1 and rank(plane) == 2, "line dimensions")
    require(not contained(line_a, line_b) and not contained(line_b, line_a), "crossed lines")
    ends = {X: plane, Y: plane, Z: plane}
    forward_a = add(Y, X, 1, line_a)
    forward_b = add(Y, Z, 1, line_a)
    moved_b = add(Y, Z, 1, line_b)
    moved_a = add(Y, X, 1, line_b)
    require(crosses(forward_a, forward_b) and crosses(forward_b, forward_a),
            "commuting ADDs are outside the reorder test")

    original = [forward_a, forward_b, *cleanup(plane)]
    moved = [moved_b, moved_a, *cleanup(plane)]
    only_a = [forward_b, moved_a, *cleanup(plane)]
    only_b = [moved_b, forward_a, *cleanup(plane)]
    original_bill = histogram(original, ends)
    moved_bill = histogram(moved, ends)
    require(original_bill == moved_bill == (0, 6, 0, 0, 0, 0, 0, 0, 0, 0),
            "crossed witness histogram")
    delta = tuple(new - old for old, new in zip(original_bill, moved_bill))
    require(moment_sign_known(delta), "nonzero invoice")
    require(sum(rank_index * count for rank_index, count in enumerate(delta)) == 0, "mass")
    require(not legal(only_a, ends) and not legal(only_b, ends), "an intermediate is legal")
    start = identity()
    restored = execute(original, start)
    require(restored == execute(moved, start) == start, "cleanup does not restore")
    require(execute(original[:2], start) == execute(moved[:2], start), "forward maps differ")

    same_line = [add(Y, Z, 1, line_a), add(Y, X, 1, line_a), *cleanup(plane)]
    require(legal(same_line, ends), "parallel swap must stay legal")
    widened = add(Y, X, 1, plane)
    widened_b = add(Y, Z, 1, plane)
    favorable = [widened_b, widened, *cleanup(plane)]
    favorable_only_a = [forward_b, widened, *cleanup(plane)]
    favorable_only_b = [widened_b, forward_a, *cleanup(plane)]
    favorable_bill = histogram(favorable, ends)
    require(favorable_bill == (0, 0, 3, 0, 0, 0, 0, 0, 0, 0), "favorable histogram")
    favorable_delta = tuple(new - old for old, new in zip(original_bill, favorable_bill))
    require(favorable_delta == (0, -6, 3, 0, 0, 0, 0, 0, 0, 0), "favorable delta")
    require(legal(favorable_only_a, ends) and not legal(favorable_only_b, ends),
            "favorable escape is not sequential on one side")
    # 3*(2^a-2) < 0 for every real a in (0,1), checked on reduced fractions.
    for denominator in range(2, 9):
        for numerator in range(1, denominator):
            require(pow(2, numerator) < pow(2, denominator), "power comparison")

    noncommuting = [add(Y, X, 1, line_a), add(Z, Y, 1, line_a)]
    swapped_noncommuting = [add(Z, Y, 1, line_a), add(Y, X, 1, line_a)]
    require(execute(noncommuting, start) != execute(swapped_noncommuting, start),
            "noncommuting swap was treated as an identity")
    scaled = [add(Y, X, 2, line_a), forward_b]
    require(execute(scaled, start) != execute(original[:2], start), "coefficient control")
    require(not crosses(add(Y, X, 1, line_a), add(Z, Y, 1, line_a)),
            "dependent ADD passed the reorder test")

    print(
        "PASS_MOVED_ADD_CROSSED_INVOICE"
        " registers=3 adds=2 cleanup=2"
        " histogram_H1=6 delta=0 rank_mass_delta=0"
        " both_intermediates=illegal scalar=commuting_identity"
        " favorable_sequential=-6H1+3H2 one_intermediate=legal"
        " no_new_kappa"
    )


if __name__ == "__main__":
    main()
