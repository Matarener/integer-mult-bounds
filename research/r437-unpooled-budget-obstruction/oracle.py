#!/usr/bin/env python3
"""Integer common-denominator audit of the fixed unpooled moment screen.

ToikY with substantial OpenAI Codex assistance in a separate audit context.
The R437 construction, hosting invoice and ordinary-transfer proof retain
their original authorship in NOTICE. No source or primary implementation is
imported or executed. Apache-2.0.
"""
import argparse
from fractions import Fraction
from hashlib import sha1, sha256
import json
from math import gcd, lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
PINS = {
    "HOST-RESULT.json": (3594,
        "000837b2b7a1e9d7e4b6b657a055c6f5f3886c7ea343239f8620f79d5d7b2ae8",
        "ee0952e10f744cf1c6d9c237006ccae4ce3c36c8"),
    "host.py": (10905,
        "df01e61dc31a1cb6b2bf3549be1e2241f7a30829c2c98567f462271e3fc216ee",
        "2cb9b22890fdfacea4ee51a75b7746dd35b78489"),
    "ORDINARY-TRANSFER-PROOF.md": (9424,
        "29ed43abaf5451a8514dff2233ba02f44c1d3839e72035ec5711d4edf060b8f9",
        "092408728aa81e5a1e6d63307a3c0b85174e2ff2"),
    "SELECTED-RECORD.json": (6419,
        "2a0220e866417774606e0f991e41b9c1d26b1f43b97857238cf478dbc7d330b5",
        "581f8d87008354eb5b869f7ed9de1317ad837ce8"),
    "SELECTED-CLAIM.json": (1460,
        "66fbb5b21f32f1c4ba544c20d5a44ebcdfd11bce2bfa2d609c656ae520d3b21e",
        "3a8673160d129f0bec6aacf3ff2c2cf693839221"),
}
PROFILE = {1: 380448, 2: 400288, 3: 22464, 4: 26592, 5: 29376,
           6: 17376, 7: 26496, 26: 32, 42: 384}
WIDTH, NORMALIZATION = 64, 28416


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def authenticate(name, raw):
    size, digest, blob = PINS[name]
    need(len(raw) == size and sha256(raw).hexdigest() == digest,
         "Oracle exact source bytes: " + name)
    need(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
         "Oracle exact source Git blob: " + name)


def rational(numerator, denominator):
    need(type(numerator) is int and type(denominator) is int and denominator > 0,
         "Oracle integer rational components")
    common = gcd(abs(numerator), denominator)
    numerator, denominator = numerator // common, denominator // common
    return str(numerator) if denominator == 1 else str(numerator) + "/" + str(denominator)


def fixed_model(profile, width, normalization):
    need(type(width) is int and type(normalization) is int
         and width == WIDTH and normalization == NORMALIZATION,
         "Oracle frozen width and normalization")
    need(all(type(r) is int and type(n) is int for r, n in profile.items())
         and canonical(profile) == canonical(PROFILE), "Oracle frozen unpooled profile")


def target_role(role):
    need(role in ("admitted_BIT", "ordinary_BIT"),
         "Oracle selected whole kappa is provenance, not a supplier target")


