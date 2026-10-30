# Literal dense guard-mask scan from an admitted stencil

## Scope and interface

The input is an **admitted** nonempty length-`L` stencil, `L>=1`, over the
fixed finite alphabet below. The output is the complete `M=2^L`-bit BAD mask,
in increasing numerical order of the MSB-first binary address. BAD is the
complement of the conjunction of the stencil's digit and guard tests.
Geometry parsing, interval ordering, threshold generation and admission are
outside this interface. `verify.py` supplies host adapters for those tasks;
their rejection tests do not certify a tape implementation of admission.

There are three reusable physical tape roles: protected stencil, private
counter, and caller-owned mask. Each has a permanent left marker `<` in its
initial configuration and otherwise initially blank cells `_`. The supplied
stencil has its `L` atoms followed by `>`. All heads start at `<`. On success
the stencil is unchanged, the counter's data and allocated right marker are
blank again, and the mask has `M` output bits followed by `>`.
Every head returns to `<`. The permanent left infrastructure is retained.
The caller must consume/transfer and clear a previous owned mask before this
same output role is reused; the theorem does not allocate a new physical
tape for each invocation. Source/payload streams are not among these roles.

An atom is `(kind,begin,end,lower_bit,upper_bit)`, with kind in `{S,D,G}`,
two Boolean boundary flags and two bits. The canonical S atom is
`(S,false,false,0,0)`. D atoms carry zero threshold bits. Non-S intervals
are ordered, disjoint and complete: exactly one begin and end, of the same
kind, with no intervening S atom. A one-cell interval may begin and end in
the same atom. G atoms contain equal-width MSB-first lower/upper strings.
There may be no intervals at all. This is a fixed product alphabet; an atom
does not contain an integer interval number or a parameter-sized descriptor.

For each D interval, reject exactly its all-ones string. For each G interval
with strings `lo,hi`, accept exactly `lo<=value<hi`. S cells impose no test.
All unmarked address bits can have arbitrary values.

## Constructive program and correctness

`machine.py` gives the complete marker-driven program. Its only tape
operations are current-cell read, current-cell write and one-cell move.
The emulator's numerical head coordinates, allocated-cell lists and action
totals are observers; the program never reads them, a tape length, `L`, `M`
or a host address/position counter. Tuple decoding is a transition on one
finite alphabet atom. All non-tape live values range over fixed finite sets:
bits, the three comparison states, interval kind and Boolean flags. The
fixed-depth helper calls may be inlined into a single finite-state control.
The mutation flags select other fixed programs; they are all false in the
theorem. No callback, E evaluator or source predicate is in the interface.

Initialization copies only the stencil's length, by scanning to `>`, and
writes an equally long all-zero binary counter and its own `>`. Literal
rewinds read symbols until `<`, paying for the boundary test. For each
counter value the two tapes are scanned together from left to right. A D
begin resets `all_ones=true`; every cell conjoins its bit, and the D end
conjoins `not all_ones` into the overall predicate. A G begin resets both
comparison flags to E. The first unequal pair sets L or G and later pairs
leave that flag unchanged. Induction over an interval proves that this is
the lexicographic comparison of its complete MSB-first strings. At its end
the lower flag must be E or G and the upper flag must be L. Thus equality
with the lower bound is accepted and equality with the upper bound rejected.
Each interval's result is conjoined, and S bits are ignored.

Write one BAD bit at the mask head and move that head one cell right. Rewind
the stencil. The counter head is at `>`: move left, replace trailing ones
by zero, replace the first zero by one, and rewind to `<`. If carrying reaches
`<`, return the overflow flag. Standard binary induction proves that the
successive scanned counters are exactly `0,1,...,M-1`, with no repetition or
omission, and that the last carry leaves all counter bits zero. This proves
both the output length and its ordering, without a host loop of `M` steps.

Overflow is not erasure: zero is distinct from blank. A final literal pass
therefore writes blank on every counter data cell **and its right marker**,
then reads/moves back to `<`. Append `>` to the mask and rewind that head.
This restores the exact initial private infinite-tape configuration while
preserving both protected input and owned output. A final fixed control state
discards the transient finite flags. The program has no variable-depth
recursion, indexed geometry lookup or parameter-dependent tape inventory.

## Exact action census and asymptotic tariff

Count each read, write and one-cell move as one action. Finite-control
transitions compile into a constant factor more machine steps, independent
of all parameters. Let `M=2^L`. The following counts are for the normal
program on every admitted stencil; they do not depend on which tests pass.

| Phase | Cell/head actions |
|---|---:|
| Initialization, including first mask move | `8L+11` |
| Predicate scan, BAD append, stencil rewind for all addresses | `(6L+8)M` |
| All counter increments, including final overflow and rewinds | `(2L+5)M-3` |
| Counter data/right-marker blank erasure and return | `5L+6` |
| Mask right marker and return | `2M+4` |

