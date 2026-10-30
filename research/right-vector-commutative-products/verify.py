#!/usr/bin/env python3
"""Fresh full BFS and separate projective/word replay, with exact typed data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def load(name, file):
    spec = importlib.util.spec_from_file_location(name,HERE/file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def compare(actual, expected):
    require(canonical(actual) == canonical(expected), "full typed regenerated payload differs")


def main():
    pins = json.loads((HERE/"SOURCE-PINS.json").read_text())
    for row in pins["files"]:
        raw = (HERE/row["path"]).read_bytes()
        require(len(raw)==row["bytes"],"source size")
        require(hashlib.sha256(raw).hexdigest()==row["sha256"],"source SHA256")
        require(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==row["git_blob"],"source Git blob")
    bfs = load("paid_bfs","engine.py").run()
    oracle = load("projective_oracle","oracle.py").run()
    compare(bfs,json.loads((HERE/"EXPECTED-BFS.json").read_text()))
    compare(oracle,json.loads((HERE/"EXPECTED-ORACLE.json").read_text()))
    key = lambda row: canonical(row["components"])
    bm = {key(row):(row["cost"],row["delta"]) for row in bfs["records"]}
    om = {key(row):(row["cost"],row["delta"]) for row in oracle["records"]}
    require(len(bm)==len(om)==216 and bm==om,"complete cost/delta cross-engine agreement")
    # These mutations exercise evidence scope/type boundaries rather than
    # asserting that a checksum alone is a mathematical certificate.
    for changed in [dict(bfs,target_count=215),dict(bfs,scratch_roles=False),dict(bfs,records=bfs["records"][:-1])]:
        try:
            compare(changed,bfs)
        except ValueError:
            pass
        else:
            raise ValueError("typed evidence corruption accepted")
    payload = dict(status="PASS_RIGHT_VECTOR_COMMUTATIVE_PRODUCTS",targets=216,
                   cost_delta_histogram=bfs["cost_delta_histogram"],
                   source_inputs=len(pins["files"]),bfs_checks=bfs["checks"],
                   bfs_controls=bfs["controls"],oracle_controls=oracle["controls"],
                   bfs_full_payload_sha256=hashlib.sha256(canonical(bfs).encode()).hexdigest(),
                   oracle_full_payload_sha256=hashlib.sha256(canonical(oracle).encode()).hexdigest(),
                   prime_fields=[r["p"] for r in oracle["prime_witnesses"]],
                   projective_pairs=sum(r["projective_pairs"] for r in oracle["prime_witnesses"]),
                   first_column_triples_F3=oracle["first_column_triples_F3"],
                   literal_upper_word_matrices=oracle["upper_word_matrices"],
                   canonical_cost=3,canonical_delta=2,typed_evidence_controls=3,
                   finite_scope="complete invertible F2^3 metric plus listed prime-field witnesses; quantified proof is separate",
                   physical_costs="unknown",new_kappa=None)
    print(canonical(payload))


if __name__ == "__main__":
    main()
