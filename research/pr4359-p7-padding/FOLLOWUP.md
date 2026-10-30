# Finite continuation over 209 algebraic profiles

`scan.py` checks pair counts p=2,...,20 and every split a+b=p-1. Each
candidate retains every middle idle, the first a initial windows and the
last b terminal windows. It uses 2p+1 copies of the pinned THREE-base
helper and unsplit paid inventories. The selected p7 profile is compared
with the actual native inventory in this package's `RESULT.json` (or the
fresh native result supplied by a caller).

The explicit candidate main profile has 224 outputs at rank16p+9 and,
for each l in {a,b}, 224 at every rank16j+25 for j=0,...,l-1. Whole idle
charges are 224 at rank8 for each of p-1 middle windows and 224 at rank16j
for j=1,...,l in each chain. This screen is arithmetic on these formulas;
it does not provide native admission for all 209 candidates.

For fixed p and 0<tau<1, a most balanced split maximizes this family's
target-minus-paid moment. A chain contributes the sum of
`g(j)=(16j+25)^tau-(16j+16)^tau`. Concavity makes g decreasing. Moving
one term from a longer chain to a chain at least two shorter increases
the moment. The checker nevertheless evaluates every declared split.

At C=0.00268648 the sole positive profile is p7,a=b=3,keep232127.
At C=0.00268649 all 209 moments are strictly negative. Each sign is
certified by outward rational enclosures in `FOLLOWUP.json`. These
finite negatives concern the declared formulas. They do not establish
an exhaustive mask search, an all-p barrier or global optimality.

Run `python research/pr4359-p7-padding/scan.py`. Normal replay compares
the checked receipt without writing; `--write-result` is an explicit
authoring option. Both source files are authenticated before importing
the interval engine. The enormous tensor and native programs are not
materialized by this bounded follow-up.
