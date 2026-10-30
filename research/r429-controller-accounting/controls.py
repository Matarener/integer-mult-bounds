#!/usr/bin/env python3
"""Compact authenticated-source and mathematical control audit.

Run only disposable fixtures. No large owner census or complete native stage.
Prepared for Ross with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile
import types


HERE = Path(__file__).resolve().parent
DEFAULT_PACKAGE = HERE


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def module_from_bytes(path):
    module = types.ModuleType("reviewed_portable")
    module.__file__ = str(path)
    raw = path.read_bytes()
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module, digest(raw)


def reject(name, action, marker, recorded):
    try:
        action()
    except (ValueError, AssertionError, FileNotFoundError) as error:
        need(marker in str(error), f"wrong rejection for {name}: {error}")
        recorded.append({"name": name, "reason": str(error)})
    else:
        raise ValueError("control accepted: " + name)


def fixture(directory, entries, adaptations=None):
    root = Path(directory).resolve()
    (root / "frozen/old/recursive").mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, raw in entries.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        hashes[name] = digest(raw)
    (root / "FROZEN-SHA256.json").write_text(json.dumps(hashes))
    (root / "ADAPTATIONS.json").write_text(json.dumps(adaptations or {}))
    return root


def lightweight_checks(v, work):
    rejected = []
    old = "/Users/ross/git/math/integer-mult-bounds/"
    entries = {
        "frozen/source.py": b'assert False, "DIRECT_SOURCE_ASSERT"\n',
        "frozen/data.json": b'{"n":1,"flag":true,"nested":{"all":[1,2,3]},"path":"'
                            + old.encode() + b'research/example.json"}\n',
        "frozen/word.json.gz": gzip.compress(b'{"ordered":[1,2,3]}\n', mtime=0),
    }
    root = fixture(work / "basic", entries)
    p = v.Portable(root)
    p.check_all()
    data = json.loads(entries["frozen/data.json"])
    need(p.equal(root / "frozen/data.json", data), "unchanged receipt")
    relocated = dict(data, path=str(root / "frozen/upstream/research/example.json"))
    need(p.equal(root / "frozen/data.json", relocated), "provenance relocation")
    need(p.word_equal(root / "frozen/word.json.gz", b'{"ordered":[1,2,3]}\n'),
         "unchanged complete word")
    reject("boolean_for_integer", lambda: p.equal(
        root / "frozen/data.json", dict(data, n=True)), "receipt mismatch", rejected)
    reject("float_for_integer", lambda: p.equal(
        root / "frozen/data.json", dict(data, n=1.0)), "receipt mismatch", rejected)
    reject("integer_for_boolean", lambda: p.equal(
        root / "frozen/data.json", dict(data, flag=1)), "receipt mismatch", rejected)
    reject("omitted_nested_field", lambda: p.equal(
        root / "frozen/data.json", dict(data, nested={})), "receipt mismatch", rejected)
    reject("reordered_list", lambda: p.equal(
        root / "frozen/data.json", dict(data, nested={"all": [3, 2, 1]})),
        "receipt mismatch", rejected)
    reject("missing_receipt", lambda: p.equal(root / "frozen/absent.json", data),
           "unregistered frozen input", rejected)
    reject("changed_word_bytes", lambda: p.word_equal(
        root / "frozen/word.json.gz", b'{"ordered":[1,3,2]}\n'),
        "complete word/geometry mismatch", rejected)
    reject("normalized_key_collision", lambda: p.normalize({
        old + "research/example.json": 1,
        str(root / "frozen/upstream/research/example.json"): 2}),
        "normalized key collision", rejected)
    reject("direct_assert_under_parent_flags", lambda: exec(
        p.code(root / "frozen/source.py"), {}),
        "DIRECT_SOURCE_ASSERT", rejected)
    (root / "frozen/source.py").write_bytes(b"pass\n")
    reject("source_changed", lambda: p.code(root / "frozen/source.py"),
           "frozen input changed", rejected)
    (root / "frozen/source.py").unlink()
    reject("missing_registered_source", p.check_all, "source.py", rejected)
    (root / "frozen/source.py").write_bytes(entries["frozen/source.py"])
    p.patches["frozen/source.py"] = [{"old": "absent", "new": "pass"}]
    reject("adaptation_not_unique", p.check_all, "adaptation no longer unique", rejected)
    p.patches = {"frozen/unbound.py": []}
    reject("unbound_adaptation", p.check_all, "unbound adaptation", rejected)
    p.patches = {}

    # Disable only the receipt equality gate. The rejection harness must now
    # fail outside its caught-error branch; unrelated hashes still match.
    original_need = v.need
    try:
        v.need = lambda ok, message: (
            None if message.startswith("receipt mismatch") else original_need(ok, message))
        try:
            reject("removed_receipt_gate", lambda: p.equal(
                root / "frozen/data.json", dict(data, n=True)),
                "receipt mismatch", [])
        except ValueError as error:
            need(str(error) == "control accepted: removed_receipt_gate",
                 "receipt control sensitivity")
        else:
            raise ValueError("receipt control did not notice its deleted check")
    finally:
        v.need = original_need
    return rejected


def nested_cache_check(v, work, mode):
    name = "frozen_fixture_inner_" + mode
    auth = b'assert False, "NESTED_SOURCE_ASSERT"\n'
    poison = b"CACHE_RAN = True\n"
    poison += b"#" + b"x" * (len(auth) - len(poison) - 2) + b"\n"
    need(len(auth) == len(poison), "same-size poisoned source")
    root = fixture(work / mode, {
        f"frozen/old/recursive/{name}.py": auth,
        "frozen/outer.py": f"import {name}\n".encode(),
    })
    inner = root / f"frozen/old/recursive/{name}.py"
    poison_path = root / "poison.py"
    poison_path.write_bytes(poison)
    stat = inner.stat()
    os.utime(poison_path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    cache = Path(importlib.util.cache_from_source(str(inner)))
    cache.parent.mkdir(parents=True, exist_ok=True)
    invalidation = (py_compile.PycInvalidationMode.TIMESTAMP if mode == "timestamp"
                    else py_compile.PycInvalidationMode.UNCHECKED_HASH)
    py_compile.compile(str(poison_path), cfile=str(cache), dfile=str(inner),
                       doraise=True, optimize=sys.flags.optimize,
                       invalidation_mode=invalidation)
    # Establish that this is a usable poison, not a stale/inert .pyc.
    spec = importlib.util.spec_from_file_location("poison_baseline_" + mode, inner)
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    need(baseline.CACHE_RAN is True, "ordinary loader did not consume poison")
    p = v.Portable(root)
    p.check_all()
    p.install()
    rejected = []
    reject("nested_" + mode + "_pyc_bypass", lambda: p.load("frozen/outer.py"),
           "NESTED_SOURCE_ASSERT", rejected)
    need(f"frozen/old/recursive/{name}.py" in p.executed, "nested source not recorded")
    return {"poison_was_executable": True, "rejection": rejected[0]}


def small_math_checks(v, package, work):
    p = v.Portable(package)
    p.check_all()
    p.install()
    m = p.load("frozen/upstream/research/r438-rehost-projectors/verify.py")
    m.source_check()
    q = [2, 0, 0, 0, 0, 0, 0, 0]
    target = m.QPERP | (1 << 8) | (1 << 9)
    parts = (m.QPERP, 1 << 8, 1 << 9)
    m.factorization(parts, target)
    m.factorization(tuple(reversed(parts)), target)
    need(m.operator_check([q], {(target, parts), (target, tuple(reversed(parts)))}) == 256,
         "equivalent factor order")
    rejected = []
    reject("missing_pending_axis", lambda: m.factorization(parts[:-1], target),
           "wrong pending operator", rejected)
    reject("overlapping_factor", lambda: m.factorization(parts + (1 << 8,), target),
           "overlapping factors", rejected)
    wrong = (m.QPERP, 1 << 8, 1 << 10)
    need(sum(x.bit_count() for x in wrong) == target.bit_count(), "equal-rank mutant")
    reject("equal_rank_wrong_axis", lambda: m.operator_check([q], {(target, wrong)}),
           "exterior address operator", rejected)
    original = m.require
    try:
        m.require = lambda ok, message: (
            None if message == "exterior address operator" else original(ok, message))
        try:
            reject("removed_axis_gate", lambda: m.operator_check([q], {(target, wrong)}),
                   "exterior address operator", [])
        except ValueError as error:
            need(str(error) == "control accepted: removed_axis_gate",
                 "mathematical control sensitivity")
        else:
            raise ValueError("mathematical control did not notice its deleted check")
    finally:
        m.require = original
    # Exercise the actual extracted-function path with an authenticated assert
    # fixture, so -O cannot turn the advertised AST preservation into a no-op.
    ast_root = fixture(work / "ast", {
        "frozen/upstream/probe.py":
            b'def probe():\n    assert False, "AST_SOURCE_ASSERT"\n',
    })
    ast_portable = v.Portable(ast_root)
    original_root, original_portable = m.ROOT, m.PORTABLE
    try:
        m.ROOT = ast_root / "frozen/upstream"
        m.PORTABLE = ast_portable
        reject("extracted_ast_assert", lambda: m.function("probe.py", "probe")(),
               "AST_SOURCE_ASSERT", rejected)
        (m.ROOT / "probe.py").write_bytes(b"def probe():\n    return True\n")
        reject("extracted_ast_changed_source", lambda: m.function("probe.py", "probe")(),
               "frozen input changed", rejected)
    finally:
        m.ROOT, m.PORTABLE = original_root, original_portable
    return {"equivalent_factor_columns": 256, "rejections": rejected,
            "deleted_named_check_detected": True}


def real_receipt_checks(v, package):
    """Exercise full equality on every registered stage receipt, without regeneration."""
    p = v.Portable(package)
    names = {name for _, receipts in v.STAGES.values() for name in receipts}
    if "NATIVE-REMAINDERS.json" in p.hashes:
        names.add("NATIVE-REMAINDERS.json")
    result = []

    def leaves(value, prefix=()):
        if isinstance(value, dict):
            for key in sorted(value):
                yield from leaves(value[key], prefix + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from leaves(item, prefix + (index,))
        else:
            yield prefix, value

    for name in sorted(names):
        raw = p.authenticate(package / name)
        value = json.loads(raw)
        need(p.equal(package / name, copy.deepcopy(value)), "complete real receipt")
        path, old = max(leaves(value), key=lambda item: len(item[0]))
        need(len(path) > 1, "real receipt has no nested coverage")
        changed = copy.deepcopy(value)
        parent = changed
        for key in path[:-1]:
            parent = parent[key]
        if type(old) is bool:
            parent[path[-1]] = not old
        elif type(old) is int:
            parent[path[-1]] = old + 1
        elif type(old) is str:
            parent[path[-1]] = old + "-MUTATED"
        else:
            parent[path[-1]] = {"mutation": True}
        rejected = []
        reject("nested_real_receipt_mutation", lambda: p.equal(package / name, changed),
               "receipt mismatch", rejected)
        omitted = copy.deepcopy(value)
        parent = omitted
        for key in path[:-1]:
            parent = parent[key]
        del parent[path[-1]]
        reject("nested_real_receipt_omission", lambda: p.equal(package / name, omitted),
               "receipt mismatch", rejected)
        result.append({"receipt": name, "sha256": digest(raw),
                       "deep_path": list(path), "rejections": rejected})
    return result


def run_child(package):
    v, source_hash = module_from_bytes(package / "verify.py")
    with tempfile.TemporaryDirectory(prefix="b02-control-fixtures-") as temporary:
        work = Path(temporary)
        ordinary = lightweight_checks(v, work)
        caches = {mode: nested_cache_check(v, work, mode)
                  for mode in ("timestamp", "unchecked_hash")}
        math = small_math_checks(v, package, work)
        receipts = real_receipt_checks(v, package)
    return {"parent_optimization": sys.flags.optimize, "verifier_sha256": source_hash,
            "compact_rejections": ordinary, "nested_cache_controls": caches,
            "mathematical_controls": math,
            "complete_real_receipt_controls": receipts,
            "receipt_check_deletion_detected": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    package = args.package.resolve()
    if args.child:
        print(canonical(run_child(package)))
        return
    runs = []
    for optimized in (False, True):
        command = [sys.executable, "-I", "-B"]
        if optimized:
            command.append("-O")
        command += [str(Path(__file__).resolve()), "--package", str(package), "--child"]
        proc = subprocess.run(command, capture_output=True, text=True)
        need(proc.returncode == 0, proc.stderr + proc.stdout)
        runs.append(json.loads(proc.stdout))
    raw = (package / "FROZEN-SHA256.json").read_bytes()
    result = {"status": "PASS_COMPACT_B02_SOURCE_AND_CONTROL_AUDIT",
              "package": str(package), "frozen_manifest_sha256": digest(raw),
              "runs": runs, "no_large_mathematical_replay": True, "no_new_kappa": True}
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(canonical(result))


if __name__ == "__main__":
    main()