def lower_certificate(profile, c_numerator, c_denominator,
                      width=WIDTH, normalization=NORMALIZATION):
    """Compute L=A+cB solely with integer sums and one common denominator."""
    need(type(c_numerator) is int and type(c_denominator) is int
         and c_numerator >= 0 and c_denominator > 0, "Oracle nonnegative saving")
    need(type(width) is int and width > 0 and type(normalization) is int
         and normalization > 0, "Oracle positive normalization")
    need(profile and all(type(r) is int and type(n) is int
                        and 0 < r <= width and n > 0 for r, n in profile.items()),
         "Oracle positive paid profile within width")
    common = lcm(*(width + r for r in profile))
    mass = sum(r * n for r, n in profile.items())
    # B has denominator width*W*common. No logarithm, exponential, root,
    # floating arithmetic or predecessor interval routine occurs here.
    slope_numerator = sum(n * r * 2 * (width - r) * (common // (width + r))
                          for r, n in profile.items())
    base = width * normalization
    numerator = mass * c_denominator * common + c_numerator * slope_numerator
    denominator = c_denominator * base * common
    return {
        "saving": rational(c_numerator, c_denominator),
        "mass": mass, "base_denominator": base, "common_log_denominator": common,
        "slope_numerator": slope_numerator,
        "A": rational(mass, base), "B": rational(slope_numerator, base * common),
        "lower": rational(numerator, denominator),
        "lower_minus_one": rational(numerator - denominator, denominator),
        "integer_lower_numerator": numerator,
        "integer_lower_denominator": denominator,
        "integer_cross_product_gap": numerator - denominator,
    }


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError("Oracle invalid model accepted")


def run():
    raw_sources = {}
    for name in PINS:
        raw = (HERE / "source" / name).read_bytes()
        authenticate(name, raw)
        raw_sources[name] = raw
    host = json.loads(raw_sources["HOST-RESULT.json"])
    selected = json.loads(raw_sources["SELECTED-RECORD.json"])
    claim = json.loads(raw_sources["SELECTED-CLAIM.json"])
    code = raw_sources["host.py"].decode()
    transfer = raw_sources["ORDINARY-TRANSFER-PROOF.md"].decode()
    need("factor=Q(n*r,64*28416)" in code
         and "pp[1]=pp.get(1,0)+Q(32*64*64*E,10**16)" in code,
         "Oracle source price normalization and omitted positive fee")
    need("a=c(1-c)=575/331776" in transfer and "c<1/512" in transfer,
         "Oracle actual historical transfer and its stated domain")
    profile = {int(r): n for r, n in host["profiles"]["new"].items()}
    fixed_model(profile, WIDTH, NORMALIZATION)
    need(host["mass_new"] == sum(r * n for r, n in profile.items()) == 1808352,
         "Oracle source hosted mass")
    need(host["new"]["forward"]["profile"] == host["new"]["reverse"]["profile"],
         "Oracle equal source forward/reverse rank invoices")
    admitted = Fraction(claim["admitted_BIT_saving"])
    ordinary = Fraction(claim["ordinary_BIT_saving"])
    kappa = Fraction(selected["kappa"])
    need(admitted == Fraction(17, 5000)
         and ordinary == Fraction(8590884599, 2500000000000)
         and Fraction(claim["kappa"]) == kappa == Fraction(62009, 20000000)
         and ordinary > admitted > kappa > 0,
         "Oracle distinct selected budget stages")
    results = {}
    for role, target in (("admitted_BIT", admitted), ("ordinary_BIT", ordinary)):
        target_role(role)
        value = lower_certificate(profile, target.numerator, target.denominator)
        need(value["slope_numerator"] > 0 and value["integer_cross_product_gap"] > 0,
             "Oracle positive necessary-moment obstruction")
        results[role] = value
    zero = lower_certificate(profile, 0, 1)
    need(zero["integer_cross_product_gap"] < 0, "Oracle zero-saving lower bound below one")
    changed = dict(profile)
    moved = changed.pop(42)
    changed[1] += moved
    need(sum(changed.values()) == sum(profile.values()),
         "Oracle changed-profile control retains total paid calls")
    changed_bound = lower_certificate(changed, admitted.numerator, admitted.denominator)
    need(changed_bound["integer_cross_product_gap"] < 0,
         "Oracle different fixed profile changes this lower-bound sign")
    guards = {
        "different_profile": reject(lambda: fixed_model(changed, WIDTH, NORMALIZATION)),
        "different_normalization": reject(lambda: fixed_model(profile, WIDTH, 28425)),
        "negative_saving": reject(lambda: lower_certificate(profile, -1, 5000)),
        "whole_kappa_as_supplier_target": reject(lambda: target_role("whole_kappa")),
        "changed_source_byte": reject(lambda: authenticate("HOST-RESULT.json",
                                      b"X" + raw_sources["HOST-RESULT.json"][1:])),
    }
    need(canonical({"bound": 1}) != canonical({"bound": True})
         and canonical({"bound": 1}) != canonical({"bound": 1.0}),
         "Oracle receipt equality preserves numeric types")
    return {
        "status": "PASS_R437_UNPOOLED_BUDGET_ORACLE",
        "source_sha256": {name: pin[1] for name, pin in PINS.items()},
        "width": WIDTH, "normalization": NORMALIZATION,
        "profile": {str(r): n for r, n in sorted(profile.items())},
        "selected_stages": {"ordinary_BIT": str(ordinary), "admitted_BIT": str(admitted),
                            "whole_kappa_provenance_only": str(kappa)},
        "integer_certificates": results,
        "inequalities": [
            "For x>=1, ln(x)>=2(x-1)/(x+1): the derivative gap is "
            "(x-1)^2/[x(x+1)^2]>=0, and the gap vanishes at1.",
            "For c>=0 and y=c*ln(x), exp(y)>=1+y; each paid weight is positive.",
            "Therefore M0(c)>=L(c)=A+cB. B>0, so L(17/5000)>1 obstructs "
            "every c>=17/5000 in this retained moment-certification budget.",
            "Under the declared necessary ordinary bridge a<=c, reaching a>=17/5000 "
            "would require such a rejected c. No physical bridge is extrapolated.",
        ],
        "controls": {
            "zero_saving": zero,
            "changed_profile_rank42_to_rank1": {
                "moved_paid_jobs": moved, "total_paid_calls_unchanged": True,
                "bound": changed_bound,
                "meaning": "Synthetic different-profile sign control only. L<1 is "
                           "not a proof that its actual moment passes or that the "
                           "changed jobs have a physical realization.",
            },
            "rejections": guards,
        },
        "scope": "Fixed unpooled invoice and retained moment-certification/contraction "
                 "budget only; no runtime complexity lower bound or algorithmic "
                 "impossibility. All omitted nonnegative charges are optimistic "
                 "omissions, not real zero costs. The source ordinary proof fixes "
                 "c=1/576 within c<1/512; it does not establish physical extension to "
                 "17/5000. Changed pooled invoices, native action, source words, "
                 "compiler and full physical/stock implementation remain outside.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true",
                        help="Print a candidate receipt without writing files")
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        retained = json.loads((HERE / "ORACLE.json").read_bytes())
        need(canonical(retained) == canonical(result), "Oracle complete typed receipt")
        print(json.dumps({"status": result["status"],
                          "admitted_lower": result["integer_certificates"]
                                             ["admitted_BIT"]["lower"]}, sort_keys=True))


if __name__ == "__main__":
    main()
