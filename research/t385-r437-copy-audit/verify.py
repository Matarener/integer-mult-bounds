#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Chris R / Clear1nsight with substantial OpenAI Codex assistance.
"""Independent R437 exact physical pullbacks and finite COPY cost audit.
Credits: PR1627's exact-stream model/gauge proof; PR2088/selected separation
and two-copy physical audits for the full-map distinction. No author imports.
"""
import argparse
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

P = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == ".gz" else b)


def authenticate():
    sources = read(P / "SOURCES.json")
    for e in sources["files"] + sources["retained"]:
        if e["usage"] != "input":
            continue
        p = P.parents[1] / e["path"]
        need(p.is_file() and not p.is_symlink(), "input missing/linked: " + e["path"])
        b = p.read_bytes()
        if e.get("encoding") == "gzip-original-utf8-bytes":
            # A lossless transport of the exact large predecessor JSON. Its
            # decompressed bytes, not a regenerated gzip header, are the input.
            b = gzip.decompress(b)
        need(hashlib.sha256(b).hexdigest() == e["sha256"], "input SHA: " + e["path"])
        need(
            hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
            == e["git_blob"],
            "input blob: " + e["path"],
        )


def projection(w, indices):
    bs = []
    for k in indices:
        x = list(map(Q, w["lines"][k]))
        for b in bs:
            c = sum(a * v for a, v in zip(x, b)) / sum(v * v for v in b)
            x = [a - c * v for a, v in zip(x, b)]
        if any(x):
            bs.append(x)
    p = [
        [sum((b[i] * b[j] / sum(v * v for v in b) for b in bs), Q(0)) for j in range(8)]
        for i in range(8)
    ]
    need(
        all(
            sum(p[i][k] * p[k][j] for k in range(8)) == p[i][j]
            for i in range(8)
            for j in range(8)
        ),
        "projector idempotence",
    )
    need(sum(p[i][i] for i in range(8)) == len(bs), "projector trace")
    return p, len(bs)


