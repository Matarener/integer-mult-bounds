#!/usr/bin/env python3
"""Admission, corruption, span/reprint controls and scanner agreement. No asserts."""

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import independent
import verify

SLUG = "research/" + HERE.name


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tree_digest(paths):
    return {
        str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
    }


def watched_files():
    files = [path for path in HERE.iterdir() if path.is_file()]
    files.extend(ROOT / name for name in verify.INPUTS)
    return sorted(files)


def test_duplicate_key():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dup.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        for reader in (verify.read_json, independent.read_json):
            try:
                reader(path)
            except ValueError as exc:
                need(str(exc) == "duplicate JSON key", "duplicate message")
            else:
                need(False, "duplicate key accepted")


def stage_tree(tmp):
    """Copy the package and its pinned inputs into a throwaway repository root."""
    root = Path(tmp)
    for name in verify.INPUTS:
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    package = root / SLUG
    package.mkdir(parents=True)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in (".py", ".json"):
            shutil.copyfile(path, package / path.name)
    return root, package


def run_optimized(script):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )


def expect_rejection(script, needle):
    done = run_optimized(script)
    need(done.returncode != 0, "corruption accepted: " + script.name)
    need(needle in done.stderr, "wrong rejection for " + script.name + ": " + done.stderr[-200:])


def test_temp_copy_corruption():
    before = tree_digest(watched_files())
    with tempfile.TemporaryDirectory() as tmp:
        root, package = stage_tree(tmp)
        for name in ("verify.py", "independent.py"):
            done = run_optimized(package / name)
            need(done.returncode == 0, "clean temp copy failed: " + done.stderr[-200:])
        cert = package / "CERTIFICATE.json"
        clean = cert.read_bytes()
        mutations = (
            ("basis_head_drop_event", 0),
            ("target_span_first_hosting_event", 3364),
            ("source_span_drop_events", [570]),
            ("target_updates_in_head_free_span", 14),
            ("target_updates_cohosting_tail_without_head", [3364]),
            ("chronology_distinct_from_published_priors", False),
        )
        for key, value in mutations:
            blob = json.loads(clean)
            need(key in blob, "mutation key missing: " + key)
            blob[key] = value
            cert.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
            expect_rejection(package / "verify.py", "certificate mismatch")
            expect_rejection(package / "independent.py", "certificate mismatch")
        text = clean.decode("utf-8").replace(
            '"schema_version": 1,', '"schema_version": 1,\n  "schema_version": 1,', 1
        )
        cert.write_text(text, encoding="utf-8")
        expect_rejection(package / "verify.py", "duplicate JSON key")
        expect_rejection(package / "independent.py", "duplicate JSON key")
        cert.write_bytes(clean)
        witness = root / verify.INPUTS[1]
        raw = bytearray(witness.read_bytes())
        position = raw.index(b'"X21"')
        raw[position:position + 5] = b'"X22"'
        witness.write_bytes(bytes(raw))
        expect_rejection(package / "verify.py", "source hash")
        expect_rejection(package / "independent.py", "source hash")
    need(tree_digest(watched_files()) == before, "live files mutated by corruption test")


