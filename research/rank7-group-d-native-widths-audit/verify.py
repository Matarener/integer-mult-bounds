# SPDX-License-Identifier: Apache-2.0
"""Group D native residual / wrapper widths and T74 owner join; no STAGE-PRICES margins."""

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import invoice
import native
from common import ENTRANCE, HELPERS, PACKAGE, authenticate, data, decode, require


def compute():
    blobs = authenticate()
    words = {tag: data(blobs, f"data/WORD-{tag}.json.gz") for tag in ("base", "extra")}
    profiles = {tag: word["report"]["local_profile"] for tag, word in words.items()}
    native_results = {}
    for tag in words:
        with tempfile.TemporaryDirectory(prefix="group-d-native-") as work:
            native_results[tag] = native.audit(blobs, tag, Path(work))
    result = {"schema_version": 1, "status": "PASS_GROUP_D_NATIVE_WIDTHS",
              "native": native_results,
              "invoice": invoice.audit(blobs, words, profiles)}
    names, widths = invoice.widths(words["base"])
    joins = {}
    for tag, record in native_results.items():
        joins[tag] = {}
        for h in HELPERS:
            binding = record["bindings"][str(h)]["forward"]
            key = binding["recipe_key"]
            rank = record["residuals"][key]["rank"]
            require(rank == widths[names.index(h)] and
                    binding["compact_helper"] == 224 + names.index(h), "native-to-owner width join")
            joins[tag][str(h)] = {"helper_index": names.index(h), "native_pair": key, "width": rank}
    result["native_to_owner_join"] = joins
    # Headline native facts only; do not register STAGE-PRICES guide margins here.
    ranks = [joins["base"][str(h)]["width"] for h in HELPERS]
    require(ranks == [6, 6, 6, 6], "emitted residual widths 6/6/6/6")
    require(result["invoice"]["group_placements"] == 2664, "T74 fill places group D 2664 times")
    for tag, record in native_results.items():
        require(set(record["residuals"]) >= {joins[tag]["454"]["native_pair"]},
                "entering residual class")
        require(all(record["bindings"][str(h)]["forward"]["entrance"] == ENTRANCE
                    for h in HELPERS), "entering helpers at span(51)")
        require(all(joins[tag][str(h)]["native_pair"] == joins[tag]["454"]["native_pair"]
                    for h in HELPERS), "shared group-D residual pair")
    require(authenticate() == blobs, "source stability during replay")
    return decode(json.dumps(result).encode())


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = compute()
    if sys.argv[1:]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(decode((PACKAGE / "RESULT.json").read_bytes()) == result, "deterministic receipt")
        joins = result["native_to_owner_join"]["base"]
        pairs = ",".join(f'{h}:{joins[str(h)]["native_pair"]}' for h in HELPERS)
        print(result["status"]
              + f" providers=2 helpers=4 residual_widths=6,6,6,6 pairs={pairs}"
              + " placements=2664 adapter_pinned both_orientations no_new_kappa")


if __name__ == "__main__":
    main()
