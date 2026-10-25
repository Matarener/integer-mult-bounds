# Explicit phase tags for the source-defined native lift

## Scope and conventions

Chris R / Clear1nsight's PR3987, scientific head
`fc536202fdaa924158789a5ef59ac079bbe21922`, already proves that the canonical
lift cocycle is an even linear character and supplies the actual inverse
witness with defect `Z_256`. Its source uses the correct adjoint; there is no
author bug to repair. The present addition is an explicit trivialization of
that cocycle, an arbitrary signed-word tag rule and the required compensation
when using the normalized section inside a frame. The representation-theoretic
conjugation below is elementary; it is not claimed as a new general Clifford
construction or as a native compiler modification.

Retain the source's ket convention, binary column matrices and right-to-left
operator composition. For `x in F_2^n`,

```
P_G |x> = |Gx>,       Z_t |x> = (-1)^(t dot x)|x>,
D |x> = i^wt(x)|x>.
```

All matrix operations in binary forms are over F_2; Hamming weights are
ordinary integers, reduced modulo four only in phases. Take any positive n
and any invertible binary G. Define exactly the source's canonical refinement

```
Q_G = I + G^-T G^-1,
q_Q(y) = sum_j Q_jj y_j + 2 sum_(j<k) Q_jk y_j y_k mod4,
K_G |x> = i^q_(Q_G)(Gx) |Gx>.
```

These are ideal exact operators on arbitrary Gaussian-dyadic amplitudes.
No numerical precision, tape, owner, native tariff or all-size admission is
implied by a phase identity.

## The normalization tag

Set `J_G=D P_G D^-1`. Then

```
J_G |x> = i^(wt(Gx)-wt(x)) |Gx>,
J_H J_G = J_(HG),         J_G^adjoint = J_(G^-1).
```

These equalities include global phase, because they follow by cancellation
of the same D factors. This section is generally different from K_G.

For completeness, the difference of their exponents is precisely an even
linear character. Both `q_(Q_G)(Gx)` and `wt(Gx)-wt(x)` have polar form
`2 x^t(G^tG+I)y mod4`. Their parities agree: the diagonal of Q_G is
`j+G^-T j`, where j is the all-ones vector, so its pairing with Gx is
`j dot Gx+j dot x`. Their difference is therefore even, vanishes at zero,
and has zero polar form. Dividing it by two gives a binary linear functional.
Consequently there is a unique input mask t_G with

```
q_(Q_G)(Gx) - wt(Gx) + wt(x) = 2(t_G dot x) mod4,
K_G = J_G Z_(t_G),        J_G = K_G Z_(t_G).
```

Its coefficients require only coordinate inputs:

```
(t_G)_j = [q_(Q_G)(G e_j)-wt(G e_j)+1]_4 / 2,
```

where the bracket is the residue 0 or 2. Binary inversion and these quadratic
evaluations use polynomial work in n, rather than enumerating all 2^n states.
The universal statement follows from the polar/parity argument, not from
sampling the coordinate inputs. All K and J operators fix `|0>` exactly;
there is no unspecified scalar phase in this normalization.

## Cocycle, inverse and arbitrary signed words

Since `Z_t J_G=J_G Z_(G^t t)`, the source cocycle has the explicit form

```
K_H K_G = K_(HG) Z_(ell(G,H)),
ell(G,H) = t_G + G^t t_H + t_(HG).
```

Masks add by XOR. This is the source's already-proved cocycle with a specified
coboundary, not a claim that the canonical K section itself composes strictly.
For the source-defined witness,

```
G = [1,2,8,32,44,128,59,66,489],
G^-1 = [1,2,28,4,79,8,130,32,431],
t_G = 144,      t_(G^-1) = 68,
ell(G,G^-1) = 144 + G^t 68 = 256.
```

Thus the credited witness `K_(G^-1) K_G=Z_256` remains intact. Its exact
inverse rule is

```
K_G^adjoint = Z_(ell(G,G^-1)) K_(G^-1)
            = J_(G^-1) Z_(G^-T t_G).
```

