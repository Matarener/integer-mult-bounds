# Explicit-width synchronized balanced CRT caller

This binds Cinna Davis's PR4100 `CRT.md:76–92` to a literal global-row
decoder and a whole balanced-tree caller. The CRT factorization and
Beneš compiler are predecessor work. All-active-target omission is
already established in Hiroki KUMAZAKI's PR4169 `PROOF.md:304–334`
and assumed by PR4174's placement audit `PROOF.md:44–50`; it is not
a new theorem claimed here. The addition is the explicit-width
row/idle interface and its executable complete caller binding.

## 1. Domain and coordinate convention

Let d>=1 be a power of two and ell>=2. Axis i has declared width
`h_i in {ell-1,ell}` and modulus `2<=s_i<2^h_i`. All moduli are
pairwise coprime. Every tuple in

```
D = product_(i=0)^(d-1) {0,...,2^h_i-1}
```

is present, including arbitrary invalid padded values. No coordinate
is initialized. A tuple is globally valid exactly when every x_i<s_i.
Declared widths are inputs; they are **not** inferred from moduli.

Logical axis0 is the innermost coordinate. With `b_i=sum_(j<i) h_j`
and `L=sum_i h_i`, packing is `sum_i x_i 2^b_i`. Local arithmetic bit q
of axis i is numeric bit `b_i+q`, or MSB-first physical position
`L-1-b_i-q`. This introduces no physical bit reversal. The present
caller runs in these canonical coordinates, before reservoir placement.

The result is a permutation of all D with the same endpoint as the
source's padded `balanced` arithmetic map. On the globally valid
subset this is its CRT map Phi. Reversing balanced levels and global
rows gives the inverse on all D. No physical tape/E tariff, compact
implementation or full multiplication theorem is included.

## 2. One literal common row schedule

The retained height-h network has target-bit schedule

```
q_h(r) = r                  for 0<=r<h,
         2h-2-r             for h<=r<2h-1.
```

Use global rows `g=0,...,2ell-2`. For width ell, local row is g.
For width ell-1 define

```
local(g) = g       if 0<=g<=ell-2,
           IDLE    if g=ell-1 or g=ell,
           g-2     if ell+1<=g<=2ell-2.                   (1)
```

For ell=2 the last interval is empty and the one-row short network
appears only at g=0. For every ell>=2, removing IDLE gives exactly
`0,...,2(ell-1)-2` in order, once each. In a nonidle row,
`q_(ell-1)(local(g))=q_ell(g)` and the bit lies inside the declared
axis. For the long width the same facts are immediate.

IDLE has **no local row, no target bit and no table query**. It does
not refer to a nonexistent high bit with zero control. The implementation
represents it by `(axis,None,None,0)` and branches before table access.
Equation (1) is a particular explicit embedding, not a claim that no
other correctly specified interleaving could work.

For an axis of width h_i, compile the permutation on its entire existing
`2^h_i` coordinates:

```
R_(i,c)(x) = (x+c) mod s_i  if x<s_i,
             x             otherwise.                  (2)
```

Retain all `(2h_i-1)` source rows. No shorter coordinate field is
substituted when a modulus would fit fewer bits.

## 3. Binding the rows to one balanced level

At level k, nodes are consecutive groups of `2^k` axes, split into
left A and right B. At the start of the level reconstruct the source's
locally scaled CRT integer k_A from the current left coordinates if
all are valid; otherwise use zero. For every i in B define

```
c_i = k_A * (S_A P_(B,i))^-1 mod s_i,
S_A = product_(j in A) s_j,
P_(B,i) = product_(j in B, j<i) s_j.                      (3)
```

Pairwise coprimality makes the inverses exist. These are precisely
the offsets in `CRT.md:35–71` and the retained `balanced` caller.
Only the unchanged left-child coordinates and fixed moduli determine
them. Thus freeze **these offsets** for the level. Do not freeze the
axis value used to query a later table row.

At each global row, decode (1) for every right-child axis. For a
nonidle row query the source table at that axis's **current** value
and flip its decoded bit by the result. Current padded values remain
valid table indices because the table has the declared `2^h_i` size.
Combine these disjoint-axis flips simultaneously.

The dependency reasoning from PR4169 applies: each switch reads its
own non-target axis bits and its node's left child. Other active axes
are right children; different nodes are disjoint. Therefore all
active target bits are omitted, including for invalid left children.
This established fact makes each global row a commuting product of
involutive switches.

