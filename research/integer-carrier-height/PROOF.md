# The minimum integer height of the fixed logarithmic guard

New proof produced by Nick Petalas. Apache-2.0.

## Statement and provenance

Fix p=322 and d=1/700000000000. For positive integer H, consider

    (H+1)^p < 2^(d H).                                      (1)

The minimum such H is

    H* = 12040587444441491.

Every integer H>=H* satisfies (1), and every positive integer H<H* fails
it. The separate side condition H>8*1024 holds at H*.

Richard Hoekstra's PR #5787, head
08f0e5899254aa82288a91e70789049dc1f29690, supplies this guard through the
logarithmic majorant in retained/PROOF.md sections 2 and 3. Its fixed-kappa
case in retained/frontier.py has p=322, tested saving .003027288245 and
declared saving .003027288235. Its rule d=(s-k)/7 gives the d above.
It supplies sufficient grid height 12040700000000000 and expressly does
not claim the minimum integer height. Those source statements are premises
for the compiler interpretation, not new results proved in this package.

## Why two adjacent comparisons settle the whole domain

For real x>0 put r(x)=ln(1+x)/x. Differentiation gives

    r'(x) = [x/(1+x) - ln(1+x)]/x^2 < 0.

The strict sign follows directly from

    ln(1+x) = integral_0^x 1/(1+t) dt > x/(1+x).

Taking logarithms in (1) and dividing by H shows that (1) holds exactly
when r(H)<d ln(2)/p. Therefore the passing set is an upper interval.
It suffices to prove strict failure at H*-1 and strict success at H*.
There is no enumeration of the roughly 10^16 preceding heights and no
assumption that a sparse grid contains the first passing integer.

Define D(H)=d H-p log2(H+1). The exact checks prove

    -36/10^15 < D(H*-1) < -35/10^15,
    1354/10^15 < D(H*) < 1355/10^15.

Both brackets lie strictly on the required side of zero. Thus the
monotonicity argument proves the statement for every positive integer H.

## Primary rational logarithm enclosure

For a positive integer n, choose k=floor(log2 n), determined by its binary
length, and a=n/2^k in [1,2). Then

    log2 n = k + ln(a)/ln(2).

For any rational a in [1,2], let z=(a-1)/(a+1), so 0<=z<=1/3. For N=80,

    S_N = 2 sum_{j=0}^{N-1} z^(2j+1)/(2j+1),
    0 <= ln(a)-S_N <= 2 z^(2N+1)/[(2N+1)(1-z^2)].

This follows from the convergent positive odd-power series and the
geometric upper bound on its tail. All terms and endpoints are exact
fractions. Endpoints are rounded outwards to multiples of 2^-220 by
integer floor and ceiling. Since the enclosure of ln(2) is strictly
positive, dividing the numerator's lower bound by the denominator's upper
bound, and conversely for the upper bound, preserves containment. A final
outward rounding preserves it again. Multiplication by p and subtraction
from d H produce the certified margin intervals.

The executable checks compare their signs with exact integer inequalities
(H+1)^(p q) versus 2^H for H=1..64, p=1..4 and q=1..4, where d=1/q.
These 1024 cases include equality and both strict signs. They corroborate
the enclosure implementation; the series argument supplies its proof.

## Separately implemented enclosure

independent.py imports no primary checker or predecessor code. It uses the
alternating series for ln(1+x) with 256 terms. For 0<=x<=1/2 the even
partial sum is a lower bound, and adding x^257/257 is an upper bound.
It computes ln(2)=ln(3/2)+ln(4/3). For normalized a>3/2 it uses
ln(a)=ln(2a/3)+ln(3/2), so every series argument remains in [1,3/2].
It proves the same two strict signs using exact fractions, without sharing
the positive-series tail or dyadic rounding implementation.

## Improvement and limits

The difference from the cited sufficient grid height is exactly
112555558509. This improves the isolated logarithmic guard at fixed p and
d. It is not another evaluation of a paid-moment root or a review of the
predecessor's complete application.

The result does not establish that the complete source compiler can be
instantiated at N=2^H*. In particular the changed finite-template counts,
precision and conjunction application, integer layout and physical
implementation need their own proof at that N. All source assumptions
remain. No global compiler optimum, complete multiplication theorem or
new kappa is claimed.
