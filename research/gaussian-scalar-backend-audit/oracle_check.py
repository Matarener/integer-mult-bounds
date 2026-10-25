#!/usr/bin/env python3
"""Replay frozen independent scalar queries; do not write package files."""

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def main():
    sibling = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", type=Path, default=sibling / "QUERY.json")
    parser.add_argument("--expected", type=Path, default=sibling / "ORACLE-QUERY-RESULT.json")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("frozen_independent_scalar_oracle", sibling / "oracle.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load sibling frozen oracle")
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    query_document = json.loads(args.query.read_text(encoding="ascii"),
                                parse_float=oracle.reject_float,
                                parse_constant=oracle.reject_float)
    # An input-only provenance wrapper may carry metadata outside queries.
    if isinstance(query_document, dict) and "queries" in query_document:
        query_document = {"queries": query_document["queries"]}
    actual = oracle.solve_document(query_document)
    expected = json.loads(args.expected.read_text(encoding="ascii"),
                          parse_float=oracle.reject_float,
                          parse_constant=oracle.reject_float)
    if oracle.canonical(actual) != oracle.canonical(expected):
        raise RuntimeError("generated typed query results differ from frozen expected records")
    serialized = oracle.canonical(actual) + "\n"
    print(oracle.canonical({"RESULT": "PASS", "queries": len(actual["results"]),
                            "canonical_sha256": hashlib.sha256(serialized.encode("ascii")).hexdigest()}))


if __name__ == "__main__":
    main()
