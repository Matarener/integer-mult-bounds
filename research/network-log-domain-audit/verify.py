#!/usr/bin/env python3
"""Replay the historical network logarithm-domain failure and proposed guard.

Prepared for roger-sato with substantial OpenAI Codex assistance. Apache-2.0.
The original numerical helper and proof producer remain Douglas Colkitt's work.
"""
import argparse
from contextlib import contextmanager
import difflib
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ANCHOR = "def certify_network(h, k, log_bound):\n"
GUARD = (
    "    # Positive Taylor terms give a lower bound only on this domain.\n"
    '    require(log_bound > 0, "Logarithm upper bound must be positive")\n'
)
ERROR = "Logarithm upper bound must be positive"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, digest, name):
    require(sha256(raw).hexdigest() == digest, "source drift: " + name)
    return raw


def sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    return {
        row["path"]: authenticate(
            (ROOT / row["path"]).read_bytes(), row["sha256"], row["path"]
        )
        for row in manifest["files"] if row["usage"] == "input"
    }


def repaired_source(original):
    text = original.decode("utf-8")
    require(text.count(ANCHOR) == 1, "ambiguous proposed-guard insertion")
    return text.replace(ANCHOR, ANCHOR + GUARD, 1).encode("utf-8")


def proposed_patch(original):
    return "".join(difflib.unified_diff(
        original.decode("utf-8").splitlines(keepends=True),
        repaired_source(original).decode("utf-8").splitlines(keepends=True),
        fromfile="a/scripts/certify.py", tofile="b/scripts/certify.py",
    ))


@contextmanager
def loaded(raw, repaired=False):
    """Execute authenticated source bytes; neither import nor write a .pyc."""
    previous = sys.modules.get("certify")
    owner = types.ModuleType("certify")
    owner.__file__ = str(ROOT / "scripts/certify.py")
    sys.modules["certify"] = owner
    try:
        code = raw["scripts/certify.py"]
        if repaired:
            code = repaired_source(code)
        exec(compile(code, owner.__file__, "exec"), owner.__dict__)
        producer = types.ModuleType("_audited_make_patch")
        producer.__file__ = str(ROOT / "scripts/make_patch.py")
        exec(compile(raw["scripts/make_patch.py"], producer.__file__, "exec"),
             producer.__dict__)
        yield owner, producer
    finally:
        if previous is None:
            sys.modules.pop("certify", None)
        else:
            sys.modules["certify"] = previous


def proof_rows(producer, k, h, bound):
    rows = list(producer.extended_files(k, h, bound))
    require(len(rows) == 6 and len({r[0] for r in rows}) == 6,
            "expected complete six-file proof proposal")
    return rows


def rejected(call, message):
    try:
        call()
    except ValueError as error:
        require(str(error) == message, "unexpected rejection: " + str(error))
    else:
        raise ValueError("invalid fixture accepted: " + message)


