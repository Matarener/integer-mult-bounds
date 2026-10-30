#!/usr/bin/env python3
"""Independent full-query Dijkstra and bit-value checks, Apache-2.0.

No primary or predecessor code is imported. Same assisted author, not an
independent human review or formal proof. Finite quotient, with no depth cap.
"""
import hashlib
import heapq
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def insist(condition, why):
    if not condition:
        raise RuntimeError(why)


def shortest(windows, source_prices, read_prices):
    # Each output stores the two coefficients (x,z0). Connector stores only
    # its x coefficient: its z0 coefficient is always one.
    m, k = len(source_prices), len(windows)
    start = (0, 0, (0,)*k)
    goal = (m, 0, (1,)*k)
    distance = {start: Fraction(0)}
    pending = [(Fraction(0), start)]
    settled = 0
    while pending:
        cost, state = heapq.heappop(pending)
        if cost != distance[state]:
            continue
        settled += 1
        if state == goal:
            return cost, settled
        t, z, outputs = state
        if t == m:
            continue
        edges = [((t, z ^ 1, outputs), source_prices[t])]
        for i, (left, right) in enumerate(windows):
            if left <= t <= right:
                yy = list(outputs)
                yy[i] ^= 2 | z
                edges.append(((t, z, tuple(yy)), read_prices[i]))
        if all(right != t or outputs[i] == 1
               for i, (_, right) in enumerate(windows)):
            edges.append(((t+1, z, outputs), 0))
        for other, price in edges:
            new = cost + price
            if other not in distance or new < distance[other]:
                distance[other] = new
                heapq.heappush(pending, (new, other))
    raise RuntimeError("no legal restored word")


def all_costs():
    records, states = [], 0
    for slots in range(1, 5):
        choices = [(start, stop) for stop in range(slots) for start in range(stop+1)]
        for count in range(4):
            for intervals in itertools.combinations_with_replacement(choices, count):
                for weights in itertools.product((1, 3), repeat=slots):
                    readers = tuple(1 + i % 2 for i in range(count))
                    price, visited = shortest(intervals, weights, readers)
                    records.append([intervals, weights, readers, str(price)])
                    states += visited
    encoded = json.dumps(records, separators=(",", ":"), sort_keys=True).encode()
    return len(records), states, hashlib.sha256(encoded).hexdigest()


def image(matrix, value):
    # Direct bit-value action, rather than formal row propagation.
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(matrix))


def exhaustive_small():
    # All 1024 dirty inputs for a 3-output/two-bit example. The source matrix
    # and reader 1 do not commute. One shared pair of B calls covers all three
    # windows, whereas three closed echoes need six B calls.
    b = (3, 2)
    aa = ((1, 2), (2, 1), (1, 3))
    windows = ((0,1),(1,2),(2,3))
    # Read y0,y1 around the first B at slot1; y2 around the second at slot2.
    words = [(1,"A",0),(1,"A",1),(1,"B",-1),(1,"A",0),(1,"A",1),
             (2,"A",2),(2,"B",-1),(2,"A",2)]
    for bits in range(1 << 10):
        x, z0 = bits & 3, (bits >> 2) & 3
        initial = [(bits >> (4+2*i)) & 3 for i in range(3)]
        z, ys = z0, initial[:]
        expected = [initial[i] ^ image(a, image(b,x)) for i,a in enumerate(aa)]
        for slot in range(4):
            for t, kind, i in words:
                if t != slot:
                    continue
                if kind == "B":
                    z ^= image(b,x)
                else:
                    insist(windows[i][0] <= t <= windows[i][1], "window")
                    ys[i] ^= image(aa[i], z)
            for i, (_, right) in enumerate(windows):
                if right == slot:
                    insist(ys[i] == expected[i], "bit-value deadline mismatch")
        insist(z == z0 and ys == expected, "bit-value final mismatch")
    return 1024


def main():
    expected = json.loads((HERE / "RESULT.json").read_text())
    count, settled, signature = all_costs()
    insist(count == expected["domain_cases"], "case inventory mismatch")
    insist(signature == expected["cost_digest"], "full query oracle cost mismatch")
    # Explicit rational-price and odd-parity controls do not use primary code.
    insist(shortest(((0,0),), (Fraction(3,2),), (Fraction(2,3),))[0] == Fraction(13,3),
            "fraction tariff")
    insist(shortest(((0,1),(1,2)), (1,9,1), (1,1))[0] == 6, "weighted tariff")
    inputs = exhaustive_small()
    print("PASS_INDEPENDENT_WINDOW_QUERIES cases=%d settled=%d dirty_inputs=%d cost_digest=%s" %
          (count, settled, inputs, signature))


if __name__ == "__main__":
    main()
