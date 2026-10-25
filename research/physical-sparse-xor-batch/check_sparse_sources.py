"""Exercise the actual source CLI and cross-cohort rejection before execution."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

import sparse_sources as sources
from sparse_sources import require


def cli(name, path):
    result = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(sources.HERE / "verify.py"),
                             "--suite", "source-check", "--archive-name", name, "--archive", str(path)],
                            capture_output=True, text=True, timeout=30)
    return result


def run():
    positive = negative = 0
    with tempfile.TemporaryDirectory(prefix="sparse-source-controls-") as directory:
        root = Path(directory)
        for name in sources.PINS:
            path = sources.HERE / "inputs" / name
            result = cli(name, path)
            require(result.returncode == 0 and result.stdout.strip() == "PASS_SPARSE_SOURCE_BYTES"
                    and not result.stderr, "actual optimized source CLI accepts pinned bytes without cleanup warnings")
            positive += 1
            changed = root / name
            data = path.read_bytes()
            changed.write_bytes(bytes([data[0] ^ 1]) + data[1:])
            result = cli(name, changed)
            require(result.returncode != 0 and "pinned source export" in result.stderr,
                    "actual CLI rejects altered export bytes before extraction")
            negative += 1
        name = "compact-export.tar"
        link = root / "alias.tar"
        link.symlink_to(sources.HERE / "inputs" / name)
        for path in (link, root / "missing.tar"):
            result = cli(name, path)
            require(result.returncode != 0 and "regular source export" in result.stderr, "actual CLI rejects alias/missing source")
            negative += 1
        with patch.dict(sys.modules, {"native_sources": object()}):
            try:
                with sources.opened():
                    raise ValueError("entered stale cohort")
            except ValueError as exc:
                require(str(exc) == "cold sparse-batch namespace", "stale cohort rejection")
        with sources.opened() as state:
            copied = root / "backend"
            shutil.copytree(state.backend, copied)
            changed = copied / "ordinary.py"
            changed.write_bytes(changed.read_bytes() + b"\n# copied mutation control\n")
            try:
                sources.compare_backend(state.roots["ordinary-rate-export.tar"], copied)
            except ValueError as exc:
                require(str(exc) == "ordinary cohort bytes: ordinary.py", "changed actual cohort rejection")
            else:
                raise ValueError("changed ordinary cohort accepted")
            from compact_control import Control
            from compact_engine import CompactEngine
            from macro_code import Code
            from sparse_control import SparseControl
            from sparse_engine import SparseEngine
            require(SparseControl.execute_state is Control.execute_state
                    and SparseEngine.swap is CompactEngine.swap and SparseEngine.rearm is CompactEngine.rearm,
                    "retained inverse and physical-call ownership methods")
            native = state.ordinary.Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                                             SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=64)
            old = native.profile
            try:
                SparseEngine(native)
            except ValueError as exc:
                require(str(exc) == "retuned native from the authenticated cohort", "old ordinary profile rejection")
            else:
                raise ValueError("old ordinary rate accepted")
            require(native.profile is old and not native.closed, "profile rejection precedes native ownership")
    return dict(status="PASS_SPARSE_SOURCE_CONTROLS", positive_cli=positive, negative_cli=negative,
                backend_files=23, stale_cohort_rejected=True, altered_cohort_rejected=True,
                old_profile_rejected=True)