def audit():
    raw = sources()
    original = raw["scripts/certify.py"]
    require((HERE / "proposed-guard.patch").read_text(encoding="utf-8")
            == proposed_patch(original), "proposed patch differs from tested guard")
    positives = [(100, 50, 20), (100, 42, 14), (46, 36, 12)]
    expected = []
    with loaded(raw) as (owner, producer):
        negative = owner.certify_network(46, 36, -1000)
        # An independent three-term polynomial calculation, not a numerical exp.
        polynomial = 1 - 1000 + 1000 * 1000 // 2
        require(polynomial == 499001 > 46**3 > 1,
                "rational contradiction witness changed")
        require(negative["exp_lower_bound"] == str(polynomial)
                and negative["exp_series_terms"] == 3
                and negative["counts"]["m"] == str(46**3),
                "historical negative-log acceptance changed")
        false_rows = proof_rows(producer, 36, 46, -1000)
        motifs = next(new for name, _, new in false_rows
                      if name.endswith("03-motifs.tex"))
        false_claim = r"gives $m<e^{-1000}$ and hence $\log m<-1000$"
        require(false_claim in motifs, "actual proof producer no longer emits false claim")
        for h, k, bound in positives:
            expected.append((owner.certify_network(h, k, bound),
                             proof_rows(producer, k, h, bound)))
        rejected(lambda: owner.certify_network(46, 36, 1),
                 "Could not certify the logarithm bound")
    controls = []
    with loaded(raw, repaired=True) as (owner, producer):
        for bound in (-10000, -1000, -1, Fraction(-1, 2), 0):
            rejected(lambda: owner.certify_network(46, 36, bound), ERROR)
            # Pull the first iterator item: no partial proof may escape the guard.
            rejected(lambda: next(producer.extended_files(36, 46, bound)), ERROR)
            controls.append(str(bound))
        for (h, k, bound), (certificate, rows) in zip(positives, expected):
            require(owner.certify_network(h, k, bound) == certificate,
                    "guard changes a published positive certificate")
            require(proof_rows(producer, k, h, bound) == rows,
                    "guard changes a published positive proof proposal")
        require(owner.certify_network(46, 36, Fraction(12))
                == expected[-1][0], "exact rational positive bound changed")
        rejected(lambda: owner.certify_network(46, 36, 1),
                 "Could not certify the logarithm bound")
    # Ensure the evidence checker fails closed for changed source bytes.
    rejected(lambda: authenticate(original + b"\n", sha256(original).hexdigest(),
                                  "scripts/certify.py"),
             "source drift: scripts/certify.py")
    pin_rows = json.loads(raw["research/rational-containment-performance/SOURCES.json"])
    pin = [row for row in pin_rows["files"] if row["path"] == "scripts/certify.py"]
    require(len(pin) == 1 and pin[0]["usage"] == "input"
            and pin[0]["sha256"] == sha256(original).hexdigest(),
            "frozen live-input adoption boundary changed")
    live_inputs = json.loads(raw["research/rational-containment-performance/VERIFY.json"])
    require("scripts/certify.py" in live_inputs["inputs"],
            "retained replay declaration changed")
    ternary = json.loads(raw["certificates/ternary-side.json"])
    require(ternary["source_sha256"]["scripts/certify.py"]
            == sha256(original).hexdigest(), "retained ternary source pin changed")
    return {
        "scope": "Historical numerical helper and proof-producer audit; no new kappa",
        "helper_input": {"h": 46, "k": 36, "log_bound": -1000},
        "accepted_historical_certificate": negative,
        "exact_polynomial_value": polynomial,
        "mathematical_contradiction": "exp(-1000) < 1 < 97336 < 499001",
        "emitted_false_claim": false_claim,
        "rejected_nonpositive_bounds": controls,
        "guard_rejects_before_first_proof_file": True,
        "positive_controls": [
            {"h": h, "k": k, "log_bound": bound, "certificate": certificate,
             "proposal_sha256": {name: sha256(new.encode("utf-8")).hexdigest()
                                 for name, _, new in rows}}
            for (h, k, bound), (certificate, rows) in zip(positives, expected)
        ],
        "positive_certificate_and_proposal_equality": True,
        "too_small_positive_bound_still_rejected": True,
        "source_mutation_rejected": True,
        "proposed_guard_sha256": sha256(repaired_source(original)).hexdigest(),
        "production_guard_adopted": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print reconstructed receipt")
    args = parser.parse_args()
    result = audit()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        print(payload, end="")
    else:
        # Byte equality also preserves integer/Boolean distinctions in claims.
        require((HERE / "RESULT.json").read_text(encoding="utf-8") == payload,
                "audit receipt differs")
        print("PASS_NETWORK_LOG_DOMAIN_AUDIT false_proof_reproduced=1 "
              "positive_pairs=3 rejected_domain_cases=5 production_guard_adopted=0")


if __name__ == "__main__":
    main()