For the carry line, the `M-1` successful increments each read `L+2` cells
and move `L+1` times, including the rewind. Final overflow reads and moves
`L+1` times. The number of carried one bits over the complete enumeration is
`M-1`; there are also `M-1` successful zero-to-one writes. Thus carry writes
are `2M-2`, and its total is `(2L+5)M-3`. This charges every marker read,
counter update and return; there is no free numerical head-zero test.

The resulting exact totals are

```
reads  = (4L+6)M + 5L + 9
writes = 3M + 2L + 1
moves  = (4L+6)M + 6L + 8
total  = 8ML + 15M + 13L + 18.
```

Visited cells, including protected input, output and all markers, are exactly
`(L+2)+(L+2)+(M+2)=M+2L+6`. The finite alphabet has constant encoding size.
Consequently this is one uniform fixed-tape procedure with time `O(ML)` and
visited space `O(M+L)`, from the admitted-stencil interface. The stored
receipt checks the exact census, not a fitted timing bound. Emulator counters,
hashing, source comparisons and host admission are not machine registers or
included action evidence.

For the source's `V=MR` caller, its stated `L=Theta(p)` and `R=Theta(p)` give
`O(ML)=O(V)`. The condition `R>=1` alone would not suffice. This conclusion
prices the detector from its supplied stencil, not a complete source caller.
Its uniform geometry/threshold producer and admission tariff remain an
explicit obligation before composing an end-to-end O(V) implementation.

## Binding the source predicate, without a hidden parity test

The three pinned current-main files are authenticated by SHA-256 and Git
blob hash before loading the source. `check_batched_crt.py:142-175` defines
the same predicate in `good` and `linear_guard`. For `B=2^G`, active digits
are the low `rG` bits of each H-bit u/t field, split into G-bit digits; each
must differ from `B-1`. For target arithmetic position j, the guard is

```
g = (y >> (j+1)) mod 2^(K-1),    2B <= g < 2^(K-1)-2B.
```

The parity bit at j is excluded. Under the explicit physical address order
`u_H | t_H | y_Y | w_W`, with each field MSB-first, digit i of either control
field occupies `[field_start+H-(i+1)G, field_start+H-iG)`. The guard occupies
`[2H+Y-j-K, 2H+Y-j-1)`, width `K-1`. Encode its two thresholds in that width.
All other cells, including inactive high control bits, target parity bits,
unused Y cells and the complete optional w field, are S. The host adapter
requires complete disjoint `[j,j+K)` target segments and `H>=rG`.
These formulas prove equality with the source for every padded address of
any admitted geometry, independently of the finite tests.

The finite fixtures are predicate projections, not full production
three-reservoir invocations: `(G,H,Y,K,targets,W)` is `(1,2,10,5,[0,5],0)`,
`(2,3,9,7,[1],0)` and `(1,1,5,5,[0],1)`. They exhaust all 49,408 addresses,
including dirty compact digits, guard boundaries, parity and spectator bits.
The two source functions agree with every literal output bit. All-S stencils
at `L=1,2,3` separately cover the no-test and smallest-overflow boundaries.
Negative controls alter lower/upper strictness, MSB significance, unadjusted
whole-K thresholds, output return and the counter's least significant bit.
The whole-K mutant keeps the K-1-bit numeric thresholds unchanged; properly
rescaled full-segment thresholds can represent the same guard and are not
claimed wrong. Host malformed-input rejection controls are admission-adapter
evidence only. Optimized Python retains every verifier check via explicit
exceptions rather than `assert`.

## Predecessors and remaining obligations

Cinna Davis already proposes this counter/ordered-descriptor scan and its
three-state comparisons in current-main `CRT.md:238-253`. This package
contributes the literal finite-control lowering, complete ownership/cell
census and source-bound executed checks; it claims no new guard mechanism.
Hiroki KUMAZAKI (@kumagi), PR4169 head
`835c3563ee7ede8ceaf329ede7372e50f7823136`, gives the arbitrary-source repair
predicate/proof and leaves guard-scan/function/sort costs open. PR4174 head
`5fec853f0c048871de3b8098d1e30d4ee19cda23` gives reservoir placement and
ordered descriptors while leaving their fixed-tape tariff open. Their
mechanisms and other source ancestry retain credit; neither open PR is
imported here. Douglas Colkitt/OpenAI's stream and compact-control framework
and all retained source notices remain unchanged. This work has substantial
OpenAI Codex assistance, Apache-2.0; no new formal-kernel or independent human
review is claimed.

Still outside certification: uniform geometry/stencil production/admission,
transported caller descriptors, extraction/reinsertion and sorting, E work on
exceptional keys, switch-table/arithmetic evaluation, payload routing, repair,
ordinary callees, numerical precision, native/outer composition and a new
kappa or multiplication theorem. No selected-frontier change follows.
