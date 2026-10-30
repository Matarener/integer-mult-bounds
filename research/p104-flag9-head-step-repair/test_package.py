#!/usr/bin/env python3
"""Behavioural tests: corruption, negative controls and read-only replay.

Each case copies the package and its pinned inputs into a temporary tree,
mutates one thing and runs both scanners there under python -O. The scanners
must reject every mutation; the clean tree must pass and stay byte-identical.
"""

import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PKG = HERE.relative_to(ROOT).as_posix()
NATIVE = "research/p104-native-channel"
COPY = [
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json",
    f"{NATIVE}/inputs/P104-FIXTURE.json",
    f"{NATIVE}/NATIVE-RECIPES.json.gz",
    f"{NATIVE}/check_native.py",
    f"{NATIVE}/vendor/native_verify.py",
    "research/p104-joint-unit-flags/CERTIFICATE.json",
]
SCANNERS = ("verify.py", "independent.py")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tree(base):
    for rel in COPY:
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, base / rel)
    shutil.copytree(HERE, base / PKG, ignore=shutil.ignore_patterns("__pycache__"))
    return base


def run(base, scanner):
    p = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(base / PKG / scanner), str(base)],
                       capture_output=True, text=True, timeout=180)
    return p.returncode, p.stdout + p.stderr


def digest(base):
    return {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(base.rglob("*")) if p.is_file()}


def edit_json(path, fn):
    data = json.loads(path.read_text())
    fn(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def cert_field(fn):
    return lambda base: edit_json(base / PKG / "CERTIFICATE.json", fn)


def dup_key(base):
    p = base / PKG / "CERTIFICATE.json"
    text = p.read_text()
    p.write_text(text.replace('"basis_head": 196,', '"basis_head": 196,\n  "basis_head": 196,', 1))


def flip_witness(base):
    p = base / f"{NATIVE}/inputs/LOWRANK-WITNESS.json"
    raw = bytearray(p.read_bytes())
    raw[len(raw) // 2] ^= 1
    p.write_bytes(bytes(raw))


def bad_phase(base):
    p = base / PKG / "REPAIR-RECIPES.json"
    data = json.loads(p.read_text())
    left = data["recipes"][0]["recipe"]["left"]
    left["phase"] = (left["phase"] + 1) % 4
    p.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


def drop_return(c):
    for row in c["repairs"]["R0"]["splices"]:
        if row["published_range"][0] == 3124:
            row["events"] = row["events"][:1]


def undercharge(c):
    for row in c["repairs"]["R0"]["splices"]:
        if row["published_range"][0] == 3489:
            row["events"][0][4] = 1


CASES = {
    "bill_rank_mass": (cert_field(lambda c: c["bill"]["R0"].__setitem__("rank_mass", 2369)), None),
    "bill_profile_delta": (cert_field(lambda c: c["bill"]["R0"]["profile_delta"].__setitem__("2", 9)), None),
    "cohosted_updates": (cert_field(lambda c: c["head_cohosting"]["R0"].__setitem__("cohosted_target_updates", [])), None),
    "delivery": (cert_field(lambda c: c["head_cohosting"]["R0"]["source_delivery_into_target"][-1].__setitem__(2, "1/4")), None),
    "admissible_3124": (cert_field(lambda c: [r.__setitem__("admissible", True) for r in c["forced_hosting"]["table"] if r["event"] == 3124]), None),
    "duplicate_key": (dup_key, "duplicate JSON key"),
    "witness_byte": (flip_witness, None),
    "recipe_phase": (bad_phase, None),
    "control_without_drop": (cert_field(drop_return), "common chart"),
    "control_undercharge": (cert_field(undercharge), "frame gap"),
}


def case(name):
    mutate, expect = CASES[name]
    with tempfile.TemporaryDirectory(prefix="flag9-repair-") as d:
        base = tree(Path(d))
        mutate(base)
        for scanner in SCANNERS:
            code, out = run(base, scanner)
            need(code != 0, f"{name}: {scanner} accepted a mutation")
            need("PASS_" not in out, f"{name}: {scanner} printed a pass marker")
            if expect:
                need(expect in out, f"{name}: {scanner} rejected for the wrong reason: {out[-400:]}")
    return name


def clean():
    with tempfile.TemporaryDirectory(prefix="flag9-repair-") as d:
        base = tree(Path(d))
        before = digest(base)
        for scanner in SCANNERS:
            code, out = run(base, scanner)
            need(code == 0 and "PASS_P104_FLAG9_HEAD_STEP_REPAIR" in out, f"clean {scanner}: {out[-500:]}")
        need(digest(base) == before, "scanners modified the tree")


def main():
    clean()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(case, sorted(CASES)))
    need(len(done) == len(CASES), "all cases ran")
    print(f"PASS_P104_FLAG9_HEAD_STEP_REPAIR_TESTS cases={len(CASES)} clean_read_only=1 scanners=2")


if __name__ == "__main__":
    main()
