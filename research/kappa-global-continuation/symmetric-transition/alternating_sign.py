#!/usr/bin/env python3
"""Native realization of A_even=[4I,8iI], A_odd=[-4I,8iI].

Conjugates actual local words by zero-port sign flips at common I/FULL
boundaries. No recursive native children are added. This is not a consumer.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import gzip
import json
import transition as t


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--followup", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    a = ap.parse_args()
    src = a.followup.resolve()
    c = t.module(src / list(t.PINS)[0], "alternating_bound_core", list(t.PINS.values())[0])
    s = t.module(src / list(t.PINS)[1], "alternating_bound_symmetric", list(t.PINS.values())[1])
    inp = src / "artifact/recovered-involutory/modern-source/inputs"
    t.need(t.digest(inp / "NATIVE-RECEIPT.json") == c.NATIVE_RECEIPT_SHA, "native receipt pin")
    receipt = t.read(inp / "NATIVE-RECEIPT.json")
    symroot = src / "artifact/recovered-involutory/symmetric-extension-review/symmetric-extended-results"
    t.need(t.digest(symroot / "RESULT.json") == t.SYMMETRIC_RESULT_SHA, "frozen symmetric receipt")
    baseline = t.read(symroot / "RESULT.json")
    transition_receipt = t.read(a.evidence / "RESULT.json")
    routes = t.read(a.evidence / "ROUTES.json.gz")
    t.need(sha256(gzip.decompress((a.evidence / "ROUTES.json.gz").read_bytes())).hexdigest() == transition_receipt["routes_payload_sha256"], "bound transition routes")
    out = dict(status="PASS_NATIVE_ALTERNATING_ZERO_PORT_SIGNS", verifier_sha256=t.digest(Path(__file__)),
        providers={}, changed_stages=[1, 3, 5, 7],
        local_alphabet="A_even=[4I8,8iI8], A_odd=[-4I8,8iI8]",
        scope="Actual literal local alternate with existing phase/data geometry. Record inversion and data restoration are separate obligations.")
    for name, item in receipt["providers"].items():
        loc = inp / "native-cache" / item["word_sha256"] / "local"
        for basename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            t.need(t.digest(loc / basename) == item["complete_native_files"]["local/" + basename], "provider source pin")
        word, original = t.read(loc / "CANONICAL-WORD.json.gz"), t.read(loc / "LOCAL-PROGRAMS.json.gz")
        raw = gzip.decompress((symroot / f"PROGRAMS-{name}.json.gz").read_bytes())
        t.need(sha256(raw).hexdigest() == t.SYMMETRIC_PROGRAM_PAYLOAD_SHA, "original literal symmetric payload")
        programs = json.loads(raw)
        info = baseline["providers"][name]
        X = tuple(range(112)) + tuple(info["source_helper_ports"])
        Y = tuple(range(112, 224)) + tuple(info["target_helper_ports"])
        flips = X[112:120] + Y[112:120]
        pre = [s.gate_scale(r, s.G(-1), 0) for r in flips]
        post = [s.gate_scale(r, s.G(-1), 1) for r in flips]
        changed = {orientation: pre + events + post for orientation, events in programs.items()}
        D = t.code_matrix(s, c, word, original)
        sign = lambda p: -1 if 112 <= p < 120 else 1
        D_odd = [{j: value * sign(i) * sign(j) for j, value in row.items()} for i, row in enumerate(D)]
        t.need(s.product(D_odd, D_odd) == [{i: s.G(1)} for i in range(128)], "odd involution")
        t.need(all({j: value for j, value in D_odd[i].items() if j < 112} ==
                   {j: value for j, value in D[i].items() if j < 112} for i in range(112)), "unchanged required original-data block")
        _, _, _, widths, checks = t.local_checks(s, c, word, changed, D_odd, info)
        for orientation in programs:
            old_bill = s.gaussian_bill(programs[orientation], c)["real_primitives_upper"]
            new_bill = checks[orientation]["scalar_invoice"]["real_primitives_upper"]
            t.need(new_bill - old_bill == 64, "exact64-real-primitive alternation bill")
            t.need(checks[orientation]["scalar_prefix_log2"] <= 192, "retained scalar cap")
        for stage in range(9):
            t.need(all(routes[f"{stage}:{112 + i}"]["owner_right_matrix_columns"] ==
                       routes[f"{stage}:{120 + i}"]["owner_right_matrix_columns"] for i in range(8)),
                   "sign conjugation compatible with actual zero-port routes")
        # An omitted output sign must be detected on an actual promoted input.
        t.need(D_odd[112] != {j: value * sign(j) for j, value in D[112].items()},
               "effective omitted-post-sign control")
        payload_sha = t.dump_gzip(a.evidence / f"ALTERNATING-PROGRAMS-{name}.json.gz", changed)
        out["providers"][name] = dict(input_columns_per_orientation=632,
            remaining_helper_inventory=dict(sorted(widths.items())), checks=checks,
            sign_flipped_source_roles=list(X[112:120]), sign_flipped_target_roles=list(Y[112:120]),
            added_scalar_macros_per_call=32, added_real_primitives_per_call=64,
            added_recursive_native_children=0, added_native_owner_maps=0,
            nine_stage_added_real_primitives=256, emitted_payload_sha256=payload_sha,
            endpoint="F_odd(z,w)=(PDP z,w+PDP z); B_odd(z,w)=(z-w,PDP w)",
            zero_port_query_relation="For a common routed queryq: ΔS=+q, ΔT=−2i q at odd stages, versusΔS=−q,ΔT=−2i q at even stages.",
            controls_rejected=["omitted output sign"])
        print("PASS_NATIVE_ALTERNATING_SIGNS", name, "both632-column orientations;64 extra realprimitives;0 children", flush=True)
    (a.evidence / "ALTERNATING-RESULT.json").write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(out["status"], flush=True)


if __name__ == "__main__":
    main()
