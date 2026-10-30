# Complete physical synthetic Fourier transforms

I implement both normalized polynomial Fourier maps W±/M with encoded
control and a reusable fixed-tape lifecycle. I use [PR3627's arbitrary-support
H call](https://github.com/CrocSwap/integer-mult-bounds/pull/3627) in natural
axis order, execute the signed-polynomial diagonals, and pay for bit reversal
at the endpoint. I include long and short axes, top rounds, support batches
and the opposite chronology. I retain the selected frontier unchanged.

I lift precision once from p to p+A, where A is the full address width.
The schedule uses exactly A normalized butterfly factors. Signed coefficient
permutations preserve the intermediate dyadic grids, so I return exactly
Q_p(W±x/M) with one final truncation. The coefficient error stays below
sqrt(2) 2^-p, and I return an ideal p-grid endpoint exactly. Both normalized
maps divide by M; their composition equals I/M.

Under the retained supplier, native, hosting, height and refinement premises,
for fixed 0<epsilon<1, D=Theta(p^epsilon), ell=Theta(p^(1-epsilon)) and
A=Theta(p), I prove

    O(V p^(1-min(epsilon,.997)*.00172899) log p)

time and O(V)+F_q space, where V=2(p+2) C 2^A 2^ell. At epsilon>=.997,
the conditional synthetic-transform saving is .00172380303. I do not claim
an integer-multiplication exponent. [PROOF.md](PROOF.md) includes the complete
pre-absorption bill, all-size diagonal algorithm, exact-grid argument and
physical ownership boundary.

I replace the old L/Kd layout contract. Each H call receives the actual named
positions and restores natural order; I then compute J from those bits.
I batch complete per-axis bit-reversal edges within PR3619's support limit.
I do not infer a full-coordinate rate from one oversized sparse-router call.

## Evidence and reproduction

I use a separate dense polynomial-matrix calculation as the packet oracle.
The registered suites cover encoded exponents, complete forward/opposite
packets, mixed axes with reduced support batches, repeated owner use,
multiple outer rows and a separate two-batch endpoint permutation. I include
malformed extent and output-ownership controls, a physical premature-rounding
mutant, and a physical omitted-reversal mutant. The ell33, 17-axis check
executes metadata only; it does not allocate that exponential payload.

The complete packets use the inherited q=2 fixture with reduced root guards
and reservations. They execute the direct/literal root paths. PR3627 retains
its separate recursive-root fixture, and PR3619 retains its separate sparse
router fixture. I have not executed a production GL64/O(73,2) full Fourier
payload. These finite checks do not prove the universal source premises.

```sh
python3.12 scripts/research_package.py --package research/physical-synthetic-fourier
```

[SOURCES.json](SOURCES.json) pins the complete official PR3627 export and
the mathematical/phase sources. [VERIFY.json](VERIFY.json) registers seven
read-only commands. [TASK.json](TASK.json) records the source/overlap scope
and the five-point expansion decision in the existing
[investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009513).

## Open next questions

1. Bind an actual bulk or fine-prime Gaussian/CRT caller to this endpoint.
   Start with its online precision, complete field layout and final M scale.
   The Gaussian exposure, product and exact recovery invoice still blocks
   an integer claim. The old conservative PR2298 Gaussian path does not
   admit a near-linear dimension merely because this synthetic map does.
2. Test a product consumer that retains bit-reversed frequency order across
   both operands and the opposite transform. Its equivariance could remove
   endpoint copies, but the current natural-order API includes and pays them.
   I have not implemented that consumer contract.

## Attribution

Jose Manuel ([jmbarrancoml](https://github.com/jmbarrancoml)), with substantial
OpenAI Codex assistance in mathematics, implementation, verification and
prose, including source-analysis agents. Apache-2.0. I claim no independent
human or formal-kernel review.

I retain OpenAI's source06 synthetic Fourier identity, its Nussbaumer/Quandalle
and Harvey/van der Hoeven lineage, and Nick Petalas's all-size identity proof.
I retain mightyOil's earlier independent layout-audit credit. I credit Sagar Thakrar's
[PR3617](https://github.com/CrocSwap/integer-mult-bounds/pull/3617), head
`4bf091f415d6470b60a5062a08b0a47e5b12dbd7`, for its fixed-round encoded
twiddle/consumer boundary, and Chris/Clear1nsight's
[PR3623](https://github.com/CrocSwap/integer-mult-bounds/pull/3623), head
`328c40966b650f60b1d62cfb0b1d67b2b755eb62`, for its actual-g spacing and
completed-round analysis. I replace their stated outer boundaries rather
than claim their underlying identities as new.

I preserve PR3627, PR3619 and PR3599 with their nested notices. That lineage
credits RaD/hipotures and Zhihao Chen for routing, Vlado Vojdanovski for the
support/compiler argument, Douglas Colkitt for Compact, Tekalign for
normalization, Hiroki Kumazaki for PR3576's factory, Nick Petalas for PR3581's
B1 boundary, and the native/borrowing/scalar contributors named in those
archives. I adapted the signed-word loop from the retained physical Gaussian
monomial implementation.
