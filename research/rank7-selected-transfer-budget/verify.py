"""Source-bound extra-child allowance. This is not supplier admission."""

import hashlib
import types
import json
from fractions import Fraction as Q
from pathlib import Path

from finite import check_invoice
from intervals import dyadic, moment, profile, require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SAVING = Q(17, 10000)
KAPPA = Q(1697, 1000000)
SOURCE_MANIFEST_SHA = "f07640bb4bff5d74469161c1ff6bc69f02f3a190e31e4ab06818d0d782606775"
OUTER_PATH = "research/complex-k492-owner-repair/vendor/multicold/engines/outer.py"


def source_bytes(path):
    require(path.is_file() and not path.is_symlink(), "regular source")
    require(path.stat().st_size <= 2**24, "input size")
    return path.read_bytes()


def read(path):
    return json.loads(source_bytes(path))


def authenticated_inputs():
    raw_manifest = source_bytes(PACKAGE / "SOURCES.json")
    sources = json.loads(raw_manifest)
    require(type(sources) is dict and
            set(sources) == {"schema_version", "base_commit", "files"}, "source schema keys")
    require(type(sources["schema_version"]) is int and sources["schema_version"] == 1,
            "integer source schema")
    require(hashlib.sha256(raw_manifest).hexdigest() == SOURCE_MANIFEST_SHA,
            "fixed source manifest bytes")
    require(type(sources["files"]) is list and len(sources["files"]) <= 16,
            "bounded source inventory")
    result = {}
    outer_source = None
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            raw = source_bytes(path)
            require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                    "source hash: " + row["path"])
            if path.suffix == ".json":
                result[row["path"]] = json.loads(raw)
            elif row["path"] == OUTER_PATH:
                require(outer_source is None, "one executable source")
                outer_source = raw
    require(type(outer_source) is bytes, "authenticated executable required")
    return result, outer_source


def allowance(histogram, live, saving, lower_count, calls):
    base = moment(histogram, 73, live, saving)
    require(base[1] < 1, "conditional source bill passes")
    one = moment({1: 1}, 73, live, saving)
    lower = (1 - base[1]) / one[1]
    upper = (1 - base[0]) / one[0]
    require(lower_count < lower <= upper < lower_count + 1,
            "sharp integer extra-child allowance")
    paid = (base[0] + lower_count * one[0], base[1] + lower_count * one[1])
    unpaid = (base[0] + (lower_count + 1) * one[0],
              base[1] + (lower_count + 1) * one[1])
    require(paid[1] < 1 < unpaid[0], "strict allowance endpoints")
    return {"moment": dyadic(base), "extra_rank1_threshold": dyadic((lower, upper)),
            "largest_extra_rank1_count": lower_count,
            "largest_passing_moment": dyadic(paid), "first_failing_moment": dyadic(unpaid),
            "one_per_call_moment": dyadic((base[0] + calls * one[0],
                                            base[1] + calls * one[1]))}


def controls():
    rejected = []
    for name, raw in (("boolean_count", {"1": True}),
                      ("zero_count", {"1": 0}), ("noncanonical_rank", {"01": 1}),
                      ("full_width_child", {"73": 1})):
        try:
            profile(raw, 73)
        except ValueError:
            rejected.append(name)
    require(len(rejected) == 4, "strict profile controls")
    require(KAPPA < SAVING / (1 + SAVING), "strict trial target")
    return rejected


def bit_surcharge_control(bit, histogram):
    endpoint = Q(bit["bit_lower"])
    live = bit["bit"]["live"]
    below = moment(histogram, 64, live, endpoint, True)
    above = moment(histogram, 64, live, endpoint + Q(1, 10**24), True)
    omitted = moment(histogram, 64, live, endpoint + Q(1, 10**24), False)
    require(below[1] < 1 < above[0] and omitted[1] < 1,
            "retained BIT surcharge changes actual endpoint decision")
    return {"endpoint_accepts": dyadic(below), "next_grid_rejects": dyadic(above),
            "omission_would_accept_next_grid": dyadic(omitted)}


def source_receipt_binding(claim, frozen):
    replay = read(PACKAGE / "evidence/SOURCE-REPLAY.json")
    admission = read(PACKAGE / "evidence/SOURCE-ADMISSION.json")
    native = read(PACKAGE / "evidence/SOURCE-NATIVE.json")
    release = read(PACKAGE / "evidence/SOURCE-RELEASE.json")
    require(replay["status"] == "PASS_RANK7_JOINT_ENDFRAMES_COMPLETE_REPLAY" and
            admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE" and
            release["status"] == "PASS_RELEASE", "actual complete source replay")
    require(replay["fresh_retained_bootstrap"] is True and
            replay["explicit_retained_reuse"] is False, "fresh retained provenance")
    require(replay["source_manifest_sha256"] == admission["source_manifest_sha256"] ==
            native["manifest_sha256"] == claim["source_manifest_sha256"], "exact derived source")
    require(replay["native_receipt_sha256"] == admission["native_receipt_sha256"] ==
            frozen["evidence/SOURCE-NATIVE.json"], "native receipt binding")
    require(replay["admission_result_sha256"] == frozen["evidence/SOURCE-ADMISSION.json"] and
            admission["release_receipt_sha256"] == frozen["evidence/SOURCE-RELEASE.json"],
            "admission/release binding")
    require(admission["package_manifest_sha256"] == release["manifest_sha256"],
            "source release package")
    require(profile(admission["profile"], 73) == profile(claim["profile"], 73),
            "complete source bill")
    require(Q(replay["kappa"]) == Q(admission["kappa"]) ==
            Q(release["kappa_decimal"]) == Q(claim["kappa"]), "source claimed release")
    return {"status": replay["status"], "fresh_retained_bootstrap": True,
            "source_manifest_sha256": replay["source_manifest_sha256"],
            "scope": "Reused source implementation and validators; no adoption of its modern outer or new kappa here."}


