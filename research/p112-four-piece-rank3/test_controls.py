"""Behavioral boundary controls, including actual optimized CLI failures. Apache-2.0."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import common
import independent
import verify


def rejects(operation, message):
    try:
        operation()
    except ValueError as error:
        common.require(message in str(error), "wrong rejecting control")
    else:
        raise ValueError("control failed to reject")


def cli_mutation(kind):
    with tempfile.TemporaryDirectory(prefix="p112-rank3-control-") as directory:
        root = Path(directory)
        package = root / "research" / common.HERE.name
        package.mkdir(parents=True)
        for source in common.HERE.iterdir():
            if source.is_file() and not source.is_symlink():
                shutil.copyfile(source, package / source.name)
        for relative in (common.DATA, common.GEOMETRY, common.PROOF):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(common.ROOT / relative, target)
        if kind == "receipt":
            target = package / "RESULT.json"
            value = common.read_json(target)
            value["code_intersection_dimension"] = False
            target.write_text(json.dumps(value))
            expected = "exact typed receipt"
        elif kind == "source":
            target = root / common.GEOMETRY
            target.write_bytes(target.read_bytes() + b"\n# changed geometry\n")
            expected = "source digest"
        elif kind == "link":
            target = root / common.DATA
            duplicate = root / "duplicate-data"
            target.rename(duplicate)
            target.symlink_to(duplicate)
            expected = "linked source input"
        else:
            target = package / "RESULT.json"
            target.write_text('{"piece_ranks": [], "piece_ranks": []}')
            expected = "duplicate JSON key"
        environment = dict(
            os.environ, PYTHONPYCACHEPREFIX=str(root / "private-bytecode")
        )
        result = subprocess.run(
            [sys.executable, "-O", "-W", "error", "-B", str(package / "verify.py")],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
        )
        common.require(
            result.returncode != 0 and expected in result.stderr,
            "actual CLI did not reject " + kind,
        )


def main():
    g, roots, live, labels, _ = common.model()
    receipt = common.read_json(common.HERE / "RESULT.json")
    row = receipt["normal_cases"][0]
    independent.check_partition(row, roots, labels, live)
    masks = [
        int(value, 16) for value in row["cover"]["maximum_candidate_partition_witness"]
    ]
    common.require(
        [mask.bit_count() for mask in masks] == [5, 10, 20, 18],
        "five-site positive boundary sizes",
    )
    normal = tuple(row["normal"])
    support = sum(
        1 << i for i, root in enumerate(roots) if root in live and g.dot(root, normal)
    )
    fives, _ = verify.section_census(labels, support, 5)
    sixes, _ = verify.section_census(labels, support, 6)
    rejects(lambda: verify.cover_check(support, fives, sixes, 5), "small-piece cover")
    common.require(
        common.rank_labels([1, 3, 5, 7]) == 3 and common.rank_labels([1, 3, 5, 9]) == 4,
        "rank-three boundary examples",
    )
    rejects(lambda: verify.flat_masks(labels, 4).__next__(), "flat domain")
    common.require(
        not common.same_json({"x": 0}, {"x": False}), "typed integer contract"
    )
    for kind in ("receipt", "source", "link", "duplicate"):
        cli_mutation(kind)
    print(
        "PASS_P112_RANK3_CONTROLS groups=9 optimized_cli_mutants=4 "
        "five_site_positive=yes"
    )


if __name__ == "__main__":
    main()
