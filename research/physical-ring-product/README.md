# Physical normalized polynomial products

I implement a complete fixed-tape consumer for `Q_p(uv/r)` in
`C[X]/(X^r+1)`, with `r=2^ell`, `1<=ell<p`. I also execute its composition
with PR3640's two forward Fourier calls, opposite call and exact final
M scale. I use a concrete Karatsuba word engine and certified inward
dyadic twiddles for the product's sequential complex FFT.

For `CM` polynomial records of disk-valued p-grid coefficients, I prove
exact recovery and return the normalized product in the original packet
order. Under `A=Theta(p)` and `M=2^A`, I charge
`O(CMr(ell+1)p^(8/5)+rp^3)` bit steps and O(V) cells, where
`V=2(p+2)CMr`. At `ell=Theta(p^(1-epsilon))`, epsilon=.997, the online
power per input bit is .603, below the complete Fourier power .99827619697.
I retain the setup term and the outer hypotheses in [PROOF.md](PROOF.md).

Through the complete convolution caller, you receive width `p+2+A` at unchanged
fractional precision p, with error less than `4sqrt(2)M2^-p` from
`(f*g)/(rM)`. A later caller needs a disk margin before narrowing its output.
I leave the selected frontier unchanged. I do not establish the remaining
Gaussian/CRT/integer join or a new integer-multiplication theorem.

## Review and reproduce

Read [PROOF.md](PROOF.md) for the quantified contract and full invoice,
[EVIDENCE.md](EVIDENCE.md) for positive checks and fault controls, and
[TASK.json](TASK.json) for the original card and expansion decision.
[Discussion3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664)
contains the claim and publication receipt.

```sh
python3.12 scripts/research_package.py --package research/physical-ring-product --check-only
python3.12 scripts/research_package.py --package research/physical-ring-product
```

I register eight standard-library Python 3.12 commands in
[VERIFY.json](VERIFY.json), with a combined timeout of 1190 seconds.
Each command opens one authenticated predecessor cohort and checks that it
loads this package's own checker module. Direct per-suite replay uses:

```sh
python3.12 -I -O -Werror -B research/physical-ring-product/verify.py --suite product
```

The registered launcher supplies a fresh bytecode-cache namespace; direct
calls do not make that additional isolation claim. The official export
includes the immutable Fourier archive and both declared external inputs.
Its verifier needs no Git metadata or network access. The public receipt
records the final committed export, unchanged-byte replay and hosted CI.

## Implementation map

| Code | Responsibility |
| --- | --- |
| `word_product.py`, `ring_words.py` | Shrinking three-child Karatsuba, signed codecs and linear shifts |
| `twiddle_setup.py` | Encoded directed Machin/Taylor intervals and inward quantization |
| `fft_arithmetic.py` | Exact butterfly numerators and one final component truncation |
| `product_plan.py`, `ring_engine.py` | Complete packet geometry, DIF/product/DIT stream and exact recovery |
| `convolution_engine.py` | Actual Fourier/product/opposite/M-scale composition and explicit width port |
| `ring_sources.py` | Whole-export authentication and one shared tape runtime |

The caller must supply disk-grid inputs. I validate packet extent and
ownership, but I do not add a disk-membership scan. Diagnostics count
executed calls; they do not select data operations or replace encoded
loop counters. The tests use host arithmetic only for separate oracles.

## Evidence and limits

I checked signed codecs, exact scalar products through 257 bits, 23 twiddles,
single-truncation butterflies and complete polynomial packets at several
precisions. I exercised 11 physical failure controls and a complete
16-Gaussian convolution with nonzero rounding. The composition uses the
actual direct/literal q2 Fourier child with reduced test guards. I make
no production GL64/O73 execution claim from that small packet.

The product proof uses exact word arithmetic and the disk precondition.
The outer composition additionally inherits PR3640's supplier/refinement
premises. My source-analysis helpers and checks are AI-assisted author
work; I claim no independent human review or formal-kernel verification.

## Open next questions

1. Can a physical Gaussian/CRT caller connect its full field layout and
   precision contract to this complete consumer? Start from one pinned
   analytic caller and account for its exposure, exact M scale and final
   recovery. The remaining Gaussian/CRT/integer join blocks a new theorem.
2. Can a production supplier path exercise the whole composition at a
   tractable size? Begin with the smallest legal GL64/O73 packet and
   budget its replay before execution. The present q2 test does not cover
   that production invocation.

I preserve predecessor notices and the original task catalogue. I credit
Karatsuba and the radix-two FFT algorithms, Mason Hale's PR2313 interval
reference, Dugongue's PR2790 multiplier/ABI precedent, PR3640's source
chain, and source06's Nussbaumer/Quandalle, Harvey/van der Hoeven and
OpenAI attribution. Jose Manuel (`jmbarrancoml`), with substantial OpenAI
Codex assistance in mathematics, implementation, source analysis and prose.

Apache-2.0, subject to the retained predecessor notices.
