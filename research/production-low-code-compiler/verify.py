# SPDX-License-Identifier: Apache-2.0
"""Complete small-field differential tests and actual selected-prime compilation."""
import argparse
from hashlib import sha256
from itertools import product, islice
import json
from pathlib import Path
import random
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import low_codes as compiled
from low_codes import LowCodes, PRIME, PowerTwoCertificate, SELECTED_CERTIFICATE, prefix_count, select_symbol
from source_binding import OLD, ANCESTRY, compile_route, low_classes, need

HERE = Path(__file__).resolve().parent


def digest(value):
    if type(value) is int:
        value = {"integer_hex": hex(value)}
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def reject(fn):
    try:
        fn()
    except (ValueError, TypeError):
        return
    raise ValueError("invalid case accepted")


def run():
    small, branch_states = [], 0
    # Complete independent determinant oracle, distinct from source counting.
    for q in (3, 5):
        expected = [((a, b), (c, d)) for a, b, c, d in product(range(q), repeat=4)
                    if (a*d-b*c) % q]
        fast, old = LowCodes(q, 2, 3), OLD.LowCodes(q, 2, 3)
        got = []
        for ordinal in range(fast.size):
            matrix = fast.unrank(ordinal)
            need(matrix == old.unrank(ordinal) and fast.rank(matrix) == old.rank(matrix) == ordinal,
                 "complete source differential")
            got.append(matrix)
            for request in (0, 2):
                for view in (False, True):
                    code = fast.encode(request, view, matrix)
                    need(code == old.encode(request, view, matrix) and fast.decode(code) == (request, view, matrix),
                         "exact complete tag and low-class code")
        # Source order is lexicographic within row-completion mixed radices.
        need(got == expected, "independent determinant/lexicographic enumeration")
        small.append({"q": q, "dimension": 2, "matrices": len(got), "sha256": digest(got)})
    # All GL3(F3) codes cover genuinely dependent and independent prefix systems.
    fast, old = LowCodes(3, 3), OLD.LowCodes(3, 3)
    whole = sha256()
    for ordinal in range(fast.size):
        matrix = fast.unrank(ordinal)
        need(matrix == old.unrank(ordinal) and fast.rank(matrix) == ordinal, "complete GL3 source differential")
        whole.update(bytes(x for row in matrix for x in row))
    small.append({"q": 3, "dimension": 3, "matrices": fast.size, "sha256": whole.hexdigest()})
    # Test closed formulas against literal sums at every reachable prefix of all
    # two-dimensional completions, including zero-length exceptional intervals.
    kinds = set()
    for q in (3, 5):
        rows_options = [()] + [(v,) for v in product(range(q), repeat=2) if any(v)]
        for rows in rows_options:
            for vector in product(range(q), repeat=2):
                c = OLD.Constraints(rows, q)
                for column, value in enumerate(vector):
                    reduced = c.next(column)
                    total = q ** (1-column)
                    counts = [total-c.excluded(reduced, x) for x in range(q)]
                    need(min(counts) >= 0, "nonnegative source completion counts")
                    for v in range(q+1):
                        need(prefix_count(c, reduced, total, v) == sum(counts[:v]), "literal prefix sum")
                    for rank in range(sum(counts)):
                        symbol, tail = select_symbol(c, reduced, total, rank)
                        need(sum(counts[:symbol]) + tail == rank and 0 <= tail < counts[symbol],
                             "literal interval inverse")
                    kind = "inconsistent" if c.inconsistent else ("pivot" if reduced[2] is not None else "exceptional")
                    kinds.add(kind)
                    branch_states += 1
                    c.choose(reduced, value)
    need(kinds == {"inconsistent", "pivot", "exceptional"}, "all structural branches")
    SELECTED_CERTIFICATE.check()
    # This is the actual field and complete dimension, not a surrogate q=2.
    codes = LowCodes(PRIME, 64, 28278)
    need(all(getattr(LowCodes, name) is getattr(OLD.LowCodes, name)
             for name in ("rank", "unrank", "encode", "decode")), "unchanged mixed-radix public methods")
    position_count = [0]
    def count(fn):
        def wrapped(*args):
            position_count[0] += 1
            return fn(*args)
        return wrapped
    compiled.prefix_count = count(prefix_count)
    compiled.select_symbol = count(select_symbol)
    rng = random.Random(19173180)
    ranks = (0, codes.size-1, rng.randrange(codes.size))
    selected = []
    for ordinal in ranks:
        before = position_count[0]
        matrix = codes.unrank(ordinal)
        need(codes.rank(matrix) == ordinal, "selected GL64 inverse")
        need(position_count[0]-before == 2*64*64, "exact direct row-position count")
        selected.append({"ordinal_sha256": digest(ordinal), "matrix_sha256": digest(matrix),
                         "old_rank_symbol_iterations": sum(map(sum, matrix)),
                         "old_unrank_symbol_iterations": sum(map(sum, matrix))+64*64,
                         "direct_rank_and_unrank_positions": position_count[0]-before})
    compiled.prefix_count, compiled.select_symbol = prefix_count, select_symbol
    # Real Catalogue iterator body; consume only its first source classes.
    iterator = low_classes(SimpleNamespace(codes=codes))
    prefix = list(islice(iterator, 2))
    need([codes.rank(m) for m in prefix] == [0, 1], "actual Catalogue low-class prefix")
    # Real compile_route body and Route type from the factory's nested archive.
    # A fixed integral shear is a legitimate chart; no runtime payload is run.
    chart = tuple(tuple(int(i == j) + int(i == 0 and j == 1) for j in range(64)) for i in range(64))
    route = compile_route(matrix, chart, codes)
    expected = tuple(tuple((row[j] + (row[0] if j == 1 else 0)) % PRIME for j in range(64)) for row in matrix)
    need(route.low == matrix and route.target_low == expected and route.q == PRIME and route.dimension == 64,
         "actual source route compiler accepts exact selected low codes")
    code = codes.encode(28277, True, route.target_low)
    need(codes.decode(code) == (28277, True, route.target_low), "actual route target request/view roundtrip")
    controls = []
    cases = {
      "wrong_prime_witness": lambda: PowerTwoCertificate(PRIME, 80, 1).check(),
      "incomplete_factor": lambda: PowerTwoCertificate(PRIME, 79, 7).check(),
      "composite_large_factor": lambda: PowerTwoCertificate(9, 3, 2).check(),
      "forged_certificate_object": lambda: LowCodes(9, 2, certificate=SimpleNamespace(check=lambda: 9)),
      "wrong_requested_prime": lambda: LowCodes(3, 2, certificate=SELECTED_CERTIFICATE),
      "large_uncertified_prime": lambda: LowCodes(263, 2),
      "negative_rank": lambda: codes.unrank(-1),
      "rank_at_size": lambda: codes.unrank(codes.size),
      "code_at_limit": lambda: codes.decode(codes.limit),
      "dependent_matrix": lambda: codes.rank(tuple((0,)*64 for _ in range(64))),
      "wrong_dimension": lambda: codes.rank(((1, 0), (0, 1))),
    }
    for name, fn in cases.items():
        reject(fn); controls.append(name)
    # Falsify the tempting omission of the exceptional interval correction.
    c = OLD.Constraints([], 3); reduced = c.next(0)
    need(prefix_count(c, reduced, 3, 1) == 2 and 1*3 != 2, "exceptional subtraction discriminator")
    controls.append("omitted_exceptional_subtraction_falsified")
    # Prime-order proof needs a large factor; Fermat alone accepts this composite.
    need(pow(2, 340, 341) == 1, "Fermat-only primality counterexample")
    controls.append("Fermat_only_false_positive")
    return {"schema_version": 1, "scope": "offline exact low-code compiler; no production payload",
            "ancestry": ANCESTRY, "small": small, "prefix_states": branch_states,
            "selected": {"q": PRIME, "dimension": 64, "requests": 28278,
                         "code_bits": codes.bits, "prime_factor": 1 << 80, "prime_witness": 7,
                         "old_constructor_trial_divisors": PRIME-2, "cases": selected,
                         "route_target_sha256": digest(route.target_low), "route_code_sha256": digest(code)},
            "controls": controls}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    target = HERE / "RESULT.json"
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        need(not target.exists(), "do not overwrite a retained result")
        target.write_text(text)
    else:
        need(target.read_text() == text, "typed deterministic result equality")
    print("PASS_PRODUCTION_LOW_CODE_COMPILER", digest(result))

if __name__ == "__main__":
    main()
