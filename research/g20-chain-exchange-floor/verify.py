#!/usr/bin/env python3
"""Exact ADD minimum for the PR5840 G20 chain/exchange component.

Replays the authenticated PR5840 boundary words, extracts the 18-register
component (wires 0..15, 30, 31), and proves by exhaustive budgeted search
that no scratch-free word of at most 19 unit ADDs on those 18 wires implements
it.  The source word has 20 ADDs, so 20 is exact.  The two closed 9-wire
subcomponents are each shown to need exactly 10.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTROLLER = ROOT / "research/g20-isolated-exchange-floor/inputs/CONTROLLER.json"
CONTROLLER_SHA256 = "978536e852c0cfbc150f143e19d2cfddbb434bac6017d914974eb99f641593a8"
WIRES = 32
COMPONENT = tuple(range(16)) + (30, 31)
EVEN = (0, 2, 4, 6, 8, 10, 12, 14, 31)
ODD = (1, 3, 5, 7, 9, 11, 13, 15, 30)
SEARCH_LIMIT_NODES = 50_000_000


class CheckError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise CheckError(message)


def run_program(program):
    """Rows are bitmasks of input coordinates held on each wire.

    ["ADD", d, s] means x_d <- x_d + x_s; ["SWAP", a, b] exchanges wires.
    """
    rows = [1 << i for i in range(WIRES)]
    for op, a, b in program:
        require(a != b and 0 <= a < WIRES and 0 <= b < WIRES, f"bad operands {op} {a} {b}")
        if op == "SWAP":
            rows[a], rows[b] = rows[b], rows[a]
        elif op == "ADD":
            rows[a] ^= rows[b]
        else:
            raise CheckError(f"unknown instruction {op}")
    return rows


def restrict(rows, wires):
    """Rows of the closed wire set, re-indexed to local coordinates."""
    local = {w: i for i, w in enumerate(wires)}
    out = []
    for w in wires:
        mask = 0
        for j in range(WIRES):
            if rows[w] >> j & 1:
                require(j in local, f"wire {w} reads coordinate {j} outside its component")
                mask |= 1 << local[j]
        out.append(mask)
    for w in range(WIRES):
        if w not in local:
            require(all(not (rows[w] >> j & 1) for j in wires),
                    f"outside wire {w} reads component coordinates")
    return tuple(out)


def transpose(rows):
    n = len(rows)
    return tuple(sum(((rows[i] >> j) & 1) << i for i in range(n)) for j in range(n))


class Search:
    """Is the target reachable from the identity within a given ADD budget?

    Admissible prunes: every row of the current state that differs from the
    target is the destination of at least one remaining ADD; the transpose of
    the remaining map R = target * state^-1 has a word of the same length, so
    every non-unit column of R also needs one.  R^T is tracked incrementally:
    the row step x_a += x_c on the state turns R^T row c into R^T[c] + R^T[a].
    Failed (state, budget) pairs are memoized; failure at budget b implies
    failure at every smaller budget.
    """

    def __init__(self, target):
        self.target = tuple(target)
        self.n = len(target)
        self.unit = tuple(1 << i for i in range(self.n))
        self.ops = [(a, c) for a in range(self.n) for c in range(self.n) if a != c]
        self.failed = {}
        self.nodes = 0

    def reachable(self, budget):
        self.failed.clear()
        self.nodes = 0
        word = []
        found = self._dfs(self.unit, transpose(self.target), budget, word)
        return found, list(reversed(word))

    def _dfs(self, state, rt, budget, word):
        # Children are bound-checked here before recursion; the bound of the
        # root is checked by the caller-facing wrapper below.
        self.nodes += 1
        if self.nodes > SEARCH_LIMIT_NODES:
            raise CheckError("search node limit exceeded; result would be inconclusive")
        target, unit = self.target, self.unit
        if state == target:
            return True
        if budget <= 0 or self.failed.get(state, -1) >= budget:
            return False
        rows_off = sum(1 for i in range(self.n) if state[i] != target[i])
        cols_off = sum(1 for j in range(self.n) if rt[j] != unit[j])
        if max(rows_off, cols_off) > budget:
            return False
        child = budget - 1
        for a, c in self.ops:
            new_a = state[a] ^ state[c]
            r = rows_off - (state[a] != target[a]) + (new_a != target[a])
            if r > child:
                continue
            new_c = rt[c] ^ rt[a]
            k = cols_off - (rt[c] != unit[c]) + (new_c != unit[c])
            if k > child:
                continue
            nxt = list(state)
            nxt[a] = new_a
            nrt = list(rt)
            nrt[c] = new_c
            if self._dfs(tuple(nxt), tuple(nrt), child, word):
                word.append((a, c))
                return True
        self.failed[state] = budget
        return False


def apply_local(word, n):
    rows = [1 << i for i in range(n)]
    for a, c in word:
        rows[a] ^= rows[c]
    return tuple(rows)


def exact_minimum(target, floor, label):
    """Return (minimum, witness, per-budget node counts) with exclusion below."""
    search = Search(target)
    log = []
    for budget in range(floor + 1):
        start = time.perf_counter()
        found, word = search.reachable(budget)
        log.append((budget, found, search.nodes, round(time.perf_counter() - start, 2)))
        if found:
            require(len(word) <= budget, f"{label}: witness longer than budget")
            require(apply_local(word, len(target)) == tuple(target), f"{label}: witness does not replay")
            return budget, word, log
    raise CheckError(f"{label}: no word within {floor} ADDs")


def literal_check(word, wires, target_rows):
    """Replay a local ADD word on all 2^k Boolean inputs of its wires."""
    k = len(wires)
    for x in range(1 << k):
        vals = [(x >> i) & 1 for i in range(k)]
        for a, c in word:
            vals[a] ^= vals[c]
        for i in range(k):
            expect = bin(target_rows[i] & x).count("1") & 1
            require(vals[i] == expect, "literal truth-table mismatch")


def main():
    raw = CONTROLLER.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == CONTROLLER_SHA256, "controller SHA256 mismatch")
    boundaries = json.loads(raw)["boundaries"]
    left = run_program(boundaries["left_program"])
    right = run_program(boundaries["right_program"])
    require(left == boundaries["left_rows"], "left rows do not replay")
    require(right == boundaries["right_rows"], "right rows do not replay")
    require(boundaries["boundary_unit_ADDs_per_port"] == 76, "source ADD count changed")

    def adds_in(program, wires):
        return sum(1 for op, a, b in program if op == "ADD" and a in wires)

    def swaps_in(program, wires):
        return sum(1 for op, a, b in program if op == "SWAP" and a in wires)

    comp = set(COMPONENT)
    require(adds_in(boundaries["left_program"], comp) == 14, "left chain count")
    require(swaps_in(boundaries["left_program"], comp) == 2, "left swap count")
    require(all(b in comp for op, a, b in boundaries["left_program"] if a in comp), "component not closed")
    source_cost = 14 + 3 * 2
    require(source_cost == 20, "source component cost")

    left_comp = restrict(left, COMPONENT)
    right_comp = restrict(right, COMPONENT)
    even = restrict(left, EVEN)
    odd = restrict(left, ODD)

    # The inverse boundary is the reversed word (every ADD and SWAP is an
    # involution), so it has the same exact minimum.  Check it is the inverse.
    n = len(COMPONENT)
    composed = [0] * n
    for i in range(n):
        for j in range(n):
            if right_comp[i] >> j & 1:
                composed[i] ^= left_comp[j]
    require(tuple(composed) == tuple(1 << i for i in range(n)), "right is not the inverse of left")

    results = {}
    for label, target, floor in (("even9", even, 10), ("odd9", odd, 10), ("component18", left_comp, 20)):
        start = time.perf_counter()
        minimum, word, log = exact_minimum(target, floor, label)
        literal_check(word, list(range(len(target))), target)
        results[label] = minimum
        print(f"{label}: minimum={minimum} nodes_by_budget={[(b, nodes) for b, _, nodes, _ in log]} "
              f"seconds={time.perf_counter() - start:.1f}", flush=True)

    require(results == {"even9": 10, "odd9": 10, "component18": 20}, f"unexpected minima {results}")

    # Controls: the search must find known shorter words.
    # 1. The chain alone (no exchange) costs its 14 ADDs, below 20.
    chain_only = [1 << i for i in range(WIRES)]
    for op, a, b in boundaries["left_program"]:
        if op == "ADD":
            chain_only[a] ^= chain_only[b]
    chain_comp = restrict(chain_only, COMPONENT)
    found, _ = Search(chain_comp).reachable(14)
    require(found, "control: chain-only target should fit in 14")
    found, _ = Search(chain_comp).reachable(13)
    require(not found, "control: chain-only target should not fit in 13")
    # 2. A target with one chain ADD removed must be reachable in 9 on 9 wires.
    weakened = list(even)
    weakened[0] = 1  # wire 0 left unchanged
    found, word = Search(tuple(weakened)).reachable(9)
    require(found and len(word) <= 9, "control: weakened even target should fit in 9")
    # 3. A pure exchange of two wires costs exactly three.
    swap = (2, 1)
    require(not Search(swap).reachable(2)[0] and Search(swap).reachable(3)[0], "control: swap")

    print("one side: chain/exchange component 20 + three isolated exchanges 3*6 = 38; both sides 76")
    print("PASS_G20_CHAIN_EXCHANGE_FLOOR component18=20 even9=10 odd9=10 controls=4")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckError as exc:
        print(f"FAIL_G20_CHAIN_EXCHANGE_FLOOR: {exc}", file=sys.stderr)
        sys.exit(1)
