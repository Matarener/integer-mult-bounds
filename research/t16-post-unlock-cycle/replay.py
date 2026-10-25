"""Run the unchanged attributed PR1087 T16 admission on a three-file overlay.

Extraction and admission follow Philippe Van Velzen's canonical T16 package
and PR3308's replay. No scientific verifier predicate is changed.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ARCHIVE = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
SELECTED = "research/community-frontier1094-audit/selected-replay.tar.gz"
LOCAL_PINS = "research/complex-t16-two-stage-cycles/LOCAL-PINS.json"
PROVIDER = "candidate/strict/global/base/providers/gauge44/"
INVOICE = "candidate/strict/global/audit/PREFIX-AND-INVOICE.json"
MAX_FILE = 32 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def environment(work):
    env = {
        key: os.environ[key]
        for key in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP")
        if key in os.environ
    }
    env.update(
        PYTHONNOUSERSITE="1",
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUTF8="1",
        PYTHONINTMAXSTRDIGITS="0",
        PYTHONPYCACHEPREFIX=str(work / "bytecode"),
        TMPDIR=str(work),
    )
    return env


def extract_source(main, work):
    source = work / "source"
    source.mkdir()
    with tarfile.open(main / ARCHIVE) as archive:
        members = archive.getmembers()
        need(len(members) <= 500, "source archive member budget")
        need(
            sum(member.size for member in members) <= 128 * 1024 * 1024,
            "archive byte budget",
        )
        for member in members:
            destination = (source / member.name).resolve()
            need(
                member.isfile() and destination.is_relative_to(source.resolve()),
                "unsafe archive member",
            )
            need(member.size <= MAX_FILE, "archive file budget")
        archive.extractall(source, filter="data")
    manifest = json.loads((source / "MANIFEST.json").read_text())
    actual = {
        path.relative_to(source).as_posix(): sha(path)
        for path in source.rglob("*")
        if path.is_file() and path != source / "MANIFEST.json"
    }
    need(actual == manifest, "PR1087 source inventory mismatch")
    return source


def extract_provider(main, work):
    local = work / "local"
    local.mkdir()
    pins = json.loads((main / LOCAL_PINS).read_text())
    need(len(pins) <= 32, "provider file count")
    with tarfile.open(main / SELECTED) as archive:
        for name, expected in pins.items():
            need(Path(name).name == name, "provider path")
            member = archive.getmember(PROVIDER + name)
            need(member.isfile() and member.size <= MAX_FILE, "provider file budget")
            content = archive.extractfile(member).read()
            need(
                hashlib.sha256(content).hexdigest() == expected,
                "selected provider pin: " + name,
            )
            (local / name).write_bytes(content)
    return local


def compare_invoice(main, strict):
    with tarfile.open(main / SELECTED) as archive:
        member = archive.getmember(INVOICE)
        need(member.isfile() and member.size <= MAX_FILE, "selected invoice budget")
        old = json.load(archive.extractfile(member))
    new = json.loads((strict / "global/audit/PREFIX-AND-INVOICE.json").read_text())
    ignored = {"template_sha256", "owner_audit_sha256", "controller_audit_sha256"}
    need(
        {k: v for k, v in old.items() if k not in ignored}
        == {k: v for k, v in new.items() if k not in ignored},
        "complete paid invoice changed",
    )
    bindings = {
        "owner_audit_sha256": "global/audit/OWNERS-AND-PROFILE.json",
        "controller_audit_sha256": "global/audit/ASYNC-AUDIT.json",
    }
    for key, relative in bindings.items():
        need(new[key] == sha(strict / relative), "invoice binding: " + key)
    return new


def run(main, package, work):
    need(__debug__, "unchanged predecessor assertions must remain enabled")
    source = extract_source(main, work)
    local = extract_provider(main, work)
    for name in ("OWNERS.json.gz", "PLAN.json", "SPEC.json"):
        shutil.copyfile(package / "data" / name, source / "data" / name)
    strict = work / "strict"
    command = [
        sys.executable,
        "-E",
        "-S",
        "-B",
        "-X",
        "pycache_prefix=" + str(work / "bytecode"),
        str(source / "verify_t16.py"),
        "--main",
        str(main),
        "--local",
        str(local),
        "--work",
        str(strict),
    ]
    with (work / "strict.log").open("w") as log:
        subprocess.run(
            command,
            env=environment(work),
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
            timeout=300,
        )
    stdout = (work / "strict.log").read_bytes()
    need(len(stdout) <= 65536, "strict stdout budget")
    print(stdout.decode("utf-8"), end="", flush=True)
    result = json.loads((strict / "REPLAY.json").read_text())
    need(
        result["status"] == "PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY",
        "strict replay did not pass",
    )
    need(
        result["controls"]
        == {
            "admission": 69,
            "bit_supplier": 12,
            "independent_t16": 6,
            "controller_mutations": 15,
        },
        "missing strict controls",
    )
    need(
        len(result["stages"]) == 11
        and all(stage["exit_code"] == 0 for stage in result["stages"]),
        "strict stage coverage",
    )
    invoice = compare_invoice(main, strict)
    return result, invoice
