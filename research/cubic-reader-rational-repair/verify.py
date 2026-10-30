"""Exact bounded evidence for the cubic-reader repair theorem; stdlib only."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb, isqrt
from pathlib import Path
import platform


MAX_R = 10_000
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_r(r):
    require(type(r) is int and 2 <= r <= MAX_R, "r outside bounded domain")


def moments(r):
    validate_r(r)
    s1 = F(r * (r - 1), 2)
    s2 = F(r * (r - 1) * (2 * r - 1), 6)
    return s1, s2, s1 * s1


def rational_root(value):
    require(isinstance(value, F) and value >= 0, "invalid square-root input")
    a, b = isqrt(value.numerator), isqrt(value.denominator)
    if a * a == value.numerator and b * b == value.denominator:
        return F(a, b)
    return None


def repair(r):
    """Events (kind, source, coefficient); a += cb or y += c source^3."""
    s1, s2, s3 = moments(r)
    u = s2 / (2 * s1)
    root = rational_root(s3 / s1 - 3 * u * u)
    h = F(1) if root is None else root
    require(h > 0, "distinct query slopes required")
    weight = s1 / (2 * h)
    events = [("shift", "b", u + h - r), ("cube", "a", -weight),
              ("shift", "b", -2 * h), ("cube", "a", weight),
              ("shift", "b", -u + h)]
    residual = s3 - 3 * s1 * u * u - s1 * h * h
    if residual:
        events.append(("cube", "b", -residual))
    return tuple(event for event in events if event[2])


def batch(r, eager):
    validate_r(r)
    events = []
    for _ in range(r):
        events.extend((("cube", "a", F(1)), ("shift", "b", F(1))))
        if eager:
            events.append(("shift", "b", F(-1)))
    if not eager:
        events.extend(repair(r))
    return tuple(events)


def inverse(events):
    return tuple((kind, source, -c) for kind, source, c in reversed(events))


def execute(events, state):
    y, a, b = state
    for kind, source, coefficient in events:
        require(kind in ("shift", "cube"), "unknown event")
        require(source in ("a", "b"), "invalid source")
        if kind == "shift":
            require(source == "b", "shift must preserve b")
            a += coefficient * b
        else:
            value = a if source == "a" else b
            y += coefficient * value ** 3
    return y, a, b


def add(left, right):
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, F(0)) + coefficient
        if not result[exponent]:
            del result[exponent]
    require(len(result) <= 5, "polynomial state exceeds cubic capacity")
    return result


def scale(poly, coefficient):
    return {e: c * coefficient for e, c in poly.items() if c * coefficient}


def multiply(left, right):
    result = {}
    for x, cx in left.items():
        for z, cz in right.items():
            exponent = tuple(x[i] + z[i] for i in range(3))
            require(sum(exponent) <= 3, "degree exceeds cubic contract")
            result[exponent] = result.get(exponent, F(0)) + cx * cz
    return {e: c for e, c in result.items() if c}


def polynomial_endpoint(events):
    """Generic convolution, without the closed-form defect/moment formulas."""
    y, a, b = ({(1, 0, 0): F(1)}, {(0, 1, 0): F(1)},
               {(0, 0, 1): F(1)})
    for kind, source, coefficient in events:
        if kind == "shift":
            a = add(a, scale(b, coefficient))
        else:
            value = a if source == "a" else b
            cube = multiply(multiply(value, value), value)
            y = add(y, scale(cube, coefficient))
    return y, a, b


def check_polynomials():
    for r in range(2, 65):
        eager, deferred = batch(r, True), batch(r, False)
        expected = ({(1, 0, 0): F(1), (0, 3, 0): F(r)},
                    {(0, 1, 0): F(1)}, {(0, 0, 1): F(1)})
        require(polynomial_endpoint(eager) == expected, "eager endpoint")
        require(polynomial_endpoint(deferred) == expected, "repair endpoint")
        identity = polynomial_endpoint(())
        require(polynomial_endpoint(deferred + inverse(deferred)) == identity,
                "polynomial inverse endpoint")
        raw = tuple(event for _ in range(r) for event in
                    (("cube", "a", F(1)), ("shift", "b", F(1))))
        raw_output = polynomial_endpoint(raw)[0]
        s1, s2, s3 = moments(r)
        defect = add(raw_output, scale(expected[0], F(-1)))
        require(defect == {(0, 2, 1): 3 * s1, (0, 1, 2): 3 * s2,
                           (0, 0, 3): s3}, "chronological defect")
    return 63


def check_dirty_inputs():
    count = 0
    states = tuple(product((F(-1), F(0), F(1)), repeat=3))
    states += ((F(5, 7), F(-2, 3), F(7, 11)),
               (F(-4, 5), F(13, 8), F(-3, 2)))
    for r in range(2, 33):
        for eager in (True, False):
            events = batch(r, eager)
            for state in states:
                y, a, b = state
                result = execute(events, state)
                require(result == (y + r * a ** 3, a, b), "dirty endpoint")
                require(execute(inverse(events), result) == state, "dirty inverse")
                count += 1
    return count


def check_square_criterion():
    two_query = []
    for r in range(2, MAX_R + 1):
        q = F(2 * r * r - 2 * r - 1, 12)
        root = rational_root(q)
        k = isqrt(((2 * r - 1) ** 2 - 3) // 6)
        pell = (2 * r - 1) ** 2 - 6 * k * k == 3
        require((root is not None) == pell, "integer square criterion")
        if root is not None:
            two_query.append(r)
            require(2 * root == k, "Pell witness")
    require(two_query == [2, 14, 134, 1322], "bounded two-query arities")
    return two_query


def check_two_cube_coefficients():
    """Exhaust a bounded rational slope set, directly comparing all coefficients."""
    slopes = sorted({F(a, b) for a in range(-4, 5) for b in range(1, 4)})
    tested = 0
    for r in range(2, 25):
        s1, s2, s3 = moments(r)
        target = (F(0), 3 * s1, 3 * s2, s3)
        for t, s in combinations(slopes, 2):
            weight = s1 / (t - s)
            coefficients = tuple(weight * comb(3, j) * (t ** j - s ** j)
                                 for j in range(4))
            u, h = (t + s) / 2, (t - s) / 2
            predicted = (2 * s1 * u == s2 and
                         s1 * (3 * u * u + h * h) == s3)
            require((coefficients == target) == predicted, "two-cube necessity")
            tested += 1
    return len(slopes), tested


def rejected(call):
    try:
        call()
    except ValueError:
        return True
    return False


def check_controls():
    r, state = 3, (F(2), F(1), F(1))
    correct = batch(r, False)
    expected = execute(batch(r, True), state)
    require(execute(correct[:-1], state) != expected, "missing b-cube control")
    wrong = correct[:-1] + (("cube", "b", -correct[-1][2]),)
    require(execute(wrong, state) != expected, "b-cube sign control")
    no_restore = tuple(e for i, e in enumerate(correct) if i != len(correct) - 2)
    require(execute(no_restore, state) != expected, "unrestored source control")
    require(execute(tuple(reversed(correct)), state) != expected,
            "chronology control")
    require(rational_root(F(11, 12)) is None, "r=3 nonsquare boundary")
    require(rational_root(F(121, 4)) == F(11, 2), "r=14 square boundary")
    require([3 * a * a * b for a, b in ((0, 0), (1, 0), (0, 1))]
            == [0, 0, 0] and 3 * 1 * 1 * 1 == 3, "basis-only blind spot")
    invalid = (0, 1, -2, MAX_R + 1, True, "3")
    require(all(rejected(lambda value=value: repair(value)) for value in invalid),
            "invalid arity rejection")
    require(rejected(lambda: rational_root(F(-1))), "negative square rejection")
    return {"semantic": 7, "invalid_arities": len(invalid), "invalid_roots": 1}


def main():
    polynomial_arities = check_polynomials()
    dirty_cases = check_dirty_inputs()
    two_query = check_square_criterion()
    slopes, coefficient_cases = check_two_cube_coefficients()
    controls = check_controls()
    pilots = {}
    for r in (3, 14):
        events = repair(r)
        pilots[str(r)] = {"repair": [[k, s, str(c)] for k, s, c in events],
                          "cube_queries": sum(k == "cube" for k, _, _ in events),
                          "source_shifts": sum(k == "shift" for k, _, _ in events)}
    root = Path(__file__).resolve().parent
    receipt = {"status": "PASS_CUBIC_READER_RATIONAL_REPAIR", "python": platform.python_version(),
               "polynomial_arities": polynomial_arities, "dirty_cases": dirty_cases,
               "square_criterion_arities": MAX_R - 1, "two_query_arities": two_query,
               "rational_slopes": slopes, "coefficient_cases": coefficient_cases,
               "controls": controls, "pilots": pilots,
               "sha256": {name: sha256((root / name).read_bytes()).hexdigest()
                          for name in PACKAGE_FILES}}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
