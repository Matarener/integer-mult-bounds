"""Strict arithmetic models for the restored-query map in PROOF.md.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.

The caller supplies 52 distinct Gaussian coefficient banks, a separate query,
and the five source-bound terminal slots.  This module neither derives those
slots nor proves that a query belongs to the inherited Newton lattice.  It
implements Q += E_r(sum of the five terminal coefficient banks), restores all
52 coefficient banks, and cleans one real arithmetic scratch register.

Only target += source, target -= source, explicit doubling, and checked exact
real halving change arithmetic registers.  In particular, there is no
source-minus-target overwrite primitive.  Python allocations make this a
functional reference model; the reported storage is the separately described
logical in-place schedule, not a measurement of Python memory or physical tape
cost.  Integers have unbounded precision and every observed width is recorded.
"""

from __future__ import annotations

import hashlib
import json
from math import comb


class DirectError(ValueError):
    """A shape, ownership, or arithmetic contract was not met."""


class ExactDivisionError(DirectError):
    """An alleged exact real halving had an odd numerator."""


def _require(condition, message):
    if not condition:
        raise DirectError(message)


def _integer(value):
    return type(value) is int


def _rank(length):
    _require(_integer(length) and length > 0, "positive bank length required")
    _require(length & (length - 1) == 0, "bank length must be a power of two")
    rank = length.bit_length() - 1
    _require(rank <= 9, "finite reference contract is rank 0 through 9")
    return rank


def _gaussian_bank(bank, length, label):
    _require(type(bank) is list, label + " must be a list")
    _require(len(bank) == length, label + " has the wrong length")
    result = []
    for value in bank:
        _require(
            type(value) in (tuple, list) and len(value) == 2,
            label + " must contain Gaussian pairs",
        )
        _require(
            all(_integer(component) for component in value),
            label + " components must be integers, excluding bool",
        )
        result.append((value[0], value[1]))
    return result


