# A shared dirty public relay for two P104 owned deliveries

This note describes the scalar and frame mechanism for the exact PR5580 word
at head `6efa248cf456d6101d757e9d09ba29711d18a13a`. Source event numbers below
refer to that word. The scalar argument below is complemented by the package verifier's complete
native, ordinary-cost, productive-credit, caller and analytic predicate checks.
Their inherited theorem assumptions remain as stated in the README.

Let `P` be the unchanged public row133 copied into owned738. That owned field
holds `-P/2`. Its three higher contacts add `P/2` to159, `-P` to203, and `-P`
to148 before it reaches its final line597. We retain the159 contact and replace
the other two contacts by one joint correction in the later public circuit.

## The public relay

The original public row734 at line597 is `x734-P/2`, where `x734` is its
arbitrary original zero-frame input. Public row587 is unchanged before its
first ascent, so after its original ADD from734 it contains

`x587 - 4 x734 + 2 P = N + 2 P`, with `N = x587 - 4 x734`.

The last read of587 while it is at zero is source event13610. Consequently
its original events14633â€“14634 can be moved immediately after13610. The
relay's next original frame773 contains frame652, so split its original
line597-to773 ascent through652. At frame652, immediately after source
event14010, insert `ADD 21,587,+1`.

An exact rational suffix propagation gives the following useful identity:
omitting the203 and148 owned reads, then inserting `2P` into21 at this
point, leaves every non-full-nine-dimensional final public row unchanged.
The actual relay inserts `2P+N`, so its only remaining error on those rows is
`u N`, where

`u = (e123 - e148 - e175 - e182 + e203 - e223)/2`.

This is a joint identity. Neither owned contact is deleted on its own, and
the relay is allowed to change an intermediate public dependency.

## Exact treatment of the arbitrary nuisance inputs

No helper input is assumed zero. All six fields in the support of `u` start
at the zero frame. The full unchanged word maps their initial-direction
combination `u` to the same combination on its non-full-nine-dimensional
outputs. Also `N(u)=0`, because `N` uses only input fields587 and734.

Precompose the word with `I-uN`: for each of those six initial fields,
subtract its coefficient in `u` times `x587-4x734`. Twelve explicit
common-zero-frame ADDs implement this transformation. Its source fields
are disjoint from its destinations, so sequential implementation has no
feedback. The inverse is `I+uN`. This cancels the entire `uN` output error
for arbitrary values of all735 public inputs.

After this preconditioning, compare the two words immediately before the
original event24461, the first late cleanup update of row133. Exactly six
public rows differ:

* Rows21 and47 have an extra `P+N/2`.
* Rows434,435,436,437 lack `P+N/2`.

All six targets and sources133,587,734 are then at the full frame127.
The three sources are exactly `P`, `x587`, `x734`; this is checked from
their full original-input covectors. Eighteen explicit common-frame ADDs
remove the six errors without modifying these sources. The remaining
suffix is unchanged, so every final public row agrees exactly.

## Transport saving and verification boundary

Removing the two owned contacts replaces the owned ranks1,3,2 after159 by
one rank6 descent. The new public587 stop replaces one rank3 ascent by
ranks1 and2. This first changes the complete MOVE histogram by `H6-2H3`.

The removed148 contact also makes its intermediate frame596 unused. Its
original events13416 and14017 are public MOVEs467-to596 and596-to655,
with ranks1 and2. No scalar read or write of148 remains between them.
Remove the first MOVE and replace the second by467-to655, of rank3. A
complete per-role adjacency audit, counting scalar source reads as well as
writes, finds no further unused intermediate MOVE frame in the new word.
The strongest verified complete histogram change is therefore

`H6 - H1 - H2 - H3`.

For `H_r(t)=r^t` and `0<t<1`, this is strictly negative by strict
subadditivity: `(1+2+3)^t < 1^t+2^t+3^t`. This transport comparison alone does not
establish a new full project bound.

The explicit construction adds29 scalar ADDs and removes two MOVEs, for
25167 events compared with the source's25140. It uses
the same735 public fields, eight owned lifetimes, and owned peak1. No new
owned storage or free nuisance erasure is required. Public endpoints,
common frames, containment directions, and cleared owned outputs are
unchanged. Independent exact replay compares all735 original-input columns
and all743 final scalar rows, rather than testing sampled inputs.

The submitted `construct.py` deterministically realizes these edits. The
verifier reconstructs its complete payload from the frozen source and checks
all final rows, signed native maps and the complete caller. The registered
receipt supplies the exact conditional pricing and fixed-invoice ceiling.

Prepared for flyingviper with substantial OpenAI Codex assistance and
independent agent derivations. The underlying P104 word and retained
source lineage are credited in README.md. Apache-2.0.
