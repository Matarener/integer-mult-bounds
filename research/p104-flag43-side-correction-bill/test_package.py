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
REPAIR = "research/p104-flag43-head-step-repair"
COPY = [
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json",
    f"{NATIVE}/inputs/P104-FIXTURE.json",
    f"{NATIVE}/NATIVE-RECIPES.json.gz",
    f"{NATIVE}/check_native.py",
    f"{NATIVE}/vendor/native_verify.py",
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    f"{REPAIR}/CERTIFICATE.json",
    f"{REPAIR}/REPAIR-RECIPES.json",
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


def cert_edit(fn):
    return lambda base: edit_json(base / PKG / "CERTIFICATE.json", fn)


def splice_events(name):
    return lambda d: d["corrections"][name]["splices"][0]["events"]


def set_event(name, k, field, value):
    def fn(d):
        splice_events(name)(d)[k][field] = value
    return cert_edit(fn)


def drop_event(name, k):
    def fn(d):
        del splice_events(name)(d)[k]
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
    "bill_T_rank_mass": cert_edit(lambda d: d["bill"]["T"]["added_vs_R0"].update(rank_mass=0)),
    "bill_P_profile": cert_edit(lambda d: d["bill"]["P"]["added_rank_by_register"].update(C=0)),
    "feeder_head": cert_edit(lambda d: d["obstruction"].update(feeder_source_head=[15])),
    "full_from": cert_edit(lambda d: d["obstruction"].update(source_forced_full_from=1517)),
    "obstruction_row": cert_edit(lambda d: d["obstruction"]["direct_first_obstruction"].__setitem__(23, [3365, None])),
    "duplicate_key": dup_key,
    "witness_byte": flip(f"{NATIVE}/inputs/LOWRANK-WITNESS.json", 4096),
    "repair_certificate_byte": flip(f"{REPAIR}/CERTIFICATE.json", 2048),
    "recipe_phase": recipe_phase,
    "T_wrong_coefficient": set_event("T", 1, 3, "-1/4"),
    "T_undercharged_lift": set_event("T", 0, 4, 2),
    "S_wrong_chart": set_event("S", 2, 4, [1, 2, 4, 8, 16, 32, 64, 128, 256]),
    "S_source_not_restored": drop_event("S", 3),
    "P_private_not_erased": drop_event("P", 5),
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
            need(code == 0 and "PASS_P104_FLAG43_SIDE_CORRECTION_BILL" in out, "clean pass: " + s + "\n" + out)
        need(digest(base) == before, "scanners are read-only")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = dict(pool.map(case, CASES))
    for name, rejected in sorted(results.items()):
        need(all(rejected), "mutation accepted: %s %s" % (name, rejected))
    print("PASS_P104_FLAG43_SIDE_CORRECTION_BILL_TESTS cases=%d clean_read_only=1 scanners=%d" % (len(CASES), len(SCANNERS)))


if __name__ == "__main__":
    main()
