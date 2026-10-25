#!/usr/bin/env python3
"""Exact depth-five chain connector minima by meet-in-the-middle (#4281 open question 1).

CI part (about 30 s, numpy):
  * replays every recorded witness word in U_6(Z/m): its product is exactly I + c E[5][0] and each call is used
    the recorded number of times (multiples of m);
  * reruns the exhaustive meet-in-the-middle at length 5m for m = 2, 3, 4 (no residue; matching #4281's BFS
    minima 16, 24 and 24/28) and m = 5 (exactly residue 1);
  * checks EVIDENCE.json: every recorded run names its exact mitm.py SHA256, count vector and found residues,
    and the claimed minima follow from those runs.
The longer exhaustive runs (m = 5 at lengths 30 and 35, m = 6 at 30) are local evidence recorded in EVIDENCE.json
with their exact commands; `python3.12 -B verify.py --full` reruns them.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("mitm_core", HERE / "mitm.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
# #4281's own m = 5, c = 1 witness, as a convention control
W4281 = ("5", "1", "3452312415342513243152415")


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main(full=False):
    ev = json.loads((HERE / "EVIDENCE.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256((HERE / "mitm.py").read_bytes()).hexdigest()
    need(ev["mitm_sha256"] == digest, "evidence recorded for this exact mitm.py")
    m, c, word = int(W4281[0]), int(W4281[1]), [int(x) for x in W4281[2]]
    need(M.product(word, m) == {(5, 0): c}, "#4281 witness under this product convention")
    for w in ev["witnesses"]:
        word = [int(x) for x in w["word"]]
        need(M.product(word, w["m"]) == {(5, 0): w["c"]}, f"witness m={w['m']} c={w['c']}")
        need([word.count(l) for l in range(1, 6)] == w["counts"] and all(n % w["m"] == 0 for n in w["counts"]),
             "witness counts")
    for m in (2, 3, 4):
        need(M.residues(m, (m,) * 5) == [] and M.decide(m, (m,) * 5) == {}, f"m={m}: no length-5m connector")
    need(M.residues(5, (5,) * 5) == [1], "m=5, length 25: exactly residue 1")
    need(sorted(M.decide(5, (5,) * 5)) == [1], "m=5, length 25: witness search agrees")
    runs = ev["runs"]
    if full:
        for r in runs:
            got = M.residues(r["m"], tuple(r["counts"]))
            need(got == r["residues"], f"rerun m={r['m']} counts={r['counts']}")
    # claimed minima: below L, every count vector (up to reversal) was run and misses c; at L some run hits c
    def vectors(mm, length):
        k = length // mm - 5
        for extra in itertools.combinations_with_replacement(range(5), k):
            n = [mm] * 5
            for e in extra:
                n[e] += mm
            yield n
    def runs_for(mm, n):
        return [r for r in runs if r["m"] == mm and r["counts"] in (n, n[::-1])]
    for mm, minima in ev["minima"].items():
        mm = int(mm)
        for c, L in minima.items():
            c = int(c)
            exact = not str(L).startswith(">")
            L = int(str(L).lstrip(">="))
            for length in range(5 * mm, L if exact else L, mm):
                for n in vectors(mm, length):
                    rec = runs_for(mm, n)
                    need(rec, f"m={mm}: run recorded for counts {n}")
                    need(c not in rec[0]["residues"], f"m={mm}, c={c}: not attained at length {length}")
            if exact:
                need(any(w["m"] == mm and w["c"] == c and sum(w["counts"]) == L for w in ev["witnesses"]),
                     f"m={mm}, c={c}: witness of length {L}")
    print(json.dumps({"status": "PASS_DEPTH5_CONNECTOR_MITM", "minima": ev["minima"],
                      "witnesses_replayed": len(ev["witnesses"]) + 1, "full_rerun": full,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main(full="--full" in sys.argv))
