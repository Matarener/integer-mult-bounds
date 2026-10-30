# Exact isolated-exchange floor for the G20 boundary

## Model and quantified statement

Work over F2. An ADD is the reversible instruction `x_d <- x_d + x_s`,
with distinct source and destination and unit scalar cost. A bank consists
of two arbitrary independent scalar wires. An isolated bank-exchange module
has exactly four wires, no scratch, no reset, and any finite ADD word.

Allow arbitrary invertible entrance and exit bases within each bank. Every
resulting exchange endpoint has matrix

```
       [ 0  A ]
M  =   [ B  0 ],       A,B in GL(2,F2).
```

There are 6*6=36 distinct such maps. Conversely, all 36 can be obtained by
local bank bases around an ordinary bank exchange. Granting independent A,B
is a relaxation of the source's compatible global basis constraints.
All instructions needed to implement the resulting four-wire map are counted;
local basis changes are not additional free instructions during the word.

**Finite statement.** Every one of these maps needs at least six ADDs.
Their exact shortest-length distribution is `{6:2, 7:8, 8:24, 9:2}`.
The certificate contains an attaining word for each map. The two ordinary
coordinate-pair exchanges, with matching straight or crossed orientation,
attain six by two disjoint three-ADD swaps.

## Complete certificate and independent check

Encode a 4-by-4 binary matrix by its four 4-bit rows in successive nibbles.
`distances.bin` has one byte for every encoding from 0 through 65535.
Singular matrices carry sentinel 255. Identity is 0x8421. The generator uses
left row additions in a breadth-first traversal and stops when its queue is
empty. Its state count is 20160 = (16-1)(16-2)(16-4)(16-8).

The checker does not import the generator or run BFS. It:

1. Classifies every one of the 65536 encodings independently by column spans.
2. Requires exactly the invertible matrices to have finite labels, with the
   identity as the unique zero.
3. Enumerates all twelve **right column-addition** neighbors of every finite
   state, checking graph closure and `|label(M)-label(ME)| <= 1`.
4. Checks a neighbor with label one smaller at every nonidentity state.
5. Enumerates the 36 anti-diagonal block maps independently and checks each
   supplied word on all sixteen Boolean inputs.

The Lipschitz condition proves the lower bound: labels can rise by at most
one along any ADD word starting at identity. Descending labels terminate
at the unique zero and certify an equally long word, since ADD is an
involution. Right multiplication suffices: products of the same twelve
generators enumerate the same set of length-k words as left multiplication.
Thus these are exact finite shortest distances, not a failed bounded search.
The graph has 241920 directed edges, diameter nine, and levels
`1,12,96,542,2058,5316,7530,4058,541,6`.

The five semantic controls falsify a six-distance exchange label to five,
substitute a singular matrix while preserving inventory cardinality, delete
an attaining ADD, break an equal-target pair, and change a source exchange
wire. They must fail. Explicit exceptions keep all checks active under `-O`.
These executable checks are not a proof-kernel formalization.

## Source application and complete cost of the stated class

The immutable source is Ali Romman's PR5840 at
`6a043d0fc0199ee5b24c61f883f1943eaf6424be`, file
`research/g20-target-pair-boundaries/CONTROLLER.json`.
The vendored file's Git blob and SHA256 are in SOURCES.json. The source
boundary is fourteen ADDs followed by eight SWAPs, with inverse left boundary.
Those SWAPs partition into four disjoint whole-bank exchanges:

```
(7,15), (8,14), (9,13), (10,12).
```

Each component is already attained by six ADDs. The checker joins the actual
wire operands to these four components, checks every target pair has equal
polynomial, and replays both 32-by-32 boundary matrices and their inverse.

Consider only circuits that keep the fourteen chain ADDs as paid fixed
instructions and implement each exchange using its own four wires, permitting
arbitrary local invertible bank bases. There is no gate sharing with the chain
or other components. Interleaving gates from disjoint exchange components
does not change the additive cost. The optimistic complete scalar invoice is

```
one side:                14 + 4*6 = 38 ADDs
boundary and inverse:    2*38     = 76 ADDs per port
111 independent ports:  111*76   = 8436 scalar ADDs.
```

The source attains this floor. Any separately required basis setup, delivery,
copy, restoration, frame changes, recursive children or physical implementation
fees are nonnegative; omitting them favors the candidate and still gives no
scalar saving inside this class. No scratch or erased state is granted. The
source's paid recursive profile and productive target credit are unchanged.
There is no new supplier admission, runtime benchmark or kappa claim.

The factorization restriction is essential. In particular this does **not**
cover arbitrary GL2 bases placed before the entire boundary: such bases can
change the chain and its interfaces. It does not cover synthesis mixing a
chain operation with an exchange, cross-component gates, added scratch,
joint synthesis of both boundaries with the core, a different controller,
nonunit tariffs, or vectorized physical cost sharing across ports. The
8436 figure counts the source's scalar per-port instruction model.
No global 32-wire CNOT minimum is proved.

## Dependencies and scope of acceptance

The finite four-wire theorem uses only exact F2 arithmetic. Its source
application depends on the authenticated controller and the stated scalar
instruction model. The full PR5840 physical caller, native maps, source
descriptors, compiler fees, stock and precision were not independently replayed.
No claim from that source is promoted to accepted status by this package.

The selected result remains conditional kappa 62009/20000000 = .00310045,
with all five assumptions: native all-column realization, owned erasure,
compiler closure, precision/fixed-tape execution and analytic recovery.
The full multiplication theorem and rounded machine remain outside this work.

## Credit

Ali Romman supplied PR5840's target-pair boundary construction and released the
general-basis question in Discussion5804. Retain PR5834's caller, PR5807/5828's
scalar synthesis, PR5708/5671, ai-nanachi PR5512, Dugongue, ToikY and the
native/controller/compiler/BIT lineage. No predecessor synthesis code is
imported here. BFS, elementary transvections and the three-ADD swap are
standard methods, not claimed as new. The new contribution is the complete
36-endpoint certificate, independent graph-label checker and its scoped
application to the actual four source exchanges.

Charan ., with substantial OpenAI Codex assistance; no subagents or independent
human/kernel acceptance. Apache-2.0.
