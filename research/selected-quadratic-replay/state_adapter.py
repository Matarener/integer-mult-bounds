"""Return the retained dense and sparse state formats from exact quadratic data.

The engine and its stabilizer proof are from Ali Romman's PR5704.
This selected-caller adapter is by Ali Romman with OpenAI Codex assistance.
Apache-2.0. The bounded process cache uses every exact state input as its key.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
ENGINE = runpy.run_path(str(ROOT / 'research/exact-clifford-quadratic-replay/quadratic.py'))
COUNTS = Counter()
TRACE = None


def frozen(value):
    """Copy supported values into an immutable key; reject numeric aliases."""
    if type(value) in (int, str):
        return value
    if type(value) in (tuple, list):
        return tuple(frozen(item) for item in value)
    raise ValueError('State input must contain only exact integers, strings and sequences')


@lru_cache(maxsize=8192)
def signature(n, circuit, initial):
    return ENGINE['signature'](n, circuit, initial)


def support(n, circuit, initial):
    key = frozen(n), frozen(circuit), frozen(initial)
    state = signature(*key)
    if TRACE is not None:
        TRACE.add(key)
    _, offset, columns, terms, real, imag, denominator = state
    polynomial = dict(terms)
    values = {}
    for mask in range(1 << len(columns)):
        address = offset
        for j in ENGINE['bits'](mask):
            address ^= columns[j]
        values[address] = ENGINE['multiply_i']((real, imag), ENGINE['value'](polynomial, mask))
    COUNTS['evaluations'] += 1
    COUNTS['amplitude_entries'] += 1 << n
    return values, denominator


def dense_state(n, circuit, initial=0):
    values, denominator = support(n, circuit, initial)
    result = [(0, 0)] * (1 << n)
    for address, pair in values.items():
        result[address] = pair
    COUNTS['dense'] += 1
    return result, denominator


def sparse_state(circuit, initial=0):
    result = support(9, circuit, initial)
    COUNTS['sparse'] += 1
    return result
