# SPDX-License-Identifier: Apache-2.0
"""Group B native residual / wrapper widths and T74 owner join; no STAGE-PRICES margins."""

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import invoice
import native
from common import HELPERS, PACKAGE, authenticate, data, decode, require


def compute():
    blobs = authenticate()
    words = {tag: data(blobs, f"data/WORD-{tag}.json.gz") for tag in ("base", "extra")}
    profiles = {tag: word["report"]["local_profile"] for tag, word in words.items()}
    native_results = {}
    for tag in words:
        with tempfile.TemporaryDirectory(prefix="group-b-native-") as work:
            native_results[tag] = native.audit(blobs, tag, Path(work))
    result = {"schema_version": 1, "status": "PASS_GROUP_B_NATIVE_WIDTHS",
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
    require(ranks == [7, 6, 6, 6, 6], "emitted residual widths 7/6/6/6/6")
    require(result["invoice"]["group_placements"] == 3330, "T74 fill places group B 3330 times")
    for tag, record in native_results.items():
        require(set(record["residuals"]) >= {
            joins[tag]["299"]["native_pair"], joins[tag]["448"]["native_pair"]},
                "cold and entering residual classes")
        require(record["bindings"]["299"]["forward"]["entrance"] == [], "helper299 cold entrance")
        require(all(record["bindings"][str(h)]["forward"]["entrance"] == [51]
                    for h in HELPERS[1:]), "entering helpers at span(51)")
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
              + f" providers=2 helpers=5 residual_widths=7,6,6,6,6 pairs={pairs}"
              + " placements=3330 adapter_pinned both_orientations no_new_kappa")


if __name__ == "__main__":
    main()
