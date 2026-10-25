"""Exact behavioural verification and source binding for the axis kernel.

Clear1nsight, with substantial OpenAI ChatGPT assistance. Apache-2.0.
This checks a local implementation, not full producer or supplier admission.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
INPUTS = {
    "research/qq16-native-rounded-components/vendor/native.py": (
        "e1976b3a55a40206808405b99a4c443093378bef",
        "999eb1230798b25821de7771ecfa86381e137124059b30ccef167169d176ee8e"),
    "research/qq16-all-depth-producer-grid/RESULT.json": (
        "372809009d835ce707eace8d514a667f2301b1d8",
        "b954ab5c5a720b21a9ab49bda2e1a0824ab184a482243d6263dab3c4bddb91bb"),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(path):
    # Execute source bytes, never a cached .pyc. Predecessor bytes are checked
    # before this function is called; no predecessor dispatcher is reused.
    namespace = {"__name__": "axis_audit_module", "__file__": str(path)}
    exec(compile(path.read_bytes(), str(path), "exec"), namespace)
    return SimpleNamespace(**namespace)


def sources(root=ROOT, package=PACKAGE):
    manifest = json.loads((package / "SOURCES.json").read_text())
    need(manifest["base_commit"] == BASE, "source base")
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    need(len(rows) == len(INPUTS), "source input cardinality")
    need({r["path"] for r in rows} == set(INPUTS), "source input set")
    for row in rows:
        blob, sha = INPUTS[row["path"]]
        need((row["git_blob"], row["sha256"]) == (blob, sha), "source pin")
        path = root / row["path"]
        need(not any(p.is_symlink() for p in [path, *path.parents]), "source symlink")
        raw = path.read_bytes()
        need(len(raw) <= 1_000_000, "source size")
        need(hashlib.sha256(raw).hexdigest() == sha, "source SHA256")
        need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
             == blob, "source Git blob")
    native = module(root / next(iter(INPUTS)))
    receipt = json.loads((root / list(INPUTS)[1]).read_text())
    lines = receipt["direct_cost_at_one"]["native_gaussian_lines"]
    need(type(lines) is int and lines == 11076, "inherited factor count")
    need(receipt["physical_routing_priced"] is False
         and receipt["supplier_admission"] is False, "inherited claim boundary")
    return native, receipt


def oracle(real, imag, axis, sign, width):
    """Independent integer formula with the full stated domain checked."""
    rr, ii = [], []
    for x in range(len(real)):
        y = x ^ (1 << axis)
        numerators = (real[x] + real[y] + sign * (imag[y] - imag[x]),
                      imag[x] + imag[y] + sign * (real[x] - real[y]))
        for z in numerators:
            need(z % 2 == 0, "oracle nonexact half")
            need(-(1 << (width - 1)) <= z < (1 << (width - 1)),
                 "oracle numerator overflow")
        rr.append(numerators[0] // 2)
        ii.append(numerators[1] // 2)
    return rr, ii


def check_case(t, real, imag, n, width, axis, sign, dirty=1, trace=False):
    want = oracle(real, imag, axis, sign, width)
    tapes = t.fixture(real, imag, width, dirty,
                      origins=[-31, 7, 101, -85, 23, 5], trace=trace)
    exterior = [dict(tape.exterior) for tape in tapes]
    control = t.axis_kernel(tapes, n, width, axis, sign)
    need(control == (0,) * 11, "finite control cleanup")
    got = t.decode(tapes[0], width), t.decode(tapes[1], width)
    need(got == want, "Gaussian value mismatch")
    need(all(tape.head == tape.origin for tape in tapes), "head restoration")
    need(all(not any(tape.cells) for tape in tapes[2:]), "scratch cleanup")
    need([tape.exterior for tape in tapes] == exterior, "dirty exterior")
    units = (1 << n) * width
    # Independent closed-window count, separated by physical tape role.
    for tape in tapes[:2]:
        need(tape.count == {"read": units, "write": units, "move": 4 * units},
             "data tape tariff")
    for tape in tapes[2:]:
        need(tape.count == {"read": units, "write": units, "move": 3 * units},
             "scratch tape tariff")
    return tapes


def verify():
    native, inherited = sources()
    t = module(PACKAGE / "tapes.py")
    pair_cases = 0
    for a, b, c, d in itertools.product(range(-4, 4), repeat=4):
        for sign in (-1, 1):
            check_case(t, [2*a, 2*c], [2*b, 2*d], 1, 7, 0, sign)
            pair_cases += 1

    routed_cases = 0
    metered_actions = pair_cases * 32 * 2 * 7
    for n in range(1, 8):
        size = 1 << n
        real = [2 * ((7*x + 1) % 23 - 11) for x in range(size)]
        imag = [2 * ((11*x + 4) % 19 - 9) for x in range(size)]
        for axis in range(n):
            for sign in (-1, 1):
                check_case(t, real, imag, n, 8, axis, sign)
                routed_cases += 1
                metered_actions += 32 * size * 8

    boundary_cases = 0
    for width in (2, 3, 4, 8, 32, 64, 279, 317, 545):
        lo, hi = -(1 << (width - 2)), (1 << (width - 2)) - 1
        for real, imag in (([lo, lo], [0, 0]), ([hi, hi], [0, 0]),
                           ([0, 0], [lo, lo]), ([0, 0], [hi, hi])):
            for sign in (-1, 1):
                check_case(t, real, imag, 1, width, 0, sign)
                boundary_cases += 1
                metered_actions += 32 * 2 * width

    real = [2 * ((x*x + 7*x) % 101 - 50) for x in range(512)]
    imag = [2 * ((13*x + 1) % 97 - 48) for x in range(512)]
    native_cases = 0
    native_digest = hashlib.sha256()
    for axis in range(9):
        for sign in (-1, 1):
            tapes = check_case(t, real, imag, 9, 12, axis, sign)
            re, im, exponent = native.line(native.vector(real, imag), 1 << axis, sign)
            need(all(x % (1 << exponent) == 0 for x in re + im), "native exact grid")
            want = ([x // (1 << exponent) for x in re],
                    [x // (1 << exponent) for x in im])
            need((t.decode(tapes[0], 12), t.decode(tapes[1], 12)) == want,
                 "pinned native mismatch")
            native_digest.update(json.dumps(want, separators=(",", ":")).encode())
            native_cases += 1
            metered_actions += 32 * 512 * 12

    # Two successive differently oriented axes reuse the *same* scratch,
    # and then their inverses undo the exact common-grid operation.
    real, imag = [16*(x-7) for x in range(16)], [16*(3-x) for x in range(16)]
    tapes = t.fixture(real, imag, 12)
    for axis, sign in ((0, 1), (3, -1), (3, 1), (0, -1)):
        before = t.decode(tapes[0], 12), t.decode(tapes[1], 12)
        want = oracle(*before, axis, sign, 12)
        need(t.axis_kernel(tapes, 4, 12, axis, sign) == (0,) * 11, "reuse control")
        need((t.decode(tapes[0], 12), t.decode(tapes[1], 12)) == want, "reuse values")
        need(all(not any(s.cells) and s.head == s.origin for s in tapes[2:]),
             "reuse scratch boundary")
    need((t.decode(tapes[0], 12), t.decode(tapes[1], 12)) == (real, imag),
         "inverse composition")
    need(sum(sum(s.count.values()) for s in tapes) == 4 * 32 * 16 * 12,
         "reuse tariff")
    metered_actions += 4 * 32 * 16 * 12

    result = {
        "status": "PASS_QQ16_GAUSSIAN_AXIS_TAPES",
        "source_base": BASE,
        "scope": "Nonuniform six-tape axis kernel on supplied owned windows",
        "exhaustive_scaled_signed_pair_cases": pair_cases,
        "routed_cases_n1_through_n7": routed_cases,
        "signed_boundary_cases": boundary_cases,
        "pinned_native_cases": native_cases,
        "native_output_digest": native_digest.hexdigest(),
        "same_scratch_composed_axes": 4,
        "total_metered_actions": metered_actions,
        "cell_actions_per_NW": {"read": 6, "write": 6, "move": 20, "total": 32},
        "data_bits_per_NW": 2,
        "discardable_scratch_bits_per_NW": 2,
        "inherited_axis_factors_per_tensor_layer":
            inherited["direct_cost_at_one"]["native_gaussian_lines"],
        "conditional_axis_only_actions_per_lambda_NW": 32 * 11076,
        "complete_producer": False,
        "caller_layout_admitted": False,
        "new_kappa": False,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="Create a new receipt, never overwrite")
    args = parser.parse_args()
    # Fail before an expensive replay if an explicit destination already exists.
    if args.write is not None:
        need(not args.write.exists(), "receipt output exists")
    result = verify()
    text = json.dumps(result, indent=2) + "\n"
    if args.write is not None:
        with args.write.open("x", encoding="utf-8") as stream:
            stream.write(text)
    else:
        stored = json.loads((PACKAGE / "RESULT.json").read_text())
        need(json.dumps(stored, sort_keys=True) == json.dumps(result, sort_keys=True),
             "receipt mismatch")
    print(result["status"], "pairs=" + str(result["exhaustive_scaled_signed_pair_cases"]),
          "native=" + str(result["pinned_native_cases"]), "actions=32*N*W",
          "no_new_kappa")


if __name__ == "__main__":
    main()
