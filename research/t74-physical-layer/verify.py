# SPDX-License-Identifier: Apache-2.0
"""Bounded cold replays for source/native, complete binding and physical joins."""
import argparse
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundles import need, opened


def command(name, script, arguments, work, environment, timeout):
    started = time.monotonic()
    argv = [sys.executable, "-B", str(script), *map(str, arguments)]
    with (work / (name + ".log")).open("w") as log:
        completed = subprocess.run(argv, cwd=work, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
    need(completed.returncode == 0, name + " failed: " + (work / (name + ".log")).read_text()[-6000:])
    print(json.dumps(dict(check=name, seconds=round(time.monotonic()-started, 3), status="PASS")), flush=True)


def report(name, function, *arguments):
    started = time.monotonic()
    value = function(*arguments)
    print(json.dumps(dict(check=name, seconds=round(time.monotonic()-started, 3), result=value), sort_keys=True), flush=True)


def run(suite):
    with opened() as (work, source, prepared):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
        for name in ("PYTHONOPTIMIZE", "PYTHONPATH", "WITNESS_SPEC", "WITNESS_RECORD", "WITNESS_DISCOVER"):
            environment.pop(name, None)
        try:
            if suite == "native":
                identities = types.ModuleType("retained_t74_generated_identity")
                path = source / "code/generated_identity.py"
                exec(compile(path.read_bytes(), str(path), "exec", optimize=0), identities.__dict__)
                for tag, pid in (("base", "gauge44"), ("extra", "extra")):
                    out = work / ("fresh-native-" + tag)
                    command("native-" + tag, source / "new/fastnative/run_native.py",
                            [source / ("new/borrow/words/BORROW-WORD-43" + tag + ".json.gz"), out],
                            work, environment, 240)
                    need(identities.artifact_identities(out / "native/local") ==
                         identities.artifact_identities(prepared / "bound/base/providers" / pid),
                         "all seven regenerated proof-relevant native artifacts: " + pid)
                report("compilation", importlib.import_module("check_compilation").run, prepared)
                report("compiled-local-endpoints", importlib.import_module("check_local_modular").run, prepared)
            elif suite == "binding":
                environment["WITNESS_SPEC"] = str(prepared / "input-package/new/CONTROLLER-SPEC.json")
                command("global-source-audit", source / "code/audit_allcold.py",
                        [prepared / "bound/base", prepared / "hosted", work / "fresh-audit.json"],
                        work, environment, 120)
                binding = importlib.import_module("binding").T74Binding(prepared)
                report("complete-binding", lambda: dict(binding.inventory(), profile=binding.check_profile()))
                report("dispatch", importlib.import_module("check_dispatch").run, prepared)
                report("monomials", importlib.import_module("check_monomials").run, prepared)
                report("height", importlib.import_module("check_t74_bounds").run, prepared)
                report("layer-budget", importlib.import_module("layer_budget").run)
            else:
                need(suite == "physical", "known replay group")
                runtime = importlib.import_module("check_runtime")
                report("private-Z-positive", runtime.fixture)
                report("private-Z-reject", runtime.fixture, True)
                root = importlib.import_module("check_root_runtime")
                report("root-direct", root.run, False)
                report("root-fast", root.run, True)
        finally:
            if "predecessor" in sys.modules:
                sys.modules["predecessor"].close_test_imports()
    print("PASS_T74_PHYSICAL_LAYER_" + suite.upper(), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("native", "binding", "physical"), required=True)
    run(parser.parse_args().suite)
