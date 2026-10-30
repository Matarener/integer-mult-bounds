# Rational recoding and shared-boundary limits for P104 owned values

All assertions below are about the literal PR5580 word at head
`6efa248cf456d6101d757e9d09ba29711d18a13a`. They do not assert a new
construction, global optimum, native implementation, or multiplication bound.

## 1. A complete classification of the unchanged producer span

Let `D_0,...,D_7` be the eight public scalar rows copied into owned fields
735 through 742. Rows are rational covectors on **all 735 arbitrary public
inputs**, including the original zero-frame helper inputs. The verifier
reconstructs the prefix from the identity, rather than assuming those helper
inputs vanish. It confirms that these producer values do not change between
the first owned INIT and their respective COPY events.

For a covector `x`, define its original-entry support to be the binary span
of the original entry frames of inputs with nonzero coefficient in `x`.
This is a property of its covector, not an assertion that `x` can be built
at that frame with no paid work.

Every proper subspace of the ambient `F_2^9` lies in a hyperplane `ker(h)`
for some nonzero binary normal `h`. For each of the 511 normals, project
the eight rational covectors onto original input coordinates whose entry
frames are not contained in that hyperplane. A combination `sum a_i D_i`
has support inside the hyperplane exactly when its coefficient vector `a`
is in this projected matrix's rational kernel.

Exact Fraction elimination gives 495 matrices of rank eight and 16 of rank
seven. The latter have one-dimensional kernels. Every listed kernel mode
has support dimension exactly eight, checked by binary elimination. Hence:

* No nonzero rational combination of the unchanged producers has
  original-entry support dimension at most seven.
* Exactly 16 projective combinations have proper support: the eight
  original producers and eight mixed modes listed in RESULT.json.
* Every other nonzero combination has support dimension nine.

This is an exhaustive rational statement, not a bounded coefficient search.
The independence minor below also excludes a nonzero coefficient vector
representing the zero covector.

## 2. Direct nested delivery does not remove an original mode

Let `L_i` be the fixed one-dimensional final delivery frame for `D_i`.
A mode with support hyperplane `ker(h)` can descend directly from that
hyperplane to `L_i` only if `h` annihilates `L_i`. The verifier tests every
one of the sixteen classified modes at every final delivery line.

After removing `D_i`, exactly three mixed modes remain eligible at `L_i`.
Their coefficient vectors have rational rank three; adjoining the unit
vector for `D_i` raises that rank to four. RESULT.json records an exact
separating functional for each destination, annihilating all three
alternates and taking value one on `D_i`.

This obstruction survives arbitrary corrections from original inputs
whose entry frame is zero. The eight producer covectors restricted to
nonzero-entry inputs have rank eight, witnessed by the explicitly checked
minor on columns `[0,1,2,4,5,6,9,12]`. Therefore a producer combination is
a zero-entry-input correction only when all eight coefficients vanish.

This is a direct nested 8-to-1 delivery obstruction in the unchanged producer
span, starting at each mode's original-entry support hyperplane and using
fixed final delivery lines.
It does not rule out earlier owned preparation, intermediate payloads
outside that span, moving through a different recipient schedule, or
changed public dependencies. Nor does an entry-support hyperplane by
itself establish legal preparation of its mixed mode there.

## 3. Joint transport floor across all eight blocks

See [JOINT-BOUNDARY.md](JOINT-BOUNDARY.md) for the independent information-cut
argument and full contract. The interval `[13378,13485)` has 41 public
boundary fields: eight producers and 33 distinct recipients. Their entry
rows have rank 41; the unchanged suffix observes their exits with rank 41.
These verified facts force a replacement using only these public fields
to preserve the exact local map.

The map carries eight independent producer coordinates from dimension-eight
inputs to dimension-one observations. At every dimension threshold 2 through
8, at least eight scalar values must cross downward in owned fields.
Common-frame scalar operations and public ascents cannot create a downward
crossing. The argument allows arbitrary rational dependencies, any number
of zero-initialized owned fields, erasures, and sharing across the blocks.

For `H_r(t)=r^t`, `0<t<=1`, the cut count implies an owned cost of at least
`8 H_7(t)`. The fixed public endpoint changes separately require `31 H_1(t)`.
Thus the shared-boundary floor is `31 H_1+8 H_7`, compared with the source
cost `33 H_1+H_2+H_3+7 H_7`. Their difference is an upper bound on possible
local savings, not an attainable replacement.

The fixed-boundary theorem does not assume that original input symbols
start at dimension eight. They mostly start at dimension zero or one.
Earlier preparation and outside public side information invalidate the
boundary hypothesis and remain meaningful research directions.

## Verification scope

The joint-boundary checker also replays all scalar rows and frame/lifetime
legality of the retained word. It verifies the final map on arbitrary input
values and clear owned outputs. These are finite algebraic checks, not a
proof-kernel verification or a replay of signed native maps, the physical
caller, interval pricing, compiler, BIT stock, or outer analytic framework.
Those unchanged obligations belong to the pinned source and are not newly
claimed here. No selected-frontier file is modified.

Prepared for flyingviper with substantial OpenAI Codex assistance and
independent agent derivations. Apache-2.0.
