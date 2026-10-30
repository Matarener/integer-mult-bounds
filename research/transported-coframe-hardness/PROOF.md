# A one-axis hardness obstruction for transported coframe optimization

This scoped proof and construction were produced by Nick Petalas. Apache-2.0.

## Statement and cost model

For a fixed finite logical linear program, choose one coframe from a supplied
two-element menu at each field. Conjugate each logical instruction by the
chosen coframes. Charge the Gaussian rank power `r^t` of every resulting
transition, including entrance and exit adapters, with `0^t=0` and `0<t<=1`.
Main entrance and exit charts are fixed to identity. Any productive endpoint
credit is fixed across choices and can therefore be subtracted as a constant.

**Theorem.** Minimizing this rank-moment bill is NP-hard even when every field
has one Gaussian axis, every menu is the same two-element menu, every paid
rank is one, and all instructions have a fixed explicit chronology. The
threshold problem for the constructed family is NP-complete. This holds for
every `0<t<=1`, with exactly the same integer objective for every such `t`.

The theorem concerns this finite rank objective. It does not assert hardness
of the already submodular common-anchor family, a particular repository word,
or a full physical cost model. Ordinary work is not included in `r^t`.

## Phase-exact axis

Work over the Gaussian dyadics `Z[i,1/2]`, or over the complex numbers. Set

```text
W = [[1,1],[1,-1]],       F = W/(1+i).
F^2 = -i I,              F^-1 = i F.
```

This is a phase-exact Fourier Clifford axis. Its computational symplectic
action interchanges the two coordinate axes, so its Gaussian rank is one.
`I` and `-i I` are monomial maps of Gaussian rank zero. All coefficients are
Gaussian dyadics. No square root or ignored global phase is required.

Use coframe `F^x` for a bit `x`. On a directed logical shear
`z_v += F z_u`, the coframe-conjugated response is

```text
K(x_u,x_v) = F^x_v F F^-x_u = F^(1+x_v-x_u).

                 x_v=0       x_v=1
x_u=0              F          -i I
x_u=1              I            F
```

Its Gaussian rank is `1[x_u=x_v]`. Each entrance adapter `F^x` and exit
adapter `F^-x` has rank `x`, giving total boundary charge `2x`.

The table is supermodular, with interaction `1+1-0-0=2`. Complementing one
endpoint reverses its sign. On a triangle, no vertex complements make all
three edges submodular: the number of edges whose endpoint complements agree
is always odd. This is an explicit one-axis instance of the signed-cycle
obstruction in David Ganz's #5693, not a new signed-switching theorem.

## An exact finite program with fixed main boundaries

Let `G=(V,E)` be an arbitrary finite simple graph with `n>=1` vertices and
`m` edges. Each vertex is a distinct arbitrary main input in a two-coordinate
payload field. Orient each edge from its smaller vertex to its larger vertex.
Set `M=2n+1`. In lexicographic edge order, execute the logical shear
`z_v += F z_u` exactly `M` times per edge. This defines a fixed invertible
logical program `P_G`, independently of any coframe assignment.

For a chosen vector `x`, apply `F^x_v` once on entrance to each field. Replace
each shear response by the literal `K(x_u,x_v)` above. On exit apply `F^-x_v`
to every field. At every instruction the physical field is `F^x_v` times its
logical field. Substitution proves this invariant and the fixed final endpoint
`P_G` by induction on chronology. In particular, every main input is arbitrary
and independent; none is silently zeroed or identified with another input.

For the rank accounting, the source-preserving implementation of a response
shear is the ordinary owned copy, transform, add and clear construction of
#5693, coframe-cut.md. Here the transform is exactly one rank-one axis or the
explicit ordinary monomial map. Its ordinary work and storage remain separate
from the rank moment. The construction's correctness also follows directly
from the block shear matrix and does not need an optimizer's certificate.

All main charts at the external boundary are identity. Both adapter charges
are retained. The endpoint, and hence any declared productive credit, is the
same for every `x`. A parent-grade legality rule can use any parent grade at
least two; all positive children have rank one. No actual selected recursive
caller or productive supplier is asserted here.

## Recovery of Simple Max Cut

Write `c_G(x)` for the number of graph edges whose endpoint bits differ, and
`|x|` for the number of one bits. The complete rank bill of the constructed
word is exactly

```text
B_G(x) = M (m-c_G(x)) + 2|x|.
```

Every rank is zero or one, so raising ranks to `t` changes no term. There are
no other Gaussian transitions in this declared word.

Let `c*` be the maximum cut size, and let `s*` be the smallest number of one
bits among assignments attaining `c*`. Since `0<=2|x|<=2n<M`, the objective
first minimizes `m-c_G(x)`, then minimizes `|x|`. Consequently

```text
min_x B_G(x) = M(m-c*) + 2s*,
c* = m - floor((min_x B_G(x))/M).
```

More explicitly, for any integer `k` with `0<=k<=m`,

```text
c* >= k  iff  min_x B_G(x) <= M(m-k)+2n.
```

The forward implication uses a cut of size at least `k`. For the converse,
every assignment with `c_G(x)<=k-1` has bill at least `M(m-k+1)`, strictly
larger than the displayed threshold. This proves a many-one reduction of the
Simple Max Cut decision problem, whose NP-completeness is due to Garey,
Johnson and Stockmeyer. The emitted word has `M m` shears and at most `2n`
adapters, hence polynomial length. A bit assignment lets a verifier compute
its integer bill in polynomial time. This proves the stated hardness and
NP-completeness. No power comparison, numerical tolerance or algebraic-number
oracle occurs in this reduction.

For `G=K3`, `M=7`, `c*=2`, and `s*=1`, so the minimum bill is nine. Dropping
both adapters would incorrectly give seven; dropping one gives eight. These
are different objectives. For `G=K5`, the minimum bill is 48.

## Attribution, consequence and limits

Ali Romman's [#5783](https://github.com/CrocSwap/integer-mult-bounds/pull/5783)
provides the exact submodular binary-table solver and explicitly leaves
unsupported pair laws outside it. David Ganz's
[#5693](https://github.com/CrocSwap/integer-mult-bounds/pull/5693), retained in
`research/joint-gaussian-coframe-search`, supplies the coframe-conjugation,
fixed-transport and signed-switching framework. Those results are cited as
predecessors. Their verifiers and actual source instances are not replayed.
The new step is this explicit one-axis reduction, with fixed main boundaries,
both adapter charges, phase-exact matrices and a common integer objective for
the full power interval.

Classical complexity input: M. R. Garey, D. S. Johnson and L. Stockmeyer,
[Some simplified NP-complete graph problems](https://doi.org/10.1016/0304-3975(76)90059-1),
Theoretical Computer Science 1, 1976, 237-267, Simple Max Cut. Fourier Clifford
identities and graph-cut/signed-switching facts retain their classical credit.
No worldwide novelty is asserted for those components.

The consequence is a worst-case obstruction to a polynomial exact extension
covering all transported binary menus, unless P=NP. Special source structure,
small exceptional deletion sets and branch-specific cuts remain valid routes.
The rank-one family here is deliberately constructed and does not establish
that any retained supplier has a hard optimization instance. It also gives no
runtime lower bound for executing its fixed linear map, no claim against
resynthesis of repeated shears, no complete paid physical invoice, no new
kappa and no change to the selected frontier. Formal proof-kernel and
independent human review remain unclaimed.
