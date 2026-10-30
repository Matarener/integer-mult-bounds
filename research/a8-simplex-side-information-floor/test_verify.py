"""Rejecting controls for the A8 simplex side-information certificate."""
import copy
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify  # noqa: E402


def rejected(call):
    try:
        call()
    except SystemExit as exc:
        if str(exc).startswith("FAIL: "):
            return
        raise
    raise AssertionError("control unexpectedly accepted")


def main():
    rr, gram, pairing, orth, readers = verify.model()
    stored = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    d3 = verify.decoder(rr, True)
    sources, costs = verify.invoice(d3, pairing, readers)
    rows = stored["witnesses"]["nine_active"]["terms"]
    k = 2
    demand = sources[k] & readers[k]

    def check(bad_rows, bad_costs=costs):
        return lambda: verify.check_terms(pairing, orth, sources, readers, bad_costs, bad_rows)

    controls = 0
    verify.check_terms(pairing, orth, sources, readers, costs, rows)  # positive control

    # 1. Singular fooling block: replace one source by a line in the span of the others.
    bad = copy.deepcopy(rows)
    S, R = bad[k]["fooling_sources"], bad[k]["fooling_readers"]
    block = [sum(pairing[i][j] << t for t, j in enumerate(R)) for i in S[:-1]]
    swap = next(i for i in sorted(sources[k]) if i not in S
                and verify.f2_rank(block + [sum(pairing[i][j] << t for t, j in enumerate(R))]) < len(S))
    S[-1] = swap
    rejected(check(bad)); controls += 1

    # 2. Fooling source outside the term.
    bad = copy.deepcopy(rows)
    bad[k]["fooling_sources"][0] = next(i for i in range(verify.N) if i not in sources[k])
    rejected(check(bad)); controls += 1

    # 3. Petersen labels swapped across an edge and a non-edge.
    bad = copy.deepcopy(rows)
    pet = bad[k]["sideinfo"]["petersen"]
    pet[0], pet[2] = pet[2], pet[0]
    rejected(check(bad)); controls += 1

    # 4. Isolated line orthogonal to a Petersen vertex.
    bad = copy.deepcopy(rows)
    info = bad[k]["sideinfo"]
    info["isolated"][0] = next(c for c in sorted(demand)
                               if c not in info["petersen"] + info["isolated"]
                               and orth[c][info["petersen"][0]])
    rejected(check(bad)); controls += 1

    # 5. Duplicated witness line.
    bad = copy.deepcopy(rows)
    info = bad[k]["sideinfo"]
    info["isolated"][1] = info["isolated"][0]
    rejected(check(bad)); controls += 1

    # 6. Too few isolated lines for the rank (Petersen + 3 against rank 9).
    bad = copy.deepcopy(rows)
    bad[k]["sideinfo"]["isolated"].pop()
    rejected(check(bad)); controls += 1

    # 7. "Independent" set containing an orthogonal pair.
    bad = copy.deepcopy(rows)
    lines = bad[k]["max_independent"]
    lines[0] = next(c for c in sorted(demand) if c not in lines and orth[c][lines[1]])
    rejected(check(bad)); controls += 1

    # 8. Independence alone cannot certify a rank-9 term: claiming it is rejected.
    bad = copy.deepcopy(rows)
    alpha = bad[k]["max_independent"]
    bad[k]["sideinfo"] = {"kind": "independent", "lines": alpha + [alpha[0]]}
    rejected(check(bad)); controls += 1

    # 9. Wrong invoice: a raised cost on one term is not bound to its row.
    bad_costs = list(costs)
    bad_costs[0] += 1
    rejected(check(copy.deepcopy(rows), bad_costs)); controls += 1

    # 10. A non-constant change to one decoder row breaks the all-pairs identity.
    broken = list(d3)
    broken[0] = tuple(x + (1 if t == 0 else 0) for t, x in enumerate(broken[0]))
    rejected(lambda: verify.require(verify.exact(broken, rr, gram), "identity")); controls += 1

    # 11. Tampered stored certificate is caught by the stored re-check.
    bad = copy.deepcopy(stored)
    bad["witnesses"]["dropped"]["terms"][3]["sideinfo"]["petersen"].reverse()
    rejected(lambda: verify.recheck(bad)); controls += 1

    # 12. Drifted predecessor input bytes fail the pinned SHA256.
    entry = next(r for r in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
                 if r["usage"] == "input")
    real = (verify.ROOT / entry["path"]).read_bytes()
    rejected(lambda: verify.require(hashlib.sha256(real + b" ").hexdigest() == entry["sha256"],
                                    "input drift")); controls += 1

    print("PASS_A8_SIMPLEX_SIDE_INFORMATION_CONTROLS rejected=%d" % controls)


if __name__ == "__main__":
    main()
