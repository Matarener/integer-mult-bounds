# Exact composition and complete invoice

All three ingredients start from the same pinned PR5580 word. Event indices in
`construct_parent` refer to that immutable source, not an already edited list.

## The corrected relay and commuting cascade

PR5605 replaces owned738's deliveries into public203 and public148 by the
earlier public587 relay. Its signal has the form `2P+N`, where
`N=x587-4x734` consists of arbitrary original inputs. The initial nilpotent
correction `I-uN` and its explicit inverse cancel the nuisance; 18 coframed
late ADDs restore the full-frame residuals. The published construction is
retained and regenerated exactly before composition.

PR5565's commuting cascade changes other scalar contacts and raises helper531's
productive rank from eight to nine. The retained generator is independently
regenerated and compared to its published word. Its edits and the relay edits
occupy disjoint intervals of the original event sequence. The verifier merges
those literal edits independently of `construct_parent` and compares every
word field. Disjointness alone is not used to infer correctness: the resulting
735-input word must also pass complete exact scalar/frame/ownership replay.

## Applying independent helper splits

Use Ali Romman's retained PR5599 split construction. For a prefix matrix P,
suffix matrix S, and a chosen common intermediate chart, a witness supplies
row a, column b, and boundary vectors c,d with

`a P = c`, `S b = d`, `a b = c d = 1`.

Both boundary vectors belong to one helper group with the same initial and
final charts. Explicit ordinary basis operations isolate this one channel at
the initial boundary and at the cut. The old independent input finishes at
the cut, while a newly introduced independent input runs the remaining suffix.
The final basis operations restore the independent endpoint interface. No
new Gaussian call, COPY or CLEAR is introduced by the split itself.

The original 15 witnesses are ordered. Original numbers 12 and 15 need pivot
visits to line597 removed by the cascade; those witnesses and their credits
are omitted. For the remaining 13, all rational vectors, pivots, charts and
split ranks are identical to the source. Only `cut_after` changes.
The verifier checks the full equalities above over every current public and
owned coordinate at each evolving cut, then replays all rows after that split.
This matters because a split basis can interact with later relay cleanup; the
old six-row residual description is not blindly transferred to the split word.

The final independently counted inventory is 748 public inputs and 540 helpers,
with the same eight owned lifetimes and peak one. Every extra input remains an
independent degree of freedom. A zero-dimensional chart never means a
zero-valued helper. All 25,502 events and every changed native map are checked.

## Signed bill and pricing

Against PR5599 the local paid and target changes respectively are

`Delta paid = -9H1-H2-2H3-2H4+4H5+H6`,

`Delta target = -2H1-H4+H5-2H8+2H9`.

The unchanged physical caller invokes the local word 18 times. All main banks,
queries, whole idles, adapters, routing and normalizations remain charged.
The resulting complete bill has 66,690 paid calls, 13,048 targets and unchanged
rank surplus 760. In particular, omitted split targets are not still credited.

The retained PR5599 price implementation independently recounts this bill,
encloses the raw crossing with its primary exact rational interval engine,
independently checks interval overlap and positive funding at the tested
endpoint with a second engine, and checks the completion tails, uniform
compiler and all 58 outer predicates at 0.0031018405. It retains decay 39/40 and compiler
power 1024. The reported claim is 0.00310184. Its exact raw crossing is
(0.00310184254783,0.00310184254784); a negative derivative bound on [0,0.0034]
makes this the ceiling for this invoice under the inherited BIT cap.

The finite certificate and conditional calculation preserve the inherited
framework assumptions listed in README.md. They do not establish a new
unconditional multiplication theorem or a universal optimality result.

Prepared for flyingviper with substantial OpenAI Codex assistance and independent
agents, preserving the predecessor attribution in README.md. Apache-2.0.
