# P104: rational recoding and joint owned-block boundaries

**Scoped negative results; no new construction or multiplication bound.**

This package tests whether the eight owned transfers in
[PR #5580](https://github.com/CrocSwap/integer-mult-bounds/pull/5580) can become
cheaper by rational recoding or by sharing work across their full joint
boundary. It provides three exact results:

1. Every nonzero rational combination of the eight unchanged producer values
   has original-entry support dimension at least eight. Exactly 16 projective
   combinations have dimension eight: eight original and eight mixed modes.
   All others have dimension nine. The verifier classifies all 511 binary
   hyperplanes with exact rational elimination; this is not a coefficient grid.
2. At each final delivery line, the three eligible mixed modes cannot reconstruct
   its original producer, even modulo arbitrary corrections from original
   zero-entry-frame inputs. Exact separators and an independence minor are
   retained in [RESULT.json](RESULT.json).
3. With the complete 41-role public boundary fixed, arbitrary sharing across
   all eight owned blocks costs at least `31 H1(t) + 8 H7(t)` for `0<t<=1`.
   The source costs `33 H1(t) + H2(t) + H3(t) + 7 H7(t)`. Their difference
   bounds possible local savings; attainability remains open.

The first two statements concern the unchanged producer span and direct nested 8-to-1
delivery starting at each mode's original-entry support hyperplane. The third allows arbitrary internal rational dependencies and private
fields, but excludes earlier preparation and outside public side information.
Those distinctions matter: the certificates do **not** rule out changed public
dependencies, partial residuals outside that span, or a larger boundary.

See [PROOF.md](PROOF.md) and [JOINT-BOUNDARY.md](JOINT-BOUNDARY.md).

## Reproduce

Python 3.12; standard library only. From this package directory:

```sh
python3.12 -I -B verify.py
python3.12 -I -O -B verify.py
```

Both print `PASS_P104_OWNED_CODING_BOUNDARIES`. Normal replay writes no files.
The source word is retained locally and authenticated before use. The verifier
also checks all scalar rows on arbitrary public inputs, chronological frame and
ownership legality, exact boundary ranks and four semantic corruption controls.
It compares the fresh receipt to the committed result; `--write` explicitly
regenerates the latter.

The registered metadata/provenance launcher, from repository root, is:

```sh
python3.12 scripts/research_package.py --package research/p104-owned-coding-boundaries
```

This launcher needs Git history for provenance; the direct verifier works in a
Git-free package export. No solver, network, native checker or external package
is required. The unchanged native maps, physical caller, pricing, compiler and
outer analytic obligations are not part of this scoped replay. The full source
replay was run separately during discovery; it is not a new proof claim here.

## Relation to previous work

[PR #5584](https://github.com/CrocSwap/integer-mult-bounds/pull/5584) established
single-block optima, delivery obstructions and a rank witness, while explicitly
leaving cross-block sharing open. This package supplies a joint information-cut
argument under a stated 41-role boundary, plus the complete rational recoding
classification. It does not add individual nonadditive loss-space bounds.

Ali Romman's [PR #5579](https://github.com/CrocSwap/integer-mult-bounds/pull/5579)
already covered fixed public windows; that obstruction is not claimed as new.
The public compensated-source work in
[Discussion #5575](https://github.com/CrocSwap/integer-mult-bounds/discussions/5575)
and the event-retiming work in
[Discussion #5574](https://github.com/CrocSwap/integer-mult-bounds/discussions/5574)
are adjacent active approaches. The later
[PR #5590](https://github.com/CrocSwap/integer-mult-bounds/pull/5590) addresses
all frame paths with scalar contacts fixed; our joint-boundary theorem permits
changed internal scalar dependencies but fixes the larger public boundary.
These are different contracts. Open-PR and discussion checks were bounded
coverage checks, not a proof of novelty. The canonical base and frozen sources
are recorded in TASK.json and SOURCES.json.

## Open next questions

* Can an earlier residual assembly or changed outside side information lower
  the complete paid-minus-productive moment? First identify actual value
  versions, a legal transfer and all preparation/restoration costs.
* Can the exceptional owned block attain the joint lower bound while meeting
  every middle-level delivery? The information cuts alone do not resolve this.

The user-authorized broader investigation continues separately; this package
is an independently reviewable checkpoint, not a claim that the overall
research goal is complete.

## Credit

Prepared for flyingviper with substantial OpenAI Codex assistance. Separate
agents derived and checked the joint-boundary argument and delivery gate;
the all-hyperplane classification was independently reconstructed by the
primary agent and reviewed by another agent. These are computational research
checks, not human review or proof-kernel acceptance. New work is Apache-2.0.

The retained word is Ali Romman's PR5580 source, with Joel Pulikkan,
DreamingOfClouds, thu-nmrc and the full P104 predecessor credit retained in
[inputs/README.md](inputs/README.md). No predecessor construction is attributed
to this package.
