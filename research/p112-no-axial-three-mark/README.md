# Source-span floors and density budgets for three P112 targets

At the fixed marks `{0,67}`, `{7,64}`, `{1,75}`, the package now closes **every
rational query dictionary in their canonical span**, with arbitrary term count
and actual readers. The exact minimum is18. A complete441-type tariff table
and support-monotone normalization reduce any hypothetical cost<=17 decoder
to at most five terms; the precisely cited prior five-term theorem closes
that remaining case. The same statement holds with queries and readers
exchanged. This is an all-coefficient source-span result at one placement,
not a fixed-dictionary or coefficient-box search.

FIXED-THREE-MARK-SOURCE-SPAN.md gives the new reduction and its exact prior
dependency. Two independent checkers rebuild all441 tariffs. The general
source-density budgets below also apply to other distinct ordinary roles.

For three ordinary canonical marks in distinct paired roles, suppose every
query is in their span and uses at least two marks. Restrict arbitrary actual
readers to the six selected ports and remove zero terms; let n count the
remaining terms. The full physical-group invoice is at least **12+n**.
Thus six or more active terms cannot improve the canonical local cost18.
The proof covers every rational coefficient choice, arbitrary reader asymmetry
and cancellation, and unbounded term counts within these explicit premises.

Allowing axial queries still gives a useful finite bound. Merge parallel axial
queries without increasing cost; let a<=3 count the remaining axial terms and
n count all active terms after restriction and merging. AXIAL-PROOF.md proves
**cost>=12+n-3a**. Therefore any cost<=17 witness has at most8,11 or14 normalized
terms when a=1,2 or3. This does not construct a saving or exclude those ranges.

The argument combines small binary geometry facts with incidence counting:
each query spans at least8 physical dimensions, a reader touching k selected
triads costs at least k+1, and six marked outputs require at least12 reader
incidences. No coefficient grid or invoice census is used.

Combining with the separately retained five-term triple theorem from
[PR3684](https://github.com/CrocSwap/integer-mult-bounds/pull/3684) rules out
all term counts in this class. That corollary has an explicit prior-theorem
dependency; the standalone12+n bound does not. The prior package's full
classification is not rerun here, and archival merging is not scientific
approval. PROOF.md and SOURCES.json identify the exact source head and proof pins.

## Reproduction and scope

From the repository root, Python3.12 or later, standard library only:

```sh
python3 -I -O -Werror -B research/p112-no-axial-three-mark/verify.py
python3 -I -O -Werror -B research/p112-no-axial-three-mark/independent.py
python3 -I -O -Werror -B research/p112-no-axial-three-mark/fixed_three_mark_source_span.py
python3 -I -O -Werror -B research/p112-no-axial-three-mark/independent_fixed_source_span.py
python3 -B scripts/research_package.py --package research/p112-no-axial-three-mark
```

All four checkers authenticate only the two foundational geometry inputs. Their
normal modes are read-only. They use different rank methods and validate the
finite premises of the written proof, not the general theorem by enumeration.

The12+n theorem excludes axial queries (a single marked coordinate); the
12+n-3a bound covers them after the stated normalization. The general density statements exclude exterior
query directions, repeated paired roles, singleton/residual targets and
changed endpoints; the complete source-span closure fixes one placement. It supplies no cost296 decoder, native schedule, universal
334 floor or improved multiplication bound.

## Open next questions

- Can another physical placement admit a cheaper axial/dense mixture? First check whether the complete441-type cheap-tariff obstruction also
  applies there; otherwise use the normalized term cap and at-most441
  exact support types at one declared placement, with cancellation constraints
  and invoice<=17. Blocker: support feasibility alone does not provide
  compatible nonzero rational coefficients or an exact endpoint.
- Can a larger jointly interacting marked set or an exterior direction evade
  these costs? First provide one exact endpoint identity and a favorable
  symbolic source/reader tariff budget. Blocker: density can erase rank savings,
  and no such candidate is supplied here.

## Credit

The geometry and canonical cover retain their original P112 attribution.
The earlier five-term boundary is flyingviper's PR3684, including Nick Petalas'
classification and transfer lineage as credited in that package. The present
source-density argument is a local deduction, arising while screening a
signed non-Fano gluing; the motivating literature is identified in PROOF.md.
Prepared by flyingviper with substantial OpenAI Codex assistance and separate
AI-agent proof/implementation audits. No independent human or proof-assistant
review is claimed. Apache-2.0.
