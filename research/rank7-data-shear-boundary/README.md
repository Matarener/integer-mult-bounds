# Complete PR2979 data-output boundary

This finite audit checks every source and target output of both original PR2979
emitted programs, in both orientations, against a separate pullback through the
original source word. It supplies the normalized data application that PR3442
explicitly left outside its complete native/helper audit. All words, frames,
allocations and paid profiles are unchanged. No supplier, new kappa or
selected-frontier change is claimed.

The claimed map on 112 source arrays X and 112 target arrays Y is

```text
forward:           X' = X,      Y' = Y + X
inverse transpose: X' = X - Y,  Y' = Y
```

Every one of the 408 original dirty helpers is an independent input. The 91
private entrances are zero by their allocation contract. These equations are
in the declared normalized coordinates, not a claim that every physical array
has the same entrance and exit frame.

[PROOF.md](PROOF.md) states the exact implication and its native/scalar premises.
[SOURCES.json](SOURCES.json) pins all consumed inputs to canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6. Original PR2979 is
`be191346391661f4d35fc0d1508d0a6029572576`. The complete native realization is
credited prior evidence from [PR3442](https://github.com/CrocSwap/integer-mult-bounds/pull/3442),
head `032c8190c535137cc12c367eb73c8e76b003adcf`, and is an explicit premise here.
No native identity census is repeated or newly claimed.

## Added coverage and controls

The original PR2979 scalar auditor already checks the source word's complete
map. PR3038 checks one emitted helper endpoint, PR3238 checks all private frees,
and PR3442 adds all emitted native events and all dirty-helper endpoints.
This package joins every emitted data output with a separately implemented
original-source covector. Its independent checking machinery is reused and
credited, rather than presented as a new implementation.

There are 224 data observations per orientation and provider, 896 in total.
Each observation is an exact rational expression in free noncommuting warp
operators, with no numerical tolerance. The complete emitted stream is bound
event for event to its original source, including center COPY/CLEAR operations,
private lifetimes and frame adapters. Fresh native artifacts and their retained
source digests are checked before observing outputs.

A deliberately inserted same-chart `L0 += L1` after all data reads leaves all
408 helper outputs and all 91 private-free values correct but corrupts L0.
Both orientations reject it at the data boundary. The full source-binding
check also rejects the inserted event; the distinction here is between
restoration observations and data observations. This is a failure control,
not a defect in the original word. The committed RESULT files retain its actual
cut, corrupted rows and all source/emitted data equations.

## Reproduce

Use Python 3.12 and `numpy==2.3.5`, required by the unchanged producer. The
new observer uses the standard library. Set an external session directory:

```sh
mkdir -p "$RUN_ROOT/scratch"
TMPDIR="$RUN_ROOT/scratch" python3.12 -Werror -B scripts/research_package.py \
  --package research/rank7-data-shear-boundary
```

The registered hook runs seven behavioral groups in normal and optimized Python,
then fresh provider replays sequentially. Direct replay is:

```sh
TMPDIR="$RUN_ROOT/scratch" python3.12 -I -Werror -B \
  research/rank7-data-shear-boundary/verify.py --provider base
TMPDIR="$RUN_ROOT/scratch" python3.12 -I -O -Werror -B \
  research/rank7-data-shear-boundary/verify.py --provider extra
```

Each provider must print `PASS_PR2979_ALL_DATA_BOUNDARY provider=base` or `extra`.
`--emit` prints a newly computed uncompressed receipt. `--artifacts DIR` reuses
supplied producer artifacts while authenticating sources and checking the whole
boundary. That option does not claim a fresh producer run. Direct replay needs
no network or Git. Registered metadata provenance checks require Git history.

## Limits

Native recipe realization, physical rational scalar/COPY/CLEAR operations,
known-zero allocation and the stated common-chart contract are premises. The
result does not price or implement backing owners, scalar instructions, movement,
storage, precision, tape or the actual T74 caller. The whole supplier invoice,
both supplier caps, outer multiplication transfer and all-size/compiler/analytic
conditions remain separate. Independent human and formal proof-kernel review
are unclaimed.

## Open next questions

The next useful task is an actual physical caller that realizes this data map
and the already checked helper/private boundary under one complete invoice.
Start with one source/target pair and its chronological scalar, frame and owner
contracts; stop at any unpaid move, unavailable dirty state or unresolved
precision obligation. The active physical T74 work is complementary. Another
endpoint census of these unchanged programs is unnecessary.

## Credit

Nick Petalas. Apache-2.0, following the repository license. Frozen predecessor
bytes and notices are unchanged.

Marius-Paul Dumitrean supplied PR2979. ToikY supplied PR3038's literal
source-to-emitted decoder, emitted covectors, artifact binding and source
regenerator. Nick Petalas supplied PR3006's separate original-source covectors
and PR3442's complete native/helper audit. commdata2338 supplied PR3238's forward
private-free observer, reused for the controls. Sagar Thakrar supplied the
separate exact Gaussian kernel used by the prior native audit. Retain Jeremy
Kothe's frame/native/cleanup and rewrite credit, Mason Hale and Jeremy
Diviney's extraction lineage, icekylinx's native compiler, Ross Richardson's
packing/invoice checks, and the geometry and construction authors named in
the pinned predecessor packages.

[Canonical scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009648).
