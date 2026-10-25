#!/usr/bin/env python3
"""Receipt check for the four waiting-revision rows in queue-oct24a.

The retained ledger and intake snapshot still name PR #5427 head
389578f2. That head's child, dacc35b1f, replaces the modular span with an
exact rational span. This checker does not replay the ZQY census and does
not close the pull request.
"""

import json
import os
import subprocess

OLD = "389578f2d3ef075495ce76f08100ac50e18f7d40"
REPAIR = "dacc35b1f35c2b4bc2e3910520ba5cf46a020bed"
LIVE = "e0192de5d97e5ac09f42d26d9ceedee6377c77e2"
BASE = "32890bc5de034ab8fc93ac88ead7279a6a416d04"
PKG = "research/zqy-observation-not-retained"
FALSE_IMPLICATION = (
    "The computed non-membership modulo p therefore implies\n"
    "non-membership over the rationals."
)
COUNTEREXAMPLE = "for `A = [p]`, `b = 1` the target is outside the modular"
HOLDS = {
    4580: "55de56abdfd9cd7fb83758241793c18b9ae9ce71",
    4612: "0e0df631da41a1f9ed3489e8df532189c2643cbf",
    5427: OLD,
    5432: "6532b45ce9f3259d7408594ec480a140ec81e0e2",
}

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fail(message):
    raise SystemExit(message)


def git(*args):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=False, capture_output=True, text=True,
    )
    if result.returncode != 0:
        fail(args[0] + " failed: " + (result.stderr or result.stdout).strip())
    return result.stdout.strip()


def show(rev, path):
    return subprocess.check_output(
        ["git", "show", rev + ":" + path], cwd=ROOT,
    ).decode("utf-8")


def ancestor(commit, descendant):
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, descendant],
        cwd=ROOT, check=False,
    )
    return result.returncode == 0


def load_span(source):
    start = source.index("class Span:")
    end = source.index("\ndef modrow(")
    namespace = {}
    exec(
        "from fractions import Fraction as Fr\nP = (1 << 61) - 1\n" + source[start:end],
        namespace,
    )
    return namespace["Span"], namespace["Fr"]


def member(span_cls, rows, target):
    span = span_cls()
    for row in rows:
        span.add(dict(row))
    return span.reduce(dict(target)) == {}


def receipt_rows():
    ledger = json.loads(
        open(os.path.join(ROOT, "docs/research/pr-ledger.json"), encoding="utf-8").read()
    )
    intake = json.loads(
        open(
            os.path.join(ROOT, "docs/research/pr-intake-evidence/queue-oct24a-20261024.json"),
            encoding="utf-8",
        ).read()
    )
    by_number = {row["number"]: row for row in ledger["pull_requests"]}
    contributions = {row["number"]: row for row in intake["contributions"]}
    for number, head in HOLDS.items():
        if number not in by_number or number not in contributions:
            fail("missing receipt row " + str(number))
        recorded = by_number[number]
        decision = contributions[number]
        if recorded["current_head"] != head or recorded["reviewed_head"] != head:
            fail("ledger head moved for " + str(number))
        if recorded["github_state"] != "OPEN" or recorded["disposition"] != "partially_reviewed":
            fail("ledger state changed for " + str(number))
        if recorded["closure"] is not None or recorded["integration_location"]:
            fail("PR " + str(number) + " is recorded as retained")
        if decision["head"] != head or decision["lane"] != "waiting_revision":
            fail("intake row changed for " + str(number))
    text = by_number[5427]["unresolved_question"]
    if "A=[p]" not in text or "b=1" not in text or "Q certificate" not in text:
        fail("ledger no longer states the modular-arithmetic hold")
    if "Part 2 is not independently accepted" not in text:
        fail("ledger dropped the Part 2 boundary")


def commit_chain():
    if git("rev-parse", REPAIR + "^") != OLD:
        fail("repair commit is not the child of the recorded head")
    parents = git("rev-parse", LIVE + "^@").split()
    if parents != [REPAIR, BASE]:
        fail("live head parents are " + " ".join(parents))
    if ancestor(REPAIR, BASE):
        fail("repair commit is already contained in the receipt base")
    if not ancestor(OLD, REPAIR) or not ancestor(BASE, LIVE):
        fail("expected ancestry does not hold")


def arithmetic():
    old_proof = show(OLD, PKG + "/PROOF.md")
    new_proof = show(REPAIR, PKG + "/PROOF.md")
    old_code = show(OLD, PKG + "/verify.py")
    new_code = show(REPAIR, PKG + "/verify.py")
    if FALSE_IMPLICATION not in old_proof or FALSE_IMPLICATION in new_proof:
        fail("false modular implication is not confined to the recorded head")
    if COUNTEREXAMPLE not in new_proof or COUNTEREXAMPLE in old_proof:
        fail("reviewer counterexample is not stated on the repair head")
    if "pow(v[c], P - 2, P)" not in old_code or "pow(v[c], P - 2, P)" in new_code:
        fail("modular inverse is not confined to the recorded checker")
    if "P = (1 << 61) - 1" not in old_code or "P = (1 << 61) - 1" in new_code:
        fail("prime modulus assignment is not confined to the recorded checker")
    new_span, fraction = load_span(new_code)
    prime = (1 << 61) - 1
    if not member(new_span, [{0: fraction(prime)}], {0: fraction(1)}):
        fail("repaired Span missed the rational dependence 1 = (1/p) p")
    if member(new_span, [{0: fraction(1)}], {1: fraction(1)}):
        fail("repaired Span reported a vector outside a one-coordinate span")
    # Independent of either checker: the Fp image of [p] is 0, while 1 = (1/p)·p over Q.
    if prime % prime != 0 or fraction(1, prime) * prime != 1:
        fail("counterexample arithmetic failed")


def main():
    receipt_rows()
    commit_chain()
    arithmetic()
    print("PASS_PR5427_HOLD_HEAD_RECEIPT")


if __name__ == "__main__":
    main()