def finite_evidence(claim):
    frozen = read(PACKAGE / "FROZEN.json")
    require(type(frozen) is dict and 1 <= len(frozen) <= 16, "bounded evidence inventory")
    for name, digest in frozen.items():
        require(type(name) is str and name.startswith("evidence/") and
                ".." not in Path(name).parts, "evidence path")
        raw = (PACKAGE / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, "actual evidence hash")
    invoice = read(PACKAGE / "evidence/FINITE-INVOICE.json")
    result = check_invoice(invoice, 65088 * 74)
    bad = dict(invoice)
    bad["strict_checks"] = dict(invoice["strict_checks"], router=1)
    try:
        check_invoice(bad, 65088 * 74)
    except ValueError:
        result["nonboolean_guard_control"] = "rejected"
    require(result.get("nonboolean_guard_control") == "rejected", "typed finite control")
    result["source_receipt_binding"] = source_receipt_binding(claim, frozen)
    return result



def selected_outer(outer_source):
    """Retained engine, with finite arithmetic separated from its premises."""
    path = ROOT / OUTER_PATH
    module = types.ModuleType("authenticated_selected_outer")
    require(type(outer_source) is bytes, "immutable authenticated executable bytes")
    exec(compile(outer_source, str(path), "exec"), module.__dict__)
    eta = beta = Q(1, 10**24)
    s = (1 - beta) * SAVING - Q(1, 10**27)
    chain = [Q(384599, 10**10)]
    for _ in range(3):
        old = chain[-1]
        value = (1 - s) * s + s * old
        require(old < value < s < 1 - value, "bootstrap exponent inequalities")
        chain.append(value)
    bridge = {"semantic": {"C0": {"base": 2, "exponent": 210000},
                            "strict_literal_gap": 1},
              "rows": {"degree_gap": Q(10**6) - Q(51 * 20161, 25)}}
    outer = module.assembly(chain[-1], SAVING, bridge, KAPPA, eta, beta)
    require(len(outer["strict_constraints"]) == 47, "complete selected outer rows")
    require(all(x > 0 for x in outer["strict_constraints"].values()), "strict outer")
    return {"status": "CONDITIONAL_ARITHMETIC_ONLY",
            "bootstrap_exponents": [str(x) for x in chain],
            "strict_constraints": {k: str(v) for k, v in outer["strict_constraints"].items()},
            "absorption_gap": str(outer["absorption_gap"]),
            "fresh_uniform_time_coefficient": None,
            "new_supplier_stock_envelope": None,
            "scope": "The selected engine is reused. Exponent inequalities do not supply uniform implementation coefficients or stock admission."}


def main():
    inputs, outer_source = authenticated_inputs()
    claim = inputs["research/rank7-joint-endframes/CLAIM.json"]
    raw = inputs["research/rank7-joint-endframes/allocation/PROFILE.json"]
    require(raw == claim["profile"], "literal complete source profile")
    histogram = profile(raw, 73)
    require(profile(claim["profile"], 73) == histogram, "strict claim counts")
    require(type(claim["calls"]) is int and claim["calls"] == 666, "call count")
    live = claim["live_families"]
    require(type(live) is int and live == 896 * 74, "live geometry")
    require(sum(r * n for r, n in histogram.items()) == 65088 * 74, "rank mass")
    bit = inputs["research/e8-bit-p111-tuned/tune/EXPECTED.json"]["nine"]
    bit_histogram = profile(bit["profile"], 64)
    bit_bill = moment(bit_histogram, 64, bit["bit"]["live"], SAVING, True)
    require(bit_bill[1] < 1, "unchanged BIT with retained bad-residue surcharge")
    selected = inputs["certificates/selected-result.json"]
    baseline = inputs["research/community-frontier1094-audit/ASSEMBLY.json"]
    require(selected["kappa"] == baseline["kappa"], "selected baseline binding")
    require(Q(selected["kappa"]) < KAPPA, "trial exceeds selected kappa")
    selected_rate = Q(selected["kappa"]) / (1 - Q(selected["kappa"]))
    trial = allowance(histogram, live, SAVING, 395, 666)
    current = allowance(histogram, live, selected_rate, 730, 666)
    require(Q(trial["one_per_call_moment"][0]) > 1,
            "one new rank-one child per call fails trial")
    require(Q(current["one_per_call_moment"][1]) < 1,
            "one per call remains open at selected limiting rate")
    result = {"status": "PASS_CONDITIONAL_RANK7_SELECTED_TRANSFER_ALLOWANCE",
              "new_kappa_obtained": False, "trial_saving": str(SAVING),
              "strict_trial_kappa": str(KAPPA), "limiting_cap": str(SAVING / (1 + SAVING)),
              "selected_kappa": selected["kappa"], "complex": trial,
              "selected_required_rate": str(selected_rate),
              "at_selected_limiting_rate": current,
              "bit_with_surcharge": dyadic(bit_bill), "controls": controls(),
              "bit_surcharge_control": bit_surcharge_control(bit, bit_histogram),
              "selected_outer_arithmetic": selected_outer(outer_source),
              "actual_finite_invoice": finite_evidence(claim),
              "scope": "Conditional supplied histogram only. New physical/admissibility costs and the selected analytic transfer must be discharged separately."}
    require(json.dumps(result, sort_keys=True) ==
            json.dumps(read(PACKAGE / "RESULT.json"), sort_keys=True),
            "typed deterministic receipt")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
