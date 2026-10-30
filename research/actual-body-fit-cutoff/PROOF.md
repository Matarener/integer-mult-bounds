# Sharp fit at the actual body depth

Fix a prime q>2^80 and a positive integer original width e. Keep the existing
atom width w=ceil(e^(17/10000)) fixed before borrowing. Define

```text
D(n)=0 for n<64, otherwise D(n)=1+D(42 floor(n/64)),
N=|GL_64(F_q)|, b=28416 N q^(4096(w-1)),
S_0=1, S_d=9475 b^d for d>=1,
n(k)=floor((e-k)/w).
```

A covering plan satisfies k>=0, 2k<e, n(k)>=64 and S_D(n(k))<=q^k.
A strict-volume plan replaces the final condition by S_D(n(k))<2q^k.
These are the exact arithmetic predicates of PR3486 and PR3523. This theorem
concerns their existence, with the prescribed reserve and atom width.

**Theorem.** Every e>=245767 has a covering plan and hence a strict-volume
plan, for every prime q>2^80. The integer 245767 is the least uniform cutoff
for each predicate. At e=245766 the certified prime
q*=213*2^80+1 admits neither plan.

This is an unconditional arithmetic theorem about the defined reserve.
Its use by a physical caller remains conditional on the predecessors' source,
fresh-row, completed-child, padding, pointwise restoration and cost premises.
It supplies no actual selected bootstrap-stage coefficient or new kappa.

## 1. Reduce existence to the largest legal borrowing

The child map is nondecreasing and contracts by at least the factor 42/64
at every active step. Thus D is finite and nondecreasing. S_d is
nondecreasing, including d=0. As k increases, n(k) and its stock decrease,
while q^k increases. This proves monotonicity for both admission predicates,
as already established by PR3486 and PR3523.

Let U=floor((e-1)/2). If n(U)>=64, U is legal and it suffices to check it.
If even this largest k fails the stock inequality, every legal k fails.
The proof below uses U as an existence witness. It does not claim U is the
least borrowing or materialize q^U on a tape.

Counting independent matrix columns gives

```text
N=q^4096 P(q), P(q)=product_(i=1)^64 (1-q^-i), 0<P(q)<1.
S_d=q^(4096wd) C_d P(q)^d, C_d=9475*28416^d, d>=1.
```

Since 9475<2^14, 28416<2^15 and q>2^80,

```text
ceil(log_q S_d) <= 4096wd + ceil((14+15d)/80).             (1)
```

The strict upper inequality before taking ceilings makes this valid even
when (14+15d)/80 is integral. All logarithms in this proof are mathematical
notation. The replays use integer inequalities only.

## 2. Four complete finite intervals

For 245767<=e<2^20, 1<e^17<2^340<2^10000, so w=2 exactly. Direct rounding
then gives n(U)=floor((e+2)/4). The least width of depth at least d obeys

```text
a_1=64, a_(d+1)=64 ceil(a_d/42).
```

Indeed, D(n)>=d+1 iff 42 floor(n/64)>=a_d. In particular,

```text
a_15=49280, a_16=75136, a_17=114496,
a_18=174528, a_19=265984.
```

Therefore n(U) has the following depths. Equation (1) gives the displayed
upper requirement L. A positive first-e minus 2L means L<e/2 throughout
that interval, and hence L<=U.

| e, inclusive | D(n(U)) | L | First e minus 2L |
| --- | ---: | ---: | ---: |
| 245767 to 300541 | 15 | 122883 | 1 |
| 300542 to 457981 | 16 | 131076 | 38390 |
| 457982 to 698109 | 17 | 139268 | 179446 |
| 698110 to 1048575 | 18 | 147460 | 403190 |

The first body has 61442 atoms, and all later bodies are larger. Thus U is
legal and covers its stock on all four intervals. No prime approximation or
unproved monotonicity of the ratio k/e across depth jumps is used.

## 3. Infinite tail, including every later atom-width jump

