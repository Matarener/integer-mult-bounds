# Verification evidence and limits

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I ran the local checks on Darwin arm64 with Python 3.12.13. I used the
repository's `run_python_replay` launcher with a fresh bytecode namespace,
`-I -O -Werror -B`, explicit process-group timeouts and no external Python
dependencies. The checks use explicit exceptions, so `-O` does not disable
their assertions. [VERIFY.json](VERIFY.json) registers eight commands with
1180 seconds of total timeout allowance.

## Mathematical and implementation coverage

| Suite | Evidence |
|---|---|
| sources | Complete 43-file core export, correction commit/archive, 14 live input pins, seven local runtime modules, one physical Count/Tape cohort and four binding controls |
| budget | 1248 exact production guard cases, complete block/tile word invoice, separately charged setup and inherited Fourier comparison |
| geometry | 78 exact exponent/crop identities, negative origins, period seams, `u*theta=4/7,4/13`, equal right endpoints and three encoded production radii |
| production | Four complete production tile descriptors at `p=4800,alpha=4,d=300`, including both period seams and a one-record ceiling transition; ten rejection controls |
| block | Two complete nonzero producer/block joins at p4/P32 and p8/P48, separate staged and periodic references, premature-extraction controls, 34 and 38 actual word calls |
| tile_overlap | Two complete blocks with equal source starts, values `[(3,0),(3,1)]`, 88 actual word calls, six fresh records and five retained overlap records |
| tile_wrap | Two complete blocks across a period seam, values `[(2,1),(3,0),(3,1)]`, 130 actual word calls, nine fresh records, seven retained overlap records, seven padding records and a clipped final block |
| ownership | Nineteen rejection/ownership controls, successful consumer reuse after failures and exact producer re-preparation |

The displayed output pairs are integer p-grid numerators. The explicit
fixtures use reduced radii and work grids; I do not apply the production tail
theorem to them. For the separate periodic reference I sum directed Gaussian
intervals through distance `8alpha`, round interval endpoints outward to
96 bits and add `2^-256` for the omitted tails. The tail estimate is
`(1/alpha+1/(16pi))*exp(-64pi)<2^-256`. I bound the maximum component error
by two target ulps. [PROOF.md](PROOF.md) gives the separate complex-norm
production argument.

At `p=4800`, the production checker derives `L=2^98`, radius280, w72,
P157286400, sigma19660800 and halo452984832000000. It checks tile indices
0,1,8,15. Tile8 has one fewer source record than the other three. The final
short block has length144. I inspect these encoded descriptors without
allocating `2^P`, a coefficient catalogue or a production-sized payload.

The actual finite consumers use the fixed 4096-bit crossover of their
inherited FftWord owner, so their recorded calls take its base/Karatsuba path.
PR3787 supplies separate actual FFT-path evidence and the retained all-size
word argument. I do not describe these expansion fixtures as new large-word
FFT execution.

## Stable payloads and preparation change

I compared exact page and output bytes before and after reusing the even
kernel pairs `k_d=k_-d`. I reproduced these hashes:

| Fixture | Page SHA256 | Output SHA256 |
|---|---|---|
| block p4 | `ea522ece071a20e7e4f3f07156aae149c425f0b642d04357eae7df51a563bcfe` | `17b837bf4383456d726bdee2c757903686c77451951319d6cdbcb0f52826e95e` |
| block p8 | `e7f9e13638be5ab74f68c2b33e2acb094c258bba998447277ff848038cd00b53` | `ba3a3fc42249d623b680b171fe61696ded2dab685d8e3b67ef891ccc1475a3e2` |
| overlap tile | `70d33b2d88b08d0f18af9eed039409c038b7f2e6ee97b2287ee4bcf418de24fc` | `cc050d5d43d1ba27893fe5658568da2157f278c545e550d08610ca4849b682fb` |
| wrapped tile | `645041b9abd04e9cba1c3ef5a3fa360d33c39392f6a6f26bb968db37a0b39b9b` | `d431d73e30d0270d3ce59de62f49169922ed409ff4c0dad8cfccd810f69b1d3c` |
| ownership tile | `1b91aa71588fe0296a04c1f0061cd0060c6b7f22135fa1247c9a3aee4b836247` | `bb2a4f35db7dd2f37c30c52d6f722af8eca987b1d549b3cb6d55cbf1332a0fa0` |

Reflection reduced the wrapped tile from32 to25 exponential evaluations and
from647 to495 Taylor steps. The block pair takes6 and9 exponentials; the
overlap tile takes15. I retained the complete fixtures and negative controls.
Local reflected-kernel debug runs took69.996 seconds for the block pair,
57.286 for overlap and142.403 for the wrapped tile. The complete ownership
run took38.950 seconds. These timings describe this environment, rather than
a portable runtime promise. The official publication receipt records the
final bounded replay and hosted outcome.

## Failures that led to corrections

I retained the following distinctions when preparing the final checks:

- The initial geometry checker mishandled marker initialization between
  cases. I corrected the checker and reran it; I did not change the geometry
  to accommodate those failures.
- The zero-scale ownership fixture did not distinguish early extraction
  from correct extraction. I restricted that negative control to the two
  nonzero-scale block cases and both complete tile cases, where it changes
  the result. The ownership fixture still checks its exact output.
- A short imaginary source record exposed a real scratch-lifetime bug in
  the tile validator. I nested the real component's ownership scope before
  reading the imaginary component, then reran the nineteen failure/reuse
  controls. The corrected consumer restores scratch and borrowed ports.

I count completed runs only. A prior source's timeout or successful receipt
does not count as execution of this package.

## Source and publication boundary

The loader authenticates the compressed core export SHA256
`5aaa84523bfa22eb817023d3130e8b8879153e9207e8f836cc6c61435fd051b8`,
its uncompressed SHA256
`2d97e093634a4119d9990dcc5d175917df3eabda5e8d1c204f640381e92ab4a2`,
and receipt SHA256
`d387e4d0a1a43b9b24104f76f8992603d4265bbe447601bea476d492e92e5340`.
It also checks the full inventory, member hashes and source head. The PR371
correction archive SHA256 is
`31a553fc4aa4443e60f285633ceb309edc84ede4f64ef7c2646f8806e61da1e8`.

The canonical [Discussion3664](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664)
records the publication head, official export/receipt hashes, unchanged-byte
replay, exact CI tree and final handoff. Keeping those transport receipts
there avoids a self-referential archive hash in this file. Source integrity
does not establish mathematical acceptance.

I leave the complete tensor/layout/CRT/integer join, production-sized
execution and independent review open. I retain the analytic, numerical
word-recovery and supplier premises from the pinned predecessors. I make no
new selected-exponent claim.
