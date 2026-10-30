#!/usr/bin/env python3
"""Read-only verification; --write-result creates a new receipt exclusively.

Prepared by @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor scientific implementation is imported.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
M = runpy.run_path(str(HERE / "model.py"))
need = M["require"]


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.is_file() and not path.is_symlink(), "regular pinned input")
            data = path.read_bytes()
            need(len(data) <= 32768, "bounded source contract")
            digest = hashlib.sha256(data).hexdigest()
            need(digest == row["sha256"], "source pin: " + row["path"])
            checked[row["path"]] = digest
    need(len(checked) == 2, "two predecessor contracts")
    return checked


def literal_trace(word, initial):
    """Independent bit execution with literal, fixed child bodies."""
    registers = list(initial)
    trace = []
    for cut in range(5):
        if cut == 1:
            registers[0] = (registers[0] + registers[3]) % 2
            registers[2] = (registers[2] + registers[3]) % 2
        elif cut in (2, 3):
            registers[0] = (registers[0] + registers[2]) % 2
            registers[2] = (registers[2] + registers[3]) % 2
        elif cut == 4:
            registers[1] = (registers[1] + registers[2]) % 2
            registers[3] = (registers[3] + registers[2]) % 2
        for destination, source in word[cut]:
            registers[destination] = (registers[destination] + registers[source]) % 2
        if cut:
            trace.append(tuple(registers))
    return tuple(trace)


def literal_accepts(trace, initial, full):
    x, y, a, b = initial
    wanted = ((x ^ b, y), (x ^ a ^ b, y), (x ^ b, y), (x ^ b, y ^ a))
    good = trace[-1] == (*wanted[-1], a, b)
    for cut in range(4):
        good &= trace[cut][1] == wanted[cut][1]
        if full or cut != 1:
            good &= trace[cut][0] == wanted[cut][0]
    return good


def enumerate_shorter():
    counts, partial_hits, full_hits = [], [], []
    executions = 0
    for count in range(3):
        seen = partial = full = 0
        for word in M["schedules"](count):
            rows = M["coefficient_trace"](word)
            p = M["accepts"](rows, M["PARTIAL_MASKS"])
            f = M["accepts"](rows, M["FULL_MASKS"])
            lp = lf = True
            for initial in itertools.product((0, 1), repeat=4):
                bits = literal_trace(word, initial)
                packed = sum(v << i for i, v in enumerate(initial))
                expected = tuple(tuple((row & packed).bit_count() % 2 for row in state)
                                 for state in rows)
                need(bits == expected, "coefficient/literal trace disagreement")
                lp &= literal_accepts(bits, initial, False)
                lf &= literal_accepts(bits, initial, True)
                executions += 1
            need((p, f) == (lp, lf), "independent observation disagreement")
            partial += p
            full += f
            seen += 1
        counts.append(seen)
        partial_hits.append(partial)
        full_hits.append(full)
    need(counts == [1, 30, 540], "complete shorter-word domain")
    need(partial_hits[:2] == [0, 0] and partial_hits[2] > 0, "partial minimum two")
    need(full_hits == [0, 0, 0], "full minimum at least three")
    return dict(schedules_by_cost=counts, partial_hits=partial_hits,
                full_hits=full_hits, literal_executions=executions,
                literal_contract_checks=2 * executions)


def positive_words():
    need(M["reference"]()[-1] == M["FINAL"], "independent final updates")
    need(M["update_rank"]() == 2, "rank-two endpoint")
    traces = {}
    for name, key, masks, full in (
            ("partial", "PARTIAL_WORD", "PARTIAL_MASKS", False),
            ("full", "FULL_WORD", "FULL_MASKS", True),
            ("eager", "EAGER_WORD", "FULL_MASKS", True)):
        word = M[key]
        rows = M["coefficient_trace"](word)
        need(M["accepts"](rows, M[masks]), "positive coefficient word")
        for initial in itertools.product((0, 1), repeat=4):
            need(literal_accepts(literal_trace(word, initial), initial, full),
                 "positive arbitrary dirty input")
        traces[name] = dict(word=word, trace=rows, adapters=sum(map(len, word)))
    return traces


def rejects(call, phrase):
    try:
        call()
    except ValueError as error:
        need(phrase in str(error), "rejection reason")
        return
    raise ValueError("invalid domain accepted")


def controls():
    p = M["PARTIAL_WORD"]
    trace = M["coefficient_trace"](p)
    need(not M["accepts"](trace, M["FULL_MASKS"]), "newly visible output")
    need(trace[1][0] ^ M["reference"]()[1][0] == 8, "hidden defect is incoming b")
    missing_u = ((), (), (), p[3], ())
    missing_l = ((), (), p[2], (), ())
    moved_u = ((), (), (), p[2] + p[3], ())
    for word in (missing_u, missing_l, moved_u):
        need(not M["accepts"](M["coefficient_trace"](word), M["PARTIAL_MASKS"]),
             "omitted or delayed adapter")
    bad_return = M["coefficient_trace"](missing_l)[-1]
    need(bad_return[:2] == M["FINAL"][:2] and bad_return[2:] != (4, 8),
         "retained outputs alone miss failed dirty return")
    for initial, expected in (((0, 0, 0, 0), True), ((0, 0, 0, 1), False)):
        need(literal_accepts(literal_trace(p, initial), initial, True) == expected,
             "clean-only false positive and dirty counterexample")
    rank_one = (*M["CHILDREN"][:-1], (1, 1, 1))
    need(M["update_rank"](rank_one) == 1, "duplicate nonzero updates are not independent")
    rejects(lambda: M["coefficient_trace"]((((2, 0),), (), (), (), ())), "alphabet")
    rejects(lambda: M["coefficient_trace"](p[:-1]), "gaps")
    rejects(lambda: M["accepts"](trace, (3, 0, 3, 3)), "masks")
    return 12


def discovery():
    """Replay the declared first-witness search, not a four-call census."""
    chains = list(itertools.product(tuple(itertools.product((0, 1), repeat=3)), repeat=4))
    random.Random(57).shuffle(chains)
    tested = inspected = 0
    for chain in chains:
        inspected += 1
        if M["update_rank"](chain) != 2:
            continue
        tested += 1
        full_min = 3
        candidates = []
        for count in range(3):
            for word in M["schedules"](count):
                rows = M["coefficient_trace"](word, chain)
                ref = M["reference"](chain)
                if rows[-1] != ref[-1]:
                    continue
                errors = tuple(sum((rows[i][o] != ref[i][o]) << o for o in (0, 1))
                               for i in range(3))
                if not any(errors):
                    full_min = min(full_min, count)
                elif sum(e.bit_count() for e in errors) == 1:
                    candidates.append((count, word, errors))
        for count, word, errors in candidates:
            if count < full_min:
                need(chain == M["CHILDREN"] and word == M["PARTIAL_WORD"],
                     "first seed-57 witness changed")
                return dict(seed=57, chain_domain=4096, inspected_chains=inspected,
                            completed_rank_two_chains=tested, shorter_schedules_per_chain=571,
                            stopping_rule="first strict one-hidden-cut witness through two adapters",
                            hidden_error_masks=errors)
    raise ValueError("the declared first witness was not found")


def invoices():
    bills = {}
    for name, key in (("partial", "PARTIAL_WORD"), ("full", "FULL_WORD")):
        gates = Counter(g for gap in M[key] for g in gap)
        for output, source, target in M["CHILDREN"]:
            gates[(output, 2 + source)] += 1
            gates[(2 + target, 3 - target)] += 1
        bills[name] = gates
    need(bills["full"] == bills["partial"] + Counter({(0, 3): 1}),
         "complete histograms differ by one output correction")
    need(sum(bills["partial"].values()) == 10 and sum(bills["full"].values()) == 11,
         "all child and adapter gates charged")
    return {name: {f"{d}<-{s}": count for (d, s), count in sorted(gates.items())}
            for name, gates in bills.items()}


def result():
    pins = authenticate()
    return dict(schema="rank-two-observation-boundary/1", no_new_kappa=True,
                claim_type="scoped written proof with exact finite corroboration",
                children=M["CHILDREN"], partial_masks=M["PARTIAL_MASKS"],
                final_rows=M["FINAL"], update_rank=2, words=positive_words(),
                enumeration=enumerate_shorter(), semantic_controls=controls(),
                discovery=discovery(), complete_gate_histograms=invoices(),
                complete_xor_bills=dict(partial=10, full=11, eager=12),
                source_sha256=pins, implementation_sha256={
                    name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                    for name in ("model.py", "verify.py")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    data = json.dumps(result(), sort_keys=True, indent=2) + "\n"
    if args.write_result is not None:
        with args.write_result.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(data)
    else:
        need((HERE / "RESULT.json").read_text(encoding="utf-8") == data,
             "committed RESULT differs from recomputed mathematics")
    print("PASS_RANK_TWO_OBSERVATION_BOUNDARY rank=2 partial=2 full=3 xor=10/11 no_new_kappa")


if __name__ == "__main__":
    main()
