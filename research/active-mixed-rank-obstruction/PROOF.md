# A mixed-rank obstruction for immutable mode delivery

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Contract and result

Use the exact F9-SOURCE-DAG-ALL8 backward word retained by PR5720.
Omit its unimplemented physical_add tail. Keep its native word, scalar
program and public boundaries. The source has 112 X fields, 112 Y fields,
408 independent helpers and nine owned fields. Its mode matrix R has eight
rows and satisfies RR^T=56I.

Each channel holds one fixed scalar combination of the original eight mode
arrays. It pays a canonical ground-to-chart transport of Gaussian rank r.
It can scatter any rational multiples of that payload at any number of
chronological contacts in that chart. It cannot change chart or recompute
its payload from changed data. Different channels can cancel their noise.
Gathering, storage, scalar scatter and all helper restoration are granted.
Y restoration is required. These grants enlarge the feasible class.

For every mixture of ranks 1 through 7, the sum of the paid ranks is at
least 65. There is no bound on the number of channels. Stronger certificates
give rank mass at least 90 for ranks at most 5, and at least 77 for ranks
at most 6. These are lower bounds, not claims of sharp minimum rank mass.

For H_r=r^q H_1, 0<q<=1, a rank-at-most-seven completion costs more than
8H_8. Thus it cannot replace the eight removed centers at a saving.
Rank-eight/rank-nine mixtures, moving charts and changed feedback remain
outside this exclusion. PR5745 supplies a legal eight-H8 attainment and
its separate clean-channel and at-most-eight-channel results.

## A necessary output quotient

Write C=I-R^T R/4. The retained scalar endpoint is X-CY, Y, H.
For a perturbation define Z=deltaX+C deltaY. The required correction has
column space U=im(R^T), of dimension eight. If Y is restored, its Z output
is exactly its required X output. Initial ground-Y preconditioning has
zero Z response. Discarding all helper coordinates can only help a repair.

Let v_(t,d) be the Z endpoint response to a scalar impulse at field d at
cut t. A channel in frame f has response in

    S_f = span{v_(t,d) : field d has frame f at cut t}.

This includes all temporal reuse. The same payload coefficient row b
multiplies the entire response vector v. A completed correction therefore
has form sum_j v_j b_j^T, with v_j in S_(f_j), and has column space U.
The rank bounds below permit arbitrary rational v_j and b_j. They do not
require the individual channels to be clean.

The checker starts the backward adjoint with columns I on X, C on Y and
zero on all other outputs. For ADD d+=a s, the source column gains a times
the destination column. For COPY d=s, the source gains the destination and
the destination becomes zero. SCALE multiplies its column; CLEAR sets it
to zero. Every native chart transition changes the available chart. The
retained common-fixed-vector specialization makes the normalized native
scalar action the identity. This is the credited necessary quotient from
PR5755, not a new all-address native theorem.

Capture a column at the final boundary and after each change to that
column or its chart during backward replay. Between such boundaries the
column and chart are constant. This exhausts the possible impulse
responses. The complete census has 22,585 events, 641 roles, 1,002 available
charts, 998 nonzero response spaces and 8,298 distinct chart/response pairs.
The complete initial adjoint is I on X and zero elsewhere. This checks the
source normalization used by Z. All 115 rank-one supports agree with the
separate forward census retained from PR5755.

## Quotient-rank inequalities

Choose any collection A of actual frame IDs. Let W be the sum of their
response spaces, and let pi be the quotient map by W. Put

    d_A = rank(pi R^T),
    E_A = {f : pi S_f is nonzero}.

If n_f channels use frame f, every successful delivery satisfies

    sum_(f in E_A) n_f >= d_A.

Indeed, apply pi to the complete matrix sum. A term outside E_A is zero.
Every other channel has matrix rank at most one, irrespective of its
coefficients and of cancellation with other terms. Rank subadditivity
proves the inequality. The full rational span is used for W; no coefficient
search or numerical rank threshold is part of this proof.

There are also coordinate inequalities. Every row of R^T is nonzero.
For each output coordinate i, at least one used frame must have a response
with nonzero coordinate i. Thus sum_(f whose support contains i) n_f>=1.

Give nonnegative rational weights to these inequalities. For each allowed
frame f, require the sum of weights on inequalities containing f to be at
most r_f. Then their weighted right sides give a lower bound on
sum_f r_f n_f. The checker rebuilds every S_f, W, d_A and E_A. It checks
every frame load with exact fractions. It does not call an LP solver.

The retained lower bounds are:

| Maximum rank | Nonzero charts | Quotient cuts | Exact dual lower bound | Integer consequence |
|---|---:|---:|---:|---:|
| 5 | 561 | 130 | 358138597/4000000 | at least 90 |
| 6 | 707 | 65 | 7637849/100000 | at least 77 |
| 7 | 875 | 45 | 6497157737/100000000 | at least 65 |

The integer step uses that each paid Gaussian rank and each channel count
is an integer. Zero-response channels cannot improve the correction.
Ground channels have zero Z response and do not enter these bounds.

## Every concave power tariff

For 1<=r<=s and 0<q<=1, r^q>=r s^(q-1). If the rank mass is at least M,
then the channel price is at least M s^(q-1) H_1. Its ratio to 8H_8 is

    (M/64) (8/s)^(1-q).

For s=7 and M=65 this is at least 65/64>1 throughout the stated interval.
This is a symbolic comparison for all real q in that interval. It is not
a sampled power check. Every omitted physical cost is nonnegative, so
adding it cannot reverse the exclusion.

## Why a support cover does not suffice

The exact support-cover optima at maximum ranks 1 through 6 are
101, 100, 79, 62, 223/4 and 467/9. Each value has a rational feasible
cover and a matching rational dual. PR5755 already supplies the rank-one
value and retains that credit. The new rank-two/rank-three bounds alone
would exclude their mixtures. They do not settle ranks four and higher.

COVER-LIMIT.json gives an integral rank-four cover of cost 62 on 17 charts.
It covers all 112 required coordinates. Even if each selected chart is
allowed to supply its entire response space for that one charge, five of
the eight target directions are still missing. The exact quotient-rank
cuts detect this failure. Coordinate coverage is not mode delivery.

## Scope and next boundary

This is a finite source-bound obstruction for the stated immutable-channel
contract. It uses the original normalized scalar quotient and grants more
helper cleanup than PR5745. It proves neither a native lower bound for
changed words nor a general lower bound for active feedback. It changes no
supplier, compiler, stock, precision/tape, analytic or outer assumption.

A better fixed-word delivery must use at least one rank-eight or rank-nine
channel together with additional noisy channels. The registered census
includes those frames, but the rank-at-most-seven dual does not price them.
The bounded all-rank search did not resolve that case. Its failure to find
a certificate is not an impossibility result or evidence of a caller.
