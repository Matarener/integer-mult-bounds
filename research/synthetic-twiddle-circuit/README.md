# Exact bit circuits for synthetic twiddle headers

The retained synthetic transform's exponent producer can use an h+1-bit accumulator in round h. This package compiles actual relocated MSB-first address bits into an ell+1-bit exponent residue modulo 2r, using only explicit AND/XOR gates. The opposite circuit emits the negative residue. Per-record integer exponents are outputs of this circuit rather than supplied arithmetic inputs.

[PROOF.md](PROOF.md) proves the unbounded mixed long/short shape family, the named-slot input order, exact gate count, sharp trailing-zero count and a scoped obstruction to additive affine exponent formulas. It also gives an explicit fixed-tape scan simulation with O(p^2 log(p+2)) work per header under the source's d*ell=O(p) hypothesis. The executed evaluator is a random-access Boolean circuit interpreter; the scan simulation is a written algorithmic proof.

For d_h participating axes and h>=1, the opposite circuit uses exactly d_h*(6h+5) gates. Forward negation adds 3*(h+1). Round zero and empty rounds use no gates. The circuit topology is immutable. Input address bits are preserved and private evaluator wires are cleared on return. Physical wire movement is additional to the gate count.

## Evidence and replay

RESULT.json records 109,208 complete address/round/direction evaluations across 93 small shapes and 712 circuits. A further 250 evaluations include ell=256 and 64 axes; the largest tested topology has 98,621 gates. All match a separately written integer exponent formula, and their slot orders match the retained literal layout engine. Four complete transform configurations check 184 full ring-module/dense comparisons and 36,544 coefficients in both directions. Fourteen malformed topology/address/shape cases reject with a valid retry. The executable compiler limits ell to 2..256 and axes to 1..64; the written proof has no such caps.

Use standard-library CPython 3.12 and an existing private external temporary directory:

```sh
python3.12 -I -Werror -B research/synthetic-twiddle-circuit/verify.py
TMPDIR=/absolute/private/run python3.12 -I -Werror -B research/synthetic-twiddle-circuit/test_controls.py
TMPDIR=/absolute/private/run python3.12 -Werror -B scripts/research_package.py --package research/synthetic-twiddle-circuit
python3 -B scripts/check_research_commit.py --package research/synthetic-twiddle-circuit --check-source-history
```

The controls invoke the actual optimized CLI on independent regular byte copies. They reject wrong branch selection, branch contamination of k, wrong shift, wrong direction, lost carry, wrong branch masking, altered receipt and changed/missing source. A full valid optimized CLI is also required. The verifier reads authenticated canonical input bytes directly and does not consume Python bytecode caches. Final publication and Git-free replay receipts are retained by the session report.

## Source, overlap and limits

The canonical base is 6f100d4bb5083f8c35d96fd95a539811c62f245c, priority revision 6. SOURCES.json pins both actual inputs, including the mathematical premise text in upstream/build/sections/06-transforms.tex. The source already gives the twiddle formula and polynomial-time address computation. The new result is a specific bit circuit, narrow accumulator and explicit simulation bound. No source defect or first encoded phase primitive is claimed.

Credit Douglas Colkitt and the retained synthetic-transform source, its Nussbaumer/Quandalle and Harvey/van der Hoeven lineage, and Philipp / mightyOil for the literal positional engine. Jose Manuel / jmbarrancoml's PR2298, PR3087 and physical Gaussian phase work are related predecessors. COMPARISONS.json records separate pending scopes without using their proof or runtime bytes. PR3516 supplies signed polynomial data rotation with supplied headers. This contribution fills its address-to-residue arithmetic subquestion, while leaving the actual packet/caller join open.

This is one partial compiler obligation. Complete encoded descriptor parsing, the executed fixed-tape header program, physical joins to PR3516 and the normalized layer/root, all dirty caller/control/storage bills, recursive/native/ordinary suppliers, outer recovery and a new kappa remain unclaimed. No selected frontier changes. Lean, Docker, complete selected cold replay and independent human or proof-kernel acceptance are outside this contribution.

## Open next questions

Translate the proved scan algorithm into the caller's actual fixed-tape instruction set, then connect its unsigned residue bits to the signed polynomial packet program and one normalized round. This matters because gate correctness alone does not charge actual address/header movement and borrowed program storage. A feasible first step is one small mixed long/short round with all control tapes, returned heads and program storage included. The blocker is the full encoded outer descriptor and conditional production layer interface. TASK.json records this question and the stop rule. Another phase census is not needed first.

Apache-2.0. Existing predecessor notices are unchanged.
