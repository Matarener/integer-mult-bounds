"""Independent direct ten-row reconstruction; does not import the new generator."""

import gzip
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_BYTES = 32 * 1024 * 1024
SWAP = (42540, 43909)
CYCLE = (47357, 16407, 11607, 8944, 6491, 1796, 0, 18745)
PLACEMENT = ("owner_replica", "child", "port", "copy", "family")
LOGICAL = ("stage", "replica", "time", "helper", "width")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    need(path.stat().st_size <= MAX_BYTES, "input budget")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "expanded input budget")
    return json.loads(raw)


def digest(rows):
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def key(row):
    return row["owner_replica"], row["child"], row["port"]


def step(rows, cycle):
    out = [dict(row) for row in rows]
    for i, index in enumerate(cycle):
        source = rows[cycle[(i + 1) % len(cycle)]]
        for field in PLACEMENT:
            out[index][field] = source[field]
    bins = defaultdict(list)
    for i, row in enumerate(out):
        bins[key(row)].append(i)
    for members in bins.values():
        offset = 0
        for i in sorted(members, key=lambda j: (out[j]["offset"], j)):
            out[i]["offset"] = offset
            offset += out[i]["width"]
    return out


def reconstruct():
    rows = read(ROOT / "research/complex-t16-two-stage-cycles/data/OWNERS.json.gz")
    patch = read(PACKAGE / "predecessor.patch.json")
    need(len(rows) == 69120 and len(patch) == 240, "input dimensions")
    for item in patch:
        index = item["index"]
        need(rows[index] == item["before"], "predecessor preimage")
        rows[index] = item["after"]
    source = read(PACKAGE / "predecessor/RESULT.json")
    need(digest(rows) == source["owner_canonical_sha256"], "exact PR3375 map")
    middle = step(rows, SWAP)
    final = step(middle, CYCLE)
    need(
        all(
            all(a[k] == b[k] for k in LOGICAL) for a, b in zip(rows, final, strict=True)
        ),
        "changed logical role",
    )
    need(
        sum(key(a) != key(b) for a, b in zip(rows, final, strict=True)) == 10,
        "ten roles",
    )
    return rows, middle, final


def main():
    old, middle, final = reconstruct()
    result = read(PACKAGE / "RESULT.json")
    need(digest(final) == result["owner_canonical_sha256"], "complete final payload")
    keys = {key(old[i]) for i in SWAP + CYCLE}
    capacities = read(
        ROOT / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
    )
    residuals = []
    for rows in (old, middle, final):
        used = Counter()
        for row in rows:
            used[key(row)] += row["width"]
        residuals.append(
            {k: capacities["windows"][f"{k[0]},{k[1]}"][0] - used[k] for k in keys}
        )
    before = Counter(residuals[0].values())
    after = Counter(residuals[2].values())
    after.subtract(before)
    need({k: v for k, v in after.items() if v} == {2: 1, 3: -2, 4: 1}, "idle delta")
    need(sum(residuals[0].values()) == sum(residuals[2].values()), "rank mass")
    print("PASS_TEN_HELPER_INDEPENDENT rows=69120 relocations=10 delta=+H2-2H3+H4")


if __name__ == "__main__":
    main()
