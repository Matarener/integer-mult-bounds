"""Real CLI corruption and restoration controls under optimized Python."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = (
    "MAP.json",
    "RESULT.json",
    "SOURCES.json",
    "ORIGINS.json",
    "PREDECESSOR-WITNESS.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mutate(data, mutation):
    if mutation == "binary":
        data["queries"][0][1] = 1
    elif mutation == "mark":
        data["marks"][0] = [0, 0, 0, 0]
    elif mutation == "premise":
        data["extremal_premises"][0]["minimal_readers"].pop()
    else:
        data["retained_pending_sources"][0]["sha256"] = "0" * 64


def main():
    with tempfile.TemporaryDirectory(prefix="alternate-star-controls-") as directory:
        target = Path(directory)
        for name in FILES:
            (target / name).write_bytes((ROOT / name).read_bytes())
        cases = [
            ("MAP.json", "binary"),
            ("MAP.json", "mark"),
            ("RESULT.json", "premise"),
            ("ORIGINS.json", "hash"),
        ]
        rejected = restored = 0
        for name, mutation in cases:
            original = (target / name).read_bytes()
            data = json.loads(original)
            mutate(data, mutation)
            (target / name).write_text(json.dumps(data))
            for program in ("verify.py", "independent.py"):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-O",
                        "-B",
                        str(ROOT / program),
                        "--data-dir",
                        str(target),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=90,
                    check=False,
                )
                require(result.returncode != 0, f"accepted {mutation} in {program}")
                rejected += 1
            (target / name).write_bytes(original)
            for program in ("verify.py", "independent.py"):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-O",
                        "-B",
                        str(ROOT / program),
                        "--data-dir",
                        str(target),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=90,
                    check=False,
                )
                require(result.returncode == 0, result.stdout + result.stderr)
                restored += 1
    print(
        json.dumps(
            {
                "optimized_corruptions_rejected": rejected,
                "restored_runs_passed": restored,
            }
        )
    )


if __name__ == "__main__":
    main()
