# A two-sided workspace reduction for Q8 words

Let `G=Q8={1,z,i,zi,j,zj,k,zk}`, where `z=i²=j²`, `z²=1`,
`ij=k` and `ji=zk`. Work over the full formal algebra `F2[G]`.
The central group element z is distinct from the scalar one.

There are R finite scalar roles with independent arbitrary dirty inputs.
A paid factor is

```text
D_l = I + ([a_l]+1) N_l,
N_l = u_l v_l^T,  u_l,v_l in F2^R,  v_l^T u_l=1,
a_l in {i,j}.
```

Every factor costs one. Free operations are binary scalar GL changes of basis.
There is no clean allocation, erasure, free address map or higher-rank call.
The endpoint is exact coefficientwise equality

```text
T = product_l D_l = diag([g_1],...,[g_R]),  g_a in G.
```

Roles with target 1 must return their arbitrary input. Let W count targets
other than 1, and t count targets in `{i,zi,j,zj}`. Factor order is fixed.

## The reduction theorem

Every such n-call word has a word with the same ordered paid labels and active
target list on at most `floor((n+t)/2)` total roles. Its remaining roles are
arbitrary restored dirty inputs. More precisely it can use
`min(rank X,rank Y)` roles, where X has columns u_l and Y has rows v_l^T.
The empty identity word reduces to zero roles.

First normalize any interleaved free scalar matrices by conjugating the paid
projectors. Binary rank and idempotence survive. Augmentation `[g] -> 1` sends
every paid factor and the endpoint to I, so the remaining scalar matrix is I.
This is the inherited register-model normalization.

For every group coefficient, the image of `T-I` lies in `U=im X` and its row
space lies in `row Y`. Each nonempty expansion term has scalar part
`u_a(v_a^T u_b)...v_c^T`, with noncommuting group coefficients in their
original order. For each nonidentity target g, the coefficient at `[g]` in
`T-I` is the projector onto its target coordinates. Thus U contains every
active coordinate axis. Also `K=ker Y` lies in the dirty coordinate space D.
These are the credited coefficient-support steps.

There are two valid reductions.

1. Restrict to U. Every N_l maps the entire space into U, hence preserves U.
   Its restriction remains rank one and idempotent because it fixes its
   nonzero image vector u_l. Write `U=E direct_sum (U intersect D)`, where E
   is the active coordinate space. A basis beginning with the active axes
   makes the restricted endpoint the same active diagonal and identity on
   the remaining dirty roles. The dimension is rank X.
2. Quotient by K. Every N_l kills K, so every paid factor fixes K pointwise
   and descends to `V/K`. Its induced rank-one map is nonzero, since
   `v_l^T u_l=1` implies `u_l notin K`; idempotence survives. Since K lies in
   D, the quotient splits as `E direct_sum (D/K)`. Its endpoint is again the
   same active diagonal and identity on all dirty roles. The dimension is
   rank Y.

Restriction and quotient commute with products of the induced maps and with
each formal group coefficient. Neither route transposes a noncommutative
matrix or asserts that every original gate is a direct sum. Intermediate
gates may read or write dirt which the reduction discards. Full restoration
at the endpoint is essential.

Define the group character chi with value one on `{i,zi,j,zj}` and zero on
`{1,z,k,zk}`. The ring map `[g] -> 1+chi(g)*epsilon`, `epsilon²=0`, gives

```text
XY = sum_l N_l = P_odd,   rank(P_odd)=t.
```

Sylvester's rank inequality over F2 gives

```text
rank X + rank Y <= n+t.
min(rank X,rank Y) <= floor((n+t)/2).
```

Choose the smaller valid reduction. This proves the theorem for every finite
R and n, rather than only the bounded executable fixtures. The same proof
works for any group with such a binary character and paid labels of character
one. That general observation is not a native supplier theorem.

Taking binary traces also gives `n=t mod 2`, since each N_l has trace one.
Idempotence is required here and to keep every paid factor legal after
reduction. Clean-only endpoint equations are insufficient for this proof.

## Two arbitrary-workspace sharp tariffs

The retained PR3471 source supplies exact finite exclusions at four total
roles, with arbitrary dirty inputs and restoration.

- No word through four calls reaches negative pairs. Representatives are
  `(zi,zi,1,1)` and `(zi,zj,1,1)` under role permutations and swapping i,j.
- No word through five calls reaches two-negative/one-positive triples.
  Representatives are `(zi,zi,i,1)`, `(zi,zi,j,1)` and `(zi,zj,i,1)`.

The unchanged native source recomputes these exclusions using exact
meet-in-the-middle equality. All binary rank-one idempotents are included.
There are 120 projectors and 240 positive factors at four roles. Inverse
prefixes of depth at most two have 42,041 distinct states. For the pair query,
the positive depth-two ball is checked against the inverse-prefix ball times
the target. For the triple query, every positive prefix of depth at most two
and every one-factor extension is tested. This covers all suffixes through
depth three, including the empty suffix. There is no heuristic pruning.
The retained README explains normalization, inversion and symmetry coverage.

For a negative pair, t=W=2. A word cheaper than six has n at most four by
trace parity. The reduction puts it on at most three roles. Pad with restored
identity roles to width four, contradicting the pair exclusion. Applying each
negative generator three times on its own coordinate attains six. Therefore
every ordered pair from `{zi,zj}` costs exactly six, with any finite restored
dirty workspace.

For exactly two negative-generator targets and one positive-generator target,
t=W=3. A word cheaper than seven has n at most five by parity. It reduces to
at most four roles and contradicts the triple exclusion. The direct word uses
`3+3+1=7` calls. Thus every such ordered triple costs exactly seven, with any
finite restored dirty workspace.

The four ordered negative pairs and 24 ordered triples exhaust these active
families. Arbitrary active positions follow by scalar permutation.
Nonuniform prices may admit longer but cheaper words, so this call-count
argument does not prove their weighted minimum. Three negative targets would
require a five-role exclusion through seven calls, which is not supplied.

## Credit and proof status

Tuafo and PR2900 supply predecessor image-restriction arguments in abelian
register models. ywz65/PR2587 supplies coefficient support and the
support/Sylvester tariff method. Nick Petalas/PR3450 supplies the combined
Q8 character; PR3460 supplies the one-negative arbitrary-workspace boundary.
The common-kernel quotient and choice of the smaller reduction give the
present noncommutative workspace bound. PR3471 retains all credit for its
finite exclusions, and Aaron Wang/PR2318 for the two-role values.

This is a written uniform proof with a computer-assisted finite dependency.
It is not proof-kernel verification, a physical compiler/caller invoice,
a new supplier, an exponent improvement or a selected-frontier change.
Independent human and formal proof-kernel review are unclaimed.
