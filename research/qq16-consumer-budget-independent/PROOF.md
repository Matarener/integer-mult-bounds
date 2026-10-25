# A caller-bound audit of the QQ16 consumer budget

Chris R / Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
This is an ordinary scoped proof and executable rational certificate, not
human review, proof-kernel verification or supplier admission.

## 1. Audited claim and independent source binding

The audited PR3908 head is
`0d8880e38ed7c88d70eec6a48e5aa829d0fb22f3`, by 1337isnot1337.
It checks the consumer-budget branch of dcharb78's PR3181, not its
dynamic-range, adjoint or grid theorems. The canonical baseline is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.

The original seven-file package is retained byte-for-byte in
`vendor/PR3908.tar.gz`, with per-file Git blob/SHA256 identities in
PREDECESSORS.json. Its original attribution and limitations are retained.
The regression suite authenticates and replays that exact executable in a
temporary source export. The independent calculation imports neither that
executable nor `ceiling.py`.

Unlike a check of reported profile dictionaries alone, the new checker
expands the literal `programs.F_0` and `programs.B_1_2` in the pinned
`research/joint-query/certificate.json.gz`. `retained_core` expands the named
core word; `cover_sweep` and `private_sweep` contribute their ordered bodies.
Each instruction is counted once per full-cover invocation, not multiplied
by the number of cover owners. This matches the per-call native invoice.
`climb` supplies its literal rank; `native_line` supplies its recipe rank.

The resulting event counts are 26,099 and 27,019. Their positive child
profiles are:

| Program | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 | Rank mass |
|---|---:|---:|---:|---:|---:|---:|
| F0 | 2,420 | 418 | 432 | 142 | 82 | 5,530 |
| B_1_2 | 2,436 | 418 | 432 | 142 | 82 | 5,546 |
| Pair average | 2,428 | 418 | 432 | 142 | 82 | 5,538 |

The same independent census checks all 37 native cases: each of the nine F
cases has the F0 profile and each of the 28 B cases has the B_1_2 profile.
This is a count check, not 37 complete operator-correctness replays.

They agree with CONSERVED-QQ16.json, whose payload hash also binds the exact
decompressed certificate. Independently counting the literal #2707 WORD.json
gives 3,823 instructions, including 336 signed rank-one lines and no stage
children. The source proof lowers each signed line using one positive
rank-one child and explicit monomial wrappers. Its functional equivalence
and physical realization are inherited, not re-proved by this census.

The per-call profile with this decoder is therefore
`{1:2596,2:418,3:432,4:142,5:82}`, of mass 5,706. PR3181 additionally reports
eight rank-eight children per call. The main obstruction below drops all of
them, so their origin or necessity is not a premise of that obstruction.
The tables explicitly labelled as retaining rank eight condition on that
additional reported profile component.

## 2. Applicability to the audited first F0 caller

The first positive child in the same literal F0 expansion is zero-based
event 9894:

```text
["climb","A",546,0,4,1]
```

Event 9895 is `L546 -= L561` in frame 4. The canonical JSON hash of the
preceding 9,894 events is
`15115954461f2cb93e2266822d82bfac1ab8de7d460ff78fcf594d21c61d2b53`,
exactly the prefix audited in PR3932, head
`12c324c576821f78070627c5eeb684d03704e20e`.
Thus our caller is inside the F0 program counted here. It is not a new
producer profile to which an unrelated histogram has been assigned.

The implication remains conditional: if this F0 and B_1_2 are used with the
unchanged #2707 decoder and their listed paid recursive ranks, and the
centre-64 coverage/halving law is retained, the budget fails at the selected
target. Correct encoding or a faster implementation of a scalar/axis
operation does not by itself delete those recursive charges.

Conversely, PR3884's six-tape operation is a local bit-tape implementation,
and PR3932 is an arithmetic caller audit. Neither supplies the complete
recursive invoice. A proof that direct implementation actually *replaces*
a listed recursive tariff, with all-depth costs and the complete consumer
charged, would change this model and must be assessed separately. This
obstruction does not prohibit that possibility or every physical caller.

Changing only F/B frequencies cannot fix the screen if the decoder charge
remains 168 rank-one children per call: the most favorable all-F mixture,
still waiving rank eight, has moment in
`[1.000090397821,1.000090398426]`. All B substitutions increase it.
This does not establish the actual decoder frequency in a new global
schedule. Different reuse/frequencies must be proved and priced; the
pair-level audit is not an admission of an outer schedule.

## 3. The conditional moment lower bound

Fix `m=73`, `w=896/9`, `R=51`, one unpaid coordinate per family and centre
charge `c`. The inherited coverage law fixes total paid rank mass

```text
T(c) = 72w + c.
```

At c=64 this is 7,232. For local profile n_r, let L=sum r*n_r and
I=T(c)-L. The outer halving guard `2R^2<m^2` permits R=51 and excludes 52.
For nonnegative a,

```text
b_a(r) = (r/73)^(1-a)
b_a(r)/r = 73^(a-1) r^(-a)
```

is non-increasing in r. Consequently any remaining idle histogram with
ranks at most 51 and mass I has cost at least `(I/51)b_a(51)`, even allowing
fractional child counts. A necessary budget test is the favorable relaxation

```text
G(n,c,a) = [sum n_r b_a(r) + (I/51)b_a(51)] / w < 1.
```

Moving any paid rank-eight child mass to rank-51 idle mass decreases this
relaxation. Omitting all eight such children is therefore favorable, not an
extra charge. At the selected

