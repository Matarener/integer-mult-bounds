# A shape-sensitive lower bound for mixed negative Q8 targets

## Model and inherited identities

Work in the full formal algebra `F2[Q8]`, with distinct basis elements
`1,z,i,zi,j,zj,ij,zij` and relations

```text
i^2 = j^2 = z,  z^2 = 1,  ji = z ij.
```

Every scalar role starts with independent arbitrary dirty input. Free
operations are binary scalar GL changes of basis. Each paid call has the
normalized form

```text
D_l = I + (1 + [g_l]) u_l v_l^T,
g_l in {i,j},  u_l,v_l binary,  v_l^T u_l = 1.
```

The endpoint is diagonal, with `t_i` copies of `[zi]`, `t_j` copies of `[zj]`
and identity on all other roles. Put `t=t_i+t_j>0` and `n=n_i+n_j`.
Every extra dirty role must restore. The role count is any finite integer.

We use the chronological identities of Nick Petalas's PR3578 and PR3589
as premises, rather than independently re-certifying those packages. Let
X contain call columns u_l and Y contain call rows v_l^T. Form L as the
strictly lower triangular part of the FULL-role YX before restricting X
and Y to active output and input coordinates. Group call coordinates by
label, preserving chronological order inside each group. Write

```text
X = (X_i X_j),  Y = (Y_i; Y_j),
K_i = I + L_ii,  K_j = I + L_jj.
```

Both K_i and K_j are invertible. The first-order equations are

```text
X_i Y_i = P_i,  X_j Y_j = P_j,  XY = I_t,
rank(P_i)=t_i,  rank(P_j)=t_j.
```

The two quadratic orientations give

```text
X_i K_i Y_i + X_j(L_ji Y_i + K_j Y_j) = 0,                 (Q)
X_i K_i Y_i + (X_i L_ij + X_j K_j)Y_j = 0.                (Q')
```

These equations also hold for mixed targets: the endpoint's first-order
sum and its tau coefficient are both I_t. The derivation of Q and Q'
uses this sum, not the homogeneous extra premise X_jY_j=0. Equivalently,
they are the two equations X(I+H)Y=0 in PR3589, expanded by label blocks.
Swapping i and j gives the reverse equations. PR3589's cubic argument gives

```text
rank(X_i), rank(Y_i), rank(X_j), rank(Y_j) >= 3t-n.         (C)
```

The first-order equations also imply `n_g>=t_g` and the trace parities
`n_i=t_i mod 2`, `n_j=t_j mod 2`. PR3736 records those block floors and
the previous necessary-count region. All ranks here are binary ranks.

## The new quadratic inequalities

Set a=rank(X_j) and b=rank(Y_j). Rank-nullity for X_jY_j=P_j gives

```text
a+b <= n_j+t_j.                                          (1)
```

Since rank(X_i),rank(Y_i)>=t_i and K_i is invertible, Sylvester gives

```text
rank(X_i K_i Y_i) >= 2t_i-n_i.
```

Equation Q bounds this rank by a; equation Q' bounds it by b. These
bounds remain valid when the right side is negative. Therefore

```text
4t_i-2n_i <= a+b <= n_j+t_j,
2n_i+n_j >= 4t_i-t_j.                                    (2)
```

Exchanging labels proves the companion inequality. Thus every exact word
satisfies the new pair

```text
2n_i+n_j >= 4t_i-t_j,
n_i+2n_j >= 4t_j-t_i.                                    (3)
```

For t_j=0 this recovers the homogeneous quadratic inequality of PR3578.
The new content is its mixed-target correction term and its combination
with the mixed cubic ranks. In particular, replacing n_j+t_j in (1) by
n_j would be unsound; the nonzero product P_j has to remain charged.

## Shape-sensitive total counts

The cubic ranks C and rank-nullity give the inherited inequalities

```text
2n+n_i >= 6t-t_i,  2n+n_j >= 6t-t_j.                      (4)
```

Add the second inequality of (4) to the first inequality of (3), written
as `2n-n_j >= 4t_i-t_j`. This gives

```text
4n >= 6t+4t_i-2t_j = 10t_i+4t_j.
```

Swapping labels and retaining PR3589's sum bound proves

```text
n >= max(11(t_i+t_j)/5, (5t_i+2t_j)/2, (2t_i+5t_j)/2).     (5)
```

The first term is inherited. The other terms improve it exactly when
one target multiplicity is greater than four times the other. Consequently
attainment of the real-valued 11t/5 bound requires
`t_i <= 4t_j` and `t_j <= 4t_i`. This is a restriction on the possible
equality shapes, not a construction at any of the remaining shapes.

## Exact projection of this necessary-count region

Consider ONLY the following arithmetic relaxation: nonnegative integer
n_i,n_j, the block floors, the two trace parities, the two inherited cubic
count inequalities (4), and the two new quadratic inequalities (3).
Its exact minimum is

