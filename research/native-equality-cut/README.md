# Native tariff constraints that permit active feedback

This package proves a necessary cost constraint for complete linear native
words. It permits changed paid inputs, feedback, arbitrary scalar mixing,
COPY, CLEAR and the full columnwise monomial alphabet. It does not keep
the old caller frozen.

For paid and target Fourier-rank profiles P and T, every such word at
width f must satisfy

```text
sum_r P_r (1-2^(-k*r)) >= sum_r T_r (1-2^(-k*r))
for every integer k with 1 <= 2*k <= f.
```

Fixed profiles that work at arbitrarily large widths must pass every k.
[cuts.py](cuts.py) decides this infinite family with a finite exact
polynomial test. It gives a failing cut when one exists. The proof uses
equality of pairs of tensor columns. Every columnwise monomial map
preserves this cut. A rank-r Clifford query has exactly the displayed
normalized cut rank.

This can reject a proposed supplier invoice before native synthesis. One
rank-one plus one rank-three call cannot supply two independent rank-two
jobs, although both the call count and rank mass agree. More strongly,
for every K there is a profile that passes all earlier cuts and first
fails at K. No fixed prefix of checks is complete. A failing cut also
forces operator norm error at least one for the ideal native word and
the stated unitary target frames.

The delayed failures include profiles with a strictly favorable raw
power moment for every saving from zero through **1/256**. Thus a large
raw saving and any fixed prefix of native cuts can both be false signals.
The adaptive exact test detects these profiles without a word search.
This is an impossibility result for those invoices, not a new kappa.

**No kappa improvement or native admission is claimed.** The pinned P104
complete profile, with 69,930 paid calls and 12,814 target jobs, passes
all these necessary constraints. The test does not reject that route.
This is a new obstruction and search filter for changed caller designs.

## Exact scope

Read [PROOF.md](PROOF.md) for the theorem and all hypotheses. Every field
has the same whole-field capacity. Paid calls are single-field Clifford
tensor maps or scalar query updates. The final credit is for independent
native target jobs. Ordinary maps must preserve the chosen cuts. The
full columnwise monomial group does; general inter-column routing does
not. Larger-field packing and different capacities need separate factors.

The exact rank obstruction also permits invertible ordinary input/output
codes. The unit error constant needs the stated unitary endpoint frames.
For a boundary with nonordinary cached observations, the joint cut rank
of the complete initial availability matrix belongs on the paid side.
Section 5 gives this relative form; the CLI does not extract that matrix.
Duplicate rows do not earn duplicate initial rank.

The original semisimple-module question led to a useful distinction:
an optimal set of arbitrary linear output rows need not fit through the
inputs of physical single-field queries. Section 7 gives the exact
three-coordinate counterexample and records that part of the research.

## Reproduce and use in a search

Python 3.12 and its standard library suffice. No native build, external
package, solver or network access is needed.

```sh
python3 -B scripts/research_package.py --package research/native-equality-cut
python3 -I -B research/native-equality-cut/cuts.py research/native-equality-cut/examples/equal-mass-trade.json
```

The second command returns exit code 1 and an exact failing witness. For
another candidate, supply JSON objects `paid` and `targets`, with decimal
rank strings and nonnegative integer counts. An optional positive `width`
restricts the check to that width. Without it the CLI checks all positive
k. Exit code 0 means only that these necessary conditions pass.

For a profile search, first include every paid call and every required
target once. Run the CLI on each proposed invoice. A witness k gives the
linear constraint displayed above for the next optimization round. Use
exact rational coefficients when certifying that constraint. A passing
profile still needs a word, physical input/output bindings and the full
compiler, precision, storage, routing and outer bill.

## Evidence

The registered normal and optimized checks use literal Gaussian-rational
matrices. They check all 24 projective one-axis Clifford classes and
constructed two-/three-axis words, including non-diagonal frames. There
are 172 literal cross-block rank checks and 172 exact partial-isometry
checks. A separate support count checks the binary Pauli Fourier rank.
The explicit rank-three obstruction supplies an additional native case.

The full input/output matrices of 48 chronological words cover 480
prefixes with feedback, overwrite, COPY, CLEAR and arbitrary dirty
directions. Controls check duplicate initial responses, the physical
input bottleneck and a noncolumnwise map that crosses the cut. The tariff
tests include 192 profile pairs, all 625 differences with four ranks and
coefficients from -2 through 2, two families with first failures at cuts
1 through 12, width boundaries and invalid inputs. The favorable raw
moment uses an exact integer-power comparison. See [RESULT.json](RESULT.json).

The P104 application authenticates a byte-exact copy of its source result
and checks its complete profiles. It does not rerun the P104 native word,
its compiler or the selected cold replay. Finite checks support the
written proof; they are not proof-kernel acceptance or independent human
review. The baseline binding helper stopped on omitted sparse source
files during orientation. No selected-baseline pass is claimed.

## Open next questions

1. Apply these linear constraints in a supplier search that changes the
   word. Start with the complete proposed paid/target profiles. A physical
   caller and its ordinary-operation contract remain necessary.
2. Find stronger invariant cuts for operations that mix tensor columns.
   First state the permitted maps and check which projectors they preserve.
   The present cuts do not charge those maps for free.
3. At an actual retained-observation boundary, extract the complete
   availability matrix J and use its joint cut rank. The missing source
   versions and physical availability ledger remain the blocker.

## Sources, overlap and credit

Base: canonical main `5e0052ca0aa3036a3afa8b0438927377c8d97d53`, priority
revision 7. [Discussion #5582](https://github.com/CrocSwap/integer-mult-bounds/discussions/5582)
is the canonical investigation. The initial claim took the open semisimple
question in [PR #5449](https://github.com/CrocSwap/integer-mult-bounds/pull/5449).
The changed scope and its input bottleneck are recorded there and in TASK.
Active P104 endpoint-retiming and joint-basis claims were excluded.

The repository already uses the classical off-diagonal rank inequality in
[the fused-block audit](../../docs/research/fused-block-audit.md), the
dirty-host cut-rank work of an664 and its reviewers, and the later tariff
work of Adam Gall and Ross Richardson. Those arguments retain their credit.
The full monomial-invariant equality cut and exact Clifford tariff are
the contribution here. General cut-rank, stabilizer and semisimple-module
theory are not claimed as new.

Chris R / Clear1nsight supplies the retained-history context in PR5425/5446.
The source-specific frozen repair is PR5526. Discussion5300/PR5310 uses
related module theory for a different finite-ring source-insertion contract.
P104 retains Gareth Davidson's PR2305, David Arias's PR2152, Cinna's PR2219,
the productive-helper, native, compiler and outer predecessors, and Ali
Romman's PR5544 integration. Its profile is evidence for the arithmetic
screen here, not a new verification of that full construction.

The exact scalar layer is unchanged from zxv's
`research/universal-dirty-certificates/fields.py`; its notice is retained.
[SOURCES.json](SOURCES.json) pins the source files and unchanged local
copies. New proof, code and prose: Ali Romman, with substantial OpenAI Codex
assistance. No subagents. Apache-2.0. No selected-frontier change.
