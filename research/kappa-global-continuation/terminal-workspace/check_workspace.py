#!/usr/bin/env python3
"""Finite terminal query lifetimes within the already counted91 private fields.

No new productive field is reserved. Whole-size field hosting and precision
remain inherited; the primitive query/image interfaces are priced separately.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--followup", type=Path, required=True)
    ap.add_argument("--continuation", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    inp = args.followup/"artifact/recovered-involutory/modern-source/inputs"
    receipt_path = inp/"NATIVE-RECEIPT.json"
    need(hashlib.sha256(receipt_path.read_bytes()).hexdigest() ==
         "7ddf3f80b2fa61d1ab12035da9ef1c95d43f76077df819d7683144d7862a3f93", "native source receipt")
    receipt = read(receipt_path)
    transition = args.continuation/"symmetric-transition/evidence"
    alternating = read(transition/"ALTERNATING-RESULT.json")
    providers = {}
    buffer_order = None
    for name, provider in receipt["providers"].items():
        local = inp/"native-cache"/provider["word_sha256"]/"local"
        word_path = local/"CANONICAL-WORD.json.gz"
        need(hashlib.sha256(word_path.read_bytes()).hexdigest() == provider["complete_native_files"]["local/CANONICAL-WORD.json.gz"], "word source binding")
        word = read(word_path)
        buffers = word["zero_buffers"]
        need(len(buffers) == len(set(buffers)) == 91, "actual91 distinct owned buffers")
        need(buffer_order is None or buffer_order == buffers, "providers use same private bank indexing")
        buffer_order = buffers
        path = transition/f"ALTERNATING-PROGRAMS-{name}.json.gz"
        payload = gzip.decompress(path.read_bytes())
        need(hashlib.sha256(payload).hexdigest() == alternating["providers"][name]["emitted_payload_sha256"], "fresh alternating provider payload binding")
        lifetimes = {}
        for orientation, program in json.loads(payload).items():
            live, seen = set(), Counter()
            peak = 0
            for index, event in enumerate(program):
                if event[0] != "zero_buffer":
                    continue
                _, operation, role = event
                need(role in buffers, "actual private buffer role")
                if operation == "alloc":
                    need(role not in live, "no overlapping local private lifetime")
                    live.add(role)
                    seen[role] += 1
                    peak = max(peak, len(live))
                else:
                    need(operation == "free" and role in live, "matching local private release")
                    live.remove(role)
            need(not live and set(seen) == set(buffers), "all91 buffers released at local exit")
            lifetimes[orientation] = {"allocated_distinct": len(seen), "peak_active": peak,
                                      "released_at_exit": 91,
                                      "zero_value_binding": "The source-bound alternating local replay separately verifies every C/Z output is exactlyzero on all632 live basis columns."}
        providers[name] = {"word_sha256": provider["word_sha256"], "local_lifetimes": lifetimes}
    invoice = read(args.continuation/"invoice-analysis/evidence/RESULT.json")["m73_literal_allocation"]
    productive = invoice["productive_candidate"]
    zbase = productive+376+8
    mapping = [{"query": 8*stage+k, "stage": stage, "mode": k,
                "logical_private_buffer": ["Z", buffer_order[8*stage+k]],
                "physical_family": zbase+8*stage+k} for stage in range(9) for k in range(8)]
    need(len({x["physical_family"] for x in mapping}) == 72, "injective query workspace map")
    need(all(productive <= x["physical_family"] < invoice["physical_family_upper"] for x in mapping), "private fields do not withdraw productive outputs")
    need(zbase+91+2 == invoice["physical_family_upper"], "same conservatively counted family stock")
    # All terminal replicas run after local and idle recursive work; the same
    # private family addresses are released and reused after every terminal.
    epochs = [{"replica": r, "begin_after": "all local and idle child calls complete" if r == 0 else f"terminal replica{r-1} releases all72 query fields",
               "allocated_query_fields": 72, "release_after": "scatter and72 admitted owned-clear operations"} for r in range(360)]
    clears = [["scalar", ["clear", ["C", j]], 1] for j in range(72)]
    need(len(clears) == 72 and all(c[1][1][1] == j for j, c in enumerate(clears)), "explicit owned-clear word")
    # Exercise the retained interpreter, not just a locally asserted grammar.
    # Every C_j is first filled with an arbitrary nonzero live basis column.
    grammar_path = args.followup/"artifact/recovered-involutory/modern_native_component.py"
    spec = importlib.util.spec_from_file_location("terminal_owned_clear_grammar", grammar_path)
    grammar = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grammar)
    grammar_word = {"start": [1], "final": [1], "frames": [[], [0]], "zero_buffers": []}
    nonzero_queries = [["scalar", ["copy", ["C", j], ["L", 0]], 1] for j in range(72)]
    grammar_profile = grammar.core_frame_check(grammar_word, nonzero_queries+clears)
    cleared_state = grammar.replay(nonzero_queries+clears, n=1)
    need(not grammar_profile and all(not cleared_state["C", j] for j in range(72)),
         "retained native grammar accepts and exactly erases72 arbitrary owned FULL queries")
    need(cleared_state["L", 0] == {(0, ()): F(1)}, "owned erasure preserves borrowed live input")
    clear_bill = grammar.scalar_bill(clears)
    need(clear_bill == {"real_primitives": 144, "macros": {"clear": 72}}, "source-counted72 owned clears")
    raw_pre = F(invoice["rank_mass"], 360)
    normalizer = F(invoice["raw_normalizer"], 360)
    need(raw_pre == 74368 and normalizer == 74752 and raw_pre+896-normalizer == 512, "FULL fallback raw rejection")
    result = {"status": "PASS_FINITE72_QUERY_WORKSPACE_WITH_EXISTING91_PRIVATE_FIELDS",
        "providers": providers, "query_to_private_family": mapping,
        "terminal_epochs": epochs, "explicit_logical_owned_clear_word": clears,
        "retained_owned_clear_grammar_check": {
            "source_sha256": hashlib.sha256(grammar_path.read_bytes()).hexdigest(),
            "functions_called": ["core_frame_check", "replay", "scalar_bill"],
            "nonzero_owned_queries_erased": 72, "borrowed_live_input_preserved": True,
            "new_recursive_children": grammar_profile,
            "owned_clear_scalar_bill": clear_bill,
            "scope": "Direct retained-interpreter check on72 owned C labels in a common FULL frame; physical labels are separately bound to the91-bank lifetime map."},
        "peak_terminal_queries": 72, "counted_private_zero_families": 91,
        "new_physical_families": 0, "withdrawn_productive_families": 0,
        "physical_query_interval": [zbase, zbase+71], "counted_zero_bank_interval": [zbase, zbase+90],
        "owned_clear_scope": "Bind the C query labels injectively to the displayed released Z families. The retained scalar grammar admits clear on owned scratch at frameFULL. Erasing borrowed arbitrary inputs is not authorized or used. An optional reversible erasure pass may replace these clears.",
        "full_gauge_fallback": {"flatten_original_X_fields": 448, "unflatten_original_X_fields": 448,
            "recursive_profile": {"1": 896}, "raw_invoice_with_fallback": 75264,
            "raw_normalizer": 74752, "raw_excess": 512,
            "price_conclusion": "Fails already at a=0, hence every positive a, because all positive child ranks are below73.",
            "native_middle": "After flattening all1024 fields have commonFULL73. Inplace source owner maps, Gaussian additions and inverse source maps implement each gather/scatter/Gram summand, restoring temporarily viewed sources. Route symbols must be expressed using the correctly conjugated FULL-basis owner maps, with the retained dual/inverse-transpose convention; normalized-coordinate P labels are not silently reused in another gauge. The retained commonFULL owner-map commutation is reused."},
        "limitations": ["Finite private capacity/lifetime binding, not a new all-size physical-hosting theorem.",
            "72 live queries do not imply72H8 children,9H8 children, or any other recursive tariff.",
            "A cheaper physical V or U implementation must provide its native gauge maps and exact child profiles.",
            "No new precision, tape, recursive-hosting or multiplication theorem is established."]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+"\n")
    print(result["status"])
    print("Q[0..71] physical families", zbase, "through", zbase+71, "; no extra denominator")
    print("conservative896H1 FULL fallback fails raw invoice by512 perreplica")


if __name__ == "__main__":
    main()
