"""Behavioral proof and actual optimized Git-free CLI controls."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arithmetic import depth, need, threshold, upper_certificate
from verify import INPUTS, PACKAGE, ROOT


def rejected(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError("invalid contract was accepted")


def arithmetic_controls():
    need(
        [depth(n) for n in (0, 1, 63, 64, 127, 128, 255, 256)] == [0, 0, 0, 1, 1, 2, 2, 3],
        "literal terminal and floor-child examples",
    )
    need([threshold(n) for n in range(1, 5)] == [64, 128, 256, 448], "inverse depth examples")
    rejected(upper_certificate, 6740)
    rejected(upper_certificate, 6741, 598)
    need(upper_certificate(6742)["margin_numerator"] > 0, "larger coefficient admitted")
    for function, value in (
        (depth, True),
        (depth, -1),
        (threshold, 0),
        (threshold, 262145),
        (depth, 1 << 200000),
    ):
        rejected(function, value)


def export_fixture(destination):
    package = destination / "research" / PACKAGE.name
    package.mkdir(parents=True)
    sources = sorted(PACKAGE.iterdir())
    need(len(sources) <= 32, "bounded package fixture inventory")
    for source in sources:
        if source.suffix in (".py", ".json", ".md"):
            need(source.is_file() and not source.is_symlink(), "regular package export")
            shutil.copyfile(source, package / source.name)
    for relative in INPUTS:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return package


def cli(package, accepted):
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-W", "error", "-B", str(package / "verify.py")],
        cwd=package.parents[1],
        env=environment,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    need((result.returncode == 0) is accepted, "actual optimized CLI acceptance")
    if accepted:
        need("PASS_SELECTED_STOCK_SHARP_INTEGER" in result.stdout, "complete positive CLI")
    else:
        need("ValueError" in result.stderr, "rejection must reach an explicit check")


def cli_controls():
    with tempfile.TemporaryDirectory(prefix="sharp-stock-controls-") as temporary:
        package = export_fixture(Path(temporary))
        cli(package, True)
        receipt = package / "RESULT.json"
        canonical = receipt.read_bytes()
        changed = json.loads(canonical)
        changed["coefficient"] = True
        receipt.write_text(json.dumps(changed))
        cli(package, False)
        receipt.write_bytes(canonical)
        receipt.write_text(
            canonical.decode().replace(
                '"coefficient": 6741', '"coefficient": 6741, "coefficient": 6741'
            )
        )
        cli(package, False)
        receipt.write_bytes(canonical)
        source = package.parents[1] / INPUTS[2]
        original = source.read_bytes()
        source.write_bytes(original + b"\n# changed source\n")
        cli(package, False)
        source.unlink()
        cli(package, False)
        source.write_bytes(original)
        engine = package / "arithmetic.py"
        original_engine = engine.read_text()
        need("COEFFICIENT = 6741" in original_engine, "fault injection target")
        engine.write_text(original_engine.replace("COEFFICIENT = 6741", "COEFFICIENT = 6740"))
        cli(package, False)
        engine.write_text(
            original_engine.replace(
                "width = 64 * ((width + 41) // 42)", "width = 64 * (width // 42)"
            )
        )
        cli(package, False)


if __name__ == "__main__":
    arithmetic_controls()
    cli_controls()
    print("PASS_SHARP_STOCK_CONTROLS groups=2 optimized_cli=7 no_git_required")
