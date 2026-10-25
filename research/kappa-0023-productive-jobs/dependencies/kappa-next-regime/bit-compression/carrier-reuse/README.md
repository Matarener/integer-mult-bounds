# Read common contributions early, then reuse the carrier

This scope makes two concrete changes to the BIT output interface:

1. Two adjacent targets read one common side query from the same original
   carrier at a shared codimension-two frame. They then move to their own
   hyperplanes and read their exclusive contributions. This reduces the
   observed side functions from ten pair-partials per target to three
   functions per target pair, without private side copies or extra raw
   rank backtracking.
2. For one isolated target pair, the common original-input gather is
   uncomputed immediately after those two reads. Its arbitrary dirty
   carrier is then reused for an exclusive query. This is a literal
   three-to-two helper reduction with all original inputs and helpers
   restored, no CLEAR operation, and no downward frame transitions.

**No new multiplication kappa is admitted.** The all-port consumer has a
fully paid but large reference producer. The isolated two-helper fragment
does not yet compose into an all-port source router. Exact profile screens
show the quantitative opportunity if a compatible compressed producer is
found; they are labeled as acquisition targets throughout.

## What was proved and checked

For targets T=K+{a} and U=K+{b}, with |K|=4, let C be their common side
neighbor sum and D_T,D_U the exclusive sums. Their outputs are -(C+D_T)
and -(C+D_U). C has rational source span
F=(span{t_T,t_U}) perpendicular under H=I-(2/25)J. Its rank is h-2 and
its normal Gram matrix is [[3,2],[2,3]]. The exclusive sums also span
explicit nondegenerate rank-(h-2) frames.

Both targets first read C at F. Only afterward do they move to their
distinct final hyperplanes. The proofs establish these inclusions for
every h>=9 and check all prototype source lines and exact rational
projectors at h9 and h19. The ambient form is indefinite at h19;
nondegeneracy, rather than an incorrect positivity assumption, is used.

| Certificate | Exact verification |
|---|---|
| All-port reference at h9 | 5,418 independent scalar roles; full operator for both signs, 29,354,724 coefficients per sign |
| Literal native phase schedule | All 33,120 ADDs checked at owner/query-specific common frames; 16,038 recursive frame changes reproduce the rank histogram |
| Dirty-helper controls | Four omitted-observation words are rejected |
| Two-helper isolated pair at h9 and h19 | Complete integer operator for both signs; every original input and both arbitrary dirty helpers restored |
| h19 two-helper fragment | 10,512 unit ADDs, 135,303,424 matrix coefficients determined by exact sparse rows; no private copies or extra rank backtracking |
| Global routing control | Explicit source requiring two distinct final hyperplanes rejects naive composition of the isolated fragments, even with delayed final retirement |
| Primitive moment screens | Exact rational log/exp enclosures; floating arithmetic only locates candidate endpoints |

The all-port scalar identity uses F3. The isolated pair identity holds
over the integers and therefore every scalar characteristic. Scalar ADD
counts exclude additional linear copying, retirement, routing and tape
work; recursive transforms on copies are charged in the rank profile.
The results concern native local phases under the retained stream contract
and shared padded cover. They do not certify a new outer arbitrary-precision
multiplication engine.

## The h19 numbers and what they mean

Here V=11,628, c=171, and the inherited cover width is m=57. A is the
number of persistent helper streams. The primitive moment parameter a is
not automatically the multiplication exponent improvement kappa.

| Model | Persistent helpers A | Status | Passing primitive a |
|---|---:|---|---:|
| One occurrence per source per query | 30,651,408 | Complete paid reference | 0.000005084 |
| Three query carriers per target pair, plus centers | 17,613 | Terminal-only acquisition target | 0.004471641 |
| Two carriers per target pair through early reuse, plus centers | 11,799 | Global acquisition target; isolated fragment constructed | 0.005369309 |

The complete paid reference is intentionally a simple construction that
makes every acquisition and restoration explicit. Its helper count is
larger than the previously retained joint-DAG reference; it is not a
numerical improvement over that reference or over the selected record.

For the first compressed target, the actual terminal profile is

\[
(5V/2+2c)H_{h-2}+(V/2+c)H_2+3V H_1+V H_{h-1}.
\]

Under the retained global profile 3 H_local + 2V H2, its h19 normalized
moment at a=.004 is **0.9993395917423624**, rigorously below one. A
compressed producer has room for at most **6,128 additional ideal H19
helpers**, or 23,741 helpers total, if it adds no other recursive work.
A separate V-source bank exceeds this first allowance.

