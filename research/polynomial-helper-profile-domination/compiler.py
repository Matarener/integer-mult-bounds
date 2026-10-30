"""Bounded rational implementation of the zero-state linear extraction.

The universal statement is in PROOF.md. This module does not certify that a
polynomial word has a linear endpoint. Its caller must establish that premise.
"""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q

MAX_ROLES = 8
MAX_WIDTH = 4
MAX_GATES = 32
MAX_DEGREE = 4
MAX_COEFFICIENT = 1024
MAX_RUNTIME_BITS = 4096


@dataclass(frozen=True)
class Gate:
    source: int
    target: int
    operator: tuple[tuple[Q, ...], ...]
    polynomial: tuple[Q, ...]
    placement: str
    label: str


@dataclass(frozen=True)
class Program:
    roles: int
    width: int
    gates: tuple[Gate, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def bounded_scalar(value: Q) -> None:
    require(type(value) is Q, "coefficients must be Fractions")
    require(abs(value.numerator) <= MAX_COEFFICIENT, "numerator limit")
    require(value.denominator <= MAX_COEFFICIENT, "denominator limit")


def validate(program: Program) -> None:
    require(type(program.roles) is int, "integer role count required")
    require(type(program.width) is int, "integer width required")
    require(2 <= program.roles <= MAX_ROLES, "role limit")
    require(1 <= program.width <= MAX_WIDTH, "width limit")
    require(type(program.gates) is tuple, "immutable gate tuple required")
    require(len(program.gates) <= MAX_GATES, "gate limit")
    for gate in program.gates:
        require(type(gate.source) is int and type(gate.target) is int,
                "integer ports required")
        require(0 <= gate.source < program.roles, "source port")
        require(0 <= gate.target < program.roles, "target port")
        require(gate.source != gate.target, "aliased ports")
        require(gate.placement in ("before", "after"), "polynomial placement")
        require(type(gate.label) is str and 1 <= len(gate.label) <= 32,
                "paid label")
        require(type(gate.operator) is tuple, "immutable operator required")
        require(len(gate.operator) == program.width, "operator height")
        for row in gate.operator:
            require(type(row) is tuple and len(row) == program.width,
                    "operator width")
            for value in row:
                bounded_scalar(value)
        require(type(gate.polynomial) is tuple, "immutable polynomial required")
        require(1 <= len(gate.polynomial) <= MAX_DEGREE + 1, "degree limit")
        for value in gate.polynomial:
            bounded_scalar(value)
        require(gate.polynomial[0] == 0, "gate does not fix zero")


def linearize(program: Program) -> Program:
    validate(program)
    gates = []
    for gate in program.gates:
        coefficient = gate.polynomial[1] if len(gate.polynomial) > 1 else Q(0)
        if coefficient:
            gates.append(Gate(gate.source, gate.target, gate.operator,
                              (Q(0), coefficient), gate.placement, gate.label))
    result = Program(program.roles, program.width, tuple(gates))
    validate(result)
    return result


def profile(program: Program) -> dict[str, int]:
    validate(program)
    return dict(sorted(Counter(gate.label for gate in program.gates).items()))


def runtime_scalar(value: Q) -> Q:
    require(max(abs(value.numerator).bit_length(), value.denominator.bit_length())
            <= MAX_RUNTIME_BITS, "runtime scalar size limit")
    return value


def apply_operator(operator: tuple[tuple[Q, ...], ...],
                   vector: list[Q]) -> list[Q]:
    return [runtime_scalar(sum(
        (coefficient * value for coefficient, value in zip(row, vector)), Q(0)))
        for row in operator]


def polynomial_value(coefficients: tuple[Q, ...], value: Q) -> Q:
    result = Q(0)
    for coefficient in reversed(coefficients):
        result = runtime_scalar(result * value + coefficient)
    return result


def evaluate(program: Program, initial: tuple[Q, ...]) -> tuple[Q, ...]:
    validate(program)
    require(len(initial) == program.roles * program.width, "input shape")
    for value in initial:
        bounded_scalar(value)
    state = [list(initial[i * program.width:(i + 1) * program.width])
             for i in range(program.roles)]
    for gate in program.gates:
        source = state[gate.source]
        if gate.placement == "after":
            image = apply_operator(gate.operator, source)
            increment = [polynomial_value(gate.polynomial, value) for value in image]
        else:
            image = [polynomial_value(gate.polynomial, value) for value in source]
            increment = apply_operator(gate.operator, image)
        state[gate.target] = [runtime_scalar(old + new) for old, new in
                              zip(state[gate.target], increment)]
    return tuple(value for row in state for value in row)


def inverse(program: Program) -> Program:
    validate(program)
    result = Program(program.roles, program.width, tuple(
        Gate(g.source, g.target, g.operator, tuple(-c for c in g.polynomial),
             g.placement, g.label) for g in reversed(program.gates)))
    validate(result)
    return result
