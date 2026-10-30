# Fixed order-three partners and restored isolated contacts

This contribution reconstructs the fixed nine-dimensional order-three partner
map on all 112 retained ports, all 5,824 legal contact frames, and the exact
source-batched scheduling maximum of eight. It completes each isolated
dirty-helper contact by paying for a literal helper return. It does not
construct a compatible shared many-edge program.

Substantial OpenAI Codex assistance. The scientific inputs are pinned to
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The historical geometry and
deterministic source-batch algorithm are adapted from `order3_geometry.py`;
the phase convention retains the paired endpoint/native compiler ancestry.
`SOURCE-INVENTORY.json` identifies exact source and runtime bytes.

## Exact phase and rank convention

All binary vector operations below are over F2. Addresses are in F2^9 and
each field contains 512 arbitrary complex values; Gaussian-dyadic values
are preserved by every stated gate. The native line gate is

```
C_v = ((1+i)I+(1-i)X_v)/2.
```

On character `chi_x(z)=(-1)^(x·z)`, its eigenvalue is `i^(v·x)`.
Its inverse has exponent `-(v·x)`. For a nondegenerate space U with
orthonormal basis u_j, define the exact representative

```
P_U = sum_j u_j u_j^T,
T_U = W diag(i^wt(P_U x)) W,
```

where W is normalized Walsh-Hadamard. Since orthogonal vectors have even
intersection weight, the weight of their binary sum is the sum of their
weights modulo four. Therefore

```
T_U = product_j C_(u_j)^(s_j),
s_j = +1 if wt(u_j)=1 mod4, and -1 if wt(u_j)=3 mod4.
```

Every factor fixes the uniform character. This fixes the global scalar
exactly, in addition to the signed Pauli images. These representatives
depend on P_U, and hence on U rather than on its basis. All T_U commute.
For orthogonal spaces U,V with such bases,
`T_(U direct_sum V)=T_U T_V`. In particular
`T_(q perpendicular)=T_I T_q^-1` for every norm-one q here.

The quadratic polar matrix of `wt(P_U x) mod4` is P_U. One direct
derivation uses the signed-C expression: the polar matrix of
`s(v·x) mod4` is `v v^T` for either odd sign s, and these matrices add
over F2. After the Walsh conjugations this is precisely the X-image
block of the Z generators, namely the native/Bruhat B block.

Thus for nested nondegenerate U subset V, the actual operator
`T_V T_U^-1` has native rank `rank(P_V+P_U)=dim(V)-dim(U)`.
The last equality follows from the orthogonal decomposition
`V=U direct_sum (V intersect U perpendicular)`. This complement is
nondegenerate, though it may be alternating and need not admit an
orthonormal basis. The rank argument does not assume such a basis.
This point matters for the rank-three contacts.

The checker uses complete 512-entry exponent arrays, not just their
hashes, for exact operator arithmetic. Each constructed frame checks all
512 projected weights against its literal signed-C factorization. Frame
transition arrays are subtracted modulo four. All native ranks are
computed from their actual quadratic polar matrices. Receipt hash
interning additionally rejects distinct phase arrays with one key.

Twelve representative transition lowerings are separately executed by
the pinned compiler: two for a rank-one contact and five distinct roles
for each of ranks two and three. Each compares the actual B block,
full signed Pauli images, exact basis-zero state, and all 512 entries of
the independently Fourier-inverted convolution column. These twelve
compiler lowerings are distinct from the complete all-edge phase/rank
argument. Since every sampled operator is a convolution, its complete
zero column also determines all of its address columns.

## Complete partner contracts

The binary column matrix is

```
O=(451,454,453,31,55,47,248,440,376), c=511.
```

The checker verifies orthogonality, `O^3=I`, and
`O+O^T=I+cc^T` on all 512 vectors. The transpose identity is evaluated
as `O+O^2`, using the separately checked orthogonality and order three.
For every one of the 112 source ports p, it verifies that p and Op are
norm one and perpendicular. All 12,544 entries of their two Gram
matrices agree.

Each ordered contract has P=p, Q=Op, and a seven-vector orthonormal
complement R. The exact historical deterministic completion rule is
retained, including its guard against leaving a nonzero alternating
space without an orthonormal basis. The complete factorization
`T_P T_Q T_R=T_I` is checked on every character at all 112 ports.
The full ordered contract list has canonical SHA256

```
2765fa3074ba08133d8dbf1810c76e6d744127b4024d7933e1fe73d84e86389f
```

where canonical bytes are UTF-8
`json.dumps(contracts,sort_keys=True,separators=(',',':'))`
with no trailing newline. This is the exact list consumed from the
historical geometry by the separately owned endpoint checker, rather
than a claim of mere rowspace equivalence.

## Minimal nondegenerate contact dimension for every legal edge

An ordered correction edge (s,t) is legal when `p_s·p_t=0`.
Write `p=p_s`, `q=O p_s`, `p'=p_t`, `q'=O p_t`.
The O identity and the norm-one ports imply

