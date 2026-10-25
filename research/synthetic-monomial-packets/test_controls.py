# SPDX-License-Identifier: Apache-2.0
"""Optimized real CLI corruption controls in a private source-only copy."""

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def private_copy(source, target):
    before = source.lstat()
    need(stat.S_ISREG(before.st_mode), "regular source-only control input")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        need(handle.write(source.read_bytes()) == before.st_size, "complete private write")
    after = target.lstat()
    need(stat.S_ISREG(after.st_mode) and after.st_uid == os.getuid()
         and (after.st_dev, after.st_ino) != (before.st_dev, before.st_ino),
         "owned inode-disjoint private copy")


def invoke(root, expected):
    command = [sys.executable, "-I", "-O", "-Werror", "-B",
               str(root / "research/synthetic-monomial-packets/verify.py"), "--smoke"]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=120)
    need((result.returncode == 0) == expected, "actual optimized CLI outcome: " + result.stderr)
    return {"exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def main():
    tmp = os.environ.get("TMPDIR")
    need(tmp is not None and Path(tmp).is_dir(), "existing private TMPDIR required")
    receipts = {}
    with tempfile.TemporaryDirectory(prefix="phase-controls-", dir=tmp) as directory:
        root = Path(directory)
        sources = json.loads((HERE / "SOURCES.json").read_bytes())
        inputs = [ROOT / row["path"] for row in sources["files"] if row["usage"] == "input"]
        for path in sorted(HERE.iterdir()) + inputs:
            if path.is_file() and not path.is_symlink():
                private_copy(path, root / path.relative_to(ROOT))
        receipts["valid"] = invoke(root, True)
        path = root / "research/synthetic-monomial-packets/packets.py"
        original = path.read_text()
        mutations = {
            "unsigned_wrap": ("back, not parity)", "back, bool(parity))"),
            "lost_quotient": ("divmod(exponent % (2 * self.r), self.r)",
                              "divmod(exponent % self.r, self.r)"),
            "wrong_negation": ("digit = 1 - word.read() + carry", "digit = word.read() + carry"),
            "split_gaussian": ("back = 2 * shift", "back = shift"),
        }
        for name, (old, new) in mutations.items():
            need(original.count(old) == 1, "single semantic mutation")
            path.write_text(original.replace(old, new))
            receipts[name] = invoke(root, False)
        path.write_text(original)
        path = root / "research/synthetic-monomial-packets/checks.py"
        original = path.read_text()
        old = "out, _, _ = apply(out, [-e for e in exponents], width, packets, packing)"
        need(original.count(old) == 1, "single opposite-round mutation")
        path.write_text(original.replace(old, "out, _, _ = apply(out, exponents, width, packets, packing)"))
        receipts["wrong_opposite_phase"] = invoke(root, False)
        path.write_text(original)
        source = root / inputs[0].relative_to(ROOT)
        original_bytes = source.read_bytes()
        source.write_bytes(original_bytes + b"\n# changed source\n")
        receipts["changed_source"] = invoke(root, False)
        source.unlink()
        receipts["missing_source"] = invoke(root, False)
    print("PASS_PACKET_CLI_CONTROLS " + json.dumps(receipts, sort_keys=True))


if __name__ == "__main__":
    main()
