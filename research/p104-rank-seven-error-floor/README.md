# Every real rank-seven P104 Gram approximation has error at least 1/4

The exact minimum maximum coefficient error is **1/4 over all real
104-by-104 matrices of rank at most seven**. This removes symmetry,
positivity, contractivity, and fixed carrier row/column spaces from
Nick Petalas's [PR6183](https://github.com/CrocSwap/integer-mult-bounds/pull/6183)
result. It answers that package's first open question. No new kappa is claimed.

Eight orthogonal D8 root columns turn any deficient-rank candidate into
a nonzero null vector. A sharp l1 norm comparison forces the error floor.
PR6183's omitted-root projector attains it. The [written proof](PROOF.md)
covers every real candidate; exact finite checks corroborate its identities
and exercise candidates outside the predecessor's domain.

The P104 coordinate identification remains an explicitly cited premise
from Matarener's PR6166, retained through PR6183. This contribution verifies
the resulting root configuration, not its physical port identification.
Both predecessors are archived as partially reviewed in the current ledger;
archival inclusion is not scientific acceptance.
The theorem also applies to all D8 lines plus any proper subset of one
half-spin shell. Root representative signs do not matter.

## Reproduce

With CPython 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -W error -B research/p104-rank-seven-error-floor/verify.py
python3.12 -I -W error -O -B research/p104-rank-seven-error-floor/verify.py
python3.12 -I -W error -O -B research/p104-rank-seven-error-floor/independent.py
python3.12 -B scripts/research_package.py --package research/p104-rank-seven-error-floor
```

The direct marker is `PASS_P104_RANK_SEVEN_ERROR_FLOOR`; the registered
marker is `PASS_REGISTERED_RESEARCH_PACKAGE`. Direct runs read only and
emit a deterministic JSON receipt with computed coverage counts. They work
in a Git-free export with an empty PATH when Python is invoked absolutely.
SOURCES.json authenticates the three predecessor document/data inputs;
VERIFY.json declares all of them. No predecessor executable is imported.

The checks cover the orthogonal eight-column frame, exact null-vector norm
inequalities, all sixteen attaining projections and every matrix entry,
oblique filters, candidates with row/column spaces outside the root code,
and hypothesis/normalization controls. Normal and optimized replay pass
6,560 nonzero ternary directions, 128 rational directions, sixteen projections
with 173,056 literal matrix-error entries, three carrier fixtures and one
candidate outside both carrier spaces. Four boundary/normalization controls
and three malformed-input rejections also pass. The proof, rather than these
finite fixtures, establishes the universal quantifier. See the emitted receipt
for exact counts and [TASK.json](TASK.json) for verification coverage.

The separately written `independent.py` uses literal Fraction roots and a
different root order, with no primary-checker import. Its optimized registered
replay passes 147 vector fixtures (including two tight norm witnesses) and
194,688 matrix entries across sixteen attaining projectors, an oblique
projector (error 3/8), and a matrix outside the carrier factorization
(error 1/2). It corroborates arithmetic and scope boundaries; it does not
mechanically prove the universal statement or constitute human review.

## Selection, overlap, and expansion decision

Canonical main was pulled first at
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8. The selected
record still specifies conditional kappa `781451/250000000` with five
framework assumptions. Its previously passing binding-only orientation
was reused after all 1,227 recorded inputs were unchanged from the prior
checkpoint; this is not a fresh scientific replay.

This takes the released [PR6183 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19268192).
The original `coverage-law-change` card is retained in TASK.json, with
scope explicitly changed to an algebraic approximation question. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19271534)
records the initial arbitrary-carrier question and its extension to all
real rank-seven matrices. Bounded all-state PR searches and the newest
visible handoffs found no competing result. The local overlap helper
searched only 28 of 8,623 notes and had no remote cache; neither it nor
the bounded live search certifies exhaustive novelty.

Nearest work: PR6183 proves the contractive case and provides attainment;
PR6181 concerns exact joint-bank spectral conjugacy over Gaussian dyadics;
PR6173 concerns generalized code support over F3 and Q. Their different
quantities are not compared numerically or silently treated as validated.

Decision: close this approximation escape, then stop. The boundary is the
whole real Gram block on arbitrary inputs. A seven-dimensional real linear
intermediate cannot approximate it arbitrarily accurately, even with new
encoder/decoder spaces. Correction, native implementation, restoration
and complete costs remain unknown. This local proof justifies no further
construction campaign or selected-frontier change on its own.

## Open next questions

- Can a changed side correction absorb an attaining residual at a favorable
  complete cost? Start with one omitted-root residual in an actual scalar
  word, charging acquisition, delivery and restoration. A physical caller
  and complete invoice are missing. This is PR6183's remaining second question.
- What is the optimum for arbitrary **complex** rank-seven approximants?
  The real absolute-value identity used here does not hold for complex
  coordinates. Start with a dual norm certificate or an exact complex
  factorization beating 1/4; numerical searches alone cannot settle it.
  No complex lower bound or physical realization is supplied.

## Credit and limits

New lower-bound proof and verifier: apoursh, with substantial OpenAI Codex
assistance and separate agent proof checks. Nick Petalas retains PR6183's
question, contractive theorem and attaining projection. Matarener retains
the D8 coordinate identification and omitted lines. Rohan Arun, Chafik
Boukhalfa, Ali Romman, DreamingOfClouds, Cinna Davis, Pierre-Loic Doulcet,
icekylinx, zxv, Jacob Alan Sussman and the retained P104/root/frame/native/
helper/compiler/BIT contributors retain their source results.

This is a scoped written proof with exact finite corroboration, not a
physical supplier, full multiplication theorem, independent human review,
or formal proof-kernel result. Masked accuracy and nonlinear consumers
remain outside scope. Sources and shared code are unchanged. Apache-2.0.
