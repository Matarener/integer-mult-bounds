"""Replay the G20 conjugations and retain every independent target.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retain all predecessor notices in prior/.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R))
from replay_options import COMPRESSION_LEVEL


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bitids(row):
    while row:
        bit = row & -row
        yield bit.bit_length() - 1
        row ^= bit


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def put(name, value):
    path = R / name
    raw = (json.dumps(value, indent=2) + "\n").encode()
    path.write_bytes(gzip.compress(raw, compresslevel=COMPRESSION_LEVEL, mtime=0) if path.suffix == ".gz" else raw)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


for item in read(R / "INPUTS.json"):
    need(sha256((R / item["local"]).read_bytes()).hexdigest() == item["sha256"],
         "Frozen input " + item["local"])
PRIOR = load("conjugation_prior_integration", R / "prior/integration.py")
SOURCE, source, S, RETIRED = PRIOR.SOURCE, PRIOR.source, PRIOR.S, PRIOR.RETIRED
sys.path.insert(0, str(R))


def run():
    import construct as C
    import native
    old = read(R / "prior/WORD.json.gz")
    _, frames, _ = source()
    geometry = SOURCE.Geometry(frames)
    cancellations = read(R / "CANCELLATIONS.json")
    rewrites, paths = read(R / "REWRITES.json"), read(R / "PATHS.json")
    word = C.cancel(old, cancellations)
    cancelled = deepcopy(word)
    profiles = []
    previous = C.paid(old)
    for witness in rewrites:
        word = C.emit(word, C.conjugate(word, witness), paths, geometry)
        paid = C.paid(word)
        delta = {k: paid[k] - previous[k] for k in set(paid) | set(previous)
                 if paid[k] != previous[k]}
        need(delta in [{}, {1: 1, 2: -2, 3: 1}], "Neutral or strictly positive concavity step")
        profiles.append(delta)
        previous = paid
    need(len(rewrites) == 45 and sum(bool(p) for p in profiles) == 2,
         "Two productive and43 neutral conjugations")
    need(C.paid(word) == {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10},
         "Exact final paid histogram")
    physical = dict(final=word["start"], start=word["final"])
    stats = native.replay(physical, frames, word["records"], set(word["owned"]))
    moduli = [native.replay(physical, frames, word["records"], set(word["owned"]), m)["native_modulus"]
              for m in [101, 10201]]
    cuts = load("conjugation_next_cuts", R / "prior/construct.py")
    need(not cuts.find(word), "No further split in the common-frame helper-pivot domain")
    rejected = []
    bad = deepcopy(rewrites[0])
    bad["candidate"]["changes"][0]["extra"][2] = 90
    try:
        C.conjugate(cancelled, bad)
    except ValueError:
        rejected.append("wrong_conjugation_source")
    else:
        raise ValueError("Wrong conjugation source accepted")
    bad = deepcopy(word)
    ix = next(i for i, e in enumerate(bad["records"]) if e[0] == "Q")
    bad["records"][ix][4] = 8
    try:
        native.replay(physical, frames, bad["records"], set(word["owned"]))
    except ValueError:
        rejected.append("invalid_native_rank")
    else:
        raise ValueError("Invalid native rank accepted")
    need(word["start"] == old["start"] and word["final"] == old["final"]
         and word["owned"] == old["owned"], "Unchanged target and owned contracts")
    put("MATCHER.json", read(R / "prior/MATCHER.json"))
    put("WORD.json.gz", word)
    result = dict(status="PASS_G20_CONJUGATION_ALL685_COLUMNS", stats=stats,
                  native_moduli=moduli, cancellation_pairs=sum(len(x["pairs"]) for x in cancellations),
                  conjugations=len(rewrites), productive_conjugations=2,
                  local_paid_delta={1: 2, 2: -4, 3: 2}, target_delta={},
                  remaining_common_frame_splits=0, negative_controls=rejected)
    put("LOCAL-RESULT.json", result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
