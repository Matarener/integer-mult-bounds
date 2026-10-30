"""Exact finite corroboration of the ordering proof; standard library only."""

import argparse
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations_with_replacement, permutations, product
import json
from math import comb
from pathlib import Path

spec = spec_from_file_location(
    "smith_axis_circuit", Path(__file__).with_name("circuit.py")
)
if spec is None or spec.loader is None:
    raise ImportError("cannot load the package-local circuit")
circuit = module_from_spec(spec)
spec.loader.exec_module(circuit)
execute = circuit.execute
exchange_delta = circuit.exchange_delta
gather_mass = circuit.gather_mass
is_optimal_order = circuit.is_optimal_order
optimal_mass = circuit.optimal_mass
optimal_orders = circuit.optimal_orders


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def literal_mass(
    gaps: tuple[int, ...],
    precision: int,
    order: tuple[int, ...],
    delivery: bool = False,
) -> int:
    """Independent enumeration of every actual pair at every stage."""
    total = 0
    for position, axis in enumerate(order):
        relevant = order[position + 1 :] if delivery else order[:position]
        for coordinate in range(1 << len(gaps)):
            if coordinate & (1 << axis) == 0:
                debt = sum(gaps[j] for j in relevant if coordinate & (1 << j))
                total += max(0, precision - debt)
    return total


def ordering_checks() -> dict[str, int]:
    counts = {"profiles_with_precision": 0, "orders": 0, "exchanges": 0}
    for width in range(1, 6):
        for gaps in combinations_with_replacement(range(5), width):
            # Repeated gaps are still distinct physical axes; check all n! orders.
            orders = tuple(permutations(range(width)))
            for precision in range(9):
                gather, delivery = optimal_orders(gaps, precision)
                expected = literal_mass(gaps, precision, gather)
                require(optimal_mass(gaps, precision) == 2 * expected, "optimal total")
                require(
                    literal_mass(gaps, precision, delivery, True) == expected,
                    "delivery reversal",
                )
                counts["profiles_with_precision"] += 1
                for order in orders:
                    actual = literal_mass(gaps, precision, order)
                    require(
                        actual == gather_mass(gaps, precision, order), "mass formula"
                    )
                    require(actual >= expected, "suboptimal sorted gather")
                    require(
                        (actual == expected)
                        == is_optimal_order(gaps, precision, order),
                        "equality classification",
                    )
                    counts["orders"] += 1
                    for index in range(width - 1):
                        swapped = list(order)
                        swapped[index : index + 2] = reversed(
                            swapped[index : index + 2]
                        )
                        delta = Fraction(
                            actual - gather_mass(gaps, precision, tuple(swapped)),
                            1 << (width - 1),
                        )
                        prefix = tuple(gaps[j] for j in order[:index])
                        require(
                            delta
                            == exchange_delta(
                                prefix,
                                gaps[order[index]],
                                gaps[order[index + 1]],
                                precision,
                            ),
                            "exchange identity",
                        )
                        counts["exchanges"] += 1
    return counts


