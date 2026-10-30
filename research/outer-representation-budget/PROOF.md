# Precision, total stock and the paid outer fallback

Prepared by [zxv](https://github.com/zxv), with substantial OpenAI Codex assistance. Apache-2.0. This is a scoped written proof about an explicitly changed admission contract, with exact arithmetic corroboration. It is not an implemented supplier or a complete multiplication theorem.

## 1. Actual sources and the changed question

The scientific baseline is canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`, selected PR6030 at κ = 0.003125804, priority revision 8. Its `pricing.py` calls the unchanged `ledger` in `research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py`. That function supplies 54 strict and three functional predicates; pricing adds the fourth functional predicate `β(1−atom)>0`, with atom = 1/250. The source pins are in SOURCES.json.

At the selected baseline, U is a completed complex uniform saving and B is the admitted ordinary BIT saving. For the hypothetical changed contract below, U and B are completed saving budgets on the above-cutoff outer call domains; all lower-width work is charged separately. Neither is a raw moment crossing, and an above-cutoff budget is not a newly admitted all-size ordinary supplier. Put

$$M=\min(U,B,1/32),\qquad c=3/32.$$

[Nick Petalas](https://github.com/petalas)'s [PR5984](https://github.com/CrocSwap/integer-mult-bounds/pull/5984) proves the original arithmetic region `OLD < κ < M`. Here OLD is the inherited bookkeeping constant 0.001730970419199163702738, not a mathematical lower limit on multiplication. We credit that result; the new question is what changes when the supplier's representation has a different precision and total-stock envelope, including the fallback's actual cost.

The nine source savings, before the change, are exactly:

| Source row | Saving below outer exponent one |
|---|---|
| main_transform | εq |
| global_coordinate_router | a |
| fused_gaussian | 1−ε+qβ |
| group_bit_router | 1−ε+aβ |
| group_scans | 1−ε+β |
| boundary_algebraic_matrix | c+ξ−ε |
| sparse_union_movement | ξ+1/2−ε |
| polynomial_products | ε |
| microbox_face_corrections | 79−ε−β |

The source definition is `ξ=ε(1+q)−c+layout`. All nine savings must strictly exceed κ. The supplier-ordering checks give `0<q<a<b<min(U,1/32)` and `a<B`. The source membership calculation requires

$$2\epsilon-1-\beta>0.$$ 

This last condition matters once ε cannot approach one.

## 2. A sufficient *interface*, not a constructed supplier

The following is the declared changed contract. It retains the same analytic decomposition, fixed tapes, global complete-field calls, arbitrary/dirty inputs, completed endpoints, restoration, native correctness, finite compiler, and inherited precision/recovery hypotheses. The five selected assumptions are not discharged. Every constant below must be fixed and computable before input length varies.

Let p = Θ(log n), total represented bit volume V = Θ(n), dimension d = Θ(p^ε), and group width g = Θ(p^β), as in the retained outer assembly. Fix rational parameters

$$\rho\ge1,\qquad 0\le\nu<1,\qquad \zeta\ge0,\qquad s=\frac{\zeta}{1-\nu}.$$

1. **Precision.** The prescribed common-grid storage and completed-defect propagation use at most `C d^ρ polylog(d)` guard bits globally, and `C h^ρ polylog(h)` at active width h. They must fit in Θ(p)-bit records with strict power slack: `ρε<1` and `ρβ<1`. A storage bound alone is not a completed-error guarantee.
2. **Total stock.** The logarithmic reserve, measured in complete selectable chunks, is at most `C(log(2h)+h^ν p^ζ (log(2p))^A+1)`. This bounds the product of simultaneous stock requirements, not their maximum. Borrowing, row padding, layout exposure and restoration obey the retained contracts. This envelope includes inherited reserves.
3. **Charged completion.** Above a cutoff `H(p)=ceil(p^t)` with **t>s**, the completed supplier meets its promised U/B runtime, including every internal charge. Below H, the wrapper processes axes individually in `O(V H(p) polylog(p))` time. The enclosing schedule has `O(p^(ε−β) polylog(p))` grouped windows. No other changed fee is omitted. A different fallback or extra per-window cost needs its own ledger.

For h ≥ H and h ≤ p, the stock fraction is bounded by a fixed multiple of

$$\frac{\log(2p)+1}{p^t}+p^{\zeta-t(1-\nu)}(\log(2p))^A=o(1).$$

Thus all fixed reserve fractions are eventually available. At a root group we additionally need `t<β`. The strict `t>s` gap absorbs every fixed logarithm and constant; an exact p^s cutoff is not asserted sufficient.

The source audit explicitly handles a polylogarithmic residual individually when ζ=0. Here that residual may have a positive power of p. Its grouped cost is

$$O\!\left(n\,p^{\epsilon-\beta+t}\operatorname{polylog}p\right).$$

Consequently the **group_scans** saving becomes

$$\boxed{1-\epsilon+\beta-t}.$$

This row conservatively pays both the original scans and the additional grouped fallback. It is a changed accounting contract; the selected source is never edited. A full-width main-layer fallback contributes saving `ε−t`. It needs no further binding row because

$$1-\epsilon+\beta-t<\epsilon-t$$

by the retained membership inequality. The new group row already funds it. This domination prevents an uncharged second residual.

The precise arithmetic model retains every source check, strengthens `group_scans_above_kappa` as displayed, and appends five checks:

$$1-\rho\epsilon>0,\quad 1-\rho\beta>0,\quad \beta(1-\nu)-\zeta>0,\quad t-s>0,\quad\beta-t>0.$$

There are 63 predicates in total. They are *sufficient strict exponent tests under this interface*. Failing a test is an obstruction to this policy, not a lower bound for an algorithm with a tighter envelope, another representation, a faster fallback, or another outer schedule.

## 3. Exact admitted region

**Theorem.** Let U,B>0 and κ be rational, and let the rational envelope domain above hold. There are rational free outer parameters and a rational cutoff t satisfying all 63 predicates if and only if

$$\boxed{\rho(1+s)<2,\qquad
\mathrm{OLD}<\kappa<\min\left(\frac{M}{\rho},\frac1\rho-s\right).}$$

Every inequality is strict. The right endpoint is a supremum and is not attained.

### Necessity

Set R=1/ρ. The guard gives ε<R. From `β>t>s` and membership, `2ε−1>β>s`. Hence `s<2R−1`. From the source ordering and main row, `κ<εq<εM<RM`. Finally the charged group row and membership give

$$\kappa<1-\epsilon+\beta-t<\epsilon-t<R-s.$$

Two exact positive-weight certificates make the obstruction especially easy to check. Denote the five relevant slacks by

$$G=1-\rho\epsilon,\quad A=2\epsilon-1-\beta,\quad
D=\beta-t,\quad E=t-s,\quad F=1-\epsilon+\beta-t-\kappa.$$

Then

$$\frac G\rho+\frac{A+D+E}{2}=R-\frac{1+s}{2},\qquad
\frac G\rho+A+F+E=R-s-\kappa.$$

All coefficients are positive. Either nonpositive right side contradicts strict feasibility. The baseline inequality is inherited directly.

### Sufficiency: one rational construction for the whole region

Assume the boxed conditions. Choose

$$L=\max\left(\kappa/M,\kappa+s,(1+s)/2\right),\qquad
\epsilon=(L+R)/2.$$

Then `1/2<ε<R≤1`. Set

$$q=(\kappa/\epsilon+M)/2,\qquad
a=(2q+M)/3,\qquad b=(q+2M)/3.$$

Thus `κ<εq<q<a<b<M≤1/32`. In particular both suppliers strictly fund the effective savings. Choose

$$\eta=\min\left(\frac{2\epsilon-1-s}{2},\frac{\epsilon-s-\kappa}{2},\frac{1-\epsilon}{2}\right),
\qquad\beta=2\epsilon-1-\eta.$$

All three entries of the minimum are positive. Hence `s<β<2ε−1<ε<1`, and

$$1-\epsilon+\beta-s-\kappa=\epsilon-s-\kappa-\eta>0.$$

Take

$$\delta=\frac14\min\{\beta-s,\ 1-\epsilon+\beta-s-\kappa,\ \epsilon-s-\kappa\},
\qquad t=s+\delta.$$

This gives `s<t<β`, positive stock slack `(1−ν)(β−s)`, positive charged group slack, and positive main residual slack `ε−t−κ`.

For the remaining geometry take

$$h=\min((\epsilon-1/2)/2,1/64),\quad
\mathrm{layout}=c-\epsilon q-h,\quad
r_0=(1-\rho\epsilon)/4,\quad
\mathrm{stop}=(b-a)/(2b).$$

Here `ξ=ε−h`; `layout>3/64`, `1/2<ξ<ε<1`, and `0<stop<1`. The following covers every source family of predicates.

- **Endpoint and leaf order.** `0<q<a<b<M` supplies all supplier gaps. The leaf saving is `(1−stop)b=(a+b)/2>a>q`. Since b>a, the internal exponent is `1−a`. With `λ=1−(q+a)/2`, every λ/internal/leaf gap is strictly positive.
- **Dimension and headers.** `0<β<2ε−1<ε<1` gives the positive group, support-span, key, membership, union-header and tag inequalities. `ε−a>0` because ε>1/2 and a<1/32. Both new precision guards hold because `β<ε<R`.
- **Global and group gauges.** `0<r0≤(1−ε)/4`. Also `3−2ξ−β=4(1−ε)+2h+η>r0`; both group gauge checks and the global gamma checks hold. The positive logarithm-absorption row is r0 itself.
- **Gaussian ordering.** `ε−β=1−ε+η≤3(1−ε)/2`. Thus `1−ε+qβ−εq≥(1−ε)(1−3q/2)>0`. The fused Gaussian saving exceeds the main saving; the group BIT saving is still larger because a>q and β>0.
- **Other outer rows.** The global router saving a exceeds κ. The boundary saving is `c−h≥5/64>κ`; the sparse-union saving is `1/2−h≥31/64>κ`. The polynomial saving ε exceeds κ; the microbox saving `79−ε−β>77` does too. The group scan/fallback row was funded above.
- **Constants and inherited functional predicates.** `2^45−7^16`, 2, 5 and 7/2 remain positive. The halo/microbox bounds follow from ε,β<1. All inherited functional checks are positive: `1−β`, `β(1−3/1000)`, `79−ε−β`, and `β(1−1/250)`. The original semantic `1−ε` guard is retained as well.

This proves all 63 predicates, not merely their minimum or the nine outer rows. Exact source evaluation corroborates this construction on 4,056 parameter points, including points 10^-24 below their supremum. The written argument supplies the universal quantifiers; the finite grid does not.

## 4. Recovery and the meaning of the precision hypothesis

The retained upstream assembly has `Tp=Θ(n)`, radix digits with at most b bits, coefficient bound `q_digit(2^b−1)^2<2^(3b)`, no cyclic wraparound, two source-normalization factors S, and a strict final error below 1/2 before nearest-integer recovery. Its exact carry scan then costs O(n). These algebraic recovery facts do not impose a new supplier-saving conversion such as a/(1+a).

A useful sufficient completed-error contract is

$$|\widetilde c_j-c_j|\le p^J2^{A b+C d^\rho-p}$$

for fixed computable A,C,J, with all producer/consumer defects, both S factors, input scales and restoration accounted for. If an applicable analytic implementation permits `p=K b` for fixed K>A, then `ρε<1` gives `C d^ρ=o(p)` and the displayed bound is eventually below 1/2. Record widths remain O(p). This is the elementary implication that justifies using the guard test; it does **not** construct implementations meeting that error contract or prove that a changed analytic implementation admits the chosen K. Those are explicit admission obligations.

At error exactly 1/2 the observation 1/2 is consistent with coefficients zero and one, so strict recovery slack is necessary for unrestricted nearest-integer decoding. The verifier checks this calibration only; it does not replay the numerical Gaussian path. In particular a narrow local grid statement, a small endpoint defect or a favorable final exact operator does not alone imply the completed-error contract.

## 5. Target-scale consequences and a falsified screen

For some κ>.01 to be admissible under this policy, the exact necessary and sufficient conditions, apart from the harmless inherited OLD threshold, are

$$M>.01\rho,\qquad s<1/\rho-.01,\qquad \rho(1+s)<2.$$

- **Quadratic prescribed guards fail in this geometry.** If ρ≥2, even s=0 cannot pass. The contradiction already comes from precision, positive group width and membership. A tighter actual guard, cheaper membership representation or another outer schedule can escape it; an O(d²) upper bound alone is not a lower bound on the supplier's necessary precision.
- **Linear precision with no power of p in stock recovers PR5984.** For ρ=1, ζ=0, ν<1, the region reduces exactly to `OLD<κ<M`. The selected admitted B=.0034 still excludes .01. No hypothetical precision change makes the selected suppliers sufficient.
- **Superlinear precision need not be fatal.** Hypothetical completed suppliers U=B=.02, ρ=3/2, ν=1/2, ζ=.05 have s=.1 and permit κ=.011. RESULT.json provides all rational parameters and all nine savings. They do not supply the suppliers.
- **Largest-call stock fit can falsely admit κ=.011.** Let U=B=.02, ρ=1, ν=1/2 and ζ=.4975, so s=.995. PR5984's original slack family at κ=.011 passes all original 58 checks. It also passes both new precision guards and stock fit at the largest group. Taking t=.995001 passes both cutoff checks. Nevertheless the paid fallback saving is only `16993/7000000` (about .00242757), so the new group row rejects. The exact supremum for *any* parameters under this policy is .005. The counterexample falsifies the free-fallback screen; it alleges no error in the source ζ=0 ledger or selected stock.

The prescribed envelope and fallback can be conservative. The obstruction says exactly which contract has to change: reduce the actual guard exponent, reduce total stock or its precision dependence, supply a faster charged small-width routine, or replace the membership/group schedule. It is not a universal κ ceiling.
