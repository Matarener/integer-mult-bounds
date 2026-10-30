"""Explicit Gaussian profiles for the pinned producer's partial-sum gaps.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.

This module implements only the diagonal profiles and the reversible change of
bank coordinates.  It neither reads the source word nor supplies a native path.
The source-bound caller is responsible for authenticating each gap and applying
its actual frame pullback.  The finite reference uses at most nine address bits;
PROOF.md gives the algebraic statements at arbitrary rank.
"""

from math import comb


MAX_RANK = 9
KINDS = ("zero", "rank_one", "terminal")


class ClassifierError(ValueError):
    """Malformed data or a violated finite-reference contract."""


class OutsideProfile(ClassifierError):
    """A Gaussian division required by the profile is unavailable."""


def require(condition, message):
    if not condition:
        raise ClassifierError(message)


def _rank(rank):
    require(type(rank) is int and 0 <= rank <= MAX_RANK,
            "rank must be an integer in 0..9")
    return rank


def _array(values, rank=None):
    require(type(values) is list and values,
            "Gaussian array must be a nonempty list")
    size = len(values)
    require(size <= 1 << MAX_RANK and size & (size - 1) == 0,
            "Gaussian array length must be a power of two at most 512")
    actual = size.bit_length() - 1
    if rank is not None:
        require(_rank(rank) == actual, "array rank mismatch")
    for value in values:
        require(type(value) is tuple and len(value) == 2,
                "Gaussian value must be a tuple of two integers")
        require(all(type(component) is int for component in value),
                "Gaussian components must be integers, not Boolean values")
    return actual


def _add(a, b):
    return a[0] + b[0], a[1] + b[1]


def _sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def _times_pi(a):
    return a[0] - a[1], a[0] + a[1]


def _divide_pi(a):
    real, imag = a
    if (real + imag) % 2:
        raise OutsideProfile("required division by 1+i is not Gaussian integral")
    return (real + imag) // 2, (imag - real) // 2


def _pi_l1(exponent):
    """Sum of absolute real/imaginary parts of (1+i)**exponent."""
    return 1 << ((exponent + 1) // 2)


def profile(kind, rank=9):
    """Return a canonical diagonal and its algebraic/abstract gate invoice.

    ``zero`` describes B_r intersect 4 Z[i]^(2**r).
    ``rank_one`` describes q and C_0 q both in 4 Z[i]^(2**r).
    ``terminal`` describes 4 B_r, encoded using +4, not pi**4 = -4.

    Index exponents are logarithms to base two of Gaussian-lattice indices.
    They are not a physical storage, operation, or supplier-cost lower bound.
    Counts describe one in-place arithmetic schedule, not Python allocations.
    """
    _rank(rank)
    require(type(kind) is str and kind in KINDS, "unknown gap kind")
    require(kind != "rank_one" or rank >= 1,
            "rank-one profile needs address bit zero")
    size = 1 << rank
    if kind == "zero":
        exponents = [max(4 - mask.bit_count(), 0) for mask in range(size)]
        gain = sum(comb(rank, degree) * _pi_l1(max(4, degree))
                   for degree in range(rank + 1))
    elif kind == "rank_one":
        exponents = [max(4 - (mask & ~1).bit_count(), 0)
                     for mask in range(size)]
        gain = sum(comb(rank - 1, degree)
                   * (_pi_l1(max(4, degree)) + _pi_l1(max(4, degree) + 1))
                   for degree in range(rank))
    else:
        exponents = [4] * size
        gain = 4 * sum(comb(rank, degree) * _pi_l1(degree)
                       for degree in range(rank + 1))
    pairs = rank * (size // 2)
    diagonal_pi_steps = sum(exponents) if kind != "terminal" else 0
    return {
        "kind": kind,
        "rank": rank,
        "dimension": size,
        "exponents": exponents,
        "exponent_histogram": {str(k): exponents.count(k) for k in range(5)},
        "pi_index_exponent": sum(exponents),
        "coefficient_to_value_component_gain": gain,
        "encode_schedule": {
            "gaussian_additions": pairs,
            "gaussian_pi_multiplications": pairs + diagonal_pi_steps,
            "gaussian_doublings": 2 * size if kind == "terminal" else 0,
        },
        "decode_schedule": {
            "gaussian_subtractions": pairs,
            "exact_gaussian_pi_divisions": pairs + diagonal_pi_steps,
            "exact_gaussian_halvings": 2 * size if kind == "terminal" else 0,
        },
        "source_path_cost_included": False,
    }


def _encode_newton(coefficients):
    rank = _array(coefficients)
    values = coefficients[:]
    for bit in range(rank):
        step = 1 << bit
        for address in range(len(values)):
            if not address & step:
                other = address | step
                values[other] = _add(values[address], _times_pi(values[other]))
    return values


def _decode_newton(values):
    rank = _array(values)
    coefficients = values[:]
    for bit in reversed(range(rank)):
        step = 1 << bit
        for address in range(len(coefficients)):
            if not address & step:
                other = address | step
                coefficients[other] = _divide_pi(
                    _sub(coefficients[other], coefficients[address]))
    return coefficients


def encode_profile(coefficients, kind):
    """Encode arbitrary Gaussian coefficients into the named local profile.

    No actual frame pullback is performed here.  Terminal convention is +4 E c.
    Inputs are never mutated.  Python integers are exact and have no hidden
    fixed-width wraparound; the proof states explicit finite-width obligations.
    """
    rank = _array(coefficients)
    data = profile(kind, rank)
    if kind == "terminal":
        return [(4 * a, 4 * b) for a, b in _encode_newton(coefficients)]
    scaled = coefficients[:]
    for address, exponent in enumerate(data["exponents"]):
        for _ in range(exponent):
            scaled[address] = _times_pi(scaled[address])
    return _encode_newton(scaled)


def decode_profile(values, kind):
    """Invert the local profile, raising OutsideProfile off its image.

    Signed division is exact: a nonzero remainder rejects before // is used.
    The output consists of the arbitrary Gaussian coefficient coordinates,
    which are a different contract from the prepared native-domain array.
    """
    rank = _array(values)
    data = profile(kind, rank)
    coefficients = _decode_newton(values)
    if kind == "terminal":
        result = []
        for real, imag in coefficients:
            if real % 4 or imag % 4:
                raise OutsideProfile("terminal Newton coefficient is not divisible by 4")
            result.append((real // 4, imag // 4))
        return result
    for address, exponent in enumerate(data["exponents"]):
        for _ in range(exponent):
            coefficients[address] = _divide_pi(coefficients[address])
    return coefficients


def _banks(banks):
    require(type(banks) is list and banks,
            "bank sequence must be a nonempty list")
    rank = _array(banks[0])
    for bank in banks[1:]:
        _array(bank, rank)
    return rank


def prefix_difference(partials):
    """Recover chronological Y sources from their independent partial sums.

    For m banks this uses m-1 field subtractions.  The separate in-place
    schedule runs indices m-1 down to 1 so the earlier partial sum survives
    until its last use.  This functional implementation does not mutate inputs.
    """
    _banks(partials)
    return [partials[0][:]] + [
        [_sub(current, previous) for current, previous in zip(partials[j], partials[j - 1])]
        for j in range(1, len(partials))
    ]


def prefix_sum(sources):
    """Invert prefix_difference using m-1 chronological field additions."""
    _banks(sources)
    partials = [sources[0][:]]
    for source in sources[1:]:
        partials.append([_add(previous, value)
                         for previous, value in zip(partials[-1], source)])
    return partials
