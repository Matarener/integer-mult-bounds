"""Derive exact Fraction zero/unit shortcuts from one authenticated function.

Original arithmetic: Ali Romman and retained completed-error lineage.
Derivation and checks: Chris R / Clear1nsight, substantial OpenAI Codex assistance.
Apache-2.0. No approximate arithmetic or integer-backend sharing.
"""
from contextlib import contextmanager
from fractions import Fraction
from hashlib import sha256
import inspect
from pathlib import Path
from types import CodeType

MODULE_SHA256 = 'a4c743e79c55e9c2ac26deb6d87cb948b1b0fbe942e4f7912ccbfba55db4b32a'
FUNCTION_SHA256 = '379c0e7c1c5ab7433ab5ad2669c1bda1234dbf0530fc61b21bfbe83528f37f53'
BEFORE = '''            for i, v in rows[event[2]].items():
                old = rows[r].get(i, F(0))
                value = old + q*v
                change = abs(value)-abs(old)
                scores[r][0] += change*weights[i][0]
                scores[r][1] += change*weights[i][1]
                scores[r][2] += change
'''
AFTER = '''            unit, negative_unit = q == ONE, q == NEGATIVE_ONE
            for i, v in rows[event[2]].items():
                old = rows[r].get(i, ZERO)
                value = old + (v if unit else -v if negative_unit else q*v)
                change = abs(value)-abs(old)
                if change == ONE:
                    scores[r][0] += weights[i][0]
                    scores[r][1] += weights[i][1]
                    scores[r][2] += ONE
                elif change == NEGATIVE_ONE:
                    scores[r][0] -= weights[i][0]
                    scores[r][1] -= weights[i][1]
                    scores[r][2] -= ONE
                elif change:
                    scores[r][0] += change*weights[i][0]
                    scores[r][1] += change*weights[i][1]
                    scores[r][2] += change
'''


def need(ok, message):
    if not ok:
        raise ValueError(message)


def transformed(raw):
    need(sha256(raw.encode()).hexdigest() == FUNCTION_SHA256, 'exact Fraction function source')
    need(raw.count(BEFORE) == 1, 'one exact Fraction coefficient loop')
    value = raw.replace(BEFORE, AFTER)
    # Shared Fraction objects are immutable; output dictionaries stay fresh.
    for token, replacement, count in [('F(0)', 'ZERO', 3), ('F(1)', 'ONE', 1), ('F(-1)', 'NEGATIVE_ONE', 1)]:
        need(value.count(token) == count, 'exact Fraction constant sites: '+token)
        value = value.replace(token, replacement)
    seam = "    n = word['public'] + word['owned_fields']\n"
    need(value.count(seam) == 1, 'one exact Fraction setup seam')
    return value.replace(seam, seam+'    ZERO, ONE, NEGATIVE_ONE = F(0), F(1), F(-1)\n')


def code_shape(code):
    # File/line tables differ when a bound function is compiled alone. Compare
    # executable structure recursively, including nested comprehensions.
    constants = tuple(code_shape(c) if isinstance(c, CodeType) else c for c in code.co_consts)
    return (code.co_code, constants, code.co_names, code.co_varnames,
            code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount,
            code.co_flags, code.co_freevars, code.co_cellvars, code.co_name,
            code.co_stacksize, code.co_nlocals, code.co_exceptiontable)


def derive(reference):
    need(reference.F is Fraction, 'exact standard Fraction type')
    path = Path(reference.__file__)
    need(sha256(path.read_bytes()).hexdigest() == MODULE_SHA256, 'exact Fraction module bytes')
    original = reference.error_trace
    raw = inspect.getsource(original)
    text = transformed(raw)
    namespace = dict(reference.__dict__)
    exec(compile(raw, '<fraction-source-check>', 'exec'), namespace)
    need(code_shape(original.__code__) == code_shape(namespace['error_trace'].__code__), 'live Fraction code agrees with source')
    need(original.__defaults__ is None and original.__kwdefaults__ is None and original.__closure__ is None, 'ordinary Fraction function')
    exec(compile(text, '<fraction-exact-zero-unit>', 'exec'), namespace)
    return namespace['error_trace']


@contextmanager
def installed(reference):
    original = reference.error_trace
    derived = derive(reference)
    reference.error_trace = derived
    try:
        yield derived
    finally:
        reference.error_trace = original
