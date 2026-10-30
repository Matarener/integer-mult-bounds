# Physical chirp middle map

I implement the complete numerical chirp sandwich from source08:
kernel generation, the first endpoint product, cyclic convolution and the
final endpoint product. I generate phases from encoded modular residues
and a short table of dyadic powers, using PR3709's actual word multiplier.
I execute the cyclic twist, full ring consumer, exact width recovery and
untwist inside the same caller.

For p-grid input of norm at most .6, p>=16 and p-A>=13, I return a p-grid
approximation to `Q_freq F_t x` with error below
`(4sqrt(2)M+22)*2^-p` and norm below .601. Here M=2^A, r=2^ell,
2<=ell<p, the preceding axis lengths are r or r/2, and the final length
is r. I preserve the complete packet order and borrowed ports.

I charge the new phase and consumer work at
`O(CT(ell+1)p^(8/5)+rp^3+(A+p+log(C+1))^3)`, in addition to three
complete inherited Fourier calls, with T=Mr. Under A=Theta(p) and
ell=Theta(p^(1-epsilon)), epsilon=.997, the added online power is .603.
I compare it with the corrected full Fourier power .99827619697.
Read [PROOF.md](PROOF.md) for the complete bill and inherited premises.

## Sources and contribution

Chafik Boukhalfa's [PR479](https://github.com/CrocSwap/integer-mult-bounds/pull/479),
head `40dd01058439cdffae3e3b41c4fe52edaccf5f91`, already supplies the
additive chirp-residue schedule and its adjacent-axis tape argument.
Ross Richardson's [PR948](https://github.com/CrocSwap/integer-mult-bounds/pull/948),
head `eb11543094825c193c4bccece4857601fcd1620a`, checks its symbolic
transitions. I implement the encoded lowering, numerical dyadic-power
evaluation and complete consumer that those sources leave open.

I retain the whole corrected [PR3709](https://github.com/CrocSwap/integer-mult-bounds/pull/3709)
export at `62264289adb01f3ba4930cd0154c75887f96203c`, including its source
notices. I preserve Mason Hale's certified interval reference and the
source07/source08 Fourier, resampling and assembly attribution. I record
the expansion decision and current claim in
[Discussion3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664).

## Reproduce and review

```sh
python3.12 scripts/research_package.py --package research/physical-chirp-middle --check-only
python3.12 scripts/research_package.py --package research/physical-chirp-middle
```

I register seven standard-library Python 3.12 suites with a combined
timeout of 1140 seconds. [EVIDENCE.md](EVIDENCE.md) records their scope.
The public receipt identifies the final committed export and hosted CI.
The official export includes the predecessor and declared reference inputs;
you can run its suite entry points outside Git without network access.

I executed the full p16 packet using both the original reduced q2 setup
and an exact specialization of three fixed fractional-power values.
I obtained the same 288-bit payload in both runs. The registered fixture
uses exact integer certificates for those metadata values and executes the
physical data operations, including both endpoint products and the full
convolution. I disclose the specialization and its rejection gate in
[EVIDENCE.md](EVIDENCE.md).

| Implementation | Responsibility |
| --- | --- |
| `chirp_odometer.py` | Fixed-width adjacent-axis state and encoded carries |
| `phase_basis.py`, `chirp_kernel.py` | Certified dyadic-power table and full numerical kernel |
| `phase_streams.py`, `cyclic_engine.py` | Exact phase products, cyclic adapter and signed width recovery |
| `chirp_engine.py` | Complete kernel/endpoint/convolution/endpoint caller |
| `chirp_sources.py`, `chirp_plan.py`, `chirp_packets.py` | Source binding, geometry and packet admission |

## Limits

I use the input norm as a caller obligation. I check dimensions, formats,
source units, exact packet extents and signed headroom. I retain the
inherited Fourier supplier/refinement hypotheses and leave the selected
frontier unchanged. I have not executed production GL64/O73 or established
the complete Gaussian/CRT/integer join.

## Open next questions

1. Can a physical Gaussian expansion/compression pair call this middle
   map with its actual norm, precision and complete field layout? Start
   from the pinned bulk Gaussian normalization and its extra inverse
   scale. Its numerical producer and full paid layout remain open here.
2. Can the mixed-radix CRT entrance and return preserve the valid interval
   and padding through the full caller? Start with one actual source/target
   field conversion and the two retained S factors in final recovery.
   A coordinate-slot permutation alone does not supply that conversion.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
mathematics, implementation, source-analysis agents, checks and prose.
I claim no independent human review or formal-kernel verification.
Apache-2.0, subject to the retained source notices.
