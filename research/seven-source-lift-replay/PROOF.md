# Independent two-stage native replay of the filtered L=20 exclusion

## Exact scope

This package independently enumerates the candidate lifts needed to rule
out a restored seven-source length-20 word with profile `(4,4,4,2,2,2,2)`
covering all 98 nonzero masks of weight at most four. It was implemented
from the model/results in PR4207's README and CENSUS at head
`5da1b72f18915820618d14905ad01422ec0a8246`, without reading its census.c,
run_census.py, verify.py or another native checker.

The route is a five-source projection followed by two insertions. It
does not rerun the predecessor's other L=16/L=18 native censuses, establish
its full 218-call minimum from scratch, alter the connector model, or
provide a multiplication supplier or new kappa.

The reported maximum 95 and 940 maximizing lifts concern **only raw
candidate lifts from full-56 six-source projections**. They are not a
global maximum or global maximizer count over every length-20 profile
word. This distinction is necessary to state the finite result correctly.

## Connector and coverage contract

A source word w of length L has symbols in `{0,...,n-1}`. Let

    q_0=0, q_(i+1)=q_i XOR (1 << w_i).

The program rejects a word unless q_L=0, equivalently every source has
even multiplicity. The available target masks are the nonzero pairwise
differences of prefix states `q_0,...,q_(L-1)`. These are exactly the
states used by the native implementation. Because q_L=q_0 for a restored
word, appending q_L would only duplicate an existing state, but the
implementation does not need that alternative convention.

Unordered pairs suffice, because XOR is symmetric. Repeated prefix
states produce zero, which is not a target. Masks of weight greater than
four are also ignored. Five, six and seven sources respectively have
30, 56 and 98 weight-one-through-four targets. The implementation builds
a fixed 128-entry target-bit table and accumulates two standard uint64
coverage words from prefix-state pair XORs. Its population count is
unsigned standard C++ arithmetic, not a floating computation or tolerance.

The model is F2. Sign reversal is the same operation and is not a valid
negative control. An order swap can change the prefix-state set and is
tested as a negative control instead. No integer signed-word equivalence
is inferred from this binary statement.

## Projection necessity

Delete all occurrences of one source s and project every parity state
by forgetting its bit. Original projected states are precisely states of
the shortened word, with repetitions when a deleted event was crossed.
Every originally covered nonzero mask avoiding s remains a difference
of two projected states. Consequently, a full target cover projects to
a full target cover on every remaining source set.

For the exceptional seven-source profile `(4,4,4,2^4)`, deleting a
fourfold source leaves `(4,4,2^4)` on six sources. A full 98 cover would
therefore have a full 56 cover in that projection. Deleting either of the
remaining fourfold sources leaves a full-30 five-source word of profile
`(4,2^4)`. These are necessary filters, rather than an assumption that
all other words have the same measured maximum.

## Stage one: complete five-source classes

The native recursion enumerates restricted-growth words: the first new
symbol is zero, the next previously unseen symbol is one, and so on.
On introducing a symbol, it assigns either the one unused multiplicity
four or one of the four indistinguishable multiplicities two. Existing
symbols may be appended whenever their individual remaining count is
positive. Both introduction possibilities are explored; the fourfold
symbol is **not fixed to label zero**.

Every source-relabeling class has exactly one such first-appearance
representative. Its introduced symbols have uniquely determined total
multiplicities, so there is exactly one recursion route to that word.
Conversely every completed route has precisely the required profile.
The number of representatives is

    12! / (4! (2!)^4 4!) = 51,975.

No cyclic rotation, reversal or word-order symmetry is factored out.
Coverage is evaluated on every class; only full-30 words seed stage two.
The full histogram and the count of full-30 seeds are emitted, rather
than assumed from a retained receipt.

## Stage two: all full-six classes with explicit multiplicity

For every full-five seed, insert a new source exactly four times at
each of the C(16,4)=1,820 position subsets. The relative order of all old
events is preserved. Every resulting word has profile `(4,4,2^4)`.
The program evaluates all these candidates and keeps only full-56 words.
It canonicalizes them afresh by first appearance and stores each
16-event sequence in a 48-bit integer, three bits per symbol, first symbol
most significant. A sorted map gives a deterministic sorted canonical
word list and an explicit multiplicity count.