```text
kappa = 836330098538459/500000000000000000
a = kappa/(1-kappa) = 836330098538459/499163669901461541
```

the decoder-inclusive minimal profile has L=5,706 and I=1,526.
The independent enclosure is

```text
1.000097677678 <= G <= 1.000097678284.
```

In particular G>100009/100000. Every admissible idle packing in this fixed
model has moment above one before additional physical costs. Since the
moment is increasing in a, this model cannot support the selected saving
or a larger one. No claim about an exact cap root is needed.

## 4. Independent exact interval construction

PR3908 uses a positive atanh/log expansion and one-sided exponential sums.
This checker instead encloses logarithms by integration. On [1,y],
1<=y<=2, the function f(t)=1/t is convex. For a uniform partition into
1,024 panels, the composite midpoint sum is a lower bound for its integral
and the composite trapezoid sum is an upper bound. Every evaluation and
sum is rational. Reduce x>=1 by powers of two and use
`ln(x)=k*ln(2)+ln(x/2^k)`; add the corresponding enclosures.

For 0<=l<=u<=1/2, the degree-six exponential polynomial at l is a lower
bound. At u, the first omitted term is t7=u^7/7!. All later term ratios
are at most u/8, so

```text
exp(u) <= sum_{j=0}^6 u^j/j! + t7/(1-u/8).
```

All used a*ln(73/r) intervals lie in this domain; the code checks it.
Every interval is rounded outward to the dyadic grid 2^-80. Positive
coefficients, mass and division by w preserve enclosure. The decimal
endpoints in RESULT.json are rational outward bounds at 10^-12, not
floating-point calculations. Full JSON equality checks every reported
field and distinguishes booleans from integers.

The retained PR3908 replay reproduces its output lower bound
1.000097677879937. Its centre-free lower bound being below one is only a
scope control, not evidence of a feasible supplier. Our new upper bounds
below one certify passing *relaxations*, also not supplier admission.

## 5. Exact decoder and centre tradeoffs

Keep the producer average fixed and let d be the total number of additional
rank-one decoder children across the two-call pair. Per-call decoder cost
is d/2. Since each added rank-one child displaces one unit of rank-51 idle
mass, G increases linearly in d with positive coefficient

```text
[b_a(1)-b_a(51)/51] / (2w).
```

This allows exact integer thresholds without a search for a root:

| Centre charge per call | Eight rank-eight children | Last integer d passing relaxation | First d excluded |
|---|---|---:|---:|
| 64 | Dropped favorably | 121 | 122 |
| 64 | Retained | 61 | 62 |
| 63 (hypothetical changed law) | Retained | 363 | 364 |

Odd d is permitted as a fractional per-call average; an even, equal split
would restrict the passing ceilings to 120, 60 and 362. This generalization
does not affect PR3908's actual even d=336.

Thus a decoder-only replacement under centre-64 must remove at least 215
of 336 calls even when all rank-eight work is waived, or at least 275 with
that work retained. Merely removing two 112-call groups leaves d=112 and
still fails the retained-rank-eight test. These are budget requirements,
not decoder lower bounds or constructions.

For the unchanged d=336 with rank eight retained, a hypothetical c=63 gives

```text
0.999987387153 <= G <= 0.999987387763.
```

Its available additional normalized moment is between 0.000012612237 and
0.000012612847. Any complete replacement must fit strictly inside its
actual remaining allowance. In the very special case where the only
additional work is rank-one local children displacing idle mass, at most
27 additional children per pair pass this relaxation; 28 are excluded.
This is not a conversion rate for tape actions or physical overhead.

## 6. Research decision and limits

Pause expansion of the unchanged F0/B_1_2 + #2707 centre-64 recipe **as a
route to the selected target**. Its optimistic bound already fails.
Retain the Gaussian/caller results as useful local interface contributions.
Do not infer a global QQ16 or multiplication impossibility statement.

The next budget-admissible research question is a *changed consumer
endpoint or native operator-specific identity*: can one identify real
eliminated centre work, corresponding to at least one average mass unit
per call in the aggregate coverage ledger, while retaining the required
final output and avoiding repayment beyond the allowance above?
One unit per call means two over this pair; a smaller saving can be
assessed by the same affine c-dependence. No such identity is supplied.

The first test must specify the actual downstream F17-native demand map,
the producer output rows it reads, chronological owner/frame interval,
arbitrary dirty state and return/restoration requirements. Compose that
map with the literal decoder before proposing cancellation. A final-output
quotient or identity specific to the fixed native operators is a declared
changed premise; relabelling selected independent demands or storing the
same first transcript is not one.

Relevant adjacent restrictions are PR2391's native first-transcript
counterexample, PR2461's owner-local repair floor, PR3120's selected
copied-demand rank floor and pending PR3873's uniform scalar-oracle and
selected coverage audits. We inspected their stated scopes, not re-proved
those theorems here; none is silently asserted for a new QQ16 endpoint.
Any proposed escape must name its difference from those contracts.

If no named consumer supplies the saving, stop at this handoff. If the
changed contract passes its complete budget, the next implementation slice
is the already identified L546 child-plus-ADD with actual tape intervals,
entry grid/range, monomials, movement/address/control and eventual return
charged. Local bit counts cannot be inserted into this recursive moment
without a justified transfer. Unknown costs remain unknown.

The complete native/bridge algebra, decoder correctness, global coverage
realization, huge all-depth payload execution, physical hosting/routing,
precision/restoration admission, F17 consumer and selected full cold replay
remain inherited or unrun. No frontier record is changed.
