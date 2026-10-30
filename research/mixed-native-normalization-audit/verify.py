#!/usr/bin/env python3
"""Independent normalization contract and real-gate mutation coverage for PR4180.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0
No native computation, supplier admission, or all-size theorem is replayed.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import copy
import gzip
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / "research/mixed-provider-admission"
RETAINED = ROOT / "research/kappa-operator-repair/late-staged-composition"
STAGES = ("native", "ledgers", "local-replay", "wrappers", "phases")
TIMED = frozenset(("CLIFFORD-REVIEW.json", "SCALAR-FRAME-AUDIT.json"))
# Independently enumerated from the two actual retained product graphs.
EDGES = (
    ("CLIFFORD-REVIEW.json", "canonical_word_sha256", "CANONICAL-WORD.json.gz"),
    ("CLIFFORD-REVIEW.json", "recipe_sha256", "CLIFFORD-RECIPES.json"),
    ("INDEPENDENT-LOCAL-REPLAY.json", "canonical_word_sha256", "CANONICAL-WORD.json.gz"),
    ("INDEPENDENT-LOCAL-REPLAY.json", "local_programs_sha256", "LOCAL-PROGRAMS.json.gz"),
    ("WARP-RECIPE-CHECKS.json", "canonical_word_sha256", "CANONICAL-WORD.json.gz"),
    ("WARP-RECIPE-CHECKS.json", "recipe_sha256", "CLIFFORD-RECIPES.json"),
)
REF_FIELDS = frozenset(field for _, field, _ in EDGES)
FILES = (
    "CANONICAL-WORD.json.gz", "CLIFFORD-RECIPES.json", "CLIFFORD-REVIEW.json",
    "FULL-WORD.json.gz", "INDEPENDENT-LOCAL-REPLAY.json", "LOCAL-CHECKS.json",
    "LOCAL-PROGRAMS.json.gz", "RESIDUAL-ADAPTERS.json", "SCALAR-FRAME-AUDIT.json",
    "WARP-RECIPE-CHECKS.json", "WRAPPER-CHECKS.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def dump(path, value, *, pretty=False, mtime=0):
    raw = json.dumps(value, sort_keys=not pretty, indent=1 if pretty else None,
                     separators=None if pretty else (",", ":"), allow_nan=True).encode()
    path.write_bytes(gzip.compress(raw, compresslevel=1, mtime=mtime)
                     if path.suffix == ".gz" else raw)


@lru_cache(maxsize=16384)
def escaped(value):
    """JSON scalar escaping, memoized only by the exact immutable string."""
    return json.dumps(value)


def canonical(value):
    """Independent structural encoder for the scientific JSON domain.

    All measured scientific numbers are integers; elapsed floats are removed.
    No predecessor encoder, normalizer, reference table, or commitment generator
    is called. Only scalar string escaping uses the standard JSON library.
    """
    if isinstance(value, dict):
        return "{" + ",".join(escaped(k) + ":" + canonical(value[k])
                               for k in sorted(value)) + "}"
    if isinstance(value, list):
        return "[" + ",".join(canonical(x) for x in value) + "]"
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    require(type(value) is str, "scientific scalar domain")
    return escaped(value)


def product_hash(value):
    return sha(canonical(value).encode())


def source_pins():
    manifest = read(HERE / "SOURCES.json")
    checked = []
    for row in manifest["files"]:
        if row.get("usage") == "input":
            path = ROOT / row["path"]
            require(path.is_file() and not path.is_symlink(), "regular source: " + row["path"])
            require(sha(path.read_bytes()) == row["sha256"], "source pin: " + row["path"])
            checked.append(row["path"])
    return checked


def oracle(native):
    """Fixed-graph, construction-based model, independent of native_outputs.py."""
    local = native / "local"
    require({p.name for p in local.iterdir()} == set(FILES), "oracle product inventory")
    require({p.relative_to(native).as_posix() for p in native.rglob("*") if p.is_file()}
            == {"STEPS.json"} | {"local/" + name for name in FILES}, "oracle file closure")
    values = {}
    for name in FILES:
        path = local / name
        require(path.is_file() and not path.is_symlink(), "oracle regular product")
        values[name] = read(path)
        require(type(values[name]) is dict, "oracle object root")
    actual_edges = {(name, key) for name, obj in values.items() for key in obj if key in REF_FIELDS}
    require(actual_edges == {(name, key) for name, key, _ in EDGES}, "oracle reference graph")
    # Reference targets are leaves of this graph: no reference or timing quotient.
    for target in {target for _, _, target in EDGES}:
        require(not (set(values[target]) & REF_FIELDS) and target not in TIMED,
                "oracle leaf target")
    result = {}
    for name, obj in values.items():
        projected = {}
        for key, val in obj.items():
            if name in TIMED and key == "seconds":
                require(type(val) in (int, float) and math.isfinite(val) and val >= 0,
                        "oracle finite nonnegative product timing")
                continue
            target = next((t for n, k, t in EDGES if (n, k) == (name, key)), None)
            if target is not None:
                require(val == sha((local / target).read_bytes()), "oracle stale reference")
                projected[key] = product_hash(values[target])
            else:
                projected[key] = val
        if name in TIMED:
            require("seconds" in obj, "oracle missing product timing")
        result[name] = product_hash(projected)
    steps = read(native / "STEPS.json")
    require(type(steps) is list and len(steps) == 5, "oracle stage count")
    for step, expected in zip(steps, STAGES):
        require(step["step"] == expected and type(step["exit_code"]) is int
                and step["exit_code"] == 0, "oracle stage projection")
    return result


@contextmanager
def actual_gate():
    """Execute pinned source bytes directly; never consult a .pyc file."""
    saved = sys.modules.get("binding")
    binding = types.ModuleType("binding")
    binding.__file__ = str(SOURCE / "binding.py")
    exec(compile((SOURCE / "binding.py").read_bytes(), binding.__file__, "exec"), binding.__dict__)
    sys.modules["binding"] = binding
    native = types.ModuleType("audit_actual_native_outputs")
    native.__file__ = str(SOURCE / "native_outputs.py")
    try:
        exec(compile((SOURCE / "native_outputs.py").read_bytes(), native.__file__, "exec"), native.__dict__)
        yield native.authenticate_native
    finally:
        if saved is None:
            sys.modules.pop("binding", None)
        else:
            sys.modules["binding"] = saved


def first_edit(value, path=()):
    """A deterministic same-type leaf edit inside a selected root field."""
    if isinstance(value, dict):
        if not value:
            return {"audit_added": 1}, path + ("audit_added",), "empty-object insertion"
        key = sorted(value)[0]
        new, changed, kind = first_edit(value[key], path + (key,))
        value[key] = new
        return value, changed, kind
    if isinstance(value, list):
        if not value:
            return [1], path + (0,), "empty-array insertion"
        new, changed, kind = first_edit(value[0], path + (0,))
        value[0] = new
        return value, changed, kind
    if type(value) is bool:
        return not value, path, "Boolean flip"
    if type(value) is int:
        return value + 1, path, "integer increment"
    if type(value) is str:
        return value + "_audit", path, "string extension"
    require(value is None, "unexpected leaf type")
    return False, path, "null replacement"


def rebind(local, objects):
    """Rewrite all six serialized references in topological order."""
    for parent in sorted({n for n, _, _ in EDGES}):
        obj = copy.deepcopy(objects[parent])
        for name, field, target in EDGES:
            if name == parent:
                obj[field] = sha((local / target).read_bytes())
        dump(local / parent, obj)


def run():
    pins = source_pins()
    commitments = read(SOURCE / "NATIVE-OUTPUTS.json")["providers"]
    require(set(commitments) == {"gauge44", "extra", "gauge44-four", "extra-four"},
            "four fixed provider commitments")
    cases = []
    providers = {}
    with actual_gate() as gate, tempfile.TemporaryDirectory(prefix="native-normalization-") as temp:
        temp = Path(temp)
        for pid, tag in (("gauge44", "base"), ("extra", "extra")):
            original = RETAINED / ("native-" + tag) / "native"
            word = RETAINED / "candidate" / ("BORROW-WORD-43" + tag + ".json.gz")
            word_sha = sha(word.read_bytes())
            require(commitments[pid]["word_sha256"] == word_sha, "honest word pin")
            products = oracle(original)
            require(products == commitments[pid]["products"], "independent commitments")
            require(gate(pid, word_sha, original) == products, "actual baseline")
            native = temp / pid
            shutil.copytree(original, native)
            local = native / "local"
            raw = {p.relative_to(native).as_posix(): p.read_bytes()
                   for p in native.rglob("*") if p.is_file()}
            objects = {name: read(local / name) for name in FILES}
            stages = read(native / "STEPS.json")
            providers[pid] = dict(products=products, root_fields=sum(map(len, objects.values())),
                                  scientific_root_fields=sum(1 for n, obj in objects.items() for k in obj
                                                            if k not in REF_FIELDS and not (n in TIMED and k == "seconds")),
                                  reference_edges=[list(e) for e in EDGES],
                                  word_sha256=word_sha)

            def restore():
                # All temporary mutations stay inside this private fixture.
                for path in sorted(native.rglob("*"), reverse=True):
                    if path.is_file() or path.is_symlink():
                        key = path.relative_to(native).as_posix()
                        if key not in raw or path.is_symlink():
                            path.unlink()
                for name, payload in raw.items():
                    path = native / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if not path.exists() or path.read_bytes() != payload:
                        path.write_bytes(payload)

            def check(name, family, mutate, expected, detail=None, *, compare_oracle=True):
                restore()
                mutate()
                try:
                    outcome = gate(pid, word_sha, native)
                except (ValueError, KeyError, FileNotFoundError) as exc:
                    status = "REJECTED"
                    reason = str(exc)
                else:
                    status = "ACCEPTED"
                    reason = None
                    require(outcome == products, "accepted products changed")
                require(status == expected, "unexpected " + status + ": " + pid + "/" + name)
                if compare_oracle:
                    try:
                        independent = oracle(native)
                    except (ValueError, KeyError, FileNotFoundError):
                        oracle_status = "REJECTED"
                    else:
                        oracle_status = "ACCEPTED" if independent == products else "REJECTED"
                    require(oracle_status == status, "oracle/gate disagreement: " + name)
                row = dict(provider=pid, name=name, family=family, result=status)
                if reason is not None:
                    # Paths in errors are fixture details, not deterministic evidence.
                    row["reason"] = reason.replace(str(native), "FIXTURE")
                if detail is not None:
                    row["detail"] = detail
                cases.append(row)

            # Mutate each scientific root field, preserving its container/type
            # where possible. Rebind every dependent reference after target edits.
            for name in FILES:
                for key in sorted(objects[name]):
                    if (name in TIMED and key == "seconds") or key in REF_FIELDS:
                        continue
                    obj = copy.deepcopy(objects[name])
                    obj[key], changed, kind = first_edit(obj[key], (key,))
                    def change(name=name, obj=obj):
                        edited = dict(objects)
                        edited[name] = obj
                        dump(local / name, obj)
                        rebind(local, edited)
                    check(name + "/" + key, "scientific-root-field", change, "REJECTED",
                          dict(path=list(changed), edit=kind))

            # The six reference edges must point to the actual serialized bytes.
            for name, key, target in EDGES:
                def stale(name=name, key=key):
                    obj = copy.deepcopy(objects[name]); obj[key] = "0" * 64
                    dump(local / name, obj)
                check(name + "/" + key, "stale-reference", stale, "REJECTED")
                def transport(target=target):
                    dump(local / target, objects[target], pretty=True, mtime=17)
                    rebind(local, objects)
                check(target + "/through/" + name, "rebound-reference-transport", transport, "ACCEPTED")

            for name in FILES:
                def add_field(name=name):
                    obj = copy.deepcopy(objects[name]); obj["audit_extra_scientific"] = 1
                    edited = dict(objects); edited[name] = obj
                    dump(local / name, obj); rebind(local, edited)
                check(name, "extra-product-field", add_field, "REJECTED")
                check(name, "missing-product", lambda name=name: (local / name).unlink(), "REJECTED")

            for name in sorted(TIMED):
                for label, value in (("zero", 0), ("fraction", 1.25), ("large", 1e100)):
                    def timing(name=name, value=value):
                        obj = copy.deepcopy(objects[name]); obj["seconds"] = value
                        dump(local / name, obj)
                    check(name + "/" + label, "allowed-product-timing", timing, "ACCEPTED")
                for label, value in (("negative", -1), ("bool", False), ("string", "0"),
                                     ("null", None), ("nan", float("nan")),
                                     ("infinity", float("inf"))):
                    def timing(name=name, value=value):
                        obj = copy.deepcopy(objects[name]); obj["seconds"] = value
                        dump(local / name, obj)
                    check(name + "/" + label, "invalid-product-timing", timing, "REJECTED")
                def missing_time(name=name):
                    obj = copy.deepcopy(objects[name]); del obj["seconds"]; dump(local / name, obj)
                check(name, "missing-product-timing", missing_time, "REJECTED")
                def nested_time(name=name):
                    obj = copy.deepcopy(objects[name]); obj["audit_nested"] = {"seconds": 0}
                    dump(local / name, obj)
                check(name, "nested-seconds-is-scientific", nested_time, "REJECTED")

            for index, stage in enumerate(STAGES):
                for kind in ("omitted", "renamed", "exit-one", "exit-bool", "exit-float"):
                    def stage_mutation(index=index, kind=kind):
                        value = copy.deepcopy(stages)
                        if kind == "omitted":
                            del value[index]
                        elif kind == "renamed":
                            value[index]["step"] += "_audit"
                        else:
                            value[index]["exit_code"] = {"exit-one": 1, "exit-bool": False,
                                                         "exit-float": 0.0}[kind]
                        dump(native / "STEPS.json", value)
                    check(stage + "/" + kind, "stage-contract", stage_mutation, "REJECTED")
            check("reversed", "stage-contract", lambda: dump(native / "STEPS.json", stages[::-1]), "REJECTED")
            check("duplicate", "stage-contract", lambda: dump(native / "STEPS.json", stages + stages[:1]), "REJECTED")
            # Execution evidence is intentionally a projection, not an event log seal.
            for label in ("minimal", "negative-time", "nan-time", "invented-provenance"):
                def projected_stage(label=label):
                    value = [{"step": s, "exit_code": 0} for s in STAGES]
                    if label != "minimal":
                        for row in value:
                            row["seconds"] = -1 if label == "negative-time" else float("nan")
                            if label == "invented-provenance":
                                row["claimed_executor"] = "synthetic audit value"
                    dump(native / "STEPS.json", value)
                check(label, "uncommitted-stage-metadata", projected_stage, "ACCEPTED")

            check("extra-local", "file-inventory", lambda: dump(local / "EXTRA.json", {}), "REJECTED")
            check("extra-outside-local", "file-inventory", lambda: dump(native / "EXTRA.json", {}), "REJECTED")
            # A same-byte symlink must still fail the regular-product predicate.
            name = "WRAPPER-CHECKS.json"
            def symlink_product():
                path = local / name; path.unlink(); path.symlink_to(original / "local" / name)
            check("symlink-product", "file-inventory", symlink_product, "REJECTED")
            def all_transport():
                for name in FILES:
                    obj = copy.deepcopy(objects[name])
                    if name in TIMED: obj["seconds"] = 0
                    # Reverse top-level key order, change whitespace and gzip headers.
                    obj = dict(reversed(list(obj.items())))
                    dump(local / name, obj, pretty=True, mtime=23)
                rebind(local, objects)
                for name in sorted(TIMED):
                    obj = read(local / name); obj["seconds"] = 0; dump(local / name, obj, pretty=True)
            check("all-products", "equivalent-serialization", all_transport, "ACCEPTED")
            restore()
            # Wrong word binding and provider identity are separate from products.
            for wrong_pid in sorted(set(commitments) - {pid}):
                try:
                    gate(wrong_pid, commitments[wrong_pid]["word_sha256"], native)
                except ValueError as exc:
                    require(str(exc) == "native scientific output commitment", "provider separation reason")
                    cases.append(dict(provider=pid, name=wrong_pid, family="cross-provider-products",
                                      result="REJECTED", reason=str(exc)))
                else:
                    raise ValueError("accepted another provider's products")
            try:
                gate(pid, "0" * 64, native)
            except ValueError as exc:
                require(str(exc) == "native commitment word binding", "word separation reason")
                cases.append(dict(provider=pid, name="wrong-word", family="word-binding",
                                  result="REJECTED", reason=str(exc)))
            else:
                raise ValueError("accepted wrong word commitment")
    require(source_pins() == pins, "source inputs unchanged after audit")
    by_family = {}
    for family in sorted({row["family"] for row in cases}):
        by_family[family] = dict(sorted(Counter(row["result"] for row in cases if row["family"] == family).items()))
    return dict(status="PASS_MIXED_NATIVE_NORMALIZATION_AUDIT", source_inputs=len(pins),
                providers=providers, cases=cases, counts=dict(sorted(Counter(row["result"] for row in cases).items())),
                by_family=by_family,
                scope="Two retained THREE providers; source/commitment and normalization boundary only. "
                      "No FOUR generation, native semantics, ordinary/outer replay, or execution-provenance claim.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="write a new deterministic receipt for review")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write_result:
        args.write_result.write_text(encoded)
    else:
        require(result == read(HERE / "RESULT.json"), "receipt differs from committed expectations")
    print(result["status"] + " providers=2 products=22 cases=" + str(len(result["cases"]))
          + " accepted=" + str(result["counts"]["ACCEPTED"])
          + " rejected=" + str(result["counts"]["REJECTED"]) + " no_new_kappa")


if __name__ == "__main__":
    main()
