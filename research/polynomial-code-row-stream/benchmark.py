"""Five interleaved fresh-process triples of the complete nine-screen replay."""

import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent


def main():
    engines = ("original", "cached", "incremental")
    samples = {key: [] for key in engines}
    expected = None
    sample_order = []
    for _ in range(5):
        for engine in engines:
            command = [sys.executable, "-I", "-W", "error", "-B",
                       str(PACKAGE / "replay.py"), "--engine", engine]
            start = time.perf_counter()
            result = subprocess.run(command, capture_output=True, timeout=60, check=False)
            elapsed = time.perf_counter() - start
            if result.returncode:
                raise ValueError("Replay failed: " + result.stderr.decode())
            if result.stderr:
                raise ValueError("Replay emitted stderr: " + result.stderr.decode())
            if expected is None:
                expected = result.stdout
            if result.stdout != expected:
                raise ValueError("Complete replay outputs differ")
            samples[engine].append(elapsed)
            sample_order.append(engine)
    receipt = {"python": platform.python_version(), "platform": platform.platform(),
               "samples_seconds": samples, "sample_order": sample_order,
               "errors": 0, "complete_replays": 15, "logical_cpus": os.cpu_count(),
               "source_manifest_sha256": hashlib.sha256(
                   (PACKAGE / "SOURCES.json").read_bytes()).hexdigest(),
               "stdout_sha256": hashlib.sha256(expected).hexdigest(),
               "script_sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                                 for name in ("stream.py", "replay.py", "benchmark.py")},
               "summary_seconds": {key: {"median": statistics.median(values),
                                         "min": min(values), "max": max(values)}
                                   for key, values in samples.items()}}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
