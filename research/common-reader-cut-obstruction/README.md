# Four reversible cuts with no common dyadic reader

This contribution was produced by Nick Petalas. It is a **scoped proof with
finite corroboration**, and makes no new kappa claim.

Four rank-one source-response matrices each admit a normalized dyadic
channel. Every proper subfamily also admits one common reader, with a
separate source column at each cut. The four matrices together admit no
common reader, even if each response only has to be a dyadic unit rather
than exactly one. A fourteen-ADD reversible scalar word realizes the four
responses and restores all four arbitrary incoming coordinates.

The result rules out inferring temporal reader compatibility from cutwise
unit capacity, even after checking every proper subfamily of this example.
It does not claim that four is the smallest possible obstruction among
all matrices.

## Contract and exact result

Let D = Z[1/2], whose units are the numbers ±2^k for integers k. Source
coordinates x and dirty helper coordinates h are columns in D^2. At cut i,
the source response is M_i, so the actual helper contents are

```text
h_i = h_in + M_i x.
```

A fixed physical reader is a row a in D^(1×2). A normalized source-response
channel at cut i is a column b_i in D^2 such that a M_i b_i = 1. The source
column may vary arbitrarily between cuts. This deliberately gives the
construction more freedom than a fixed input basis would.

This definition concerns the coefficient of the source response. The
observed value a h_i also contains arbitrary dirt a h_in. The pairing test
does not erase that dirt or supply an independent productive output.

Take M_i = e_i e_i^T, where

```text
e_1 = (1,0)^T    e_2 = (0,1)^T
e_3 = (1,1)^T    e_4 = (1,-1)^T.
```

The theorem has three parts.

1. Each M_i has unit-pairing capacity exactly one. Every nonempty proper
   subset J of {1,2,3,4} has a row a and dyadic columns b_i with
   a M_i b_i = 1 for all i in J.
2. For every a in D^(1×2), there is an i such that a M_i b is in the
   proper ideal 3D for **every** b in D^2. In particular, no fixed reader
   produces unit responses at all four cuts.
3. The matrices occur as source responses along the explicit integer
   reversible word below. Its endpoint is the identity on both x and h,
   for every incoming state, including dirty h.

A fixed invertible dyadic change of helper basis cannot escape part 2:
any chosen output coordinate is still some row a. Cut-dependent unit
rescaling also preserves the obstruction. Extra coordinates, changing
readers, non-dyadic coefficients or a different response family change
the hypotheses.

## Proof

Each M_i has a unit entry and rational rank one. Selecting its unit entry
gives a one-channel identity pairing. Rank subadditivity excludes a
two-channel identity pairing.

For the proper-subfamily claim, omit any index k outside J and use the
corresponding row in this table. The displayed evaluations include all
three remaining cuts, so they also cover every smaller subset.

| Omitted cut k | Reader a | Evaluations a e_i at the other cuts, in index order |
|---:|---|---|
| 1 | (0,1) | 1, 1, -1 |
| 2 | (1,0) | 1, 1, 1 |
| 3 | (1,-1) | 1, -1, 2 |
| 4 | (1,1) | 1, 1, 2 |

Every displayed evaluation is a unit of D. Choose a coordinate j where
e_ij is ±1 and let b_i be the j-th coordinate column divided by
(a e_i)e_ij. Then b_i is dyadic and

```text
a M_i b_i = (a e_i)(e_i^T b_i) = 1.
```

For the obstruction, reduction modulo three is a ring homomorphism
D → F_3 because two is invertible modulo three. Write the reduced reader
as (u,v). If u=0, then a e_1 reduces to zero. If v=0, use e_2. Otherwise
u and v are both ±1, so either u+v=0 or u-v=0 in F_3. Use e_3 in the first
case and e_4 in the second. This covers every reader, including the zero
row. For the chosen i,

```text
a M_i b = (a e_i)(e_i^T b) = 0 mod 3
```

for every dyadic b. A unit has nonzero reduction, so this response is
never a unit. The argument covers unbounded numerators and power-of-two
denominators; its scope does not depend on a finite rational search.
Equivalently, the four kernels are all four lines of the elementary
projective-line cover of F_3^2.

The dyadic restriction matters. Over Q, the single row (1,2) has
evaluations 1,2,3,-1 on the four vectors. Dividing a selected coordinate
column by each evaluation normalizes all four responses. Exactly one
of those four columns uses a denominator three and is not dyadic.

## Reversible realization and dirty state

Use two unchanged source registers x_0,x_1 and two helper registers h_0,h_1.
An ADD below has coefficient +1 or -1 and acts on the actual current
contents. No helper is initialized to zero. Vertical gaps mark the cuts.

```text
h_0 += x_0
                         # M_1
h_0 -= x_0
h_1 += x_1
                         # M_2
h_0 += x_0
h_0 += x_1
h_1 += x_0
                         # M_3
h_0 -= x_1
h_0 -= x_1
h_1 -= x_0
h_1 -= x_0
                         # M_4
h_0 -= x_0
h_0 += x_1
h_1 += x_0
h_1 -= x_1
                         # zero source response; original h restored
```

