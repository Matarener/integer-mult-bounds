# Actual rolling residual and a common scalar observation floor

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This note concerns one source-bound raw three-call word and a precisely
specified scalar observation contract. It proves an exact counterexample and
a111-reader information lower bound. It proves no native tariff, unrestricted
routed-reader bound or new multiplication exponent.

## Actual source and coefficient fields

The source is the THREE-COPY C511 word, gzip SHA256
`ac8a6dcd5957f49eefd6fc945332b1c31afa26c48fc301d37bfb1338beea6847`.
Its1487 source-only ADDs determine a binary111-by-111 matrix C with
`rank(C)=111`, `rank(C−I)=9`, and exact order511. This is distinct from the
later pruned order28 code. The independent checker executes each source input
column separately, reconstructs all entries, and checks C^511=I while C^7 and
C^73 are nonidentity. Since511=7·73, these checks establish its exact order.
The finite-order relation is not used in the three-call expansion below.

VALUE coefficients are over F₂. The counterexample's ADDRESS coordinates are
over the odd field F101. These fields play different roles: VALUE impulses
cancel modulo two, while ADDRESS routes use dyadic matrices reduced modulo101.

The111 retained root lines and their port order come from the pinned R438 word
(`a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022`).
The complete120-line geometry is pinned by
`1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55`.
The actual upstream breadth-first Weyl routes determine an eight-dimensional
orthogonal matrix g_p for each retained port. With root q_p, define

`P_p = q_p q_p^T /4`, `A_p = g_p[:,1:8]`,
`rho_p = [[P_p,A_p],[A_p^T,0]]` on15 coordinates.

These rho_p are the actual source charts; they are not newly chosen gauges.
The independent checker reconstructs the breadth-first tree with a FIFO queue
and applies each Householder reflection as an exact rank-one update. It matches
all111 saved rational rho hashes and verifies rho_p²=I. This retains source
signs and routes before reducing to F101.

## The raw three-call residual

Let N be the common rank-one ADDRESS exchange, N²=I. After the declared
source precode, the normalized source-consuming inverse call at stage i has
the two-bank matrix

`S_i = [[I,0],[N C_i,I]]`.

Both public banks are arbitrary. No initially zero target or restored-source
condition is imposed. The actual local native identity and fresh-prefix
commutations justifying this normalization belong to the source interface
proof; the following computation then occurs in the noncommutative operator
ring over F₂.

Use S_0 forward, its bank-swapped stage1 counterpart backward, and S_2 forward.
Writing `a_i = N C_i N`, direct multiplication gives

`R3 = [[I+a_1 C_0, N C_1],
       [N(C_2+C_2 a_1 C_0+C_0), I+a_2 C_1]]`.

The independent polynomial checker reduces only adjacent N N to I. It matches
every saved coefficient of this matrix without assuming the C_i commute or
using C_i^511=I. After factoring off the required parent FULL exchange, its
bank0 diagonal block is

`Phi = N(I+a_1 C_0) = N+C_1 N C_0`.

Thus the scalar rank of C−I does not identify the rank or observation needs of
this routed operator. The bank0 residual contains C_1 N C_0, with N between
codes belonging to different native stages.

### Exact neighboring cancellation is excluded under the stated freshness

Suppose one tries to cancel `a_(i+1) C_i` exactly. This requires
`C_(i+1)=N C_i^(-1) N`. Let G be the next fresh exchange. The actual native
family supplies `[C_i,G]=0`, `[N,G]=0`, and
`[C_(i+1),F]=0` for `F=NG`; G is invertible. Substitution into the last
commutation relation gives

`N C_i^(-1) G = G C_i^(-1) N = C_i^(-1) N G`.

Cancel G to obtain `[C_i^(-1),N]=0`, equivalently `[C_i,N]=0`. This contradicts
the actual source coefficient. Independently reconstructed routed edge(0,1)
has `C[0,1]=1`; the two projector-route products differ at entry(0,8), with
values1 and0. The same local code family at fresh stages retains this
noncommutation. At the initial scalar stage, distinct root projectors already
give a nonzero commutator on this off-diagonal edge.

This excludes that exact cancellation mechanism with those freshness
relations. It excludes neither arbitrary intermediate gates nor other coupled
bank words. The earlier millions-of-pairs bounded searches are not premises
of this proof and are not independently replayed here.

## Actual ADDRESS impulse

Use15 ADDRESS coordinates: the common eight plus the seven fresh coordinates
used by the routed stage1 code. Pad the remaining seven fresh coordinates by
zero to embed this example in the22-coordinate three-call parent.

At a port p, the partial exchange N acts on HEAD/TAIL pair(h,t) by

`(h,t) -> ((I−P_p)h+P_p t, P_p h+(I−P_p)t)`.

C_0 is the literal scalar source code. The stage1 coefficient from middle port
k to destination p is `C[p,k]` times the head/tail-separate push by
`rho_p rho_k`. For an entering HEAD vector v and TAIL0, put

`h_k = (I−P_k)v`, `t_k = P_k v`.

The contribution of C_1 N C_0 along a source q, middle k, destination p path
has VALUE coefficient `C[p,k] C[k,q]` and ADDRESS

`(rho_p rho_k h_k, rho_p rho_k t_k)`.

Add the direct N contribution at destination q and cancel equal output
impulses modulo two. For q=0 and v=e_0, the result has exactly3131 nonzero
output impulses. Exactly one has nonzero TAIL:

