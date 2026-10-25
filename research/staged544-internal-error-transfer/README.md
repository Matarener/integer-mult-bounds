# Staged544 internal errors: 27 sufficient relative guard bits

**A source-bound completed-word precision lemma, with arbitrary dirty state.**
For both PR3945 literal providers, in either prescribed orientation, a uniform
relative completed-instruction error allowance

```
u <= 2^(-beta-27)
```

suffices for final maximum block-Hilbert error at most `H 2^(-beta)`, where
`H` bounds all initial data, dirty helper and private-buffer blocks. The
conditional native isometry and macro-error premises are explicit below. This
is a finite producer-interior coefficient, not a selected stock coefficient,
a physical native implementation, supplier admission or a new κ.

The new method pairs arithmetic-circuit analysis with noncommutative operator
norms and the numerical-analysis technique of transporting perturbations into
initial coordinates. It retains cancellation in exact forward and inverse
prefixes. A direct unsigned-path proof on the same instructions needs 94/100
sufficient guard bits; this certificate reduces that allowance to 27 for both
orientations. The result is a bound, not an optimal-precision claim.

## Exact result

| PR3945 orientation | Certified exact-path range bound /H | All-cut additive-fault gain | Final additive-fault gain | Relative guard bits |
| --- | ---: | ---: | ---: | ---: |
| Primal |302|22518781/4|1335|27|
| Dual |169|31719103/8|4841|27|

The same table applies to `base` and `extra`. Each new word executes 17,598
literal instructions:16,266 ADD/correction sites,1,164 SCALEs and 168 native
warp sites, including all wrappers and cleanup. Each field is a Hilbert block;
these are literal macro counts, not a count or tariff for internal native
arithmetic. Both PR3734 words are retained controls; they have 17,596 literal
instructions and the same final gains/range maxima.

The exact final map is the intended shear on all 632 live fields, with every
one of 91 private buffers returned identically and with **zero private-buffer
to live-field response**. This holds for arbitrary initial buffer contents in
the free-operator model. It extends the predecessor's conservative zero-buffer
endpoint predicate. PR3969's independently established relative old/new
program identity is compatible with this stronger full-state calculation.

An absolute-error alternative is especially simple: every instruction may
return an arbitrary block defect at most `H 2^(-beta-13)`; the final error is
at most `H 2^(-beta)` and every actual intermediate block has norm `<1024 H`.
The primal final bound alone uses 11 extra bits.

A separate full-state-cut extension allows errors in arbitrary source, helper and private fields: 25 sufficient absolute bits, or 38 relative bits primal / 37 dual under its stated aggregate-cut contract. It provides an allowance for frame/recursive defects once the actual implementation binds them to those cuts.

For d complex coordinates,
per-real-component rounding needs the explicit additional
`ceil(log2(sqrt(2 d)))` allowance. A completed native macro must supply its
block-defect guarantee; internal native work and scratch are not free.

[PROOF.md](PROOF.md) proves the prefix/suffix identities, exact dirty-state
claim, sufficient precision inequalities and a repeated-call recurrence.
[RESULT.json](RESULT.json) contains all eight source/orientation receipts,
phase bounds and reproducible stream hashes. [LEDGER.json](LEDGER.json)
distinguishes proved finite bounds, conditional implementations and unresolved
physical or all-size costs.

## Reproduce

Python 3.12 or later, standard library only; no network, Git, third-party package,
constructor or predecessor evaluator is used by the scientific checker.

```
python3 -B research/staged544-internal-error-transfer/verify.py
python3 -O -B research/staged544-internal-error-transfer/test_controls.py
python3 scripts/research_package.py --package research/staged544-internal-error-transfer
```

The default checker authenticates all four inputs, reruns every source and both
orientations, and compares the full receipt. It writes no source or result
files. `--emit /absolute/external/result.json` explicitly generates a new
receipt outside the package. The controls use an independent dense scalar
matrix oracle, Gauss-Jordan inverse prefixes, concrete noncommuting unitary
matrices, and production mutations of compensation, cleanup, dirty-buffer
leakage and return. Exact forward and reverse free-operator maps agree on all
723 input/output blocks in each of the eight cases. [VALIDATION.json](VALIDATION.json)
records measured executions and publication checks.

## Boundaries and source credit

This is a changed scope of the `selected-stock-envelope` card, explicitly
assigned to the pending staged544 stream. It does **not** derive the selected
m=73 stage coefficient or substitute 27 for the stock coefficient sigma. The
selected κ remains 0.001672660197076918. The actual native/recursive macro
realization, input magnitude relative to caller data, physical owners, exact
restoration under rounding, allocation/tape, all-size depth and the selected
producer/consumer map remain obligations.

The four immutable words come from PR3945 head
`91f81d131252db704f945891da1ea54e29d46b8b`; the two old words preserve the
PR3734 providers. [FROZEN-SOURCES.json](FROZEN-SOURCES.json) records exact
source paths, sizes and SHA 256 values. Their external head is an attribution
and byte pin, not asserted to be an ancestor of this package. [SOURCES.json](SOURCES.json)
binds the current-main task and selected-record provenance. All four words
remain byte-identical to their authenticated inputs.

New mathematics and code: Chris R / Clear 1 nsight with substantial OpenAI Codex
assistance. No independent human or proof-kernel review is claimed. Credit
Dugongue for PR3945, dataisfire for PR3734, Jeremy Kothe's rewrites, Sagar
Thakrar/roger-sato's semantic audit and Arham Tahir's contract, and all native,
owner and outer contributors retained in [NOTICE-PR3945.md](NOTICE-PR3945.md)
and [PREDECESSOR-CREDITS.md](PREDECESSOR-CREDITS.md). Those two documents are
verbatim predecessor notices, not authorship claims for this new package.
The program adapter follows the credited literal execution contract; the
forward, reverse, inverse-prefix and error analyses are newly implemented and
import no predecessor executable. QQ16 producer-error and rounded-envelope
work supplied the contract distinction between producer interiors and completed
output errors; its different source constants are not imported.

## Open next questions

1. Bind one changed PR3945 native/recursive macro to a concrete rounded
   implementation and prove its block-error budget plus actual scratch cost.
   This converts a conditional finite-word lemma into a usable physical
   component. Native interiors and exact borrowed restoration are the blockers.
2. Map one actual caller's dirty-state range, tensor dimension and ordered
   calls into the composition recurrence before pricing its reservoir. This
   would supply a true caller reserve coefficient; no selected-stage or uniform
   all-size map is established here.
3. Compare the actual ordered caller shears with the conservative factor-two
   composition bound. Exact cancellations may further reduce required precision,
   but only after an authenticated consumer sequence is available.
