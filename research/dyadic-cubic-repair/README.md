# Dyadic coefficients for cubic-reader repair

Prepared by **apoursh** with substantial OpenAI Codex assistance. Apache-2.0.
**Scoped proof with exact finite corroboration; no new kappa.**

This answers the first open question of Nick Petalas's
[PR6200](https://github.com/CrocSwap/integer-mult-bounds/pull/6200), pinned at
`8b705d15869ba12d55adcb9075c68a2c7d44602d`. Retain every original child
`y += a^3; a += b`, then repair the source and output to the eager endpoint
on arbitrary incoming y,a,b. The predecessor proves that two rational cube
queries suffice exactly when `(2r-1)^2-6k^2=3` has an integer solution k.

The new coefficient-ring classification is:

- Over `Z[P^-1]`, two queries suffice exactly when that equation has a
  positive integer solution k and every prime divisor of k is inverted.
- The obstruction applies to arbitrary nonmonic forms: rescaling cannot hide
  the forced reduced weight denominator k.
- Over dyadics `Z[1/2]`, two queries suffice **only for r=2**.
- For r>=5 with r=2 mod 3, exactly **three integer-weighted queries** attain
  the dyadic minimum. Four integer-weighted queries suffice for every r>=3.
  Three dyadic queries also attain r=3 and r=4. A full classification of
  three versus four for the other residue classes remains open here.

[PROOF.md](PROOF.md) proves the all-r statements and gives the complete
source-restoring schedules. At r=14, the optimal rational repair uses weights
`+/-91/11`; dyadic coefficients require at least three queries. This integer
program attains three, starting from the actual drifted source `a_entry+14*b`:

```
a -= 9*b
y -= 91*a^3
a -= b
y += 91*a^3
a -= 4*b
y -= 2730*b^3
```

Every one of the fourteen original cube children remains. The program replaces
fourteen eager restoration shifts with three shears and three extra cube
queries. This is an event-count comparison, not a runtime improvement.
Weighted query, coefficient preparation, source access, routing, private
restoration, precision, storage and dispatch costs still need a physical bill.
Reading b directly is in the predecessor's alphabet; a backend restricted to
one designated read register must also pay routing and its reversal.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/dyadic-cubic-repair
python3.12 -I -W error -B research/dyadic-cubic-repair/verify.py
python3.12 -I -O -W error -B research/dyadic-cubic-repair/verify.py
python3.12 -I -W error -B research/dyadic-cubic-repair/independent_check.py
python3.12 -I -O -W error -B research/dyadic-cubic-repair/independent_check.py
python3.12 -B scripts/check_research_commit.py --package research/dyadic-cubic-repair --check-source-history
```

The registered runner executes both checkers in normal and optimized modes.
Checks are exact, bounded and read-only. The written proof establishes the
universal lower bound and constructions; finite arithmetic scans do not prove
them by extrapolation. The independent checker is separately authored AI work,
not independent human or proof-kernel review. No predecessor executable is
imported, and no selected-supplier cold replay is claimed.

The primary checker replays 255 universal integer programs (r=2..256) and
85 congruence-family programs, including every retained child, the eager
endpoint, source restoration and both literal inverses. Seven Pell fixtures
test the forced denominators; 584 nonmonic normalizations over 38 ring-case
iterations corroborate the localization argument. Ten semantic controls
detect changed query weights, omitted readers or restoration, reversed
chronology, an assumed entry snapshot, forbidden coefficients and feedback.

The independent checker obtains the defect by binary concatenation of literal
reader blocks and fits cube weights by exact elimination. It checks 136
arities, including eight Pell fixtures and three large arities, with 136
four-form and 51 main-family replays, plus the r=3,4 examples. Four controls
test restoration, signs and hidden odd denominators. The distinct derivation
avoids importing the primary checker or predecessor code.

Both registered normal/optimized replays passed locally on CPython 3.12.14,
macOS arm64. Separate copies with either retained source document corrupted
or the predecessor head changed are rejected. Committed-byte/mode/source-history
preflight, official export integrity and read-only Git-free replay are the
publication checks; their results are reported in the PR.

## Sources, coordination and scope

The retained [source proof](sources/pr6200-PROOF.md) and
[source README](sources/pr6200-README.md) preserve the precise pending contract,
open question, attribution and license for offline review. Their bytes were
compared exactly against the immutable raw URLs in
[SOURCE-PINS.json](SOURCE-PINS.json); the primary verifier checks both hashes.
The pending head is a source label, not an asserted ancestor of this branch.
It is not a Git source pin in SOURCES.json, and the source-history preflight
does not independently authenticate publication of that pending head.

[SOURCES.json](SOURCES.json) pins the original card and selected record through
base `a5bff3bf133e482541c09eba4e773884bdb2b1b7`. All scientific runtime files
are package-local, so package changes trigger replay; there are no external
live inputs. Full source documents are retained for the cited contract, not
as a copied predecessor computation. The selected record remains PR6030,
`kappa=781451/250000000`, with its five framework assumptions unchanged.

This is an explicitly changed scope of `joint-query-controller`: a nonlinear
coefficient-feasibility side result answering a concrete handoff. It does not
meet the card's complete supplier acceptance gate. A prior binding-only
orientation pass is reused after comparing all 1,227 covered paths against
the refreshed canonical base and finding no changes. No scientific replay
or assumption discharge is inferred from that reuse.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19275718)
records the investigation. Overlap coverage includes the newest twenty PRs
through #6211, all-state searches for `cubic dyadic`, `cubic repair` and `6200`,
and the newest fifteen visible handoffs. The local sparse helper searched
30 of 8,623 HEAD note paths and had no usable remote cache; this is not a
global novelty certificate. PR6200 explicitly leaves this question open.
PR6192/6208's linear cyclotomic operators and PR5084/5132's norm-six feature
factorization concern different objects; their computations are not combined.

The contract excludes child fusion, intermediate observations, output feedback,
nonlinear source maps, approximate queries and finite fields. No actual native
caller, selected-supplier integration, favorable complete invoice, all-size
compiler, stock bound, Lean or Docker replay is supplied. Shared infrastructure,
predecessor packages, frozen evidence and selected frontier are unchanged.

## Credit

Nick Petalas retains PR6200's defect calculation, rational criterion, Pell
test, restoring-schedule method and dyadic handoff. Sricharan Vagvala /
theon199 retains PR1532's quadratic fixed-reader/paid-repair interface;
Adam Gall / PR1205 and Hanson Sun / PR1246 retain the linear lineage.
Classical binary-form decompositions and elementary localization retain their
background credit. No general Waring-rank theorem or historical priority is
claimed. OpenAI Codex assisted derivation, proof, separately authored checkers,
mathematical audit, documentation and publication for apoursh.

## Open next questions

1. **Which further arities admit three dyadic queries?** The proof includes
   r=3 and r=4 examples outside the main congruence family. Start with the
   three-form coefficient equations, allowing nonmonic forms and using prime
   valuations to derive further families or an obstruction. A failed monic
   or finite search would not settle the remaining three-versus-four gap.
2. **Can an actual r=14 caller benefit?** First pin the indivisible child
   interface and price every event in the displayed program and eager
   comparator. The missing backend and complete favorable bill block any
   claim of paid-work or multiplication-bound improvement.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).
