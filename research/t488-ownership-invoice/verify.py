#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Invoice check: PR3653 published T488 profile versus literal helper outputs.

Does not import or rerun the composition's owner expander. Helper output widths
are recomputed from canonical frame ranks. The predecessor invoice is the
owner certificate's published profile, not a fresh 1,791,936-row sum.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"

# File bytes of PR #3653 head 607a09ff441c79b215a8127a81f4cc70021d0d9b.
PINS = {
    "checked-base-CANONICAL-WORD.json.gz":
        "ba1e3767f52c849c49d7d3852b879d9562265f1f51d15ca40421c51cae0aae6a",
    "checked-extra-CANONICAL-WORD.json.gz":
        "f30605f35030460f18b053dbd6031e862bf3c6661141d481d54ffdc1e8d1ad01",
    "PROVIDERS.json":
        "d96f2798024ab83edbb8848b62c425992aec182f1f24ef46bb8286dd390618c2",
    "CANDIDATE.json":
        "fbdda845beac5bba9baa4b1b8c8f596e98f70b59e1d60ebf4f4d3e8758631bfd",
}
PROVIDER_OF = {
    "checked-base-CANONICAL-WORD.json.gz": "gauge44",
    "checked-extra-CANONICAL-WORD.json.gz": "extra",
}
PUBLISHED = {1: 10817496, 2: 3179808, 3: 1024434, 4: 447984,
             5: 94794, 8: 35136, 48: 186782}
NEW_LOCAL = {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}
CALLS = 4392
REPLICAS = 488
HELPERS = 408
HELPER0 = 224


def need(ok, message):
    if not ok:
        raise SystemExit(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def rank(masks):
    pivots = {}
    for mask in masks:
        while mask:
            bit = mask.bit_length() - 1
            if bit in pivots:
                mask ^= pivots[bit]
            else:
                pivots[bit] = mask
                break
    return len(pivots)


def load_pinned():
    blobs = {}
    for name, digest in PINS.items():
        data = (INPUTS / name).read_bytes()
        need(sha256(data) == digest, "pin mismatch " + name)
        blobs[name] = data
    return blobs


def ints(mapping):
    return {int(key): value for key, value in mapping.items()}


def output_widths(word):
    frames = word["frames"]
    start = word["start"]
    final = word["final"]
    need(len(start) == len(final) == HELPER0 + HELPERS, "register table length")
    widths = []
    for helper in range(HELPERS):
        before = rank(frames[start[HELPER0 + helper]])
        after = rank(frames[final[HELPER0 + helper]])
        need(after >= before, "helper output rank fell")
        widths.append(after - before)
    return widths


def frame_rank(word, index):
    return rank(word["frames"][index])


def invoice(candidate, local):
    old_local = ints(candidate["local_profile"])
    old_profile = ints(candidate["profile"])
    ranks = set(old_local) | set(local) | set(old_profile) | set(PUBLISHED)
    delta = {rank: local.get(rank, 0) - old_local.get(rank, 0) for rank in ranks}
    composed = {rank: old_profile.get(rank, 0) + CALLS * delta.get(rank, 0)
                for rank in ranks}
    composed = {rank: count for rank, count in composed.items() if count}
    idle = {}
    for rank in ranks:
        residual = composed.get(rank, 0) - CALLS * local.get(rank, 0)
        old_residual = old_profile.get(rank, 0) - CALLS * old_local.get(rank, 0)
        need(residual == old_residual, "idle residual moved at rank " + str(rank))
        if residual:
            idle[rank] = residual
    return delta, composed, idle


def controls(widths, candidate):
    bumped = list(widths)
    bumped[0] += 1
    need(bumped != widths, "width control did not change")
    bad_profile = dict(PUBLISHED)
    bad_profile[1] += 1
    _, composed, _ = invoice(candidate, NEW_LOCAL)
    need(composed != bad_profile, "profile control matched a shifted histogram")
    need(composed == PUBLISHED, "control setup lost the published profile")


def main():
    blobs = load_pinned()
    candidate = json.loads(blobs["CANDIDATE.json"])
    providers = json.loads(blobs["PROVIDERS.json"])
    need(candidate["S"] == 8 and candidate["baseT"] == 61, "replica shape")
    need(candidate["baseT"] * candidate["S"] == REPLICAS, "T488 replica count")
    need(len(candidate["order"]) * candidate["S"] == CALLS, "call count")
    old_local = ints(candidate["local_profile"])
    need(old_local == {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8},
         "predecessor local bill")

    words = {}
    boundary = None
    for name, provider_id in PROVIDER_OF.items():
        word = json.loads(gzip.decompress(blobs[name]))
        need(word["R"] == HELPERS and word["v"] == 112 and word["h"] == 9,
             "word geometry")
        need(len(word["zero_buffers"]) == 91, "zero buffers")
        need(ints(word["local_profile"]) == NEW_LOCAL, "stored local bill " + name)
        widths = output_widths(word)
        need(widths == providers[provider_id]["widths"],
             "helper output widths differ from provider " + provider_id)
        need(ints(providers[provider_id]["actual_paid_profile"]) == old_local,
             "provider paid profile is not the predecessor bill")
        words[name] = word
        indices = word["start"][HELPER0:] + word["final"][HELPER0:]
        if boundary is None:
            boundary = (word["start"], word["final"], indices)
        else:
            need(word["start"] == boundary[0] and word["final"] == boundary[1],
                 "helper entrance or final index moved")

    base, extra = (words[name] for name in PROVIDER_OF)
    mismatches = [index for index, (left, right) in enumerate(zip(base["frames"], extra["frames"]))
                  if left != right]
    need(mismatches == [300], "unexpected canonical frame difference")
    need(frame_rank(base, 300) == frame_rank(extra, 300) == 4,
         "the single internal frame change is not rank-stable")
    need(300 not in boundary[2], "changed frame is a helper boundary")

    delta, composed, idle = invoice(candidate, NEW_LOCAL)
    need(delta == {1: -2, 2: -2, 3: 2, 4: 0, 5: 0, 8: 0, 48: 0}, "local delta")
    need(composed == PUBLISHED, "composed profile is not the published histogram")
    need(idle == {1: 114192, 3: 31842, 5: 6954, 48: 186782}, "idle invoice")
    mass = sum(rank * count for rank, count in composed.items())
    need(mass == 65088 * REPLICAS == 31762944, "rank mass")
    need(896 * REPLICAS + 509 == 437757, "physical family count")
    width_mass = sum(output_widths(base))
    need(width_mass == 3279, "placed width per call")
    need(sum(rank * count for rank, count in delta.items()) == 0, "delta mass")
    controls(providers["gauge44"]["widths"], candidate)

    result = {
        "status": "PASS_T488_OWNERSHIP_INVOICE",
        "calls": CALLS,
        "replicas": REPLICAS,
        "helpers": HELPERS,
        "published_profile": composed,
        "local_delta": {1: -2, 2: -2, 3: 2},
        "idle": idle,
        "rank_mass": mass,
        "physical": 437757,
        "helper_width_matches": 2,
        "frame_mismatch_index": 300,
        "rows_regenerated": False,
        "no_new_kappa": True,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
