# Exact dyadic attainment of the P104 spectral correction ranks

New construction and proof: AAAmirinu, with substantial OpenAI Codex
assistance. Apache-2.0. This is a scoped algebraic proof, not a physical
supplier or a new kappa.

## Sources, contract and theorem

Nick Petalas's [PR6181](https://github.com/CrocSwap/integer-mult-bounds/pull/6181),
head `65704df0ff4e7cad336694d39ff3492df48e0c04`, proves stable lower bounds
for the complete two-stage P104 Gram operator: correction rank at least 832,
and at least 1664 when both spectral coefficients vanish modulo 13. Its
sharpness construction is over F13; its exact Gaussian-dyadic attainment
question is explicitly open. Those lower bounds retain their attribution.

Chris R / Clear1nsight's
[PR3979](https://github.com/CrocSwap/integer-mult-bounds/pull/3979), head
`a8a1d744811cd7d1f9c43ec7ccbae85ef9695b61`, supplies the stronger explicit
congruence used here. Its P104 coordinates and the retained P104/native/caller
lineage keep their attribution. The new step is a different common code and
its exact additive endpoint correction, not a reconstruction of the original
native-channel proof or its physical invoice. Tensor identities, rank
inequalities and reduction of minors are classical linear algebra.

Let R = Z[i,1/2] and let K = Q(i). Matrix ranks without a specified field
mean ranks over K. Transpose is ordinary transpose, not conjugate transpose.
All P104 matrices used below are in fact real dyadic matrices. Put n = 104,
r = 8 and P = diag(I_r,0). The retained congruence is

```text
U = [ I_r  W ],       U^-1 = [ I_r  -W ],       W W^t = 12 I_r,
    [  0   I ]              [  0    I ]

A = U^t P U,         M = U U^t,                 det U = det M = 1.
```

Here W is the retained 8-by-96 signed-half matrix. In particular A^2 = 13A,
rank_K A = r, and U and its inverse belong to GL_n(R). These are stronger
source premises than the abstract square-zero reduction alone used for the
lower bound. This proof uses this explicit congruence; it does not claim
that every matrix satisfying only A^2 = 13A has it.

On two n^2-coordinate data banks set

```text
B = A tensor I_n,        C = I_n tensor A,
P_r = P tensor I_n,      P_c = I_n tensor P,

F = upper(-C) lower(B) = [ I-CB  -C ],
                           [ B      I ]

T(alpha,beta) = upper(-alpha P_c) lower(beta P_r)
              = [ I-169 P_c P_r  -alpha P_c ],
                [ beta P_r            I    ]
alpha beta = 169.
```

The lower shear is applied first. An allowed code is one common
Q in GL_(2n^2+h)(R), used at both endpoints, with any finite h >= 0
independent dirty scratch coordinates returned identically. Thus the
correction being measured is

```text
Q (F direct-sum I_h) Q^-1 - (T(alpha,beta) direct-sum I_h).
```

**Theorem.** For the retained P104 congruence, the exact minimum correction
rank is 832 for (alpha,beta) = (1,169), and 1664 for (alpha,beta) = (13,13).
One explicit determinant-one R-valued code attains both minima with h = 0.
The lower bounds even allow arbitrary joint-bank codes and finite returned
scratch, as proved in PR6181. The upper bounds below require neither scratch
nor joint-bank mixing. No assertion of attainment for every other permitted
coefficient pair is needed or made.

## One common Gaussian-dyadic code

Write U^-t for (U^-1)^t and define

```text
X = U^-t tensor U^-t,       X^-1 = U^t tensor U^t,
Y = U^-t tensor U,          Y^-1 = U^t tensor U^-1,
Q = diag(X,Y),              Q^-1 = diag(X^-1,Y^-1).
```

All displayed matrices and inverses have entries in R. The tensor determinant
identity and det U = 1 give det X = det Y = det Q = 1. The same Q is used for
both shears; no change of code at their internal boundary is introduced.

The ordered tensor calculations are

```text
X C Y^-1
  = (U^-t I_n U^t) tensor (U^-t A U^-1)
  = I_n tensor P = P_c,

Y B X^-1
  = (U^-t A U^t) tensor (U U^t)
  = (P M) tensor M =: L.
```

In the second identity U^-t A U^t = P U U^t = PM, using A = U^t P U.
There is no interchange of noncommuting factors. Consequently

```text
Q F Q^-1 = upper(-P_c) lower(L) = [ I-P_c L  -P_c ],
                                           [    L       I   ]

L = P_r (M tensor M),        P_r L = L.
```

This code normalizes the upper shear and retains the lower coupling L.
The nonzero corrections below are essential: this is not a free simultaneous
spectral normalization and does not contradict either predecessor obstruction.

## Asymmetric target: exact rank 832

Take alpha = 1 and beta = 169 and put

```text
D = L - 169 P_r = P_r (M tensor M - 169 I_(n^2)).
```

Subtracting the complete target, including its product term, gives

```text
E_asym = Q F Q^-1 - T(1,169) = [ -P_c D  0 ].
                                         [    D     0 ]
```

The map v -> (-P_c v,v) is injective, so rank E_asym = rank D. The factor P_r
on the left of D places its image in im P_r, yielding rank D <= nr = 832.

For a matching lower bound on this explicit D, reduce R into F13 by i -> 5
and 1/2 -> 7, and denote reduction with a bar. The inverse of M reduces too,
so M-bar tensor M-bar is invertible. Since 169 reduces to zero,

```text
D-bar = P_r (M-bar tensor M-bar),       rank_F13 D-bar = nr.
```

A nonzero nr-by-nr minor after reduction comes from a nonzero minor over K.
Therefore rank_K D >= nr, and both inequalities give rank E_asym = 832.
PR6181 supplies the matching lower bound for every allowed common code and
every finite returned scratch extension. Our explicit code therefore attains
the stable global minimum in this endpoint-rank problem.

## Balanced target: the same code attains exact rank 1664

Take alpha = beta = 13. Direct subtraction, without modifying Q, gives

```text
E_bal = Q F Q^-1 - T(13,13)
      = [ -P_c L + 169 P_c P_r    12 P_c ].
        [       L - 13 P_r           0   ]
```

The whole upper output lies in im P_c, and the whole lower output lies in
im P_r. Each space has dimension nr, in its own bank. Hence

```text
rank_K E_bal <= dim(im P_c direct-sum im P_r) = 2nr = 1664.
```

For completeness, this explicit upper bound has the following direct lower
bound after reduction:

```text
E_bal-bar = [ -P_c L-bar  -P_c ],
            [    L-bar      0  ]

L-bar = P_r (M-bar tensor M-bar),       rank_F13 L-bar = nr.
```

The equation E_bal-bar (x,y) = 0 first forces L-bar x = 0 from its lower
bank, and then forces P_c y = 0 from its upper bank. Conversely these two
conditions suffice. Thus its kernel is ker L-bar direct-sum ker P_c,
of dimension 2(n^2-nr). Its rank is 2nr. Lifting a nonzero minor proves
rank_K E_bal >= 2nr, so the exact rank is 1664.

This also agrees with the stronger lower bound from PR6181: both target
coefficients vanish modulo 13, so the reduced target is the identity and
the reduced source minus identity has rank 2nr. That predecessor already
proves this lower bound for every allowed common code and stable extension.
The construction here supplies its previously missing exact dyadic attainment.

## Explicit integral lift for the predecessor's smallest example

PR6181 proposes A_0 = [[13,1],[0,0]], n = 2, r = 1 as the first exact lifting
test. This matrix is not the symmetric P104 congruence above. It has its own
direct integer construction, requiring no claim that it has that congruence.
Let P_0 = diag(1,0) and define

```text
H = [ 13  1 ],       H^-1 = [ 0   1 ],       A_0 H^-1 = P_0,
    [  1  0 ]              [ 1 -13 ]

Q_0 = diag(I_4, I_2 tensor H),               det Q_0 = 1.
```

Form F_0, P_r and P_c with this A_0 and n = 2. For alpha = 1, beta = 169,
the same complete-product subtraction yields

```text
Q_0 F_0 Q_0^-1 - T(1,169) = [ -P_c D_0  0 ],
                                      [    D_0     0 ]

D_0 = A_0 tensor H - 169(P_0 tensor I_2)
    = [  0    13  13  1 ]
      [ 13  -169   1  0 ]
      [  0     0   0  0 ]
      [  0     0   0  0 ].
```

The first two rows and last two columns give H, of determinant -1. The other
two rows vanish. Hence rank D_0 = 2, and injectivity of v -> (-P_c v,v)
gives exact correction rank two. Both Q_0 and its inverse are integral;
the forbidden denominator 13 in the predecessor's rational escape is absent.
This is an exact endpoint equality and rank witness, not only a modular lift.

## Scope, verification boundary and next question

Appending Q with I_h gives the same corrections direct-sum zero, so arbitrary
initial scratch is returned exactly. Our attainers already use h = 0. The
proof concerns the complete ordered pair and every independent scalar input;
it neither deletes a payload subspace nor initializes a source to zero.

The universal conclusions follow from the displayed identities, rank arguments
and the retained source premises. Finite exact fixtures can corroborate the
formula and detect a wrong inverse, tensor order, coefficient or product term;
they do not constitute formal proof-kernel acceptance or a replay of the
predecessor's complete scientific pipeline. No independent human review is
claimed. Package verification evidence and its exact scope are recorded in
the accompanying README and generated receipt.

The rank here is the rank of an additive endpoint difference. It is not the
number of native children, paid frame descents or scalar gates. We have not
implemented Q or either correction in the physical P104 charts, priced
coefficient delivery, supplied a chronological owner/restoration schedule,
or completed the identity side channels. No compiler, precision, tape, stock,
outer-theorem or multiplication-theorem obligation is discharged. The selected
#6030 result and its five framework assumptions remain unchanged; no new kappa
or supplier admission is claimed.

The next useful question is whether one of these explicit factored corrections
has a legal physical implementation whose complete cost fits an identified
caller. Begin with its input/output charts and the required reads for one
factor, and account for entry/exit coding, correction, dirty restoration and
the caller's retained identity-side work together. Endpoint rank alone gives
no favorable tariff or permission to omit those costs. Stop physical expansion
if this boundary or complete allowance remains unspecified.
