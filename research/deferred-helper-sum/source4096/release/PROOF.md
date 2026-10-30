# One shared release, two independent dirty-helper channels

This finite check uses PR4076 at
`9744f9df268590295a9872b1952c695a678192b9`, both `NEW-base` and `NEW-extra`
providers. All eight required source files have byte hashes embedded in
`check.py`; all four OLD/NEW word hashes are checked after decompression.
Indices below are zero based. `RESULT.json` gives the exact provider hashes,
rows, literal edits and invoices.

The result is a literal sharing construction with **zero change to the recursive
frame profile or helper widths**, followed by a scoped obstruction to replacing
all four releases by one persistent scalar channel. It establishes no larger
kappa, new supplier, owner fill or all-size theorem.

## Assumptions and exact arithmetic

Every one of the 632 live register inputs and 91 private buffer inputs is
independent and arbitrarily dirty. Coefficients are rational; all gates here are
dyadic. Each of the 72 native operators is an independent invertible generator
of a free group. No two distinct generators commute. An expression is an exact
finite rational linear combination of `(input, reduced operator word)` terms.
The source's inverse-cleanup exclusions, restored-helper buffer renaming and
borrow-word frame contract are retained.

`check.py` independently interprets this operator algebra, including the full
forward map, inverse-transpose map, boundary map, and reverse-inverse identity.
For the paid frame invoice it calls the exact pinned `audit_core.py`, with the
Lagrangian binary action check enabled. This reuses the credited frame accountant;
it is not an independent native Clifford-phase proof.

## The actual shared word and its complete local change

The source NEW B list at indices 948, 949, 950 contains, in order,

```
610 -= 608
608 -= 410
610 -= 609
```

Each gate uses `F = span(144,75,42,7)`, of dimension four. Native warps 33, 34,
35 and 36 immediately precede B948 and remain there, in the same order with
the same lenders and matrices. There is no warp between the three gates.
The changed B list replaces precisely that slice by

```
608 += 609
610 -= 608
608 -= 609
608 -= 410
```

at frame `F`. Every later B scalar is retained in order. Every native warp whose
old B position is at least 951 receives position `old+1`; no native operation
is added, removed or changed. All other word fields stay fixed except literal
cleanup, which is regenerated from the entire changed non-target word.

For arbitrary current values `(x,y,z,w)` in `(608,609,610,410)`, both local
words map them to `(x-w,y,z-x-y,w)`. This uses no cleanliness or commutation
assumption. The corresponding local inverse, in chronological cleanup order,
is

```
608 += 410
608 += 609
610 += 608
608 -= 609
```

and the checker rebuilds the complete reverse-inverse cleanup rather than
inserting this block into a stale tail. The complete cleanup length is
`5228 -> 5229` in each provider. All 723 input columns of the complete boundary,
forward and inverse-transpose maps agree with the source word.

Before the shared block, helpers 608 and 609 have frame
`span(97,45) = span(76,45)` of dimension two; 610 has its inherited frame.
The first new gate raises both pair cells to `F`. The original word raised 608
at B948 and 609 at B950. The positive frame changes for every register remain
the same ordered sequence; only the local time of 609's existing raise changes.
The independently recalculated local invoice is unchanged:

```
2488 H1 + 714 H2 + 223 H3 + 102 H4 + 20 H5 + 8 H8.
```

The inventory is also unchanged:
`5:28, 6:18, 7:56, 8:93, 9:213`; helpers 608 and 609 each retain width seven.
No register, private buffer, native warp, wrapper, entrance frame, terminal
frame or recursive frame event is added. The literal changes add one forward
scalar addition and one inverse-cleanup scalar addition. Two writes into 610
become one write into 610, but the two reversible mix/unmix additions consume
that apparent saving. The complete scalar-addition delta is therefore **+2**.

Equality of local profiles and endpoint inputs is necessary for retaining an
outer bill. Conditional on an unchanged valid owner/source-window contract,
the recursive moment has delta zero at every exponent. This check does not
replay the 1,321,920-role owner witness, prove source-window reuse, or admit the
changed word to the physical native/outer supplier.

## Correct target-dirt compensation and the one-channel obstruction

The four releases are exactly NEW B388, B410, B948 and B950:

```
121 += 609/2
137 -= 608/2
610 -= 608
610 -= 609
```

The later B1498 read `137 -= 608/2` is a distinct operation and is retained.
Matching releases only by register pair and coefficient would wrongly remove
that later read. The checker pins literal sites and their full opcode preimages.

Omit exactly these four releases using identity padding at their original
frames and regenerate the complete cleanup. Relative to the correct endpoint,
the resulting entire target-dirt map is

```
R608 = -(e121 + e137)/2,
R609 = -(e114 + e173)/2.
```

All their free-group words are empty; there are no additional defects on other
live or dirty-buffer input columns. Consequently the target correction columns
are `C608=(e121+e137)/2` and `C609=(e114+e173)/2`. The minor in rows 121 and 114
and columns 608 and 609 is exactly `1/4`.

In particular, all four release demands cannot factor as
`C = L [P Q]` through one linear channel `s=P x608+Q x609`, with subsequent
linear readout and no additional retained information. This remains true even
if `L,P,Q` have finite free-group-polynomial coefficients: the augmentation
homomorphism sending every native generator to 1 would produce a rational
rank-at-most-one factorization of a matrix with the displayed nonzero minor.
This is a fixed-interface channel obstruction. It does not cover a reused
mutable cell carrying different information at successive cuts, nonlinear
encoding, extra source queries, or a changed compensation/terminal contract.

