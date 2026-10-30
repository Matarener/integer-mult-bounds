#!/usr/bin/env python3
"""Behavioural tests: corruption, negative controls and read-only replay.

Each case copies the package and its pinned inputs into a temporary tree,
mutates one thing and runs both scanners there under python -O. The scanners
must reject every mutation; the clean tree must pass and stay byte-identical.
"""

import concurrent.futures
import hashlib
import json
import os
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
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]


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


def cert_edit(fn):
    return lambda base: edit_json(base / PKG / "CERTIFICATE.json", fn)


def events(d, base, name):
    return d["corrections"][base][name]["splices"][0]["events"]


def set_event(base, name, k, field, value):
    def fn(d):
        events(d, base, name)[k][field] = value
    return cert_edit(fn)


def drop_event(base, name, k):
    def fn(d):
        del events(d, base, name)[k]
    return cert_edit(fn)


def dup_key(base):
    p = base / PKG / "CERTIFICATE.json"
    text = p.read_text()
    p.write_text(text.replace('"schema_version": 1', '"schema_version": 1,\n  "schema_version": 1', 1))


def flip(rel, offset):
    def fn(base):
        p = base / rel
        raw = bytearray(p.read_bytes())
        raw[offset] ^= 1
        p.write_bytes(bytes(raw))
    return fn


def recipe_phase(base):
    p = base / PKG / "CORRECTION-RECIPES.json"
    data = json.loads(p.read_text())
    left = data["recipes"][0]["recipe"]["left"]
    left["phase"] = (left["phase"] + 1) % 4
    p.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


CASES = {
    "bill_T_rank_mass": cert_edit(lambda d: d["bill"]["T"]["added_vs_base"].update(rank_mass=0)),
    "bill_E_register_mass": cert_edit(lambda d: d["bill"]["E"].update(added_rank_by_register={"Y7": 2})),
    "forcing_head": cert_edit(lambda d: d["obstruction"].update(forcing_source_head=[131])),
    "exit_event": cert_edit(lambda d: d["obstruction"]["source_leaves_target_final_at"].__setitem__(0, 1311)),
    "strict_row": cert_edit(lambda d: d["obstruction"]["strict_first_obstruction"].__setitem__(5, [1312, None])),
    "cohost_rescue": cert_edit(lambda d: d["obstruction"].update(order_preserving_cohost_single_register_rescues=[])),
    "cohost_discount": cert_edit(lambda d: d["end_cut_comparison"].update(cohost_discount_R1=0)),
    "duplicate_key": dup_key,
    "witness_byte": flip(f"{NATIVE}/inputs/LOWRANK-WITNESS.json", 4096),
    "pr3532_certificate_byte": flip(f"{PKG}/inputs/pr3532/CERTIFICATE.json", 2048),
    "recipe_phase": recipe_phase,
    "T_wrong_coefficient": set_event("R0", "T", 1, 3, "1/4"),
    "T_undercharged_lift": set_event("R0", "T", 0, 4, 5),
    "S_wrong_chart": set_event("R0", "S", 2, 4, FULL),
    "S_source_not_restored": drop_event("R0", "S", 3),
    "P_private_not_erased": drop_event("R0", "P", 5),
    "E_wrong_chart": set_event("R1", "E", 1, 4, [95, 486, 232]),
    "E_wrong_sign": set_event("R1", "E", 1, 3, "-1/2"),
}


def case(name):
    with tempfile.TemporaryDirectory() as tmp:
        base = tree(Path(tmp))
        CASES[name](base)
        results = [run(base, s) for s in SCANNERS]
        return name, [code != 0 for code, _ in results]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = tree(Path(tmp))
        before = digest(base)
        for s in SCANNERS:
            code, out = run(base, s)
            need(code == 0 and "PASS_P104_FLAG1_SIDE_CORRECTION_BILL" in out, "clean pass: " + s + "\n" + out)
        need(digest(base) == before, "scanners are read-only")
    workers = max(2, min(8, os.cpu_count() or 2))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = dict(pool.map(case, CASES))
    for name, rejected in sorted(results.items()):
        need(all(rejected), "mutation accepted: %s %s" % (name, rejected))
    print("PASS_P104_FLAG1_SIDE_CORRECTION_BILL_TESTS cases=%d clean_read_only=1 scanners=%d" % (len(CASES), len(SCANNERS)))


if __name__ == "__main__":
    main()
