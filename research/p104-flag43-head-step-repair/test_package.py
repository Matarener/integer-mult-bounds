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
                       capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout + p.stderr


def digest(base):
    return {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(base.rglob("*")) if p.is_file()}


def edit_json(path, fn):
    data = json.loads(path.read_text())
    fn(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def drop_splices(events):
    def fn(c):
        rows = c["repairs"]["R0"]["splices"]
        c["repairs"]["R0"]["splices"] = [r for r in rows if r["published_range"][0] not in events]
    return fn


def set_rank(event, value):
    def fn(c):
        for r in c["repairs"]["R0"]["splices"]:
            if r["published_range"][0] == event:
                r["events"][0][4] = value
    return fn


def cert_field(fn):
    return lambda base: edit_json(base / PKG / "CERTIFICATE.json", fn)


def dup_key(base):
    p = base / PKG / "CERTIFICATE.json"
    text = p.read_text()
    p.write_text(text.replace('"basis_head": 15,', '"basis_head": 15,\n  "basis_head": 15,', 1))


def flip_witness(base):
    p = base / f"{NATIVE}/inputs/LOWRANK-WITNESS.json"
    raw = bytearray(p.read_bytes())
    k = raw.index(b"3525") if b"3525" in raw else len(raw) // 2
    raw[k] ^= 1
    p.write_bytes(bytes(raw))


def bad_phase(base):
    p = base / PKG / "REPAIR-RECIPES.json"
    data = json.loads(p.read_text())
    left = data["recipes"][0]["recipe"]["left"]
    left["phase"] = (left["phase"] + 1) % 4
    p.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


CASES = {
    "bill_rank_mass": (cert_field(lambda c: c["bill"]["R0"].__setitem__("rank_mass", 2369)), None),
    "bill_profile_delta": (cert_field(lambda c: c["bill"]["R0"]["profile_delta"].__setitem__("2", 4)), None),
    "cohosted_updates": (cert_field(lambda c: c["head_cohosting"].__setitem__("R0_cohosted_target_updates", [])), None),
    "delivery": (cert_field(lambda c: c["head_cohosting"]["R0_source_delivery_into_target"][-1].__setitem__(2, "1/4")), None),
    "admissible_3231": (cert_field(lambda c: [r.__setitem__("admissible", True) for r in c["forced_hosting"]["table"] if r["event"] == 3231]), None),
    "forced_set": (cert_field(lambda c: [r["forced"].pop("D28") for r in c["forced_hosting"]["table"] if r["event"] == 3364]), None),
    "kappa": (cert_field(lambda c: c.__setitem__("selected_kappa", "0.0016726601970769181")), None),
    "duplicate_key": (dup_key, "duplicate JSON key"),
    "witness_byte": (flip_witness, None),
    "recipe_phase": (bad_phase, None),
    "control_target_only": (cert_field(drop_splices({3362, 3612, 3365, 3366, 3460, 3461, 3462, 3569, 3634})), "common"),
    "control_without_y103": (cert_field(drop_splices({3365, 3366, 3460, 3461, 3462, 3569, 3634})), "common"),
    "control_without_d28": (cert_field(drop_splices({3460, 3462, 3634})), "common"),
    "control_undercharge": (cert_field(set_rank(3525, 1)), None),
}


def case(name):
    mutate, expect = CASES[name]
    with tempfile.TemporaryDirectory(prefix="flag43-repair-") as d:
        base = tree(Path(d))
        mutate(base)
        for scanner in SCANNERS:
            code, out = run(base, scanner)
            need(code != 0, f"{name}: {scanner} accepted a mutation")
            need("PASS_" not in out, f"{name}: {scanner} printed a pass marker")
            if expect:
                need(expect in out, f"{name}: {scanner} rejected for the wrong reason: {out[-300:]}")
    return name


def clean():
    with tempfile.TemporaryDirectory(prefix="flag43-repair-") as d:
        base = tree(Path(d))
        before = digest(base)
        for scanner in SCANNERS:
            code, out = run(base, scanner)
            need(code == 0 and "PASS_P104_FLAG43_HEAD_STEP_REPAIR" in out, f"clean {scanner}: {out[-400:]}")
        need(digest(base) == before, "scanners modified the tree")


def main():
    clean()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(case, sorted(CASES)))
    need(len(done) == len(CASES), "all cases ran")
    print(f"PASS_P104_FLAG43_HEAD_STEP_REPAIR_TESTS cases={len(CASES)} clean_read_only=1 scanners=2")


if __name__ == "__main__":
    main()
