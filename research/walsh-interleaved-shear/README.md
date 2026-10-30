# Sharp rounding error with one interleaved integer shear

**Scoped theorem and independent verification. No new κ.**

Inserting an exact grid-preserving addition between two rounded Walsh stages
can invalidate the error guarantee for pure Walsh stages. For every integer
coefficient `m` and all twelve directed off-diagonal shears on four coordinates,
the exact worst-case sup-norm error is

```
h * (|m| + 3) / 4.
```

Here `h` is the grid spacing. Each stage is one distinct **normalized** real
Walsh factor `H0=(1/2)[[1,1],[1,-1]]`, rounded to nearest with ties to even.
The intervening operation is `y[target] += m*y[source]`. The exact comparison
map contains **the same shear**. This is not an error comparison against a
different, shear-free transform.

The unsheared case is `3h/4`; even a unit shear increases the sharp error to
`h`. For `m=-1`, target 0, source 1 and grid-unit input `(0,-1,-1,-1)`, the
rounded output is zero while the exact output is `(-1,1/4,0,1/4)`.

[PROOF.md](PROOF.md) gives the universal upper bound using nearest-even parity,
then proves sharpness for all integer coefficients from 24 fixed small inputs
in [WITNESSES.json](WITNESSES.json). The certificate rows are finite exact
identities; their affine dependence on `m` proves attainment for the unbounded
coefficient domain. No finite search is presented as a full theorem proof.

## What is new

