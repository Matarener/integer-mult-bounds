# Mixed P112 pair queries have the sharp actual-reader floor

**No new κ.** For the literal PR3370 partition, replacing any two of its
32 indicator queries by **any finite list of queries in their span** cannot
lower the complete-plane actual-reader tariff below the two original terms.
This includes arbitrary mixtures of axes and dense directions, arbitrary
coefficient fields, and readers that cancel outside the target. All 496 pairs
are covered. Disjoint pair replacements therefore retain the total floor **224**.

The new step is a four-direction normalization: merge the two axis directions,
then use submodularity of binary rectangular rank to replace all dense readers
by two nested support layers without increasing the charge. This turns the
unbounded list into a finite three-state-per-port problem. The exact census
covers all **435,456 states** for 120 distinct group pairs; the remaining
16 same-group pairs have a short plane-wise rank argument. Literal axis queries
attain every stated bound.

[PROOF.md](PROOF.md) gives the quantified argument, finite certificate contract,
and exact scope. [RESULT.json](RESULT.json) records every pair's gap histogram,
equality count and rank-table digest. The written proof plus the finite geometry
checks establish the scoped result; a finite replay is not a formal proof of
all-size multiplication.

## What is new and why it matters

Tekalign's PR3370 supplies the exact sixteen-group partition and its 224 literal
tariff. Nick Petalas's PR3429 covers at most three projective directions;
PR3447 covers arbitrarily many **dense-only** directions and explicitly leaves
mixed lists open. This package removes that mixed-list restriction using a
submodular multicover argument, without importing either predecessor theorem or
code. It changes supports collectively, so it does not assert the termwise
binary map that PR3429 shows can fail at four directions.

PR3383's whole-row-space **query self-cost** is different from the actual
rectangular reader cost used here; PR3398 already identifies that distinction.
The controls retain a literal term with self-cost greater than actual cost.
No credit is claimed for the partition, dense-only floor, three-direction
floor, or elementary rank submodularity itself.

This rejects a specific proposed source of savings before native construction:
mixed pair recoding cannot reduce **copied-rank mass**. It does not rule out a
more favorable recursive rank distribution at the same or larger mass, a
multi-indicator recoding, a changed fitting matrix, or a different physical
contract. The selected complex and bit suppliers and overall multiplication
result are unchanged.

## Reproduce and inspect the evidence

From the repository root, standard-library Python 3.12:

```sh
python3 -I -Werror -B scripts/research_package.py --package research/p112-mixed-query-reader-floor
```

Expected: `PASS_MIXED_QUERY_READER_FLOOR`, `PASS_MIXED_QUERY_INDEPENDENT`,
`PASS_MIXED_QUERY_CONTROLS`, then `PASS_REGISTERED_RESEARCH_PACKAGE`.
The bounded replay takes seconds to tens of seconds, depending on the machine.
`VERIFY.json` registers all three commands and the sole live external input.

- The primary checker uses integer column elimination and the two-layer formula.
  It also checks all 1,505,280 entries of 120 exact rational operator fixtures,
  including 40 cancellations outside the target.
- The separately written checker imports neither primary nor predecessor code.
  It uses explicit binary matrix row elimination and direct minimum-cost
  multicover dynamic programming: **23,319,544 transitions**, independently
  reproducing all 435,456 layer equalities and complete pair receipts.
  It checks 15,714 coefficient tuples over F2,F3,F5 and 1,272 axis deliveries.
- Seven mathematical control/boundary groups cover partition and orthogonality,
  omitted dense work, an invalid operator after a term is removed, incomplete
  plane closure, self-cost confusion, and 32 exact same-group operators.
  Three real optimized-CLI corruptions alter the live source, retained artifact
  and expected result. Each must fail; the restored optimized replay must pass.

The committed receipt is regenerated only by the explicit package-local
`verify.py --write-receipt` option. Normal replays are read-only.
[VALIDATION.md](VALIDATION.md) records tests actually executed and their limits.

## Pins, search coverage and budget decision

Base main: `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
[SOURCES.json](SOURCES.json) binds the originating card and selected record,
the live binary-label payload (Git blob plus SHA256), the unchanged retained
PR3370 certificate, and exact bibliographic predecessor heads. The certificate
was compared byte-for-byte with the public pinned PR3370 source. No pending Git
object, external package, solver, or network access is needed for mathematical
replay. The registered metadata check additionally uses the base Git objects.

[Task and local claim](TASK.json): OS-random assignment seed **25**, complex
supplier track, priority revision 6. Three narrow candidate scopes were compared;
`25 mod 3 = 1` selected the mixed-list handoff. The seed also fixes supplemental
operator fixtures, but does not randomize the exhaustive census. The normal-form
search domain is all 120 distinct group pairs and all ternary states; the
stopping rule was complete enumeration or a counterexample, before any native
implementation. Completed coverage is exact for this finite domain.

The overlap helper searched 3,738 local records but lacked `gh` remote access;
connected GitHub searches and public newest handoffs supplied the live checks.
The public discussion page hides older comments, so this is not a complete
novelty census. No pinned sprint issue was found, and the connected tools offer
no Discussion write, so the claim and final handoff are local-only. No upstream
PR or reservation issue was created.

The optimistic experiment charges actual copied rank and relaxes all other
nonnegative costs. Acquisition, scalar coefficients, frames, dirty restoration,
physical hosting, stock, precision and the full recursive/outer invoice are
**unknown**, not zero in an admitted supplier. Because the proposed copied-mass
saving is absent even in this relaxation, this session stops that implementation
route. The broader family is not closed. Inherited all-size/compiler, source
realization, bit-supplier and analytic-transfer assumptions remain untouched.

## Open next questions

- Can a specific three-or-more-indicator recoding reduce the actual tariff?
  It is outside the pair-span reduction and could alter the copy budget. First
  specify the exact source subspace, produce an exact factorization, and price
  rectangular reader supports; a self-Gram sum is insufficient.
- Can a pair recoding with equal mass improve the *complete recursive moment*?
  This result does not order rank distributions. First compare one fully stated
  profile at a certified reference exponent, then account for native acquisition,
  coefficients, frames and restoration. No physical saving is established here.

These are the structured handoffs in `TASK.json`; this package claims neither.

## Attribution and license

Prepared for **@CubeJerry**, with substantial **OpenAI Codex** assistance in
mathematics, implementation, documentation and verification. The separate
implementation is code-disjoint but by the same AI-assisted contributor, not
independent human review or proof-assistant verification.

Credit Tekalign (`tekuuu`), PR3370; Nick Petalas (`petalas`), PR3447/3429/3398/3383
and the PR3356/3414 lineage; Philippe Van Velzen and PR3345; Matarener/Mark and
PR3335; and the retained E8/P112/native/compiler/supplier lineage, including
ywz65, thakrarsagar, Cinna Davis, Adam Gall, ctoth and Jeremy Diviney. Their
source-specific credit remains authoritative. `RETAINED-RANK32.json` is
Tekalign's unchanged PR3370 artifact. New work and that retained artifact are
under the repository's Apache-2.0 license.
