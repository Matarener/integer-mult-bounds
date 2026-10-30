"""Git-free publication orchestration for the unchanged frozen H25 v4 payload.

Apache-2.0. Publication custody/copy/cleanup costs are separate from the already
qualified six samples. No replay here creates another performance-factor claim.
"""
from hashlib import sha256
import fcntl
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parent
PAYLOAD = ROOT / "payload"
STAGE_SHA256 = "558eebbc1dc65e42bbcb3ffd9973f8bc86641a3539493ecc1d53d8077c39cdbc"
RUNNER_SHA256 = "b74366a925dd44c0e95a7ad87aa1505cbdcad9fefcb9360d77d6459679f102be"
INNER_TIMEOUT = 150
RSS_CAP = 1024 ** 3
ALLOWED_JOBS = ("finite-all", "finite-O-all", "full-none", "full-all")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    hasher = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def _relative(name):
    need(type(name) is str, "Manifest path must be text")
    path = PurePosixPath(name)
    need(bool(path.parts) and not path.is_absolute() and ".." not in path.parts and
         "\\" not in name and path.as_posix() == name,
         "Noncanonical publication path: " + name)
    return path


def _files(directory):
    need(directory.is_dir() and not directory.is_symlink(), "Regular source directory required")
    result = {}
    for path in sorted(directory.rglob("*")):
        need(not path.is_symlink(), "Symlink in publication source: " + str(path))
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = path
        else:
            need(path.is_dir(), "Special file in publication source: " + str(path))
    return result


def _stage_inventory(directory, declared, require_modes):
    files = _files(directory)
    need(set(files) == set(declared["files"]) | {"STAGE.json"}, "Exact v4 payload file census")
    need(digest(files["STAGE.json"]) == STAGE_SHA256, "Exact v4 stage manifest bytes")
    for name, row in declared["files"].items():
        _relative(name)
        need(digest(files[name]) == row["sha256"], "Exact v4 payload bytes: " + name)
        if require_modes:
            need(stat.S_IMODE(files[name].stat().st_mode) == row["mode"], "Exact copied v4 mode: " + name)
    if require_modes:
        need(stat.S_IMODE(files["STAGE.json"].stat().st_mode) == 0o444, "Readonly copied STAGE manifest")


def authenticate():
    """Authenticate bytes; publication checkout write/execute bits may differ.

    CODE-SOURCES.json is bound by committed package identity, not a self-hash.
    Its raw digest and current protected-file modes are returned for after-run
    equality. STAGE.json has the independent fixed v4 digest above.
    """
    raw = (ROOT / "CODE-SOURCES.json").read_bytes()
    manifest = json.loads(raw)
    need(manifest.get("schema_version") == 1 and type(manifest.get("files")) is dict,
         "Publication source manifest version")
    files = _files(ROOT)
    modes = {}
    for name, expected in manifest["files"].items():
        _relative(name)
        need(name != "CODE-SOURCES.json", "Source manifest cannot hash itself")
        need(name in files and type(expected) is str and len(expected) == 64 and
             digest(files[name]) == expected, "Exact protected publication source: " + name)
        modes[name] = stat.S_IMODE(files[name].stat().st_mode)
    expected_code = {name for name in manifest["files"] if Path(name).suffix in (".py", ".c")}
    actual_code = {name for name in files if Path(name).suffix in (".py", ".c")}
    need(actual_code == expected_code, "Complete protected publication code census")
    need(digest(PAYLOAD / "STAGE.json") == STAGE_SHA256, "Frozen v4 stage identity")
    declared = json.loads((PAYLOAD / "STAGE.json").read_bytes())
    need(declared.get("schema") == "h25-bookkeeping-immutable-stage-v1" and
         len(declared["files"]) == 160 and declared["runner_sha256"] == RUNNER_SHA256,
         "Frozen v4 payload contract")
    payload_names = {"payload/" + name for name in declared["files"]} | {"payload/STAGE.json"}
    need(payload_names <= set(manifest["files"]), "Entire payload must be protected by publication manifest")
    _stage_inventory(PAYLOAD, declared, False)
    modes["CODE-SOURCES.json"] = stat.S_IMODE((ROOT / "CODE-SOURCES.json").stat().st_mode)
    return {"manifest_sha256": sha256(raw).hexdigest(), "stage": declared,
            "protected_file_modes": modes}


