# Optimistic refinement budget

Let `f_C(r)=r^(1-C)` for positive integer rank r and `0 <= C <= 17/5000`.
Fix all paid and target terms except n original H9 targets. A permitted
refinement replaces each H9 by independently productive targets with positive
integer ranks summing to nine. It must surrender the original target. Arbitrary
successive refinements flatten to such a partition; no particular geometry,
cut order, basis or scalar circuit is imposed. This is a deliberately favorable
relaxation of the physical construction.

**Maximum credit.** For each integer `r >= 1`, `r^(1-C) <= r`.
Consequently a partition `(r_1,...,r_k)` of nine has target moment at most
nine, attained by nine rank-one parts. For `0<C<1`, any part greater than one
makes the inequality strict. For n original targets the maximal extra credit is

`G_n(C) = n (9 - 9^(1-C))`.

This function is increasing in C, since its derivative is
`n log(9) 9^(1-C) > 0`. Thus its value at `17/5000` bounds the whole closed
interval. A newly charged positive-integer-rank call has cost at least one
because `1-C > 0`. With every other term fixed, the candidate's change in
paid-minus-target moment is therefore at least `1-G_n(C)`.

The certificate gives

`870799206563/10^12 < G_13(17/5000) < 870799206564/10^12 < 1`.

So the loss is strictly greater than `129200793436/10^12` everywhere in the
interval. It multiplies by eighteen when the edit and new call occur at all
eighteen FULL invocations. No extra target, removed paid job or reduced stock
charge is silently introduced. Granting the remaining helper, basis, access,
normalizer, copy, restoration, frame and compiler operations zero extra cost
only favors the candidate. Their actual nonnegative added costs cannot reverse
this particular raw-moment comparison.

**Sharp source-count control in this relaxation.** Put
`g=9-9^(4983/5000)`. The rational bounds certify `14g<1<15g`.
Hence fifteen is the first n whose maximal credit can exceed one at this
endpoint. This is arithmetic attainability by integral rank partitions, not
attainability by physical independent helper channels.

**Binary comparison.** Strict concavity of `x^(1-C)` for `0<C<1` makes
`a^(1-C)+(9-a)^(1-C)` maximal for integer `a=4 or 5`. At the endpoint write
`b=4^(4983/5000)+5^(4983/5000)-9^(4983/5000)`.
The certificate proves `47b<1<48b`. The finite enumeration independently
compares every two-part partition. These binary and arbitrary-refinement
thresholds apply at the named endpoint, not uniformly at all smaller C.

**Exact numerical method.** For `z=(r-1)/(r+1)`,

`log r = 2 sum_{k>=0} z^(2k+1)/(2k+1)`.

After N=128 terms, the omitted positive tail is at most
`2 z^(2N+1) / ((2N+1)(1-z^2))`. For `x=C log r` in the checked range `0<=x<1`,
the degree-17 Taylor polynomial for `exp(-x)` is a lower bound and the
degree-16 polynomial is an upper bound, by decreasing alternating terms.
Monotonicity in x then gives exact Fraction bounds for `r exp(-C log r)`.
Signed moments choose the correct bound for each sign; output intervals round
outward to a rational grid of denominator `10^12`.

An independent final check raises both rank-nine interval endpoints to the
5000th power and compares their integer numerator/denominator powers to
`9^4983`. This check uses no logarithm or exponential code. It directly
certifies the decisive root enclosure. Proof and finite checks remain distinct:
neither is a formal proof of the full multiplication algorithm.

Prepared by OpenAI Codex for Charan with substantial AI assistance. Apache-2.0.
