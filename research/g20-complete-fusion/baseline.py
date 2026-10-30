"""Emit owned G20 retirements after their last nonzero source read.

The four partial-helper construction is due to Dugongue, PR5629.
The frozen word and replay are ai-nanachi PR5512, using Ali Romman PR5421.
Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
from functools import lru_cache
import importlib.util
import json
import sys

R = Path(__file__).resolve().parent
S = R / "source/vendor/g20"
PARTIAL = frozenset([462, 463, 466, 468])


def need(test, message):
    if not test:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for item in json.loads((R / "INPUTS.json").read_text()):
    need(sha256((R / item["local"]).read_bytes()).hexdigest() == item["sha256"], "Frozen source bytes: " + item["local"])
SOURCE = load("credited_g20_relations", R / "source/local_relations.py")


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def put(name, value):
    path = R / name
    data = (json.dumps(value, indent=2) + "\n").encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == ".gz" else data)


@lru_cache(maxsize=1)
def source():
    return SOURCE.source()


@lru_cache(maxsize=1)
def original_word():
    return read(R / "source/WORD.json.gz")


def construct(new_owned=PARTIAL):
    base, frames, _ = source()
    source_word = original_word()
    word = source_word["records"]
    owned = set(source_word["owned"])
    new_owned = set(new_owned)
    need(new_owned <= set(range(222, 658)) - owned, "Only new original helper owners")
    rows = [0 if i in new_owned else 1 << i for i in range(660)]
    last = {h: -1 for h in sorted(new_owned)}
    for ix, e in enumerate(word):
        op, d = e[:2]
        if op == "ADD":
            if e[2] in new_owned and rows[e[2]]:
                last[e[2]] = ix
            rows[d] ^= rows[e[2]]
        elif op == "ERASE":
            rows[d] = 0

    rows = [1 << i for i in range(660)]
    output, edits, closed = [], [], set()
    for h in sorted(new_owned):
        output.append(["ERASE", h, base["final"][h]])
        rows[h] = 0
    for ix, e in enumerate(word):
        op, d = e[:2]
        for h in sorted(new_owned):
            if ix > last[h] and h not in closed:
                output.append(["ERASE", h, base["start"][h]])
                closed.add(h)
                rows[h] = 0
        if d in closed:
            edits.append({"source_record": ix, "event": e, "reason": "unobserved_owned_tail"})
            continue
        if op == "ADD":
            if e[2] in closed:
                edits.append({"source_record": ix, "event": e, "reason": "zero_cold_read"})
                continue
            rows[d] ^= rows[e[2]]
        elif op == "ERASE":
            rows[d] = 0
        elif op == "Q" and not rows[d]:
            edits.append({"source_record": ix, "event": e, "reason": "whole_zero_query"})
            e = ["ZERO_Q", *e[1:]]
        output.append(e)
    need(closed == new_owned, "All new owned tails close")
    return output, owned | new_owned, last, edits


def run():
    base, frames, _ = source()
    word, owned, cuts, edits = construct()
    stats = SOURCE.replay(base, frames, word, owned)
    native = [SOURCE.replay(base, frames, word, owned, m) for m in [101, 101 ** 2]]
    expected = {1: 1305, 2: 1342, 3: 73, 4: 40, 5: 102, 6: 10, 7: 9}
    need(stats["paid"] == expected, "Exact changed local invoice")
    need(stats["retained_originals"] == 645 and stats["owned_allocated"] == 15, "Retained and owned census")
    removed = Counter(e["event"][4] for e in edits if e["event"][0] == "Q")
    need(removed == {1: 4, 3: 4}, "All four source H1 and H3 removals")
    faults = []
    for kind in ["missing_initial_clear", "early_retirement", "retained_input_erasure"]:
        bad = [e[:] for e in word]
        if kind == "missing_initial_clear":
            bad.pop(0)
        elif kind == "early_retirement":
            ix = next(i for i, e in enumerate(bad) if e[0] == "ADD" and e[2] == 462)
            bad.insert(ix, ["ERASE", 462, bad[ix][3]])
        else:
            bad.insert(0, ["ERASE", 47, base["final"][47]])
        try:
            SOURCE.replay(base, frames, bad, owned)
        except ValueError:
            faults.append(kind)
        else:
            raise ValueError("Accepted corruption: " + kind)
    result = {"status": "PASS_G20_FOUR_RETIREMENTS_ALL660_COLUMNS", "stats": stats,
              "native_moduli": [x["native_modulus"] for x in native], "cuts": cuts,
              "removed_queries": dict(removed), "edit_counts": dict(Counter(e["reason"] for e in edits)),
              "rejected_controls": faults,
              "canonical_word_sha256": sha256(json.dumps(word, separators=(",", ":")).encode()).hexdigest()}
    put("WORD.json.gz", {"records": word, "owned": sorted(owned), "start": base["final"] + [None, None], "final": base["start"] + [None, None]})
    put("EDITS.json", edits)
    put("LOCAL-RESULT.json", result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