```text
N(t_i,t_j) = t + 2 max(ceil(3t/5), ceil(3t_i/4), ceil(3t_j/4)).           (6)
```

This is not asserted to be a realizable word length. To prove (6), write

```text
n_i=t_i+2a,  n_j=t_j+2b,  s=a+b,  a,b nonnegative integers.
```

The four inequalities become

```text
3a+2b >= t_i+2t_j,  2a+3b >= 2t_i+t_j,
2a+b >= t_i-t_j,    a+2b >= t_j-t_i.
```

For fixed integer s, a is allowed exactly when

```text
max(0, t_i+2t_j-2s, t_i-t_j-s)
 <= a <=
min(s, 3s-2t_i-t_j, 2s+t_i-t_j).                         (7)
```

Both endpoints are integers. Comparing the three lower endpoints with
the three upper endpoints gives exactly

```text
s >= 0,
3s >= 2t_i+t_j,  3s >= t_i+2t_j,
2s >= t_i-t_j,   2s >= t_j-t_i,
5s >= 3t,       4s >= 3t_i,  4s >= 3t_j.
```

The ninth comparison repeats s>=0. The last three inequalities imply
all earlier ones. For example, 5s>=3t and 4s>=3t_i imply

```text
s >= (5/9)(3t/5) + (4/9)(3t_i/4) = (2t_i+t_j)/3.
```

The other three-fold bound follows by symmetry. Also
`3t_i/4 >= (t_i-t_j)/2` for nonnegative multiplicities, and likewise
after swapping labels. Hence (7) is nonempty exactly when

```text
s >= max(ceil(3t/5), ceil(3t_i/4), ceil(3t_j/4)).
```

Choosing the lower endpoint in (7) explicitly supplies integer a,b in
this arithmetic relaxation. This proves both necessity and sufficiency
for that relaxation and establishes (6), including parity.

## A strict improvement and an infinite excluded family

At shape `(t_i,t_j)=(7,1)`, the old mixed cubic/floor/parity region
admits `(n_i,n_j)=(7,11)`, total 18. The new first quadratic inequality
would require `25>=27`, so that pair is impossible. Formula (6) gives
N(7,1)=20, attained within the relaxation by `(n_i,n_j)=(7,13)`.
An actual 20-call word is not supplied. The direct word costs 24.

More generally, for every positive integer k, shape `(7k,k)` and counts
`(7k,11k)` satisfy every old mixed cubic/floor/parity condition, but violate
the new quadratic inequality `25k>=27k`. Also every actual word at that
shape has `n>=37k/2`; parity strengthens this to
`n>=8k+2 ceil(21k/4)`. Thus the improvement is not confined to a finite
search domain. No universal 5t/2 mixed-target bound is asserted.

The relaxation is still insufficient: at shape (2,1), (6) gives seven,
while PR3536's separate full-algebra result gives the actual minimum nine.
That earlier minimum is cited, not independently replayed here. In
particular the four-target ten-versus-twelve questions are unchanged.

## Evidence, limits and credit

The proof above is a scoped mathematical argument using PR3578/PR3589's
chronological equations as inherited premises. Its new step is the
mixed quadratic rank charge, followed by the exact integer projection.
The verifier corroborates the projection by exhaustive bounded integer
enumeration and checks full formal direct words as positive controls.
Its generic binary rank fixtures test the new rank inference; they are
not endpoint realizations. The emitted receipt binds all package and
declared input bytes by SHA256. No receipt is written by hand.

Produced by Nick Petalas. Nick Petalas's PR3570, PR3578, PR3589 and PR3736
retain credit for the cubic identities, homogeneous method, mixed ranks
and previous count region. Their retained lineage includes PR3536 and
PR3558's chronological and cyclic methods, PR3517's normalization,
Tuafo/PR2900, ywz65/PR2587, PR3487, Aaron Wang/PR2318, Cinna Davis,
steph4n-gh and the credited Q8/register sources. Standard rank inequalities
are not claimed as new. Exact source pins appear in SOURCES.json.

Independent human and formal proof-kernel review are unclaimed. No actual
shorter word, physical caller, scalar/routing/hosting/precision invoice,
supplier admission, multiplication theorem or new kappa is supplied.
The selected frontier is unchanged. The selected full cold replay, Lean
and Docker builds were not run because this result changes none of them.

## Open next questions

- Can any imbalanced shape attain (6) as a full eight-coefficient endpoint?
  Start at (7,1), where the new bound is 20 and direct execution costs 24.
  Count fixtures alone cannot answer this question.
- Does equality in both rank charges impose a further obstruction? Start
  at the simultaneous quadratic/cubic equalities on the real boundary
  t_i=4t_j, retaining the same chronological L in both orientations.
- Any formal saving still needs a matched physical caller and complete
  invoice. No such caller is identified by the count theorem.