The side of a tag matters; input and output masks are not interchangeable.

For a chronological word `W=K_(G_s)^(epsilon_s)...K_(G_1)^(epsilon_1)`,
with each epsilon either +1 or -1, put

```
H_i = G_i,       d_i=t_(G_i)             if epsilon_i=+1;
H_i = G_i^-1,    d_i=G_i^-T t_(G_i)      if epsilon_i=-1.
```

Starting with `P_0=I,v_0=0`, update in chronological order

```
P_i = H_i P_(i-1),
v_i = v_(i-1) + P_(i-1)^t d_i.
```

Induction using the Z/J commutation rule proves

```
W = J_(P_s) Z_(v_s)
  = K_(P_s) Z_(v_s+t_(P_s)).
```

This is an exact word certificate in the stated K/adjoint alphabet. It does
not normalize arbitrary serialized Clifford recipes, translations or inserted
nonmonomial children without their additional relations. A binary product
alone omits the final mask and need not determine the signed word.

## A frame cannot silently change its lift convention

For the source frame `T=K_B C_[r] K_B^adjoint`, compensation gives

```
T = J_B (Z_(t_B) C_[r] Z_(t_B)) J_B^adjoint.
```

Replacing the middle expression by C_[r] generally changes the intended
native action. To see the exact change, let
`C_u=((1+i)I+(1-i)X_u)/2`, with `X_u|x>=|x+u>`. Then

```
Z_t C_u Z_t = C_u                 if t dot u=0,
Z_t C_u Z_t = i C_u^adjoint       if t dot u=1.
```

The second branch has a necessary global i. For a product of commuting
coordinate C gates, k selected directions therefore contribute i^k and become
adjoints; the other directions remain unchanged. The new independent checker
corroborates both branches on all 512 columns for the witness tag 144 with
u=1 and u=16, rejecting omission of i. These are deliberately constructed
calibration primitives, not a claim that this exact frame or occurrence is
present in the supplier word.

Using J internally is consequently a change of signed-lift convention that
requires retained compensating tags, retagged central children and rebound
interfaces. This package leaves the author's existing correct adjoints and
recipes unchanged. It does not assign a free physical implementation to Z
passes or to their possible fusion with neighboring operations.

## Evidence and remaining obligations

Six unchanged PR3987 exports bind the definitions, recipes and retained
notices. RECIPES.json contains 40 descriptors and exactly four distinct binary
maps in its changed warp-interface subset. This is not the complete PR3945
native inventory. The source's 20,480 full local action comparisons and original
inverse/cocycle results retain their original credit; they are not newly
claimed by extracting these four maps.

The primary checker constructs the tags and word certificates symbolically.
The separate checker imports no primary or predecessor executable. It uses
row/permutation tables, exhaustive permutation inversion and direct weight
phases, checking the four maps and inverses on all 512 states, their 16 ordered
pair products, and every prefix of an eight-gate signed-word fixture. Pair
products and this word are algebraic controls, not asserted chronological
adjacencies in the supplier. It additionally checks all 168 elements of
GL(3,2), all 28,224 ordered pairs on eight states, and 5,376 exact frame columns.
Its compensated frames agree, while 2,688 naive unretagged frame columns
differ. Gaussian numerators are integer pairs with explicit dyadic denominators;
no floating tolerance accepts an equality. These finite checks corroborate the
written arbitrary-dimension and arbitrary-word proof.

No complete native serialization, full emitted-program replay, recipe
replacement, dirty-buffer return, physical scratch/routing/owner/tape bound,
uniform precision theorem, passing supplier invoice, selected frontier update,
human acceptance or proof-kernel verification is claimed. The useful next step
is a separately priced integration of this explicit tag discipline into one
named physical interface, not a free replacement of K by J.

Prepared by ToikY with substantial OpenAI Codex assistance and separate AI
implementation/review contexts. Credit Chris R / Clear1nsight's PR3987,
Dugongue's PR3945/3929, Cinna Davis's PR2226, dataisfire's PR3734 and the full
retained native/compiler/phase/owner lineage in the unchanged notices.
Apache-2.0.
