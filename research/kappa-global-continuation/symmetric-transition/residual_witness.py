#!/usr/bin/env python3
"""Exact actual-route witness against free constant-D cancellation.

Also checks the eight Gaussian zero-port invariants that may inform a consumer.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from pathlib import Path
import json
import transition as t


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--followup", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, required=True)
    a = ap.parse_args()
    src = a.followup.resolve()
    c = t.module(src / list(t.PINS)[0], "witness_bound_core", list(t.PINS.values())[0])
    s = t.module(src / list(t.PINS)[1], "witness_bound_symmetric", list(t.PINS.values())[1])
    inp = src / "artifact/recovered-involutory/modern-source/inputs"
    t.need(t.digest(inp / "NATIVE-RECEIPT.json") == c.NATIVE_RECEIPT_SHA, "native receipt pin")
    receipt = t.read(inp / "NATIVE-RECEIPT.json")
    routes = t.read(a.evidence / "ROUTES.json.gz")
    parent = t.read(a.evidence / "RESULT.json")
    t.need(parent["status"] == "PASS_LITERAL_TWO_CALL_AND_NINE_STAGE_ZERO_PORT_GEOMETRY", "required transition receipt")
    import gzip
    from hashlib import sha256
    t.need(sha256(gzip.decompress((a.evidence / "ROUTES.json.gz").read_bytes())).hexdigest() == parent["routes_payload_sha256"],
           "actual routed transition payload")
    out = {"status": "PASS_ACTUAL_ROUTE_RESIDUAL_WITNESS_AND_ZERO_PORT_INVARIANTS", "providers": {}}
    for name, item in receipt["providers"].items():
        loc = inp / "native-cache" / item["word_sha256"] / "local"
        for basename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            t.need(t.digest(loc / basename) == item["complete_native_files"]["local/" + basename], "actual provider pin")
        word, programs = t.read(loc / "CANONICAL-WORD.json.gz"), t.read(loc / "LOCAL-PROGRAMS.json.gz")
        D = t.code_matrix(s, c, word, programs)
        for i in range(8):
            row = D[120 + i].copy()
            s.add(row, D[112 + i], s.G(0, -2))
            t.need(row == {120 + i: s.G(1), 112 + i: s.G(0, -2)}, "Gaussian zero-port invariant")
        p = 112
        rho_p = routes[f"1:{p}"]["owner_right_matrix_columns"]
        operators = {}
        contributions = []
        for j, coefficient in D[p].items():
            if p not in D[j]:
                continue
            a_ = coefficient * D[j][p]
            rho_j = routes[f"1:{j}"]["owner_right_matrix_columns"]
            cols = tuple(t.act(rho_p, col) for col in rho_j)
            operators[cols] = operators.get(cols, s.G()) + a_
            contributions.append(dict(intermediate_port=j, coefficient=a_.data(), identity_route=cols == t.AXES))
        operators = {cols: q for cols, q in operators.items() if q}
        at_identity = operators.get(t.AXES, s.G())
        t.need(at_identity == s.G(-55), "actual delta-cover diagonal witness")
        t.need(at_identity != s.G(1), "constant-D cancellation rejected")
        original_terms = [x for x in contributions if x["intermediate_port"] < 112]
        t.need(len(original_terms) == 56 and all(x["coefficient"] == s.G(1).data() and not x["identity_route"] for x in original_terms),
               "all56 positive actual nonidentity routes")
        out["providers"][name] = dict(
            input="X0 port112 is delta at the identity orthogonal cover class; all other normalized data and helpers zero",
            query="Y0 port112 immediately after stage1, equivalently signed X0 port112 after the complete baseline bridge/controller pattern",
            actual_two_call_coefficient_at_identity=at_identity.data(), required_ordinary_coefficient=s.G(1).data(),
            difference=s.G(-56).data(), intermediate_terms=contributions,
            distinct_actual_route_operators=len(operators),
            complete_controller_argument="After F0 and B1, X0=0 and Y0=D1D0 X0_initial. The first bridge writes -Y0 intoY1; F2 leavesY0 unchanged becauseX0=0; the next bridge cancelsY1. Later pairs see zero. The final signed exchange therefore still carriesD1D0.",
            zero_port_invariants=[f"T_{i} - 2i S_{i}" for i in range(8)],
            invariant_scope="An invariant is not a complete decoder; the data scatter uses stage- and port-dependent routes.")
    (a.evidence / "RESIDUAL-WITNESS.json").write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(out["status"], flush=True)


if __name__ == "__main__":
    main()
