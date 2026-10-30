# Certified rational FFT and rounded parity-triangular programs

I connect the retained rational phase construction to the actual FFT and
Toeplitz-shear gate schedule, and prove a complete coefficient/data error
bound for both dirty banks. I execute the adapted one- and two-wire gates.
This advances the child-execution obligation left by PR4198's macro replay.
I also execute the retained near-identity parity-triangular recursion and
its inverse under one coefficient and data-grid allocation. I preserve
the source's parallel even/odd branches, including reversed caller wires.

For dyadic \(n=2^d\), the target is \((x,y)\mapsto(x,y+Tx)\), with rational
Toeplitz \(T\). I use rational butterflies
\[
\begin{pmatrix}a&bw\\b&-aw\end{pmatrix},
\qquad a^2+b^2=|w|^2=1,
\]
and adjoints of the same stored gates. I certify their approximation to
the ideal FFT, prepare the **unnormalized** DFT multipliers, round those
coefficients before online use, and round data after each gate.

The exact rational circuit restores the source. Fixed-grid execution
generally has nonzero source-restoration error, which I include in the
budget rather than treating exact coefficient unitarity as exact data recovery.

## Result and source

For kernel envelopes \(M_g,M_h\), let \(M=M_g+M_h\), phase error
\(\nu=2^{-P}\), multiplier grid \(v=2^{-S}\), and data grid \(u=2^{-F}\).
With \(L=4d+8\) and \(H=1+M+2v\), I prove
\[
\|\widehat z-S(T)z_0\|_2
\le\bigl(4(d+1)M\nu+2v\bigr)R+LHnu,
\quad R\ge\max(1,\|z_0\|_2).
\]
I give explicit \(P,S,F\) choices for target \(2^{-t}\), preserve finer
incoming grids, and bound coefficient, signed data-record and temporary
widths. Every exact contiguous circuit segment and inverse segment has
norm at most \(H\); I do not multiply amplification once per layer.
[PROOF.md](PROOF.md) gives the domains, oracle bounds and full derivation.

For the triangular program I admit a rational symbol \(f\) of dyadic
length \(N\) with component-l1 distance from the identity at most \(1/2\).
I round the scalar leaves and use exact reciprocals of those stored values
for the inverse. I prove forward and inverse endpoint error
\[
eR+32DBN\,2^{-F}\le2^{-t},\qquad
e=2qB^3\,2^{-s},
\]
where \(B=100N^3\), \(q=2\log_2N+1\) and
\(D=4(\log_2N)^2+12\log_2N+1\). I give explicit \(s,P,S,F\), preserve
the incoming grid, and bound intermediate states using arbitrary circuit
segments. The online records and gate temporaries need
\(O(F_0+t+\log N+\log R)\) bits.
[TRIANGLE-PROOF.md](TRIANGLE-PROOF.md) separates that claim from exact
offline preparation and physical coefficient delivery.

I start from canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
priority 7, and pin the retained PR4100 source
`337d04939571a637aeab54a0f58f54fde811663a`.
[SOURCES.json](SOURCES.json) binds the actual bytes.
[Discussion4202](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202)
records the claim, overlap and publication handoff.

## Verification

Use CPython 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py \
  --package research/rational-unitary-fft
