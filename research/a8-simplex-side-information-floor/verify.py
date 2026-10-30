"""Orthogonal side information keeps the A8 simplex nine-term COPY floor at 72.

Standard library only. Rebuilds the 120 E8 root lines in the A8 simplex
frame of research/a8-simplex-decoder-floor (#1248), its two pinned sharp
shift witnesses, and checks two finite certificates per term:

  fooling   rho_k source lines S and reader lines R inside the term with
            B[S,R] invertible over F2 (any message, linear or not, needs
            2^rho_k values: no side information);
  sideinfo  readers know every orthogonal input: an induced
            "Petersen + (rho_k - 5) isolated" subgraph of the orthogonality
            graph on the term's demand lines (broadcast rate rho_k), or a
            pairwise non-orthogonal set of size rho_k (independence bound).

It also computes, by exact branch and bound, the largest pairwise
non-orthogonal set in every demand graph. That independence bound alone
certifies only 64 on each witness, so the Petersen step is needed.

The stored RESULT.json must equal the rebuilt certificate.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PRED = ROOT / "research" / "a8-simplex-decoder-floor"
N = 120


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def pinned_inputs():
    """Every usage=input file must match its SOURCES.json SHA256 before use."""
    rows = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
    for row in rows:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"], "input drift: " + row["path"])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def f2_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            top = value.bit_length() - 1
            if top in pivots:
                value ^= pivots[top]
            else:
                pivots[top] = value
                break
    return len(pivots)


def roots():
    """A8 realization, scaled by 3: 36 pair roots e_a-e_b, 84 triple roots 1_S-1/3."""
    rows = []
    for a, b in itertools.combinations(range(9), 2):
        rows.append(tuple(3 if k == a else -3 if k == b else 0 for k in range(9)))
    for subset in itertools.combinations(range(9), 3):
        rows.append(tuple(2 if k in subset else -1 for k in range(9)))
    return rows


def model():
    rr = roots()
    require(len(rr) == N and all(sum(r) == 0 and dot(r, r) == 18 for r in rr), "A8 root model")
    gram = [[dot(x, y) for y in rr] for x in rr]
    require(all(g % 9 == 0 for row in gram for g in row), "integral Gram")
    # B_ij = 1 iff the true inner product is even: orthogonal or the same line.
    pairing = [[(g // 9 + 1) % 2 for g in row] for row in gram]
    orth = [[i != j and gram[i][j] == 0 for j in range(N)] for i in range(N)]
    readers = [frozenset(j for j in range(N) if rr[j][k]) for k in range(9)]
    return rr, gram, pairing, orth, readers


def decoder(rr, active):
    """#1248 witness: D_i = 2(r_i - r_i[anchor]) (scaled by 3); row 0 anchors at 1 when active."""
    return [tuple(2 * (x - r[1 if active and i == 0 else 0]) for x in r) for i, r in enumerate(rr)]


def exact(d3, rr, gram):
    # D T^t = 2G with D = d3/3 and T = r/3.
    return all(dot(d3[i], rr[j]) == 2 * gram[i][j] for i in range(N) for j in range(N))


def invoice(d3, pairing, readers):
    sources = [frozenset(i for i in range(N) if d3[i][k]) for k in range(9)]
    costs = []
    for k in range(9):
        rows = [sum(pairing[i][j] << j for j in readers[k]) for i in sorted(sources[k])]
        costs.append(f2_rank(rows))
    return sources, costs


def fooling(pairing, src, rdr, rho):
    """Greedy rho x rho invertible submatrix B[S,R]; returns sorted (S, R)."""
    S, basis_rows = [], []
    for i in sorted(src):
        row = sum(pairing[i][j] << j for j in rdr)
        if f2_rank(basis_rows + [row]) > len(basis_rows):
            S.append(i)
            basis_rows.append(row)
    require(len(S) == rho, "fooling sources reach the rank")
    R = []
    for j in sorted(rdr):
        cand = R + [j]
        cols = [sum(pairing[i][c] << t for t, c in enumerate(cand)) for i in S]
        if f2_rank(cols) == len(cand):
            R = cand
    require(len(R) == rho, "fooling readers reach the rank")
    return S, R


