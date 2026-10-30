# The fixed two-clique REL floor survives ambient excursions

Prepared by AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
This extends Nick Petalas's confined relay theorem in
[PR6229](https://github.com/CrocSwap/integer-mult-bounds/pull/6229), pinned at
`50540b2a7e0d219bc4920e6252e75113b5a9d8d8`, specifically
`research/p104-two-clique-relay-floor/PROOF.md`. The underlying REL question
and its outside-reaching case are from DreamingOfClouds's
[PR6170](https://github.com/CrocSwap/integer-mult-bounds/pull/6170), pinned at
`445fb9124eb3fcb5d4f342c476b9ae3637f185aa`,
`research/p104-designer-toolkit-v2/P104-LEMMAS.md`, sections 10.1 and 11.5.
The actual P104 ports are retained from Ali Romman's helper-subspace work,
`research/p104-helper-subspace-splits/WORD.json.gz`, as in PR6229.

The new step is intersection with the source span, including an explicit
zero-gap extension of the confined proof. No predecessor file is modified.

## Fixed sources and ambient REL contract

In the concrete fixture the labels are binary vectors in `F2^9`, encoded
as integers, with pairing `b(p,q) = popcount(p & q) mod 2`:

```text
A = (73, 239, 336, 502)
B = (81, 247, 328, 494)
G = A followed by B
W = span_F2(81, 502, 239, 73),  dim_F2 W = 4.
```

Their Gram matrix has value one within each class, including the diagonal,
and zero between classes. In particular the eight labels lie in `W`.
The theorem also allows any finite-dimensional binary ambient space `V`
with a symmetric bilinear form `b` containing an isometric copy of this
fixed `W`. The form on `V` may be degenerate. All frame dimensions below
are over `F2`; source coefficients and matrix ranks are over `Q`.

Let `e_i`, for the eight ports `p_i`, be independent rational source
coordinates, and set

```text
X(g) = span_Q {e_i : p_i belongs to g}.
```

A finite, chronologically ordered ambient REL network consists of moves
`mu = 1,...,M` with arbitrary binary subspaces of `V` satisfying

```text
L_mu < g_mu,
v_mu = l_mu + sum_(nu < mu) a_mu,nu v_nu,
l_mu belongs to X(g_mu),
a_mu,nu != 0 implies L_nu is contained in g_mu.
```

Here `<` is strict subspace containment and all coefficients are rational.
For its receiving vector `u_mu` require

```text
u_mu(j) != 0 implies L_mu is contained in Q_j,
Q_j = {x in V : b(p_j,x) = 0}.
```

The endpoint and paid bill are

```text
C = sum_mu u_mu v_mu^T,
P = sum_mu (dim g_mu - dim L_mu).
```

Identify each binary Gram entry with the rational number zero or one and
write `Gamma_ji = b(p_j,p_i)`. Correctness is

```text
H = C Hadamard-product Gamma = I_8.
```

These are exactly the source, arrival, receiver and endpoint rules of the
eight-source REL relaxation, with the confinement `g_mu <= W` removed.
Arbitrary branching, merging, cancellation, resets and public re-ascents
are allowed. Public transport and other scalar operations remain free in
this relaxation. No source coordinate is initialized to zero.

**Theorem.** Every network satisfying this contract has `P >= 8`.
The exact minimum is eight, including when frames may leave `W`.

## 1. Cost-nonincreasing contraction

For every move retain all rational data and replace only its frames by

```text
g'_mu = g_mu intersect W,
L'_mu = L_mu intersect W.
```

The contracted frames satisfy `L'_mu <= g'_mu <= W`, but the first
containment need not be strict. They form an auxiliary **weak REL**
network, in which equal gather and landing frames are permitted at zero
cost. This is a proof relaxation, not a proposed native primitive.

All four relevant facts follow directly.

1. **Local sources are unchanged.** Since every `p_i` is in `W`,
   `p_i in g_mu` if and only if `p_i in g'_mu`. Consequently
   `X(g_mu) = X(g'_mu)`, and the identical `l_mu` is available.
2. **Every used arrival is preserved.** From `L_nu <= g_mu` follows
   `L'_nu <= g'_mu`. Retaining the recurrence and its order therefore
   retains every `v_mu`, by induction on `mu`.
3. **Every used receiver is preserved.** From `L_mu <= Q_j` follows
   `L'_mu <= Q_j intersect W`. Thus the identical `u_mu` is allowed,
   and the entire matrices `C` and `H` are unchanged.
4. **No gap increases.** Inclusion induces an injective linear map

   ```text
   (g_mu intersect W)/(L_mu intersect W) --> g_mu/L_mu.
   ```

   Its kernel is zero: a vector of `g_mu intersect W` whose class lies in
   `L_mu` already lies in `L_mu intersect W`. Hence

   ```text
   dim g'_mu - dim L'_mu <= dim g_mu - dim L_mu.
   ```

Let `P'` be the sum of the contracted gaps. Then `P' <= P`. No division
by a gap or deletion of a zero-gap step is used. Deletion would require
extra care because a zero-gap step may still relay content to successors.

For example `g = span_F2(73,1)` and `L = span_F2(73)` have gap one in
`F2^9`. The vector `1` is outside `W`, and their intersections with `W`
both equal `span_F2(73)`, so the contracted gap is zero. This is why the
strict-descent checker from PR6229 cannot simply be invoked unchanged.

## 2. The confined cumulative proof permits zero gaps

Here is the confined argument with the weak inclusion made explicit.
Choose a representative `a_0` of `A` and `b_0` of `B`, and define the binary
linear map

```text
pi : W --> F2^2,
pi(x) = (b(a_0,x), b(b_0,x)).
```

For an `A` port its image is `(1,0)`, and for a `B` port it is `(0,1)`.
All ports in one class have the same pairing functional on `W`: they
agree on the spanning set `G`, hence agree on its span. This assertion
is used only on `W`, never on an outside part of an original frame.

Represent the five binary subspaces of `F2^2` by rational subspaces:

| Binary subspace `S` | Rational subspace `T(S)` |
| --- | --- |
| zero | zero |
| `span_F2(1,0)` | `span_Q(1,0)` |
| `span_F2(0,1)` | `span_Q(0,1)` |
| `span_F2(1,1)` | `span_Q(1,1)` |
| `F2^2` | `Q^2` |

This table preserves inclusions and dimensions. For a contracted frame
`h <= W`, put `T_h = T(pi(h))`. Let `t_i` be `(1,0)` or `(0,1)` according
to the class of port `i`. The following properties hold.

* If `p_i in h`, then `t_i in T_h`.
* If `h <= Q_j`, then the rational functional `t_j^T` annihilates `T_h`.
  Indeed the appropriate coordinate functional of `pi` vanishes on `h`;
  the table preserves precisely these coordinate-annihilation cases.
* If `k <= h`, then `T_k <= T_h` and

  ```text
  dim_Q T_h - dim_Q T_k
    = dim_F2 pi(h) - dim_F2 pi(k)
    <= dim_F2 h - dim_F2 k.
  ```

The final inequality follows from the surjection
`h/k --> pi(h)/pi(k)`. All these statements allow equality `k = h`.

For a rational source vector `v`, let `B(v)` be the `2 by 8` rational
matrix whose column `i` is `t_i v(i)`. We construct increasing rational
subspaces `D_mu` of source rows satisfying

```text
z^T B(v_nu) belongs to D_mu
  for every nu <= mu and every z in ann(T_L'_nu),

dim D_mu <= sum_(nu <= mu)
             (dim T_g'_nu - dim T_L'_nu).
```

Start with `D_0 = 0`. If `z` annihilates `T_g'_mu`, the local term
`z^T B(l_mu)` vanishes because every one of its columns lies in
`T_g'_mu`. Every used earlier parent has
`T_L'_nu <= T_g'_mu`, so the induction hypothesis gives

```text
z^T B(v_mu)
  = sum_(nu < mu) a_mu,nu z^T B(v_nu) belongs to D_(mu-1).
```

Extend a basis of `ann(T_g'_mu)` to one of `ann(T_L'_mu)`. Adjoin to
`D_(mu-1)` the rows `z^T B(v_mu)` for the new basis functionals.
Their number is exactly `dim T_g'_mu - dim T_L'_mu`. This establishes
both induction statements. If the contracted gather and landing are
equal, the two annihilators are equal and **zero new functionals** are
adjoined; the displayed parent equation establishes the invariant for
that step. Thus a zero-gap step needs no independent charge and may
remain in the chronological graph.

For each output row `j`, the class Gram rule gives

```text
H_j,* = sum_mu u_mu(j) t_j^T B(v_mu).
```

Every nonzero receiving coefficient has `L'_mu <= Q_j`, so `t_j^T`
annihilates `T_L'_mu`. Therefore every row of `H` belongs to `D_M` and

```text
rank_Q H <= dim D_M
         <= sum_mu (dim T_g'_mu - dim T_L'_mu)
         <= P' <= P.
```

For a correct network `H = I_8`, proving `8 <= P`. This is a bound on
the complete chronological network. It is not a sum of separate rank
bounds on its moves, whose relayed content may be shared.

## 3. Attainment, including an outside-reaching example

For each matched pair `(a_i,b_i)` from `A,B`, the confined move

```text
g_i = span_F2(a_i,b_i),  L_i = 0,
v_i = u_i = e_Ai + e_Bi
```

has gap two and obeys all availability rules. The four moves have no
parents and give

```text
C = [[I_4, I_4], [I_4, I_4]],  rank_Q C = 4,
H = I_8,  P = 8.
```

They are valid in every ambient space containing the fixed `W`, proving
attainment in that contract. In the concrete ambient `F2^9`, an attaining
network can also use frames outside `W`. Set `z = 1`, and use these four
moves with the same `v_i,u_i` and no parents:

| Matched ports | Gather `g_i` | Landing `L_i` | Gap |
| --- | --- | --- | --- |
| `73,81` | `span(73,81)` | zero | 2 |
| `239,247` | `span(239,247)` | zero | 2 |
| `336,328` | `span(336,328,z)` | `span(z)` | 2 |
| `502,494` | `span(502,494,z)` | `span(z)` | 2 |

Here `z` is outside `W`, so each of the last two gathers has dimension
three and its landing has dimension one. Both ports in each of those
pairs have least-significant bit zero, so they are orthogonal to `z`.
Local source availability and receiver availability therefore hold.
The endpoint is the same rank-four `C`, with `H = I_8` and paid eight.
This checks that permitting outside frames is substantive and that the
floor remains attainable there. These are abstract REL examples, not
admissible-root or physical-word constructions.

## Scope and remaining obligations

The theorem resolves the outside-reaching extension of PR6229 for this
fixed eight-source, two-clique contract. It imposes no bound on the number
of ambient dimensions, moves or parents beyond finiteness. Its proof is
not a finite enumeration. Finite checks of the stated fixture, contraction
rules and examples are evidence for their exact algebraic implementation,
not a substitute for the argument over all networks.

The contraction need not preserve a native admissible-root condition, a
strict MOVE primitive, helper lifetimes or physical support constraints.
It need only land in the weaker auxiliary REL contract proved above.
An application to a native model must separately establish that the
original native network satisfies the stated REL rules and paid bill.
No native lowering, complete physical invoice, supplier admission or
multiplication theorem is claimed here.

In particular **do not add eight across several groups whose networks
share paid moves**. This proof charges one complete network for the one
fixed set of sources. Several applications to shared frames may charge
the same original dimension gap repeatedly. A global block-sum lower
bound requires a separate non-duplication argument and is not proved.
The result does not settle the P104 NEED threshold, all 104-port
completions, or the global owned-paid budget. The selected #6030 frontier
and its kappa are unchanged. Independent human review and formal proof-
kernel verification are unclaimed.

The feasible next question is whether a proposed multi-group REL witness
admits a single shared-cost invariant; begin with two explicit groups and
one shared relay and retain its full invoice. Merely summing the present
per-group bounds does not address that question.
