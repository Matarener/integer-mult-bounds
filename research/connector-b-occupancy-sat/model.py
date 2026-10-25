"""Independent occupancy CNF for the simple seven-source pattern-B problem.

No predecessor solver, path signatures, capacity tests or pruning is imported.
Nick Petalas. Apache-2.0.
"""

import itertools
from functools import lru_cache

MAX_VARIABLES = 60_000
MAX_CLAUSES = 500_000


def need(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(maxsize=1)
def paths():
    """All 112 ordered simple paths in Q3 starting at zero, including empty."""
    result = []
    for size in range(8):
        for tail in itertools.permutations(range(1, 8), size):
            vertices = (0, *tail)
            steps = tuple(a ^ b for a, b in itertools.pairwise(vertices))
            if all(step in (1, 2, 4) for step in steps):
                word = tuple(step.bit_length() - 1 for step in steps)
                result.append((vertices, word))
    need(len(result) == 112, "Q3 ordered-path census")
    return tuple(result)


def canonical(word):
    representatives = []
    for permutation in itertools.permutations((1, 2, 3)):
        mapping = (0, *permutation)
        renamed = tuple(mapping[x] for x in word)
        for oriented in (renamed, renamed[::-1]):
            representatives.extend(oriented[i:] + oriented[:i] for i in range(10))
    return min(representatives)


@lru_cache(maxsize=1)
def templates():
    """Position-subset enumeration of all labeled (4,2,2,2) low words."""
    result = set()
    for heavy in itertools.combinations(range(10), 4):
        remaining = [i for i in range(10) if i not in heavy]
        for one in itertools.combinations(remaining, 2):
            last = [i for i in remaining if i not in one]
            for two in itertools.combinations(last, 2):
                word = [3] * 10
                for positions, label in ((heavy, 0), (one, 1), (two, 2)):
                    for position in positions:
                        word[position] = label
                points, end = prefix_points(word)
                need(end == 0, "even low counts restore")
                if len({a ^ b for a in points for b in points}) == 16:
                    result.add(canonical(word))
    need(len(result) == 77, "complete B low-orbit census")
    return tuple(sorted(result))


def prefix_points(word):
    state, points = 0, []
    for label in word:
        points.append(state)
        state ^= 1 << label
    return points, state


class Formula:
    def __init__(self):
        self.variables = {}
        self.clauses = []
        self.choices = []

    def var(self, *key):
        if key not in self.variables:
            need(len(self.variables) < MAX_VARIABLES, "variable budget exhausted")
            self.variables[key] = len(self.variables) + 1
        return self.variables[key]

    def add(self, clause):
        need(len(self.clauses) < MAX_CLAUSES, "clause budget exhausted")
        self.clauses.append(list(clause))

    def iff_or(self, result, arguments):
        self.add([-result, *arguments])
        for argument in arguments:
            self.add([-argument, result])

    def exactly_one(self, literals, name):
        self.add(literals)
        previous = None
        for i, literal in enumerate(literals):
            state = self.var("seen", name, i)
            if previous is None:
                self.add([-literal, state])
            else:
                self.add([-literal, state])
                self.add([-previous, state])
                self.add([-previous, -literal])
            previous = state

    def exactly_count(self, literals, count, name):
        """Unary prefix sums, capped at count+1, with complete equivalences."""
        need(
            0 <= count <= len(literals) <= 120 and len(literals) > 0,
            "cardinality bounds",
        )
        previous = []
        for i, literal in enumerate(literals):
            current = []
            for k in range(1, count + 2):
                state = self.var("sum", name, i, k)
                prior = previous[k - 1] if previous else None
                lower = previous[k - 2] if previous and k > 1 else None
                if k == 1:
                    self.iff_or(state, ([prior] if prior else []) + [literal])
                elif lower is None:
                    self.add([-state])
                else:
                    conjunction = self.var("increment", name, i, k)
                    self.add([-conjunction, literal])
                    self.add([-conjunction, lower])
                    self.add([conjunction, -literal, -lower])
                    self.iff_or(state, [prior, conjunction])
                current.append(state)
            previous = current
        if count:
            self.add([previous[count - 1]])
        self.add([-previous[count]])


def block(formula, index, fixed):
    choices = []
    for start in range(8):
        if index == 0 and start:
            continue
        for ordinal, (vertices, word) in enumerate(paths()):
            selected = formula.var("path", index, start, ordinal)
            choices.append((selected, start, vertices, word))
            visited = {vertex ^ start for vertex in vertices}
            end = vertices[-1] ^ start
            for vertex in range(8):
                literal = formula.var("occupancy", index, vertex)
                formula.add([-selected, literal if vertex in visited else -literal])
            for axis in range(3):
                for field, value in (("start", start), ("end", end)):
                    literal = formula.var(field, index, axis)
                    formula.add([-selected, literal if value >> axis & 1 else -literal])
                for threshold in range(1, 5):
                    literal = formula.var("count", index, axis, threshold)
                    formula.add(
                        [
                            -selected,
                            literal if word.count(axis) >= threshold else -literal,
                        ]
                    )
    formula.exactly_one([row[0] for row in choices], ("path", index))
    if fixed is not None:
        matching = [x for x, start, _, word in choices if (start, word) == fixed]
        need(len(matching) == 1, "fixed ordered path absent")
        formula.add(matching)
    formula.choices.append(choices)


def high_symmetry(formula, blocks):
    """Equal-count axes can be renamed in their first-appearance order."""
    for index in range(blocks):
        for axis in range(3):
            before = formula.var("used", index, axis)
            after = formula.var("used", index + 1, axis)
            if index == 0:
                formula.add([-before])
            formula.iff_or(after, [before, formula.var("count", index, axis, 1)])
        for selected, _, _, word in formula.choices[index]:
            seen = set()
            for axis in word:
                for smaller in range(axis):
                    if smaller not in seen:
                        formula.add([-selected, formula.var("used", index, smaller)])
                seen.add(axis)


def occupancy(formula, lows, cover):
    for i in range(len(lows)):
        for j in range(i + 1, len(lows)):
            if lows[i] == lows[j]:
                for vertex in range(8):
                    formula.add(
                        [
                            -formula.var("occupancy", i, vertex),
                            -formula.var("occupancy", j, vertex),
                        ]
                    )
    for low in range(16):
        for high in range(8):
            readers = [
                formula.var("occupancy", j, high)
                for j in range(len(lows))
                if lows[j] == low
            ]
            formula.iff_or(formula.var("point", 8 * low + high), readers)
    if not cover:
        return
    for difference in range(1, 128):
        witnesses = []
        for first in range(128):
            second = first ^ difference
            if first >= second:
                continue
            witness = formula.var("difference", difference, first)
            left, right = (formula.var("point", vertex) for vertex in (first, second))
            formula.add([-witness, left])
            formula.add([-witness, right])
            formula.add([witness, -left, -right])
            witnesses.append(witness)
        formula.add(witnesses)


def build(low, target=(4, 4, 4), cover=True, fixed=None, symmetry=True):
    need(
        1 <= len(low) <= 10 and all(type(x) is int and 0 <= x < 4 for x in low),
        "low-word bounds",
    )
    need(
        len(target) == 3 and all(type(x) is int and 0 <= x <= 8 for x in target),
        "target-count bounds",
    )
    lows, end = prefix_points(low)
    need(end == 0, "low word must restore")
    need(fixed is None or len(fixed) == len(low), "fixed-path count")
    formula = Formula()
    for index in range(len(low)):
        block(formula, index, None if fixed is None else fixed[index])
    for index in range(len(low)):
        for axis in range(3):
            end = formula.var("end", index, axis)
            start = formula.var("start", (index + 1) % len(low), axis)
            formula.add([-end, start])
            formula.add([end, -start])
    for axis in range(3):
        counts = [
            formula.var("count", j, axis, k)
            for j in range(len(low))
            for k in range(1, 5)
        ]
        formula.exactly_count(counts, target[axis], axis)
    occupancy(formula, lows, cover)
    if symmetry:
        need(
            target == (4, 4, 4) and fixed is None,
            "symmetry requires equal counts and unfixed paths",
        )
        high_symmetry(formula, len(low))
    return formula


def word_from(formula, low, assignment):
    selected = set(assignment)
    word, high = [], 0
    for index, choices in enumerate(formula.choices):
        chosen = [(start, path) for x, start, _, path in choices if x in selected]
        need(len(chosen) == 1 and chosen[0][0] == high, "model path choice/join")
        for label in chosen[0][1]:
            word.append(label)
            high ^= 1 << label
        word.append(low[index] + 3)
    need(high == 0, "model high restoration")
    return word


def check_word(word, target, cover):
    need(len(word) <= 80 and all(0 <= x < 7 for x in word), "ordinary-word bounds")
    points, end = prefix_points(word)
    counts = tuple(word.count(axis) for axis in range(3))
    coverage = len({a ^ b for a in points for b in points})
    need(
        end == 0 and len(set(points)) == len(points), "ordinary restoration/simplicity"
    )
    need(
        counts == target and (not cover or coverage == 128), "ordinary counts/coverage"
    )
    return {"length": len(word), "coverage": coverage, "counts": counts}