```

I declare four normal/optimized commands, with 240-second limits each.
I authenticate the source before parsing its schedule or executing its
interval oracle. The adapter preserves bit reversal, gate ownership,
disjoint layers, shear orientation and chronological calls. It replaces
four coefficient sites and the relevant NumPy arithmetic with certified
rational operations; it preserves source assertions under optimized execution.

The finite replay covers 12 cases through \(n=16\), 1,428 gates and
61 rounded data states. I include real/complex Toeplitz inputs, zero and
rank-one matrices, large dirty values, cancellation, an 80-bit incoming
grid and a small-grid source-loss witness. I check exact local unitarity,
FFT adjoint round trips, direct Fourier enclosures, exact Toeplitz
references, both banks' error bounds and canonical signed grid widths.

The direct DFT reference uses a separate formula but shares the certified
phase oracle. Its squared-Frobenius checks corroborate consequences of
the written operator-norm proof; they do not independently establish the
sharper operator bound. The exact dense matrices serve as checker oracles.
I do not use their accumulated denominators as online data representations.

Controls cover inverse order, missing bit reversal, wrong multiplier
normalization, the inverse twist, nonunitary coefficient rounding,
underfunded phase/data precision, discarded incoming precision, stale
phase coefficients, floating inputs and source corruption.
I compare the complete typed [RESULT.json](RESULT.json).
Observed temporary heights describe completed complex components, not
an exhaustive trace of internal `Fraction` temporaries.

The recursive verifier adds ten cases through 16 wires, 1,806 gates and
62 rounded states in forward and inverse directions. I check the exact
macro factorization against a direct Toeplitz matrix and the inverse
against separate Gauss-Jordan elimination. I include complex non-dyadic
leaves, the half-identity admission boundary, a zero odd polynomial,
reversed wires, a 100-bit incoming grid and small-grid data.
Controls reject missing Schur correction, swapped parity banks, serialized
siblings, wrong inverse order and leaf adjoints used as reciprocals.
I check rounded round trips under their separate error and second-pass
width allowances. [TRIANGLE-RESULT.json](TRIANGLE-RESULT.json) records
the complete recursive receipt. Exact dense endpoint arithmetic remains
a checker oracle, outside the online representation claim.

## Overlap and attribution

I inspected 100 recent PR records and 35 hub comments, the retained
phase/FFT implementations and targeted local searches. The overlap helper
searched 5,234 records and found one unrelated rational-unitary frame
example, with no usable remote cache. At the next checkpoint I refreshed
unchanged main and source feedback and inspected 60 PR records and
10/707 hub comments. PR4201 concerns CRT tapes and PR4203 concerns D4
interfaces. I found no equivalent certified unitary child in that coverage;
older comments, arbitrary diffs, unpublished work and literature priority
remain outside the search.
Before publication I rechecked unchanged main, the source head, 60 PR
records and 12/708 hub comments.
Before the recursive extension I refreshed unchanged main and inspected
40 PR records and 12/713 hub comments, following a separate 100-PR/35-comment
orientation. I found no competing rounded parity-child claim in that
coverage. James Reed's claimed finite PR4198 check addresses the generator
identities, a separate question. I extend this PR rather than duplicate
the child package.

I credit Chafik Boukhalfa/PR628 for exact rational unit phases and the
certified interval machinery; Vlado Vojdanovski/PR1673 for the FFT/shear
circuit; the classical Fourier/FFT lineage; and Cinna Davis for the later
caller. PR3709 already supplies certified inward twiddles and rounded FFT
execution under a different normalization. I claim the connection to this
unitary child and its complete approximation/rounding contract, not the
invention of certified phases or rounded FFTs.
Vlado also supplied the parity identity, recursion and qualitative
near-identity stability argument. I add the explicit global coefficient
perturbation, inverse, rounding and intermediate-width contract, with
source-bound recursive execution.

I preserve the first completed revision `f02a4ab5ab70a8af80415ac35c5b48cd5a93a475`
and its FFT receipt
`2e203e42d3d617e828e3341ffeb44254c931db2aebb8a040d04d67338b5b4016`.
Its [hosted replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39442494617)
and 18-file export remain evidence for that revision. The recursive
extension has a separate receipt and verification commands.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including source-analysis agents. I count those agents within the author
process. I retain frozen sources and notices, and claim no independent
human/formal-kernel acceptance, worldwide novelty or selected-frontier change.
Apache-2.0.

## Open next questions

In [TASK.json](TASK.json) I specify the next steps and blockers: compose
these children inside the actual bounded-generator program, then bind
their coefficients and data widths to the physical
Gaussian caller. This package supplies neither complete fixed-tape
lowering nor complete multiplication-theorem acceptance.
