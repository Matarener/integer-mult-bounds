# Exact optima for fixed-budget hidden windows

Claim type: proposed scoped mathematical proof with exact finite corroboration.
Prepared for human review; no new kappa.

This follows Karnaugh33's [PR6139](https://github.com/CrocSwap/integer-mult-bounds/pull/6139)
and Nick Petalas's [PR6153](https://github.com/CrocSwap/integer-mult-bounds/pull/6153).
PR6153 already classifies all budgets attaining the earlier lower bound. Its
remaining question is the actual minimum width at every other budget.

The proposed proof here reduces that optimization to discriminant one, with
one completely classified small-budget exception, proved algebraically in
endpoint coordinates. The reference implementation
returns all minimizing residuals and a finite certificate checked by a separate
divisor formulation. No new multiplication algorithm or kappa is claimed.

## Exact claim

Use the same minimal rank alphabet 2^j, 0<=j<=2h+2, integer call counts,
h-fold endpoint zeros, two distinct interior roots and positive window as in
PR6139. The call budget N is **per profile**, including common paid padding.
Set S=6^h/2 and L=floor(N/S). Then:

- L<31: no eligible profile pair exists.
- 31<=L<=34: the only oriented residual is 5x^2-15x+11, with discriminant 5.
- L>=35: every minimum-width residual has discriminant 1. Maximize its trace z
  over the exact integer search in [PROOF.md](PROOF.md); the minimum width is
  log_2((z+1)/(z-1)). All ties and permitted common padding are included.

The proof supplies a feasible discriminant-one seed whose width is strictly
less than every residual with discriminant at least four. Integer discriminants
cannot equal two or three. This proves the reduction for every budget, rather
than inferring it from a search. The remaining search uses square tests in
(z,k), with k=R(1); certificate verification uses divisors of t(t+1).

This is an exact finite algorithm and an all-budget theorem under the stated
hypotheses. It is not an elementary closed formula for the maximizing trace.

## Examples

The table uses h=1, hence S=3. Counts are per side before common padding.

| N | L | All optimal residuals (a,z,c), meaning ax^2-zx+c | Calls per side |
|---:|---:|---|---|
| 92 | 30 | none | — |
| 93 | 31 | (5,15,11), discriminant 5 | 93 |
| 111 | 37 | (6,17,12) | 105 |
| 120 | 40 | (6,19,15) | 120 |
| 432 | 144 | (28,71,45), (30,71,42) | 432, 429 |
| 1000 | 333 | (60,161,108), (72,161,90) | 987, 969 |
| 3000 | 1000 | (205,491,294), (210,491,287) | 2970, 2964 |

The (5,15,11) polynomial already appears in PR6153's verifier; the new claim
is its complete small-budget uniqueness threshold. The N=1000 result exactly
reproduces PR6139's census. The L=144 tie is also
in PR6153. They are regression checks, not new claims. Intermediate and larger
cases illustrate the general procedure; the uniform claim rests on the proof.

## Reproduce locally

Python 3.10+ standard library only; tested here with CPython 3.14.7.
From this package directory:

```sh
python3 -I -W error -B verify.py
python3 -I -W error -O -B verify.py
python3 -I -W error -B independent_check.py --package .
python3 -I -W error -O -B independent_check.py --package .
python3 -I -W error -B endpoint_coordinate_check.py
python3 -I -W error -O -B endpoint_coordinate_check.py
python3 -I -W error -B optimum.py --budget 1000 --h 1
python3 -I -W error -B optimum.py --normalized-budget 100000
```

Expected suite marker: `PASS_EXACT_HIDDEN_WINDOW_OPTIMA`. The initial full
normal replay took about two seconds on the author host; time is host-dependent.
Commands write JSON to stdout only. They do not use network, subprocesses,
repository executables or optional dependencies. Checks use explicit exceptions
and remain active under optimization. The suite compiles the adjacent `optimum.py` source bytes directly and hashes
those same bytes in its receipt; adjacent bytecode caches cannot replace them.
Isolated Python mode works.

