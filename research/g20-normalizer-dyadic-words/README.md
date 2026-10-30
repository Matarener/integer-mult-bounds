# Constructive dyadic words for G20 port normalizers

This supplies explicit operation words for all 111 exact port normalizers
`W` and `W^-1` retained by Ali Romman's PR #5798 at
`eaa9cc8c15d8e994d7b81b0cda3f6dd63b0db826`. The source audit already
checks the matrices. This contribution constructs finite words and a declared
address-kernel embedding; it does not claim the native construction or a new
conditional bound. [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5777#discussioncomment-19204776).

Both directions together contain **5,960 ADDs and 2,174 SCALEs**. Every scale
is a signed power of two; all ADD coefficients are dyadic. The largest
absolute numerator or denominator is 4. Swaps are explicitly lowered to
three ADDs and one sign scale. The unit-preserving Euclidean construction
never divides by an odd nonunit. Classical elimination is not claimed as a
new general theorem.

The serialized convention is **RIGHT**: `I E1 ... Em = W`, where
`ADD[i,j,a] = I+a e_i e_j^T` updates row coordinate `j` from `i`. The
inverse word reverses the word and inverts each factor. The source's column
identity is separate: `W` maps the central coordinate axis to the local line,
and `W^-1` maps that line to the central axis. No automatic entry/exit
choice is inferred from the word names.

The chosen compatible 127-coordinate layout uses central coordinate 0 and
one seven-coordinate block for each of the exact 18 thick-stage positions.
A stage uses its **position** in the retained list, not its raw stage ID.
Each placement fixes 119 spectator coordinates. For `N=127f`, a right
factor uses addresses `half*N^2 + row*N + column*f + lane`, across every
one of the N matrix rows and f lanes, on two disjoint address halves.
This is a declared layout, not the retained literal physical head map.

## Exact evidence and conditional cost

[RESULT.json](RESULT.json) retains every forward/inverse word, source
port/line/complement binding, coefficient histogram, layout, positive named
call counts and six targeted rejection controls. [ORACLE.json](ORACLE.json)
records independent dense elementary-matrix products, separate basis-row
execution and both round trips: 222 checks of each kind. Its flattened
address checks cover all 18 layouts at f=1 and f=2.

A catalogue cross-product over all ports, stages, halves and both words has
7,992 kernel instances. **This is not an actual paid-event incidence count**
and no event is presumed to equal one word. Both directions are already in
the word histogram. Per coefficient, lifting it to the full catalogue
multiplies its count by `18*2*N*f = 4572*f^2`. At f=1 this gives 27,249,120
`ordered_shift` and 9,939,528 `unit_scale` calls. Each coefficient retains
its own positive named primitive tariff; none is assigned zero or a universal
unit price. Each symbolic tariff may depend on the radix, width and tape parameters; no uniform implementation bound is supplied. This is not absorption into the source's finite fee.

The named P2 ABI is pinned to the current-main
[ROW generator](https://github.com/CrocSwap/integer-mult-bounds/blob/de5ec2e7a6074068452f45b1a191b5c72832df4a/research/bit-row-route-generator/generator.py).
Its implementations, coefficient preparation and physical tape tariffs remain
contracts. Full ROW borrowing, old-low cache COPY/CLEAR, carries, low-type
commit, padding, return, ownership and caller integration are outside this
kernel certificate. The full supplier and five inherited framework
assumptions are not admitted here.

## Reproduction

Python 3.12 and the standard library suffice. Neither checker imports the
other or any predecessor implementation. Frozen source data authenticate
by SHA256; the independent oracle also checks their Git blob identities.

```sh
python3.12 -B scripts/research_package.py --package research/g20-normalizer-dyadic-words
```

The primary generator/replayer uses unit-only elimination; the oracle
consumes the retained words and independently checks RIGHT products,
basis-row semantics, address isolation and positive per-coefficient counts.
Default runs compare complete canonical JSON receipts, including numeric
type distinctions. `--emit` is an explicit candidate-generation mode and
never writes files. The six controls remove an operation, reverse word
order, insert a forbidden odd scale in the chosen unit alphabet, corrupt
source bytes, write a spectator and confuse raw stage ID with position.
They are injected faults, not defects alleged in predecessor code.

[SOURCES.json](SOURCES.json) pins the exact data and main-context ABI;
[TASK.json](TASK.json) records the changed finite constructive scope and
source-bound budget. No Lean build ran. The selected baseline passed source
bindings/metadata only; no selected native replay or frontier change.

## Open next questions

Bind one exact kernel direction and paired owner to the complete retained
ROW route, including all old-low cache, carry, type-commit, padding and
restoration costs. Prove the literal physical head-map correspondence and
actual route incidence before treating the catalogue counts as a caller
invoice. Physical P2 preparation/tariffs and compiler/stock/precision/tape
obligations remain blockers. The structured next question is in TASK.json.

## Credit

Ali Romman with OpenAI Codex assistance supplied the G20 source audit and
normalizer witnesses. Retain Dugongue, ai-nanachi, the PR #5679/#5708
construction, PR #5782 native audit and all predecessor credit in NOTICE.
Joyboy Brian with Codex assistance supplied the retained ROW generator and
P2 schedule; its predecessors retain their credit. New finite words and
certificate: ToikY with substantial OpenAI Codex assistance, using separate
primary, independent-oracle and read-only proof/review contexts. Apache-2.0.
