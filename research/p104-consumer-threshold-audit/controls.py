#!/usr/bin/env python3
"""Negative controls: each mutation goes through verify.audit or verify.load_sources
and must break its named claim (m_16p_plus_8 is a value-binding control: the
425/426 threshold survives it; stated enclosures and passing ranges break). Sagar Thakrar (thakrarsagar) with AI assistance
from Claude (Anthropic, Claude Opus 5.5). Apache-2.0."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify  # noqa: E402


def mutated(base, **changes):
    par = {k: (dict(v) if isinstance(v, dict) else v) for k, v in base.items()}
    for key, value in changes.items():
        if key in ("F", "D"):
            par[key].update(value)
        else:
            par[key] = value
    return par


def main():
    F, D, _ = verify.load_sources()
    base = verify.default_params(F, D)
    claims, _ = verify.audit(base)
    verify.need(all(claims.values()), "positive control failed")
    old = json.loads(verify.F_PATH.read_bytes())["censuses"]["dual2712"]["profile"]
    cases = {
        "P_3015": (mutated(base, P=3015), "B_finite_p1_to_p23_positive"),
        "P_3013": (mutated(base, P=3013), "E426_p7_kappa_negative"),
        "D9_92": (mutated(base, D={9: 92}), "B_finite_p1_to_p23_positive"),
        "D1_1317": (mutated(base, D={1: 1317}), "E426_p7_kappa_negative"),
        "D9_dropped": (mutated(base, D={9: 0}), "B_finite_p1_to_p23_positive"),
        "old_PR2712_dual": (mutated(base, D={**{int(r): n for r, n in old.items()}, 9: 0}), "E426_p7_kappa_negative"),
        "F7_76": (mutated(base, F={7: 76}), "E426_p7_kappa_negative"),
        "m_16p_plus_8": (mutated(base, m_const=8), "stated_E425_p7"),
        "W_209p": (mutated(base, w=209), "B_finite_p1_to_p23_positive"),
        "reject_claim_at_426": (mutated(base, d_fail=426), "B_finite_p1_to_p23_positive"),
        "pass_claim_at_425": (mutated(base, d_pass=425), "E426_p7_kappa_negative"),
        "p4_reject_at_428": (mutated(base, p4_fail=428), "p4_427_fails_at_kappa"),
        "p4_pass_at_427": (mutated(base, p4_pass=427), "p4_428_passes_at_a596"),
    }
    report = {}
    for name, (par, expected) in cases.items():
        broken = sorted(k for k, v in verify.audit(par)[0].items() if not v)
        verify.need(expected in broken, "control did not break " + expected + ": " + name)
        report[name] = [expected] + [k for k in broken if k != expected]
    # source binding: one changed byte in the vendored PR3609 receipt must be rejected
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "RECEIPT.json"
        shutil.copyfile(verify.D_PATH, bad)
        data = bytearray(bad.read_bytes())
        at = data.index(b'"9": 93')
        data[at + 6] = ord("2")
        bad.write_bytes(bytes(data))
        saved, verify.D_PATH = verify.D_PATH, bad
        try:
            verify.load_sources()
        except AssertionError as error:
            report["receipt_byte_changed"] = [str(error)]
        else:
            raise AssertionError("corrupted receipt accepted")
        finally:
            verify.D_PATH = saved
    for name, broken in report.items():
        print(name + ": " + ", ".join(broken[:4]) + (" ..." if len(broken) > 4 else ""))
    print("PASS_P104_CONSUMER_THRESHOLD_CONTROLS rejected=%d positive=1" % len(report))


if __name__ == "__main__":
    main()
