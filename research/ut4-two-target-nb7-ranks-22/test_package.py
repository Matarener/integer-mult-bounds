#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Relocation, -O/need, certificate corruption and independent-import controls.

Full census replay is owned by verify.py / independent.py under research_package
(each ~400s). This harness exercises the cheap gates under -O within the 1200s
replay budget. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*")
        if p.is_file()
    }


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix="nb7-22-pkg-") as directory:
        target = Path(directory) / "isolated-package"
        shutil.copytree(
            HERE,
            target,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.txt"),
        )

        repo = HERE.parents[1]
        env = os.environ.copy()
        env.pop("PYTHONOPTIMIZE", None)
        env["UT4_NB7_22_CONTROLS_ONLY"] = "1"

        def run(script="verify.py", expected_error=None, controls_only=True):
            run_env = env if controls_only else {k: v for k, v in env.items() if k != "UT4_NB7_22_CONTROLS_ONLY"}
            result = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(target / script)],
                cwd=str(repo),
                text=True,
                capture_output=True,
                timeout=120,
                env=run_env,
            )
            if expected_error is None:
                need(
                    result.returncode == 0
                    and "PASS_UT4_TWO_TARGET_NO_NB7_RANKS_22" in result.stdout,
                    "isolated replay failed: " + result.stderr + result.stdout,
                )
            else:
                need(
                    result.returncode != 0
                    and expected_error in (result.stderr + result.stdout),
                    "corruption escaped or wrong reason: " + result.stderr + result.stdout,
                )

        before = inventory(target)
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o444)
        run()
        need(inventory(target) == before, "normal replay mutated the isolated package")
        checks.append("isolated-optimized-read-only-replay")
        for path in target.rglob("*"):
            if path.is_file():
                path.chmod(0o644)

        import ast

        tree = ast.parse((target / "independent.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                need(
                    all(a.name.split(".")[0] != "verify" for a in node.names),
                    "independent imports verify",
                )
            if isinstance(node, ast.ImportFrom) and node.module:
                need(node.module.split(".")[0] != "verify", "independent imports verify")
        checks.append("independent-no-verify-import")

        # Subsample census: a few rank-(2,2) middles must contribute zero I-pairs.
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-O",
                "-B",
                "-c",
                "import sys; sys.path.insert(0, %r); "
                "from core import middle_sequences, ranks_XY, side_zero_keys, count_key_pairs, need; "
                "n=0\n"
                "for bt in middle_sequences(7, True):\n"
                "    if ranks_XY(bt)!=(2,2): continue\n"
                "    keys,_=side_zero_keys(bt)\n"
                "    need(count_key_pairs(keys)==0, 'subsample I-pair')\n"
                "    n+=1\n"
                "    if n>=32: break\n"
                "need(n==32, 'subsample size')\n"
                "print('PASS_SUBSAMPLE', n)\n" % (str(target),),
            ],
            cwd=str(repo),
            text=True,
            capture_output=True,
            timeout=60,
            env={k: v for k, v in env.items() if k != "UT4_NB7_22_CONTROLS_ONLY"},
        )
        need(
            result.returncode == 0 and "PASS_SUBSAMPLE" in result.stdout,
            "subsample failed: " + result.stderr + result.stdout,
        )
        checks.append("subsample-zero-pairs")

        def mutate(name, filename, edit, message):
            path = target / filename
            saved = path.read_bytes()
            path.write_bytes(edit(saved))
            try:
                run(expected_error=message)
                checks.append(name)
            finally:
                path.write_bytes(saved)

        def json_edit(data, edit):
            obj = json.loads(data)
            edit(obj)
            return (json.dumps(obj, sort_keys=True) + "\n").encode()

        # Explicit certificate mismatch (full census path checks this against the
        # recomputed census; here we exercise check_certificate directly).
        mini = subprocess.run(
            [
                sys.executable,
                "-I",
                "-O",
                "-B",
                "-c",
                "import sys; sys.path.insert(0, %r); import verify; "
                "cert=verify.read_json(verify.HERE/'CERTIFICATE.json'); "
                "fake=dict(cert); fake['key_pairs_abc_cba_I']=1; "
                "\ntry:\n"
                " verify.check_certificate({k:cert[k] for k in verify.CERT_KEYS}, expected=fake)\n"
                " raise SystemExit('escaped')\n"
                "except ValueError as e:\n"
                " assert 'certificate mismatch' in str(e), e\n"
                " print('PASS_CERT_MISMATCH')\n" % (str(target),),
            ],
            cwd=str(repo),
            text=True,
            capture_output=True,
            timeout=30,
            env={k: v for k, v in env.items() if k != "UT4_NB7_22_CONTROLS_ONLY"},
        )
        need(
            mini.returncode == 0 and "PASS_CERT_MISMATCH" in mini.stdout,
            "certificate mismatch control failed: " + mini.stderr + mini.stdout,
        )
        checks.append("corrupted-certificate-pairs")

        mutate(
            "duplicate-json-key",
            "CERTIFICATE.json",
            lambda data: b'{"status":"first","status":"second"}\n',
            "duplicate JSON key",
        )
        mutate(
            "sources-base-drift",
            "SOURCES.json",
            lambda data: json_edit(data, lambda x: x.update(base_commit="0" * 40)),
            "base pin",
        )

        need(inventory(target) == before, "corruption controls failed to restore source bytes")
        checks.append("need-survives-python-O")

    print("PASS_UT4_TWO_TARGET_NO_NB7_RANKS_22_PACKAGE_CONTROLS", "checks=" + str(len(checks)))
    print(json.dumps(checks))


if __name__ == "__main__":
    main()
