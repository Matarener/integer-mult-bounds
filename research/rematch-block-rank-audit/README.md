# Independent block-payload audit of the rematched P112 mask

**Exact minimum rank `34d`, for every field and every integer `d >= 1`, on
PR3335's fixed matching. No native price, supplier admission or new kappa.**

[PR3335](https://github.com/CrocSwap/integer-mult-bounds/pull/3335), exact head
`1d46df8b5aeac49d165cae58c1dd1036666bb789`, supplies a new matching of the 112
selected P112 ports and proves scalar fitting rank 34. Its matching, 34-support
construction and 17-plane clique are predecessor results. This package checks
those finite certificates with a separate implementation and spells out the
consequence for arbitrary vector payloads: unrestricted directed `d x d` free
blocks, including nonsymmetric and noncommuting ones, cannot reduce the
normalized rank below 34 on this matching.

This is a source-bound application of the existing
[block-fitting framework](../paired-plane-block-rank/README.md), which treats
the older PR1825 matching and proves its different minimum `49d`. No new
general block-rank method or independent human review is claimed.

## Exact contract

The 112 binary labels `q_i` come from the selected #1094 source archive, in
its actual port order. PR3335 pairs them into 56 planes `E_i`. Both ports of
a matched pair have the same complete plane. Every pair has binary Gram `I2`.

Let `F` be any field. Each port now carries `F^d`. A matrix `M` with 112 by
112 blocks of size `d x d` fits when

```
M_ii = I_d;
M_ij = 0_d if i != j and E_i is not orthogonal to E_j.
```

Rows are target ports and columns are source ports. The two directions of a
permitted pair are independently free. We assume neither symmetry nor
commutativity. In particular, two distinct ports in the **same** Gram-`I2`
plane have a required zero cross block even though their individual labels
are orthogonal. The source/reader permission is the full-plane condition
`E_j <= E_i^perp`. This is the inherited strict mask, not a new physical
decoder contract.

## Proof for every field and dimension

**Lower bound.** The independently checked clique consists of plane indices

```
1 5 8 12 16 20 24 30 32 37 43 44 49 51 52 53 55.
```

They are pairwise nonorthogonal. Take both ports of all 17 planes. Every
off-diagonal block in this principal submatrix is forced to zero: between
different planes by the clique, and within one plane by its nondegeneracy.
Its diagonal blocks are `I_d`. Thus every fit contains `I_(34d)` as a
principal submatrix. Deleting rows and columns cannot increase rank, so
`rank_F(M) >= 34d`. This argument works in characteristic two as well as
every other characteristic; there is no division by a field element.

**Upper bound.** The 34 predecessor supports partition all 112 ports.
Different ports in one support lie in orthogonal planes. Set `K_ij=1` when
`i,j` share a support, and zero otherwise. The scalar mask holds, so
`K tensor I_d` fits. For each support, sum its source vectors into one
`F^d` message and broadcast that message to its members. This factors the
matrix through a space of dimension `34d`, proving rank at most `34d`.
Selecting one port per support also gives `I_(34d)` directly. Consequently

```
min { rank_F(M) : M fits this fixed block mask } = 34d.
```

The lower bound applies to every fitting matrix, not only tensor products or
the exhibited factorization. A linear layer `M = D T` through a query space
of total dimension `r` therefore needs `r >= 34d`. If each message carries
at most `d` field coordinates, it needs at least 34 messages. This is a
dimension statement, not the recursive rank price of those messages.

## Why the larger payload class is actually exercised

The replay constructs `M_ij = K_ij P_i P_j^-1` with unimodular local charts.
For three ports in one actual support, choose respectively

```
A = [[1,1],[0,1]], I_2, C = [[1,0],[1,1]].
```

Two free blocks are then `A` and `C^-1`; their products in the two orders
differ by a diagonal entry of magnitude one. They do not commute over any
field, including GF(2). The charted construction still fits, and its rank
is 68. These charts are algebraic examples; their native cost is unpriced.

The verifier independently enumerates every vector in every binary plane,
compares that mask with a basis-pair oracle, checks all 11,440 forced port
entries and both identity-minor certificates, and measures ranks `34d` for
`d=1,2,3` over GF(2), GF(3) and GF(101). A separate vector-query interpreter
checks all 224 source-coordinate columns and all 224 arbitrary dirty target
columns for `d=2`. It realizes `Y -> Y + M X`, **not** an asserted complete
native `Y -> Y + X` endpoint. Allowed cross terms still require the consumer
specified by the physical contract.

Eight controls reject a line-only mask, a one-direction nonzero forbidden
block and its reverse, a diagonal shear with unchanged trace, an incomplete
clique, an invalid support reassignment, a repeated matching port and
duplicate JSON keys. The hidden forbidden block `[[1,-1],[1,-1]]` has trace
zero and annihilates constant payloads, so trace/constant-vector probes alone
would miss it. Full coordinate tests detect it. Finite samples corroborate
the code and binding; the dimension proof establishes the universal theorem.

## The separate 28-support statement

For any legal matching, at most four complete Gram-`I2` planes can be pairwise
orthogonal in `F_2^9`: their `2k` orthonormal spanning labels are independent,
so `2k <= 9`. A disjoint fitting support contains at most one port from each
of such planes. Its size is at most four. Thus a partition into disjoint
supports needs at least `112/4 = 28` supports; the two-supports-per-colour
construction also needs at least 14 colours.

This bounds that construction class. It does not, by itself, prove rank at
least 28 for arbitrary signed, overlapping or nonsymmetric fitting matrices
over all matchings. PR3335's open-question interval "28 to 34" should keep
that qualification unless an additional universal lower proof is supplied.
This audit supplies no counterexample below 28 and no new all-matching
lower bound. The fixed-matching `34d` theorem above is unaffected.

The replay includes a concrete logical control. In seven rational coordinates,
with form `J = diag(1,-1,-1,-1,-1,-1,-1)`, take the 27 vectors

```
a_i = e_i                                  (1 <= i <= 6),
b_i = 2e_0 - sum(e_j : 1 <= j <= 6, j != i),
c_ij = e_0 - e_i - e_j                     (1 <= i < j <= 6).
```

Every vector has squared length -1, and distinct pairings are zero or one.
Permit a cross entry precisely at pairing one. Every permitted edge has
exactly one common neighbour, and there are triangles, so a disjoint fitting
support has size at most three. Any support partition therefore needs at
least nine terms. Nevertheless `-V J V^T` fits this mask and has rational
rank seven. The code checks its seven-coordinate factorization, full mask,
triangle/common-neighbour argument and exact rational rank. This classical
27-line/Haemers fixture is a control for the invalid general inference,
**not a P112 example below 28 or a new graph-theory result**.

The block-fitting definitions are standard; see Bukh and Cox,
[On a fractional version of Haemers' bound](https://arxiv.org/html/1802.00476v2),
section 2, which credits Blasiak for the fractional parameter. Historical
rank-bound credit belongs to Haemers,
[Eigenvalue techniques in design and graph theory](https://doi.org/10.6100/IR41103).
Our numerical values are established by the explicit construction here, rather
than imported from those sources.

## Reproduce and source boundary

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -O -B research/rematch-block-rank-audit/verify.py
python3.12 -I -B research/rematch-block-rank-audit/test_integrity.py
python3.12 -B scripts/research_package.py --package research/rematch-block-rank-audit
```

`verify.py --emit` prints the deterministic receipt without modifying it.
Normal replay checks exact typed equality with [RESULT.json](RESULT.json).
No solver, native build, network, Lean or predecessor checker is used.

[SOURCES.json](SOURCES.json) binds the selected archive and the byte-identical
vendored PR3335 certificate by SHA256 and Git blob. The latter's original
path and exact public head were fetched and inspected at entry. Its Git blob
is `a99dfa5e83d5f70b4ef8d9cf2fa7a275aeddf8bb`. It is a `remote_sources`
observation verified by this script, rather than an assertion that a future
clone contains the unmerged predecessor commit. The generic metadata checker
does not authenticate that external head. The standalone verifier needs only
the retained archive, vendored certificate, this code, source metadata and
receipt. Input bytes are checked before and after mathematical replay.

## Scope and handoff

The actual complete source and reader copy tariff is the separate concurrent
[PR3345](https://github.com/CrocSwap/integer-mult-bounds/pull/3345), head
`529959bb00abd01664b7109d2e40574ecb0c8da1`, following the
[Discussion1587 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19007603).
Its author-checked invoice was read at the submission checkpoint, not replayed
here. This package does not reprice its channels or repeat the direct-block
native implementation. It does not prove a native recipe, chronological acquisition,
restoration, storage, hosting, precision/tape, all-size supplier, bit supplier,
complete paid invoice, outer transfer or multiplication theorem. The selected
frontier is unchanged. No selected cold replay or formal-kernel build ran.

## Open next questions

1. For an arbitrary changed matching, what lower bound holds for *every*
   fitting matrix, beyond the disjoint-support construction class? First
   specify the coefficient field and payload model, then give a rank witness
   or prove a universal structural inequality. The 28-support packing argument
   alone is the blocker; no additional matching search is justified by this
   audit.
2. Can genuinely fractional source/reader factors, or a changed physical
   contract, lower the complete invoice? The concurrent tariff result rules
   out merely regrouping these integral support-partition factors under its
   stated model. First join a different exact factorization's complete-plane
   tariff to an explicit message/consumer program. Scalar dimension, payload rank,
   acquisition, restoration and storage must be charged separately. This
   package provides the fixed-mask dimension boundary only.

Structured questions, overlap coverage and the scoped checkpoint are in
[TASK.json](TASK.json). The advisory claim is
[here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19007618).

## Credit

Arham Tahir with substantial OpenAI Codex assistance in investigation,
implementation, proof and checking; no independent human or formal-kernel
review. New work is Apache-2.0; the certificate retains predecessor attribution.

Matarener, session donor Mark and Claude supplied PR3335's matching, supports
and clique. Sagar Thakrar/thakrarsagar supplied PR2484's exact rank-49 result;
ywz65 supplied PR2471's mask/clique framework. Cinna Davis supplied the
PR1825/2126 plane construction and 1337isnot1337 supplied PR2118's earlier
local rematch. Adam Gall/PR1889 supplied the strict scalar-mask audit. Retain
ctoth and Philippe Van Velzen's plane contract and tariff credit, Jeremy
Diviney's native-payload distinction, and ywz65 for
`paired-plane-block-rank` and its larger block interface. Selected source
credit remains with Rohan Arun, Jeremy Kothe, icekylinx and their retained
geometry/compiler/word lineage. None of these predecessor results is claimed
as new here.
