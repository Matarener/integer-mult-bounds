#!/usr/bin/env python3
"""Check docs/research/pr-ledger.md against docs/research/pr-ledger.json.

`scripts/find_overlap.py` reads the Markdown ledger as its `local-ledger`
overlap corpus, so a stale or hand-edited `.md` silently misreports disposition,
attribution and recorded review coverage.  `scripts/verify_pr_reconciliation.py`
checks the machine ledger only, and `scripts/reconcile_pr_queue.py` writes both
files but never verifies the committed `.md`.

This script re-derives the Markdown projection that `reconcile_pr_queue.py`
emits (disposition counts, then one row per PR: number, contributor, disposition
and ordered evidence records) and compares it with the committed file.  It
reports a bounded set of differences instead of a single boolean.

Scope: this is an attribution/coverage binding check.  It says nothing about
whether a recorded review was correct, and it does not touch GitHub.

    python3 scripts/verify_pr_ledger_markdown.py
    python3 scripts/verify_pr_ledger_markdown.py --json
    python3 scripts/verify_pr_ledger_markdown.py --root /tmp/fixture
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_RELATIVE = "docs/research/pr-ledger.md"
LEDGER_RELATIVE = "docs/research/pr-ledger.json"
REPORT_LIMIT = 20
NO_REVIEW_DETAIL = "No exact-head review established; inspect contribution and dependencies."


class LedgerMismatch(Exception):
    """Raised when the Markdown ledger cannot be projected from the JSON ledger."""


def require(condition: object, message: str) -> None:
    if not condition:
        raise LedgerMismatch(message)


def expected_counts(ledger: dict) -> dict:
    counts: dict[str, int] = {}
    for pr in ledger["pull_requests"]:
        counts[pr["disposition"]] = counts.get(pr["disposition"], 0) + 1
    return counts


def expected_detail(pr: dict) -> str:
    """Reproduce the generator's evidence-record column for one PR."""
    refs = sorted({entry["evidence"] for entry in pr["evidence"]})
    if pr.get("reconciliation_evidence"):
        refs.extend(pr["reconciliation_evidence"])
    refs = list(dict.fromkeys(refs))
    if not refs:
        return NO_REVIEW_DETAIL
    return " · ".join(f"[record {i + 1}](../../{name})" for i, name in enumerate(refs))


def expected_row(pr: dict) -> str:
    return "| [#{number}]({url}) | {login} | {disposition} | {detail} |".format(
        number=pr["number"],
        url=pr["url"],
        login=pr["contributor"]["login"],
        disposition=pr["disposition"].replace("_", " "),
        detail=expected_detail(pr),
    )


def parse_markdown(text: str) -> tuple[dict, list, list]:
    """Return (declared counts, per-PR row lines, structural problems)."""
    lines = text.split("\n")
    problems: list[str] = []

    counts: dict[str, int] = {}
    seen_header = False
    for index, line in enumerate(lines):
        if line.startswith("| Disposition | Count |"):
            seen_header = True
            cursor = index + 2  # skip the |---|---|---:| separator
            while cursor < len(lines) and lines[cursor].startswith("|"):
                cells = [cell.strip() for cell in lines[cursor].strip().strip("|").split("|")]
                if len(cells) != 2:
                    problems.append(f"counts table line {cursor + 1}: expected 2 cells, found {len(cells)}")
                else:
                    try:
                        counts[cells[0]] = int(cells[1])
                    except ValueError:
                        problems.append(f"counts table line {cursor + 1}: non-integer count {cells[1]!r}")
                cursor += 1
            break
    if not seen_header:
        problems.append("disposition counts table header '| Disposition | Count |' not found")

    rows = [(index + 1, line) for index, line in enumerate(lines) if line.startswith("| [#")]
    if not rows:
        problems.append("no '| [#N](...)' inventory rows found")
    return counts, rows, problems


def display_counts(counts: dict) -> dict:
    """The generator prints disposition keys with spaces; normalise for comparison."""
    return {name.replace("_", " "): value for name, value in counts.items()}


def check(markdown: str, ledger: dict) -> dict:
    require(isinstance(ledger, dict) and "pull_requests" in ledger, "JSON ledger has no pull_requests")
    counts, rows, problems = parse_markdown(markdown)
    counts = display_counts(counts)
    prs = ledger["pull_requests"]

    differences: list[str] = list(problems)

    want_counts = display_counts(expected_counts(ledger))
    declared = ledger.get("counts")
    if declared is not None and display_counts(declared) != want_counts:
        differences.append(f"JSON 'counts' field disagrees with its own pull_requests: {declared} != {expected_counts(ledger)}")
    for name in sorted(set(want_counts) | set(counts)):
        if counts.get(name) != want_counts.get(name):
            differences.append(f"count {name!r}: markdown {counts.get(name)} != json {want_counts.get(name)}")

    if len(rows) != len(prs):
        differences.append(f"inventory row count: markdown {len(rows)} != json {len(prs)}")

    row_text: dict[int, str] = {}
    first_line: dict[int, int] = {}
    for line_no, line in rows:
        number = int(line.split("]", 1)[0].split("#", 1)[1])
        if number in row_text:
            differences.append(f"line {line_no}: duplicate row for #{number} (first at line {first_line[number]})")
            continue
        row_text[number] = line.rstrip("\r")
        first_line[number] = line_no
    seen = first_line
    missing = sorted({pr["number"] for pr in prs} - set(seen))
    extra = sorted(set(seen) - {pr["number"] for pr in prs})
    if missing:
        differences.append(f"missing rows: {missing[:REPORT_LIMIT]}")
    if extra:
        differences.append(f"unexpected rows: {extra[:REPORT_LIMIT]}")

    by_number = {pr["number"]: pr for pr in prs}
    field_mismatches = 0
    for number in sorted(seen):
        pr = by_number.get(number)
        if pr is None:
            continue
        want = expected_row(pr)
        if row_text[number] != want:
            field_mismatches += 1
            if field_mismatches <= REPORT_LIMIT:
                differences.append(f"line {seen[number]}: #{number} row differs\n  markdown: {row_text[number]!r}\n  from json: {want!r}")
    if field_mismatches > REPORT_LIMIT:
        differences.append(f"... and {field_mismatches - REPORT_LIMIT} further row mismatches")

    return {
        "markdown_rows": len(rows),
        "json_prs": len(prs),
        "counts": want_counts,
        "markdown_counts": counts,
        "row_mismatches": field_mismatches,
        "missing_rows": missing,
        "unexpected_rows": extra,
        "differences": differences,
        "ok": not differences,
    }


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    parser.add_argument("--markdown", type=Path, help="override Markdown ledger path")
    parser.add_argument("--json-ledger", type=Path, help="override JSON ledger path")
    parser.add_argument("--json", action="store_true", help="emit the full report as JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    markdown_path = args.markdown or root / MARKDOWN_RELATIVE
    ledger_path = args.json_ledger or root / LEDGER_RELATIVE
    try:
        require(markdown_path.is_file(), f"missing Markdown ledger: {markdown_path}")
        require(ledger_path.is_file(), f"missing JSON ledger: {ledger_path}")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        report = check(markdown_path.read_text(encoding="utf-8"), ledger)
    except LedgerMismatch as error:
        report = {"ok": False, "differences": [str(error)]}

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif report["ok"]:
        print(f"PASS_PR_LEDGER_MARKDOWN_CONSISTENT rows={report['markdown_rows']} counts={report['counts']}")
    else:
        print("FAIL_PR_LEDGER_MARKDOWN_MISMATCH", file=sys.stderr)
        for difference in report["differences"]:
            print(f"  - {difference}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())