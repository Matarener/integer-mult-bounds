"""Bounded exact transpose endpoints using classical integer substitution.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction

MAX_ROLES = 1024
MAX_EVENTS = 60000
MAX_BITS = 4096
MAX_PACKED_BITS = 128000000
KINDS = frozenset(("ADD", "COPY", "SCALE", "INIT", "CLEAR"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(n, events, expected):
    require(type(n) is int and 1 <= n <= MAX_ROLES, "role limit")
    require(
        isinstance(events, (tuple, list)) and len(events) <= MAX_EVENTS, "event limit"
    )
    require(len(expected) == n, "expected row count")
    for kind, r, s, numerator, shift in events:
        require(kind in KINDS, "opcode")
        require(type(r) is int and 0 <= r < n, "destination")
        require(type(s) is int and 0 <= s < n, "source")
        require(
            type(numerator) is int and 0 < abs(numerator) < 2**20, "numerator limit"
        )
        require(type(shift) is int and 0 <= shift <= 32, "denominator limit")
        require(kind not in ("ADD", "COPY") or s != r, "distinct roles")
    for row in expected:
        require(isinstance(row, dict) and len(row) <= n, "expected row")
        for column, value in row.items():
            require(type(column) is int and 0 <= column < n, "expected column")
            require(type(value) in (int, Fraction), "expected coefficient")
            q = Fraction(value)
            d = q.denominator
            require(d & (d - 1) == 0, "dyadic expected coefficient")
            require(
                max(abs(q.numerator).bit_length(), d.bit_length()) <= MAX_BITS,
                "expected bit limit",
            )


def step(values, exponents, event, absolute=False):
    """Transpose one event; with absolute coefficients, propagate an l1 bound."""
    kind, r, s, numerator, shift = event
    if kind in ("INIT", "CLEAR"):
        values[r], exponents[r] = 0, 0
        return
    if absolute:
        numerator = abs(numerator)
    if kind == "SCALE":
        require(exponents[r] + shift <= MAX_BITS, "exponent limit")
        values[r] *= numerator
        exponents[r] += shift
        return
    level = max(exponents[s], exponents[r] + shift)
    require(level <= MAX_BITS, "exponent limit")
    values[s] = (values[s] << (level - exponents[s])) + numerator * (
        values[r] << (level - exponents[r] - shift)
    )
    exponents[s] = level
    if kind == "COPY":
        values[r], exponents[r] = 0, 0


def expected_row(row, exponent):
    level = max(
        [exponent] + [Fraction(q).denominator.bit_length() - 1 for q in row.values()]
    )
    coefficients = []
    for column, value in row.items():
        q = Fraction(value)
        numerator = q.numerator << (level - q.denominator.bit_length() + 1)
        coefficients.append((column, numerator))
    return coefficients, level


def plan(n, events, expected):
    validate(n, events, expected)
    bounds, exponents = [1] * n, [0] * n
    largest = 1
    for event in reversed(events):
        step(bounds, exponents, event, absolute=True)
        largest = max(largest, bounds[event[1]], bounds[event[2]])
        require(largest.bit_length() <= MAX_BITS, "growth limit")
    targets = []
    for row, bound, exponent in zip(expected, bounds, exponents, strict=False):
        coefficients, level = expected_row(row, exponent)
        difference_bound = (bound << (level - exponent)) + sum(
            abs(q) for _, q in coefficients
        )
        largest = max(largest, difference_bound)
        targets.append((coefficients, level))
    width = largest.bit_length() + 1
    require(width <= MAX_BITS + 1, "comparison growth limit")
    require(n * n * width <= MAX_PACKED_BITS, "packed memory limit")
    return width, targets


def check_transpose(n, events, expected):
    """Check all n squared endpoint coefficients, never a random fingerprint."""
    width, targets = plan(n, events, expected)
    values = [1 << (width * i) for i in range(n)]
    exponents = [0] * n
    for event in reversed(events):
        step(values, exponents, event)
    for r, (coefficients, level) in enumerate(targets):
        encoded = sum(q << (width * column) for column, q in coefficients)
        actual = values[r] << (level - exponents[r])
        require(actual == encoded, "transpose endpoint row " + str(r))
    return {
        "columns": n,
        "coefficients": n * n,
        "arithmetic": "Dense integer rows with binary denominators; reverse chronology",
    }


def source_events(word):
    """Project the retained P104 scalar syntax; frame/ownership checks stay external."""
    require(
        type(word.get("public")) is int and 1 <= word["public"] <= 1016, "public roles"
    )
    program = word.get("program")
    require(isinstance(program, list) and len(program) <= MAX_EVENTS, "program limit")
    n = word["public"] + 8
    events = []
    for e in program:
        require(isinstance(e, list) and len(e) >= 2, "event shape")
        kind, r = e[:2]
        if kind == "MOVE":
            require(len(e) == 5, "MOVE shape")
            continue
        if kind in ("INIT", "CLEAR"):
            require(len(e) == 3, "lifetime shape")
            events.append((kind, r, r, 1, 0))
            continue
        require(kind in ("ADD", "COPY", "SCALE"), "scalar opcode")
        require(len(e) == (4 if kind == "SCALE" else 5), "scalar shape")
        require(type(e[-2]) in (int, str), "coefficient syntax")
        require(len(str(e[-2])) <= 64, "coefficient text limit")
        q = Fraction(e[-2])
        require(q.denominator & (q.denominator - 1) == 0, "dyadic coefficient")
        events.append(
            (
                kind,
                r,
                e[2] if kind != "SCALE" else r,
                q.numerator,
                q.denominator.bit_length() - 1,
            )
        )
    live = word.get("live")
    require(isinstance(live, list) and len(live) <= n, "live roles")
    require(
        all(type(r) is int and 0 <= r < word["public"] - 112 for r in live),
        "live output bound",
    )
    require(len(live) == len(set(live)), "duplicate live role")
    expected = [{r: 1} if r < word["public"] else {} for r in range(n)]
    for r in live:
        expected[r][r + 112] = 1
    return n, events, expected


def reverse_columns(word):
    return check_transpose(*source_events(word))
