"""Five alternating complete-command pairs; produced by Nick Petalas, Apache-2.0."""
import hashlib
import json
import os
import platform
import statistics
import sys

from incidence import require
from replay import PACKAGE, authenticate
from verify import captured


def measure(scope):
    samples = {"scalar": [], "bitset": []}
    expected = None
    transcript_hashes = []
    for pair in range(5):
        order = ("scalar", "bitset") if pair % 2 == 0 else ("bitset", "scalar")
        for engine in order:
            elapsed, output = captured(scope, engine)
            if expected is None:
                expected = output
            require(output == expected, "complete benchmark output mismatch")
            samples[engine].append(elapsed)
            transcript_hashes.append(hashlib.sha256(output.encode()).hexdigest())
    medians = {key: statistics.median(values) for key, values in samples.items()}
    return {"seconds": samples, "median_seconds": medians,
            "range_seconds": {key: [min(values), max(values)] for key, values in samples.items()},
            "reduction": 1 - medians["bitset"] / medians["scalar"],
            "completed_commands": len(transcript_hashes), "errors": 0,
            "transcript_sha256": transcript_hashes}


def main():
    require(len(sys.argv) == 1, "benchmark writes JSON to stdout")
    authenticate()
    record = {"schema_version": 1, "python": sys.version,
              "platform": platform.platform(), "numpy": __import__("numpy").__version__,
              "logical_cpus": os.cpu_count(), "load_average_before": os.getloadavg(),
              "method": "five alternating fresh-process pairs per complete command; all work timed"}
    for scope in ("span", "complete"):
        record[scope] = measure(scope)
    record["load_average_after"] = os.getloadavg()
    record["implementation_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.glob("*.py"))}
    record["source_manifest_sha256"] = hashlib.sha256((PACKAGE / "SOURCES.json").read_bytes()).hexdigest()
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