class Maps:
    def __init__(self):
        self.values = []
        self.index = {}
        self.identity = self.put([int(i == j) for i in range(16) for j in range(16)], 1)

    def put(self, a, d):
        g = math.gcd(d, *a)
        key = tuple(x // g for x in a), d // g
        need(key[1] > 0 and key[1] & (key[1] - 1) == 0, "non-dyadic address map")
        if key not in self.index:
            self.index[key] = len(self.values)
            self.values.append(key)
        return self.index[key]

    def swap(self, p):
        a = [
            Q(i % 8 == j % 8) - p[i % 8][j % 8] if i // 8 == j // 8 else p[i % 8][j % 8]
            for i in range(16)
            for j in range(16)
        ]
        d = math.lcm(*(x.denominator for x in a))
        return self.put([int(x * d) for x in a], d)

    @lru_cache(None)
    def mul(self, l, r):
        if l == self.identity:
            return r
        if r == self.identity:
            return l
        a, ad = self.values[l]
        b, bd = self.values[r]
        c = [0] * 256
        for i in range(16):
            for k in range(16):
                x = a[16 * i + k]
                if x:
                    for j in range(16):
                        c[16 * i + j] += x * b[16 * k + j]
        return self.put(c, ad * bd)

    def pull(self, row, m):
        return {(i, self.mul(a, m)) for i, a in row}

    def serial(self, m):
        a, d = self.values[m]
        return dict(
            denominator=d, rows=[list(a[i : i + 16]) for i in range(0, 256, 16)]
        )


def geometry(w, a):
    dims = []
    maps = []
    for indices in w["frames"]:
        p, d = projection(w, indices)
        m = a.swap(p)
        need(a.mul(m, m) == a.identity, "D_P involution")
        dims.append(d)
        maps.append(m)
    need(len(dims) == 636 and dims[:2] == [0, 8], "frame convention")
    return dims, maps


def emit(w, dims):
    v = w["v"]
    n = 2 * v + w["R"]
    cur = w["start"][:]
    rows = [1 << i for i in range(n)]
    out = []
    captures = []

    def move(r, f):
        old = cur[r]
        if old != f:
            need(set(w["frames"][old]) <= set(w["frames"][f]), "frame descent")
            out.append([0, r, old, f, dims[f] - dims[old], 0])
            cur[r] = f

    for sec in ["D", "A", "B", "C"]:
        if sec == "B":
            for j, r in enumerate(w["ret"]):
                f = cur[r]
                need(dims[f] == 7, "COPY rank")
                targets = [v + t for t, ss in enumerate(w["scatter"]) if j in ss]
                captures.append(dict(center=r, frame=f, row=rows[r], targets=targets))
                out.append([2, r, n, f, 0, 7, 0])
                for t in targets:
                    need(cur[t] == 0, "noncold scatter")
                    out.append([1, t, n, 1, 0, 0])
                    rows[t] ^= rows[r]
                out.append([3, r, n, f, 0, 0, 0])
        for f, d, ss in w[sec]:
            need(d not in ss and len(ss) == len(set(ss)), "ambiguous grouped ADD")
            for r in [d] + ss:
                move(r, f)
            for s in ss:
                out.append([1, d, s, 1, f, 0])
                rows[d] ^= rows[s]
    for r, f in enumerate(w["final"]):
        move(r, f)
    need(
        rows
        == [(1 << i) ^ ((1 << (i - v)) if v <= i < 2 * v else 0) for i in range(n)],
        "scalar arbitrary-dirty endpoint",
    )
    return out, captures


def inverse(records, dims):
    out = []
    for op, d, s, a, b, *tail in reversed(records):
        if op == 0:
            out.append([0, d, a, s, b, 1])
        elif op == 1:
            out.append([1, d, s, -a, b, 1])
        elif op == 3:
            out.append([2, d, s, a, b, abs(dims[a] - dims[b]), 1])
        else:
            out.append([3, d, s, a, b, tail[0], 1])
    return out


def execute(
    records,
    w,
    dims,
    swaps,
    a,
    rev=False,
    wrong_copy=None,
    omit_dirty=False,
    omit_moves=False,
    omit_capture_input=None,
):
    v = w["v"]
    n = 2 * v + w["R"]
    initial = w["final"] if rev else w["start"]
    final = w["start"] if rev else w["final"]
    cur = initial[:] + [-1]
    rows = [{(i, a.identity)} for i in range(n)] + [set()]
    norm = [1] * n + [0]
    live = None
    profile = Counter()
    counts = Counter()
    peak = 1
    atoms = 0
    caps = []
    for op, d, s, x, y, *tail in records:
        if op == 0:
            need(cur[d] == s and d != live, "MOVE state")
            lo, hi = (x, s) if rev else (s, x)
            need(
                set(w["frames"][lo]) <= set(w["frames"][hi])
                and dims[hi] - dims[lo] == y > 0,
                "MOVE containment/rank",
            )
            if not omit_moves:
                rows[d] = a.pull(rows[d], a.mul(swaps[s], swaps[x]))
            atoms += len(rows[d])
            cur[d] = x
            profile[y] += 1
            counts["MOVE"] += 1
        elif op == 1:
            need(d < n and d != s and d != live, "ADD mutates live center")
            need(cur[d] == cur[s] == y, "ADD common native frame")
            need(s < n or live is not None, "read closed private")
            rows[d] ^= rows[s]
            norm[d] += norm[s]
            peak = max(peak, norm[d])
            counts["ADD"] += 1
        elif op == 2:
            need(
                live is None and s == n and not rows[n] and cur[n] == -1,
                "COPY nonblank/aliased private",
            )
            need(cur[d] == x and y == 0 and tail[0] == dims[x] == 7, "COPY frame/rank")
            m = a.mul(swaps[x], swaps[y]) if wrong_copy is None else wrong_copy
            rows[n] = a.pull(rows[d], m)
            if omit_dirty:
                rows[n] = {(i, z) for i, z in rows[n] if i < 2 * v}
            if omit_capture_input is not None and d == omit_capture_input[0]:
                rows[n] = {(i, z) for i, z in rows[n] if i != omit_capture_input[1]}
            cur[n] = y
            norm[n] = norm[d]
            live = d
            profile[7] += 1
            counts["COPY"] += 1
            caps.append(
                dict(
                    center=d,
                    frame=x,
                    terms=len(rows[n]),
                    dirty_terms=sum(i >= 2 * v for i, z in rows[n]),
                )
            )
        elif op == 3:
            need(live == d and s == n and cur[d] == x and cur[n] == y, "ERASE state")
            need(
                rows[n] == a.pull(rows[d], a.mul(swaps[x], swaps[y])),
                "ERASE complete transported equality",
            )
            rows[n] = set()
            norm[n] = 0
            cur[n] = -1
            live = None
            counts["ERASE"] += 1
        else:
            raise ValueError("unknown event")
    need(
        live is None and not rows[n] and cur[n] == -1 and cur[:n] == final,
        "return boundary",
    )
    endpoints = []
    for r in range(n):
        want = {(r, a.mul(swaps[initial[r]], swaps[final[r]]))}
        if v <= r < 2 * v:
            want ^= {(r - v, a.mul(swaps[initial[r - v]], swaps[final[r]]))}
        need(rows[r] == want, "physical arbitrary-function endpoint " + str(r))
        endpoints.append([(i, a.serial(m)) for i, m in sorted(rows[r])])
    return dict(
        counts=dict(sorted(counts.items())),
        profile=dict(sorted(profile.items())),
        positive_bound=peak,
        arbitrary_input_functions=n,
        private_streams_peak=1,
        transported_atoms=atoms,
        captures=caps,
        endpoint_sha256=hashlib.sha256(canon(endpoints)).hexdigest(),
    )


def reject(fn, label):
    try:
        fn()
    except ValueError as e:
        return dict(control=label, rejected_by=str(e))
    raise ValueError("accepted control: " + label)


def cost(t, fw, bw, discard_charge=None):
    need(
        (t["m"], t["live"], t["stages"], t["replicas"]) == (64, 28416, 9, 32),
        "host scope",
    )
    need(
        t["private_centre_reserve"] == 9 and not any(t["banks_per_stage"].values()),
        "host/private stock",
    )
    wins = {e["idx"]: e for e in t["schedule"] if e["kind"] == "idle"}
    occupied = defaultdict(set)
    assigned = {}
    for i, cp, off, width, stage, h in t["hosting"]["slots"]:
        need(
            0 <= cp < 222
            and 0 <= h < 437
            and width == 8
            and 0 <= off
            and off + 8 <= wins[i]["rank"],
            "slot capacity",
        )
        need(
            stage in t["hosting"]["windows"][str(i)][2] and (stage, h) not in assigned,
            "slot eligibility/uniqueness",
        )
        axes = set(range(off, off + 8))
        need(not occupied[i, cp] & axes, "slot overlap")
        occupied[i, cp] |= axes
        assigned[stage, h] = i, cp, off
    need(len(assigned) == 9 * 437, "helper inventory")
    idle = Counter()
    for i, w in wins.items():
        for cp in range(222):
            left = set(range(w["rank"])) - occupied[i, cp]
            need(
                not left or left == set(range(min(left), w["rank"])), "residual suffix"
            )
            if left:
                idle[len(left)] += 32
    profile = Counter({r: n * 288 for r, n in fw["profile"].items()})
    profile.update(idle)
    need(
        dict(profile)
        == {
            1: 380160,
            2: 400864,
            3: 22176,
            4: 26592,
            5: 29376,
            6: 17376,
            7: 26496,
            26: 32,
            42: 384,
        },
        "whole finite profile",
    )
    seen = set()
    for call in t["calls"]:
        st, rep = call["stage"], call["replica"]
        need((st, rep) not in seen, "duplicate call")
        seen.add((st, rep))
        owners = call["owners"]
        need(
            len(owners) == 659 and all(0 <= o[0] < 28416 for o in owners),
            "private aliases persistent family",
        )
        data_families = {o[0] for o in owners[:222]}
        need(len(data_families) == 222, "data family aliases")
        physical = set()
        for h, (family, desc) in enumerate(owners[222:]):
            i, cp, off = assigned[st, h]
            w = wins[i]
            side, port = divmod(cp, 111)
            need(
                family not in data_families
                and family == rep * 888 + (2 * w["pair"] + side) * 111 + port
                and desc == ["hosted", i, off, 8],
                "helper owner binding",
            )
            start = 1 if w["source_level"] == -1 else 8 + 7 * w["source_level"]
            key = family, tuple(range(start + off, start + off + 8))
            need(key not in physical, "identical physical owner chart")
            physical.add(key)
    need(len(seen) == 288, "complete call inventory")
    E = sum(profile.values())
    episodes = len(seen) * fw["counts"]["COPY"]
    need(
        episodes == len(seen) * fw["counts"]["ERASE"] == 2592,
        "COPY/ERASE charge coverage",
    )
    if discard_charge is None:
        discard_charge = episodes
    need(discard_charge == episodes, "linear complete-private-stream discard charge")
    J = 8 * 32 * 9 * 659 + 8 * 8 * 111 * 32 + 2 * 9 * 32 * 437 + 2 * episodes
    prefix = 2**18 * fw["positive_bound"] ** 5 * bw["positive_bound"] ** 4
    route = read(P / "inputs/r437-geometry.json.gz")["max_route_factors"]
    components = dict(
        unit_ADD=288 * fw["counts"]["ADD"] + 18 * 111 * 32,
        source_move_copy_high=J * 16 * (64**2 + 1) ** 2,
        source_move_copy_physical=J * 28425,
        good_edges=E * (8 * 64**2 + 8),
        compiler_edges=E * 128 * 128**3,
        matrix_test=16 * 64**3,
        linear_private_discard=discard_charge,
        selectors=2 * 9 * 32 * ((28416 - 1) + 437 * 64 * (route + 144 + 2 + 63 + 64)),
        prefix=prefix,
        one=1,
    )
    coefficient = sum(components.values())
    two = (coefficient + 1) ** 2 * (E + 1) ** 2
    need(
        (prefix.bit_length(), coefficient.bit_length(), two.bit_length())
        == (177, 177, 393),
        "finite precision ledger",
    )
    need(sum(r * n for r, n in profile.items()) == 1808352, "rank mass")
    need(
        64 * 28416 - 1808352 == 10272 and 2 * max(profile) ** 2 < 64**2,
        "deficit/halving guard",
    )
    fallback_exact = 6 * 128 * 127 + 3 * 128 + 6 * 127
    need(fallback_exact == 98682 < 32 * 64**2, "bad-class fallback overcharge")
    return dict(
        local_calls=288,
        COPY_episodes=episodes,
        COPY_rank_mass=7 * episodes,
        ERASE_linear_episodes=episodes,
        private_family=28416,
        reserved_private_families=9,
        physical_families=28425,
        helper_owner_occurrences=125856,
        profile=dict(sorted(profile.items())),
        edges=E,
        J=J,
        components={k: str(v) for k, v in components.items()},
        prefix_bits=177,
        charged_prefix_bits=192,
        coefficient_bits=177,
        two_level_bits=393,
        charged_two_level_bits=512,
        ROW=18355,
        bad_fraction="1/10000000000000000",
        fallback_exact_per_edge=fallback_exact,
        fallback_overcharge_per_edge=32 * 64**2,
        fallback_total_rank_one_weight=32 * 64**2 * E,
        cost_reuse="Historical high/physical/compiler/route/prefix/ROW/fallback coefficient bounds are source-bound inputs, not re-proved implementations",
        implementation_cost_status="INHERITED_CONDITIONAL_NOT_A_NEW_COMPILER_BOUND",
    )


def calculate():
    authenticate()
    w = read(P / "inputs/r437-word.json.gz")
    old = read(P / "inputs/selected589-word.json.gz")
    t = read(P / "inputs/r437-template.json.gz")
    need((w["v"], w["R"], w["h"]) == (111, 437, 8), "word scope")
    a = Maps()
    dims, swaps = geometry(w, a)
    rec, caps = emit(w, dims)
    rev = inverse(rec, dims)
    need(
        rec == t["local_programs"]["forward"] and rev == t["local_programs"]["reverse"],
        "literal template programs",
    )
    reports = dict(
        forward=execute(rec, w, dims, swaps, a),
        reverse=execute(rev, w, dims, swaps, a, True),
    )
    fw = reports["forward"]
    bw = reports["reverse"]
    need(
        fw["counts"] == bw["counts"] == dict(ADD=24208, COPY=9, ERASE=9, MOVE=2906),
        "local event count",
    )
    need(
        fw["profile"]
        == bw["profile"]
        == {1: 1320, 2: 1344, 3: 77, 4: 43, 5: 102, 6: 11, 7: 18},
        "local recursive profile",
    )
    need(
        [fw["positive_bound"], bw["positive_bound"]] == [49347, 1113998],
        "positive bounds",
    )
    for key in ["lines", "frames", "scatter"]:
        need(w[key] == old[key], "selected geometry/scatter")
    _, oldcaps = emit(old, dims)
    changes = []
    for before, after in zip(oldcaps, caps):
        od = {i for i in range(222, 661) if before["row"] >> i & 1}
        nd = {i for i in range(222, 659) if after["row"] >> i & 1}
        survive = {i - int(i > 464) - int(i > 470) for i in od if i not in [464, 470]}
        need(
            before["frame"] == after["frame"]
            and before["row"] & ((1 << 111) - 1) == after["row"] & ((1 << 111) - 1),
            "clean capture boundary",
        )
        changes.append(
            dict(
                old_center=before["center"],
                new_center=after["center"],
                frame=after["frame"],
                old_dirty_count=len(od),
                new_dirty_count=len(nd),
                removed_old_dirty_labels=sorted(od & {464, 470}),
                added_surviving_labels=sorted(nd - survive),
                removed_surviving_labels=sorted(survive - nd),
                arbitrary_dirty_row_hex=hex(after["row"] >> 222),
                SOURCE_row_hex=hex(after["row"] & ((1 << 111) - 1)),
                COPY_address_map=a.serial(swaps[after["frame"]]),
            )
        )
    controls = [
        reject(
            lambda: execute(rec, w, dims, swaps, a, omit_dirty=True),
            "project helper dirt away at COPY",
        ),
        reject(
            lambda: execute(rec, w, dims, swaps, a, wrong_copy=swaps[1]),
            "rank-eight swap priced seven",
        ),
        reject(
            lambda: execute(rec, w, dims, swaps, a, wrong_copy=swaps[caps[1]["frame"]]),
            "different rank-seven map",
        ),
        reject(
            lambda: execute(rec, w, dims, swaps, a, omit_moves=True),
            "MOVE labels without address action",
        ),
    ]
    bad = json.loads(json.dumps(t))
    bad["calls"][0]["owners"][222][0] = 28416
    controls.append(
        reject(
            lambda: cost(bad, fw, bw), "private family aliases persistent dirty input"
        )
    )
    controls.append(
        reject(lambda: cost(t, fw, bw, discard_charge=0), "omit private discard cost")
    )
    controls.append(
        reject(
            lambda: execute(rec, w, dims, swaps, a, omit_capture_input=(475, 340)),
            "predecessor-only dirt contract at changed capture 475",
        )
    )
    # An actual changed-label witness: copying only the predecessor's surviving
    # named dirt subset omits input 340 in the current center 475. All other
    # input functions may be zero and input 340 may be the constant-one function.
    changed = changes[5]
    need(
        changed["new_center"] == 475 and changed["added_surviving_labels"] == [340],
        "changed-label witness",
    )
    need(caps[5]["row"] >> 340 & 1, "dirty witness missing from complete capture")
    return dict(
        status="PASS_R437_ARBITRARY_STREAM_AND_FINITE_COPY_COST_AUDIT",
        domain="Ideal exact Boolean streams on odd-characteristic address fields; arbitrary complete functions including correlated dirt",
        directions=reports,
        capture_changes=changes,
        label_specific_counterexample=dict(
            center=475,
            frame=515,
            arbitrary_dirty_input=340,
            input_function="constant one; every other initial function zero",
            complete_COPY_value=1,
            predecessor_surviving_named_dirt_only_COPY_value=0,
            scope="Counterexample to a weaker label-specific contract, not to R437's stated universal contract",
        ),
        finite_cost=cost(t, fw, bw),
        controls=controls,
        new_compiler_or_supplier_admission=False,
        selected_frontier_changed=False,
        remaining=[
            "uniform all-size source-preserving COPY child and restored recursive scratch",
            "actual tape/routing/volume-normalized cost",
            "mutable SOURCE/common field/cover realization",
            "precision/recovery/analytic/BIT premises",
        ],
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", type=Path)
    args = ap.parse_args()
    # Histograms use integer ranks internally; JSON object keys are strings.
    # Normalize that representation before comparing the complete receipt.
    result = json.loads(canon(calculate()))
    if args.emit:
        with args.emit.open("x") as f:
            json.dump(result, f, sort_keys=True, indent=2)
            f.write("\n")
    else:
        need(result == read(P / "RESULT.json"), "recomputed result differs")
    print(
        result["status"],
        "functions=659 directions=2 controls=" + str(len(result["controls"])),
    )


if __name__ == "__main__":
    main()
