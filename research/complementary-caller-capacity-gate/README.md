# A whole-caller obstruction for the actual seven-axis B/C suppliers

**Scoped proof; no new kappa.** The unchanged B/C suppliers cannot give a
positive complete recursive moment in the declared coordinate model, even
with arbitrary main wiring, any number of independent inputs, field mixing,
axis reuse, retained values and paid extra queries of any rank.

The result extends the fixed-224-owner serial ceiling in
[PR4848](https://github.com/CrocSwap/integer-mult-bounds/pull/4848).
It gives a concrete expansion gate: adding owners, scalar role gauges or
another schedule inside this model cannot improve kappa. A useful new
construction must change the source, helper contract or permitted maps.

## Result and scope

For t=1-C, every whole B or C call contributes at most

    K(t) = 28 + 140*7^t + 84*8^t

to the independent main target moment after the exact extra-query moment
is subtracted. The source paid bill minus its independent helper credit
strictly exceeds K(t) for every 0<t<1. At C=.0036, the excess per call is
greater than 31.58147 for B and 23.98603 for C. These are raw moment
deficits, not kappa values. See [PROOF.md](PROOF.md) for all hypotheses
and the proof for the entire interval.

All calls and targets use one common coordinate chart. Ordinary maps are
complex-linear field matrices in the scalar algebra of the coordinate
Gaussian even powers. This includes noncoordinate scalar role mixing and
ordinary sector projectors. It excludes general address maps, value
conjugation and free odd input gauges. Each whole call retains its 408
fresh independent helpers, separate from the main computation. The proof
allows inverses, transposes, inverse transposes, different central axes
between calls, and any target/query ranks. It holds at every width f>=3.

The key step compares two sign characters in a fixed even-power sector.
Rank distance is subadditive through arbitrary linear circuits. Averaging
random sign cuts gives an exact whole-call polynomial. A positive integral
then converts this cut bound into the rank^t moment for every 0<t<1.
The two-character argument removes the rank cutoff in the initial claim.

## Evidence and reproduction

[RESULT.json](RESULT.json) records 864 exact rational pair/orientation/sign
checks, all 256 source sign masks, 5952 character-pair comparisons in twelve
mixed finite-field circuits, the source bill cancellation, and four rejected
corruptions. The cutoff-free proof is written mathematics; finite circuit
checks alone do not prove it. Integer-power inequalities certify the stated
numerical deficits. Positive controls retain query-only equality and the
larger capacity of an eight-transverse-axis A interface.

```sh
python3.12 -B scripts/research_package.py --package research/complementary-caller-capacity-gate
```

The registered replay runs normal and optimized Python with isolated imports
and warnings as errors. Python 3.12 and its standard library suffice. Direct
replay also works without Git:

```sh
python3.12 -I -W error -B research/complementary-caller-capacity-gate/verify.py
```

The direct checker authenticates the package-local frozen bytes in
[INPUTS.json](INPUTS.json). [SOURCES.json](SOURCES.json) records canonical
main `6cf7a683f447b9f1e2333791907fd92be5009a63`, exact Git objects and hashes.
The native source word and its complete phase/ownership/compiler audit
are inherited from PR4703/4712 and were not rerun here. No native caller,
formal-kernel proof, selected result or independent scientific acceptance
is claimed. The productive eight-axis P104 family is outside this result.

## Coordination and prior work

[Discussion5628](https://github.com/CrocSwap/integer-mult-bounds/discussions/5628)
is the canonical claim and handoff. The current priorities, handoffs,
paginated open PRs, Discussions and tracked local package notes were checked
before this round. Code diffs, all closed historical PR bodies and private
work were not searched exhaustively. No overlap search proves novelty.

The exact B/C source and audit are
[PR4703](https://github.com/CrocSwap/integer-mult-bounds/pull/4703) and
[PR4712](https://github.com/CrocSwap/integer-mult-bounds/pull/4712).
[PR4848](https://github.com/CrocSwap/integer-mult-bounds/pull/4848) gives the
narrower serial result and credits the direct-price method of
[PR4674](https://github.com/CrocSwap/integer-mult-bounds/pull/4674).
[PR5578](https://github.com/CrocSwap/integer-mult-bounds/pull/5578) and
[PR5586](https://github.com/CrocSwap/integer-mult-bounds/pull/5586) give the
typed-provider work. [PR5626](https://github.com/CrocSwap/integer-mult-bounds/pull/5626)
supplies the query-rank perspective. No emitter or source word was copied
from that pending contribution.

## Open next questions

1. Can a shared native producer use helper information in the main computation
   with a favorable full bill? Give one exact all-input joint endpoint and
   independent helper census first. No such producer is supplied here.
2. Can a map outside the declared complex-linear coordinate algebra reduce a
   whole caller bill? Exhibit the exact failed sign-sector implication and
   price preparation, restoration and every paid query. No profitable map
   or caller of this kind is supplied here.

## Credit

Credit Dugongue, Cao Yifan/intqwq, Chris R/Clear1nsight, Cinna Davis, DaysSky,
zxv, Jacob Alan Sussman and all retained native/controller/compiler authors.
Classical rank-distance and integral identities are not claimed as new.
Prepared by Ali Romman with substantial OpenAI Codex assistance. New work is
Apache-2.0; frozen source notices are retained.