At each cut the complete prefix matrix on (x,h) is
`[[I,0],[M_i,I]]`. Every gate is invertible, and the final source response
is zero. Thus the complete word is the identity on arbitrary inputs over
D, Q or any commutative ring. This proves restoration algebraically;
the bounded dirty-input tests below are corroboration. The fourteen ADDs
are the count of this listed construction, with no optimality claim.

These are source-response matrices of a synthetic scalar trajectory.
They are not asserted to be the eligible prefix/suffix module pairing
matrices of an actual P104 helper split. Native charts, owned delivery,
dirt cancellation and complete paid/target accounting are additional
obligations.

## Evidence and reproduction

From the repository root, run:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/common-reader-cut-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/common-reader-cut-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/common-reader-cut-obstruction/verify.py
```

Any CPython 3.12 interpreter can replace the local interpreter path.
There are no third-party dependencies or scientific external inputs.
Each direct run must print `PASS_COMMON_READER_CUT_OBSTRUCTION`; the
registered launcher must also print `PASS_REGISTERED_RESEARCH_PACKAGE`.

The exact checker enumerates:

- All fourteen nonempty proper subfamilies and their twenty-eight
  reader/source normalizations, plus the four individual-cut witnesses.
- All eighty-one residue reader/source pairs, with a failing cut chosen
  for each of the nine readers, and 198 dyadic denominator controls.
- Five complete symbolic four-by-four prefixes, including the dirty
  identity endpoint, and 625 integer incoming states in both directions,
  totaling 17,500 scalar updates.
- Four rational normalizations and the single non-dyadic column.
- Thirty-seven controls: twenty-eight one-gate deletion/sign mutations,
  five missing/duplicated-cut cover failures, two invalid reader families,
  an odd-denominator rejection and a normalization sign control.

The verifier uses explicit exceptions for acceptance checks, including in
optimized Python. An optional `--receipt /absolute/scratch/receipt.json`
writes a generated receipt containing these results, control names,
interpreter version and SHA256 hashes of all five package files. It is
not a proof-kernel receipt. Normal execution writes no files.

Implementation inspection follows Power of Ten with Python deviations:
managed-runtime and Fraction allocations are unavoidable, and are bounded
by fixed fixture domains, at most a four-by-four live symbolic matrix,
625 streamed inputs and thirty-seven control labels. No recursive code
or unbounded search is used. Short negative-control callbacks have only
the explicit checker targets in `check_controls`. Warning-strict normal
and optimized execution supply the available runtime diagnostics; no
repository-wide analyzer configuration is changed.

## Source, credit and limits

Base: canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority
revision 8. The selected record resolves to conditional kappa .003125804;
the source-binding baseline is orientation, not a scientific replay.

Ali Romman's [PR5615](https://github.com/CrocSwap/integer-mult-bounds/pull/5615)
supplies the single-cut dyadic unit-pairing background, with PR5602/5611/5599,
Nick Petalas's PR5115 and their retained helper/native/controller/compiler
lineage. Its proof is pinned as provenance in SOURCES.json; no predecessor
verifier or numerical result is rerun. The projective-line covering argument
is elementary classical linear algebra. The new contribution is this
deletion-minimal temporal source-response counterexample, its written
dyadic obstruction, proper-subfamily witnesses and reversible realization.

The target was posed independently at the temporal-compatibility bottleneck.
It does not generalize the static tensor-capacity contract or reuse an
open question from that package. Parallel activation at one common cut,
including concurrent work on higher-order pooling, has a different
quantifier and object.

Live handoffs and active Discussions, open PRs, merged-PR searches and
canonical-main README searches were inspected before claiming this target.
The cached overlap report covered 338 open PRs and 5,959 Discussion records;
its sparse local pass covered 91 of 8,625 notes. Separate Git searches read
the main-tree README inventory for the distinctive reader/cover terms.
These are bounded overlap checks, not a proof of novelty or coverage of
unpublished work.

No actual selected-word trajectory, native Gaussian job, free dirty read,
productive target, physical rebasing tariff, supplier admission or complete
multiplication theorem is supplied. The selected frontier and all five
framework assumptions remain unchanged. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

The structured questions are also in TASK.json.

1. Does a nominated physical helper trajectory have a fixed-reader residue
   obstruction? First derive its source-response matrices in a fixed
   physical basis. Actual native/helper eligibility and a consumer contract
   are missing here; without them this synthetic example is not a supplier
   exclusion.
2. What is the least fully charged reader-rebasing cost for this trajectory
   under a specified physical alphabet? First specify entrance, exit and
   restoration, then price one explicit two-reader schedule. Changing the
   reader escapes the theorem, and no physical tariff has been assigned.
