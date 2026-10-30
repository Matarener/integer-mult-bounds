# A fifth rational frame never saves a call: the minimum is eight for every rational t

**Scoped proof in a formal register model, with a finite exact check. No
selected supplier or new κ is claimed.**

## Result

Take the four-role target of
[PR #2085](https://github.com/CrocSwap/integer-mult-bounds/pull/2085),

$$
T=\operatorname{diag}([A+P],[A+Q],[B+P],[B+Q]),
$$

with $A=E_{11}$, $B=E_{22}$, $P=\tfrac12\begin{pmatrix}1&1\\1&1\end{pmatrix}$
and $Q=A+B-P$. A paid call is $I_4+([F]-1)N$ with $N$ any of the 120 rank-one
idempotents in $M_4(\mathbb F_2)$, and free role mixing is allowed. Add the
fifth rational rank-one address

$$
R_t=(1,t)^T(1,t)=\begin{pmatrix}1&t\\t&t^2\end{pmatrix},\qquad t\in\mathbb Q .
$$

**Theorem.** For every rational $t$, every word over $\{A,B,P,Q,R_t\}$ that
equals $T$ in $M_4(\mathbb F_2[\Lambda_t])$, $\Lambda_t=\mathbb ZA+\mathbb ZB+\mathbb ZP+\mathbb ZR_t$,
has at least eight calls. The direct eight-call word attains this, so the
exact minimum is eight.

For $t=1/2$ this settles the seven-call case that
[PR #2112](https://github.com/CrocSwap/integer-mult-bounds/pull/2112) left
open: its bound $7\le\min\le8$ becomes $\min=8$. It also answers the family
question in #2085's open-next-questions for the whole slope family $R_t$.

## Proof

Coordinates. Write a symmetric matrix $\begin{pmatrix}a&c\\c&b\end{pmatrix}$ as
$(a-c)A+(b-c)B+2cP$. Then $R_t=(1-t)A+(t^2-t)B+2tP$, and the four target
frames are $A+P$, $2A+B-P$, $B+P$ and $A+2B-P$.

**Step 1 (exponent support).** Over $\mathbb F_2$,
$I+([F]-1)N=(I+N)+[F]N$. Expanding a product of $k$ such factors gives a sum
over subsets $S$ of calls of $[\sum_{j\in S}F_j]$ times a binary matrix. The
group elements $[x]$ are a basis of $\mathbb F_2[\Lambda_t]$, so the diagonal
entry $[C_i]$ of $T$ forces $C_i=\sum_F n_FF$ with $0\le n_F\le k_F$, where
$k_F$ is the number of calls with label $F$. This is an equality of rational
matrices, not a congruence.

With $n_R=0$ each target has exactly one such representation:
$A+P$, $A+Q$, $B+P$, $B+Q$. With $n_R\ge1$, the $P$-coordinate equation
$n_P-n_Q+2n_Rt=c_P$ fixes $t$. Enumerating every $n$ with $\sum n_F\le7$ shows
that the only rational $t$ admitting such a representation is $t=0$, where
$R_0=A$. Hence, for $t\ne0$, a word with at most seven calls uses each of
$A,B,P,Q$ at least once.

**Step 2 (first order).** Let $L$ be a lattice containing all labels and
targets. Modulo the square of the augmentation ideal, a word equal to $T$
satisfies $\sum_F S_F\otimes\bar F=\sum_iE_{ii}\otimes\bar C_i$ in
$M_4(\mathbb F_2)\otimes L/2L$, where $S_F$ is the sum of the idempotents on
calls labelled $F$. A sum of $k$ rank-one idempotents has rank at most $k$ and
trace $k\bmod2$; write $f(S)$ for the resulting floor. This is the method of
#2085 and #2112.

**Step 3 (lattice by denominator parity).** Let $t=p/q$ in lowest terms. The
coordinate $t^2-t=p(p-q)/q^2$ has exact denominator $q^2$, so
$\Lambda_t/\Lambda$ is cyclic of order $q^2$, with $\Lambda=\mathbb ZA+\mathbb ZB+\mathbb ZP$.

- *$q$ odd.* The index is odd, so $\Lambda/2\Lambda\to\Lambda_t/2\Lambda_t$ is
  an isomorphism. Two-adically $1-t\equiv1+p$, $t^2-t\equiv0$ and $2t\equiv0$,
  so $R_t\equiv A$ ($p$ even) or $R_t\equiv0$ ($p$ odd). In the first case the
  calls labelled $A$ or $R_t$ together sum to the old $S_A$; in the second,
  $R_t$ calls add cost without first-order effect. Either way the floor is the
  #2085 floor $\min_S f(S)+f(S+P_A)+f(S+P_B)+f(S+I)=8$, with
  $P_A=\operatorname{diag}(1,0,0,1)$ and $P_B=\operatorname{diag}(0,1,1,0)$.
  This case needs no support argument and holds for every word length.
- *$q$ even.* The two-part of $\Lambda_t/\Lambda$ is cyclic and nontrivial, so
  $\Lambda/2\Lambda\to\Lambda_t/2\Lambda_t$ has a one-dimensional kernel. The
  kernel is spanned by $q^2R_t\bmod 2\Lambda$, whose $B$-coordinate $p(p-q)$ is
  odd and whose other coordinates are even: $B\in2\Lambda_t$. So $A,P,R_t$
  give a basis of $\Lambda_t/2\Lambda_t$, $Q\equiv A+P$, and the targets reduce
  to $A+P$, $P$, $P$, $A+P$. A word that uses no $R_t$ lies in
  $\mathbb F_2[\Lambda]$ and has the #2085 floor of eight. A word that uses
  $R_t$ has $S_{R}=0$, so an even number $k_R\ge2$ of $R_t$ calls. By Step 1
  it also has $k_B\ge1$ and $k_A,k_P,k_Q\ge1$. With $g(S)=f(S)$ when $f(S)>0$
  and $g(0)=2$,
  $$k_A+k_P+k_Q\ge\min_Sg(S)+g(S+P_A)+g(S+I)=5,$$
  so $k\ge5+2+1=8$.

The case $t=0$ has odd denominator. This proves the theorem.

The verifier recomputes every finite input:

- both first-order minima over all 65,536 masks;
- the support enumeration over all rational $t$;
- the 120 idempotents, each of rank one and trace one;
- the parity classification of $\Lambda_t/2\Lambda_t$ on all 1,431 reduced
  $t=p/q$ with $q\le24$ and $|p|\le48$. This is a check on the general
  argument above, not its proof.

It also multiplies the direct eight-call word exactly in the group algebra.
Two controls must fail: dropping one call, and dropping the $P$-bits of roles
2 and 3 from the even-case mask, which lowers that floor from five to three.

## What is new and what is reused

The model, target, rank/trace floor and the $t=1/2$ lattice come from Cinna
Davis's #2085 and #2112. #2112 excludes six calls at $t=1/2$ by enumerating
388,800 words; this package does not repeat or check that enumeration. The
new parts are the exponent-support step, which forces a $B$ call that the
first-order relaxation cannot see, the resulting seven-call exclusion, and the
reduction of every rational slope to the two denominator-parity cases.
Expanding a product of such factors over subsets of calls is elementary and
is not claimed as a new technique.

## Scope

This is a scoped proof in the formal paid-call model above: all word lengths
for odd-denominator $t$, and all words of at most seven calls for even
denominators (enough for the exact minimum). It does not cover other rank-one
addresses such as scalar multiples $cR_t$, two or more added frames, other
targets, frame construction, addition, precision, or interface charges. It
gives no supplier mapping and no κ change. Python 3.12 is the registered
runtime. The general lattice argument is a hand proof checked on a finite grid,
not a proof-assistant verification.

## Reproduce

From the repository root:

```sh
python3.12 -I -B research/bit-fifth-rational-frame-every-rational-t/verify.py
python3.12 -B scripts/research_package.py --package research/bit-fifth-rational-frame-every-rational-t
```

Expected line (under a second):

```text
PASS_FIFTH_RATIONAL_FRAME_EVERY_T_EXACT_MINIMUM_8 grid_odd=949 grid_even=482 support_exceptions=['0'] idempotents=120 odd_floor=8 even_visible_floor=5 even_total=8 mutated_visible_floor=3 direct_calls=8
```

## Open next questions

- **Scaled and two-frame alphabets.** Does any rational rank-one address
  $c\,v^Tv$ in the symmetric span, or any pair of added frames, lower eight?
  The support step still applies. The first step is to classify which
  addresses can enter a target's exponent support with at most seven calls.
  Only those can matter beyond the first-order floor.
- **Support-plus-first-order as a general screen.** The support step is
  valid for any torsion-free address alphabet. Combining it with the
  first-order floor may decide other open minimum-length cases in this model
  family without enumerating words. The blocker is targets whose supports are
  not unique.

## Credit

Produced by Nick Petalas. The model, target, rank/trace floor and the
$t=1/2$ instance are Cinna Davis's (1337isnot1337) #2085 and #2112, cited
above and pinned in [SOURCES.json](SOURCES.json). New work is Apache-2.0.