Omitting only the two releases into 610 gives equal residual columns
`-(e114+e121)/2` for each helper. That submechanism does factor through the sum.
The literal word above realizes exactly this sharing and demonstrates why its
scalar read reduction does not change the fully paid recursive profile.

## Current-cut and receiver-aware termination check

The two entries' metadata both say `cut:10535`, but the second entry is applied
to the word *after* the first. They are not the same physical event. The checker
replays all three ordered staged-entry edit records, labels surviving OLD
events, and requires the final opcode sequence to equal the NEW word. It finds:

| Entry | Recorded source cut | OLD physical cut | NEW physical cut | NEW B position | Next gate |
| --- | ---: | ---: | ---: | ---: | --- |
| 608 | 10535 | 10535 | 10523 | 302 | `3 -= 554` |
| 609 after 608 | 10535 | 10539 | 10527 | 306 | `181 += 397` |

The literal final NEW global cut 10535 is B314 before `161 -= 34/2`; it is a
third event. At **each** of these three NEW cuts, assign arbitrary independent
current values to all 723 cells and let `M_c` be the remaining prefix through
the cleanup boundary. Direct suffix interpretation and inversion give the same
pair columns and inverse rows below. Thus this result does not infer an
arbitrary-current-state suffix from an entrance-only calculation.

Let `H={608,609}` and `R={608,609,417,419,421,610}`. At each checked cut,

```
M_c e608 = e608 + e417/2 - e421/2 - e610,
M_c e609 = e609 + e417/2 - e419/2 - e610.
```

The difference therefore leaks into two receivers:

```
M_c(e608-e609) = e608-e609 + (e419-e421)/2.
```

Containing that column support in `R` does not make raw helper directions
recoverable from `R`. The two relevant inverse rows are, exactly,

```
row608(M_c^-1) = 608/2 - 609/2 - 417 - 419 - 421 - 610/2
                + 410/2 - 612 + 2*342 + 2*356,
row609(M_c^-1) = 608/2 + 609/2 + 417 - 419 + 421 + 610/2
                + 410/2 - 612 - 276 - 292.
```

All terms again have empty operator words. Suppose a scalar covector `alpha`
is supported on `R` and `alpha M_c` is supported on `H`. Write
`alpha M_c = b608 e608^T + b609 e609^T`, so
`alpha = b608 row608(M_c^-1) + b609 row609(M_c^-1)`.
Coordinate 342, which is outside `R`, forces `2 b608=0`; coordinate 276 forces
`-b609=0`. Hence `alpha=0`. The source-recovery rank is zero even after adding
the four natural receivers to the pair. In particular there is no such
covector with nonzero pairing against `e608-e609`.

Receiver-aware termination by itself therefore does not remove this
fixed-cone obstruction. A different candidate must admit additional source
consumers or change the cut/observation contract. The displayed raw-pair inverse
already requires factory cells outside `R`; this check does not assert that
adding those cells would be legal or beneficial after pricing their frames,
restoration, owners and recursive children.

## Reproduction, controls and covered domain

```
python3 check.py --source /path/to/source4076 --out result.json
python3 -O check.py --source /path/to/source4076 --out result-optimized.json
```

The eight required inputs are the four `inputs/{OLD,NEW}-{base,extra}.json.gz`
files, `vendor/audit_core.py`, `NOTICE.md`, `PROOF.md`, and
`recipe/ENTRIES.json`. No repository checkout, external package, network,
source manifest, hidden local checker or other runtime source file is read.
All checks use explicit exceptions and remain active under Python `-O`.

For each provider, controls reject: a wrong actual unmix sign with cleanup
regenerated, deletion of an actual inverse-cleanup addition, stale literal
cleanup, omission of the exact target release with cleanup regenerated, and a
collapsed rank-one correction matrix. Forward and inverse-transpose coverage
includes every dirty buffer. The suffix results are finite exact identities on
all current states at the three pinned cuts; the one-channel and receiver-cone
arguments are written algebraic consequences of those finite exact matrices.
There is no formal-kernel proof or independent human review.

The result does not prove native global phases, physical hosting, the owner fill,
precision/tape bounds, all-size source existence, outer admission or a changed
selected frontier. It fires the bounded stop rule for this pair, this common
release, these current cuts and this natural receiver cone.

## Sources and credit

Rohan Arun's PR4076 supplies the three staged entries, their literal words and
owner construction, with Anthropic Claude assistance. Dugongue's PR3945 supplies
the predecessor terminal-width-five words, owner/frame/native lineage and OpenAI
Codex-assisted work. Ross Richardson's PR3605 supplies staged entrance and
literal cleanup machinery. Sagar Thakrar's PR3687 supplies the pinned frame
accountant and credited free-word format, retaining Arham Tahir's audit credit;
the independent sparse interpreter here imports no semantic functions from it.
The complete retained attribution and Apache-2.0 notices are in source
`NOTICE.md` and `audit_core.py`.

The new contribution here is the explicit shared-610 word, its regenerated
cleanup and unchanged frame invoice, the four-site target correction columns,
the exact sequential-cut mapping, and the independent receiver-cone witnesses.
It was derived and checked with substantial OpenAI Codex GPT-6.1 Sol assistance.
Prior shared-kernel and staged-entry mechanisms motivate the question; their
reported savings are not transferred to this changed word.
