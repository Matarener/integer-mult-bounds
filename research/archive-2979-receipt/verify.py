#!/usr/bin/env python3
"""Disposition receipt for the archived PR 2979 tree.

The archive lists 112 blobs. This checker compares each listed oid with the
blob at the pinned base commit. It does not import the rank-7 package.
"""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ARCHIVE_2979_RECEIPT blobs_match_main=true no_new_kappa"
HEAD = "be191346391661f4d35fc0d1508d0a6029572576"


def fail(message):
    raise SystemExit("FAIL_ARCHIVE_2979_RECEIPT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def blob_at(base, path):
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"{base}:{path}"],
        text=True,
    ).strip()


def count_matches(pairs):
    return sum(1 for left, right in pairs if left == right)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "docs/research/pr-intake-evidence/archive-pr2979.json",
        "docs/research/pr-intake-decisions.json",
        "docs/research/pr-ledger.md",
        "CONTRIBUTORS.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    return sources["base_commit"]


def evaluate():
    base = authenticate()
    archive = json.loads(
        (ROOT / "docs/research/pr-intake-evidence/archive-pr2979.json").read_text(encoding="utf-8")
    )
    decisions = json.loads((ROOT / "docs/research/pr-intake-decisions.json").read_text(encoding="utf-8"))
    ledger = (ROOT / "docs/research/pr-ledger.md").read_text(encoding="utf-8")
    contributors = (ROOT / "CONTRIBUTORS.md").read_text(encoding="utf-8")
    contribution = archive["contributions"][0]
    installed = archive["installed"]
    require(contribution["number"] == 2979 and contribution["head"] == HEAD, "the archived head changed")
    require(contribution["author"]["login"] == "mdumitrean", "the archived author changed")
    files = contribution["files"]
    require(len(files) == 112 and len(installed) == 112, "the file count changed")
    pairs = []
    for row in files:
        path = row["path"]
        oid = row["source"]["oid"]
        require(installed[path]["oid"] == oid, "the installed oid moved " + path)
        pairs.append((oid, blob_at(base, path)))
    require(count_matches(pairs) == 112, "a retained blob differs from main")
    decision = next(row for row in decisions["pull_requests"] if row["number"] == 2979)
    require(decision["reviewed_head"] == decision["current_head"] == HEAD, "the decision head changed")
    require(decision["disposition"] == "partially_reviewed", "the disposition changed")
    require(decision["closure"]["kind"] == "merged_for_archive_only", "the closure changed")
    require(decision["closure"]["merge_commit"] == "30f016dd79ee6a23c40d7dab44a9466c148c42dd", "the merge commit changed")
    review = decision["review_completion"]
    require(review["scoped_mechanism_review"] is False, "mechanism review is marked complete")
    require(review["required_execution_complete"] is False, "execution is marked complete")
    retention = archive["source_retention"]
    require(retention["status"] == "PASS" and retention["installed_blobs_exact"] is True, "the receipt dropped its blob claim")
    require(retention["all_original_heads_in_ancestry"] is True, "the receipt dropped its ancestry claim")
    require(
        "| [#2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979) | mdumitrean | partially reviewed |"
        in ledger,
        "the ledger row moved",
    )
    require(
        "- **aigent-marius (@mdumitrean)** — [#2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979):"
        in contributors
        and "(source archive)." in contributors[contributors.find("[#2979]") : contributors.find("[#2979]") + 400],
        "the contributor line moved",
    )
    return {
        "pull_request": 2979,
        "author": "mdumitrean",
        "head": HEAD,
        "head_unchanged": True,
        "files": 112,
        "blobs_match_main": True,
        "merge_commit": "30f016dd79ee6a23c40d7dab44a9466c148c42dd",
        "disposition": "partially_reviewed",
        "closure": "merged_for_archive_only",
        "mechanism_review": False,
        "execution_complete": False,
        "receipt_blobs_exact": True,
        "receipt_says_heads_in_ancestry": True,
        "contributor_line": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
