"""Kernel-checked gate-operand parity between the pinned checker and exporter.

Three layers, separately labelled:

* source pins: the frozen operator lines that `sym` and `exp` formalize, and
  the Lean source bytes;
* a bounded finite census (standard library, independent of the Lean run) that
  cross-checks the contract predicate against direct simulation;
* kernel mode (`--lean`): a fresh Lean build of `lean/GateParity.lean` with the
  axiom reports of the five named theorems.

The default command never claims Lean ran.  Kernel mode requires the pinned
Lean 4.21.0 executable.

Prepared by Nick Petalas with AI assistance.  Apache-2.0.
"""
from pathlib import Path
import argparse
import hashlib
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

LEAN_SOURCE = HERE / "lean" / "GateParity.lean"
LEAN_SHA256 = "f4ec5064bcdf1b0ab255e5d92271041ae1503bb83744a633d1eeed3170c59266"
LEAN_VERSION = "4.21.0"
AXIOM_TARGETS = [
    "GateParity.sym_eq_exp_iff_contract",
    "GateParity.allEvenCount_xfold",
    "GateParity.xfold_indicator",
    "GateParity.exp_dest_free",
    "GateParity.exp_split_d",
]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

# Frozen operator lines that the Lean definitions formalize.
PINNED = [
    (
        "research/e8-bit-p111-tuned/code/xcheck_p.py",
        "af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e",
        ["acc = 0", "for s in srcs:", "acc ^= val[s]", "val[d] ^= acc"],
    ),
    (
        "research/e8-bit-carrier-skeleton/code/bit/export_records.py",
        "8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3",
        ["for s in srcs: rec.append((1,d,s,1,f,ph))"],
    ),
]

# Statement bindings: exact normalized definition bodies of the Lean formalization.
STATEMENT_BINDINGS = [
    "def Contract (d : Nat) (srcs : List Nat) : Prop := "
    "d ∉ srcs ∨ ∃ p t, srcs = p ++ (d :: t) ∧ d ∉ t ∧ ∀ r, EvenCount (p.count r)",
    "def sym (d : Nat) (srcs : List Nat) (v : Nat → Bool) : Nat → Bool := "
    "fun r => if r = d then bxor (v d) (xfold (srcs.map v)) else v r",
    "def step (d : Nat) (x : Nat → Bool) (s : Nat) : Nat → Bool := "
    "fun r => if r = d then bxor (x d) (x s) else x r",
    "def exp (d : Nat) (srcs : List Nat) (v : Nat → Bool) : Nat → Bool := "
    "srcs.foldl (step d) v",
]

ESCAPES = ["sorry", "axiom", "admit", "unsafe", "partial", "opaque",
           "native_decide", "run_tac", "elab", "macro", "syntax"]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lean_code(source):
    """Remove nested Lean comments; keep newlines and code tokens."""
    out, depth, i = [], 0, 0
    while i < len(source):
        if source.startswith("/-", i):
            depth += 1
            i += 2
        elif depth and source.startswith("-/", i):
            depth -= 1
            i += 2
        elif not depth and source.startswith("--", i):
            end = source.find("\n", i)
            i = len(source) if end < 0 else end
        else:
            out.append(source[i] if not depth or source[i] == "\n" else " ")
            i += 1
    need(depth == 0, "unterminated Lean comment")
    return "".join(out)


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def check_lean_source(source=None, digest=None):
    """Byte pin, axiom-command binding and proof-escape scan."""
    if source is None:
        need(sha256(LEAN_SOURCE) == LEAN_SHA256, "Lean source bytes changed")
        source = LEAN_SOURCE.read_text()
    code = lean_code(source)
    lines = code.splitlines()
    for target in AXIOM_TARGETS:
        need(any(line.strip() == "#print axioms " + target for line in lines),
             "missing axiom report for " + target)
    body = "\n".join(line for line in lines if not line.strip().startswith("#print "))
    for name in ESCAPES:
        need(not re.search(r"\b" + name + r"\b", body), "proof escape present: " + name)
    text = normalize(body)
    for binding in STATEMENT_BINDINGS:
        need(normalize(binding) in text, "statement binding missing: " + binding[:40])
    return len(AXIOM_TARGETS)