def test_optimized_admission():
    script = (
        "import sys\n"
        f"sys.path.insert(0, {str(HERE)!r})\n"
        "import verify, independent\n"
        "verify.need(__debug__ is False, 'optimization off')\n"
        "for module in (verify, independent):\n"
        "    try:\n"
        "        module.need(False, 'admission')\n"
        "    except ValueError as exc:\n"
        "        if str(exc) != 'admission':\n"
        "            raise SystemExit('wrong admission')\n"
        "    else:\n"
        "        raise SystemExit('admission skipped')\n"
        "print('PASS_OPTIMIZED_ADMISSION')\n"
    )
    done = subprocess.run(
        [sys.executable, "-O", "-I", "-B", "-c", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    need(done.returncode == 0, "optimized admission failed: " + done.stderr)
    need("PASS_OPTIMIZED_ADMISSION" in done.stdout, "optimized marker")


def test_sample_span_geometry():
    drop = ["transport", "X21", [15], [3, 4, 8, 128, 256], 4]
    frames = verify.annotated_frames(drop, "X21")
    need(frames[0] == ("before", [15]), "sample before")
    need(15 not in frames[1][1], "sample literal drop")
    need(verify.span_combination(15, drop[3]) == [3, 4, 8], "primary decomposition")
    need(independent.subset_xor(15, drop[3]) == [3, 4, 8], "subset decomposition")
    need(3 ^ 4 ^ 8 == 15, "head arithmetic")
    need(verify.span_contains(drop[3], drop[2]), "primary nesting")
    need(independent.closure(drop[2]) <= independent.closure(drop[3]), "closure nesting")
    need(verify.rank(drop[3]) - verify.rank(drop[2]) == drop[4], "rank step")
    late = [95, 447, 6, 32, 20]
    need(not verify.in_span(15, late), "primary late span")
    need(15 not in independent.closure(late), "closure late span")
    need(len(verify.span_elements(late)) == 32, "late span size")
    need(sorted(independent.closure(late)) == verify.span_elements(late), "late closure")
    tail = [387, 6, 18, 32, 67, 128, 1, 2]
    need(verify.tail_in_span(tail, late) == [6, 18, 32], "late tail")
    need(6 ^ 20 == 18, "tail arithmetic")
    for bad in ([15, 15], [3, 4, 7]):
        for check in (verify.rank, independent.dimension):
            try:
                check(bad)
            except ValueError:
                pass
            else:
                need(False, "dependent frame accepted")


def test_span_negative_control():
    pinned = verify.pin_sources()
    helpers = json.loads(pinned[verify.INPUTS[0]])["helpers"]
    witness = json.loads(pinned[verify.INPUTS[1]])
    clean = verify.build_receipt(witness, helpers)
    need(clean["target_updates_in_head_free_span"] == 15, "clean update count")
    mutated = copy.deepcopy(witness)
    program = mutated["program"]
    need(
        program[3363][:2] == ["transport", "Y59"]
        and program[3363][3] == [95, 447, 6, 32, 20],
        "anchor 3363",
    )
    need(program[3364][:3] == ["add", "Y59", "D17"], "anchor 3364")
    hosted = [95, 447, 15 ^ 20, 32, 20]
    program[3363][3] = list(hosted)
    program[3364][-1] = list(hosted)
    program[3525][2] = list(hosted)
    shifted = verify.build_receipt(mutated, helpers)
    need(shifted["target_preterminal_annotations_containing_basis_head"] == 0, "literal blind")
    need(shifted["target_preterminal_annotations_span_hosting_basis_head"] == 2, "span sees head")
    need(15 in shifted["target_arrive_before_span"], "arrive before now hosts head")
    need(shifted["target_span_first_hosting_event"] == 3363, "span arrive moved")
    need(shifted["target_updates_in_head_free_span"] == 14, "update now hosts head")
    need(
        shifted["target_updates_cohosting_tail_without_head"] == [3231],
        "tail-without-head list follows the head",
    )
    need(shifted["endpoint_transports_span_nested_upward"] is True, "control broke nesting")
    need(shifted["endpoint_transport_rank_steps_match"] is True, "control broke rank steps")
    need(shifted != clean, "control did not change receipt")


def test_reprint_guard():
    """A prior with flag 43's own chronology must trip both scanners' DEFER guard."""
    own = [570, 3525, 2955]
    saved_verify = verify.PRIOR_TUPLES
    saved_independent = independent.PRIORS
    try:
        verify.PRIOR_TUPLES = dict(saved_verify, reprint_probe=own)
        independent.PRIORS = saved_independent + (("reprint_probe", tuple(own)),)
        for module in (verify, independent):
            try:
                module.evaluate()
            except ValueError as exc:
                need(str(exc) == "reprint of a prior", "wrong reprint rejection")
            else:
                need(False, "reprint accepted by " + module.__name__)
    finally:
        verify.PRIOR_TUPLES = saved_verify
        independent.PRIORS = saved_independent


def test_scanners_agree():
    before = tree_digest(watched_files())
    left = verify.evaluate()
    right = independent.evaluate()
    need(left == right, "scanner disagreement")
    verify.admit(left, verify.read_json(HERE / "CERTIFICATE.json"))
    need(tree_digest(watched_files()) == before, "package or input files mutated")


def main():
    test_duplicate_key()
    test_temp_copy_corruption()
    test_optimized_admission()
    test_sample_span_geometry()
    test_span_negative_control()
    test_reprint_guard()
    test_scanners_agree()
    print("PASS_P104_PRESENT_HEAD_FLAG43_TESTS groups=7")


if __name__ == "__main__":
    main()
