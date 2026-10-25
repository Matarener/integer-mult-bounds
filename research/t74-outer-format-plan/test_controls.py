# SPDX-License-Identifier: Apache-2.0
"""Run actual optimized CLI mutations against private retained runtimes."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from prepare import prepare, require


def main():
    mutations = (
        ("word_order.py", "buffer.step(-1)", "buffer.step(1)", "bridge reverse buffer"),
        (
            "outer_root_plan.py",
            "floor_power(precision, *self.dimension_exponent)",
            "floor_power(precision, 997, 1000)",
            "actual encoded outer dimension law",
        ),
        (
            "outer_layer.py",
            "return self.exit.run(result, width, gaussians)",
            "return result",
            "actual root with complete component-order adapters",
        ),
        (
            "outer_layer.py",
            "entry = self.entrance.run(payload, width, gaussians)",
            "entry = payload",
            "actual root with complete component-order adapters",
        ),
    )
    results = []
    for index, (filename, before, after, message) in enumerate(mutations):
        with tempfile.TemporaryDirectory(prefix="t74-boundary-control-") as temporary:
            controller = prepare(Path(temporary) / "runtime")
            target = controller / filename
            original = target.read_text()
            require(original.count(before) == 1, "one mutation site")
            target.write_text(original.replace(before, after))
            command = [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(HERE / "checks.py"),
                str(controller),
            ]
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=300
            )
            require(
                completed.returncode != 0 and message in completed.stderr,
                "specific optimized CLI rejection: "
                + filename
                + completed.stdout
                + completed.stderr,
            )
            results.append(
                {"control": index + 1, "file": filename, "rejection": message}
            )
    print(json.dumps({"optimized_cli_controls": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
