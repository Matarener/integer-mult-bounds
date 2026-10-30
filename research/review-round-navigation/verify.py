#!/usr/bin/env python3
"""The status page's latest-round sentence matches intake packages 2000-2600.

The nineteenth prose review remains the last row of the status table. Later
recorded rounds are archive and tooling intake packages. Round 2200's own
heading says "final unbatched remainder"; rounds 2300-2600 are recorded after
that heading. No selected frontier is changed.
"""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "docs/research/current-status.md"
REVIEW_1900 = ROOT / "docs/research/community-efficient1900-review.md"
BANNER = "> **Below this point every section is a historical snapshot.**"
OLD_LATEST = "The latest recorded round is"
PROSE_STOP = "The last prose review"
LATEST_LINK = "../../research/community-efficient2600-audit/README.md"
ROUND_2000_LINK = "../../research/community-efficient2000-audit/README.md"

ROUNDS = (
    (2000, "# Twentieth 100-PR intake", "**50 archived/merged; 50 still open.**"),
    (2100, "# Twenty-first 100-PR intake", "**37 archived/merged; 63 still open.**"),
    (2200, "# Twenty-second intake: final unbatched remainder", "**63 archived/merged; 22 still open.**"),
    (2300, "# Twenty-third100-head intake: research attributes and versions", "**32 archived/merged; 68 still open.**"),
    (2400, "# Twenty-fourth 100-head reconciliation", "**19 archived; 81 remain open in this batch.**"),
    (2500, "# Twenty-fifth 100-head reconciliation", "**28 archived; 72 remain open in this batch.**"),
    (2600, "# Twenty-sixth 100-head reconciliation", "**5 merged; 95 remain open in this batch.**"),
)


class NavError(Exception):
    pass


def current_section(text):
    if BANNER not in text:
        raise NavError("historical snapshot banner missing")
    return text.split(BANNER, 1)[0]


def first_bold(text):
    match = re.search(r"\*\*(.+?)\*\*", text)
    if not match:
        raise NavError("no bold count sentence")
    return match.group(1)


def check_status(text, review_text):
    current = current_section(text)
    if OLD_LATEST in current:
        raise NavError("status page still calls one round the latest recorded round")
    if PROSE_STOP not in current or "nineteenth reconciliation" not in current:
        raise NavError("status page does not keep the nineteenth prose review as the last table row")
    if "twenty-sixth reconciliation" not in current or LATEST_LINK not in current:
        raise NavError("status page does not link the twenty-sixth intake")
    if ROUND_2000_LINK not in current:
        raise NavError("status page does not link the twentieth intake")
    if "final unbatched remainder" not in current:
        raise NavError("status page does not warn that round 2200's final heading is not a stop")
    if "Review in progress" in current:
        raise NavError("nineteenth disposition still says review in progress")
    counts = first_bold(review_text)
    row = next(
        (line for line in current.splitlines() if line.startswith("|") and "efficient1900" in line),
        "",
    )
    if counts not in row:
        raise NavError("efficient1900 row does not repeat the review count: " + counts)
    for link in (LATEST_LINK, ROUND_2000_LINK):
        target = (STATUS.parent / link).resolve()
        if not target.is_file():
            raise NavError("missing intake target " + link)
    return counts


def check_rounds(readme_by_number, prose_review_names):
    for number, heading, counts in ROUNDS:
        text = readme_by_number.get(number)
        if text is None:
            raise NavError("missing intake readme " + str(number))
        lines = text.splitlines()
        if not lines or lines[0] != heading:
            raise NavError("heading mismatch for " + str(number))
        opening = "\n".join(lines[:6])
        if counts not in opening:
            raise NavError("count mismatch for " + str(number))
        if "No scientific claim" not in opening:
            raise NavError("intake " + str(number) + " does not keep its no-scientific-claim sentence")
        prose_name = "community-efficient%d-review.md" % number
        if prose_name in prose_review_names:
            raise NavError("unexpected prose review for intake " + str(number))
    if "final unbatched remainder" not in readme_by_number[2200].splitlines()[0]:
        raise NavError("round 2200 no longer names itself final")
    if any(number not in readme_by_number for number in (2300, 2400, 2500, 2600)):
        raise NavError("rounds after the 2200 final heading are missing")


def selected_decimal_remains(text):
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    if "**%s**" % selected["decimal"] not in current_section(text):
        raise NavError("selected decimal missing from the current section")
    return selected["decimal"]


def run_controls():
    review = "**63 merged; 1 closed as superseded; 36 pending.** Frozen.\n"
    good = "\n".join([
        "The last prose review",
        "in this table is the [nineteenth reconciliation](community-efficient1900-review.md).",
        "the [twenty-sixth reconciliation](%s)" % LATEST_LINK,
        "rounds [2000](%s) through" % ROUND_2000_LINK,
        'heading says "final unbatched remainder"',
        "| [efficient1900](community-efficient1900-review.md) | selection | 63 merged; 1 closed as superseded; 36 pending. |",
        BANNER,
    ])
    check_status(good, review)
    stale = good.replace("The last prose review", "The latest recorded round is the nineteenth. The last prose review")
    try:
        check_status(stale, review)
    except NavError as exc:
        if "latest recorded round" not in str(exc):
            raise
    else:
        raise NavError("control accepted the old latest-round sentence")
    in_progress = good.replace("36 pending. |", "36 pending. | Review in progress")
    try:
        check_status(in_progress, review)
    except NavError as exc:
        if "review in progress" not in str(exc):
            raise
    else:
        raise NavError("control accepted an in-progress nineteenth disposition")
    readmes = {number: heading + "\n\n" + counts + " No scientific claim.\n" for number, heading, counts in ROUNDS}
    check_rounds(readmes, set())
    broken = dict(readmes)
    broken[2600] = "# Twenty-seventh\n\n**5 merged; 95 remain open in this batch.** No scientific claim.\n"
    try:
        check_rounds(broken, set())
    except NavError as exc:
        if "heading mismatch for 2600" not in str(exc):
            raise
    else:
        raise NavError("control accepted a changed twenty-sixth heading")
    try:
        check_rounds(readmes, {"community-efficient2600-review.md"})
    except NavError as exc:
        if "unexpected prose review" not in str(exc):
            raise
    else:
        raise NavError("control accepted a prose review for round 2600")


def main():
    status = STATUS.read_text(encoding="utf-8")
    review = REVIEW_1900.read_text(encoding="utf-8")
    counts = check_status(status, review)
    decimal = selected_decimal_remains(status)
    readmes = {}
    for number, _heading, _counts in ROUNDS:
        path = ROOT / ("research/community-efficient%d-audit/README.md" % number)
        readmes[number] = path.read_text(encoding="utf-8")
    prose = {path.name for path in (ROOT / "docs/research").glob("community-efficient*-review.md")}
    check_rounds(readmes, prose)
    run_controls()
    print(
        "PASS_REVIEW_ROUND_NAVIGATION prose_last=1900 intake_last=2600 "
        "counts_1900=%s selected=%s rounds=7 controls=4 no_new_kappa"
        % (counts.replace(" ", "_"), decimal)
    )


if __name__ == "__main__":
    try:
        main()
    except NavError as exc:
        raise SystemExit("FAIL_REVIEW_ROUND_NAVIGATION " + str(exc)) from None
