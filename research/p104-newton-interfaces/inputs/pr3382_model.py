"""Exact Gaussian Newton-lattice reference for the pinned P104 collector.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
The all-rank statements are written in PROOF.md. This finite reference accepts
at most nine address bits and 8192 magnitude bits per real array component. It imports
no predecessor implementation and makes no recursive or physical cost claim.
"""

from math import comb, isqrt

MAX_RANK = 9
MAX_COMPONENT_BITS = 8192
PI = (1, 1)
ZERO = (0, 0)


class ModelError(ValueError):
    """A malformed input or violated finite-reference contract."""


class OutsideLattice(ModelError):
    """A required exact Gaussian division is unavailable."""


def require(condition, message):
    if not condition:
        raise ModelError(message)


def rank_check(rank):
    require(type(rank) is int and 0 <= rank <= MAX_RANK, "rank must be in 0..9")
    return rank


def gaussian_check(value):
    require(type(value) is tuple and len(value) == 2, "Gaussian value must be a pair")
    require(all(type(x) is int for x in value), "Gaussian components must be integers")
    require(all(x.bit_length() <= MAX_COMPONENT_BITS for x in value),
            "Gaussian component exceeds finite reference limit")
    return value


def validate(values, rank=None):
    require(type(values) is list and values, "array must be a nonempty list")
    size = len(values)
    require(size <= 1 << MAX_RANK and size & (size - 1) == 0, "binary array length")
    actual = size.bit_length() - 1
    if rank is not None:
        require(rank_check(rank) == actual, "array rank mismatch")
    for value in values:
        gaussian_check(value)
    return actual


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def rot(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def times_pi(value):
    return value[0] - value[1], value[0] + value[1]


def divide_pi(value):
    a, b = value
    if (a + b) % 2:
        raise OutsideLattice("not divisible by 1+i")
    return (a + b) // 2, (b - a) // 2


def half_exact(value):
    if value[0] % 2 or value[1] % 2:
        raise OutsideLattice("ideal Gaussian pair has a nonintegral component")
    return value[0] // 2, value[1] // 2


def pi_power(exponent):
    rank_check(exponent)
    result = (1, 0)
    for _ in range(exponent):
        result = times_pi(result)
    return result


def encode(coefficients):
    """E_r c, with E_1(c0,c1)=(c0,c0+(1+i)c1), in address-bit order."""
    rank = validate(coefficients)
    out = coefficients[:]
    for bit in range(rank):
        step = 1 << bit
        for address in range(len(out)):
            if not address & step:
                out[address | step] = add(out[address], times_pi(out[address | step]))
    validate(out, rank)
    return out


def decode(values):
    """Exact E_r inverse; membership fails on an unavailable pi division."""
    rank = validate(values)
    out = values[:]
    for bit in reversed(range(rank)):
        step = 1 << bit
        for address in range(len(out)):
            if not address & step:
                out[address | step] = divide_pi(sub(out[address | step], out[address]))
    validate(out, rank)
    return out


def member(values):
    validate(values)
    try:
        decode(values)
    except OutsideLattice:
        return False
    return True


def newton(values):
    """Unweighted multilinear coefficients, obtained by Boolean differences."""
    rank = validate(values)
    out = values[:]
    for bit in range(rank):
        step = 1 << bit
        for address in range(len(out)):
            if not address & step:
                out[address | step] = sub(out[address | step], out[address])
    validate(out, rank)
    return out


def ideal_pair_numerators(a, b, inverse=False):
    """Return twice C(a,b), so nonintegral examples can be checked exactly."""
    gaussian_check(a)
    gaussian_check(b)
    require(type(inverse) is bool, "inverse flag must be Boolean")
    total = add(a, b)
    difference = rot(sub(a, b), 3 if inverse else 1)
    return add(total, difference), sub(total, difference)


def ideal_pair(a, b, inverse=False):
    first, second = ideal_pair_numerators(a, b, inverse)
    return half_exact(first), half_exact(second)


def lift_pair(a, b, inverse=False):
    """Literal componentwise signed-floor lifting, without a grid change."""
    gaussian_check(a)
    gaussian_check(b)
    require(type(inverse) is bool, "inverse flag must be Boolean")
    difference = sub(a, b)
    middle = add(b, (difference[0] // 2, difference[1] // 2))
    difference = rot(difference, 3 if inverse else 1)
    second = sub(middle, (difference[0] // 2, difference[1] // 2))
    return add(second, difference), second


def stage(values, bit, inverse=False, literal=False):
    rank = validate(values)
    require(type(bit) is int and 0 <= bit < rank, "address bit outside array")
    require(type(inverse) is bool and type(literal) is bool, "stage flags must be Boolean")
    out = values[:]
    step = 1 << bit
    pair = lift_pair if literal else ideal_pair
    for address in range(len(out)):
        if not address & step:
            other = address | step
            out[address], out[other] = pair(out[address], out[other], inverse)
    validate(out, rank)
    return out


def ideal_stage(values, bit, inverse=False):
    return stage(values, bit, inverse=inverse)


def lift_stage(values, bit, inverse=False):
    return stage(values, bit, inverse=inverse, literal=True)


def gate_bits(kind, bits, rank):
    require(kind in ("C", "CINV", "S", "SINV", "X", "SWAP", "CNOT", "CZ"),
            "unsupported gate")
    count = 2 if kind in ("SWAP", "CNOT", "CZ") else 1
    require(type(bits) in (tuple, list) and len(bits) == count, "gate arity")
    require(all(type(bit) is int and 0 <= bit < rank for bit in bits), "gate address bits")
    require(len(set(bits)) == len(bits), "gate bits must be distinct")
    return tuple(bits)


def value_gate(values, kind, bits):
    """The physical Gaussian gate; CNOT bits are (control,target)."""
    rank = validate(values)
    bits = gate_bits(kind, bits, rank)
    if kind in ("C", "CINV"):
        return ideal_stage(values, bits[0], inverse=kind == "CINV")
    out = [ZERO] * len(values)
    for address, value in enumerate(values):
        target, phase = address, 0
        first = (address >> bits[0]) & 1
        if kind == "X":
            target ^= 1 << bits[0]
        elif kind in ("S", "SINV"):
            phase = first * (1 if kind == "S" else 3)
        elif kind == "CNOT":
            target ^= first << bits[1]
        elif kind == "CZ":
            phase = 2 * first * ((address >> bits[1]) & 1)
        elif first != ((address >> bits[1]) & 1):
            target ^= (1 << bits[0]) | (1 << bits[1])
        out[target] = rot(value, phase)
    return out


def coefficient_pair(a, b, kind):
    if kind == "C":
        return add(a, b), rot(b, 1)
    if kind == "CINV":
        last = rot(b, 3)
        return sub(a, last), last
    if kind == "S":
        return a, rot(add(a, b), 1)
    if kind == "SINV":
        return a, sub(rot(b, 3), a)
    require(kind == "X", "unsupported coefficient pair")
    return add(a, times_pi(b)), rot(b, 2)


def coefficient_gate(coefficients, kind, bits):
    """Direct integral E^-1 gate E formulas; no encode/decode calls."""
    rank = validate(coefficients)
    bits = gate_bits(kind, bits, rank)
    if kind == "SWAP":
        return value_gate(coefficients, kind, bits)
    out = coefficients[:]
    first = 1 << bits[0]
    if len(bits) == 1:
        for address in range(len(out)):
            if not address & first:
                other = address | first
                out[address], out[other] = coefficient_pair(out[address], out[other], kind)
        validate(out, rank)
        return out
    second = 1 << bits[1]
    for address in range(len(out)):
        if address & (first | second):
            continue
        a, b, c, d = (out[address | mask] for mask in (0, first, second, first | second))
        if kind == "CNOT":
            out[address | first] = add(add(b, c), times_pi(d))
            out[address | first | second] = sub(rot(times_pi(c), 1), d)
        else:
            require(kind == "CZ", "unsupported coefficient block")
            out[address | first | second] = sub(add(rot(a, 1), rot(times_pi(add(b, c)), 1)), d)
    validate(out, rank)
    return out


def wrapper_plan(record):
    """Exact source convention: input x receives its phase, then moves to Ax+b."""
    keys = {"matrix_rows", "offset", "linear_Z4", "quadratic_rows", "phase"}
    require(type(record) is dict and set(record) == keys, "wrapper schema")
    rows, linear, quadratic = (record[name] for name in
                               ("matrix_rows", "linear_Z4", "quadratic_rows"))
    require(type(rows) is list, "wrapper matrix rows")
    rank = rank_check(len(rows))
    require(type(linear) is list and type(quadratic) is list, "wrapper phase arrays")
    require(len(linear) == len(quadratic) == rank, "wrapper dimensions")
    size = 1 << rank
    require(all(type(row) is int and 0 <= row < size for row in rows + quadratic),
            "wrapper binary rows")
    require(all(type(value) is int and 0 <= value < 4 for value in linear), "linear phases")
    require(type(record["offset"]) is int and 0 <= record["offset"] < size, "affine offset")
    require(type(record["phase"]) is int and 0 <= record["phase"] < 4, "global phase")
    result = []
    for address in range(size):
        target = record["offset"]
        phase = record["phase"]
        for j in range(rank):
            target ^= ((rows[j] & address).bit_count() & 1) << j
            if address >> j & 1:
                phase += linear[j]
                for k in range(j + 1, rank):
                    phase += 2 * ((quadratic[j] >> k) & 1) * ((address >> k) & 1)
        result.append((target, phase % 4))
    require(len({target for target, _ in result}) == size, "wrapper must be bijective")
    return result


def wrapper(values, record, inverse=False):
    validate(values)
    require(type(inverse) is bool, "inverse flag must be Boolean")
    plan = wrapper_plan(record)
    require(len(plan) == len(values), "wrapper and array dimensions")
    out = [ZERO] * len(values)
    for source, (target, phase) in enumerate(plan):
        if inverse:
            out[source] = rot(values[target], -phase)
        else:
            out[target] = rot(values[source], phase)
    return out


def codec_ledger(rank):
    rank_check(rank)
    size = 1 << rank
    pairs = rank * size // 2
    return {"rank": rank, "complex_coordinates": size, "pairs_per_direction": pairs,
            "encode": {"gaussian_adds": pairs, "pi_multiplications": pairs,
                       "real_add_subtracts": 4 * pairs, "component_reads": 4 * pairs,
                       "component_writes": 2 * pairs},
            "decode": {"gaussian_subtracts": pairs, "exact_pi_divisions": pairs,
                       "real_add_subtracts": 4 * pairs, "exact_real_halves": 2 * pairs,
                       "component_reads": 4 * pairs, "component_writes": 2 * pairs},
            "owned_in_place_complex_words": size, "pair_real_work_words": 4,
            "borrowed_input_copy_included": False, "routing_included": False}


def codec_bounds(rank, component_bound):
    """Sufficient integer bounds, per codec's own entrance; not physical prices."""
    rank_check(rank)
    require(type(component_bound) is int and component_bound >= 0, "nonnegative bound")
    gain = sum(comb(rank, k) * sum(abs(x) for x in pi_power(k)) for k in range(rank + 1))
    inverse_gain = 1 << ((rank + 1) // 2)
    return {"rank": rank, "entrance_component_bound": component_bound,
            "encode_component_gain": gain, "encode_component_bound": gain * component_bound,
            "encode_scratch_bound": 3 * gain * component_bound,
            "decode_component_gain": inverse_gain,
            "decode_component_bound": inverse_gain * component_bound,
            "decode_scratch_bound": 4 * inverse_gain * component_bound}


def collector_bounds(rank, source_count, component_bound):
    rank_check(rank)
    require(type(source_count) is int and 1 <= source_count <= 5, "source count in 1..5")
    require(type(component_bound) is int and component_bound >= 0, "nonnegative bound")
    size = 1 << rank
    root = isqrt(2 * size)
    if root * root < 2 * size:
        root += 1
    native = source_count * root * component_bound
    return {"rank": rank, "entrance_component_bound": component_bound,
            "source_count": source_count, "native_prefix_component_bound": native,
            "query_component_bound": native + component_bound,
            "pair_scratch_component_bound": 5 * native,
            "assumption": "exact unitary native prefixes on the admitted lattice"}


def collector_ledger(rank, native_rank, wrapper_cycle_counts):
    """Complete direct collector counts; four actual source wrappers are required."""
    rank_check(rank)
    require(type(native_rank) is int and 1 <= native_rank <= rank, "native rank")
    size = 1 << rank
    require(type(wrapper_cycle_counts) is list and len(wrapper_cycle_counts) == 4,
            "four literal wrapper cycle counts required")
    require(all(type(c) is int and 1 <= c <= size for c in wrapper_cycle_counts),
            "wrapper cycle count")
    pairs = native_rank * size
    swaps = 4 * size + sum(wrapper_cycle_counts)
    return {"complex_coordinates": size, "native_rank_each_direction": native_rank,
            "paired_butterflies": pairs, "field_adds": 11,
            "real_add_subtracts": 8 * pairs + 22 * size,
            "floor_halves": 4 * pairs, "butterfly_quarter_turns": pairs,
            "wrapper_cycle_counts": wrapper_cycle_counts[:],
            "wrapper_cycles": sum(wrapper_cycle_counts), "wrapper_swaps": swaps,
            "wrapper_unit_phases": 4 * size,
            "butterfly_component_reads": 4 * pairs, "butterfly_component_writes": 4 * pairs,
            "field_add_component_reads": 44 * size, "field_add_component_writes": 22 * size,
            "source_component_reads_within_field_adds": 20 * size,
            "wrapper_swap_component_reads": 4 * swaps, "wrapper_swap_component_writes": 4 * swaps,
            "private_initialization_components": 2 * size, "private_zero_check_components": 2 * size,
            "borrowed_source_complex_words": 5 * size, "mutable_query_complex_words": size,
            "owned_private_complex_words": size, "wrapper_zero_scratch_complex_words": 1,
            "pair_real_work_words": 4, "codecs_included": False,
            "physical_routing_and_recursive_tariff_included": False}


def cold_codec_ledger(rank):
    """Optional T=E^-1 U E caller: prepare five owned source banks and query."""
    codec = codec_ledger(rank)
    size = 1 << rank
    pairs = codec["pairs_per_direction"]
    return {"rank": rank, "encodes": 6, "decodes": 6,
            "owned_source_copy_adds": 5, "owned_source_cleanup_adds": 5,
            "extra_owned_source_complex_words": 5 * size,
            "extra_private_initialization_components": 10 * size,
            "extra_private_zero_check_components": 10 * size,
            "codec_real_add_subtracts": 48 * pairs,
            "codec_exact_real_halves": 12 * pairs,
            "codec_pi_multiplications": 6 * pairs, "codec_exact_pi_divisions": 6 * pairs,
            "codec_component_reads": 48 * pairs, "codec_component_writes": 24 * pairs,
            "copy_cleanup_real_add_subtracts": 20 * size,
            "copy_cleanup_component_reads": 40 * size,
            "copy_cleanup_component_writes": 20 * size,
            "add_to_direct_collector_invoice": True,
            "logical_output_map": "T = E_r^-1 U E_r",
            "original_U_caller_admitted": False,
            "physical_routing_and_recursive_tariff_included": False}


def cold_codec_bounds(rank, component_bound):
    """Compose the optional cold caller's bounds from its raw coefficient entry."""
    encoder = codec_bounds(rank, component_bound)
    physical = collector_bounds(rank, 5, encoder["encode_component_bound"])
    decoder = codec_bounds(rank, physical["query_component_bound"])
    return {"rank": rank, "raw_entrance_component_bound": component_bound,
            "encoded_component_bound": encoder["encode_component_bound"],
            "native_prefix_component_bound": physical["native_prefix_component_bound"],
            "encoded_query_component_bound": physical["query_component_bound"],
            "decoded_query_component_bound": decoder["decode_component_bound"],
            "complete_scratch_component_bound": max(encoder["encode_scratch_bound"],
                                                      physical["pair_scratch_component_bound"],
                                                      decoder["decode_scratch_bound"]),
            "logical_output_map": "T = E_r^-1 U E_r"}