def check_fooling(pairing, src, rdr, S, R):
    """Distinct inputs on S give distinct reader vectors on R."""
    require(set(S) <= src and set(R) <= rdr and len(S) == len(R), "fooling support")
    require(len(set(S)) == len(S) and len(set(R)) == len(R), "fooling repeats")
    rows = [sum(pairing[i][j] << t for t, j in enumerate(R)) for i in S]
    require(f2_rank(rows) == len(S), "fooling block invertible")
    return len(S)


def masks(orth):
    full = (1 << N) - 1
    on = [sum(1 << j for j in range(N) if orth[i][j]) for i in range(N)]
    off = [full ^ on[i] ^ (1 << i) for i in range(N)]
    return on, off


def members(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def to_mask(lines):
    return sum(1 << i for i in lines)


KNESER = list(itertools.combinations(range(5), 2))
ADJ = [[not set(KNESER[a]) & set(KNESER[b]) for b in range(10)] for a in range(10)]


def petersen_in(on, off, pool):
    """Induced Petersen (edges = orthogonal pairs) inside the bitmask pool, or None."""
    assign = []

    def bt(t, rest):
        if t == 10:
            return list(assign)
        allowed = rest
        for u in range(t):
            allowed &= on[assign[u]] if ADJ[u][t] else off[assign[u]]
        for line in members(allowed):
            assign.append(line)
            found = bt(t + 1, rest & ~(1 << line))
            if found:
                return found
            assign.pop()
        return None
    return bt(0, pool)


def petersen_witness(on, off, demand, extra):
    """`extra` pairwise non-orthogonal lines, then an induced Petersen among the
    demand lines non-orthogonal to all of them. Returns (petersen, isolated)."""
    def bt(isolated, cand, common):
        if len(isolated) == extra:
            found = petersen_in(on, off, common)
            return (found, isolated) if found else None
        for line in members(cand):
            cand &= ~(1 << line)
            found = bt(isolated + [line], cand & off[line], common & off[line] & ~(1 << line))
            if found:
                return found
        return None
    pool = to_mask(demand)
    return bt([], pool, pool)


def max_independent(off, demand):
    """Exact largest pairwise non-orthogonal set inside demand (branch and bound)."""
    best = []

    def bt(chosen, cand):
        nonlocal best
        if len(chosen) + cand.bit_count() <= len(best):
            return
        if not cand:
            best = list(chosen)
            return
        for line in list(members(cand)):
            if len(chosen) + cand.bit_count() <= len(best):
                return
            bt(chosen + [line], cand & off[line])
            cand &= ~(1 << line)
    bt([], to_mask(demand))
    return sorted(best)


def check_petersen(orth, demand, petersen, isolated):
    lines = petersen + isolated
    require(len(petersen) == 10 and len(isolated) <= 4, "witness shape")
    require(len(set(lines)) == len(lines) and set(lines) <= demand, "witness inside the term")
    for a, b in itertools.combinations(range(10), 2):
        require(orth[petersen[a]][petersen[b]] == ADJ[a][b], "Petersen adjacency")
    for c in isolated:
        require(not any(orth[c][x] for x in lines if x != c), "isolated vertex")
    # Broadcast rate of Petersen is 5; isolated receivers add one each.
    return 5 + len(isolated)


def check_independent(orth, demand, lines, rho):
    require(len(lines) == rho and len(set(lines)) == rho and set(lines) <= demand, "independent support")
    require(not any(orth[a][b] for a, b in itertools.combinations(lines, 2)), "independent non-orthogonal")
    return rho


def term_certificates(pairing, orth, sources, readers, costs):
    on, off = masks(orth)
    out = []
    for k in range(9):
        src, rdr, rho = sources[k], readers[k], costs[k]
        S, R = fooling(pairing, src, rdr, rho)
        demand = src & rdr
        alpha = max_independent(off, demand)
        row = {"term": k, "rank": rho, "sources": len(src), "demand_lines": len(demand),
               "fooling_sources": S, "fooling_readers": R, "max_independent": alpha}
        if len(alpha) >= rho:
            row["sideinfo"] = {"kind": "independent", "lines": alpha[:rho]}
        else:
            require(rho >= 5, "term %d needs a Petersen witness" % k)
            found = petersen_witness(on, off, demand, rho - 5)
            require(found is not None, "Petersen witness in term %d" % k)
            row["sideinfo"] = {"kind": "petersen+isolated", "petersen": found[0], "isolated": found[1]}
        out.append(row)
    return out


def check_terms(pairing, orth, sources, readers, costs, rows):
    fool, side, indep = [], [], []
    for k, row in enumerate(rows):
        require(row["term"] == k and row["rank"] == costs[k], "term row binding")
        fool.append(check_fooling(pairing, sources[k], readers[k],
                                  row["fooling_sources"], row["fooling_readers"]))
        demand = sources[k] & readers[k]
        indep.append(check_independent(orth, demand, row["max_independent"], len(row["max_independent"])))
        info = row["sideinfo"]
        if info["kind"] == "petersen+isolated":
            side.append(check_petersen(orth, demand, info["petersen"], info["isolated"]))
        else:
            require(info["kind"] == "independent", "certificate kind")
            side.append(check_independent(orth, demand, info["lines"], costs[k]))
    require(fool == costs, "no-side-information bounds equal the linear invoice")
    require(side == costs, "side-information bounds equal the linear invoice")
    return sum(fool), sum(side), sum(indep)


def source_witnesses():
    pinned_inputs()
    data = json.loads((PRED / "CERTIFICATE.json").read_text(encoding="utf-8"))
    require(data["sharp_cost"] == 72, "pinned sharp cost")
    return {"dropped": (False, data["dropped_witness_costs"]),
            "nine_active": (True, data["active_witness_costs"])}


def result():
    rr, gram, pairing, orth, readers = model()
    require(all(f2_rank(sum(pairing[i][j] << j for j in readers[k]) for i in range(N)) == 9
                for k in range(9)), "reader supports have full pairing rank")
    out = {"schema_version": 1, "root_lines": N, "petersen_terms": 0,
           "orthogonal_pairs": sum(orth[i][j] for i in range(N) for j in range(i)),
           "witnesses": {}}
    for name, (active, pinned_costs) in source_witnesses().items():
        d3 = decoder(rr, active)
        require(exact(d3, rr, gram), name + " all-pairs identity")
        sources, costs = invoice(d3, pairing, readers)
        require(costs == pinned_costs, name + " invoice equals pinned predecessor")
        rows = term_certificates(pairing, orth, sources, readers, costs)
        fool, side, indep = check_terms(pairing, orth, sources, readers, costs, rows)
        require(fool == side == 72, name + " totals")
        require(indep == 64, name + " independence bound alone gives 64")
        out["petersen_terms"] += sum(r["sideinfo"]["kind"] == "petersen+isolated" for r in rows)
        out["witnesses"][name] = {"costs": costs, "no_side_info_floor": fool,
                                  "orthogonal_side_info_floor": side,
                                  "independence_only_floor": indep, "terms": rows}
    return out


def recheck(stored):
    """Re-check the stored certificate itself, not only its regeneration."""
    rr, gram, pairing, orth, readers = model()
    for name, (active, _) in source_witnesses().items():
        sources, costs = invoice(decoder(rr, active), pairing, readers)
        fool, side, indep = check_terms(pairing, orth, sources, readers, costs,
                                        stored["witnesses"][name]["terms"])
        require(fool == side == 72 and indep == 64, name + " stored totals")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="explicitly regenerate RESULT.json")
    args = ap.parse_args()
    evidence = result()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(evidence, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    else:
        stored = json.loads(path.read_text(encoding="utf-8"))
        require(stored == json.loads(json.dumps(evidence)), "stored certificate mismatch")
        recheck(stored)
    digest = hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()[:16]
    print("PASS_A8_SIMPLEX_SIDE_INFORMATION_FLOOR roots=120 witnesses=2 no_side_info=72 "
          "orthogonal_side_info=72 independence_only=64 petersen_terms=%d certificate=%s no_new_kappa"
          % (evidence["petersen_terms"], digest))


if __name__ == "__main__":
    main()