More strongly, all switches on different right-child axes commute
throughout this level: their only external inputs are left-child
coordinates which never change. Equation (1) preserves each axis's
own row order. The synchronized interleaving therefore equals the
serial composition of its complete per-axis words. By the predecessor
compiler, each word is (2). Consequently the whole level equals the
source's arithmetic level, for **every** padded tuple.

Full rotations fix each invalid target value and map valid target
values among themselves. Left axes are unchanged. Hence whole-level
endpoints preserve the global valid/invalid partition; composition
over all levels is the source's padded permutation. On globally
valid inputs, the predecessor CRT factorization gives Phi. The
finite valid-subset check also compares the direct CRT formula.

## 4. Exact inverse and ownership of intermediate invariants

At each level the stored offsets depend only on its unchanged left
axes. Reversing higher levels first restores the starting state needed
for a lower inverse level. Recompute (3) from that level's current
left axes and execute global rows in reverse order. Each row is an
involution, so this exactly reverses the level. Reverse the levels
as well. This uses the **same c_i tables in reverse row order**;
the source's separately compiled negative-offset route is another
word with the same inverse endpoint.

Validity is a **whole-network/level endpoint** invariant. It need
not hold between its microscopic switch rows. The exact retained
compiler for N=4,s=3,c=1 has tables

```
(bit0, [0,0,1,1]),
(bit1, [0,1,0,1]),
(bit0, [1,1,1,1]).
```

Input1 stays1, becomes invalid padded value3, then becomes valid
endpoint2. The genuine two-axis caller with moduli `(7,3)`, declared
widths `(3,2)` and ell=3 has c=1 at input `(1,1)`. Its short rows
appear at global rows0,1,4. Gating a micro-switch on the **current
target** being below3 incorrectly skips the final flip and leaves
`(1,3)` instead of `(1,2)`. This is a counterexample to that altered
control interface, not to PR4100's correctly defined table lookup.

Likewise, global invalid tuples are not all pointwise fixed. For
moduli `(5,7,11,13)` and widths `(3,3,4,4)`, input `(5,0,1,0)`
becomes `(5,0,1,6)`: one invalid coordinate remains, while the
independent right node performs a valid rotation. Bijection and
preservation of the invalid set do not imply pointwise fixation.

## 5. Finite source binding and limits

The source's `balanced(...compiled=True)` helper infers each table
size from `(s_i-1).bit_length()`. Its own finite tests use those
minimal widths. It is an appropriate additional oracle when declared
widths match them. It is not an oracle on all wider declared dirty
fields: e.g. moduli `(5,3)`, widths `(3,3)`, input `(0,4)` has a
legitimate fixed padded target, but the helper indexes its smaller
four-entry target table outside that helper's domain. This is a
finite API coverage boundary, not a defect in the production prime
family or the mathematical CRT construction.

The verifier therefore always compares to source **uncompiled**
`balanced` on all padded tuples, additionally compares compiled
source where widths are minimal, and checks `direct` on the complete
globally valid subset. It verifies both inverse compositions and
complete distinct-destination coverage. At every visited forward
row it recomputes the level controls from current left fields and
toggles every active target to test the actual decoder/control binding.
This corroborates predecessor omission at the newly explicit rows.

The small fixtures use canonical logical coordinates. They do not
execute reservoir placement, the compact word/repair, the ordinary
callee or physical data movement. Source functions and network
caching are host computations with no claimed tape or E cost.
The counted rows are schedule events, not machine steps.

PR4174 already proves mixed-width field allocation and coordinate
transport for a supplied synchronized layer; its executable caller
uses one target axis. PR4169 already proves the arbitrary-source
compact inverse and all-target omission; its executable caller also
uses one target axis. This package adds the literal global/local row
map, explicit declared-width binding and a whole mixed-width,
multi-target balanced-tree execution. It does not repackage their
omission, allocator or inverse theorem as a new result.

Credit Cinna Davis for the original CRT/network construction, Hiroki
KUMAZAKI (@kumagi) for PR4169/4174, Douglas Colkitt and the retained
routing/compact-control lineage. Prepared with substantial OpenAI
Codex assistance. Apache-2.0. No independent human or formal-kernel
verification is claimed.
