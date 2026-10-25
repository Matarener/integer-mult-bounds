# Independent audit of the pointwise Clifford tensor theorem

**Independent AI-assisted proof audit; no substantive gap found in the stated core theorem.**
This package audits Sections 2–5 of Ali Romman's
[PR5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526) at
`45f7de73b168721cdf7ec8c1769b1b594493716a`: stabilizer and Clifford overlap counts,
uniform rational Gram bounds, and the four-residue fixed-program implication.
The theorem and constants remain the predecessor's work. No new kappa,
selected-frontier change, independent human review or formal verification is claimed.

The added value is a written independent review, a separate exhaustive binary-matrix
check, and literal exact matrix/phase evidence with failure controls. The
[audit](AUDIT.md) makes the Gaussian-dyadic lift step explicit and distinguishes
fixed exterior coefficients from width-dependent coefficients and arbitrary
nonunitary scales. The source already provides projective Choi and signed-Pauli
censuses; independently regenerating similar finite counts is corroboration,
not a new theorem. Our source proof and README copies are immutable, attributed
review inputs. No predecessor executable is imported.

## Evidence and reproduction

Python 3.12 and its standard library suffice. From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-pointwise-audit
```

The six registered commands run serially, each with a 120-second limit. The
literal matrix and independent symplectic checkers run both normally and under
`-O`; two mutation drivers each test both modes. On the recorded Linux/Python
3.12.14 host this is a small, single-CPU replay, with no large tensor matrices.
Actual commands, timings and results are recorded in [VALIDATION.json](VALIDATION.json).
Direct standalone commands also work from a Git-free package export:

```sh
python3.12 -I -W error -B research/clifford-pointwise-audit/verify.py
python3.12 -I -O -W error -B research/clifford-pointwise-audit/verify.py
python3.12 -I -W error -B research/clifford-pointwise-audit/verify_symplectic.py
python3.12 -I -O -W error -B research/clifford-pointwise-audit/verify_symplectic.py
python3.12 -I -W error -B research/clifford-pointwise-audit/audit_mutations.py
python3.12 -I -W error -B research/clifford-pointwise-audit/audit_matrix_mutations.py
```

The checks cover:

* All **96 + 46,080 exact Gaussian-dyadic Clifford matrices** on one/two axes,
  retaining central phases during generation and finding four phase lifts per
  projective class. Literal normalized trace distributions agree with the
  separate fixed-space character computation. The classical generator/order
  theorem is an explicit shared assumption; finite closure alone is not a proof
  of completeness for an unspecified group.
* All **16 + 65,536 binary matrices**, directly selecting 6 + 720 symplectic
  preservers. Their fixed spaces, actual character sums, residual-form preimages,
  nondegeneracy, symmetrization and injection are checked. This enumeration
  does not use Clifford gate generation or predecessor code.
* Exact Gaussian-rational ranks of the one-axis Gram matrix at widths 1–11,
  including the rank-23 width-four failure and rank-24 width-five positive
  fixture. The earlier PR5376 already establishes the sharp one-axis result;
  these are controls, not a claimed cutoff improvement. Both spectral bounds
  are checked by 192 positive rational Schur pivots at widths 8–11. The finite
  row budgets and complete infinite-tail majorants are checked separately.
* Four omitted-residue counterexamples; phase-copy singularity; the H-prime
  central phase; an omitted generator; exterior versus tensor scalar placement;
  changing coefficients; and a nonunitary-scale residual that passes four
  consecutive widths but fails the next. These expose the theorem's boundaries.
* Six actual defects in the independent checker, two false mathematical
  expectations and an erased tensor width in the matrix checker, plus source
  and receipt corruption: **22 rejecting subprocess runs** across
  normal/optimized modes. Expected diagnostics are required, not just nonzero exits.

`verify.py --emit` prints a fresh complete matrix receipt for comparison. Ordinary
replay compares [MATRIX-RESULT.json](MATRIX-RESULT.json) without writing it.
Mutation drivers write only to temporary directories. Source replay hashes bind
both retained documents, and their bytes were compared with Git blobs at the
exact fetched source head. [SOURCE-RECEIPT.json](SOURCE-RECEIPT.json) records those
pins. No pending-source Git objects or network are needed for standalone replay;
[SOURCES.json](SOURCES.json) uses only the canonical base for package provenance.

## Scope, coordination and review

The base is canonical `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
The task picker retrieved `formal-interface-lemma` after the live handoff-first
check. [TASK.json](TASK.json) records the changed scope: an informal independent
core-proof audit, before any formalization campaign. It answers part of
[this handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19174354)
in [Discussion5236](https://github.com/CrocSwap/integer-mult-bounds/discussions/5236).
The direct API claim attempt was rejected with `FORBIDDEN: Resource not accessible
by integration`; copyable claim text was supplied to the donor. No retrospective
public reservation is asserted.

Initial overlap covered 403 open PRs, 4,682 closed/merged PRs, 4,828 Discussion
records and all 7,402 local indexed notes. Snapshots are non-atomic and exclude
arbitrary diffs, nested source histories and unpublished work. PR5531 explicitly
uses the general bound as a premise; PR5521 audits the smaller monomial class.
The merged DLamdata PR2880 audits an unrelated encoded-bank theorem and is
unchanged. Neither an empty search nor a merged archive is scientific acceptance.

An independently deriving verifier and a skeptical reviewer found no substantive
defect. Their arguments and coverage are consolidated in AUDIT.md; the review
resolutions are in [REVIEW.md](REVIEW.md). Both are native AI agents. Shared
assumptions include classical stabilizer/Clifford structure, character
orthogonality, exact integer/rational arithmetic and the reviewed statement.
The lead's literal matrix orbit shares the general gate-generation idea with
one predecessor check; the exhaustive binary-matrix method is complementary.
Agreement alone is not the evidence.

The **later 104-return repair theorem, invoice, actual passive-caller binding,
native frontend implementation, physical costs and full multiplication theorem
remain unaudited here**. The source's complete registered suite was not run,
because it covers those additional claims and dependencies. The selected
PR5413 cold replay was also not run; the selected record is unchanged, and its
source-binding orientation is not scientific admission. This is a narrow audit,
not a general endorsement of PR5526 or any downstream application.

## Open next questions

The remaining portion of the original handoff is an independent source-bound
review of the actual passive-caller implication. Start with the latest pinned
application and inventory every allowed observation/operator, including ownership
and excluded internal prefixes. The blocker is that complete caller binding,
not another small-group census. Separately, the later paid-repair theorem needs
its own quotient/capacity/original-input audit and invoice binding. Check live
claims before taking either task. Structured first steps and blockers are in
TASK.json. This result does not justify another construction search within an
unchanged mechanism.

## Credit and license

Ali Romman supplies PR5526 and the retained PR5376 tensor-Gram/native lineage.
The classical ingredients include Dehaene–De Moor's stabilizer normal forms,
symplectic residual/Wall forms, character orthogonality, Fourier inversion and
Gram diagonal dominance. The source preserves related contributions by Chris R /
Clear1nsight, Krzysztof Wojt, Nick Petalas and the native/paid-history authors;
none of their applications or general methods is claimed as new here. The full
source attribution remains in the immutable copied README and proof.

Prepared for DLamdata with substantial OpenAI Codex assistance, including two
scoped native subagents. New work is Apache-2.0 under the repository license;
source notices are retained. This package changes no frozen predecessor,
shared verifier, project guidance or selected result.