```
(p·q') + (q·p') = 1 in F2.
```

The checker verifies this at every legal edge. A contact frame L must
contain p and q' and lie inside both upper caps `q perpendicular` and
`p' perpendicular`.

* If p=q', their one-dimensional span is already nondegenerate.
* If p and q' are distinct and perpendicular, their span has Gram I2.
* If p and q' are distinct and have dot product one, their two-dimensional
  span has Gram matrix with every entry one. Its nonzero radical is
  p+q', so no nondegenerate two-dimensional frame can contain that span.
  At least three dimensions are necessary.

For the last case the complete finite witness chooses the least w with

```
w·q=0, w·p'=0, w·(p+q')=1, w·(q'+c)=1.
```

The third condition makes span(p,q',w) nondegenerate. The fourth ensures
that q' is not its characteristic vector, allowing the retained
orthonormal completion beginning with q'. The checker constructs that
completion and verifies all pairings, cap containments and required
span membership. This supplies existence for every such edge; it is
not an unproved assertion about all possible binary geometries.

There are exactly 5,824 legal ordered edges. Their minimum nondegenerate
contact dimensions are

| Contact dimension f | Number |
|---|---:|
| 1 | 104 |
| 2 | 2,912 |
| 3 | 2,808 |

The per-edge dimension lower argument is a written linear-algebra proof;
the coverage and existence claims refer to this complete finite family.
It is not a lower bound for arbitrary algorithms or different helpers.

## Actual arbitrary-input word and literal helper return

Fix one contact of dimension f=2 or 3 and coefficient a in {+1,-1}.
At entrance write the physical fields as

```
x=T_p X, y=T_q' Y, h=T_q' H
```

for arbitrary X,Y,H. This notation is not an executed free entrance
transform: each physical input itself is arbitrary and the frame is
invertible.

Execute the following chronological word:

1. At frame q', perform `y -= a h`.
2. Apply `T_L T_p^-1` to x.
3. Apply `B=T_L T_q'^-1` to y, and separately to h.
4. At the common exact frame L, perform `h += x`, `y += a h`,
   and `h -= x`, in that order.
5. Apply the actual inverse `B^-1=T_q' T_L^-1` to h.
6. Apply `T_(q perpendicular) T_L^-1` to x and
   `T_(p' perpendicular) T_L^-1` to y.

Immediately before step 5, h is `T_L H`, y is `T_L(Y+aX)` and
x is `T_L X`. The helper's logical value is restored at that point,
but its physical field still differs from the entrance by B. Step 5
is necessary to restore the arbitrary raw helper exactly.

The final physical three-field block map, expressed in entrance raw
coordinates, is

```
[ T_(q perpendicular) T_p^-1                0                       0 ]
[ a T_(p' perpendicular) T_p^-1   T_(p' perpendicular) T_q'^-1     0 ]
[                  0                       0                       I ].
```

The code executes the entire word with independent input columns on
all three fields, complete phase arrays, and both signs a at every
edge. It never assumes H=0 or discards a helper-dirt coefficient.
Each term in the symbolic row calculation denotes an actual complete
512-character convolution operator. Exact identical-key cancellation
therefore proves the full arbitrary-input identity. Unequal candidate
rows in controls are further evaluated on characters to exhibit a
specific Gaussian-integer physical defect.

For f=1, p=q'. Use direct `y += a x` in that frame, followed by the
two public cap transitions. No helper is needed; the third field in
the replay is an unchanged arbitrary spectator.

## Complete isolated native and scalar invoice

The two public transitions on each data field have ranks f-1 and 8-f,
whose sum is seven. For f=2,3 the helper preparation and actual return
each have rank f-1. The complete positive-rank and scalar invoices are:

| f | Positive native rank histogram | Rank mass | Signed whole-field ADDs |
|---|---|---:|---:|
| 1 | {7:2} | 14 | 1 |
| 2 | {1:4,6:2} | 16 | 4 |
| 3 | {2:4,5:2} | 18 | 4 |

All six native occurrences for f=2,3 are charged, even when two recipes
coincide. The helper remains a full arbitrary 512-coordinate field;
f-1 is a transition rank, not a reduced physical storage allocation.
The four signed ADDs include precompensation, both helper updates and
delivery. An implementation with signed ADD primitives needs no
separate scalar NEG for those signs.

Rank-r lowering means an actual r-axis Fourier-type native child
between two monomial maps. There are consequently at most four such
map occurrences for f=1 and twelve for f=2,3 in the unfused lowering.
These are paid occurrences, not free renaming. A monomial map
`|z> -> i^phi(z)|Gz+b>` can be implemented by phasing coordinates and
rotating address-permutation cycles. There are at most 511 swaps and
512 Gaussian-unit multiplications per map; each swap uses three complex
ADDs and one NEG. Address arithmetic and cycle discovery are also paid,
and a generic constant-space cycle-leader scan can cost quadratic
binary-address work. Alternatively an output array is charged as
storage and copying. No free execution of an unsimplified native
history is licensed by the rank-zero adapters.

The sample compiler receipts give explicit monomial maps for the
twelve replayed transition instances. The all-edge proof supplies
actual ranks and interfaces; it does not pretend that every distinct
adapter was separately lowered, optimized or scheduled. These local
invoices do not establish a global power moment.

## Exact fixed-source-batch maximum

Define the complete 112-by-112 binary matrix
`M_st=p_s·O p_t`. For this screen we stipulate the triangular-zero
source-batched model: a valid order is a sequence of distinct vertices
with `M_ab=0` for every earlier a and later b. The matrix includes all
port pairs, including pairs that are not old orthogonal correction
edges. No equivalence with every physical source-batched realization
is assumed.

The dynamic program considers each possible first vertex v and
recurses on the remaining mask intersected with its zero-neighbor
mask. This recurrence is exact by deleting or prepending the first
vertex of an admissible sequence. For pruning, define compatibility
when the two directed entries are not both one. Every admissible
sequence is a clique in this undirected graph. A deterministic greedy
partition into independent color classes gives a valid clique upper
bound. A branch is skipped only when one plus that upper bound cannot
improve the current witness. Thus the coloring does not change the
exact recurrence's maximum.

The complete computation visits 259,479 cached states and returns

```
maximum = 8
witness = (93,27,87,60,59,57,101,6).
```

The witness entries are zero-based indices in the pinned ordered port list,
not the binary port vectors themselves. The complete matrix, witness and state
count are retained. This maximum
belongs to this O and source-batched triangular-zero contract. Arbitrary
edge interleavings, changed compensation graphs, other O and altered
source-access contracts are outside it.

## Separate historical changed-terminal screen

There is also a favorable screen for the different helper contract
`Q_t -> Q_s perpendicular`. For every old legal edge, orthogonality of O
gives `Q_s·Q_t=p_s·p_t=0`. The source line Q_t therefore lies in the
nondegenerate eight-dimensional terminal cap. Its actual phase operator
`T_(Q_s perpendicular) T_Qt^-1` has rank seven by the projector-difference
argument above. This helper is not returned to its original physical
state.

Assume the old model allocates one separate helper to each nondirect
edge and retains two rank-seven data boundaries for every one of the
112 ports. Even removing all 104 direct contacts leaves

```
helpers = 5824-104 = 5720,
helper rank mass = 5720*7 = 40040,
data rank mass = 224*7 = 1568,
total rank mass >= 41608.
```

Under the separately stipulated old 65-dimensional normalization with
896/9 productive calls, the zero-rate capacity is
`65*(896/9)=58240/9`. Exact integer cross multiplication gives
`9*41608-58240=316232>0`. This favorable old one-helper-per-edge screen
already fails before other paid work is included. The receipt retains
the exact integers and verifies every relevant Q_s/Q_t orthogonality.

The assumption of a separate helper per nondirect edge is part of this
screen, not a lower bound for shared-helper methods. Its changed terminal
is distinct from the physically restored isolated contact proved above.
It is not a contradiction between the two invoices and makes no new
multiplication-bound claim.

## Controls, reproduction and precise limits

Fourteen actual mutated candidates run through production predicates:
one-bit O corruption, self pairing, omitted rank-three extension,
reversed schedule prefix, and at each f=2,3 omitted helper return,
omitted dirt precompensation, wrong delivery sign, global phase i,
and omitted scalar accounting for a physically cancelling ADD pair.
Each rejection matches the intended error exactly. Each same production
guard is then disabled and the corresponding candidate executes to
acceptance, outside the rejection catch. Boundary deletion removes
only the selected output-field comparison. The global phase controls
carry a concrete character witness, so tableau-only acceptance cannot
mask their error. Deletion probes are scoped guard-sensitivity evidence,
not a claim that all other whole-pipeline checks are removed.

Run with an unused output path:

```
python3 check_geometry.py --ports CANONICAL-WORD.json.gz \
  --compiler clifford_exact.py --output /tmp/fresh-GEOMETRY.json
```

The exact authenticated compiler byte buffer is compiled with
`dont_inherit=True,optimize=0`. Outer Python optimization cannot disable
its internal assertions. The checker itself uses explicit exceptions.
Normal and `python3 -O` outputs are byte-identical. Runtime outputs
include neither paths nor timings and cannot overwrite an existing file.

The endpoint proof owns the physical positive-C entrance translations,
canonical-to-chosen frame gauges and B4 controller. Those endpoint
adapters remain separate paid interfaces. The contact proof above
uses its explicitly chosen T frames.

These isolated words cannot be concatenated without checking and
charging the actual shared source and target frame histories. No old
408-helper stock, global correction schedule, caller histogram,
precision/rounding bound, fixed-tape implementation, formal-kernel
proof or improved multiplication bound follows from this package.
