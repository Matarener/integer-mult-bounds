# A production Gaussian inverse bound that retains the concentration factor

Produced by Nick Petalas. Apache-2.0.

This is a scoped written mathematical proof. Its universal statements do not
follow from the finite corroboration and have no independent human or formal
proof-kernel review claimed here.

## Statement and cited premises

Use the unchanged parameters and original-coordinate rounded matrix H of Jose
Manuel's [PR #3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851).
The production guards include positive integers p,u,d with

    p >= 101,  u >= ceil(log2(8p)),  u*d <= p,
    1/(4d) < theta = t/s - 1 < 1/(2d-1),  1 < t/s < 2,
    P = 32768p,  2w < s.

Let N_w be the ideal retained-band matrix defined in JoyboyBrian's
[PR #6099](https://github.com/CrocSwap/integer-mult-bounds/pull/6099),
PROOF.md at `38ce77a4925c18eb66f94634b1b11a1242af8a87`. Its diagonal is
one, its retained entry at signed offset h is

    exp(-pi*u*((rho*h+beta_i)^2-beta_j^2)),
    rho=t/s, q_i=floor(rho*i+1/2), beta_i=rho*i-q_i,

and other off-diagonal entries vanish. The retained signed offsets obey
|h|<=w and j congruent to i+h modulo s. The beta sequence is periodic,
including ties where beta=-1/2. The physical cut remains a cell boundary.

We cite two mathematical premises, without re-verifying them:

1. The bilateral row majorant of PR1673,
   `research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md` section 1,
   with a=pi*u>=1, bounds the sum of every nonzero-offset coefficient by

       S = exp(-2*pi*u*theta) + 5 exp(-2*pi*u).

   It includes nonzero periodic diagonal aliases. The off-sum of N_w is a
   subset of that nonnegative bilateral sum. Deleting aliases, discarding
   tails and restricting to a principal window cannot increase it.

2. PR6099's retained-band theorem, conditional on its cited scalar enclosure
   theorem in PR6085, gives

       ||H-N_w||_infinity < E = p*2^(16p+4)*2^(-32768p).

   This theorem concerns the actual within-cell rational ratios and across-cell
   coefficients. We use it as an input, not as an audit target. No Git objects
   or executable code from either pending PR are imported by our verifier.

Then, for H and every nonempty principal restriction H_J,

    gap(N_w) > u^2/(p+u^2),
    gap(H_J) > u^2/(2(p+u^2)),
    ||H_J^-1||_infinity < 2 + 2p/u^2.

Here gap means the minimum diagonal absolute value minus off-diagonal absolute
row sum. In particular the source's strict row-dominance test succeeds under
these cited premises. No production page is materialized by this argument.

## The new parameter step

Put v=u^2. Since d>=1 and u*d<=p, we have 1<=u<=p and 1<=v<=p^2.
Crucially, the guards imply

    u*theta > u/(4d) >= u^2/(4p).

Use pi>3, e>2, and 2^u>=8p. The two terms of the cited majorant satisfy

    exp(-2*pi*u*theta) < exp(-3v/(2p)) <= 2p/(2p+3v),
    5 exp(-2*pi*u) < 5*2^(-6u) <= 5/(8p)^6 = T.

The first non-strict inequality is exp(x)>=1+x. Therefore

    gap(N_w) >= 1-S > 3v/(2p+3v) - T.

The exact algebraic reserve above our proposed gap is

    3v/(2p+3v) - v/(p+v) = p*v/((2p+3v)(p+v)).

Since v<=p^2 and v>=1, this is at least

    1/[p(3p+2)(p+1)] >= 1/(10p^3).

Meanwhile T<1/(10p^3): clearing positive denominators reduces this to
50<8^6*p^3, valid for every p>=1. Thus the ideal gap is strictly greater
than v/(p+v). This retains the squared concentration factor that the
historical 1/(8p) estimate discards.

## Paying rounding and bounding the inverse

Write E=16p*2^(-32752p). For integers p>=1, induction gives both p<=2^p
and p+1<=2^p. Consequently

    32p(p+1) <= 2^(2p+5) <= 2^(7p) < 2^(32752p),

so E<1/[2(p+1)]<=v/[2(p+v)]. Subtract this row perturbation from the
ideal gap. H and every principal restriction have gap strictly greater
than v/[2(p+v)]. Their diagonals are exactly one, by the unchanged
Axis.matrix_entry convention. Hence ||I-H_J||_infinity<1-v/[2(p+v)].
The convergent Neumann series proves the asserted inverse bound.

The published production metadata example has p=16384 and u=32. The new
inverse bound is exactly 34, versus the old bound 8p=131072. These are
analytic upper bounds; neither is a measurement of the actual inverse norm.

## Boundaries and necessity of a hypothesis

The result is conditional on the two cited estimates and their retained scalar
arithmetic contract. It settles the row-gap part of PR6099's open question
with a stronger bound. Its infinite-periodized comparison and tail estimate
remain open in that question. Column or spectral norms, LU growth, physical
setup and tape costs, full production pages, tensor/CRT assembly, the selected
framework assumptions and a new kappa are not established here.

The similarity guard cannot simply be removed. Set p=16384, u=32,
s=10^10, t=s+1 and i=s/2. Then beta_i=-1/2 and the +1 coefficient has
exponent 2*pi*u/s. A retained band containing that coefficient has gap at
most 1-exp(-2*pi*u/s)<8u/s<1/34. Thus the new row-gap lower bound is false
in this relaxed parameter family. This does not refute the inverse upper
bound separately. The family satisfies the concentration inequality but
cannot satisfy both u*d<=p and theta>1/(4d). This counterexample is local
to that removed-hypothesis model, not a claim about admitted production plans.