This route covers **every** full-six class. Delete either of its two
fourfold symbols; projection necessity gives a full-five class, present
in stage one. The deleted symbol's four positions define a unique lift
of that canonical five-source representative, after source renaming.
Both choices are represented.

Each canonical full-six word is emitted exactly twice: once per choice
of its newly inserted fourfold symbol. For a fixed deleted symbol, the
deletion word and its canonical renaming are unique, and the insertion
position set is unique. Since every source occurs, no nonidentity source
permutation fixes the literal word. Thus there is no additional label
stabilizer multiplicity. The program checks the multiplicity histogram
instead of merely dividing the raw count by two without evidence.

The native full run reports the number of raw candidates, raw full covers,
unique full covers, the coverage histogram and all sorted packed full-six
words. The complete target for this stage is 17,152 raw full covers,
8,576 unique classes and the multiplicity histogram `{2:8576}`. These
numbers are checked after actual enumeration, not read from a supplied
core list. An independent code path can compare that complete list.

## Final lift: complete candidates for a full seven-source cover

For each of the 8,576 full-six classes, insert a seventh source exactly
four times at every C(20,4)=4,845 position subset. This executes

    8,576 * 4,845 = 41,550,720

raw candidate lifts. The final word is not canonicalized or deduplicated:
the predecessor's candidate-lift count and maximum-count convention are
raw lifts. Source relabeling does not change mask weights or coverage.
Every possible full-98 seven-source class has at least one such lift by
projection necessity, so zero full covers in this candidate set excludes
all full covers in the complete exceptional profile.

The actual native run must check: no full-98 lift, candidate maximum 95,
and exactly 940 raw candidate lifts at that maximum. It emits the full
candidate coverage histogram and a deterministic first maximizing witness.
These values are not used to prune the traversal.

For words without any full-six projection obtained by deleting a fourfold
source, the simple projected ceiling
is at most 55 masks avoiding a deleted source plus 42 masks containing
that source, hence at most 97. Words with a full-six projection obtained
by deleting a fourfold source are among the candidate lifts and have the
enumerated ceiling 95. Thus the entire
profile has a valid upper bound 97 and no full 98 cover. This argument
does not establish whether 97 is attained, or claim 95 as the complete
profile's maximum.

## Execution, controls and limits

`census.cpp` is single-threaded standard C++17 with standard-library
containers. It has no imported predecessor module, external core list,
third-party library, random sampling or allocation proportional to all
41.5 million candidates. A lift uses one reusable word buffer; retained
storage is the five-source full seeds, the 8,576 packed six-source
classes, small histograms and a final witness. Output includes the
complete packed six-source list for cross-checking.

`--quick` runs controls only and is explicitly labelled quick-only. The
full default performs every enumeration above. Controls check the
retained restored length-22 full-98 witness; the retained length-18
weight-three cover with 63/63 versus only 91/98 for weight four; a known
full-six word; an order swap that reduces coverage; and unrestored-word
rejection. These controls do not replace the full census.

Source bytes are frozen before the full native run. Receipts record the
actual compiler version/arguments, exits, runtime, peak child RSS and
source hashes before/after. A later cold compile/replay is separate
verification. This finite exhaustive computation is not a formal-kernel
proof, an audit of the historical billion-class rows, or validation of
the full multiplication theorem.

## Credit and open next questions

Credit Nick Petalas/PR4207 for the length-20 projection argument, first
native result, explicit request for a second implementation, and specific
suggestion of the five-source (51,975)-then-lifts route; and
nightangelflowerwin-ops/PR4079 and PR3780, commdata2338/PR2397,
Cinna Davis/PR2229/PR2236 and Ross Richardson/PR943 for the retained
connector/projection and readout-cost lineage. This package adds the
independent five-source-then-two-lifts native replay and complete core-list
comparison interface. Substantial OpenAI Codex assistance; Apache-2.0.

Open next questions are the separately requested independent L=18
billion-class replay, downstream uses of the older 216 planning floor,
and mechanisms outside the fixed connector alphabet. None is completed
or imported into this bounded L=20 replay. No merge or selected-frontier
change is part of this contribution.