def _protected_root():
    # Generic exports retain research/<package>; standalone package directories
    # also work without treating their entire filesystem parent as a repository.
    return ROOT.parent.parent if ROOT.parent.name == "research" else ROOT


def external(path, *, new=True):
    path = Path(path).resolve()
    need(not path.is_relative_to(ROOT) and not path.is_relative_to(_protected_root()),
         "Evidence must be outside the publication package/repository")
    if new:
        need(not path.exists(), "Fresh external evidence directory required")
    return path


def _temporary_base():
    # Avoid tempfile.gettempdir(): its first call may probe TMPDIR by writing a
    # test file before we have rejected an immutable/package-local destination.
    candidates = [Path(value) for value in (os.environ.get("TMPDIR"),) if value]
    candidates.extend((Path("/tmp"), Path("/var/tmp")))
    for candidate in candidates:
        candidate = candidate.resolve()
        if (candidate.is_dir() and not candidate.is_relative_to(_protected_root()) and
                os.access(candidate, os.W_OK | os.X_OK)):
            return candidate
    raise ValueError("No writable temporary directory outside the immutable publication root")


def _mark_owned(directory):
    (directory / "PUBLICATION-WORKSPACE.json").write_text(json.dumps({
        "schema": "h25-private-publication-workspace-v1", "path": str(directory),
        "stage_sha256": STAGE_SHA256}, sort_keys=True) + "\n")


def temporary_parent():
    directory = Path(tempfile.mkdtemp(prefix="h25-bookkeeping-check-", dir=_temporary_base())).resolve()
    _mark_owned(directory)
    return directory


def cleanup_owned(directory):
    """Remove only a wrapper-created external workspace after all checks pass."""
    directory = external(directory, new=False)
    marker = json.loads((directory / "PUBLICATION-WORKSPACE.json").read_text())
    need(marker == {"schema": "h25-private-publication-workspace-v1", "path": str(directory),
                    "stage_sha256": STAGE_SHA256}, "Fresh private workspace ownership required")
    need(directory.is_dir() and not directory.is_symlink(), "Private cleanup root must be a directory")
    # Readonly copied files need no chmod; only their private parent directories
    # become writable so unlink can succeed. Never follow or chmod symlinks.
    for path in directory.rglob("*"):
        if path.is_dir() and not path.is_symlink():
            path.chmod(0o755)
    directory.chmod(0o755)
    shutil.rmtree(directory)


def source_module(name, path, expected):
    raw = path.read_bytes()
    need(not path.is_symlink() and sha256(raw).hexdigest() == expected, "Authenticated source module: " + str(path))
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def _copy_stage(directory, declared):
    stage = directory / "stages/v4"
    stage.parent.mkdir()
    shutil.copytree(PAYLOAD, stage)
    # Git stores executable status, not readonly permissions. Recreate the exact
    # measured stage modes exclusively within this fresh external copy.
    for name, row in declared["files"].items():
        (stage / name).chmod(row["mode"])
    (stage / "STAGE.json").chmod(0o444)
    for path in stage.rglob("*"):
        if path.is_dir():
            need(not path.is_symlink(), "Symlink in private stage copy")
            path.chmod(0o555)
    stage.chmod(0o555)
    _stage_inventory(stage, declared, True)
    return stage


def _check_scientific(job, guard, science):
    need(guard["status"] == "PASS" and guard["source_bytes_and_modes_unchanged"],
         "Fresh bounded runner must pass with unchanged copied sources")
    finite = job.startswith("finite-")
    lanes = "none" if job == "full-none" else "all"
    need(science["lanes"] == lanes, "Requested lane selection must be observed")
    if finite:
        need(science["status"] == "H25_BOOKKEEPING_FINITE_PASS" and
             science["optimized"] == (1 if job == "finite-O-all" else 0),
             "Complete finite union in requested interpreter mode")
        original, additions = science["original_controls"], science["new_controls"]
    else:
        need(science["status"] == "FULL_NETWORK_COMPLETE_PASS" and science["mode"] == "candidate",
             "Complete assertion-on native caller")
        anchor = json.loads((PAYLOAD / "baseline/anchor.json").read_text())
        need(science["science"] == anchor["science"], "Full exact historical science equality")
        original, additions = science["finite_controls"], science["bookkeeping"]["new_controls"]
    need(original["status"] == "FINITE_NATIVE_GF2_CONTROLS_PASS", "Original independent controls retained")
    need(set(additions) == ({"sets", "guards", "trace", "trace_entry_freshness"} if lanes == "all" else set()),
         "Complete requested new-control union")


