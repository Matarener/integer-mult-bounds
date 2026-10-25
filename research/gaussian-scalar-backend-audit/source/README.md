# Certified normalized Gaussian calls through full Toeplitz circuits

I connect the retained normalized Gaussian `Tsec` function and its
`full_plan` call to requested-precision rational coefficients and the
complete logical forward/inverse circuit. For dyadic size \(N\),
rational \(c>0\), \(|s|\le1/2\), and
\(T_{ij}=\exp[-\pi c((j-i)^2-2s(j-i))]\), I prove error below \(2^{-t}\)
with online widths
\[
O(F_0+t+\log N+\log R+1/c).
\]
I derive leading-section conditioning, pay omitted offsets and coefficient
quantization, and pass the same rational root to the full compiler.
I preserve the diagonal ones and both closed half-shift endpoints.
[GAUSSIAN-PROOF.md](GAUSSIAN-PROOF.md) gives the interval termination,
conditioning, perturbation and composed error arguments.
Raw Gaussian gauges, common-reference assembly and physical delivery
require further work.

I execute the retained full Toeplitz recursion and its stored inverse,
using the rational generator, triangular and FFT circuits below.
For dyadic size \(N\), I assume \(\|T\|\le\Lambda\) and
\(\|T_b^{-1}\|\le Q\) for every leading section.
I prove a completed-call prefix/inverse bound
\(256N^3(\Lambda Q)^{12}\) through scalar unit-LDU factors and legal
completed-call sets. I handle unequal parallel branches with disjoint
active fragments and obtain sufficient online widths
\[
O(F_0+t+\log N+\log\Lambda+\log Q+\log R).
\]
I compute stronger rational component envelopes for executable admission;
their inflation preserves this width bound.
[FULL-PROOF.md](FULL-PROOF.md) gives the domain, frontier induction,
explicit allocation and comparison with the earlier guard.

I connect PR4198's exact rational generators to the retained compensated
gate program, replacing its exact matrix callbacks with certified FFT,
Toeplitz-shear and parity-triangular circuits. I execute the actual
one- and two-wire schedule on both dirty banks and prove a common
coefficient/data error and storage budget. I preserve parallel even/odd
branches, reversed caller wires and the source's compensation order.

For the Toeplitz-shear child of dyadic size \(n=2^d\), the target is
\((x,y)\mapsto(x,y+Tx)\), with rational Toeplitz \(T\). I use rational butterflies
\[
\begin{pmatrix}a&bw\\b&-aw\end{pmatrix},
\qquad a^2+b^2=|w|^2=1,
\]
and adjoints of the same stored gates. I certify their approximation to
the ideal FFT, prepare the **unnormalized** DFT multipliers, round those
coefficients before online use, and round data after each gate.

The exact rational shear circuit restores its source bank. Fixed-grid execution
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

For a rational matrix \(T\) of dyadic size \(m\), the complete generator
program implements \((x,y)\mapsto(x,y+Tx)\). I reuse each stored triangular
inverse and pair the compensating shear with negated stored spectral
multipliers. Completed terms then have exact unrounded endpoints
\(\widehat G_j(\widehat P_j-I)\), and their operator defects add.
I prove a complete error bound
\[
\Delta R+D K_{\rm exec}m\,2^{-F}<2^{-t}
\]
with explicit polynomial \(K_{\rm exec}\), depth
\(D=r(8d^2+32d+18)\), and online widths
\(O(F_0+t+\log m+\log(1+B_E)+\log R)\).
Here \(r\) is the exact Stein rank, \(d=\log_2m\), and
\(B_E\ge\|T-ZTZ^T\|_2\).
[GENERATOR-PROOF.md](GENERATOR-PROOF.md) gives the four checkpoint
prefix/suffix forms, paired-rounding rule and complete allocation.

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

I declare eight normal/optimized commands, with limits of 60, 60, 90,
90, 150, 150, 300 and 300 seconds, totaling 1,200 seconds.
In each final slot I run the full verifier followed by the Gaussian
verifier in the same process. I preserve the full receipt and compare
the separate [GAUSSIAN-RESULT.json](GAUSSIAN-RESULT.json) receipt.
I check nine Gaussian cases, 4,527 gates and 38 rounded forward/inverse
states, including both half shifts, paid truncation and a 512-bit
incoming vector. I compare finer scalar interval references and exact
leading-section inverses, and reject 16 controls. The finer references
share the declared interval backend; I claim no independent transcendental
implementation. The complete Gaussian receipt is
`0a0548963b8132b430f43b8534abbd4220b93a138eb9e0a28a9cfd7432922928`.
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

The full generator replay covers 57 matrices, 71 generators, 5,614 gates
and 172 rounded dirty-bank states. I execute the retained Schur walk
to collect 50 actual shear matrices, including the predecessor's complex
corner fixture, then add seven stress matrices. I check exact rank with
separate elimination, both Stein reconstructions, the full stored endpoint
and source restoration, and rounded error/width bounds. I check actual
checkpoint prefixes, suffixes and their inverses on selected root-Schur,
dense-complex and large-scale cases.

