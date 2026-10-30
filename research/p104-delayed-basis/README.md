# Conditional kappa 0.00310440 by composing a paid boundary change

This composes Ali Romman's helper341 boundary identity from [PR #5602](https://github.com/CrocSwap/integer-mult-bounds/pull/5602)
with the delayed/prepared construction in [PR #5612](https://github.com/CrocSwap/integer-mult-bounds/pull/5612).
The complete conditional endpoint increases from **0.00310299 to 0.00310440**,
a gain of **0.00000141**. The basis identity is credited to its author;
this contribution verifies that it survives the intervening shared relays,
changed contacts, independent splits and owned preparation.

Three initial coframed ADDs and one final coframed correction replace eight
operations on helper341. Its last rank5 transport disappears, and its
productive target changes from rank9 to rank4. The local funding gain is
`H4+H5-H9`, where `Hr=r^(1-kappa)`. The complete gain is18 times that expression.
The target debit is included; the removed transport alone is not the gain.

The exact raw crossing is **(0.00310440547057,0.00310440547058)**, tested at
0.0031044005. The full invoice has **66,618 paid calls,13,030 productive
targets and rank surplus760**. The word has25,525 events,747 independent
inputs,539 helpers,nine owned roles,11 owned lifetimes and peak occupancy two.
No independent input or owned lifetime is added. Every retained input is
preserved exactly, and every owned role returns zero.

Read [PROOF.md](PROOF.md), [the pinned witness](WITNESS.json), [the small constructor](construct.py)
and [the complete receipt](RESULT.json). The specialized constructor must agree
exactly with the unchanged published PR5602 constructor on this new source.
Only the causal cut index changes, from11151 to11285; the boundary covectors,
helper identity and chart remain exactly the same.

## Reproduce

Python3.12 and its standard library suffice:

```sh
python3.12 -B scripts/research_package.py --package research/p104-delayed-basis
```

Both registered modes print `PASS_P104_DELAYED_BASIS_KAPPA_00310440`.
The launcher prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Replay authenticates the
official24-file PR5612 export, its retained PR5608 export and33-file framework;
checks the exact published witness, two complete constructions, all756 endpoint
rows and dense transpose columns, every signed native map, the full physical
caller, complete invoice and ordinary charges, two interval engines at the
tested endpoint, the compiler and58 outer predicates. Five controls reject
missing input correction, missing cut correction, missing owned initialization,
old target credit and an unpaid transport. Complete decompressed candidate
payloads are compared; compressed source archives remain byte-pinned.

The inherited prepared checker is reused unchanged and checked against its
retained source adaptation. [PRICING-EDITS.json](PRICING-EDITS.json) and
[PRICING-CHANGES.diff](PRICING-CHANGES.diff) declare the only five price changes:
endpoint, comparator, paid count, output decimal and comparator label.
The original mathematical inequalities and compiler reserves remain unchanged.

## Scope and ceiling

The five inherited framework assumptions remain: native all-column realization,
owned erasure, uniform compiler closure, precision and fixed-tape costs, and
analytic recovery. The helper-endpoint contract remains. The enormous uniform
word and complete rounded multiplier are not materialized. No independent
human or proof-kernel acceptance is claimed, and the selected record is unchanged.

The signed moment is strictly decreasing on[0,0.0034]. The fixed-invoice raw
ceiling is the interval above, leaving5.47057e-9 to5.47058e-9 above the claimed
endpoint. This is not an optimum over other constructions. Logarithm power1024,
tail decay39/40 and the complete outer/ordinary conditions are retained.

## Sources and independent checks

Base: canonical main `d7633ce230196a1d5d061347de7a0fd8be512ed6`, priority revision7.
PR5612 is pinned at `faa9f6dbe6b8cc4a996d3edeca71823056453e1a`;
PR5602 at `6c224aa720203c4f4615e6538d8038a275387db8`. Exact archives,
source files, hashes and original notices are retained through[SOURCES.json](SOURCES.json).
Replay requires no foreign Git objects, network or local workspace files.

Two independent agents checked the compatibility: one derived the causal
witness and compared complete histograms; another implemented separate exact
scalar/frame/ownership replay over all756 original columns and checked the
ordered basis updates. This is agent verification, not independent human review.

Credit Ali Romman for PR5602's identity and constructor, independent splits,
frame changes and native/caller/price machinery; Scratch-net for prepared573;
Pierre-Loic Doulcet/hexapode for commuting contacts; flyingviper for shared and
delayed relays; Joel Pulikkan/GamingPuzzled, DreamingOfClouds, thu-nmrc,
Gareth Davidson, David Arias, Cinna Davis, Jacob Alan Sussman, zxv, Cao Yifan
and all retained geometry, BIT and analytic contributors. This composition
and verification were prepared for flyingviper with substantial OpenAI Codex
assistance and independent agents. Apache-2.0.

## Open next questions

Can a changed independent split cut make another published boundary identity
compatible without losing more target credit than it saves? First derive a
current-value relation after the helper's last source read; preserve its full
arbitrary-input boundary basis and debit every changed productive rank.
The other five PR5602 witnesses are not claimed compatible here. Structured
questions and the assignment refinement are in[TASK.json](TASK.json).
