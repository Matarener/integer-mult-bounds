#!/usr/bin/env python3
"""Show that the R439 scalar saving leaves the paid histogram unchanged.

Four recorded words have different ADD counts and the same nine rank-7
copies. The owner check compares every word with one profile. This checker
does not import that replay.
"""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_R439_SCALAR_HISTOGRAM adds_differ=true no_new_kappa"
ORDER = ("helper_star", "composition", "candidate", "pair_control")


def fail(message):
    raise SystemExit("FAIL_R439_SCALAR_HISTOGRAM " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rank_mass(profile):
    return sum(rank * count for rank, count in profile.items())


def adds_differ(counts):
    return len(set(counts)) == len(counts) and len(counts) > 1


def profile_assignment(source):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PROFILE":
                    return ast.literal_eval(node.value)
    raise ValueError("PROFILE")


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/r439-bsection-stars-seed01/README.md",
        "research/r439-bsection-stars-seed01/CERTIFICATE.json",
        "research/r439-bsection-stars-seed01/verify.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    note = (ROOT / "research/r439-bsection-stars-seed01/README.md").read_text(encoding="utf-8")
    checker = (ROOT / "research/r439-bsection-stars-seed01/verify.py").read_text(encoding="utf-8")
    certificate = json.loads(
        (ROOT / "research/r439-bsection-stars-seed01/CERTIFICATE.json").read_text(encoding="utf-8")
    )
    require(
        "profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` (rank mass 5,129) are unchanged."
        in note,
        "the histogram sentence moved",
    )
    require(
        "need(own['profile'] == PROFILE and sum(r * c for r, c in own['profile'].items()) == 5129, name + ' paid profile')"
        in checker,
        "the profile check moved",
    )
    profile = profile_assignment(checker)
    require(profile == {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}, "the profile constant moved")
    require(rank_mass(profile) == 5129, "the rank mass moved")
    counts = []
    for name in ORDER:
        word = certificate["words"][name]
        require(word["copy_ranks"] == [7, 7, 7, 7, 7, 7, 7, 7, 7], "copy ranks moved " + name)
        require(word["exporter"]["copies"] == 9 and word["exporter"]["erasures"] == 9, "copy count moved " + name)
        counts.append(word["literal"]["native_ADDs"])
        require(word["exporter"]["adds"] == word["literal"]["native_ADDs"], "ADD fields disagree " + name)
    require(counts == [11783, 11515, 11500, 11715], "the ADD counts moved")
    require(adds_differ(counts), "the ADD counts are not distinct")
    require(certificate["new_kappa_claim"] is False, "the certificate claims a new kappa")
    return {
        "profile_mass": 5129,
        "copy_rank": 7,
        "copies": 9,
        "native_adds": counts,
        "adds_differ": True,
        "histogram_shared": True,
        "new_kappa_claim": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
