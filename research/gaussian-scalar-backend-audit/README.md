# Independent normalized Gaussian scalar backend audit

This audits one acceptance gap in Jose Manuel's completed normalized Gaussian
interface, PR4205 at **66b95cc916552f487203be14fd99a7aea0bdd78e**. Its finer
references explicitly share the producer's interval backend. This contribution
adds a separately frozen certified transcendental implementation, binds it to
every scalar preparation in the nine saved cases, and independently derives the
existing scalar width and precision implication from the actual source code.
It preserves the author's active raw/common-reference extension as separate work.

## Exact result and evidence

For every nonnegative rational `f` and integer `J >= 16`, the unchanged
`Gaussian.exponential(f,J)` terminates mathematically, encloses `exp(-pi*f)`, and
has width at most `512 J^2 2^-J`. The written source audit checks rational
coercion, the large-exponent shortcut, Taylor stopping, reciprocal, squaring
and clamping. It also derives the coefficient precision rule `J=2p+32` and
the positive conditioning denominator at `J_Q=2 ceil(2/c)+36`.
This uniform width assertion is for the constructed argument `pi_interval(J)*f`,
not arbitrary wide boxes passed directly to `exp_negative`. The scalar
conditioning allowance is not an independent matrix-inverse theorem.

The independent oracle uses a positive arcsine series for pi and a negative
alternating exponential series with outward dyadic squaring. It imports no
predecessor code. Its core, proof and 36 self-tests were frozen before it read
the source-generated input-only queries; source numeric outputs were never
shown to that implementation. A second freeze records query evaluation and a
small exact replay checker without changing the mathematical core.
Separate prepublication review corrected the query checker's Boolean/integer
receipt comparison; the original mathematical freeze and certified intervals
remain unchanged, and the updated query freeze records the correction.

All **128 unique scalar inputs** are certified independently. Every certified
oracle interval is contained in the corresponding actual source interval,
covering all **186 delegated source calls**. This containment direction is
essential; overlapping boxes alone would not certify the source enclosure.
The actual calls cover 11 large-exponent shortcuts, 141 ordinary backend calls
and 34 exact-zero bypasses. Extra inputs include tiny factors, very large
factors and points near the shortcut regime at three working precisions.

The adapter imports the unchanged real Gaussian class and its original module
closure. It wraps `exponential` only to record calls while delegating to the
original method, constructs the actual nine producer instances, and executes
their retained `Tsec` expression directly. It checks **43 retained quantized
offsets**, **61 finite offsets**, scalar reciprocal allowances, finite omitted
tails and the saved coefficient/kernel ledger. The cases include both half
shifts, nonzero truncation, a 512-bit incoming-precision parameter and two output precisions.
Three calibrated source mutations expose omitted pi, zero-billed quantization
error and a zero-billed automatic tail. They are failure controls, not defects
observed in the original source.

## Reproduction and integrity

Python 3.12 and its standard library; six normal/strict-optimized commands:

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-scalar-backend-audit
```

The commands replay the independent self-tests, every independent query and
the actual scalar source adapter, without writing package files. `FREEZE.json`
and `QUERY-FREEZE.json` retain the two distinct independence checkpoints and
all named receipt bytes. `SOURCE-CAPTURE.json` retains the complete observed
scalar data; `INTEGRATION-RESULT.json` binds its canonical digest. The original
oracle `RESULT.json` is its first-freeze receipt, not the source integration
result. `WIDTH-AUDIT` and `ORACLE-REVIEW` record the separate written reviews.

All 17 unchanged source exports, licenses and NOTICE are pinned through public
source ancestor `607924844afbfb907c835dbf47bc2ac1da00557f`.
`SOURCE-PINS.json` records their original repositories, paths, commits and credit.
The scoped attributes preserve original bytes, including the evaluator's CRLF.
Report source basenames resolve under `source/`; independent freeze entries
resolve in this package. Source module imports do not execute their circuit
factories.

## Remaining obligations

No `Gaussian.compile`, `compile_root`, `Full` construction, admission solver,
gate execution or global circuit replay occurs. This does not independently
admit the leading-section inverse proof, full normalized circuit, raw scalar or
diagonal gauges, a common rounded reference, efficient setup, physical delivery,
tape costs, native/outer construction or multiplication theorem. Exact scalar
arithmetic is an offline correctness oracle, not a fast physical producer.
Written and mechanical review are not independent human or formal-kernel
acceptance. No new kappa or selected-frontier change.

## Open next questions

After refreshing its current claim, independently audit one completed raw
gauge/common-reference implication at its own frozen head. That matters because
normalized scalar correctness does not pay raw scaling, inverse sensitivity or
shared-reference assembly. The author's active extension and all complete
circuit/physical obligations remain separate; see `TASK.json` for the bounded
follow-up and blocker.

## Credit

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance, supplied
the normalized interface, scalar width argument and source integration. Mason
Hale/PR2313 supplied the unchanged interval routines and earlier dense Gaussian
execution; retain its NOTICE. Credit Jeremy Kothe/IdeaOuter for `Tsec`, Vlado
Vojdanovski/PR1673 for q-LDU and full circuits, Chafik Boukhalfa for phases, Cinna
Davis for the caller, and the retained Gaussian lineage. James Reed's prior
finite audit at the earlier head excludes this new scalar layer. Classical
series and interval estimates are not claimed as new general mathematics.
ToikY used substantial OpenAI Codex assistance for a separately implemented
oracle, source adapter and separate proof/code review. Apache-2.0.