Controls include omitted inverse/compensation, extra row conjugation,
tiny exact rank, inadequate scaled-child precision and the half-grid
failure of independently rounded positive/negative compensation.
[GENERATOR-RESULT.json](GENERATOR-RESULT.json) carries the full receipt.
I freeze the executed producer with its original
[provenance](vendor/STEIN-PROVENANCE.json) and pin its local archive
separately from the original sibling PR commit.

The full-recursion replay adds 11 cases, 3,659 gates and 68 rounded
forward/inverse states. Nontrivial cases reach size eight; a size-16
identity exercises zero-layer shear calls. I include indefinite and
half-shift Gaussian matrices, complex scalar pivots, a small pivot,
reversed wires, a nonzero 512-bit incoming fixture and an identity left
subtree paired with a longer right subtree.

I check 151 ideal completed-call sets and 12 selected physical cuts.
I enumerate all legal sets through size four and use actual atom-boundary
sets for larger cases. Ownership/precedence checks cover every layer cut;
selected operator checks compare both active-fragment factorizations,
including two simultaneously unfinished, nonempty fragments.
I check complete matrix and separate inverse references, stored-circuit
inversion, global rounding errors and signed word widths.
Fifteen controls cover leading-section admission, source order, ordinary
transpose, parallel timing, zero-layer calls, scalar reciprocals, incoming
precision and the upper-frontier inverse.
[FULL-RESULT.json](FULL-RESULT.json) records the complete receipt.

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
Before the generator extension I refreshed unchanged main, inspected
30 PR records and 10/717 hub comments, and checked targeted generator
searches. The card-wide helper searched 5,236 local records but had no
usable remote cache. I found no competing complete generator-gate claim
in that coverage. PR4208 addresses CRT stencil production.
Before the full extension I refreshed unchanged main and inspected
25 PR records and 8/733 hub comments. ToikY's PR4209 supplies a distinct
same-rho Schur-closure theorem under row/column majorant admission,
excluding full gate execution and global allocation. I credit that
sharper local result without transferring its hypothesis to the present
leading-section domain.

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

For the normalized Gaussian extension, I retain Mason Hale/PR2313's
interval arithmetic and existing dense Gaussian/integer execution,
Jeremy Kothe/IdeaOuter's shifted `Tsec` source, and Vlado's q-LDU factors.
I rederive our PR4193 finite-cap implication in GAUSSIAN-PROOF.md rather
than require an unmerged sibling proof as an unchecked hypothesis.
I preserve full revision `7ab1bc8973cc9e606053c65f094ca3abc4a42fee`
and its complete receipt
`b1bdf09eb959cc4821c5515fa865c06541215224174bcdfc667e6515210bfbb6`.
Its [hosted replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39463338955)
remains evidence for that revision.
Before the extension I refreshed unchanged main, inspected 20 recent
open PR records and 8/776 hub comments, and checked our canonical thread.
I found no competing normalized coefficient-to-circuit claim in that
coverage. I compared PR4212's P112 audit and PR4208's CRT stencil work;
they address different native/physical obligations.

I preserve the first completed revision `f02a4ab5ab70a8af80415ac35c5b48cd5a93a475`
and its FFT receipt
`2e203e42d3d617e828e3341ffeb44254c931db2aebb8a040d04d67338b5b4016`.
Its [hosted replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39442494617)
and 18-file export remain evidence for that revision. The recursive
extension has a separate receipt and verification commands.
I also preserve recursive revision `203d04313c0cb2b4a4663a5a2d4d407e5a5b6d20`,
its [hosted replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39448550970)
and receipt `d430fced712daa2e620b53a49dd09f0ba10ddddb4a4ff6b79d2abbbfd3afc1e6`.
The generator extension retains both earlier scientific receipts and
adds a third record and two commands.
I preserve the completed generator head
`fdcdc2690910392f7b42dbae4155b7d7b5790abd`, its
[hosted replay](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/39454327335)
and receipt `f74e0efc459e9c3d44d8ca8b3a33dc0fccc31731d0829419c3d515fe7f0f1e02`.
James Reed's [finite audit](https://github.com/CrocSwap/integer-mult-bounds/pull/4205#issuecomment-6295524563)
at that fixed head checks budgets and source seals; he excludes circuit
re-execution and universal-proof acceptance. I retain that scoped credit.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including source-analysis agents. I count those agents within the author
process. I retain frozen sources and notices, and claim no independent
human/formal-kernel acceptance, worldwide novelty or selected-frontier change.
Apache-2.0.

## Open next questions

In [TASK.json](TASK.json) I specify the next steps and blockers: incorporate
the raw Gaussian gauges and scalar factors, compare with the common rounded
reference, and connect the coefficients and data widths to physical delivery.
Reviewers still need to assess the universal proofs and complete setup,
fixed-tape lowering and the full multiplication construction.
