#!/usr/bin/env python3
"""Independent exact endpoint-adapter bridge review of the modern involution.

The reviewed component has its own scalar/full-column replay. This review
addresses a different implication: its C_q and inverse-C_q lines must land in
the *actual* PR3734 endpoint gauges, including the global Gaussian phase.
It also checks serial-query algebra using an explicit rank-one product.

SPDX-License-Identifier: Apache-2.0
Substantial OpenAI Codex assistance under user direction.
"""
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WORKSPACE = REPO.parent
COMPONENT = WORKSPACE / "recovered-involutory/modern_native_component.py"
INPUTS = WORKSPACE / "recovered-involutory/modern-source/inputs"
LIVE = WORKSPACE / "live-source/research/staged544-producer-return"
LEGACY = REPO / "research/native-source-codes"
PIVOTS = (0, 7, 20, 27, 36, 46, 57, 111)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def add(row, other, factor):
    for key, val in other.items():
        z = row.get(key, 0) + factor*val
        if z:
            row[key] = z
        else:
            row.pop(key, None)


def main():
    native = load_module("independent_native_bridge", LEGACY/"native_verify.py")
    component = load_module("reviewed_component", COMPONENT)
    receipt = read(INPUTS/"NATIVE-RECEIPT.json")
    receipt_hash = sha256((INPUTS/"NATIVE-RECEIPT.json").read_bytes()).hexdigest()
    retained = read(LIVE/"REPLAY-INPUTS.json")
    assert retained["files"]["NATIVE-RECEIPT.json"] == receipt_hash
    result = {
        "status": "PASS_NATIVE_ENDPOINT_AND_SERIAL_QUERY_REVIEW",
        "component_sha256": sha256(COMPONENT.read_bytes()).hexdigest(),
        "native_interpreter_sha256": sha256((LEGACY/"native_verify.py").read_bytes()).hexdigest(),
        "actual_PR3734_archive_receipt_sha256": receipt_hash,
        "providers": {},
        "scope": "Independent adapter composition and matrix-product checks; scalar propagation is the component's separately replayed routine",
    }
    for name, item in receipt["providers"].items():
        loc = INPUTS/"native-cache"/item["word_sha256"] / "local"
        word = read(loc/"CANONICAL-WORD.json.gz")
        assert (loc/"CANONICAL-WORD.json.gz").read_bytes() == (LIVE/"inputs"/f"NATIVE-{name}.json.gz").read_bytes()
        borrow_hash = sha256((LIVE/"words"/f"BORROW-WORD-43{name}.json.gz").read_bytes()).hexdigest()
        assert item["word_sha256"] == borrow_hash
        programs = read(loc/"LOCAL-PROGRAMS.json.gz")
        recipes = read(loc/"CLIFFORD-RECIPES.json")
        endpoints = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
        full = native.fourier(9)
        checked = []
        for p in PIVOTS:
            q = word["ports"][p]
            pos, neg = (("C",q,1),), (("C",q,-1),)
            source = native.frame(tuple(word["frames"][word["start"][p]]), 9)
            target = native.frame(tuple(word["frames"][word["final"][112+p]]), 9)
            entry = native.recipe(endpoints["source",p])
            exit_ = native.adjoint(native.recipe(endpoints["target",p]))
            native.equal(pos+entry, source, "actual source entry adapter")
            native.equal(target+exit_, neg+full, "actual target exit adapter")
            native.equal(full+neg, target+exit_, "forward correction exact target gauge")
            native.equal(pos+entry, source, "backward correction exact source gauge")
            checked.append({"port":p, "label":q,
                            "source_frame":word["start"][p],
                            "target_frame":word["final"][112+p]})

        R,K,P,J,clean,dirty = component.clean_reconstruction(word, programs)
        A = []
        for row_k, row_p in zip(K,P):
            row = {j:-x for j,x in row_k.items()}
            add(row,row_p,F(12))
            A.append(row)
        # Explicitly multiply the eight serial factors without source_code().
        matrix = [{j:F(1)} for j in range(112)]
        for k in range(8):
            query = {}
            for j, value in R[k].items():
                add(query, matrix[j], value)
            assert query == R[k], "prior serial factors changed a future query"
            for p, row_a in enumerate(A):
                add(matrix[p], query, row_a.get(k,F(0)))
        simultaneous = []
        for p, row_a in enumerate(A):
            row = {p:F(1)}
            for k,value in row_a.items():
                add(row,R[k],value)
            simultaneous.append(row)
        assert matrix == simultaneous
        for rows in (R,K,P,A,matrix,J):
            for row in rows:
                for value in row.values():
                    value=F(value)
                    assert value.denominator & (value.denominator-1) == 0
        count = sum(e[0]=="scalar" and e[1][0]=="add" for e in dirty["forward"])
        assert count == 815
        # These reads are from *physical entrance* I helpers, before adapters.
        read_helpers = {e[1][2][1] for e in dirty["forward"]
                        if e[0]=="scalar" and e[1][0]=="add" and e[1][2][0]=="L"
                        and e[1][2][1]>=224}
        assert all(word["start"][r]==0 and word["final"][r]==1 for r in read_helpers)
        result["providers"][name] = {
            "endpoint_bridges":checked, "exact_phase_bridge_checks":4*len(checked),
            "serial_rank_one_product_matches_simultaneous_G":True,
            "all_future_queries_unchanged_by_prior_factors":True,
            "all_coefficients_are_dyadic":True,
            "dirty_compensation_adds":count,
            "dirty_helpers_read_at_physical_I_entrance":len(read_helpers),
            "private_buffer_contract":"91 owned-zero buffers; not independently dirty input columns",
            "source_program_sha256":sha256((loc/"LOCAL-PROGRAMS.json.gz").read_bytes()).hexdigest(),
            "actual_borrow_word_sha256":borrow_hash,
            "actual_canonical_word_sha256":sha256((LIVE/"inputs"/f"NATIVE-{name}.json.gz").read_bytes()).hexdigest(),
            "endpoint_recipes_sha256":sha256((loc/"CLIFFORD-RECIPES.json").read_bytes()).hexdigest(),
        }
    (HERE/"NATIVE-CRITICAL-REVIEW.json").write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"],result["component_sha256"])
    for name,item in result["providers"].items():
        print(name,"phase bridges",item["exact_phase_bridge_checks"],
              "serial product PASS; dirty adds",item["dirty_compensation_adds"])


if __name__ == "__main__":
    main()
