# Independent audit of the normalized Gaussian exponential backend

## Conclusion and exact scope

No correctness gap was found in the following universal implication for the authenticated source at PR4205 head `66b95cc916552f487203be14fd99a7aea0bdd78e`: for every nonnegative rational f and integer J>=16, the actual `Gaussian.exponential(f,J)` terminates mathematically, encloses exp(-pi*f), and returns width at most 512 J^2 2^(-J). Its coefficient and conditioning precision corollaries follow. This is an independent written/code derivation, not acceptance inferred from a finite sweep or an independent proof-assistant/human theorem.

The uniform width assertion applies to the argument constructed as `pi_interval(J) * f`. It is not a width theorem for `exp_negative` on an arbitrary unrelated wide nonnegative interval. No leading-section inverse estimate, full-circuit proof, raw Gaussian gauge/normalization, complete producer cost, physical delivery or multiplication theorem is audited here.

## Authenticated source and arithmetic contract

`intervals.py` is the unchanged Mason Hale implementation, Git blob `91d458865aa026bdf0d59653a4ecbfe3a178ecbc`, SHA256 `159d2a7d32a8cc7c8f56632a8ef127308b984a0a6753c9d6bdccacc6e7d6d4df`. `gaussian.py` is the completed wrapper, Git blob `52ad2e1d605f5f7d669234567c25bc087306dd44`, SHA256 `08155357fd39b5fd7959f51f1d205b6511b8577b51520d793c89f92368b399ab`.

The following line references use these exact unchanged source files. Integers and `Fraction` operations are assumed exact under the stated CPython arithmetic contract. No floating transcendental operation occurs in these routines. Machin's identity and the standard alternating/positive Taylor remainder arguments are mathematical dependencies, not a formal-kernel claim.

For h=2^(-J), `Interval.rational` (lines35-38) encloses a rational with total endpoint deficit at most h. Addition is exact (45-47). Multiplication takes all four endpoint products and rounds outward (60-64), adding less than 2h to the exact product width. Division by a positive integer uses direct floor/ceiling (68-79), not a separately rounded reciprocal, and adds less than 2h to the divided width. Positive reciprocals reverse the endpoints and round outward (72-74). These facts follow directly from integer floor and `ceildiv` (16-18), including negative inputs when present.

## 1. Machin enclosure and termination

At `pi_interval`, lines99-108, after n terms of arctan(1/q), the next alternating term is

    r_n = 1 / ((2n+1) q^(2n+1)).

The terms decrease to zero. The parity-specific return endpoints in line108 are the two consecutive alternating partial bounds. Thus each returned interval encloses the arctangent and has width r_n. For q>=5,

    r_n < 2^(-4n-2).

Consequently n=ceil((J+16)/4) already satisfies the strict source stop r_n<2^(-J-16). Both loops terminate within that many terms. Lines109-111 combine the exact rational endpoints by Machin's formula before the one dyadic rounding. Therefore

    width(P) < (2 + 20/65536) h < 3h,

where P=[P_L,P_U] is the returned pi interval. The 20 is 16+4, and the 2h is the final outward endpoint rounding; there is no per-series-term dyadic error to accumulate.

The same alternating bounds give coarse rational bounds with comfortable margins:

    16(1/5 - 1/(3*5^3)) - 4/239 > 25/8,
    16/5 - 4(1/239 - 1/(3*239^3)) < 7/2.

Since J>=16, the final endpoint rounding and the arctangent tails are much smaller than those margins. Hence 3<=P_L<=pi<=P_U<=4. This checks the source proof's endpoint constants rather than assuming rounding preserves a bare strict inequality 3<pi<4.

## 2. Constructed argument and the large-exponent branch

The wrapper at `gaussian.py` lines177-185 admits the stated f,J, returns exact one for f=0, and otherwise forms X=P*F, where F is the outward coercion of rational f. Write F_L<=f<=F_U. Both endpoints are nonnegative and

    (f-F_L) + (F_U-f) <= h.

Using the TOTAL deficit h is essential; bounding each deficit separately would lose a constant. Before the final product rounding,

    P_U F_U - P_L F_L
      = f(P_U-P_L) + P_U(F_U-f) + P_L(f-F_L)
      <= 3 f h + 4h.

After product rounding this gives W_X<= (3f+6)h. Also X_L>=3f-4h, since F_L>=f-h, P_L>=3, and lower product rounding loses less than h. Nonnegativity is preserved by the floor of a nonnegative product.

If X_L>=J, `intervals.py` lines118-120 returns [0,h]. Because pi*f>=X_L and e>2, exp(-pi*f)<=e^(-J)<h. This branch encloses the answer and has width h, within the claimed bound for all J>=16. It also handles arbitrarily large encoded f without range-reduction squarings.

Otherwise X_L<J, whence f<(J+4h)/3<(J+1)/3. Thus

    W_X <= (J+7)h <= 2Jh,
    X_U = X_L+W_X < J+2Jh <= J+1 <= 2J.

The f-dependence of intermediate argument width has therefore been eliminated only after splitting on the actual source branch.

## 3. Range reduction and the positive Taylor loop

Let a=2^k be the least divisor selected by lines121-124. The loop terminates because X_U is finite and the threshold grows without bound. If k=0 then a=1; otherwise minimality gives a<16 X_U. Hence a<=32J in either case. Integer division gives Y=X/a with width

    W_Y <= W_X/a + 2h.