def check_pins(root=ROOT):
    for rel, digest, lines in PINNED:
        path = root / rel
        need(path.is_file(), "pinned source missing: " + rel)
        need(sha256(path) == digest, "pinned source bytes changed: " + rel)
        text = path.read_text()
        for line in lines:
            need(line in text, "pinned operator line missing in %s: %s" % (rel, line))
    return len(PINNED)


def b_sym(d, srcs, val):
    off = False
    for s in srcs:
        off ^= val[s]
    out = list(val)
    out[d] ^= off
    return out


def b_exp(d, srcs, val):
    out = list(val)
    for s in srcs:
        out[d] ^= out[s]
    return out


def b_contract(d, srcs):
    if d not in srcs:
        return True
    k = max(i for i, s in enumerate(srcs) if s == d)
    prefix, suffix = srcs[:k], srcs[k + 1:]
    return d not in suffix and all(prefix.count(r) % 2 == 0 for r in set(prefix))


def census(registers=4, max_len=4, contract=b_contract):
    """Agreement for every valuation iff the contract, over every list."""
    total = agree = diverge = 0
    vals = [[(mask >> i) & 1 == 1 for i in range(registers)]
            for mask in range(1 << registers)]
    lists = []
    stack = [[]]
    while stack:
        cur = stack.pop()
        lists.append(cur)
        if len(cur) < max_len:
            for r in range(registers):
                stack.append(cur + [r])
    for srcs in lists:
        for d in range(registers):
            total += 1
            same_all = all(b_sym(d, srcs, val) == b_exp(d, srcs, val) for val in vals)
            need(same_all == contract(d, srcs),
                 "contract mismatch at d=%d srcs=%r" % (d, srcs))
            if contract(d, srcs):
                agree += 1
            else:
                diverge += 1
    return total, agree, diverge


def parse_axioms(output, targets=AXIOM_TARGETS):
    found = {}
    for name, raw in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output):
        need(name not in found, "duplicate axiom report: " + name)
        axioms = sorted(x.strip() for x in raw.split(",") if x.strip())
        need(set(axioms) <= ALLOWED_AXIOMS, "unexpected axiom for %s: %r" % (name, axioms))
        found[name] = axioms
    for name in re.findall(r"'([^']+)' does not depend on any axioms", output):
        need(name not in found, "duplicate axiom report: " + name)
        found[name] = []
    need(set(found) == set(targets),
         "axiom report set mismatch: missing %r extra %r"
         % (sorted(set(targets) - set(found)), sorted(set(found) - set(targets))))
    need("sorryAx" not in output, "unchecked proof reported")
    return found


def kernel_build(lean):
    need(lean.is_file(), "Lean executable missing: " + str(lean))
    version = subprocess.check_output([str(lean), "--version"], text=True)
    need(LEAN_VERSION in version, "wrong Lean version: " + version.strip())
    result = subprocess.run([str(lean), str(LEAN_SOURCE)], capture_output=True,
                            text=True, timeout=900)
    output = result.stdout + result.stderr
    need(result.returncode == 0, "Lean build failed:\n" + output[-2000:])
    reports = parse_axioms(output)
    return version.strip(), reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", type=Path, default=None,
                        help="path to the pinned Lean 4.21.0 executable")
    args = parser.parse_args()

    targets = check_lean_source()
    pins = check_pins()
    total, agree, diverge = census()
    if args.lean is None:
        print("PASS_GATE_OPERAND_PARITY_LEAN pins=%d targets=%d census_pairs=%d "
              "census_agreements=%d census_divergences=%d contract_matches=1 "
              "lean_kernel=not_run" % (pins, targets, total, agree, diverge))
    else:
        version, reports = kernel_build(args.lean)
        summary = ",".join(sorted({a for ax in reports.values() for a in ax}))
        parsed = re.search(r"version (\S+?)[,)]", version)
        print("PASS_GATE_OPERAND_PARITY_LEAN_KERNEL pins=%d targets=%d census_pairs=%d "
              "census_agreements=%d census_divergences=%d contract_matches=1 "
              "lean=%s axioms=%s sorry_free=true"
              % (pins, targets, total, agree, diverge,
                 parsed.group(1) if parsed else version.split()[0], summary or "none"))


if __name__ == "__main__":
    main()