`output port0, HEAD=0, TAIL=e_0, VALUE coefficient1`.

The complete ordered output digest is
`ae0d4019d97be344e97730f586c84152eaea4fb16e83f541edadf0e22dc76eb0`.
The independent reconstruction obtains every output, rather than checking
only this witness or its total count.

Let U be the subspace of VALUE arrays supported on TAIL0, across all ports
and banks. The admitted free alphabet uses scalar port/bank mixing and
head/tail-separate linear ADDRESS routes, so it preserves U. Its invertible
elements and their inverses preserve U, hence induce invertible maps on the
quotient by U. The displayed nonzero quotient output cannot be erased by
such an invertible terminal free decoder. This remains true when the decoder
mixes both banks: a nonzero class cannot become zero under an invertible
quotient map. This is a counterexample to the actual raw word, not a claim
about every ADDRESS operator or caller.

## Complete common scalar readout bound

For each j=0,...,7, give every source port q the same input ADDRESS impulse
`HEAD=e_j, TAIL0`, with an arbitrary binary VALUE coefficient x_q. For each
output port and ADDRESS with nonzero TAIL, the corresponding VALUE output is
one scalar linear form `w·x`, with `w ∈ F₂^111`.

The independent checker constructs these coefficient rows by following each
individual source column through the actual C_0, N and routed C_1. Equal
ADDRESS paths cancel modulo two. It then sorts the rows in the saved canonical
order. The complete census is:

| HEAD sample | Nonzero projected coefficient rows | Accumulated binary rank |
|---|---:|---:|
|e_0|3268|63|
|e_1|3051|90|
|e_2|3054|105|
|e_3|3127|105|
|e_4|3127|111|
|e_5|3125|111|
|e_6|3128|111|
|e_7|3018|111|

There are24898 rows in total; every sample uses all111 source columns. The
complete row digest is
`607fd1d55202d616c7d50a913511c205ebe83aeb1dfec49be000beb598c725f3`.
All111 saved original witness rows are looked up by their exact sample,
destination and ADDRESS, compared entrywise, and independently shown to have
rank111 with low-bit Gaussian pivots. This independent rank engine differs
from the producer's high-bit echelon construction.

**Theorem.** Suppose the residual admits a factorization

`Phi = H_free + sum_(i=1)^t A_i (c_i^T tensor I_ADDRESS)`,

where H_free preserves U, each A_i is an F₂-linear response map, and each
`c_i ∈ F₂^111` is one fixed scalar source
row, independent of ADDRESS. Each reader combines whole source arrays at
matching addresses; the same c_i must work for all inputs. The response maps
A_i may depend on ADDRESS and route their already collected reader arrays.
Then `t ≥ 111`.

**Proof.** Restrict the input to sample j. Reader i returns
`(c_i·x) delta_(e_j,0)`. Apply A_i and project one tail-nonzero output impulse.
Its scalar output coefficient is a multiple of `c_i·x`. H_free contributes
zero to that projection because the input lies in U. Therefore every observed
coefficient row w is in `span{c_1,...,c_t}`. The complete observed row space has
dimension111, so t is at least111. This is a finite witness to an exact
necessary statement for all factorizations in the declared model. ∎

The readers counted here are whole-array observations with scalar port
coefficients, not individual bits and not native child queries. The theorem
does not price their acquisition, storage, ADDRESS access or restoration. In
particular, it gives no native rank111 tariff. Routed/ADDRESS-dependent reader
rows, direct access to public inputs, extra native source queries, other cuts
or a changed word alter the factorization model and remain outside this bound.

## Controls and verification boundary

Setting both codes to identity makes `Phi=N+N=0` identically. The independent
checker verifies cancellation on all111·8 sampled impulses using the actual
rho_p rho_p adapters. This is a positive cancellation control, not merely an
expected rank string.

Two actual changes affect the reconstructed map. Removing the existing bit
`C_0[0,1]` while retaining C_1 and all ADDRESS routes changes a projected
coefficient row at output port3; the row's source1 bit flips and the full first
sample digest changes. Omitting the direct N term flips the source0 coefficient
of the unique tail-nonzero boundary impulse from1 to0. Neither changed word is
claimed to be an admitted construction.

The original failed-candidate invoice had rank mass15183 and a hypothetical
deficit213 if both banks reached the required parent endpoint. The actual
counterexample prevents that coverage from being credited. The number213 is
only a failed-candidate diagnostic. It is not a positive supplier moment.

Normal and optimized execution of the independent checker compare identical
receipts. This review does not replay the large bounded cut searches, and it
does not substitute for the root's primary producer or portable-package checks.
The five-call restored interface is a separate construction with its own
native proof and invoice. Chronological whole-helper owners, arbitrary dirty
restoration at new caller cuts, rounded errors, all-size recursion, physical
tape/access cost and an outer multiplication theorem remain separate.

## Credit

The source word and geometry retain their E8/R438 ancestry and source notices,
including Sagar Thakrar's transported R438 word and the predecessor THREE-COPY
source-code construction. The local mutable-source lane supplied the C511
interface, actual chart receipt, raw residual and scalar quotient certificate.
This review independently reconstructs the source code, Weyl routes, impulse
paths, coefficient rows and noncommutative expansion. It claims no new geometry
or generic observation theorem. Prepared with substantial OpenAI Codex
assistance; Apache-2.0. Exact finite evidence and the written argument are not
formal-kernel evidence or independent human review.
