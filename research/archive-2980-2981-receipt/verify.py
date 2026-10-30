#!/usr/bin/env python3
"""Audit the archived receipt for pull requests 2980 and 2981.

Exact installed blobs are compared with the tree. The decisions file supplies
the reviewed head, the current head and the archive-only closure. Predecessor
sentences are read from the retained READMEs.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ARCHIVE_2980_2981_RECEIPT integration=partial heads_unchanged=true no_new_kappa"
RECEIPT_PATH = "docs/research/pr-intake-evidence/archives-pr2980-2981.json"
DECISIONS_PATH = "docs/research/pr-intake-decisions.json"
LEDGER_PATH = "docs/research/pr-ledger.md"
CONTRIBUTORS_PATH = "CONTRIBUTORS.md"
MERGE = "86b5e56d4aa0ced955ac7f059eac0c3a5633ca59"
OPEN_REVIEW = "Independent mechanism/proof review and source-bound replay remain open."
PREDECESSORS = (
    "PR2899 emits that callee as a ROOT",
    "PR2809/PR2808 archives",
    "Credit Nick Petalas/PR2920/2909/2896 for the fixed covers and residual geometry,",
    "Chafik Boukhalfa/PR1991",
)
LEDGER_ROWS = (
    "| [#2980](https://github.com/CrocSwap/integer-mult-bounds/pull/2980) | jwr404 | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |",
    "| [#2981](https://github.com/CrocSwap/integer-mult-bounds/pull/2981) | petalas | partially reviewed | [record 1](../../docs/research/pr-intake-decisions.json) |",
)
CREDIT_LINES = (
    "- **James Reed (@jwr404)** — [#2980](https://github.com/CrocSwap/integer-mult-bounds/pull/2980): Record the odd-prime depth-zero unit root as a weight, not a padded-row reversal (source archive).",
    "- **Nick Petalas (@petalas)** — [#2981](https://github.com/CrocSwap/integer-mult-bounds/pull/2981): Research: certify joint P104 unit-step endpoint flags (no new kappa) (source archive).",
)


def fail(message):
    raise SystemExit("FAIL_ARCHIVE_2980_2981_RECEIPT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def blob_oid(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def predecessor_gap(sentences, readme, receipt, credit):
    return sum(
        1 for sentence in sentences
        if sentence in readme and sentence not in receipt and sentence not in credit
    )


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        RECEIPT_PATH,
        DECISIONS_PATH,
        LEDGER_PATH,
        CONTRIBUTORS_PATH,
    }
    receipt = json.loads((ROOT / RECEIPT_PATH).read_text(encoding="utf-8"))
    expected.update(receipt["installed"])
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    return receipt


def directory_files(directory):
    found = []
    for path in (ROOT / directory).rglob("*"):
        if path.is_file():
            found.append(path.relative_to(ROOT).as_posix())
    return sorted(found)


def decision_for(decisions, number):
    rows = [row for row in decisions["pull_requests"] if row.get("number") == number]
    require(len(rows) == 1, "decision count for %s is %s" % (number, len(rows)))
    return rows[0]


def evaluate():
    receipt = authenticate()
    decisions = json.loads((ROOT / DECISIONS_PATH).read_text(encoding="utf-8"))
    ledger = (ROOT / LEDGER_PATH).read_text(encoding="utf-8")
    contributors = (ROOT / CONTRIBUTORS_PATH).read_text(encoding="utf-8")
    require(receipt["source_retention"]["status"] == "PASS", "the receipt dropped its source pass")
    require(receipt["source_retention"]["all_installed_blobs_exact"] is True, "the receipt dropped exact blobs")
    require(receipt["source_retention"]["all_original_heads_in_ancestry"] is True, "the receipt dropped its ancestry claim")
    installed = receipt["installed"]
    contributions = receipt["contributions"]
    require([item["number"] for item in contributions] == [2980, 2981], "the receipt pair moved")
    records = []
    readme = []
    for item in contributions:
        number = item["number"]
        files = item["files"]
        require(len(files) == len({row["path"] for row in files}), "duplicate path in %s" % number)
        for row in files:
            path = row["path"]
            data = (ROOT / path).read_bytes()
            require(blob_oid(data) == installed[path]["oid"], "installed blob moved " + path)
            require(blob_oid(data) == row["source"]["oid"], "contribution blob moved " + path)
            intake = next(
                block["files"][path]
                for block in receipt["intake"]["pull_requests"]
                if block["number"] == number
            )
            require(hashlib.sha256(data).hexdigest() == intake["sha256"], "sha256 moved " + path)
            require(len(data) == intake["bytes"], "length moved " + path)
        decision = decision_for(decisions, number)
        head = item["head"]
        require(decision["current_head"] == head, "current head changed for %s" % number)
        require(decision["reviewed_head"] == head, "reviewed head changed for %s" % number)
        require(decision["metadata"]["headRefOid"] == head, "metadata head changed for %s" % number)
        require(decision["disposition"] == "partially_reviewed", "disposition changed for %s" % number)
        require(decision["github_state"] == "MERGED", "github state changed for %s" % number)
        require(decision["closure"]["kind"] == "merged_for_archive_only", "closure changed for %s" % number)
        require(decision["closure"]["merge_commit"] == MERGE, "merge commit changed for %s" % number)
        require(decision["review_completion"]["scoped_mechanism_review"] is False, "mechanism review changed")
        require(decision["review_completion"]["required_execution_complete"] is False, "execution flag changed")
        require(decision["verification_evidence"] == [RECEIPT_PATH], "evidence path changed for %s" % number)
        directory = item["files"][0]["path"].split("/")[1]
        require(decision["integration_location"] == ["research/" + directory], "integration path changed")
        require(directory_files("research/" + directory) == sorted(row["path"] for row in files), "directory contents changed")
        publication = receipt["publication"]["p%s" % number]
        require(publication["headRefOid"] == head, "publication head changed")
        require(publication["state"] == "MERGED", "publication state changed")
        require(publication["mergeCommit"]["oid"] == MERGE, "publication merge changed")
        intake = next(block for block in receipt["intake"]["pull_requests"] if block["number"] == number)
        require(intake["remaining"] == OPEN_REVIEW, "the open-review sentence moved")
        require(intake["status"] == "archive_ready", "archive status moved")
        readme_path = "research/%s/README.md" % directory
        readme.append((ROOT / readme_path).read_text(encoding="utf-8"))
        records.append({
            "number": number,
            "head": head,
            "author": item["author"]["login"],
            "files": len(files),
            "disposition": "partially_reviewed",
        })
    require(records[0]["author"] == "jwr404" and records[1]["author"] == "petalas", "author login moved")
    require(sum(row["files"] for row in records) == len(installed) == 16, "file count moved")
    credit = "\n".join(CREDIT_LINES)
    for line in CREDIT_LINES:
        require(line in contributors, "contributor line moved")
    for row in LEDGER_ROWS:
        require(row in ledger, "ledger row moved")
    gap = predecessor_gap(PREDECESSORS, "\n".join(readme), (ROOT / RECEIPT_PATH).read_text(encoding="utf-8"), credit)
    require(gap == len(PREDECESSORS), "a predecessor sentence left the readme or entered the receipt")
    return {
        "receipt": RECEIPT_PATH,
        "records": records,
        "files_exact": 16,
        "extra_files": 0,
        "heads_unchanged": True,
        "merge_commit": MERGE,
        "source_blobs_retained": True,
        "receipt_says_heads_in_ancestry": True,
        "mechanism_review": False,
        "execution_complete": False,
        "closure": "merged_for_archive_only",
        "integration": "partial",
        "predecessor_sentences_outside_receipt": gap,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