The repository package runner accepts the metadata and six pinned provenance
files with `--check-only`. VERIFY.json registers all six checker commands for
its required Python 3.12 environment. That managed replay was not run locally:
Python 3.12 was unavailable; direct replays used CPython 3.14.7. The metadata
pass is not a mathematical acceptance check.

The reference API accepts 0<=L<=100000, or 1<=h<=16 and a positive N with
floor(N/(6^h/2))<=100000. It rejects booleans, wrong types and values outside
those bounds. The mathematical proof has no such caps. The constructor makes
O(L) exact square tests; no bit-complexity or runtime improvement claim is made.

## Verification coverage

- Literal positive-coefficient enumeration checks **10,586,800 triples** through
  L=400, including every discriminant, and all **401** budget prefixes. It finds
  14,498 eligible residuals and the unique exception below 35.
- A separately organized divisor census checks all **4,062** budgets 35..4096,
  finds 1,867 discriminant-one residuals, and verifies every certificate and tie.
  It makes 260,610 divisor trials. The dominance proof is still required to
  exclude other discriminants outside the full-triple census.
- An all-discriminant largest-c oracle checks 13 specified budgets through
  L=8192, totaling **2,815,810** (a,z) pairs. Its completeness argument is written
  in PROOF.md and its small cases agree with the literal census.
- 78 signed profiles check exact counts, rank mass, endpoint multiplicities and
  signs; 156 common-padding/scaling cases check h=1..6 and budget remainders.
- 21 invalid-input/certificate controls, two excluded-root-boundary fixtures,
  a seed-only counterexample, four larger reference cases through L=100000,
  and 2,002 seed-interval/large-integer fixtures pass.
- Separate reviewer checks add a signed-quartic/Sturm census of 13,590,150
  trials through h=1,N=150; a Farey-root census through L=4096; 741 malformed
  certificates; and an endpoint-coordinate census of 98,182 triples through
  L=512. See REVIEW.md for independence and coverage limits.

Normal and optimized outputs should agree after excluding elapsed time. The
stdout receipt hashes this package's Python, Markdown and JSON files.
SOURCES.json binds predecessor and guidance files to exact Git blob IDs and
SHA256 hashes at the recorded base commit; these are provenance, not runtime imports.

## Credit, review status and limits

[SOURCES.json](SOURCES.json) pins current main
`a5bff3bf133e482541c09eba4e773884bdb2b1b7` and the exact predecessor heads.
Both PR6139 and PR6153 are merged but listed as **partially reviewed** in the
current ledger. Their scientific status is not promoted by this draft.

Karnaugh33 supplies the normalization, width bound, comparison statistic and
seed family. Nick Petalas supplies the complete bound-attainment classification.
zxv's PR6049 supplies the minimal-support framework, retaining Nick Petalas's
PR5174 and Ali Romman's rank-budget lineage. The quadratic and divisor identities
are classical. No global literature-priority claim is made.

This proof, code and checks were produced with substantial OpenAI Codex
assistance, using GPT-6 Astra Ultra authoring and separate AI reviewers.
Separate AI reviewers challenged the proof, reran normal/optimized checks and
added independent signed-polynomial/Sturm, Farey-root and endpoint-coordinate
censuses. One source-loading weakness was corrected in this package; original
research evidence was preserved. See REVIEW.md for coverage and limits.
Human mathematical review and proof-assistant checking remain outstanding.

The alphabet and zero-pattern restrictions are essential. No arbitrary-rank or
larger-support result, legal native supplier, independent targets, restoration,
compiler, stock, precision/tape or analytic recovery is established. The five
framework assumptions and selected kappa 781451/250000000 remain unchanged.
Selected scientific replay, predecessor executables, Lean, Docker and hosted
CI were not run. No existing package or selected record was edited.

## Open next questions

First independently review the discriminant-domination inequality and exact
search completeness. A useful later formalization would prove the finite
integer certificate checker sound under the polynomial reduction. Its blocker
is a proof-kernel development, not a larger search. No additional construction
or arbitrary-alphabet campaign is reserved or justified by this side result.

Apache-2.0; retain predecessor attribution.
