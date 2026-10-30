# SPDX-License-Identifier: Apache-2.0
"""Authenticate actual production ancestry; execute source bytes, never pyc."""
import ast
import builtins
import io
import json
import math
import tarfile
import types
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (root / row["path"]).read_bytes()
            need(sha256(raw).hexdigest() == row["sha256"], "input changed: " + row["path"])
            result[row["path"]] = raw
    return result


def member(raw, path):
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
        hits = [m for m in archive.getmembers() if m.name == path]
        need(len(hits) == 1 and hits[0].isfile(), "one regular source archive member: " + path)
        return archive.extractfile(hits[0]).read()


def module(name, raw, imports=None):
    result = types.ModuleType(name)
    imports = {} if imports is None else imports
    def importing(key, *args, **kwargs):
        if key in imports:
            return imports[key]
        raise ImportError("undeclared source import: " + key)
    result.__dict__["__builtins__"] = dict(vars(builtins), __import__=importing)
    exec(compile(raw, "<authenticated:" + name + ">", "exec"), result.__dict__)
    return result


def extract(raw, names, namespace):
    tree = ast.parse(raw)
    nodes = [node for node in tree.body if getattr(node, "name", None) in names]
    need({node.name for node in nodes} == set(names), "exact source extraction")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "<authenticated source slice>", "exec"), namespace)
    return namespace


def load():
    inputs = authenticate()
    raw = inputs["research/physical-gaussian-leaf/inputs/pr3087.tar"]
    ancestry = []
    for path in ("inputs/pr3055.tar", "inputs/pr2899.tar", "inputs/pr2809.tar"):
        raw = member(raw, path)
        ancestry.append({"member": path, "sha256": sha256(raw).hexdigest()})
    prefix = "inputs/pr2753/predecessor/"
    low_raw = member(raw, prefix + "vendor/low_codes.py")
    catalogue_raw = member(raw, prefix + "catalogue.py")
    routes_raw = member(raw, prefix + "vendor/routes.py")
    oracle_raw = member(raw, prefix + "vendor/oracle.py")
    pairs = ((low_raw, "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/low_codes.py"),
             (catalogue_raw, "research/selected-bit-node/catalogue.py"),
             (routes_raw, "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/routes.py"),
             (oracle_raw, "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/oracle.py"))
    for value, path in pairs:
        need(value == inputs[path], "production archive agrees with declared source: " + path)
    words = module("original_words", member(raw, prefix + "vendor/words.py"))
    old = module("original_low_codes", low_raw, {"math": math, "words": words})
    oracle = module("original_oracle", oracle_raw, {"math": math, "words": words})
    # Extract two complete source definitions; no payload engine or stub is run.
    env = {"dataclass": dataclass, "Fraction": Fraction, "need": words.need,
           "__name__": __name__, "__builtins__": dict(vars(builtins),
           __import__=lambda name, *a, **k: oracle if name == "oracle" else builtins.__import__(name, *a, **k))}
    extract(routes_raw, {"Route", "compile_route"}, env)
    tree = ast.parse(catalogue_raw)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Catalogue")
    low = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "low_classes")
    low_env = {}
    exec(compile(ast.Module(body=[low], type_ignores=[]), "<original Catalogue.low_classes>", "exec"), low_env)
    return old, env["compile_route"], low_env["low_classes"], ancestry

OLD, compile_route, low_classes, ANCESTRY = load()