Nick Petalas's [PR6129](https://github.com/CrocSwap/integer-mult-bounds/pull/6129)
proves the sharp law for distinct pure Walsh stages and explicitly excludes
intervening gates. Josie Elliston's
[PR6140](https://github.com/CrocSwap/integer-mult-bounds/pull/6140) independently
audits that law and asks whether it survives an intervening grid shear. This
package answers the complete **two-stage, one-integer-shear** instance, using
new implementations and a proof that does not assume the pure-stage recurrence.
It finds no defect in either predecessor or in CubeJerry's unchanged PR6119
surrogate.

The existing nearest-even shear-history and shear-equivariance obstructions
concern different contracts. This contribution is a precision side result,
not a new paid supplier or a selected-caller proof. The assigned track is
independent verification/formalization, OS random integer **83**. The original
catalogue card is retained in [TASK.json](TASK.json), with the scope change to
a written theorem explicitly disclosed. No proof-assistant formalization is
claimed.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -I -W error -B research/walsh-interleaved-shear/verify.py
```

Expected: JSON with `status: PASS_WALSH_INTERLEAVED_SHEAR`,
`complete_residue_inputs: 196608`, `witnesses: 24`, sixteen rejected controls
and `no_new_kappa: true`, exactly matching [RESULT.json](RESULT.json).
The direct command also works from a relocated copy of this package without
Git or the rest of the repository. Context files are checked against their
recorded SHA256 and Git blob IDs; they are not executable dependencies.

The registered runner checks the historical task/source bindings and runs the
same complete replay in ordinary and optimized Python, then the portable CLI
and damaged-artifact controls:

```sh
python3.12 -B scripts/research_package.py --package research/walsh-interleaved-shear
```

Expected final marker: `PASS_REGISTERED_RESEARCH_PACKAGE`, outcome `completed`.
Full repository history is needed for those provenance checks. `VERIFY.json`
declares no external live inputs; both context documents are included locally.

`verify.py --emit-witnesses` deterministically reconstructs the certificate,
searching `{-1,0,1}^4` in lexicographic order and stopping at the first witness
for each of the 24 pair/sign keys. `verify.py --emit-result` performs the full
replay and prints the receipt without comparing it to the committed receipt.
Both options print to stdout and never overwrite a frozen file.

## Evidence and failure coverage

The integer engine uses signed floor quotients for nearest-even rounding and
literal butterfly loops. Its independent oracle uses explicit dense matrices
and `Fraction` rounding; neither imports predecessor code. They compare every
rounded output, every exact output and the first stored vector, not merely a
common maximum.

| Check | Completed coverage |
| --- | --- |
| Residue census | `8^4 * 12 * 4 = 196608` inputs; 786432 output coordinates |
| Fixed-source affine witnesses | 24 rows; both coefficient signs, including signed 201-bit coefficients |
| Signed half-integer rounding | 2051 cases against exact rational rounding |
| Period/coefficient controls | 768 reproducible large signed cases, seed 83 |
| Reversed stage order | 2916 cases plus the written coordinate-conjugacy argument |
| Semantic mutations | Floor ties, missing shear, reversed shear, repeated axis, wrong difference sign, missing exact-comparator shear, and single-final-round all detected |
| Certificate/domain controls | Missing, duplicate, zeroed, wrong-slope and Boolean witnesses; off-grid input, fractional coefficient and aliased ports all rejected |
| Overextended predecessor bound | Explicit unit-shear input defeats `3h/4`; removing the shear restores `3h/4` |

The written input-period-eight and coefficient-residue lemmas explain why the
census covers its stated domain. The all-input upper proof is independent of
that census. All verifier checks use explicit exceptions and remain active
under `-O`. The transcript SHA256 in RESULT.json binds the ordered complete
computed vectors; it is an integrity check, not a substitute for mathematics.

`check_artifacts.py` additionally runs the actual optimized CLI in a relocated
temporary package with an empty PATH and no Git. It checks that every file and
mode remains unchanged, then rejects four private-copy corruptions: changed
context bytes, missing context, a missing witness and a Boolean receipt field
replaced by integer one. The last control catches the `True == 1` ambiguity of
untyped Python dictionary comparison. These four controls are separate from
the sixteen mathematical/domain controls in RESULT.json.

Local validation used CPython 3.12.14 on Linux x86_64. Normal and optimized
registered scientific checks passed in 30.827 seconds combined; this is a
descriptive replay duration, not a performance improvement claim. The portable
CLI and all four artifact controls also passed. Witness regeneration matches
the committed certificate byte for byte. Full environment and checkpoint
details are in TASK.json. Hosted CI is not claimed.

## Pins and limitations

Base: `721c03822c421b7f7fcbb2598993b947c4d88419`, priority revision 8.
The accepted selected record at that base is PR6030, κ = `0.003125804`.
The actual construction, source manifest and review are recorded in TASK.json;
historical task-card numbers are not treated as current frontiers.

[SOURCES.json](SOURCES.json) pins the historical selected record and catalogue,
plus the exact predecessor context documents:

- PR6129 head `f496734450c346468c66818c1c35521165b0cdda`, PROOF.md.
- PR6140 head `1c97110e1f25e8345f8ee63c570b88e172d75be9`, README.md.

The two small verbatim context documents preserve the excluded scope and open
question for review; their original notices remain intact. No pending PR's
code is imported and no pending commit is required in publication ancestry.
The mathematical statement is self-contained in this package.

Assumptions: real grid inputs, exactly two distinct axes, one integral
off-diagonal shear, exact arithmetic before each specified rounding, and
sufficient range. Scaling gives arbitrary `h>0`; conjugacy gives the reversed
axis order. Independent spectator fibers are covered only for shears within
each fiber. No complex mixing, cross-fiber shear, nonintegral coefficient,
multiple shear, more-stage, finite-width or overflow theorem is asserted.

No bit/tape cost, reversible restoration, clean-scratch service or accelerated
recursive child is supplied. All selected assumptions—`native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`—remain open
here. No selected cold replay, Lean kernel proof, hosted CI result or independent
human review is claimed. **No new κ; the selected frontier is unchanged.**

## Open next questions

Can this exact normalization and rounding contract be bound to an actual
selected `precision_tape` caller? First extract one complete rounded trace and
compare its grid, gates and exact comparison map against the unit-shear witness.
That binding is needed before changing any precision allocation; contracts
with more stages or nonintegral/complex gates need separate analysis. This
question and its blocker are structured in TASK.json.

## Credit

Prepared for Jerry Chen (@CubeJerry) with substantial OpenAI Codex assistance
in derivation, implementation, verification and writing. New work is Apache-2.0.
Nick Petalas retains credit for PR6129's pure-stage theorem and PR5912's history
analysis; Josie Elliston for PR6140's audit and explicit open question;
CubeJerry for PR6119's surrogate; Vlado Vojdanovski for PR1673's deferred-row
context; Sricharan Vagvala for PR1631's distinct equivariance obstruction.
The retained source documents credit their underlying native/BIT/analytic
lineage. Douglas Colkitt's package scaffold and the repository's source/export
verification tools are reused without modification.
