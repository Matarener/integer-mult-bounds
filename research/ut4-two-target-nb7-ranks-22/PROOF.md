# No two-target UT4 word has n_b = 7 with middle ranks (2,2)

In the formal group-algebra model of
[CrocSwap/integer-mult-bounds#1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662),
every legal word realizing two central targets satisfies `n_b >= 6`, and
[CrocSwap/integer-mult-bounds#3887](https://github.com/CrocSwap/integer-mult-bounds/pull/3887)
excludes `n_b = 6`, so every such word has `n_b >= 7`. This note proves the
scoped statement:

> No legal word equal to `I+([z]+1)I_2`, of any finite length and on any finite
> restored dirty workspace, has exactly seven paid `b` factors with middle ranks
> `(rank X, rank Y) = (2, 2)`, under the same unrestricted side-zero profile
> reduction that #3887 used for `n_b = 6`.

Middle-rank patterns `(2,3)` and `(3,2)`, and unrestricted `n_b = 7`, are left
open. There is no new κ; the selected decimal `0.001672660197076918` is
unchanged.

## 1. Model and the (2,2) slice at n_b = 7

Let `G = UT4(F2)` with `a = I+E12`, `b = I+E23`, `c = I+E34`, `z = I+E14`, and
work in `R = F2[G]`. On `r >= 2` roles a paid factor is
`I + ([g]+1) x y^T` with `g in {a,b,c}` and `x y^T` a nonzero binary rank-one
coupling. The target is `T = I + ([z]+1) P` with
`P = diag(I_2, 0_(r-2))`. Scalar `GL_r(F2)` mixing is free and normalized into
the couplings.

Use the fixed 17-dimensional quotient

```
Q = F2<a,b,c>/(a^2,b^2,c^2,ac-ca, deg >= 4)
```

of #1662. Write `B_j = x_j y_j^T` for the seven middle couplings in product
order, and set

```
X = [x_j] (r x 7),   Y = [y_j^T] (7 x r).
```

#1662 gives `XY = 0` and `n_b >= 2 + rank X + rank Y`, together with
`rank X, rank Y >= 2` from the `bac` and `acb` coefficients. At `n_b = 7` the
admissible patterns are therefore

```
(2,2), (2,3), (3,2).
```

This package treats only `(2,2)`. In that case every middle coupling is
supported on a fixed 2-dimensional active plane `H` (after a free `GL_r` change
of basis that places `P` in the leading block). The patterns `(2,3)` and
`(3,2)` require an extra dirty role and are out of scope.

## 2. Reduction to two active roles

With all seven `b`-couplings in `H x H`, an interior dirty contraction
`v_i(u_{i+1})` in a degree-`<=3` product can involve only `a` and `c` calls:
any factor that is a `b` call has zero dirty row and column, so contractions
against `b` see only the active block. Same-label dirty contractions between
two `a` calls (resp. two `c` calls) vanish in `R` because `([a]+1)^2 = 0`
(resp. `([c]+1)^2 = 0`).

Consequently the monomials that use only `{a,b}` or only `{c,b}`, and the
cross monomials `abc` and `cba`, receive no interior dirty contribution. Their
active `H x H` blocks are exactly the two-role coefficients computed from:

- the seven active middle couplings (a zero-sum sequence in the nine nonzero
  rank-one `2 x 2` matrices);
- the active prefix sums `P_j` of `a`-couplings before each middle call;
- the active suffix sums `Q_j` of `c`-couplings after each middle call.

Unrestricted outer length means every 7-tuple of `2 x 2` matrices arises as
such a profile for some finite `n_a` (resp. `n_c`). This is the same
unrestricted side-zero reduction #3887 used at `n_b = 6` (there labelled
`e_b = 0` because ranks forced equality with the paid count).

Therefore a realizing word with `n_b = 7` and middle ranks `(2,2)` on any
`r >= 2` yields a two-role profile pair with

```
(ab, ba, aba, bab) = (0,0,0,0),
(cb, bc, cbc, bcb) = (0,0,0,0),
(abc, cba) = (I_2, I_2).
```

## 3. Finite census on two roles

Conjugation by `GL_2(F2)` fixes the two-role target `I_2` and acts on middle
sequences. There are 49,686 conjugation-minimal zero-sum length-7 sequences of
nonzero rank-one `2 x 2` matrices. Of these, 546 have `rank X != 2` or
`rank Y != 2` on the active plane (they are the rank patterns `(1,2)` and
`(2,1)`); the remaining **49,140** have ranks exactly `(2,2)` and are searched.

For each such middle, the side-zero profiles are collected by a 3+4
meet-in-the-middle on the packed side table of #1690. Each side-zero profile
determines a transport key `(U_0,U_1,W_0,W_1)` whose bits record `(P_j x_j)` and
`(y_j^T P_j)`. The identity cross condition `abc = cba = I_2` is exactly the
key-pairing equation of #1690 with target packing `9 = I_2`.

**Result.** Across all 49,140 rank-`(2,2)` middles the set of side-zero keys
admits **zero** pairs with `abc = cba = I_2`. Certificate counts:

| Quantity | Count |
|---|---:|
| Canonical zero-sum middles | 49,686 |
| With `rank X = rank Y = 2` | 49,140 |
| Sum of side-zero key cardinalities | 46,169,088 |
| Key pairs with `abc = cba = I_2` | **0** |

A low-rank control middle with ranks `(1,2)` still produces many identity key
pairs, so the screen is not vacuous: the obstruction is the rank-`(2,2)`
constraint together with the side-zero locus.

## 4. Conclusion

No two-role profile pair meets the necessary quotient conditions of Section 2
for middle ranks `(2,2)`. By the dirty-contraction reduction, no word on any
finite `r >= 2` with `n_b = 7` and middle ranks `(2,2)` reaches the degree-three
quotient endpoint, hence none equals the formal target.

The patterns `(2,3)` and `(3,2)`, and the unrestricted statement that no
`n_b = 7` word exists at all, are not decided here.

## Credit

Model and separate-label bound: #1662 (@ToikY). Unit-tariff exactness and the
weighted open question: #1816. `n_b = 6` exclusion and the unrestricted
side-zero reduction reused here: #3887. Profile/key pipeline: #1690
(Aaron Wang / @navinor), as used by #1816. Workspace compression context:
#1680. Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
