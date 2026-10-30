"""Two-pass x -> A*x+c modulo odd Q, A in {2,4}, and its inverse.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
Runtime cardinalities stay on encoded tapes. Only bounded residues enter control.
"""
import fused_sources
fused_sources.activate()
from bitstream import copy_bits
from cardinal_counts import Count, positive
from routes import copy_rows
from stream import Counter
from words import BLANK, need


def bounded_residue(modulus, amount):
    """Return abs(amount) mod Q in a five-state finite controller."""
    residue = 0
    count = Counter(modulus)
    try:
        for _ in range(abs(amount)):
            count.decrement()
            residue += 1
            if count.finished:
                count.close()
                count = Counter(modulus)
                residue = 0
        return residue
    finally:
        count.close()


def shortened(value, amount):
    count = Counter(value)
    try:
        for _ in range(amount):
            count.decrement()
        return Count(count.tape)
    finally:
        count.close()


def transformed(source, ring, before, suffix, multiplier, amount, factory, inverse=False):
    """Borrow the entire B*Q*S cube; return a distinct, owned affine image."""
    need(type(multiplier) is int and multiplier in (2, 4), 'fixed dyadic multiplier')
    need(type(amount) is int and abs(amount) <= 4, 'fixed bounded affine offset')
    need(type(inverse) is bool, 'literal affine direction')
    positive(before)
    positive(suffix)
    quotient = modulus = main = output = None
    counts, rest, small = [], [], []
    try:
        modulus = Count(ring.modulus)
        quotient = Count(modulus)
        residue_q = quotient.divide_small(multiplier)
        need(residue_q & 1 == 1, 'odd high modulus')
        r = bounded_residue(modulus, amount)
        first_small = (residue_q-r) % multiplier if amount >= 0 else 0
        sizes = [sum((first_small+t) % multiplier == j for t in range(r))
                 for j in range(multiplier)]
        for j in range(multiplier):
            total = Count(quotient)
            try:
                if j < residue_q:
                    total.increment()
                counts.append(shortened(total, sizes[j]))
            finally:
                total.close()
        quotient.close()
        quotient = None
        main = shortened(modulus, r)
        modulus.close()
        modulus = None
        for _ in range(multiplier):
            rest.append(factory())
        for _ in range(multiplier):
            small.append(factory())
        output = factory()

        def block(source_word, target_word):
            copy_bits(source_word, target_word, suffix)

        def ordered_parts(scattering):
            for k in range(multiplier):
                j = (-k*residue_q) % multiplier
                source_rest, target_rest = (source, rest[j]) if scattering else (rest[j], output)
                source_small, target_small = (source, small[j]) if scattering else (small[j], output)
                if amount < 0:
                    for _ in range(sizes[j]):
                        block(source_small, target_small)
                copy_rows(source_rest, target_rest, counts[j], suffix)
                if amount >= 0:
                    for _ in range(sizes[j]):
                        block(source_small, target_small)

        def rotated_parts(scattering):
            def short_part():
                for t in range(r):
                    j = (first_small+t) % multiplier
                    block(source if scattering else small[j], small[j] if scattering else output)

            def long_part():
                counter = Counter(main)
                j = r % multiplier if amount < 0 else 0
                try:
                    while not counter.finished:
                        block(source if scattering else rest[j], rest[j] if scattering else output)
                        j = (j+1) % multiplier
                        counter.decrement()
                finally:
                    counter.close()
            if amount >= 0:
                short_part()
                long_part()
            else:
                long_part()
                short_part()

        for second in (False, True):
            outer = Counter(before)
            try:
                while not outer.finished:
                    if second == inverse:
                        ordered_parts(not second)
                    else:
                        rotated_parts(not second)
                    outer.decrement()
            finally:
                outer.close()
            if not second:
                need(source.read() == BLANK, 'complete affine source')
                source.rewind()
                for word in (*rest, *small):
                    word.rewind()
        need(all(word.read() == BLANK for word in (*rest, *small)), 'complete affine buckets')
        output.rewind()
        result, output = output, None
        return result
    finally:
        source.rewind()
        for word in (*rest, *small, output):
            if word is not None:
                word.clear()
        for count in (*counts, quotient, modulus, main):
            if count is not None:
                count.close()