We reuse the dyadic method of Aakash's original-width stock theorem, with
the changed coefficient C_d and the body at U. Since 2*42^2<64^2, two active
steps more than halve the width. Thus D(n)<=2 ceil(log2 n) for n>=2.
For d>=1, (14+15d)/80<=29d/80<d, so

```text
log_q S_d < 4097wd.
```

For e>=2^20 put j=floor(log2 e)>=20. Then d=D(n(U))<=2(j+1) and
w<=2e^(17/10000)<2*2^((17/10000)(j+1)). Consequently

```text
ceil(log_q S_d) <= B_j+1,
B_j=16388(j+1)2^((17/10000)(j+1)).
```

At j=20, 21*17/10000<1/2 and sqrt(2)<3/2 imply

```text
B_20+1 < 16388*21*(3/2)+1 = 516223 < 524288 = 2^19.
```

The ratio of successive normalized B terms is

```text
(B_(j+1)/2^j)/(B_j/2^(j-1))
 = ((j+2)/(j+1))*2^(17/10000)/2
 < (22/21)*(3/4) = 11/14 < 1.
```

The normalized additional one contracts by 1/2, also at most 11/14. Induction
therefore gives B_j+1<2^(j-1)<=e/2 for every j>=20. The required integer
borrowing is at most U.

It remains to check that U leaves an internal body, rather than assume it.
Since e-U>e/2 and w<=2e^(17/10000),

```text
n(U) > e/(2w)-1 >= e^(1-17/10000)/4-1 > sqrt(e)/4-1 >= 255.
```

This exceeds 64. The tail plan is legal. This proof handles every future
ceiling jump of w and every depth jump, without a finite-width replay being
used as evidence for an infinite quantifier.

## 4. Sharp failure for both predicates

Set e*=245766. The exact width is w=2. The largest legal borrowing is
U=122882 and its body has n(U)=61442, of depth 15. Every smaller borrowing
has a body of depth at least 15.

Use Aakash's certified prime q*=213*2^80+1=257501199577916014212415489.
The replay checks the exact modular identity

```text
7^((q*-1)/2) mod q* = q*-1,
(2^80+1)^2 > q*.
```

For completeness, if a prime p divides q*, then 7 is a unit modulo p and
its order divides 213*2^80 but not 213*2^79. Hence 2^80 divides p-1,
so p>=2^80+1>sqrt(q*). A composite integer has a prime divisor no greater
than its square root. This proves primality without a probable-prime test.

The product bound product(1-x_i)>=1-sum(x_i), the geometric series and
Bernoulli's inequality give

```text
P(q*) > 1-1/(q*-1),
P(q*)^15 > 1-15/(q*-1) > 1/2.
```

For the exact integer C_15=9475*28416^15, the replay checks

```text
4(q*)^2 < C_15 < (q*)^3.
```

As 4096*2*15=122880, these inequalities imply

```text
2(q*)^122882 < S_15 < (q*)^122883.
```

Thus even the weaker strict-volume predicate fails at U. For every k<=U,
S_D(n(k))>=S_15>2(q*)^U>=2(q*)^k. Neither predicate admits a plan. Every
proposed smaller universal cutoff includes e*, proving sharpness of 245767
for both. This does not claim every smaller e fails for every prime.

## 5. What changed and what remains conditional

PR3486 already proves least actual-body covering selection. PR3523 supplies
the encoded strict-volume selector; PR3503 supplies its padding equivalence.
This result adds a universal sharp fit cutoff, not another selector. The
distinct original-width theorem at 311311 uses
(269241600*N*q^(4096(w-1)))^D(e). Its sharpness statement remains correct
for that prescribed stock. No theorem about that unchanged stock is replaced.

PR3246 and Tekalign's PR3264 justify the smaller one-factor NODE reserve under
completed-child and fresh-row premises. Applying the arithmetic theorem to
the real two-return caller retains every such premise, the genuine other
high field, immediate restriction, all paid preparation/children/cleanup,
full-cover, selected coefficients, routing, frame, precision/tape and outer
transfer obligations. Neither physical GL64 execution nor a supplier theorem
follows from fit. Independent human and formal proof-kernel review are unclaimed.