def run(job, evidence):
    """Run one fresh fixed job; retain all evidence; never retry or select timings."""
    need(job in ALLOWED_JOBS, "Fixed finite/full publication job required")
    need(sys.platform == "linux" and sys.implementation.name == "cpython" and
         sys.version_info[:2] == (3, 12), "Linux CPython3.12 required; no dependency installation")
    need(sys.flags.optimize in (0, 1), "Only deliberate normal/-O finite modes are supported")
    need(job.startswith("finite-") or sys.flags.optimize == 0, "Full caller requires original assertions")
    need(Path("/usr/bin/python3.12").is_file() and Path("/usr/bin/time").is_file(),
         "System CPython3.12 and GNU time required; compiler and Python headers are also required")
    before = authenticate()
    evidence = external(evidence)
    lock_path = _temporary_base() / ("croc-h25-bookkeeping-" + STAGE_SHA256[:20] + ".lock")
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(lock_path, flags, 0o600), "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        evidence.mkdir(parents=True)
        _mark_owned(evidence)
        publication = {"schema": "h25-publication-replay-v1", "status": "PREPARING",
            "job": job, "stage_sha256": STAGE_SHA256, "runner_sha256": RUNNER_SHA256,
            "publication_manifest_sha256": before["manifest_sha256"],
            "runner_overrides": {"HERE": str(evidence), "TIMEOUT": INNER_TIMEOUT},
            "sampled_process_group_rss_bytes_cap": RSS_CAP,
            "execution_phase_aggregate_seconds": 600, "registered_outer_timeout_seconds": 180,
            "fresh_private_stage_permissions_restored": False,
            "automatic_retries": 0, "fixed_benchmark_sample": False,
            "hosted_performance_factor_claim": False,
            "cost_scope": "Publication authentication, private copy, mode restoration and cleanup are additional correctness-wrapper costs, not replacement performance samples."}
        receipt_path = evidence / "PUBLICATION-REPLAY.json"
        receipt_path.write_text(json.dumps(publication, indent=2, sort_keys=True) + "\n")
        old_argv = sys.argv[:]
        try:
            stage = _copy_stage(evidence, before["stage"])
            publication["fresh_private_stage_permissions_restored"] = True
            (evidence / "control").mkdir()
            (evidence / "control/EXECUTION-PHASE.json").write_text(json.dumps({
                "phase": "PUBLICATION_CORRECTNESS_ONLY", "aggregate_cap_seconds": 600,
                "single_job": True, "no_performance_selection": True}, sort_keys=True) + "\n")
            runner = source_module("_h25_frozen_publication_runner", stage / "run_guarded.py", RUNNER_SHA256)
            runner.HERE = evidence
            runner.TIMEOUT = INNER_TIMEOUT
            need(runner.RSS_CAP == RSS_CAP, "Frozen one-GiB process-group limit")
            sys.argv = [str(stage / "run_guarded.py"), "v4", job, "replay"]
            runner.main()
            guard_path = evidence / "runtime/runs/replay/receipt.json"
            scientific_path = evidence / "runtime/runs/replay/science/receipt.json"
            guard = json.loads(guard_path.read_text())
            science = json.loads(scientific_path.read_text())
            _check_scientific(job, guard, science)
            _stage_inventory(stage, before["stage"], True)
            need(authenticate() == before, "Publication bytes/modes changed during correctness replay")
            publication.update(status="PASS", package_bytes_and_modes_unchanged=True,
                               guard_receipt_sha256=digest(guard_path), scientific_receipt_sha256=digest(scientific_path))
            receipt_path.write_text(json.dumps(publication, indent=2, sort_keys=True) + "\n")
            return {"publication": publication, "guard": guard, "scientific": science, "evidence": str(evidence)}
        except BaseException as error:
            publication.update(status="FAIL", exception_type=type(error).__name__, exception=str(error))
            receipt_path.write_text(json.dumps(publication, indent=2, sort_keys=True) + "\n")
            error.add_note("Publication replay evidence retained at " + str(evidence))
            raise
        finally:
            sys.argv = old_argv