The second target uses the proven isolated reuse pattern and has profile

\[
(3V/2+2c)H_{h-2}+(3V/2)H_{h-1}+(5V/2)H_1+cH_2.
\]

It has moment **0.998138608664116** at .004 and room for at most
**14,815 additional ideal H19 helpers**, or 26,614 total. This is a
larger design allowance. It remains conditional on a global producer:
the common inputs must remain available for early uncomputation, all
source routes must be compatible, and actual input acquisition fragments
the helper paths. The receipt separately prices several such fragmented
paths; the single-H19 allowance is an optimistic screen.

| Extra-helper trajectory at h19 | Three-carrier target: maximum extras | Reused-carrier target: maximum extras |
|---|---:|---:|
| One H19, optimistic | 6,128 | 14,815 |
| H1+H16+H2, acquired input reaching a codimension-two frame | 4,109 | 9,934 |
| 2H1+H17, acquired input reaching a target hyperplane | 4,456 | 10,773 |

Consequently, even the reused-carrier target cannot simply add a whole
V=11,628 bank with either displayed below-I input trajectory. The original
input reuse and the global frame-aware acquisition must be designed together.

Both models retain the split target path H(h-2)+H1, all center copies,
all helper retirements, both data endpoints, and the cover connectors.
Neither treats a source sum as a free input.

## Why the isolated reuse is an actual change

Before acquisition, the helper dirt z,w is compensated at frame zero:
Y_T receives 2z and Y_U receives z+w. The common helper then holds z+C,
which is subtracted from both targets at F. Reversing the common gather
while its original inputs remain at F returns the helper exactly to z.
That same carrier next holds z+D_T at H_T and is read again. The other
helper handles w+D_U at H_U. Reversing both exclusive gathers restores
the helper inputs.

This changes when the first carrier becomes available. Its signal is
removed by an explicit inverse computation while its parents remain
live. It does not assume an arbitrary dirty value can be cleared.

The exact global counterexample identifies the next difficulty: source
mask 31 would need to visit the distinct rank-18 hyperplanes for target
masks 241 and 227 in two different matched pairs. Those hyperplanes are
incomparable. A global producer must encode, combine, or route source
information before making such incompatible commitments.

## What the literature contributes

The primary sources in [LITERATURE.md](LITERATURE.md) support three
specific ideas: eager uncomputation while original inputs remain live;
in-place linear matrix realization without an output register bank; and
factorizations into single-register assignments. The first is implemented
by the two-helper pair. The latter two motivate a joint mutable producer,
but their unrestricted register model does not pay rational address
changes or enforce native common frames.

The next bounded experiment is a frame-aware linear basis quotient. For
each live query, choose a frame between its source span and the
intersection of its remaining target hyperplanes. After an early read,
that upper constraint can grow. Bring compatible live states to one
allowed frame, synthesize an invertible basis change using independent
dirty directions, and retain only the observations still needed. The
two-helper word is a positive test case; the incompatible-hyperplane
witness is a required rejection case. Such a producer must fit the exact
moment allowance before it can be turned into a kappa claim.

## Reproduce

Use ordinary Python 3 with its standard library. No external packages,
network access, inherited paths, or installed repository checkout are
needed to execute these checks. The source compiler and cover documents
are proof dependencies identified in SOURCES.json, rather than runtime
imports. The interval/matrix helper file under reference/ is an exact
copy of the prior frozen program and is hashed in each receipt.

```bash
python -B paired_consumer.py
python -B borrowed_pair.py
python -B verify.py
```

The last command authenticates the declared file inventory, makes a fresh
relocated copy, deletes both generated receipts, regenerates them, and
compares their exact bytes. It writes VALIDATION.json. By default the
temporary replay tree is removed after successful validation.

Files:

- `PROOF.md`: general algebra, rational geometry, phase paths, both cost
  ledgers, exact scope of the negative routing witness, and the next
  synthesis problem.
- `PAIRED-CONSUMER.json`: rational frames, full all-port scalar replay,
  labeled native phases, fully charged reference invoices, conditional
  terminal profiles, and exact moment/helper-budget gates.
- `BORROWED-PAIR.json`: two-helper integer operators, all actual native
  transitions, negative controls, and explicit routing witnesses.
- `SOURCES.json` and `LITERATURE.md`: source pins, primary papers and
  model distinctions. No exhaustive novelty claim is made.
- `REPLAY-PLAN.json`, `INTEGRITY.json`, `VALIDATION.json`: reproducibility
  plan, canonical byte inventory and relocated verification receipt.

Prior frozen files in bit-output and kappa-resume are unchanged.
