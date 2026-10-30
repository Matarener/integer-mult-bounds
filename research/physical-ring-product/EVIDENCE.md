# Verification scope

I run the eight registered suites with Python 3.12, isolated imports,
optimization enabled, warnings as errors and explicit exceptions for
checks. I use no assertions as proof gates. The public publication receipt
records the final commit, official export and hosted run; this file records
the tests and their expected semantic results.

| Suite | Evidence |
| --- | --- |
| sources | Whole 16-file predecessor export, shared Count/Tape cohort, seven local runtime modules, two external source hashes; changed binding and second-runtime rejection |
| budget | 8128 exact precision plans and 241 twiddle-bound controls; strict 243<256 Karatsuba inequality; favorable and unfavorable outer powers; full Fourier power bound to the authenticated predecessor |
| words | 45 signed codec/add/subtract cases, shifts and ties; 35 unsigned packet calls through 257 bits; actual three-child recurrence and restoration |
| twiddles | 23 coefficients in six forward/opposite packets, including L=16; exact norms, separate certified intervals, conjugation, protected output and invalid descriptors |
| fft | Four exact butterfly cases, including a physical premature-DIF-truncation mutant |
| product | Four complete packets across p=2,3,8 and ell=1,2; nonzero outputs, multiple rows, unit-disk boundary, changed-shape owner reuse |
| convolution | Actual two-forward/product/opposite/scale composition;16 Gaussians, two rows, nonzero rounding and protected output-width port |
| failures | Eleven controls, followed by a positive nonzero packet after ordinary rejections |

For the 257-bit scalar case I execute 364 nodes and 243 leaves, with scratch
pool peak 6. I obtain the raw 514-bit output hash
`55f0d3596b5bee627414412ca1ffe7169152729c8f3e0a5279654f0c3ecb771e`.
The scalar checker compares exact integer products and verifies the full
park/restore counts. It also executes a wrong-middle-sign mutant.

For Q=16,L=8, the forward twiddle numerators are
`(65536,0),(46340,-46340),(0,-65536),(-46340,-46340)`.
I compare them with Mason Hale's authenticated, separately implemented
Fraction interval reference at extra precision. I treat quarter turns by
their exact rational identities, since an outward interval around 1 alone
cannot certify an inward endpoint equal to 1.

In the DIF rounding control, Q=16 and integer inputs
`(3,3,0,0,46340,-46340)` give `(1,1,2,0)`. With the premature truncation
mutant I obtain `(1,1,1,0)`. I check the location of rounding here,
beyond agreement on exact quarter-turn examples.

The complete product checker uses a separate direct O(r²) Gaussian
negacyclic convolution oracle. The p=2 packet returns
`(1,0),(0,1),(0,1),(1,0)`, hash
`8a5d8577054a9681c97b0be53c3028ab64f20ffcff2a14fd54f23c19973eb1e3`.
At p=3, ell=2, C=2, I execute 704 scalar products and 2816 word nodes;
the output hash is
`d6188f3fb15ca850e7ee4dd0bbb986a223f21aa23edfd036d1738bc87c81925b`.
At p=8, ell=2, C=1, I execute 352 products and 4576 nodes, including
two recursion levels; the hash is
`0f492a4328e30182f7b911c97ccbfa9265208706b79ef0640ec4a14cbe893f21`.
The all-boundary packet hash is
`87fde0e1f70265278ba75116fb3168da7fba801ed883b5f7a19a522b904de829`.
I measure product pool peak 53 and maximum twiddle pool peak 31.

The complete convolution uses A=1,p=3,ell=2,C=2 and one short-axis flag.
I compare its output with an exact staged Fourier/product oracle and a
separate direct cyclic/negacyclic convolution model. I obtain width 6 and
a 192-bit payload, hash
`24dbd9823bb225398b94c297d282891f55f15c37a53fe97ea1778126910b6319`.
I measure maximum squared error 841/256 in p-grid numerator units, positive
and below the bound 32M². I verify the actual call counts 2,1,1,1 and
reject reuse after consuming the payload but leaving the width port live.

The failure suite rejects zero dimension, zero degree log, ell>=p,
short left input, extra right input, aliased input packets and protected
output reuse. It executes wrong inverse twiddles, a wrong recovery shift,
omitted negacyclic subtraction and a dynamic Tape allocation. I require
the expected oracle mismatch or named physical guard. I verify ordinary
precondition rejection cleanup; I do not claim transactional recovery from
arbitrary injected faults halfway through a child operation.

During development I found a checker-name collision with an inherited
`check_failures` module. I renamed this package's checkers to `ring_check_*`
and added an exact package-local path check at the registered entry point.
I rerun the registered suites on those final entry points.

The finite evidence does not establish the universal runtime recurrence,
the trigonometric tail proof or the inherited supplier refinement. Read
[PROOF.md](PROOF.md) for those arguments and their explicit hypotheses.

In a source trace after initial publication, I found that I had labelled the
primitive exponent 332353/332929 as the complete Fourier power. I corrected
the proof and bound the budget check to PR3640's authenticated calculation.
The full power is .99827619697, above both the relaxed native exponent and
the primitive exponent. The product's .603 allowance still fits. I changed
no data-word, transform, rounding or restoration implementation in this
correction; the published receipt identifies the corrected commit and replay.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
