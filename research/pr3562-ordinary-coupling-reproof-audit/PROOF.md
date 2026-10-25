# Independent reproof of the arithmetic layer of PR3562's ordinary-rate theorem

Sagar Thakrar (`thakrarsagar`), with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.

**Object.** [PR3562](https://github.com/CrocSwap/integer-mult-bounds/pull/3562)
by Jose Manuel (`jmbarrancoml`), head `abb93be8b9ceca07a2b17f3a97db7bb6b074271d`,
file `research/retuned-ordinary-coupling/PROOF.md` (sha256
`3e554832c38b4b801f55b20868679f3283bc90cd5a9d8ce1960f828ed2655f22`). Line
numbers below refer to that file. I wrote this reproof from that PROOF.md and
its stated premises only. I did not read PR3562's EVIDENCE.md, certificate or
verifier code.

**Verdict.**

- Every audited arithmetic step (a)-(e) holds from premises P1-P5 below, with
  c fixed by P6.
- One exposition gap. Line 156 lists `n<=e^(1-c)`, `w<=2e^c` and the bound
  `n^(1-c)w <= 2^c e^(1-a)` of line 158. Line 158 is stated without
  derivation. The two bounds listed beside it do not imply it: alone they give
  only `n^(1-c)w <= 2e^(1-a)` (exact witness below).
- The inequality `n <= e/w` follows from the selector definition
  `n=floor((e-k)/w)` on line 117 of the same file, and it does imply line 158.
  So the stated bound, and the constant `4283584`, hold exactly as written.
- Deriving line 158 from the two line-156 bounds alone would give the
  coefficient `8033584`. The O-bound `O_q(V e^(1-a))` would be unchanged.

**Scope.** This is an independent check of a scoped all-size arithmetic
implication, P1-P5 ⇒ (2) and the Consequence, under PR3562's retained
source/refinement and physical-cost premises. It does not admit those
premises. In particular it takes PR3562's line 154 as premise P5, although
PR3562 derives that line (lines 141-154) from physical claims audited nowhere
here. It does not reprove history, preparation and reserve (lines 84-104), the
binary transfer (lines 172-174), or the space, restoration and ownership claims
(lines 20-25). It is not a κ, not a frontier change and not a complete
multiplication theorem.

## Premises used (all stated in PR3562's PROOF.md)

- P1 (lines 36-41): m=64, W=28416, H={1:381024, 2:400416, 3:22752,
  4:26880, 5:29376, 6:17376, 7:26784, 42:288}, ε=10^-16, F=32·64²·ΣH_r=118606528512.
- P2 (lines 45-50): the C0 recurrence for normalized time T(n,w), with f=floor(n/64):
  T(n,w) ≤ Cw for 0<n<64, and for n ≥ 64
  T(n,w) ≤ Σ_r (H_r/W) T(rf,w) + (εF/W) max_{1≤j≤f} T(j,w) + C(n+w).
  The root e, w and history domain are fixed along a call (line 52).
- P3 (lines 108-118): D, K(w), stock=K(w)^D(e), k=min{j≥0: q^j ≥ stock},
  w=ceil(e^c). The elementary branch is used iff 2k ≥ e or floor((e-k)/w) < 64.
  Otherwise n=floor((e-k)/w) and ℓ=e-k-nw.
- P4 (lines 120-121): D(e) ≤ 2log2(e) for e ≥ 2, |GL_64(F_q)| < q^4096, 269241600 < q.
- P5 (line 154, derived on lines 141-154): C dominates the C0 coefficient, the
  wrapper bill CV(n+k+w+1) and the elementary fallback coefficient. Two reversed C0
  calls each have padded volume below 2V, so
  T_B(e)/V ≤ C(801n + 4000000 n^(1-c) w + k + w + 1).
  Its coefficients are one line of arithmetic from (1):
  2·2·(200n + 10^6 n^(1-c) w) + (n + k + w + 1) = 801n + 4000000 n^(1-c) w + k + w + 1.
  The verifier checks 801 = 2·2·A + 1 with A=200. I take line 154 as given and audit
  what follows from it. Its physical inputs are not audited: exactly two calls,
  padded volume below 2V per call, cost equal to padded volume times T at the same
  n, and a complete wrapper bill.
- P6 (line 18): c=1/577, a=c(1-c)=576/332929. Lines 86-97 use 17/10000 < c < 1/512
  only to keep PR2753's history estimates; those are retained and not audited here.

Write μ_t = (Σ_r H_r (r/64)^t + εF (1/64)^t)/W (line 55).

## (a) Moment certificates

**Claim.** μ_1 < 199/200 and μ_(576/577) < 1 - 10^-6, inside PR3562's
stated enclosure [999998938581682162866772413602, ...603]/10^30.

**Exact μ_1.** Σ_r r H_r = 1808352. Hence

    μ_1 = (1808352/64 + εF/64)/W = 2874298095721977/2890625000000000,
    200(1-μ_1) = 200·16326904278023/2890625000000000 ≈ 1.12965 > 1.

**μ_(576/577).** It is enclosed by two exact engines. They use the same two
methods that PR3562 says it used (lines 64-72), implemented independently
without reading PR3562's code:

- E1, integer-root bisection. For each r, find the integer z with
  z^577·64^576 ≤ r^576·Q^577 < (z+1)^577·64^576, at Q=2^128 (PR3562: 2^160). Then
  z/Q ≤ (r/64)^(576/577) < (z+1)/Q.
- E2, a rational interval series. It encloses ln 2, ln 3, ln 5 and ln 7 by
  atanh(1/m) series for m=3,5,9,15, each with an explicit geometric tail. It then
  forms L_r = ln(64/r) and encloses exp(t·L_r) by a Horner Taylor sum. All
  terms are positive, so outward dyadic rounding at 2^-256 is monotone, and the
  Lagrange tail is u^(K+1)/(K+1)!·1/(1-u/(K+2)). Finally
  (r/64)^t = 1/exp(t·L_r).

Both engines combine the eight radix terms and the fallback term with exact
nonnegative rational weights:

| engine | enclosure of μ_(576/577) | width (printed by verify.py) |
|---|---|---|
| E1 | 0.999998938581682162866772413602788… | 9.358e-38 |
| E2 | 0.999998938581682162866772413602788… | 1.695e-77 |

Both enclosures lie inside PR3562's 10^-30 enclosure, and
10^6(1-μ_(576/577)) = 1.0614183178… > 1 under both. The fallback term is
retained. Without it, μ_(576/577) = 0.999998938575113…, which is outside PR3562's
enclosure. So PR3562's stated enclosure is the fallback-inclusive moment, as
claimed.

**Source binding.** The verifier binds P1 to main:

- H and W match the selected bit supplier: the "nine" profile and live count
  in `research/e8-bit-p111-tuned/tune/EXPECTED.json`, whose `bit_lower` equals the
  selected `ASSEMBLY.json` value.
- εF/W matches the literal `118606528512 / (10000000000000000 * 28416)` in
  `research/lean-bit-moment-discharge/lean/Selected.lean`.

## (b) The C0 majorant (parametric)

**Lemma B.** Let 0<t≤1, C ≥ 0, and A, M ≥ 1 with A(1-μ_1) ≥ 1 and M(1-μ_t) ≥ 1. Then
under P2, for all integers n ≥ 1 and all w ≥ 1,

    T(n,w) ≤ G(n) := A C n + M C n^t w.

*Proof.* Strong induction on n.

- *Base, 0<n<64.* T(n,w) ≤ Cw ≤ M C n^t w ≤ G(n), because n^t ≥ 1 and M ≥ 1.
- *Step, n ≥ 64.* Here f=floor(n/64) ≥ 1. Every child size satisfies
  1 ≤ rf ≤ 42f ≤ 42n/64 < n, and every fallback index satisfies 1 ≤ j ≤ f < n.
  So the hypothesis applies to all of them.
- G is nondecreasing in its argument (C ≥ 0), so max_{j≤f} G(j) = G(f).
- Using f ≤ n/64, which gives rf ≤ (r/64)n and (rf)^t ≤ (r/64)^t n^t:

      T(n,w) ≤ Σ_r (H_r/W) G(rf) + (εF/W) G(f) + C(n+w)
             ≤ A C n μ_1 + M C w n^t μ_t + Cn + Cw
             = G(n) - Cn[A(1-μ_1) - 1] - Cw[M(1-μ_t) n^t - 1]
             ≤ G(n),

  because A(1-μ_1) ≥ 1 and M(1-μ_t) n^t ≥ M(1-μ_t) ≥ 1. ∎

The lemma does not assume that measured T is monotone; only the majorant G is.
PR3562's (1) is the case t=576/577, A=200, M=10^6, whose hypotheses step (a)
certifies with strict margins 1.12965 and 1.0614. The fallback weight enters
through G(f) with the factor (1/64)^t. That is why the moment must include the
εF(1/64)^t term: a certificate without it would not cover the fallback term of
the induction. At c=1/577 the numerical margin happens to absorb the 6.6e-12
contribution.

## (c) Selector fit for e ≥ 2^20 (parametric in c ∈ (17/10000, 1/512))

1. *D(e) ≤ 2log2(e) for e ≥ 2* (P4; reproved). For e<64, D(e)=0. For e ≥ 64,
   e' = 42·floor(e/64) satisfies 42 ≤ e' ≤ 42e/64 < e. By strong induction,
   D(e) ≤ 1 + 2log2(42e/64) = 2log2(e) + 1 - 2log2(64/42) < 2log2(e), since
   2log2(64/42) > 1.2. The verifier also checks 2^D(e) ≤ e² for every
   2 ≤ e ≤ 2^20. As a side computation it prints the largest ratio
   D(e)/floor(log2 e) there: 22/19, first attained at e = 941248.
   The induction uses child rank r_max = 42; it needs 2log2(64/r_max) ≥ 1,
   that is r_max ≤ 45.
2. *Stock exponent.* By P4, K(w) < q·q^4096·q^(4096(w-1)) = q^(4096w+1). So
   stock < q^((4096w+1)D(e)) whenever D(e) ≥ 1. Hence
   k ≤ (4096w+1)D(e) ≤ 4097w·2log2(e) = 8194 w log2(e) ≤ 8195 w log2(e).
   If D(e)=0, then stock=1 and k=0. Since w=ceil(e^c) ≤ e^c+1 ≤ 2e^c,
   k ≤ 16390 e^c log2(e) for e ≥ 2, as stated on line 123.
3. *2k<e.* The function g(e) = e^(c-1)log2(e) has d(ln g)/d(ln e) = (c-1) + 1/ln(e),
   which is negative for ln(e) > 1/(1-c), so in particular for e ≥ 2^20. Thus
   2k/e ≤ 32780 g(e) ≤ 32780·20·2^(20c)/2^20. Also 20c < 20/512 = 5/128, and
   2^(5/128) < 17/16 because 17^128 > 32·16^128. So
   2k/e < 32780·20·(17/16)/2^20 = 696575/2^20 < 1.
4. *n ≥ 64.* From 2k<e and w ≤ 2e^c we get (e-k)/w > (e/2)/(2e^c) = e^(1-c)/4.
   Hence n=floor((e-k)/w) > e^(1-c)/4 - 1 ≥ 2^10/4 - 1 > 64, since c<1/2.

So for e ≥ 2^20 neither elementary predicate fires, as stated on lines 133-135.
At e=2^20 itself: w=2, D=22 and k ≤ 180246. The worst case of k then gives
n ≥ 434165, an exact boundary check.

## (d) The composed bound (2): the 2^c factor and the constant

In the non-elementary branch, P3 gives n=floor((e-k)/w) with k ≥ 0. So

    n ≤ e/w.                                                         (N)

Together with e^c ≤ w ≤ 2e^c and 1-a = 1-c+c²:

    n^(1-c) w ≤ (e/w)^(1-c) w = e^(1-c) w^c ≤ e^(1-c)(2e^c)^c = 2^c e^(1-a).   (*)

Also 2^c < 2^(1/512) < 17/16, because 17^512 > 2·16^512. This is
line 158's inequality.

**The derivation gap (lines 156-158).** Line 156 lists n ≤ e^(1-c), w ≤ 2e^c and
the bound of line 158; line 158 is stated without derivation. Lines 160-161 bound
only k, w and 1, so n ≤ e^(1-c) is what bounds the 801n term. The two bounds listed
beside line 158 do not imply it: alone they give
n^(1-c)w ≤ e^((1-c)²)·2e^c = 2e^(1-a), not 2^c e^(1-a).

*Witness.* For c=p/q, take e=2^q. The values n=e^(1-c)=2^(q-p) and
w=2e^c=2^(p+1) satisfy both line-156 bounds with equality. For them,
log2(n^(1-c)w) - log2(2^c e^(1-a)) = 1-c exactly. So the ratio is
2^(1-c) > 2^(511/512) > 17/16, which violates line 158's conclusion. These
values have nw = 2^(q+1) > e, so they violate (N). They also violate
w = ceil(e^c) = 2^p (line 18). (N) excludes the witness, and (N) follows from
line 117.

*Sharper witness, respecting line 18.* Take e=2^20, c=1/577, w=2 and n=1023683.
Then 1 < e^c < 2, so w = ceil(e^c) ≤ 2e^c, and n = floor(e^(1-c)) because
n^577 ≤ 2^11520 < (n+1)^577. Raising to the power 332929 = 577², the exact integer
comparison n^(576·577)·2^332929·16^332929 > 17^332929·2^577·2^(20·332353) shows
n^(1-c)w > (17/16)·2^c·e^(1-a); the ratio to 2^c e^(1-a) is about 1.9502. These
values satisfy both line-156 bounds and line 18 and violate only (N), since
n > e/w = 524288. So among the stated constraints, (N) is what closes the gap. This
check is not part of verify.py; it was run separately (and in one AI review pass),
and this one line reproduces it:

    python3 -c "n=1023683; print(n**577<=2**11520<(n+1)**577, n**(576*577)*2**332929*16**332929 > 17**332929*2**577*2**(20*332353), 2*n>2**20)"

which prints `True True True`. So line 158 is true for the actual selector; what is missing is only
its derivation.

**Constant.** The remaining terms of P5 are bounded as follows, for e ≥ 1 and
c < 1/512:

- n ≤ e/w ≤ e^(1-c) ≤ e^(1-a);
- w ≤ 2e^c ≤ 2e^(1-a), since c ≤ 1-a ⟺ (1-c)² ≥ 0;
- 1 ≤ e^(1-a);
- k ≤ 16390 e^c log2(e) ≤ 32780 e^(1-a). This uses log2(x) ≤ 2x^s for x ≥ 1 and
  s=(1-c)²: max_{x≥1} log2(x)/x^s = 1/(s·exp(1)·ln 2) < 2, because s·exp(1)·ln 2 > 1/2.
  For e=1, k=0.

Hence

    T_B(e)/V ≤ C e^(1-a) (801 + 4000000·17/16 + 32780 + 2 + 1) = 4283584 C e^(1-a).

The identity 801 + 4250000 + 32780 + 2 + 1 = 4283584 is exact. Deriving line 158
from the two line-156 bounds alone (factor 2) would give
801 + 8000000 + 32780 + 3 = 8033584. This derivation of (2) does not use
e ≥ 2^20, so it covers every e at which the non-elementary branch is taken.

**Elementary branch and setup.**

- For e < 2^20, a < c < 1/512 gives e^a < 2^(20/512) < 2. So C·V·e < 2C·V·e^(1-a)
  fits (2). This reads the "elementary fallback coefficient" of line 142, used on
  lines 165-166, as T_elem ≤ C·V·e; PR3562 does not write that form explicitly.
- For e ≥ 2^20, step (c) rules out the elementary branch.
- *Setup absorption* (1+log2 V)^4 ≤ 512V for V ≥ 1, by a different route from
  PR3562's. Since ln 2 > 1/2, 1+log2 V ≤ 1+y with y = 2ln V. Then
  (1+y)^4 exp(-y/2) is maximized at y=7, where it equals 8^4 exp(-7/2) < 4096/33 < 512.
  The verifier certifies exp(7) > 33² with E2's exp bounds.

## (e) Consequence arithmetic

- The excess is exact: a - C_complex = 576/332929 - 1729033982646513517717/10^24
  = 354445191478901059996907/(332929·10^24) ≈ 1.0646e-6 > 0, as on line 181.
- E2 brackets the selected bit root inside (b_sel, b_sel+10^-24], with
  b_sel = 0.001733427039589844234749. Hence 1/577 < b < 1/576.
- The ratio 576/577² exceeds C_complex, while 577/578² < C_complex.
- (j-1)/j² - j/(j+1)² = (j²-j-1)/(j²(j+1)²) > 0 for j ≥ 2, so (j-1)/j² is
  decreasing on j ≥ 2.
- Together these give the restricted statement on lines 183-187: among couplings 1/j,
  j ≥ 2, only j=577 passes both tests.

C_complex is PR2979's primitive complex lower bound. Main's archived comparator
`research/rank7-coupled-586-588-carrier-fold/comparators/PR2979-CLAIM.json`
records `complex_lower` = 1729033982646513517717/10^24 and
κ = complex_lower - 10^-46 - 10^-70. So line 181 compares primitive with primitive.

## Gap classification

| step | status | consequence |
|---|---|---|
| (a) μ_1, μ_(576/577) | proved, two engines, inside the stated enclosure | none |
| (b) majorant (1) | proved (Lemma B, parametric) | none |
| (c) fit for e ≥ 2^20 | proved; 8195 is looser than the 8194 that P4 gives | none |
| (d) line 158 | exposition gap: stated without derivation; not implied by the bounds listed on line 156, implied by (N) from line 117 | 4283584 stands; deriving from the line-156 bounds alone gives 8033584, same O-bound |
| (d) elementary branch | holds; reads the elementary cost as C·V·e (implicit in PR3562) | none |
| (e) consequence | exact | none |

[PR3576](https://github.com/CrocSwap/integer-mult-bounds/pull/3576) (`kumagi`)
substitutes PR3562's exponent τ = 1-a = 332353/332929 into T74. The audited layer it
inherits, including (2) with the constant 4283584, holds from P1-P5, conditional on P5
and PR3562's other retained premises. This narrows, and does not lift, PR3576's stated
limit that the all-size PR3562 theorem is not independently reproved.
[PR3690](https://github.com/CrocSwap/integer-mult-bounds/pull/3690) (`zxv`) inherits
only the parametric template below; its step (a) on R437 is not checked here.

Steps (b)-(d) are parametric. At PR3690's c=1/576 with M=10^6, the (c)-(d)
arithmetic gives the same 4283584 and a = 575/331776. This assumes PR3690 keeps the
same selector and stock definitions (D with child rank 42, K(w)), the same P5
composition, A=200 and the same P2 form for R437. PR3690 reports its own two-engine
moment enclosure; I did not recheck it or bind its R437 histogram. Under the
selected histogram, μ_(575/576) > 1, because 1/576 > b.

## Ceiling remark (proof shape, not a barrier)

This shape needs μ_(1-c) < 1, that is c < b, where b is the fallback-inclusive
root. The function c(1-c) is increasing on (0,1/2). So on the selected bit program
the shape's exponent has supremum b(1-b) = 0.001730422270288263023337…, not attained.
E2 places the root in (b_sel, b_sel+10^-24], where b_sel is the selected
bit_saving. E1 independently brackets it in (10/5769, 9/5192). verify.py certifies
that the fallback-free root lies above b_sel + 10^-24, so the selected value is the
fallback-inclusive root. Independent 60-80 digit decimal bisections outside verify.py
put the fallback-free root about 2.01·10^-12 higher; the verifier does not certify
that figure.

**Like-for-like comparisons.** PR2979, PR3633, PR3642 and PR3653 each state their
endpoint as κ = X - 10^-46 - 10^-70, with X a primitive complex lower bound (the
modern outer). So the like-for-like comparison is a or b(1-b) against X, primitive
with primitive. Under the retained transfer x ↦ x/(1+x), both sides move by the same
increasing map and no order changes. I do not use the mixed comparison of a/(1+a)
against a modern-outer κ, which this loop's sibling PR3700 withdrew.

| endpoint X | a - X, a = 576/332929 | b(1-b) - X |
|---|---|---|
| PR2979 | +1.0646e-6 | +1.3883e-6 |
| PR3633 | +2.246e-9 | +3.259e-7 |
| PR3642 | -2.958e-7 | +2.788e-8 |
| PR3653 | -3.203e-7 | +3.371e-9 |

The reciprocal coupling clears PR2979 and PR3633 but not PR3642 or PR3653. A
non-reciprocal c can still clear PR3653, inside a window of width about 3.4e-9
below b. One E2-only example: c' = b_sel - 10^-9 gives c'(1-c') - X_3653 = +2.374e-9.
It needs M = 305992814, so the coefficient is 2601006087/2 ≈ 1.3e9. This is a remark
about the shape's reach, not a claimed endpoint. Which primitive binds is decided by
the complex side; this audit does not change it.

On a different supplier, pending PR3690 (R437, c=1/576) reports a = 575/331776.
verify.py prints 575/331776 - X for all four endpoints; the smallest is +2.678e-6
(PR3653). So this ceiling matters only if R437 is not admitted. R437's moments are
not checked here.

## Not covered

- PR3562's retained premises: P5 and its physical composition (lines 141-154), and
  the PR2753/PR2809/PR2899/PR2808 inventory, history and wrapper arguments.
- History, preparation and reserve (lines 84-104) and the bit-wrapper transfer
  (lines 172-174).
- The O_q(V)+F_q space bound, borrowed-input restoration and ownership claims
  (lines 20-25).
- PR3562's code, EVIDENCE.md and production factory.
- PR3576's T74 binding, and PR3690's R437 source binding and moments.
