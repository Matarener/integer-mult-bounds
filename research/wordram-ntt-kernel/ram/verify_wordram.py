"""Portable adversarial replay and source-independent arithmetic oracles."""
import hashlib
import json
from pathlib import Path
import random
from wordram_kernel import (
    Builder, MODULUS as P, MASK, SCRATCH, butterfly_program, multiply_program, run,
)


def check_frame(result, initial, outputs):
    assert result is not None and result.accepted
    assert result.writes <= SCRATCH | set(outputs)
    for cell, value in initial.items():
        if cell not in SCRATCH | set(outputs):
            assert result.memory.get(cell, 0) == (value & MASK)
    assert all(result.memory.get(cell, 0) == 0 for cell in SCRATCH)


def run_checks():
    rng = random.Random(20261024)
    mul = multiply_program()
    fused, duplicate = butterfly_program(), butterfly_program(fused=False)
    assert (len(mul), len(fused), len(duplicate)) == (104, 113, 162)
    maximum_mul = maximum_fused = maximum_duplicate = 0
    # This complete finite sweep crosses every attainable product quotient:
    # floor(65536*b/65537)=b-1 for 1<=b<=65536.
    for b in range(P):
        initial = {0: P - 1, 1: b, -97: MASK - b, 1000007: b + 31}
        result = run(mul, initial)
        check_frame(result, initial, {3})
        assert result.memory[3] == ((P - 1) * b) % P
        assert result.steps == 88 + (((P - 1) * b) // P).bit_count()
        maximum_mul = max(maximum_mul, result.steps)
    edge = [0, 1, 2, 255, 256, 32767, 32768, P - 3, P - 2, P - 1]
    triples = [(u, b, w) for u in edge for b in edge for w in edge]
    triples += [(rng.randrange(P), rng.randrange(P), rng.randrange(P)) for _ in range(4096)]
    for u, b, w in triples:
        initial = {0: u, 1: b, 2: w, -97: rng.getrandbits(64), 1000007: rng.getrandbits(64)}
        initial.update({a: rng.getrandbits(64) for a in SCRATCH | {3, 4}})
        f, d = run(fused, initial), run(duplicate, initial)
        check_frame(f, initial, {3, 4}); check_frame(d, initial, {3, 4})
        v = b * w % P
        expected = ((u + v) % P, (u - v) % P)
        assert (f.memory[3], f.memory[4]) == expected
        assert (d.memory[3], d.memory[4]) == expected
        bits = ((b * w) // P).bit_count()
        corrections = int(u + v >= P) + int(u >= v)
        assert f.steps == 95 + bits + corrections
        assert d.steps == 128 + 2 * bits + corrections
        assert d.steps - f.steps == 33 + bits
        maximum_fused = max(maximum_fused, f.steps)
        maximum_duplicate = max(maximum_duplicate, d.steps)
        # One fewer than the exact halt count must not return a verdict.
        assert run(fused, initial, budget=f.steps - 1) is None
    # Exercise the otherwise unused indirect/signed-address interpreter semantics.
    e = run([('load', 0, 1), ('store', 2, 0), ('accept',)], {1: -4, -4: 123, 2: -5})
    assert e.accepted and e.memory[0] == 123 and e.memory[-5] == 123 and e.steps == 3
    # Prove literal-synthesis count against its syntax, including zero and sign boundary.
    for n in [0, 1, 2, 3, 65537, (1 << 62) - 1, (1 << 63) - 1]:
        builder = Builder(); builder.setup(); start = len(builder.code)
        builder.literal(100, n)
        literal_ops = len(builder.code) - start
        assert literal_ops == (1 if n == 0 else n.bit_length() + n.bit_count() - 1)
        builder.cleanup(); builder.accept()
        e = run(builder.program(), {})
        assert e.accepted and e.memory[100] == n
    return {
        'status': 'PASS', 'word_bits': 64, 'modulus': P,
        'exhaustive_multiply_inputs': P, 'exhaustive_slice': 'a=65536, all 0<=b<=65536',
        'butterfly_input_triples': len(triples), 'random_seed': 20261024,
        'static_lengths': {'multiply': len(mul), 'fused_butterfly': len(fused), 'duplicate_butterfly': len(duplicate)},
        'observed_max_dynamic': {'multiply': maximum_mul, 'fused_butterfly': maximum_fused, 'duplicate_butterfly': maximum_duplicate},
        'scope': 'Executable replays plus informal universal invariant proof; no Lean kernel check',
        'files_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},
    }

if __name__ == '__main__':
    print(json.dumps(run_checks(), indent=2))
