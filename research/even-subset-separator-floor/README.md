# Exact separating-frame cost for an even-subset cube

**Scoped negative result with an attaining binary construction; no new kappa.**
For each even k >= 2, one parity cross block of the inherited even-subset
kernel has size N=2^(k-1) and scalar rank N-binomial(k,k/2)/2. A decomposition
into scalar rank-one terms with separate orthogonal nondegenerate binary
endpoint hulls needs exactly N terms and total hull dimension 2kN.
Row stars attain both bounds. At k=4 the scalar rank is five, but the two
exact minima are eight terms and dimension charge 64.

The [proof](PROOF.md) gives the all-k argument, explicit attaining hulls,
and the exact class. The [receipt](RESULT.json) records exact finite checks
and controls. This is a binary-frame bound, not a full native-circuit bound.
The stronger historical orthonormal-residual conditions, native phases,
physical transport, dirty restoration and complete recursive cost remain
unproved for these constructions. The selected frontier is unchanged.

## Reproduce

Use Python 3.12 and its standard library, from the repository root:

```sh
python3.12 -B research/even-subset-separator-floor/verify.py
python3.12 -O -B research/even-subset-separator-floor/verify.py
python3.12 -B scripts/research_package.py --package research/even-subset-separator-floor --check-only
python3.12 -B scripts/research_package.py --package research/even-subset-separator-floor
```

Each direct replay prints `PASS_EVEN_SUBSET_SEPARATOR_FLOOR`. It reads the
saved receipt and rejects any difference. No output file is written by
default. The registered replay runs both normal and optimized Python. Use
`--write-result PATH` only to write a new receipt to a separate review path.
No third-party solver, network, Lean or native compiler is used.
The local registered normal and optimized runs passed on CPython 3.12.14.
Direct normal and optimized runs also passed on CPython 3.14.7.
Hosted CI and a full native or selected-construction replay were not run.

The checker computes the rational cross-block rank at k=2,4,6 and the exact
Walsh spectrum at even k from two through twelve. It checks all 65,025
nonempty support pairs at k=4, builds simultaneous minimum hulls for every
feasible pair, and compares the criterion with a separate enumeration of
all 374 ambient subspaces at k=2. It checks the row-star reconstruction and
its hulls, all small star-readable counts, and deliberate false premises
and corruptions. Finite checks support the proof; they are not a formal
proof of every k or a full multiplication theorem.

## Sources, overlap and credit

The kernel, its dyadic values and its exact full-star spans come from
[Cinna Davis's PR #2225](https://github.com/CrocSwap/integer-mult-bounds/pull/2225),
with the author notice in the
[pinned predecessor README](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/even-subset-dyadic-kernels/README.md)
and its
[pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/even-subset-dyadic-kernels/PROOF.md).
That work credits Cinna Davis (@1337isnot1337), substantial Codex assistance,
and prior subset/compiler sources. This package does not claim a new kernel.

The common-span obstruction is prior work from Douglas Colkitt's
[preserved parity-side research](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/docs/research/parity-side.md).
The distinction between separating hulls and the stronger historical
orthonormal-residual interface is explicit in
[PR #920](https://github.com/CrocSwap/integer-mult-bounds/pull/920), prepared
for Arnav with substantial Codex assistance; see its
[pinned research note](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/complex-parity-frames-seed35/README.md).
The new result is the sharp factor-count and endpoint-dimension theorem
for this cube, including matching binary hull constructions. The scalar
rank formula is a supporting calculation. The star-readable formula is a
corollary of the inherited support geometry.

The base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`. Exact hashes are in
[SOURCES.json](SOURCES.json). The selected record and task catalogue are
historical provenance. The four listed proof files are declared live inputs.
The verifier is new and imports no predecessor code. Prepared for Ali Romman
with substantial OpenAI Codex assistance; new work is Apache-2.0. Retain all
predecessor attribution and license notices.

## Open next questions

A physical side construction must change this separate scalar-factor
contract or pay its exact hull charge, then prove native transports,
restoration and a full recursive invoice. The binary row-star construction
alone is not a reason to expand a synthesis search. No new construction round
is proposed here. [TASK.json](TASK.json) records this closeout decision.
