#!/usr/bin/env python3
"""Run the source-bound four-provider extension in a fresh external directory.

SPDX-License-Identifier: Apache-2.0
Prepared for yssite with substantial OpenAI Codex assistance.
No frontier record is modified. Finite release is not an all-size proof.
"""
import argparse
from importlib.metadata import version
import importlib.util
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from adapt import BASE_ENGINE, BASE_MANIFEST, HERE, MIXED, REPO, TAGS, extend_engine, extend_source, tree, write
from binding import need, read, sha
from native_outputs import authenticate_native
from sources import authenticate_sources

PREDECESSOR = REPO / "research/kappa-operator-repair/late-staged-composition"
STAGES = ["native", "ledgers", "local-replay", "wrappers", "phases"]
DEPENDENCIES = {"numpy": "2.3.5", "scipy": "1.17.0", "sympy": "1.14.0", "mpmath": "1.3.0"}


def baseline_preflight(output):
    """Redirect output placement only; the predecessor's exact pins still apply."""
    output.mkdir()
    shutil.copytree(PREDECESSOR / "candidate", output / "candidate")
    path = PREDECESSOR / "run_release.py"
    spec = importlib.util.spec_from_file_location("pr4085_preflight", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = output
    saved = sys.argv
    sys.argv = [str(path), "--work", str(output / "release-work/preflight"), "--preflight-only"]
    try:
        module.main()
    finally:
        sys.argv = saved
    return output / "release-work/preflight"


def check_preflight(baseline):
    result = read(baseline / "PREFLIGHT-RESULT.json")
    need(result["status"] == "PASS_ALL_THREE_WORD_REVIEWS_SOURCE_READY_NOT_ADMITTED",
         "completed predecessor preflight")
    need(result["runner_sha256"] == sha(PREDECESSOR / "run_release.py"),
         "preflight runner binding")
    need(result["source_manifest_sha256"] == BASE_MANIFEST
         == sha(baseline / "inputs/source/MANIFEST.json"), "preflight source pin")
    need(result["source_files"] == 676, "preflight source count")
    need(result["candidate_gzip_sha256"] ==
         {tag: sha(MIXED / f"inputs/THREE-{tag}.json.gz") for tag in ("base", "extra")},
         "preflight candidate bindings")
    need(result["admission_engine_sha256"] == BASE_ENGINE
         == sha(baseline / "admit_composed.py"), "preflight admission engine")
    for field, name in (("source_adaptation_sha256", "SOURCE-ADAPTATION.json"),
                        ("admission_adapter_receipt_sha256", "COMPOSED-ADMISSION-ADAPTER.json")):
        need(result[field] == sha(baseline / name), "preflight adaptation binding")
    need(read(baseline / "COMPOSED-ADMISSION-ADAPTER.json")["adapted_sha256"] == BASE_ENGINE,
         "preflight effective engine")
    need(tree(baseline / "inputs/source", ("MANIFEST.json",))
         == read(baseline / "inputs/source/MANIFEST.json"), "preflight source inventory")
    expected = ["independent-terminal-word", "independent-staged-word", "independent-receiver-word"]
    need(read(baseline / "STAGES.json") == result["completed_reviews"],
         "preflight stage receipt equality")
    need([s["name"] for s in result["completed_reviews"]] == expected,
         "predecessor review coverage")
    for s in result["completed_reviews"]:
        need(s["exit_code"] == 0 and sha(baseline / (s["name"] + ".log")) == s["log_sha256"],
             "completed predecessor review log")
    inventory = read(PREDECESSOR.parent / "sources/PR4076/research/"
                     "staged544-triple-entry-fill/admission/pr3945/PREDECESSOR.json")["files"]
    retained = {n: h for n, h in inventory.items() if not n.startswith("source/")}
    actual = {n: h for n, h in tree(baseline / "inputs").items() if not n.startswith("source/")}
    need(actual == retained, "all 95 retained engine/helper/native-cache input bindings")


def bind_cache(baseline, source, output, native_dirs, fresh_tags=()):
    cache = output / "native-cache"
    shutil.copytree(baseline / "inputs/native-cache", cache)
    receipt = read(baseline / "inputs/NATIVE-RECEIPT.json")
    need(tree(cache) == receipt["cache_files"], "retained parent cache")
    compiler = tree(source / "new/fastnative/vendor")
    bindings = {}
    for pid, tag in TAGS.items():
        origin = native_dirs[tag]
        result = read(origin / "RESULT.json")
        word = source / f"new/borrow/words/BORROW-WORD-43{tag}.json.gz"
        need(result["status"] == "PASS_COMPLETE_T74_NATIVE_REPLAY"
             and result["word_sha256"] == sha(word), "native source input")
        need(result["source_sha256"] == compiler == tree(origin / "source"),
             "exact native compiler closure")
        need([r["step"] for r in result["steps"]] == STAGES
             and all(r["exit_code"] == 0 for r in result["steps"]), "native five-stage coverage")
        native = origin / "native"
        need(read(native / "local/FULL-WORD.json.gz") == read(word), "native full word")
        products = authenticate_native(pid, sha(word), native)
        evidence = "NATIVE" if tag.endswith("-four") else "THREE"
        base = tag.split("-")[0]
        need(read(native / "local/CANONICAL-WORD.json.gz")
             == read(MIXED / f"evidence/{evidence}-CANONICAL-{base}.json.gz"),
             "retained canonical native identity")
        entry = cache / sha(word)
        need(not entry.exists(), "fresh candidate cache entry")
        shutil.copytree(native, entry)
        write(entry / "CACHE.json", dict(word_sha256=sha(word), files=tree(entry)))
        receipt["providers"][tag] = dict(word_sha256=sha(word),
                                         complete_native_files=tree(entry, ("CACHE.json",)))
        bindings[pid] = dict(word_sha256=sha(word), compiler=compiler,
                             native_result_sha256=sha(origin / "RESULT.json"),
                             canonical_sha256=sha(entry / "local/CANONICAL-WORD.json.gz"),
                             scientific_products=products,
                             execution=("executed_by_this_driver" if tag in fresh_tags else
                                        "explicitly_supplied_cache" if tag.endswith("-four") else
                                        "retained_PR4085"))
    receipt.update(source_commit="pr4088-four-provider-admission-v1",
                   manifest_sha256=sha(source / "MANIFEST.json"), cache_files=tree(cache))
    write(output / "NATIVE-RECEIPT.json", receipt)
    write(output / "PROVIDER-BINDINGS.json", bindings)
    return cache


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--checked-preflight", type=Path)
    ap.add_argument("--four-native-base", type=Path)
    ap.add_argument("--four-native-extra", type=Path)
    ap.add_argument("--prepare-only", action="store_true")
    args = ap.parse_args()
    need(__debug__, "inherited admission requires assertions")
    authenticate_sources()
    need(sys.version_info[:2] == (3, 12), "full replay requires Python 3.12")
    need({name: version(name) for name in DEPENDENCIES} == DEPENDENCIES,
         "full replay dependency pins")
    if os.name == "posix":
        # Let the stage's finally block clean its process group on termination.
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(128 + signal.SIGTERM))
    work = args.work.resolve()
    need(not work.exists() and not work.is_relative_to(REPO), "fresh external work")
    work.mkdir(parents=True)
    # Research subprocesses do not inherit account credentials or network configuration.
    env = dict(PATH=os.environ["PATH"], PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
               PYTHONINTMAXSTRDIGITS="0", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1",
               AUDIT_RUNTIME_CONTROLS="fork" if hasattr(os, "fork") else "pickle")
    stages = []

    def run(name, command, timeout=1800):
        started = time.monotonic()
        log = work / (name + ".log")
        with log.open("w") as stream:
            process = subprocess.Popen(command, env=env, stdin=subprocess.DEVNULL,
                                       stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=(os.name == "posix"))
            try:
                code = process.wait(timeout=timeout)
            finally:
                # A bounded replay must also stop descendants after failure or
                # interruption. Proof-relevant children must finish before success.
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                elif process.poll() is None:
                    process.kill()
                process.wait()
        stages.append(dict(name=name, exit_code=code, seconds=time.monotonic()-started,
                           log_sha256=sha(log)))
        write(work / "STAGES.json", stages)
        need(code == 0, "failed " + name + "; inspect its log")
        print("PASS", name, flush=True)

    # These source-specific word and all-character gates supplement the inherited release.
    for name in ("verify.py", "owner_verify.py", "operator_verify.py"):
        run("pr4088-" + name[:-3], [sys.executable, "-B", str(MIXED / name), "--controls"], 300)
    if args.checked_preflight:
        baseline = args.checked_preflight.resolve()
    else:
        # The source reconstruction also runs in the credential-free child
        # environment, rather than importing predecessor code in the caller.
        run("predecessor-preflight",
            [sys.executable, "-B", "-c",
             "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
             "from replay import baseline_preflight; baseline_preflight(Path(sys.argv[2]))",
             str(HERE), str(work / "baseline")], 300)
        baseline = work / "baseline/release-work/preflight"
    check_preflight(baseline)
    source = work / "source"
    _, changes = extend_source(baseline, source)
    changes += extend_engine(baseline, source, work / "admit_mixed.py")
    write(work / "ADAPTATION.json", changes)
    natives = {tag: PREDECESSOR / ("native-" + tag) for tag in ("base", "extra")}
    fresh_tags = set()
    for tag in ("base", "extra"):
        supplied = getattr(args, "four_native_" + tag)
        if supplied:
            natives[tag + "-four"] = supplied.resolve()
        else:
            natives[tag + "-four"] = work / ("native-four-" + tag)
            run("native-four-" + tag, [sys.executable, "-B", str(MIXED / "native/run_native.py"),
                                      str(MIXED / f"inputs/FOUR-{tag}.json.gz"),
                                      str(natives[tag + "-four"])], 900)
            fresh_tags.add(tag + "-four")
    cache = bind_cache(baseline, source, work, natives, fresh_tags)
    source_before = tree(source)
    cache_before = tree(cache)
    original = baseline / "inputs"
    arguments = {
        "source": source, "fill": MIXED / "owner/FILL.json.gz",
        "order": MIXED / "owner/ORDER.json", "dispatch": MIXED / "owner/MIXED-DISPATCH.json",
        "native-cache": cache, "native-receipt": work / "NATIVE-RECEIPT.json",
        "work": work / "admission", "replica-helper-dir": work / "helpers",
        "reconstructor": work / "helpers/reconstruct_replica.py",
        "comparison-claim": REPO / "research/staged544-triple-entry-fill/admission/pr3945/PR3682-CLAIM.json",
        "blocknorm-checker": original / "extension_blocknorm.py",
    }
    command = [sys.executable, "-B", str(work / "admit_mixed.py")]
    for key, value in arguments.items():
        command += ["--" + key, str(value)]
    command += ["--source-profile", "staged544", "--comparison-profile", "pr3682", "--jobs", "1"]
    if args.prepare_only:
        command.append("--prepare-only")
    run("inherited-admission", command, 2400)
    need(tree(source) == source_before and tree(cache) == cache_before,
         "immutable source/cache after admission")
    result = read(work / "admission/RESULT.json")
    need(result["profile"] == read(MIXED / "RESULT.json")["profile"], "complete profile")
    if args.prepare_only:
        need(result["status"] == "PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED",
             "preparation is not admission")
    else:
        need(result["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE",
             "complete inherited release")
    write(work / "RESULT.json", dict(status=result["status"], stages=stages,
                                     admission_result_sha256=sha(work / "admission/RESULT.json"),
                                     source_manifest_sha256=sha(source / "MANIFEST.json"),
                                     runtime=dict(python=sys.version.split()[0],
                                                  dependencies=DEPENDENCIES, platform=sys.platform),
                                     selected_frontier_changed=False))
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