Since 1/8 lies exactly on the J-grid, upper outward rounding cannot move a number at most 1/8 above 1/8. Consequently 0<=Y_L<=Y_U<=1/8.

At lines125-137, `term` encloses Y^n/n!. Its upper endpoint is always at most one: multiplication by Y maps an upper endpoint at most one to at most the exactly representable 1/8; positive integer division cannot exceed that bound. Let d_n be its width after the nth iteration. The product-width and integer-division bounds give

    d_0=0,
    d_n <= d_(n-1)/8 + W_Y + 4h,
    d_n <= (8/7)(W_Y+4h) <= 2W_Y+5h.

The actual stop is independent of rounded term endpoints. For 0<=y<=1/8, the omitted positive exponential tail after degree n is at most

    2 / (8^(n+1) (n+1)!).

This follows by a geometric upper bound on successive omitted-term ratios. At n=ceil(J/3), even dropping the factorial makes that expression less than h. Thus the loop terminates by that degree, at most J. The positive tail is strictly between zero and h, so its outward addition in line136 is exactly one grid unit. Additions of interval endpoints are exact. The total enclosure S for exp(Y) has S_L>=1 and

    W_S <= J(2W_Y+5h)+h.

## 4. Reciprocal, squaring and the final clamp

`total.reciprocal()` at line138 is always defined because S_L>=1. Its width is at most W_S+2h: the reciprocal derivative has modulus at most one on [1,infinity). Its endpoints are in [0,1], since the rounded reciprocal upper endpoint of an interval lower endpoint at least one is at most the exactly representable one.

For endpoints 0<=l<=u<=1, u^2-l^2<=2(u-l). Each rounded squaring in lines139-140 therefore changes a width W to at most 2W+2h and retains endpoints in [0,1]. After k squarings,

    W_E <= a W_S + (4a-2)h
        <= 2J W_X + a(9J+5)h
        <= (292J^2+160J)h
        <= 512J^2 h.

Here a<=32J and W_X<=2Jh were proved for the non-shortcut branch. The final clamp in line141 cannot lose the true positive answer, which is at most one; in the derived endpoint bounds it is already redundant. The initial pi/coercion/product box encloses pi*f, positive Taylor followed by reciprocal encloses exp(-Y), and squaring restores exp(-X). Thus the width derivation accompanies an enclosure proof rather than a narrow-box assumption.

## 5. Coefficient precision and inward quantization

For integer p>=1 and J=2p+32,

    512 J^2 2^(-J) <= 2^(-p).

Equivalently 512(2p+32)^2<=2^(p+32). At p=1 the left side is591872 and the right side is2^33. The ratio of successive left/right ratios is ((p+17)/(p+16))^2/2<=162/289<1. This is a quantified induction, not evidence inferred from checking finitely many p.

For E=[L,U] within [0,1], `inward_quantize` lines202-221 returns the p-grid floor of L when L>0 and zero when L=0. Its distance from every enclosed value is at most width(E)+2^(-p). The imaginary input box is exact zero and contributes zero error. For p=b+1 this is at most2^(-b), establishing the bound checked at `gaussian.py` lines195-204. When f=0 the wrapper supplies exact one and inward quantization returns one with zero error. For admitted integer offsets and |s|<=1/2, f=c(u^2-2su)>=0; zero also occurs at the appropriate half-shift off-diagonal, not only at u=0.

## 6. Conditioning precision corollary, without accepting a matrix inverse bound

Let c>0 be rational, a=ceil(2/c)>=1, J_Q=2a+36, and y=exp(-pi/(4c)). The exact rational ceiling in `gaussian.py` line131 yields that integer a. The width theorem implies

    width(E_Q) <= 2^(-(a+2)).

Indeed this is equivalent to512(2a+36)^2<=2^(a+34). At a=1 the two sides are739328 and2^35; the ratio multiplier is ((a+19)/(a+18))^2/2<=200/361<1.

The elementary pi<4 and e<4 imply y>exp(-1/c)>2^(-2/c)>=2^(-a). Therefore width(E_Q)<y/4. Enclosure gives

    0 < (3/4)y <= L <= y,
    N/y <= N/L <= (4/3) N/y.

Strict inequalities can be retained at the lower endpoints. Thus the positivity/width guards at lines133-136 cannot reject a mathematically valid evaluation under this arithmetic contract, and the rational qbar=N/L has the claimed multiplicative relation to N*exp(pi/(4c)). This audits the backend scalar allowance only. It does not independently prove that this analytic scalar bounds any Gaussian leading-section inverse; that is the separate Section2 matrix theorem.

## Remaining obligations and credit

Independent finite oracle/source-integration comparison can corroborate these formulas and expose implementation defects, but does not replace the all-rational/all-precision derivation above. Full normalized caller/circuit correctness, coefficient-table/root binding beyond this backend, finite-cap leading-section conditioning, raw alpha/gauges, rational setup complexity, physical delivery, native/outer admission and formal-kernel acceptance remain outside this audit.

Credit Mason Hale, with substantial OpenAI Codex assistance, for unchanged outward arithmetic and transcendental routines; Jose Manuel/jmbarrancoml for the wrapper, explicit width/precision proposition and normalized logical connection; retained original NOTICE/license and prior Gaussian/circuit source lineage. This review verifies the stated existing implication independently and claims no new general transcendental method or broad novelty.
