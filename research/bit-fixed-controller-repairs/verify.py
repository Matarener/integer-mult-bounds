#!/usr/bin/env python3
"""Replay three fixed historical controller records from authenticated sources.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
import builtins
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import tempfile
from types import SimpleNamespace


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compile_checked(source, filename, mode):
    return builtins.compile(source, filename, mode, dont_inherit=True, optimize=0)


def recipe_tree(source):
    tree = ast.parse(source)
    matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "recipe"]
    need(len(matches) == 1, "recipe definition must be unique")
    return tree


def literal_raw_sha(source):
    nodes = [n for n in ast.parse(source).body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "RAW_SHA" for t in n.targets)]
    need(len(nodes) == 1, "original RAW_SHA binding must be unique")
    value = ast.literal_eval(nodes[0].value)
    need(isinstance(value, str) and len(value) == 64, "original RAW_SHA is not a digest")
    return value


class Frozen:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.hashes = json.loads((self.root / "FROZEN-SHA256.json").read_bytes())
        self.executed = {}
        self.compared = set()

    def raw(self, name):
        need(name in self.hashes, "unregistered frozen input: " + name)
        data = (self.root / name).read_bytes()
        need(hashlib.sha256(data).hexdigest() == self.hashes[name],
             "frozen input changed: " + name)
        return data

    def decoded(self, name):
        raw = self.raw(name)
        return gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw

    def data(self, name):
        return json.loads(self.decoded(name))

    def check_all(self):
        for name in self.hashes:
            self.raw(name)
        origins = json.loads((self.root / "ORIGINS.json").read_bytes())
        need(set(origins) == set(self.hashes), "origin and frozen inventories differ")
        for name, row in origins.items():
            need(row["sha256"] == self.hashes[name], "origin container binding differs")
            if "original_sha256" in row:
                need(hashlib.sha256(self.decoded(name)).hexdigest() == row["original_sha256"],
                     "compressed original bytes changed: " + name)

    def functions(self, name, names, globals_):
        tree = ast.parse(self.raw(name), filename=str(self.root / name))
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        need(Counter(n.name for n in nodes) == Counter(names), "function selection changed")
        namespace = dict(globals_)
        exec(compile_checked(ast.Module(body=nodes, type_ignores=[]),
                             str(self.root / name), "exec"), namespace)
        self.executed[name] = list(names)
        return SimpleNamespace(**{name: namespace[name] for name in names})

    def module(self, name):
        namespace = {"__name__": "authenticated_review", "__file__": str(self.root / name)}
        exec(compile_checked(self.raw(name), str(self.root / name), "exec"), namespace)
        self.executed[name] = ["complete independent checker"]
        return namespace

    def compare(self, name, value):
        need(canonical(value) == canonical(self.data(name)), "complete receipt mismatch: " + name)
        self.compared.add(name)


class SourcePath:
    """Read-only logical paths whose only I/O is Frozen.raw."""
    def __init__(self, frozen, mapping, logical=""):
        self.frozen, self.mapping, self.logical = frozen, mapping, str(logical)

    def __truediv__(self, name):
        return SourcePath(self.frozen, self.mapping, str(PurePosixPath(self.logical) / name))

    def __str__(self):
        return "authenticated-source:/" + self.logical

    def read_bytes(self):
        need(self.logical in self.mapping, "undeclared historical source read: " + self.logical)
        return self.frozen.raw(self.mapping[self.logical])


def historical(frozen):
    mapping = {
        "recipe.py": "frozen/upstream/global_k.py",
        "old/recursive/BIT-THREE-ROW-INPUT.json": "frozen/geometry/MATRICES.json",
        "endpoint/expanded_sections.py": "frozen/routes/expanded_sections.py",
        "R438.json.gz": "frozen/geometry/R438.json.gz",
        "repo/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz":
            "frozen/geometry/E8.json.gz",
    }
    source = SourcePath(frozen, mapping)
    tree_api = SimpleNamespace(parse=recipe_tree, FunctionDef=ast.FunctionDef, Module=ast.Module)
    common = dict(ast=tree_api, compile=compile_checked, sha256=hashlib.sha256,
                  json=json, argparse=argparse)
    hybrid_names = ["need", "reduce_word", "inverse_word", "add", "left", "identity",
                    "serial", "recipe", "old_word", "hybrid_word", "apply", "evaluate",
                    "transpose_operator_word", "transpose_operators", "product", "receipt"]
    hybrid = frozen.functions("frozen/hybrid/closed_hybrid.py", hybrid_names,
                              dict(common, RECIPE=source / "recipe.py",
                                   PIN="20ecf2891d80b5acf18d980b2164fb44ea7faa90"))
    frozen.compare("frozen/hybrid/CLOSED-HYBRID.json", hybrid.receipt())

    ring = frozen.functions("frozen/recipe/bit_seeded_star.py",
                            ["need", "mul", "plus", "scale", "ident"], {})
    route_names = ["need", "bits", "xor", "eye", "product", "mm", "tr",
                   "eyeq", "roots_and_routes"]
    raw_sha = literal_raw_sha(frozen.raw("frozen/provenance/bit_cap_copy_local.py"))
    need(raw_sha == frozen.hashes["frozen/geometry/R438.json.gz"],
         "original R438 constant differs from frozen input")
    cap = SimpleNamespace(RAW=source / "R438.json.gz",
                          RAW_SHA=raw_sha)
    routes = frozen.functions("frozen/routes/expanded_sections.py", route_names,
                              dict(F=Fraction, json=json, gzip=gzip, sha256=hashlib.sha256,
                                   REPO=source / "repo", cap=cap))
    routes.F, routes.cap = Fraction, cap
    old_argv = sys.argv[:]
    with tempfile.TemporaryDirectory(prefix="bit-controller-historical-") as td:
        output = Path(td)
        nilpotent = frozen.functions("frozen/recipe/bit_nilpotent_recipe.py", ["rank", "main"],
                                    dict(common, SOURCE=source / "recipe.py", HERE=output,
                                         **vars(ring)))
        early = frozen.functions("frozen/hybrid/early_promotion.py", ["need", "main"],
                                 dict(argparse=argparse, json=json, gzip=gzip, sha256=hashlib.sha256,
                                      HERE=output, OLD=source / "old", ENDPOINT=source / "endpoint",
                                      source=routes))
        try:
            sys.argv = ["authenticated-historical-replay", "--write"]
            nilpotent.main()
            early.main()
        finally:
            sys.argv = old_argv
        for name, expected in [
            ("BIT-NILPOTENT-RECIPE.json", "frozen/recipe/BIT-NILPOTENT-RECIPE.json"),
            ("EARLY-PROMOTION.json", "frozen/hybrid/EARLY-PROMOTION.json"),
        ]:
            frozen.compare(expected, json.loads((output / name).read_bytes()))
    frozen.executed["frozen/upstream/global_k.py"] = ["recipe (unique nested AST definition)"]
    need(frozen.compared == {
        "frozen/hybrid/CLOSED-HYBRID.json", "frozen/hybrid/EARLY-PROMOTION.json",
        "frozen/recipe/BIT-NILPOTENT-RECIPE.json",
    }, "historical complete receipt coverage changed")
    return {"status": "PASS_THREE_COMPLETE_HISTORICAL_RECORDS",
            "compared": sorted(frozen.compared), "executed": frozen.executed}


def independent(frozen, stage):
    inputs = {
        "recipe": [
            ("--recipe-source", "frozen/upstream/global_k.py"),
            ("--historical-receipt", "frozen/recipe/BIT-NILPOTENT-RECIPE.json"),
        ],
        "hybrid": [
            ("--recipe", "frozen/upstream/global_k.py"),
            ("--matrices", "frozen/geometry/MATRICES.json"),
            ("--r438", "frozen/geometry/R438.json.gz"),
            ("--roots", "frozen/geometry/E8.json.gz"),
        ],
    }
    checker = f"frozen/reviews/{stage}/check.py"
    receipt = f"frozen/reviews/{stage}/CHECKS.json.gz"
    module = frozen.module(checker)
    old_argv = sys.argv[:]
    with tempfile.TemporaryDirectory(prefix="bit-controller-independent-") as td:
        output = Path(td) / "CHECKS.json"
        argv = ["authenticated-independent-checker"]
        for flag, name in inputs[stage]:
            frozen.raw(name)
            argv.extend([flag, str(frozen.root / name)])
        argv.extend(["--output", str(output)])
        try:
            sys.argv = argv
            module["main"]()
        finally:
            sys.argv = old_argv
        frozen.compare(receipt, json.loads(output.read_bytes()))
    need(frozen.compared == {receipt}, "independent complete receipt coverage changed")
    return {"status": "PASS_INDEPENDENT_" + stage.upper() + "_COMPLETE_RECEIPT",
            "compared": sorted(frozen.compared), "executed": frozen.executed}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", choices=["historical", "recipe", "hybrid"], required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    frozen = Frozen(Path(__file__).resolve().parent)
    if args.output:
        need(not args.output.resolve().is_relative_to(frozen.root), "output must be external")
    frozen.check_all()
    result = historical(frozen) if args.stage == "historical" else independent(frozen, args.stage)
    frozen.check_all()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
