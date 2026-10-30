"""Bind Charles Bethin's merged gate-table zero_state to the clifford_exact.py copy that PR6030's replay loads.

Prepared by Josie Elliston with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.

The evaluator itself is research/clifford-state-performance/fast_state.py (Charles Bethin, with OpenAI
Codex assistance; lineage of PR662), unchanged and loaded from its repository path after a SHA256 check.
It was written for, and tested against, the same clifford_exact.py bytes (PIN below), which that package
pins at research/complex-multicold/.../clifford/clifford_exact.py.  PR6030's chain loads another
byte-identical copy (research/p104-native-channel/vendor/clifford_exact.py, extracted from PR5827's
archive chain).  Nothing here changes what is checked: `run.install` executes a clifford_exact.py module
from its hashed bytes only when they hash to PIN, then swaps the method; `differential` runs both versions
on every call that reaches the method.
"""
from hashlib import sha256
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
PIN = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'          # clifford_exact.py
EVALUATOR = ROOT / 'research/clifford-state-performance/fast_state.py'
EVALUATOR_PIN = '2fe087ba4558bd21ca49945dbedaa4047e4170e8fd4e2280701bb2f0481811b5'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def source_digest(raw):
    return sha256(raw).hexdigest()


def evaluator():
    """Load the pinned fast_state.py from the exact bytes that were hashed."""
    raw = EVALUATOR.read_bytes()
    need(source_digest(raw) == EVALUATOR_PIN, 'Pinned fast_state.py bytes')
    spec = importlib.util.spec_from_loader('p104_6030_fast_state', loader=None, origin=str(EVALUATOR))
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(EVALUATOR)
    exec(compile(raw, str(EVALUATOR), 'exec'), module.__dict__)
    return module


def counted(fast, counter):
    def zero_state(self, basis=0):
        counter['fast_calls'] += 1
        return fast(self, basis)
    return zero_state


def differential(original, fast, counter):
    """Run both implementations on every call; return the original's value after requiring equality."""
    def zero_state(self, basis=0):
        expected = original(self, basis)
        actual = fast(self, basis)
        if actual != expected or type(actual[0]) is not list or any(type(t) is not tuple for t in actual[0]):
            raise ValueError('zero_state differential mismatch')
        counter['differential_calls'] += 1
        return expected
    return zero_state
