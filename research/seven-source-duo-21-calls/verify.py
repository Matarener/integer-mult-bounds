"""Verify two seven-source singleton+DUO universal connector words.

Independent of the search. Rebuilds each word's steps from its prefix states,
checks closure, step weights, label parity, all 128 pairwise masks (and a
separate dual test), the all-127-row bill, Pareto dominance over the cited
#2396 word, and mutation controls. Produced by Nick Petalas. Apache-2.0.
"""
import hashlib
import json
import sys
from pathlib import Path

N = 7
MASKS = 1 << N
ROWS = MASKS - 1
READOUTS = 2 * ROWS  # two paired readouts per output row, as in #2396
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRED = ROOT / "research/connector-seven-source-duo/CERTIFICATE.json"
PRED_SHA256 = "6b8c5bd2d27a0b4cbeb073bc0ac224220fdf99bc94760afd9a1be79aa31c4a63"


class CheckError(Exception):
    pass


def require(cond, msg="check failed"):
    if not cond:
        raise CheckError(msg)


def steps_of(states):
    return [states[i] ^ states[(i + 1) % len(states)] for i in range(len(states))]


def covered(states):
    return {a ^ b for a in states for b in states}


def dual_missing(states):
    present = set(states)
    return [m for m in range(MASKS) if not any((p ^ m) in present for p in states)]


def profile(steps):
    """Return (k, d, W) after checking the word is a legal restored word."""
    require(steps, "empty word")
    acc = 0
    counts = [0] * N
    for s in steps:
        require(0 < s < MASKS, f"step {s} out of range")
        require(bin(s).count("1") in (1, 2), f"step {s} is not a singleton or DUO call")
        acc ^= s
        for j in range(N):
            counts[j] += (s >> j) & 1
    require(acc == 0, "word does not restore the connector")
    require(all(c % 2 == 0 and c > 0 for c in counts), f"label counts {counts}")
    d = sum(1 for s in steps if bin(s).count("1") == 2)
    return len(steps), d, sum(bin(s).count("1") for s in steps)


def states_of(steps):
    out, acc = [], 0
    for s in steps:
        out.append(acc)
        acc ^= s
    return out


def universal(steps):
    states = states_of(steps)
    return len(covered(states)) == MASKS and not dual_missing(states)


def check_word(name, rec):
    states = rec["prefix_states"]
    require(states[0] == 0)
    steps = steps_of(states)
    k, d, w = profile(steps)
    require(states_of(steps) == states)
    require((k, d, w) == (rec["k"], rec["duo_calls"], rec["W"]), (name, k, d, w))
    require(len(covered(states)) == MASKS, f"{name} covers {len(covered(states))}")
    require(dual_missing(states) == [], name)
    require(k + READOUTS == rec["queries_all_127_rows"])
    require(w + READOUTS == rec["adds_all_127_rows"])
    return steps, k, w


def mutations(steps):
    """Each mutation must be rejected as illegal or non-universal."""
    rejected = 0
    trials = []
    trials.append(steps[1:])  # delete a call
    duo = next(i for i, s in enumerate(steps) if bin(s).count("1") == 2)
    low = steps[duo] & -steps[duo]
    trials.append(steps[:duo] + [low] + steps[duo + 1:])  # shrink DUO
    trials.append(steps[:2] + [steps[2] ^ 64 if steps[2] ^ 64 else 1] + steps[3:])  # retarget
    trials.append(steps[:-2] + [steps[-1]])  # drop the penultimate call
    for t in trials:
        try:
            profile(t)
            ok = universal(t)
        except CheckError:
            ok = False
        rejected += not ok
    require(rejected == len(trials), f"only {rejected}/{len(trials)} mutations rejected")
    return rejected


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    pred_bytes = PRED.read_bytes()
    require(hashlib.sha256(pred_bytes).hexdigest() == PRED_SHA256, "predecessor pin")
    pred = json.loads(pred_bytes)["headline_22_24"]
    pk, pd, pw = profile(pred["steps"])
    require((pk, pw) == (22, 24) and universal(pred["steps"]), "predecessor control")
    a_steps, ak, aw = check_word("k21_W24", cert["words"]["k21_W24"])
    b_steps, bk, bw = check_word("k20_W26", cert["words"]["k20_W26"])
    # (21,24) strictly dominates (22,24): one fewer call, same adds.
    require(ak < pk and aw == pw)
    # (20,26) beats (21,24) in c = q*o + a*p exactly when o > 2p.
    require((bk - ak, bw - aw) == (-1, 2))
    muts = mutations(a_steps) + mutations(b_steps)
    print(
        "PASS_SEVEN_SOURCE_DUO_21_CALLS "
        f"k21_W24_queries={ak + READOUTS} k20_W26_queries={bk + READOUTS} "
        f"pred_queries={pk + READOUTS} universal=128/128 mutations_rejected={muts}"
    )


if __name__ == "__main__":
    try:
        main()
    except CheckError as exc:
        print(f"FAIL_SEVEN_SOURCE_DUO_21_CALLS {exc}")
        sys.exit(1)
