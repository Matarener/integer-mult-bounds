# Sharp declared-width window for the paid residue child

SPDX-License-Identifier: Apache-2.0. Prepared for ToikY with substantial
OpenAI Codex assistance, including separate mathematical review. This is a
written proof with exact finite checks, not a formal-kernel certificate.

## Scope and predecessor

PR3881 at `75e098dc12a2567e73a2858137408e08d31dbf84` supplies the
residue-assisted Gaussian construction and its all-input finite-box proof.
Credit Dugongue for that extension and Mason Hale for the retained certified
Gaussian backend, normalization, CRT ordering and carry reconstruction;
their retained notices give the earlier lineage. This result determines the
sharp size window of the unchanged exact lane and instantiates its k=28 point.

## Attained size theorem

Let n,b be positive integers, 1 <= k <= b, and 0 <= x < 2^n. Define

    L = ceil(n/b), t = n - b(L-1), h = ceil(log2 L), w = 2k+h.

Here 1 <= t <= b and h=(L-1).bit_length(), including h=0 at L=1.
Write x in exactly L base-2^b digits a_j, retaining leading zeroes. The
unchanged lane forms P(x)=sum_j (a_j mod 2^k) 2^(wj). Its exact maximum is

    P_max = (2^k-1) sum_(j=0)^(L-2) 2^(wj)
            + (2^min(k,t)-1) 2^(w(L-1)),

with an empty sum when L=1. Each full digit is independently at most 2^b-1;
the top digit is at most 2^t-1. Reducing them gives precisely the displayed
coordinatewise maxima, attained simultaneously by x=2^n-1. Lower packed
slots occupy positions below w(L-1), while the highest digit has exactly
min(k,t) bits. Therefore the attained maximum operand bit length is

    D_star(n,b,k) = min(k,t) + (L-1)(2k+h).

This applies separately to both operands. The predecessor's conservative
D=k+(L-1)w exceeds it by max(k-t,0). For equal-length arrays, every packed
product coefficient is at most L(2^k-1)^2 < L 2^(2k) <= 2^w; hence the
packing remains carry-free. This bound concerns each child input, not the
product's potentially twice-longer output or its computation cost.

## Exact strict admission and closed maximum

A child is uniformly strictly smaller than declared width n exactly when

    (L-1)(w-b) < t-min(k,t) = max(t-k,0).

Equality D_star=n fails strict admission. For L=1 the condition is k<n.
For L>=2, w<b admits every t; w=b admits exactly t>k; w>b admits exactly
t>k+(L-1)(w-b). These cases exhaust all integers w. In the last two cases
the inequality becomes (2L-1)k < n-h(L-1). Consequently the largest admitted
k in 1..b, with 0 meaning none, is

    L=1: min(b,n-1);
    L>=2: min(b,max(0, floor((b-1-h)/2),
                       floor((n-1-h(L-1))/(2L-1)))).

The first floor describes all w<b; the second describes the remaining
strict inequality. Their union is an initial interval of residue widths.

## Consequences within the retained 64-bit-digit box

For n=14592, L=228,t=64,h=8. At k=28, w=64 and D_star=14556<n;
at k=29, w=66 and D_star=15011>n. Both are attained by the maximal input.
Thus 28 is the largest residue width with a strict child at this declared
width. It is not a largest residue width for every smaller declared width.

For example n=65,k=29 gives L=2,t=1,w=59 and D_star=60<65, while D=88.
The conservative bill would miss this admission. For k=28 every n from
29 through 8192 is admitted. Above 8192, L=129..228 and w=64, so precisely
top widths t=29..64 are admitted: n=8220 has D_star=n, but n=8221 is strict.
For k=27, w<=62 throughout L<=228, so every n=28..14592 is admitted.
It is the largest fixed k with admission throughout its tail k+1..14592:
every k>=28 fails at n=8193, whose top digit has width 1 and whose w>=64.
These statements use declared width, not the shorter actual length of a
particular operand. The separate Gaussian capacity condition is 2L-1<=455.

## Frozen precision transfer and all-input implication

Retain source axes (5,7,13), target axes (8,16,32), alpha=5, Q=448 and b=64.
The predecessor proves that prepared matrices and their operator enclosures
are independent of rounded payload precision p. Its source certificate is
U_i(p)=A_i 2^(-p)+B_i, A_i=2(log2(t_i)+2)2^50, so sum A_i=36*2^50.
Both normalization factors remain in C=455^2*2^132. The uniform recovered
coefficient radius is exactly

    R(p) = C[(108*2^50+2)2^(-p) + 3 sum_i B_i + 8*2^(-448)].

The replay derives the p-independent remainder from the authenticated p=208
receipt, checks its nonnegativity, and checks exact rational inequalities
R(208-k)<2^(k-1)<=R(207-k) for every integer k=0..64. The coefficient of
2^(-p) is positive, so p_min=208-k for this fixed sufficient certificate.
The original p>100, alpha^2<p, integer/theta, Q guard, operator-residual,
disk and exact-input-grid conditions remain required; the replay checks
their admitted domains and regenerates the three actual p=180 operators.
This is not a lower bound on other numerical methods or certificates.

At n=14592,k=28,p=180, the regenerated uniform radius is below 2^27 and
the exact child inputs have at most 14556 bits. Under the unchanged backend
and predecessor proof premises, every pair 0<=x,y<2^14592 therefore yields
its exact product: carry-free packing supplies genuine residues, strict
residue spacing gives unique coefficient lifts, capacity prevents cyclic
wrap, inverse CRT orders the coefficients, and the inherited carry scan
preserves their positional value. Two executed maximal-input boundary
cases corroborate this implication; the reference product is only a
postcheck and never supplies decoder data.

The full invoice still includes three tensor transforms, pointwise products,
one exact multiplication, packing/extraction, lifting/carry and preparation.
No physical caller, all-size recurrence/base cases, measured whole-runtime
gain, supplier admission, new kappa or selected-frontier change is proved.
