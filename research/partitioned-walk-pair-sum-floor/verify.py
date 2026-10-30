"""Pair-sum floor for partitioned independent-walk duals at every query count.

Extends Wentao Li's PR #2779 model (research/independent-walks-7q-obstruction)
to arbitrary labels (repeats and zero revisits) and any number of walks, and
answers its open question 2. The walk tables, two-port dual and tariff are
imported from that package's model.py, which is a pinned live input.
"""
from __future__ import annotations

import json
import random
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "independent-walks-7q-obstruction"))
import model  # noqa: E402  (pinned predecessor model)

INF = model.INF
ENDPOINT = 436
FULL = 32


def need(ok, message):
    if not ok:
        raise ValueError(message)


def walks(n):
    """Every restored walk of length n with arbitrary labels in F2^5."""
    for tail in product(range(FULL), repeat=n - 1):
        slots = (0,) + tail
        if model.valid_restored_walk(slots):
            yield slots


def rank(vals):
    return model.gf2_span(vals)[1]


def pair_sums(slots):
    return {a ^ b for i, a in enumerate(slots) for b in slots[i + 1:] if a ^ b}


def dual_table(tables):
    """k-port min-plus convolution: cost of m = min over a_1^...^a_k = m."""
    acc = tables[0]
    for e in tables[1:]:
        nxt = [INF] * FULL
        for a in range(FULL):
            if acc[a] >= INF:
                continue
            for b in range(FULL):
                if e[b] < INF and acc[a] + e[b] < nxt[a ^ b]:
                    nxt[a ^ b] = acc[a] + e[b]
        acc = nxt
    return acc


def dual_R(walk_list):
    table = dual_table([model.even_table(w) for w in walk_list])
    if any(table[m] >= INF for m in range(1, FULL)):
        return None
    return sum(table[1:])


def pair_sum_floor(walk_list):
    covered = set().union(*(pair_sums(w) for w in walk_list))
    return 4 * 31 - 2 * len(covered)


def closed_floor(q):
    """max over partitions of sum C(n_i,2) is 1 + C(q-2,2), at (2, q-2)."""
    return max(62, 122 - (q - 2) * (q - 3))


def partitions(q, parts_min=2):
    """Non-increasing partitions of q into at least two parts >= 2."""
    def rec(rest, cap):
        if rest == 0:
            yield ()
            return
        for p in range(min(rest, cap), parts_min - 1, -1):
            for tail in rec(rest - p, p):
                yield (p,) + tail
    return [p for p in rec(q, q) if len(p) >= 2]


def check_table_lemma(max_len):
    """Every walk: e[v] finite iff v in span; e[v]==2 iff v is a pair sum."""
    count = 0
    for n in range(2, max_len + 1):
        for w in walks(n):
            e = model.even_table(w)
            span, _ = model.gf2_span(w)
            ps = pair_sums(w)
            for v in range(1, FULL):
                need((e[v] < INF) == (v in span), f"span lemma {w} {v}")
                if e[v] < INF:
                    need(e[v] >= 2 and e[v] % 2 == 0, f"even cost {w} {v}")
                need((e[v] == 2) == (v in ps), f"pair-sum lemma {w} {v}")
            count += 1
    return count


def census_q7():
    """Q=7 two-walk duals: covering needs full combined rank, hence distinct
    nonzero labels in each walk. Enumerates every arbitrary-label walk."""
    stats = {}
    for n, need_rank in ((2, 1), (3, 2), (4, 3), (5, 4)):
        total = full = 0
        for w in walks(n):
            total += 1
            if rank(w[1:]) == need_rank:
                full += 1
                need(len(set(w[1:])) == n - 1 and 0 not in w[1:],
                     f"full-rank walk with repeat {w}")
        stats[n] = {"walks": total, "full_rank": full,
                    "rank_deficient": total - full}
    return stats


def random_controls(trials, seed=16):
    rng = random.Random(seed)
    covering = 0
    for _ in range(trials):
        q = rng.randrange(7, 12)
        parts = rng.choice(partitions(q))
        ws = []
        for n in parts:
            while True:
                w = (0,) + tuple(rng.randrange(FULL) for _ in range(n - 1))
                if model.valid_restored_walk(w):
                    ws.append(w)
                    break
        r = dual_R(ws)
        span_rank = rank([x for w in ws for x in w])
        need((r is not None) == (span_rank == 5), f"cover iff full span {ws}")
        if len(ws) == 2:
            r2 = model.dual_independent_R(model.even_table(ws[0]),
                                          model.even_table(ws[1]))
            need(r2 == r, f"k-port dual disagrees with model {ws}")
        if r is None:
            continue
        covering += 1
        need(r >= pair_sum_floor(ws) and r >= 62, f"pair-sum floor {ws} {r}")
        need(r >= closed_floor(q), f"closed floor {ws} {r}")
    return covering


WITNESSES = {
    8: ((0, 10), (0, 22, 5, 31, 24, 20)),
    9: ((0, 3), (0, 18, 1, 5, 11, 20, 27)),
}


def main():
    full_mode = "--quick" not in sys.argv
    lemma_walks = check_table_lemma(5 if full_mode else 4)
    q7 = census_q7()
    covering = random_controls(4000)

    for q in range(7, 12):
        for parts in partitions(q):
            s = sum(n * (n - 1) // 2 for n in parts)
            need(s <= 1 + (q - 2) * (q - 3) // 2, f"partition max {parts}")
    for q in range(7, 7 + 1):
        need(all(sum(n - 1 for n in p) < 5 for p in partitions(q) if len(p) >= 3),
             "three walks cannot cover at Q=7")

    witnesses = {}
    for q, ws in WITNESSES.items():
        need(sum(len(w) for w in ws) == q, "witness size")
        need(all(model.valid_restored_walk(w) for w in ws), "witness valid")
        r = dual_R(ws)
        need(r == closed_floor(q), f"witness {q} attains floor: {r}")
        x = sum(model.path_X(w) for w in ws)
        witnesses[q] = {"walks": [list(w) for w in ws], "R": r, "path_X": x,
                        "tariff": model.tariff_qrx(q, r, x)}

    tariff = {}
    for q in range(7, 12):
        r = closed_floor(q)
        t = model.tariff_qrx(q, r, 0)
        need(t > ENDPOINT, f"tariff floor {q}")
        tariff[q] = {"R_floor": r, "tariff_floor_X0": t}
    need(model.tariff_qrx(12, 0, 0) > ENDPOINT, "Q>=12 by queries alone")

    report = {"table_lemma_walks": lemma_walks, "q7_walks": q7,
              "random_covering_duals": covering, "witnesses": witnesses,
              "tariff_floor": tariff}
    print(json.dumps(report, sort_keys=True))
    print("PASS_PARTITIONED_WALK_PAIR_SUM_FLOOR"
          f" lemma_walks={lemma_walks} q7_full_rank_5walks={q7[5]['full_rank']}"
          f" q8_min_R=92 q9_min_R=80 min_tariff={min(v['tariff_floor_X0'] for v in tariff.values())}"
          " no_new_kappa")


if __name__ == "__main__":
    main()
