"""Constant-input necessary conditions for first-read G20 captures.

Jerry Chen (@CubeJerry), with OpenAI Codex assistance. Apache-2.0.
No predecessor implementation is imported. Native address permutations act
as identity on constant functions; this is a necessary-condition projection,
not an exact native interpreter.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/g20-conjugation-admission/"
WORD = PREFIX + "WORD.json.gz"
FRAMES = PREFIX + "prior/prior/prior/source/vendor/g20/inputs/FRAMES.json"
LOCAL = PREFIX + "LOCAL-RESULT.json"
TOKENS = {1: 17, 2: 33, 3: 49, 4: 64, 5: 80, 6: 96}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticate(data, digest, name):
    require(sha256(data).hexdigest() == digest, "source hash: " + name)


def inputs():
    source = json.loads((HERE / "SOURCES.json").read_text())
    blobs = {}
    for row in source["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            authenticate(data, row["sha256"], row["path"])
            blobs[row["path"]] = data
    require(set(blobs) == {WORD, FRAMES, LOCAL}, "complete input manifest")
    return (json.loads(gzip.decompress(blobs[WORD])),
            json.loads(blobs[FRAMES])["frames"], json.loads(blobs[LOCAL]))


def census(word, frames, expected):
    records, start, final = word["records"], word["start"], word["final"]
    width = len(start)
    require(len(final) == width, "boundary width")
    owned = set(word["owned"])
    helpers = set(range(222, width)) - owned
    helper_mask = sum(1 << h for h in helpers)
    owned_mask = sum(1 << h for h in owned)
    dims = {int(f): row["dim"] for f, row in frames.items()}
    targets = {h: abs(dims[start[h]] - dims[final[h]]) for h in helpers}
    first, last = {}, {}
    for index, event in enumerate(records):
        if event[0] == "ADD":
            first.setdefault(event[2], index)
            last[event[2]] = index
    require(helpers <= first.keys(), "every helper has a first read")
    rows = [1 << i for i in range(width)]
    state = list(start)
    queries, eligible, early_cross = [], [], []
    early = {h: [] for h in helpers}
    paid = Counter()
    for index, event in enumerate(records):
        op, dest = event[:2]
        require(0 <= dest < width, "destination range")
        if op == "ADD":
            _, _, src, frame = event
            require(0 <= src < width and src != dest, "ADD operands")
            require(state[dest] == state[src] == frame, "ADD frame")
            rows[dest] ^= rows[src]
        elif op in ("ERASE", "INIT"):
            require(dest in owned, "reset of public input")
            if op == "ERASE":
                rows[dest] = 0
            state[dest] = event[2]
        elif op in ("Q", "ZERO_Q"):
            _, _, src_frame, dst_frame, rank = event
            require(state[dest] == src_frame, "query frame")
            require(abs(dims[src_frame] - dims[dst_frame]) == rank, "query rank")
            if op == "ZERO_Q":
                require(rows[dest] == 0, "nonzero free query")
            else:
                row = rows[dest]
                require(row != 0 and not row & owned_mask, "query input support")
                paid[rank] += 1
                before_read = dest in helpers and index < first[dest]
                query = (index, dest, rank, row)
                queries.append(query)
                if before_read:
                    early[dest].append((index, rank))
                support = row & helper_mask
                # If dest is not captured, its early query can still vanish
                # through ANOTHER captured helper. Keep those queries here.
                if support and (not before_read or support & ~(1 << dest)):
                    eligible.append(query)
                    if before_read:
                        early_cross.append(index)
            state[dest] = dst_frame
        else:
            raise ValueError("unknown event: " + op)
    require(state == final, "final frames")
    require(dict(sorted(paid.items())) ==
            {int(k): v for k, v in expected["stats"]["paid"].items()}, "paid profile")
    require(Counter(targets.values()) == {8: 413, 4: 2}, "target inventory")
    partial = {h for h in helpers if targets[h] == 4}
    require(partial == {465, 684}, "partial helpers")
    require(all(len(q) <= 1 and all(rank in (1, 2) for _, rank in q)
                for q in early.values()), "early-query tariff")
    require(all(not early[h] for h in partial), "partial early-query tariff")
    require(not any(h in helpers and i > last[h] for i, h, _, _ in queries),
            "no unpriced post-last-read query")
    free_two = {h for h in helpers if early[h] and early[h][0][1] == 2}
    vectors = sorted({row for _, _, _, row in eligible})
    ids = {row: i for i, row in enumerate(vectors)}
    multiplicities = Counter()
    for _, _, rank, row in eligible:
        multiplicities[ids[row]] += TOKENS[rank]
    return dict(word=word, helpers=helpers, targets=targets, first=first,
                early=early, partial=partial, free_two=free_two, vectors=vectors,
                multiplicities=multiplicities, queries=queries, eligible=eligible,
                early_cross=early_cross, final_rows=rows, paid=paid)


def independent(rows, low=False):
    basis = {}
    for value in rows:
        while value:
            pivot = (value & -value).bit_length() - 1 if low else value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
        else:
            return False
    return True


def check_partition(data, certificate):
    require(certificate["schema"] == "g20-first-read-flag-partition/v1", "certificate schema")
    limits = certificate["limits"]
    require(limits == [64, 92, 108], "flag capacities")
    groups = certificate["groups"]
    require(len(groups) == limits[2], "color count")
    vectors = data["vectors"]
    partial_mask = sum(1 << h for h in data["partial"])
    two_mask = sum(1 << h for h in data["free_two"])
    seen = Counter()
    for i, group in enumerate(groups):
        require(all(type(x) is int and 0 <= x < len(vectors) for x in group), "row ID")
        require(len(group) == len(set(group)), "duplicate in color")
        rows = [vectors[x] for x in group]
        if i >= limits[0]:
            require(all(not row & partial_mask for row in rows), "partial flag")
        if i >= limits[1]:
            require(all(not row & two_mask for row in rows), "rank-two flag")
        require(independent(rows) and independent(rows, low=True), "dependent color")
        seen.update(group)
    require(seen == data["multiplicities"], "complete token coverage")
    return [len(group) for group in groups]


def power_bounds():
    # Integer powers prove all inequalities on the full 99/100 <= t <= 1
    # interval, by monotonicity. No floating-point acceptance decision.
    for r in (1, 2, 3):
        require(r**99 * 64**100 <= 4**99 * TOKENS[r]**100, "rank token envelope")
    require(all(TOKENS[r] * 4 == 64 * r for r in (4, 5, 6)), "large-rank envelope")
    require(2**99 * 64**100 > 127**100, "lower 2^t")
    require(4**99 * 33**100 > 128**100, "upper 4^-t")
    require(2**99 * 65**100 > 128**100, "upper 2^-t")
    # The 108-color bound has uniform positive full-helper margins:
    require(127 * 2 - 92 * 2 - 65 == 5, "rank-two strict margin")
    require(127 * 2 - 108 * 2 - 33 == 5, "other strict margin")


def read_certificate():
    return json.loads(gzip.decompress((HERE / "PARTITION.json.gz").read_bytes()))
