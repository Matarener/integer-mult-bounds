#!/usr/bin/env python3
"""Admit PR4181's optimal chronological fill with the source-bound PR4180 engine.

Only the selected fill/dispatch, active provider set, exact source identity,
and output placement change. All inherited scientific predicates remain.
Frozen source files are never edited. Apache-2.0; substantial Codex assistance.
"""
import argparse
from collections import Counter
import os
from pathlib import Path
import shutil
import subprocess
import sys

from common import (ADMISSION, CANDIDATE, HERE, REPO, authenticate,
                    check_no_python_caches, need, read, sha, write)

ACTIVE = {"gauge44": "base", "extra": "extra", "extra-four": "extra-four"}
COUNTS = {"gauge44": 1568, "extra": 592, "extra-four": 1080}


def make_adapter(destination):
    """Derive a separately recorded executable copy from exact frozen source."""
    authenticate()
    dispatch = read(CANDIDATE / "owner/MIXED-DISPATCH.json")
    need(Counter(r[2] for r in dispatch) == COUNTS, "exact active provider census")
    shutil.copytree(ADMISSION, destination)
    patches = []

    def replace(name, old, new, count=1, purpose="source binding"):
        path = destination / name
        before = sha(path)
        text = path.read_text()
        need(text.count(old) == count, "exact successor preimage: " + name + ": " + old[:80])
        path.write_text(text.replace(old, new))
        patches.append(dict(path=name, before_sha256=before, after_sha256=sha(path),
                            old=old, new=new, occurrences=count, purpose=purpose))

    # Location adapters do not change authenticated source bytes or predicates.
    for name in ("adapt.py", "sources.py"):
        replace(name, "REPO = HERE.parents[1]", "REPO = Path(" + repr(str(REPO)) + ")",
                purpose="resolve canonical inputs from external adapter")
    replace("adapt.py", 'MIXED = REPO / "research/staged544-mixed-fourth-entry"',
            'MIXED = REPO / "research/staged544-mixed-fourth-entry"\n'
            + "CANDIDATE = Path(" + repr(str(CANDIDATE)) + ")")
    replace("adapt.py", 'TAGS = {"gauge44": "base", "extra": "extra",\n'
            '        "gauge44-four": "base-four", "extra-four": "extra-four"}',
            "TAGS = " + repr(ACTIVE), purpose="exact active registry, retaining bijection checks")
    replace("adapt.py", 'read(MIXED / "owner/MIXED-DISPATCH.json")',
            'read(CANDIDATE / "owner/MIXED-DISPATCH.json")', purpose="actual t<1080 selector")
    # These strings are the new sides of PR4180's literal two-to-four patches.
    # Their old sides stay byte-identical, so the inherited two-provider source
    # must still match before every generated change.
    replacements = [
        ("pkg, loc_g, loc_e, loc_g4, loc_e4, out = map(Path, sys.argv[1:7]);",
         "pkg, loc_g, loc_e, loc_e4, out = map(Path, sys.argv[1:6]);"),
        ("locs = {'gauge44': loc_g, 'extra': loc_e, 'gauge44-four': loc_g4, 'extra-four': loc_e4};",
         "locs = {'gauge44': loc_g, 'extra': loc_e, 'extra-four': loc_e4};"),
        ("('base','extra','base-four','extra-four')", "('base','extra','extra-four')"),
        ("nat['base']/'local',nat['extra']/'local',nat['base-four']/'local',nat['extra-four']/'local'",
         "nat['base']/'local',nat['extra']/'local',nat['extra-four']/'local'"),
        ("nat['base'],nat['extra'],nat['base-four'],nat['extra-four'],*[p_",
         "nat['base'],nat['extra'],nat['extra-four'],*[p_"),
        ("[('extra','extra'),('gauge44-four','base-four'),('extra-four','extra-four')]",
         "[('extra','extra'),('extra-four','extra-four')]"),
        ("for tag in ('base', 'extra', 'base-four', 'extra-four'):",
         "for tag in ('base', 'extra', 'extra-four'):"),
        ("natives['extra'] / 'local', natives['base-four'] / 'local', natives['extra-four'] / 'local', work / 'rebound'",
         "natives['extra'] / 'local', natives['extra-four'] / 'local', work / 'rebound'"),
    ]
    for old, new in replacements:
        # The runtime-copy list occurs once in source adaptation and once in
        # engine adaptation. Both paths must use the same active catalogue.
        count = 2 if old.startswith("[('extra','extra')") else 1
        replace("adapt.py", old, new, count=count, purpose="route all three active providers")
    replace("adapt.py", "pr4088-four-provider-admission-v1", "pr4181-pooled-active-provider-admission-v1")
    replace("replay.py", "from binding import need, read, sha", "from binding import need, read, sha\nfrom adapt import CANDIDATE")
    replace("replay.py", "pr4088-four-provider-admission-v1", "pr4181-pooled-active-provider-admission-v1")
    replace("replay.py", '    for tag in ("base", "extra"):\n        supplied =',
            '    for tag in ("extra",):\n        supplied =',
            purpose="fresh native execution for the only active FOUR word")
    for path in ("owner/FILL.json.gz", "owner/MIXED-DISPATCH.json", "RESULT.json"):
        replace("replay.py", 'MIXED / "' + path + '"', 'CANDIDATE / "' + path + '"',
                purpose="bind full engine to actual pooled fill and complete price")
    marker = "    if args.checked_preflight:\n"
    extra = ('    run("pooled-exact-operator", [sys.executable, "-B", '
             + repr(str(HERE / "operator_admission.py"))
             + ', "--controls", "--output", str(work / "POOLED-OPERATOR.json")], 300)\n')
    replace("replay.py", marker, extra + marker,
            purpose="fresh all-character admission for the changed chronological fill")
    # All reuse and inherited semantic challenges are unchanged; only their
    # runtime paths and active TAGS are supplied by the derived adapter.
    write(destination / "SUCCESSOR-ADAPTATION.json", dict(
        predecessor="15a4153e734a8d1d485c6d3bea9b1a8201328a4c",
        candidate="4ed92bed95dd483f5662e98ef246b258c3cfe64f",
        active_providers=ACTIVE, call_counts=COUNTS, patches=patches))
    return patches


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--adapter-only", action="store_true")
    ap.add_argument("--checked-preflight", type=Path)
    ap.add_argument("--four-native-extra", type=Path)
    args = ap.parse_args()
    need(__debug__, "full inherited admission requires assertions")
    work = args.work.resolve()
    need(not work.exists() and not work.is_relative_to(REPO), "fresh external work")
    work.mkdir(parents=True)
    if args.checked_preflight:
        check_no_python_caches([args.checked_preflight.resolve()])
    adapter = work / "adapter"
    patches = make_adapter(adapter)
    if args.adapter_only:
        print("PREPARED_POOLED_ADAPTER_NOT_ADMITTED", len(patches))
        return
    command = [sys.executable, "-B", str(adapter / "replay.py"), "--work", str(work / "replay")]
    for flag in ("checked_preflight", "four_native_extra"):
        value = getattr(args, flag)
        if value:
            command += ["--" + flag.replace("_", "-"), str(value.resolve())]
    env = dict(PATH=os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               PYTHONINTMAXSTRDIGITS="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    subprocess.run(command, check=True, env=env)
    result = read(work / "replay/RESULT.json")
    need(result["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE",
         "complete pooled-fill release")
    for optimized in (False, True):
        command = [sys.executable] + (["-O"] if optimized else []) + [
            "-B", str(adapter / "challenge.py"), "--work", str(work / "replay")]
        if args.checked_preflight:
            command += ["--preflight", str(args.checked_preflight.resolve())]
        log = work / ("challenges-optimized.json" if optimized else "challenges-normal.json")
        with log.open("w") as stream:
            subprocess.run(command, env=env, check=True, stdout=stream)
    authenticate()
    check_no_python_caches([work] + ([args.checked_preflight.resolve()]
                                   if args.checked_preflight else []))
    write(work / "RESULT.json", dict(
        status="PASS_POOLED_COMPLETE_FINITE_ADMISSION", inherited_status=result["status"],
        source_pins=sha(HERE / "INPUT-PINS.json"), active_providers=ACTIVE, call_counts=COUNTS,
        candidate_profile=read(CANDIDATE / "RESULT.json")["profile"],
        adaptation_sha256=sha(adapter / "SUCCESSOR-ADAPTATION.json"),
        inherited_result_sha256=sha(work / "replay/RESULT.json"),
        operator_receipt_sha256=sha(work / "replay/POOLED-OPERATOR.json"),
        inherited_source_loading="Clean scientific source trees before and after; bytecode writes disabled.",
        mathematical_scope="Finite complete conditional admission; uniform physical and analytic hypotheses remain.",
        selected_frontier_changed=False))
    print("PASS_POOLED_COMPLETE_FINITE_ADMISSION")


if __name__ == "__main__":
    main()