def _digest(value):
    encoded = json.dumps(value, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def _magnitude(bank):
    return max((abs(component) for value in bank for component in value), default=0)


def _pi_power(exponent):
    real, imag = 1, 0
    for _ in range(exponent):
        real, imag = real - imag, real + imag
    return real, imag


def encode_gain(rank):
    """Exact maximum real absolute row sum of E_r."""
    _require(_integer(rank) and 0 <= rank <= 9, "rank must be an integer in [0, 9]")
    return sum(
        comb(rank, degree) * sum(abs(x) for x in _pi_power(degree))
        for degree in range(rank + 1)
    )


def logical_cost(rank, mode):
    """Arithmetic and logical-storage invoice; no physical routing tariff."""
    _require(_integer(rank) and 0 <= rank <= 9, "rank must be an integer in [0, 9]")
    _require(mode in ("zero", "inplace"), "mode must be zero or inplace")
    length = 1 << rank
    pairs = rank * length // 2
    field_operations = 11 if mode == "zero" else 9
    add_sub = 14 * pairs + 2 * length * field_operations
    return {
        "rank": rank,
        "gaussian_entries_per_bank": length,
        "newton_pairs_per_direction": pairs,
        "full_gaussian_bank_add_sub": field_operations,
        "real_add_sub_excluding_doubling": add_sub,
        "real_doublings": pairs,
        "exact_real_halves": 2 * pairs,
        "real_add_sub_if_doubling_is_one_add": add_sub + pairs,
        "gaussian_banks_owned_beyond_inputs": 1 if mode == "zero" else 0,
        "real_zero_scratch_registers": 1,
        "owned_zero_gaussian_bank_initialisations": 1 if mode == "zero" else 0,
        "owned_zero_gaussian_bank_erasures": 1 if mode == "zero" else 0,
        "arithmetic_scratch_initialisations": 1,
        "arithmetic_scratch_zero_checks": 2 * pairs,
        "arithmetic_scratch_final_disposals": 1,
    }


class _StrictMachine:
    """Flat real registers with the permitted reversible arithmetic only."""

    def __init__(self, banks, query_bank, work_bank):
        self.length = len(banks[0])
        self.stride = 2 * self.length
        self.values = [component for bank in banks for pair in bank for component in pair]
        self.tau = len(self.values)
        self.values.append(0)
        self.query_bank = query_bank
        self.work_bank = work_bank
        self.counts = {"add": 0, "subtract": 0, "doubling": 0, "exact_half": 0}
        self.clean_pi_exits = 0
        self.trace = hashlib.sha256()
        self.peak_all = max(abs(x) for x in self.values)
        self.peak_nonquery = max(
            abs(x)
            for index, x in enumerate(self.values)
            if index // self.stride != query_bank
        )
        self.peak_query = _magnitude(banks[query_bank])
        self.peak_work = _magnitude(banks[work_bank])
        self.peak_tau = 0

    def _record(self, operation, target, source=None):
        record = operation + ":" + str(target)
        if source is not None:
            record += ":" + str(source)
        self.trace.update((record + "\n").encode("ascii"))
        magnitude = abs(self.values[target])
        self.peak_all = max(self.peak_all, magnitude)
        bank = target // self.stride
        if bank == self.query_bank:
            self.peak_query = max(self.peak_query, magnitude)
        else:
            self.peak_nonquery = max(self.peak_nonquery, magnitude)
        if bank == self.work_bank:
            self.peak_work = max(self.peak_work, magnitude)
        if target == self.tau:
            self.peak_tau = max(self.peak_tau, magnitude)

    def add(self, target, source, sign=1):
        _require(target != source, "aliased ADD requires the explicit doubling primitive")
        _require(type(sign) is int and sign in (-1, 1), "ADD sign must be +1 or -1")
        self.values[target] += sign * self.values[source]
        operation = "add" if sign == 1 else "subtract"
        self.counts[operation] += 1
        self._record(operation, target, source)

    def double(self, target):
        self.values[target] += self.values[target]
        self.counts["doubling"] += 1
        self._record("doubling", target)

    def half(self, target):
        if self.values[target] % 2:
            raise ExactDivisionError("exact halving rejected an odd signed numerator")
        self.values[target] //= 2
        self.counts["exact_half"] += 1
        self._record("exact_half", target)

    def multiply_pi(self, real, imag):
        _require(self.values[self.tau] == 0, "pi multiplication requires zero scratch")
        self.add(self.tau, real)
        self.add(real, imag, -1)
        self.add(imag, self.tau)
        self.double(self.tau)
        self.add(self.tau, real, -1)
        self.add(self.tau, imag, -1)
        _require(self.values[self.tau] == 0, "pi multiplication left dirty scratch")
        self.clean_pi_exits += 1

    def divide_pi(self, real, imag):
        _require(self.values[self.tau] == 0, "pi division requires zero scratch")
        self.add(self.tau, real)
        self.add(self.tau, imag)
        self.half(self.tau)
        self.add(imag, real, -1)
        self.half(imag)
        self.add(real, imag)
        self.add(self.tau, real, -1)
        _require(self.values[self.tau] == 0, "pi division left dirty scratch")
        self.clean_pi_exits += 1

    def field_add(self, target_bank, source_bank, sign=1):
        _require(target_bank != source_bank, "full-bank ADD operands must be distinct")
        target_start = target_bank * self.stride
        source_start = source_bank * self.stride
        for offset in range(self.stride):
            self.add(target_start + offset, source_start + offset, sign)

    def newton(self, bank, inverse=False):
        rank = _rank(self.length)
        bits = range(rank - 1, -1, -1) if inverse else range(rank)
        start = bank * self.stride
        for bit in bits:
            mask = 1 << bit
            for low in range(self.length):
                if low & mask:
                    continue
                high = low | mask
                low_real = start + 2 * low
                high_real = start + 2 * high
                if inverse:
                    self.add(high_real, low_real, -1)
                    self.add(high_real + 1, low_real + 1, -1)
                    self.divide_pi(high_real, high_real + 1)
                else:
                    self.multiply_pi(high_real, high_real + 1)
                    self.add(high_real, low_real)
                    self.add(high_real + 1, low_real + 1)

    def bank(self, bank):
        start = bank * self.stride
        return [
            (self.values[start + 2 * index], self.values[start + 2 * index + 1])
            for index in range(self.length)
        ]


def run_direct(coefficients, query, terminal_slots, mode):
    """Compute the stated map, returning arrays plus a deterministic receipt.

    Bank-list identities represent logical ownership boundaries.  Equal-valued
    distinct banks are legal; repeated bank objects, query aliasing, repeated
    terminal slots, and Boolean integer fields are rejected.  The inputs are
    copied by this reference implementation.  In logical inplace mode the
    first supplied terminal bank is mutable work and is restored exactly.

    The query need not be in B_r for this arithmetic model to run.  Admission
    of the initial query to B_r, when that is the surrounding caller contract,
    is a separate obligation; adding E_r of a Gaussian vector preserves it.
    """
    _require(type(coefficients) is list and len(coefficients) == 52, "52 coefficient banks required")
    _require(type(query) is list, "query must be a list")
    length = len(query)
    rank = _rank(length)
    _require(len({id(bank) for bank in coefficients}) == 52, "coefficient banks must be distinct")
    _require(all(query is not bank for bank in coefficients), "query must be distinct from coefficients")
    _require(type(terminal_slots) in (tuple, list) and len(terminal_slots) == 5, "five terminal slots required")
    _require(
        all(_integer(slot) and 0 <= slot < 52 for slot in terminal_slots),
        "terminal slots must be integer indices in [0, 51]",
    )
    _require(len(set(terminal_slots)) == 5, "terminal slots must be distinct")
    _require(type(mode) is str and mode in ("zero", "inplace"), "mode must be zero or inplace")
    originals = [_gaussian_bank(bank, length, "coefficient bank") for bank in coefficients]
    initial_query = _gaussian_bank(query, length, "query")
    banks = [list(bank) for bank in originals] + [list(initial_query)]
    query_bank = 52
    if mode == "zero":
        banks.append([(0, 0) for _ in range(length)])
        work_bank = 53
        gather_slots = list(terminal_slots)
    else:
        work_bank = terminal_slots[0]
        gather_slots = list(terminal_slots[1:])
    machine = _StrictMachine(banks, query_bank, work_bank)
    for slot in gather_slots:
        machine.field_add(work_bank, slot)
    machine.newton(work_bank)
    machine.field_add(query_bank, work_bank)
    machine.newton(work_bank, inverse=True)
    for slot in reversed(gather_slots):
        machine.field_add(work_bank, slot, -1)
    result_coefficients = [machine.bank(index) for index in range(52)]
    result_query = machine.bank(query_bank)
    _require(result_coefficients == originals, "coefficient restoration failed")
    _require(machine.values[machine.tau] == 0, "final real scratch is dirty")
    zero_erased = mode == "zero" and all(pair == (0, 0) for pair in machine.bank(work_bank))
    _require(mode != "zero" or zero_erased, "owned Gaussian scratch was not zero at erase")
    invoice = logical_cost(rank, mode)
    observed = machine.counts
    _require(
        observed["add"] + observed["subtract"] == invoice["real_add_sub_excluding_doubling"],
        "observed ADD/SUB count differs from schedule",
    )
    _require(observed["doubling"] == invoice["real_doublings"], "doubling count differs")
    _require(observed["exact_half"] == invoice["exact_real_halves"], "half count differs")
    _require(machine.clean_pi_exits == invoice["arithmetic_scratch_zero_checks"], "scratch check count differs")
    coefficient_bound = max(_magnitude(bank) for bank in originals)
    query_bound = _magnitude(initial_query)
    gain = encode_gain(rank)
    arithmetic_bound = 20 * gain * coefficient_bound
    stored_bound = 5 * gain * coefficient_bound
    final_query_bound = query_bound + stored_bound
    _require(machine.peak_nonquery <= arithmetic_bound, "non-query arithmetic exceeded proved width")
    _require(machine.peak_query <= final_query_bound, "query exceeded proved width")
    receipt = {
        "status": "PASS",
        "mode": mode,
        "rank": rank,
        "terminal_slots": list(terminal_slots),
        "logical_work_bank": "owned_zero" if mode == "zero" else terminal_slots[0],
        "all_52_coefficient_banks_restored": True,
        "query_initial_B_admission_checked_here": False,
        "real_scratch_final": machine.values[machine.tau],
        "owned_gaussian_scratch_zero_erased": zero_erased if mode == "zero" else None,
        "invoice": invoice,
        "observed_primitives": dict(observed),
        "completed_pi_operations_with_zero_scratch": machine.clean_pi_exits,
        "instruction_sha256": machine.trace.hexdigest(),
        "initial_coefficients_sha256": _digest(originals),
        "final_coefficients_sha256": _digest(result_coefficients),
        "initial_query_sha256": _digest(initial_query),
        "final_query_sha256": _digest(result_query),
        "width": {
            "initial_coefficient_component_bound_H": coefficient_bound,
            "initial_query_component_bound_J": query_bound,
            "newton_real_row_sum_gain": gain,
            "proved_stored_encoded_sum_bound": stored_bound,
            "proved_nonquery_arithmetic_bound": arithmetic_bound,
            "proved_query_bound": final_query_bound,
            "observed_all_registers": machine.peak_all,
            "observed_nonquery_registers": machine.peak_nonquery,
            "observed_work_bank": machine.peak_work,
            "observed_query": machine.peak_query,
            "observed_real_scratch": machine.peak_tau,
            "observed_signed_storage_bits": machine.peak_all.bit_length() + 1,
        },
    }
    return {"coefficients": result_coefficients, "query": result_query, "receipt": receipt}


def _closed_form_encode(values):
    """Small independent subset formula used only by the local controls."""
    rank = _rank(len(values))
    output = []
    for address in range(1 << rank):
        real, imag = 0, 0
        subset = address
        while True:
            power_real, power_imag = _pi_power(subset.bit_count())
            source_real, source_imag = values[subset]
            real += power_real * source_real - power_imag * source_imag
            imag += power_real * source_imag + power_imag * source_real
            if subset == 0:
                break
            subset = (subset - 1) & address
        output.append((real, imag))
    return output


def _expect_reject(callback, error=DirectError):
    try:
        callback()
    except error as exception:
        return {"status": "REJECT", "reason": str(exception)}
    raise DirectError("negative control was unexpectedly accepted")


def verify_controls():
    """Bounded signed, low-rank, arithmetic, and ownership controls.

    This is a reference-model gate.  It does not repeat the native source
    replay, authenticate terminal slots, or supply physical ownership proof.
    """
    slots = [2, 9, 16, 27, 51]
    cases = []
    for rank in (0, 1, 2, 9):
        length = 1 << rank
        coefficients = [
            [
                (
                    ((37 * bank + 17 * index + 3 * index.bit_count()) % 11) - 5,
                    ((19 * bank + 29 * index + 5 * index.bit_count()) % 13) - 6,
                )
                for index in range(length)
            ]
            for bank in range(52)
        ]
        query = [((7 * index % 17) - 8, (11 * index % 19) - 9) for index in range(length)]
        terminal_sum = [
            tuple(sum(coefficients[slot][index][part] for slot in slots) for part in (0, 1))
            for index in range(length)
        ]
        increment = _closed_form_encode(terminal_sum)
        expected = [(q[0] + y[0], q[1] + y[1]) for q, y in zip(query, increment)]
        receipts = []
        for mode in ("zero", "inplace"):
            result = run_direct(coefficients, query, slots, mode)
            _require(result["query"] == expected, "subset-formula endpoint control failed")
            _require(result["coefficients"] == coefficients, "dirty coefficient restoration control failed")
            receipts.append(result["receipt"])
        cases.append({"rank": rank, "subset_formula_endpoint_sha256": _digest(expected), "modes": receipts})
    pi_roundtrips = 0
    signed_exact_divisions = 0
    for real in range(-4, 5):
        for imag in range(-4, 5):
            machine = _StrictMachine([[(real, imag)], [(0, 0)]], 1, 0)
            machine.multiply_pi(0, 1)
            _require(machine.bank(0) == [(real - imag, real + imag)], "pi control failed")
            machine.divide_pi(0, 1)
            _require(machine.bank(0) == [(real, imag)], "inverse pi control failed")
            _require(machine.values[machine.tau] == 0, "roundtrip scratch control failed")
            pi_roundtrips += 1
            signed_exact_divisions += 2
    odd_machine = _StrictMachine([[(-1, 0)], [(0, 0)]], 1, 0)
    dirty_machine = _StrictMachine([[(1, -2)], [(0, 0)]], 1, 0)
    dirty_machine.values[dirty_machine.tau] = 1
    zero_coefficients = [[(0, 0)] for _ in range(52)]
    zero_query = [(0, 0)]
    aliased_coefficients = list(zero_coefficients)
    aliased_coefficients[1] = aliased_coefficients[0]
    boolean_coefficients = [[(0, 0)] for _ in range(52)]
    boolean_coefficients[0] = [(False, 0)]
    rejections = {
        "negative_odd_pi_division": _expect_reject(lambda: odd_machine.divide_pi(0, 1), ExactDivisionError),
        "dirty_real_scratch": _expect_reject(lambda: dirty_machine.multiply_pi(0, 1)),
        "aliased_coefficient_bank": _expect_reject(lambda: run_direct(aliased_coefficients, zero_query, slots, "zero")),
        "aliased_query": _expect_reject(lambda: run_direct(zero_coefficients, zero_coefficients[0], slots, "inplace")),
        "repeated_terminal_slot": _expect_reject(lambda: run_direct(zero_coefficients, zero_query, [2, 9, 16, 27, 27], "zero")),
        "boolean_terminal_slot": _expect_reject(lambda: run_direct(zero_coefficients, zero_query, [False, 9, 16, 27, 51], "zero")),
        "boolean_component": _expect_reject(lambda: run_direct(boolean_coefficients, zero_query, slots, "zero")),
    }
    equal_values = [
        run_direct(zero_coefficients, zero_query, slots, mode)["receipt"]
        for mode in ("zero", "inplace")
    ]
    return {
        "status": "PASS",
        "signed_rank_cases": cases,
        "small_signed_pi_roundtrips": pi_roundtrips,
        "small_signed_exact_halves": signed_exact_divisions,
        "rejected_controls": rejections,
        "equal_valued_distinct_banks": equal_values,
    }
