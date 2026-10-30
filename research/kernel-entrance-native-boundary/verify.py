#!/usr/bin/env python3
"""Replay the public normaliser before the fixed kernel-entrance construction.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
Finite changed-contract evidence, not physical ownership or supplier admission.
Source snapshot and Boost authentication follow credited PR3326 conventions.
"""

import argparse
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
BOUNDARY = "research/xor-scatter-boundary/boundary.py"
CONSTRUCTOR = "research/bit-kernel-entrance-seed18/verify.py"
CERTIFICATE = "research/bit-kernel-entrance-seed18/CERTIFICATE.json"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")
IMPLEMENTATION = ("verify.py", "native_adapter.py", "independent_model.py")
BOOST_SHA256 = "7009fe1faa1697476bdc7027703a2badb84e849b7b0baad5086b087b971f8617"
KERNEL_SHA256 = "9e3840f625233859f54e180dba17986a3b2a7b49fc1262c328623d1db16e0351"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def load_module(path, name):
    """Execute the exact source bytes, without accepting cached bytecode."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def source_bytes(row, source_root, git_sources):
    path = PurePosixPath(row["path"])
    require(not path.is_absolute() and ".." not in path.parts and str(path) == row["path"],
            "canonical source path")
    require(re.fullmatch(r"[0-9a-f]{40}", row["commit"]) and
            re.fullmatch(r"[0-9a-f]{40}", row["git_blob"]), "exact Git source pin")
    if git_sources:
        environment = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}
        blob = subprocess.check_output(
            ["git", "rev-parse", row["commit"] + ":" + row["path"]],
            cwd=source_root, env=environment, timeout=30).decode().strip()
        require(blob == row["git_blob"], "Git source binding: " + row["path"])
        body = subprocess.check_output(["git", "cat-file", "blob", blob],
                                       cwd=source_root, env=environment, timeout=30)
    else:
        source = source_root / path
        require(source.is_file() and not source.is_symlink(), "regular source: " + row["path"])
        body = source.read_bytes()
    require(len(body) == row["size_bytes"] and digest(body) == row["sha256"],
            "source SHA256: " + row["path"])
    git_blob = hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest()
    require(git_blob == row["git_blob"], "source Git blob: " + row["path"])
    return body


def snapshot_sources(manifest, source_root, git_sources, snapshot):
    rows = manifest["files"]
    require(len(rows) == 14 and len({row["path"] for row in rows}) == 14,
            "fixed unique fourteen-file source inventory")
    snapshot.mkdir()
    for row in rows:
        body = source_bytes(row, source_root, git_sources)
        target = snapshot / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)


def run(arguments, timeout=130):
    return subprocess.run([str(arg) for arg in arguments], capture_output=True,
                          text=True, timeout=timeout, check=False)


def write_word(path, word):
    body = canonical(word)
    path.write_bytes(gzip.compress(body, mtime=0))
    return {"canonical_sha256": digest(body), "gzip_sha256": digest(path.read_bytes())}


def artifact_hashes(output):
    require(output.is_dir() and sorted(p.name for p in output.iterdir()) == sorted(ARTIFACTS),
            "exact exporter artifact inventory")
    return {name: digest((output / name).read_bytes()) for name in ARTIFACTS}


def public_normalisation(snapshot, directory, name, word, boundary):
    input_path = directory / (name + "-input.json.gz")
    hashes = write_word(input_path, word)
    output = directory / (name + "-public-export")
    result = run([sys.executable, "-I", "-B", snapshot / BOUNDARY,
                  "export", input_path, output])
    require(result.returncode == 0, "public zero-start boundary: " + result.stderr)
    receipt = json.loads(result.stdout)
    require(receipt["schema"] == "xor-scatter-v1" and
            receipt["export"]["sha256"] == artifact_hashes(output),
            "public normaliser output receipt")
    normalised, occurrences = boundary.normalize(copy.deepcopy(word))
    require(occurrences == receipt["input_occurrences"] and
            sum(map(len, normalised["scatter"])) == receipt["normalized_scatter_terms"],
            "pure/public normalisation agreement")
    normalised_path = directory / (name + "-normalised.json.gz")
    normalised_hashes = write_word(normalised_path, normalised)
    direct_output = directory / (name + "-normalised-direct-export")
    direct = run([sys.executable, "-I", "-B", snapshot / EXPORTER,
                  normalised_path, direct_output])
    require(direct.returncode == 0, "pure normal form original export: " + direct.stderr)
    require(artifact_hashes(direct_output) == artifact_hashes(output),
            "actual CLI and constructor input have identical three-file exports")
    return normalised, output, {"input": hashes, "accepted": True, "receipt": receipt,
                               "normalised_word": normalised_hashes,
                               "pure_normal_form_export_equals_public_cli": True}


def export_kernel(snapshot, directory, name, candidate, boundary):
    word_path = directory / (name + "-candidate.json.gz")
    hashes = write_word(word_path, candidate)
    output = directory / (name + "-kernel-export")
    result = run([sys.executable, "-I", "-B", snapshot / EXPORTER, word_path, output])
    require(result.returncode == 0, "original exporter: " + result.stderr)
    inspected = boundary.inspect_export(output, sum(map(len, candidate["scatter"])),
                                        len(candidate["ret"]))
    require(inspected["sha256"] == artifact_hashes(output), "candidate export hashes")
    rejected_output = directory / (name + "-forbidden-public-export")
    rejected = run([sys.executable, "-I", "-B", snapshot / BOUNDARY,
                    "export", word_path, rejected_output])
    expected = "target/helper 444 does not start at frame 0"
    require(rejected.returncode == 2 and not rejected.stdout and
            not rejected_output.exists() and
            rejected.stderr.strip() == "REJECT xor-scatter-v1: checker.py rejected:",
            "changed-start public CLI must reject without publishing an export")
    # The inherited CLI preserves only delegated stderr; the checker prints
    # its detailed rejection to stdout. Replay that unchanged checker directly.
    diagnosed = run([sys.executable, "-I", "-B", snapshot / CHECKER, word_path])
    require(diagnosed.returncode == 1 and not diagnosed.stderr and
            diagnosed.stdout.strip() == "REJECT " + expected,
            "original checker must identify the changed zero-start entrance")
    return output, {"candidate": hashes, "export": inspected,
                    "changed_start_public_cli": {"accepted": False,
                    "output_published": False, "rejection": expected,
                    "stderr": rejected.stderr.strip(), "returncode": rejected.returncode,
                    "direct_original_checker": {"returncode": diagnosed.returncode,
                                                "stdout": diagnosed.stdout.strip(),
                                                "stderr": diagnosed.stderr}}}


def prepare(snapshot, workdir, model):
    boundary = load_module(snapshot / BOUNDARY, "pinned_xor_boundary")
    constructor = load_module(snapshot / CONSTRUCTOR, "pinned_kernel_constructor")
    original = json.loads(gzip.decompress((snapshot / WORD).read_bytes()))
    require((original["h"], original["v"], original["R"]) == (8, 111, 439) and
            original["ret"] == list(range(472, 481)), "frozen source dimensions and retained list")
    alias = copy.deepcopy(original)
    alias["ret"].append(472)
    row_index = next(i for i, row in enumerate(alias["scatter"]) if 0 in row)
    require(row_index == 2, "first active-alias target is register 113")
    alias["scatter"][row_index] = [9 if slot == 0 else slot for slot in alias["scatter"][row_index]]
    alias["scatter"][row_index] += [9, 9]
    directory = workdir / "fixtures"
    directory.mkdir()
    outputs, evidence, models, words, normalised_outputs = {}, {}, {}, {}, {}
    for name, input_word in (("kernel", original), ("active_alias", alias)):
        normalised, public_export, public = public_normalisation(
            snapshot, directory, name, input_word, boundary)
        candidate = constructor.construct(copy.deepcopy(normalised), 444, 470)
        alternate, _ = boundary.normalize(constructor.construct(copy.deepcopy(input_word), 444, 470))
        require(canonical(alternate) == canonical(candidate), "authenticated pure maps commute")
        models[name] = model.analyse_case(input_word, normalised, candidate)
        if name == "kernel":
            require(digest(canonical(candidate)) == KERNEL_SHA256 and
                    json.loads((snapshot / CERTIFICATE).read_text())["candidate"]["payload_sha256"]
                    == KERNEL_SHA256,
                    "exact predecessor candidate reproduced")
        outputs[name], changed = export_kernel(snapshot, directory, name, candidate, boundary)
        evidence[name] = {"public_zero_start_boundary": public, "changed_contract": changed,
                          "authenticated_pure_maps_commute": True,
                          "normalised_word_sha256": digest(canonical(normalised))}
        words[name], normalised_outputs[name] = candidate, public_export
    paired = copy.deepcopy(original)
    paired["scatter"][0] += [0, 0]
    normalised, paired_output, public = public_normalisation(
        snapshot, directory, "paired_absent", paired, boundary)
    candidate = constructor.construct(normalised, 444, 470)
    require(canonical(candidate) == canonical(words["kernel"]), "paired null input gives identical gauge")
    require(artifact_hashes(paired_output) == artifact_hashes(normalised_outputs["kernel"]),
            "paired null input gives identical three public export artifacts")
    evidence["paired_absent"] = {"public_zero_start_boundary": public,
                                 "candidate_word_sha256": digest(canonical(candidate)),
                                 "same_candidate_and_public_exports_as": "kernel",
                                 "native_receipt_reused_by_exact_word_equality": "kernel"}
    return outputs, evidence, models, words


def authenticate_boost_archive(archive, backend):
    with archive.open("rb") as stream:
        archive_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    require(archive_hash == BOOST_SHA256, "official Boost archive SHA256")
    wanted = {}
    for dependencies in [backend["probe_dependencies"], *backend["native_dependencies"].values()]:
        for name, value in dependencies.items():
            require(name not in wanted or wanted[name] == value, "Boost changed between compiles")
            wanted[name] = value
    require(wanted, "nonempty compiler-observed Boost dependency inventory")
    seen = set()
    with tarfile.open(archive, "r|bz2") as stream:
        for member in stream:
            name = member.name.removeprefix("boost_1_85_0/")
            if not member.name.startswith("boost_1_85_0/") or name not in wanted:
                continue
            require(name not in seen and member.isfile(), "unique regular Boost archive header")
            require(digest(stream.extractfile(member).read()) == wanted[name],
                    "compiled Boost header differs from official archive")
            seen.add(name)
    require(seen == set(wanted), "all used Boost headers authenticated")
    return {"status": "PASS_COMPILED_BOOST_HEADERS_MATCH_OFFICIAL_ARCHIVE",
            "archive_sha256": archive_hash, "headers_checked": len(seen)}


def reconcile(native, models, words, model):
    mapping = {"records": "records", "moves": "nested_moves", "adds": "total_scalar_adds",
               "copies": "copies", "erasures": "copies", "scatter_adds": "normalised_scatter_adds",
               "rank_mass": "raw_rank_mass"}
    for name, result in models.items():
        literal = native["fixtures"][name]["invoice"]
        require(all(literal[key] == result["invoice"][field] for key, field in mapping.items()),
                "independent source/native invoice: " + name)
        paid = [[int(rank), count] for rank, count in result["invoice"]["paid_histogram"].items()]
        require(sorted(paid) == literal["paid_histogram"], "complete paid histogram: " + name)
        selection = native["fixtures"][name]["adaptation"]["selection"]
        require(model.validate_selection(selection, words[name]), "native selection binds to candidate")
    control = native["controls"]["wrong_partner"]
    wrong = copy.deepcopy(native["fixtures"]["kernel"]["adaptation"]["selection"])
    wrong[0]["partners"] = control["mutation"]["after"]
    witness = models["kernel"]["controls"]["wrong_declared_partner"]
    require(canonical(wrong) == canonical(witness["selection"]),
            "native mutation and independent false-kernel witness are identical")
    try:
        model.validate_selection(wrong, words["kernel"])
    except model.ModelError as error:
        control["independent_model"] = {"accepted": False, "reason": str(error),
                                         "first_kernel_failure": witness["first_kernel_failure"]}
    else:
        raise ValueError("unbound partner must fail independent selection-to-word check")
    expected = models["kernel"]["controls"]["missing_exit_shear"]["endpoint_differences"]
    observed = [{"output": row["output"], "inputs": row["input_columns"]}
                for row in native["controls"]["missing_exit_shear"]["scalar_differences"]]
    require(observed == expected, "independent/native missing-restoration witness")


def replay(args, workdir):
    raw_manifest = (PACKAGE / "SOURCES.json").read_bytes()
    manifest = json.loads(raw_manifest)
    hashes = {name: digest((PACKAGE / name).read_bytes()) for name in IMPLEMENTATION}
    model = load_module(PACKAGE / "independent_model.py", "independent_kernel_model")
    adapter = load_module(PACKAGE / "native_adapter.py", "kernel_native_adapter")
    snapshot = workdir / "sources"
    snapshot_sources(manifest, args.source_root.resolve(), args.git_sources, snapshot)
    outputs, boundary, models, words = prepare(snapshot, workdir, model)
    native = adapter.run_native(snapshot, outputs, workdir / "native",
                                args.boost_include.resolve(), args.compiler)
    reconcile(native, models, words, model)
    native["backend"]["archive_authentication"] = authenticate_boost_archive(
        args.boost_archive.resolve(), native["backend"])
    for row in manifest["files"]:
        source_bytes(row, snapshot, False)
    require((PACKAGE / "SOURCES.json").read_bytes() == raw_manifest and
            hashes == {name: digest((PACKAGE / name).read_bytes()) for name in IMPLEMENTATION},
            "source manifest or implementation changed during replay")
    return {"schema": "kernel-entrance-native-boundary/receipt-v1",
            "status": "PASS_KERNEL_ENTRANCE_NATIVE_COMPOSITION",
            "base_commit": manifest["base_commit"], "predecessor_heads": manifest["predecessor_heads"],
            "source_manifest_sha256": digest(raw_manifest), "source_count": len(manifest["files"]),
            "source_snapshot_unchanged": True, "implementation_sha256": hashes,
            "boundary": boundary, "independent_model": models, "native": native,
            "environment": {"python": platform.python_version(), "platform": platform.platform(),
                            "compiler": args.compiler, "boost_archive_sha256": BOOST_SHA256},
            "limits": ["Finite changed-entrance composition, not an unchanged public H1-H5 admission.",
                       "Nonempty logical kernel; physical owner and donor manifests remain absent.",
                       "The inherited bank-audit label is not evidence that a fresh bank audit ran here.",
                       "The old width-eight host repays the one-unit local rank saving as an idle charge.",
                       "Five-stage scalar/geometry evidence only; native nine/eleven stages, complete banks, "
                       "hosting, entry conversion, selected ancestry, precision/tape, and all-size transfer unrun.",
                       "No new kernel mechanism, support census, selected frontier, or hosted-CI claim."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--git-sources", action="store_true",
                        help="read already-fetched exact Git objects without an intentional network fetch")
    parser.add_argument("--boost-include", type=Path, required=True)
    parser.add_argument("--boost-archive", type=Path, required=True)
    parser.add_argument("--compiler", default="c++")
    parser.add_argument("--workdir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists() and not args.output.is_symlink(), "receipt must be new")
    if args.workdir:
        args.workdir.mkdir(parents=True, exist_ok=False)
        receipt = replay(args, args.workdir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="kernel-native-") as directory:
            receipt = replay(args, Path(directory))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"status": receipt["status"], "receipt": str(args.output),
                      "native_fixtures": 2, "formal_columns_per_fixture": 883,
                      "source_count": receipt["source_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
