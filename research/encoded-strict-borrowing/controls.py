# SPDX-License-Identifier: Apache-2.0
"""Corrupt actual exported public CLIs, with distinct owned regular byte copies."""

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import require

HERE = Path(__file__).resolve().parent


def copy_package(destination):
    files = sorted(HERE.iterdir())
    require(len(files) <= 32, "bounded control package")
    records = []
    for source in files:
        st = source.lstat()
        require(
            stat.S_ISREG(st.st_mode) and st.st_uid == os.getuid(),
            "owned regular source for control copy",
        )
        require(st.st_size <= 500000, "bounded source copy")
        target = destination / source.name
        with target.open("xb") as output:
            output.write(source.read_bytes())
        dt = target.lstat()
        require(
            stat.S_ISREG(dt.st_mode)
            and dt.st_uid == os.getuid()
            and (dt.st_dev, dt.st_ino) != (st.st_dev, st.st_ino),
            "distinct owned regular control copy",
        )
        records.append((source.name, source.read_bytes()))
    return records


def mutate(root, name):
    path = root / "strict_selector.py"
    text = path.read_text()
    if name == "lost_strict_increment":
        text = text.replace("threshold.increment()", "# omitted strict increment")
    elif name == "saturated_final_rows":
        text = text.replace(
            'candidate.replace("rows", power(work.get("radix"), work.get(borrowed_name)))',
            "# omitted exact final materialization",
        )
    elif name == "omitted_compatibility":
        text = text.replace("stock.multiply_small(compatibility)", "pass")
    elif name == "covering_instead_of_strict":
        text = text.replace(
            'candidate.get("threshold")) == 0', 'candidate.get("stock")) == 0'
        )
    elif name in ("archive_drift", "proof_drift"):
        target = root / ("pr3518.tar" if name == "archive_drift" else "PR3503-PROOF.md")
        raw = target.read_bytes()
        target.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        return
    elif name == "boolean_receipt":
        target = root / "RESULT.json"
        receipt = json.loads(target.read_text())
        receipt["plans"]["cases"] = True
        target.write_text(json.dumps(receipt))
        return
    else:
        raise ValueError("unknown bounded mutant")
    require(text != path.read_text(), "mutant reaches actual implementation")
    path.write_text(text)


def main():
    mutants = (
        "lost_strict_increment",
        "saturated_final_rows",
        "omitted_compatibility",
        "covering_instead_of_strict",
        "archive_drift",
        "proof_drift",
        "boolean_receipt",
    )
    results = []
    for name in mutants:
        with TemporaryDirectory(prefix="strict-control-") as temporary:
            root = Path(temporary)
            before = copy_package(root)
            mutate(root, name)
            argv = [
                sys.executable,
                "-I",
                "-O",
                "-W",
                "error",
                "-B",
                str(root / "verify.py"),
            ]
            run = subprocess.run(argv, capture_output=True, text=True, timeout=90)
            require(
                run.returncode != 0 and "ValueError" in run.stderr,
                "actual optimized public CLI rejects " + name,
            )
            require(
                all((HERE / filename).read_bytes() == raw for filename, raw in before),
                "control preserves original package",
            )
            results.append(
                dict(
                    mutant=name,
                    exit=run.returncode,
                    diagnostic=run.stderr.strip().splitlines()[-1],
                )
            )
    print(
        json.dumps(
            dict(status="PASS_STRICT_SELECTOR_CLI_CONTROLS", controls=results),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