def reference_pi(exponent: int) -> tuple[int, int]:
    # Independent binomial expansion, rather than the interpreter's recurrence.
    return (
        sum(comb(exponent, j) * (-1) ** (j // 2) for j in range(0, exponent + 1, 2)),
        sum(
            comb(exponent, j) * (-1) ** ((j - 1) // 2)
            for j in range(1, exponent + 1, 2)
        ),
    )


def reference_product(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    real = left[0] * right[0] - left[1] * right[1]
    imag = left[1] * right[0] + left[0] * right[1]
    return real, imag


def dense_kernel(gaps: tuple[int, ...]) -> tuple[tuple[tuple[int, int], ...], ...]:
    factors = []
    for gap in gaps:
        value = reference_pi(gap)
        factors.append((((0, 1), (1, 0)), ((1, 0), (value[0], value[1] - 1))))
    matrix = []
    for row in range(1 << len(gaps)):
        entries = []
        for column in range(1 << len(gaps)):
            value = (1, 0)
            for axis, factor in enumerate(factors):
                value = reference_product(
                    value, factor[(row >> axis) & 1][(column >> axis) & 1]
                )
            entries.append(value)
        matrix.append(tuple(entries))
    return tuple(matrix)


def congruent(left: tuple[int, int], right: tuple[int, int], precision: int) -> bool:
    """Independent parity-lattice criterion for divisibility by pi**P."""
    real, imag = left[0] - right[0], left[1] - right[1]
    scale = 1 << (precision // 2)
    if real % scale or imag % scale:
        return False
    return precision % 2 == 0 or (real // scale - imag // scale) % 2 == 0


def dense_action(matrix: tuple, values: tuple) -> tuple:
    output = []
    for row in matrix:
        terms = [
            reference_product(coefficient, value)
            for coefficient, value in zip(row, values, strict=True)
        ]
        output.append((sum(term[0] for term in terms), sum(term[1] for term in terms)))
    return tuple(output)


def endpoint_case(
    gaps: tuple[int, ...],
    precision: int,
    values: tuple,
    matrix: tuple,
    gather: tuple[int, ...],
    delivery: tuple[int, ...],
) -> None:
    expected = dense_action(matrix, values)
    actual, mass = execute(gaps, precision, gather, delivery, values)
    require(
        all(congruent(a, b, precision) for a, b in zip(actual, expected, strict=True)),
        "heterogeneous tensor endpoint",
    )
    require(
        mass
        == literal_mass(gaps, precision, gather)
        + literal_mass(gaps, precision, delivery, True),
        "literal emitted tariff",
    )


def endpoint_checks() -> dict[str, int]:
    counts = {"basis_endpoints": 0, "arbitrary_endpoints": 0, "exhaustive_inputs": 0}
    for width in range(1, 5):
        for gaps in product(range(3), repeat=width):
            matrix = dense_kernel(gaps)
            length = 1 << width
            basis = [
                tuple((int(index == column), 0) for index in range(length))
                for column in range(length)
            ]
            arbitrary = [
                tuple(
                    ((index * 7 + seed * 3) % 13 - 6, (index * index + seed) % 11 - 5)
                    for index in range(length)
                )
                for seed in range(3)
            ]
            for precision in range(6):
                gather, delivery = optimal_orders(gaps, precision)
                for first, second in ((gather, delivery), (delivery, gather)):
                    for vector in basis:
                        endpoint_case(gaps, precision, vector, matrix, first, second)
                        counts["basis_endpoints"] += 1
                    for vector in arbitrary:
                        endpoint_case(gaps, precision, vector, matrix, first, second)
                        counts["arbitrary_endpoints"] += 1
    for gaps in ((0,), (1,), (2,), (4,), (1, 4)):
        matrix = dense_kernel(gaps)
        for precision in range(3):
            representatives = tuple(
                product(
                    range(1 << ((precision + 1) // 2)), range(1 << (precision // 2))
                )
            )
            gather, delivery = optimal_orders(gaps, precision)
            for vector in product(representatives, repeat=1 << len(gaps)):
                endpoint_case(gaps, precision, vector, matrix, gather, delivery)
                counts["exhaustive_inputs"] += 1
    return counts


def strict_fixture_endpoints() -> int:
    gaps, precision = (1, 4), 3
    matrix = dense_kernel(gaps)
    gather, delivery = optimal_orders(gaps, precision)
    vectors = [tuple((int(j == k), 0) for j in range(4)) for k in range(4)]
    vectors += [
        ((3, -2), (5, 7), (-1, 4), (6, -8)),
        ((-9, 11), (0, 1), (1, 0), (12, -13)),
    ]
    for vector in vectors:
        for first, second in ((gather, delivery), (delivery, gather)):
            endpoint_case(gaps, precision, vector, matrix, first, second)
    return 2 * len(vectors)


def controls() -> dict[str, object]:
    gaps, precision = (1, 4), 3
    gather, delivery = optimal_orders(gaps, precision)
    good = literal_mass(gaps, precision, gather) + literal_mass(
        gaps, precision, delivery, True
    )
    bad = literal_mass(gaps, precision, delivery) + literal_mass(
        gaps, precision, gather, True
    )
    require((good, bad) == (18, 22), "strict improving fixture")
    require(not is_optimal_order(gaps, precision, delivery), "wrong-direction control")
    require(is_optimal_order((4, 7), 3, (0, 1)), "clipped equality control")
    require(not congruent((0, 0), (1, 0), 3), "corrupt endpoint accepted")
    correct, _ = execute((4,), 3, (0,), (0,), ((0, 0), (1, 0)))
    require(not congruent(correct[0], (0, 0), 3), "early truncation witness")
    require(good != gather_mass(gaps, precision, gather), "omitted delivery control")
    invalid = [
        ((), 1, (), ()),
        ((-1,), 1, (0,), (0,)),
        ((65,), 1, (0,), (0,)),
        ((True,), 1, (0,), (0,)),
        ((1,), -1, (0,), (0,)),
        ((1,), 65, (0,), (0,)),
        ((1,), True, (0,), (0,)),
        ((1,), 1, (1,), (0,)),
        ((1, 2), 1, (0, 0), (0, 1)),
        ((1,), 1, (0,), (True,)),
    ]
    rejected = 0
    for profile, p, first, second in invalid:
        try:
            execute(profile, p, first, second, ((0, 0), (0, 0)))
        except ValueError:
            rejected += 1
        else:
            raise ArithmeticError("malformed input accepted")
    for vector in (((0, 0),), ((True, 0), (0, 0)), ((10**6 + 1, 0), (0, 0))):
        try:
            execute((1,), 1, (0,), (0,), vector)
        except ValueError:
            rejected += 1
        else:
            raise ArithmeticError("malformed Gaussian input accepted")
    return {
        "malformed_inputs_rejected": rejected,
        "semantic_controls": 6,
        "strict_fixture_endpoints": strict_fixture_endpoints(),
        "fixture": {
            "gaps": gaps,
            "precision": precision,
            "original_mass": bad,
            "optimal_mass": good,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = {
        "claim_type": "scoped proof with finite corroboration",
        "ordering": ordering_checks(),
        "endpoints": endpoint_checks(),
        "controls": controls(),
    }
    package = Path(__file__).resolve().parent
    result["package_sha256"] = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(package.iterdir())
        if path.is_file()
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        args.receipt.write_text(payload)
    print(payload, end="")
    print("PASS_SMITH_AXIS_ORDER")


if __name__ == "__main__":
    main()
