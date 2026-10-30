# Exact counts of optimal unsigned one-source words

## Model and statement

Let R be a nonzero unital ring of exact finite characteristic m >= 2. Let
X, Z and Y be left R-modules, and let B: X -> Z and A: Z -> Y be arbitrary
compatible R-linear maps. The three distinct data roles x, z and y may be
arbitrarily dirty. The only paid calls are

```text
B: z += Bx
A: y += Az
```

Calls are complete, source-preserving additive implementations, with their own
private state restored and their heads returned. Every call includes its full
implementation price. No inverse, sign change, scalar multiplier, frame change,
copy, direct AB call, source mutation, or additional connector is free. The
word is independent of input contents, and y is observed only after completion.
Correctness is universal in the maps and modules. Additional relations in a
particular choice of maps can permit shorter specialized words.

For c in {1,...,m-1}, the target is y += c ABx with x and z unchanged. The
minimum length is 2m. Write N_m(c) for the number of distinct literal words
attaining this minimum. Define N_m(0) as an auxiliary count over **balanced**
words with exactly m A events and m B events. It is not the optimum-word
count for the zero target, whose optimum is the empty word.

Let mu be the Mobius function and define the integer Ramanujan sum

```text
R_d(c) = sum_{e | gcd(d,c)} e mu(d/e).
```

Then, for every m >= 2 and every 0 <= c < m,

```text
N_m(c) = (1/m) sum_{d | m} R_d(c) binom(2m/d, m/d).                 (1)
```

For nonzero c this is the complete optimal-word count. The complete number of
restored length-2m words for the zero target is N_m(0)+2, adding A^(2m) and
B^(2m). The number for each other target is unchanged.

If p is prime, (1) reduces to

```text
N_p(0) = [binom(2p,p) + 2(p-1)]/p,
N_p(c) = [binom(2p,p) - 2]/p,             1 <= c < p.              (2)
```

The nonzero target coefficients have equal optimal-word counts **if and only
if m is prime**. For any m, N_m(c) depends only on gcd(m,c); in particular all
unit coefficients have the same count. Reversing a word changes c to -c and
gives an unsigned inverse of the same length.

This is a scoped proof in the complete-call interface. The finite verifier is
corroboration of the proof, not its all-characteristic justification.

## 1. Dirty-state reduction and optimal length

For a word w, let a and b be its A and B counts. Let I(w) be the number of
ordered event pairs in which B occurs before A. Straight-line substitution
gives the exact action

```text
x_final = x,
z_final = z + b Bx,
y_final = y + a Az + I(w) ABx.
```

No commutation of A and B is used. Their order is AB because B writes z and
A reads z. Universal correctness forces b = 0 mod m to restore z and a = 0
mod m to cancel arbitrary connector dirt. To see necessity, take X=Y=Z=R,
use identity maps, and vary x and z independently. Exact characteristic m
means k*1_R=0 exactly when m divides k.

For nonzero c, both operators must occur. Thus a,b >= m and the total length
is at least 2m. The literal word

```text
B^c A B^(m-c) A^(m-1)
```

has a=b=m and I(w)=c mod m. It attains the bound. Every length-2m word for
nonzero c must therefore have a=b=m, and it realizes c exactly when I(w)=c
mod m. This also gives the minimum fixed-price bill m(c_A+c_B) for any positive
complete-call prices c_A,c_B. The count theorem, rather than this elementary
minimum-length extension of the F3 argument, is the contribution here.

For a balanced word, reversing the event order exchanges before and after in
all m^2 B/A pairs. Hence I(reverse(w))=m^2-I(w)=-I(w) mod m. This proves the
inverse statement without granting a free signed call.

## 2. The coefficient is a subset-position statistic

Choose the m positions of A in {0,...,2m-1}, written s_1<...<s_m. Before the
jth A, there are s_j earlier events and j-1 of them are A. Consequently

```text
I(w) = sum_j [s_j-(j-1)] = sum_j s_j - m(m-1)/2.                  (3)
```

Each m-element position subset determines exactly one balanced word. In
particular sum_c N_m(c)=binom(2m,m). The shift in (3) cannot be dropped in
even characteristic.

## 3. Exact root-of-unity transform

Fix a divisor d of m, and a primitive complex dth root zeta. Complex roots
are only a finite counting device; they impose no assumption on R. By (3),
with t=m(m-1)/2,

```text
sum_w zeta^I(w)
  = zeta^(-t) [u^m] product_{s=0}^{2m-1} (1 + u zeta^s)
  = zeta^(-t) [u^m] [1-(-u)^d]^(2m/d)
  = zeta^(-t) (-1)^((d+1)m/d) binom(2m/d,m/d).                  (4)
```

The product identity follows because each dth root occurs 2m/d times and
product_{s=0}^{d-1}(1+u zeta^s)=1-(-u)^d.

The phase and sign in (4) cancel. If d is odd, d divides t because d divides
m and 2 is invertible modulo d. Thus zeta^(-t)=1, and d+1 is even. If d is
even, m is even, zeta^(d/2)=-1 and

```text
zeta^(-t) = (-1)^((m/d)(m-1)) = (-1)^(m/d).
```

Since d+1 is odd, the other sign is also (-1)^(m/d). Therefore

```text
sum_w zeta^I(w) = binom(2m/d,m/d).                              (5)
```

This includes d=1, which gives the total number of balanced words.

## 4. Fourier inversion gives the divisor formula

Let omega be a primitive mth root. The elementary finite geometric sum gives

```text
1_{I=c mod m} = (1/m) sum_{k=0}^{m-1} omega^(k(I-c)).
```

Sum over balanced words and use (5). Group k by the exact order d of omega^k.
The resulting sum of primitive dth roots to the power -c is R_d(c).
For completeness its integer form follows from inclusion-exclusion. If

```text
S_d(c) = sum_{zeta primitive of order d} zeta^(-c),
```

then sum_{e|d} S_e(c) is the sum of all dth roots to the power -c. This is d
if d divides c and zero otherwise. Mobius inversion yields

```text
S_d(c) = sum_{e|d} mu(d/e) e 1_{e|c}
       = sum_{e|gcd(d,c)} e mu(d/e) = R_d(c).
```

This proves (1). No census or numerical complex arithmetic is needed.

## 5. Exactly the primes have uniform nonzero counts

When m=p is prime, its divisors are 1,p. R_p(0)=p-1 and R_p(c)=-1 for
nonzero c, while binom(2,1)=2. This proves (2).

Conversely suppose all N_m(c) for c!=0 were a common value b. Their Fourier
transform at any nontrivial mth root would then be N_m(0)-b, because the sum
of the nontrivial powers of that root over the residues is -1. It would be
independent of the root's order. If m is composite, choose a proper prime
divisor p of m. Equation (5) at order m gives 2; at order p it gives
binom(2m/p,m/p)>2 since m/p>=2. Both roots are nontrivial, a contradiction.
Thus uniformity holds exactly for prime m.

Finally gcd(m,c) determines gcd(d,c) for every divisor d of m, so (1) proves
the asserted gcd dependence. This gives N_m(c)=N_m(-c) as also witnessed by
word reversal.
