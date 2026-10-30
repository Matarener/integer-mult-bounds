# Complete PR2979 source/native boundary

This finite audit checks both complete emitted native streams and all 408
arbitrary dirty-helper outputs of the original PR2979 construction, in both
orientations. It extends PR3038's single endpoint cone and PR3238's all-private
free cone. The source word, allocation and paid costs are unchanged. No new
supplier, kappa or selected-frontier change is claimed.

The precise statement and composition argument are in [PROOF.md](PROOF.md).
[SOURCES.json](SOURCES.json) pins every consumed input to canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. The original
construction is PR2979 at `be191346391661f4d35fc0d1508d0a6029572576`.

## Added coverage

Each complete source stream has 22,748 events. Every native event is selected
from that complete stream, without dependency pruning. Both orientations have
3,481 classes per provider. Against PR3238's exact class union, that adds 833
forward classes and 314 inverse-transpose classes. Those new classes cover
998 and 317 event occurrences. In total, native event coverage increases from
3,717/4,537 to 5,125 in each orientation, adding 1,408 forward and 588
inverse-transpose event occurrences. This also includes new occurrences of
previously checked classes. Existing classes are replayed too. These increments
are relative to PR3238, not claims that every individual identity is new.
The group-A and group-B direct-path audits already cover selected identities.

The new forward observer checks all 408 final helper rows and every actual
private free over exact rational free-warp expressions. A separate retained
backward source-covector algorithm checks every original helper output.
Native classes are checked on all 512 address columns, including global phase.
The residual Fourier factors, all 91 private families and the full local
paid profile remain charged.

A literal helper ADD outside the prior expanded cone can have its sign flipped
while all earlier private-free and helper249 roots still pass. The complete
helper check rejects that mutant. A global-phase fault in a newly covered
native class also rejects. At inverse-transpose event 21,886, the helper ADD
sign change leaves helper287 equal to x287-2*x286 while all older roots pass.
These are semantic failure controls, not defects reported in the original
word. Exact indices, rows and class/event associations
are retained in the two compressed RESULT files.

The source decoder, native selector, exact Gaussian kernel, forward arithmetic
and backward covector machinery are credited reused checking tools. This is a
coverage extension using those independent implementations, not a claim to
have independently reimplemented them.

## Reproduce

Use Python 3.12 with `numpy==2.3.5`, which the unchanged producer requires.
The new proof calculations and exact kernel use the standard library. Run
commands sequentially with an external session-owned temporary directory:

```sh
mkdir -p "$RUN_ROOT/scratch"
TMPDIR="$RUN_ROOT/scratch" python3.12 -Werror -B scripts/research_package.py \
  --package research/rank7-complete-native-boundary
```

The registered hook runs eight behavioral groups, then a fresh source/native
replay for each provider. Direct replay is:

```sh
TMPDIR="$RUN_ROOT/scratch" python3.12 -I -O -Werror -B \
  research/rank7-complete-native-boundary/verify.py --provider base
TMPDIR="$RUN_ROOT/scratch" python3.12 -I -O -Werror -B \
  research/rank7-complete-native-boundary/verify.py --provider extra
```

Each command authenticates inputs before executing retained code, generates
fresh recipes, checks source/event and retained artifact equality, executes
semantic controls and compares the complete deterministic receipt. It prints
`PASS_COMPLETE_SOURCE_NATIVE_BOUNDARY provider=base` or `provider=extra`.
`--emit` prints a fresh uncompressed receipt. `--artifacts DIR` reuses supplied
producer artifacts but still authenticates and checks all identities; that mode
does not claim a fresh producer execution. Replay needs no network or Git.

## Limits

The theorem is conditional on physical rational scalar, COPY/CLEAR and
fresh-zero allocation contracts. Normalized restoration includes paid native
residual Fourier children; it is not a physical identity on every helper's
whole array. Actual backing and owner geometry, movement, storage,
precision/prefix/tape, the complete intended source/target application,
both supplier caps, outer coupling and all-size/compiler/analytic obligations
are separate. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

The next useful step is to join a newly covered helper endpoint and its
recursive residual to the actual owner placement and paid physical scalar
implementation. This determines whether the checked local operator fits the
complete invoice. Unknown physical and precision costs block admission.
Another native-class census of this fixed word is unnecessary.

## Credit

Nick Petalas. Apache-2.0, following the repository license. Frozen predecessor
sources and their notices remain unchanged.

Marius-Paul Dumitrean supplied PR2979 and PR2942. ToikY supplied PR3038's
source/native machinery and Sagar Thakrar supplied its separate exact
Gaussian-integer kernel. commdata2338 supplied PR3238's forward free-algebra
arithmetic and all-private-free coverage. Nick Petalas supplied
PR2993/3006/3008/3014 and the backward covector engine. The group-A and group-B
native/interface audits are credited complementary checks. Retain Jeremy
Kothe's frame/native/cleanup and rewrite credit, Mason Hale and Jeremy
Diviney's extraction lineage, icekylinx's native compiler, Ross Richardson's
packing/invoice audits, and Tekalign, Yiyang Lu, Dugongue, Cinna Davis,
DreamingOfClouds, Douglas Colkitt and the source packages' geometry lineage.

[Canonical scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009367).
