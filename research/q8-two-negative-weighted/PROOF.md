# Complete class-count fronts for the retained positive-Q8 families

Work in the full formal algebra `F2[Q8]`, with central `z=i^2=j^2`,
`z^2=1`. The symbols `z` and `1` denote distinct group basis elements.
Paid factors are `I+([g]+1)uv^T`, with positive labels `g in {i,j}`,
binary vectors and `v^T u=1`. Only binary scalar GL mixing is free.
All roles have arbitrary independent dirty inputs. Every identity target
must restore its input. Normalization is the credited augmentation argument
in the retained PR3487 proof.

Let `s_i` count targets in `{i,zi}`, `s_j` count targets in `{j,zj}`,
and `nu` count negative targets in `{zi,zj}`. Other targets are identity.
The theorem applies to these three families:

- `nu=2`, `s_i+s_j=2`, any finite number of restored dirty roles.
- `nu=2`, `s_i+s_j=3`, any finite number of restored dirty roles.
- `nu=3`, exactly three total roles. No extra workspace is allowed in this case.

The first two families have the complete Pareto-minimal paid-label count set

```text
(s_i, s_j+4), (s_i+2, s_j+2), (s_i+4, s_j).
```

The third has the four vectors `s+(0,6), s+(2,4), s+(4,2), s+(6,0)`.
Every vector listed is attainable. Every legal word, however long, has a
count vector coordinatewise at least one of the listed vectors. This does
not classify all count vectors above the frontier as reachable.

Consequently, for all nonnegative real prices alpha for i and beta for j,
the exact minimum is

```text
alpha*s_i + beta*s_j + 2*nu*min(alpha,beta).
```

## Separate label floors and parity

Use the ring map into `F2[x,y]/(x^2,xy,yx,y^2)` sending
`[i]` to `1+x`, `[j]` to `1+y`, and `[z]` to `1`.
The negative targets zi and zj therefore have the same first-order
images as i and j. Equating coefficients gives

```text
sum_(i calls) u_l v_l^T = P_i,
sum_(j calls) u_l v_l^T = P_j,
```

where the disjoint diagonal projectors have ranks `s_i,s_j`.
Rank subadditivity gives `n_i>=s_i` and `n_j>=s_j`.
Taking binary traces, each idempotent contributes one, so
`n_i=s_i mod 2` and `n_j=s_j mod 2` separately. These steps do not bound
workspace and use no clean initialization. This first-order method is
inherited from ywz65/PR2587 and the retained mixed-tariff proof.

## The exact unit-count input

PR3487 proves `n_i+n_j>=6` for the first family and `>=7` for the
second, uniformly over finite restored dirty workspace. Its proof restricts
to the image span or quotients by the common kernel, preserving ordered
labels and the active endpoint on at most `floor((n+t)/2)` roles. The
combined character makes `t=s_i+s_j`; trace parity and the retained PR3471
four-role exclusions close the lower bounds.

For the third family, PR3471's exact three-role exclusion through seven
calls and trace parity give `n_i+n_j>=9`. This argument does not extend
that family to four or more total roles.

Thus in every stated family

```text
n_i+n_j >= s_i+s_j+2*nu.
```

The exact proof, source, receipt, reduction implementation and original
notices from PR3487 are retained unchanged in `inputs/pr3487/` and replayed.
The PR3471 native implementation searches the original finite domains;
the present work does not enlarge that census. The two largest complete
membership streams still have one native implementation. The retained
Hamilton engine independently checks all stored balls and probes and the
smaller pair meets, as stated in its original receipt.

## Why longer words cannot lower the weighted bill

Write `n_i=s_i+2a`, `n_j=s_j+2b`. The separate floors and parity give
nonnegative integers a,b, and the unit-count input gives `a+b>=nu`.
Choose an integer c with

```text
max(0,nu-b) <= c <= min(nu,a).
```

This interval is nonempty because `a+b>=nu`. The count vector of the
word dominates `s+(2c,2(nu-c))`. This proves that the stated finite set
dominates every legal count vector, including counts of arbitrarily long
words. It does not assume that the shortest word is cheapest.

Alternatively, its cost is at least

```text
alpha*s_i + beta*s_j + min(alpha,beta)*((n_i-s_i)+(n_j-s_j))
  >= alpha*s_i + beta*s_j + 2*nu*min(alpha,beta).
```

This inequality needs nonnegative prices, including zero. Negative prices
are excluded because padding by a fourth power can lower cost indefinitely.
The proof is for real prices; executable fixtures use exact rationals.

## Attaining every frontier vector

Apply the positive underlying generator once on each active coordinate.
For any c negative targets, apply i twice on that same coordinate, and
apply j twice on each other negative coordinate. Both squares equal the
central z, so every designated negative target receives exactly its missing
sign. Each factor uses a coordinate projector, and all identity-target
coordinates remain untouched. The resulting counts are exactly
`s+(2c,2(nu-c))`, with no extra role. Different coordinates commute;
the same-coordinate sign factor is central. All nu+1 vectors have the same
total, so no distinct one dominates another. They are exactly the
Pareto-minimal feasible counts.

For the minimum bill choose all sign corrections in the cheaper class.
For example two zi targets have cost `2*alpha+4*min(alpha,beta)`.
At `alpha=10,beta=1`, the six-call word with counts `(2,4)` costs 24,
whereas using i three times on each coordinate costs 60. All three
frontier vectors are needed to describe counts, although the middle one
is exposed only when the two prices tie.

## Added claim, credit and limits

PR3487 supplies the arbitrary-workspace unit minima and explicitly leaves
nonuniform prices unclaimed. PR3471 supplies the finite three-negative
minimum and all retained finite exclusions. The present addition is their
complete class-count antichain and sharp nonnegative-price corollary. No
new unit minimum or independently duplicated largest native stream is claimed.

Credit Tuafo/PR2900 for image restriction, ywz65/PR2587 for coefficient
support and label-rank/Sylvester methods, PR3450 for the combined Q8
character, PR3460 for the one-negative boundary, and Aaron Wang/PR2318 for
two-role values. The retained package preserves its full predecessor notices,
including Cinna Davis, steph4n-gh and the register-model lineage. Arham Tahir's
PR3137 compiler and PR3461's scalar preparation have separate physical costs.

This is a scoped computer-assisted mathematical theorem. The executable
role cap of twelve bounds fixtures only; the first two written claims are
uniform over finite workspace. No general three-negative workspace theorem,
four independently priced signed-label theorem, physical supplier, new
kappa or selected-frontier change follows. Independent human and formal
proof-kernel review are unclaimed.
