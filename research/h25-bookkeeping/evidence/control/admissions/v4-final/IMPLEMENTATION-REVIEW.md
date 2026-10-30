# Independent H25 implementation and integration review

Source review only, 2026-10-28. No reviewer scientific imports, compilation, numerical execution or source implementation edits. Parent alone owns execution. All observations below are explicitly parent-reported, not independently replayed by this reviewer.

## Decisions and exact reviewed lane sources

| Lane/file | SHA256 | Source disposition |
|---|---|---|
| P1 `set_reuse.py` revision 3 | `d375bb352ddff7a922bf1413d2911935b977d3bcce670db4954f6939afa15f29` | Parent-reported complete pilot passed; retained historical source. |
| P1 `set_reuse.py` revision 4 | `eeeead34731e73f74dff250f354e57b72314c4e18670848bfa9f48c87de1305d` | Admit fresh combined normal/optimized finite union; runtime validation pending. |
| P1 `finite_set_controls.py` initial version | `2c481c74cbf85edc1734b3d139cc665ec731b0910317cb2636da57b423844231` | Normal passed; optimized fixture expectation needs the bounded repair below. |
| P1 `finite_set_controls.py` revision 3 | `9fbe76c6d5ce123d12fc3c231786a9a85996fad41102835e08112768dd75738d` | Control-only repair independently reviewed; parent reports both finite modes passed. |
| P1 `finite_set_controls.py` revision 4 | `760f151efd18b281c7045e979d2c3f95ce58c5d8bb1340e34d2afa68bd072919` | Retains the repair and all prior controls; adds exact-pin policy and receipt consistency controls. |
| P2 `guard_candidate.py` | `320435ec4125544f2b2aedf74f21469b232d08683fe76f0913607516254bbd29` | Admit finite and, following reported passes, complete pilot. |
| P2 `guard_controls.py` | `514e3d08793323cf216c7a1f76cafdc8dbba4ab4656e64167c788985f9e63291` | Bounded independent behavioral controls accepted. |
| P3 `trace_encoder.c` | `57d6f0f71d5bfd2145397ac0159837d32990b276fead2ec1b1d6854d8913bd7e` | Admit finite and, following reported passes, complete pilot. |
| P3 `trace_adapter.py` | `4bdb401271ffd049c52eff0edc28d8d604a11faf66fec419555a82cbd3b32d60` | Same source gate. |
| P3 `trace_controls.py` | `527bb08e870dc2ee19bebf101e7353c6db8422a5702a80bca231b54d2a4af447` | Original observer, exact bytes/prefix/error controls accepted. |

P1 authenticates the source, splices the original prefix and literal fallback tail, retains both intersection loops, and uses live source globals. Parent constructor captures, final wrapper sealing, single-use reservation before the prefix, post-prefix shape/Fraction/environment checks and finally expiry implement the reviewed new whole-tail invariant. Ordinary unleased calls delegate the original once. The explicit private-list clearing and left-reference reset address traceback-retained frames. This is a scoped fresh frozen-caller contract, not generic alias or process-security proof.

P2 preserves all distinct predicates, slot checks, short-circuit ordering, messages and original call boundaries. It deduplicates only repeated function identities. Controls reuse four bindings, with 237 mutation pairs × 7 actions and 14 stable pairs; they compare behavior rather than reimplementing the guard. Empty-cell errors, fallback entry, first failure, same-code distinct functions and shared-state restoration are covered.

P3 retains input snapshots and original output validation, then emits a complete record through a stateless checked native call. Exact types precede direct container access, unsigned overflow is the only cleared conversion error, borrowed references remain within a GIL-held call, and one bytes allocation copies the bounded stack buffer. The adapter preserves count-read and hash/byte/count order. Primary [FASTCALL](https://docs.python.org/3.12/c-api/structures.html#c.METH_FASTCALL), [integer conversion](https://docs.python.org/3.12/c-api/long.html#c.PyLong_AsUnsignedLongLong) and [bytes ownership](https://docs.python.org/3.12/c-api/bytes.html#c.PyBytes_FromStringAndSize) documentation supports these API checks. Controls include exact record bytes, every prefix, width/type/fallback boundaries, digit-limit restoration, hash/counter failures and alias/reference behavior.

## Integration and runner source gates

Reviewed integration sources, rehashed unchanged for the revision 4 combination gate:

- `integration/adapters.py`: `f7ca7f4f03ac63c1a95ba42f06149543211566de5e29f487a3dc4d08c5ee9b94`
- `integration/full_driver.py`: `5b963a5f108b334a627e68001c80b9843fb300c7394693e72f34ce0a6050e6f1`
- `integration/derive_driver.py`: `a18d312e6992786fa7b2cf8a613eea068e0ad282ff684d03781a5928bde2692a`
- `integration/DERIVATION.json`: `6a1b9148c48fe9016a3dc98c1aec339fba3efe73f421ecac2d3cb12d87c53256`
- `run_guarded.py`: `b74366a925dd44c0e95a7ad87aa1505cbdcad9fefcb9360d77d6459679f102be`

Both new arms execute the native C configuration. The driver has its own digest and separately names the immutable original driver digest; declared literal edits and exact inverse evidence do not claim original driver bytes executed. The complete scientific anchor, original phase counts, native coverage, original controls and observer remain intact. Selected new source custody is charged inside the child before imports and before finite/full receipts. Finite returns also recheck original and copied inventories. The outer runner separately pins stage bytes/modes and preserves failures under one lock and aggregate budget.

The initially proposed late trace-class import would have compared two candidate encoders in the old finite suite. Parent repaired this before execution: `backend.ComplementTrace` stays original; the candidate full observer is explicit; new controls compare it to the unchanged observer.

The new native owner/entry check is installed before binding and initialized before base guard construction invokes `self.check()`. It runs at every original wrapper boundary. Five negative actions cover held guard, native Gram/complement and wide fallback Gram/complement without advancing counters or observations. Following parent-reported finite passes, source admission supports all three complete pilots. The reviewed sources are also admitted to a fresh combined finite-union stage; combined complete qualification still depends on that union passing.

## Parent-reported observations and retained failure

| Work | Reported outcome | Limit |
|---|---|---|
| P2 normal / optimized finite | PASS, about 1.78 / 2.04 seconds wall | Parent report; no reviewer replay. |
| P2 complete B/C pilot | PASS, wall 27.9081 → 25.7346; CPU 27.79 → 25.62 seconds; exact science agrees | Approximately 7.79% / 7.81%; one pilot, not a qualified factor. |
| P3 normal / optimized finite | PASS, about 1.85 / 2.22 seconds wall | Parent report. |
| P3 complete B/C pilot | PASS, wall 27.0782 → 25.0697; CPU 27.01 → 24.98 seconds | Approximately 7.4%; one pilot, not a qualified factor. |
| P1 normal finite | PASS, 2.419 seconds wall | Complete ownership/performance not yet established. |
| P1 optimized finite, initial control | STOP, 2.8227 seconds, collision fixture expected a callback absent under optimized assertions | Failure retained and charged. No complete P1 admission yet. |
| P1 revision 3 normal / optimized finite | PASS, 2.4495 / 2.5654 seconds wall | Parent report. |
| P1 revision 3 complete B/C pilot | PASS, wall 28.38259 → 25.13970 seconds | Parent report; about 11.43%; one pilot, not a qualified factor; does not qualify revision 4. |

The P1 optimized failure is a control expectation issue: the original tail's collision-triggering `got.get` calls are inside an assertion removed by `-O`. Revision 3 was independently source-reviewed and approved: it keeps unconditional outcome, callback-sequence, fallback and lease comparisons, requires nonempty callbacks with assertions enabled, and explicitly requires empty callback lists under `-O`. The logging-Q fixture received the same justified correction because all original `verify_map` Q calls occur inside assertions. No controls were removed and the adapter is unchanged. Freeze a new stage before rerunning; do not erase the failed version.

## Revision 4 Fraction source portability gate

**ADMIT_SERIAL_COMBINED_FINITE_UNION_ON_FRESH_REVISION_4_SOURCES.** Independent source review finds no blocker in the bounded two-pin change. Hashing and inert AST comparison confirm the active local file has SHA256 `cf33568f7b767f66896995a7a81cc662e8be226f2e58efb61d2028f64eb5d231` (38,067 bytes), while the retained official-reference file has SHA256 `d52d1ab9d5be26924e4914a5e40069c992bbfa68f773694c2e5ee8452d0766a0` (38,147 bytes). Only `Fraction.__pow__` differs in the AST; constructor, hash, equality, properties and `_hash_algorithm` are identical. Official tag/commit retrieval provenance is the worker's retained evidence, not a second network retrieval by this reviewer.

The adapter uses a fixed two-entry tuple and requires an exact string before comparing its digest. Unknown digests and string subclasses still reject. It hashes the active `fractions.__file__`, selects a profile, and compares loaded functions with that source compiled locally by the running interpreter at the current optimization level. Descriptor, MRO, global, class, function and per-reservation/per-admission freshness checks are unchanged. The existing driver/native backend CPython 3.12 family gate remains unchanged. No alternate Fraction implementation is loaded by the added controls or adapter.

The receipt now carries the actual selected `fraction_sha256` and `fraction_source_profile`, rather than a hard-coded local digest. Added controls recognize both exact pins, reject three unknown/nonexact inputs, and compare each binding receipt with the pin policy. Every revision 3 differential control and its optimized-mode repair remains. The previous local pilot is evidence for revision 3 only.

Verified supporting file hashes: `PORTABILITY.md` = `8f2e5b95ade7b100634d1d875d7ac8fbef608ed74e2539f340a22d0c17a212e1`; `PORTABILITY-SOURCE.json` = `2c385ad61b64fb7e58d915ac597eb223d65365fcf1737dbd6320a2b438f3cc82`; `SOURCE-READINESS.json` = `4ac8964004938d4d02840e135254b3bc1a57c0cc3f1018ed50909bf79a1cb556`.

The new pin lookup, selected-profile receipt, controls and reference-file custody belong in the complete bill. Existing custody enumerates selected `.py` sources, so retaining `cpython-3.12.15-fractions.py` adds its 38,147-byte read/hash to selected P1/combined candidate custody without executing it; the baseline with lanes=none does not select that directory. An exact-source policy pass does not establish hosted runtime compatibility: actual hosted interpreter and active Fraction digest receipts, normal/optimized finite validation and the complete assertion-on replay remain required. Hosted correctness cannot transfer local performance measurements.

## Combination gate and remaining obligations

The proposed order is compatible: P2 guard, then P3 extended guard; old controls keep the original observer; new P2 mutations restore before P3 native/digit mutations; those restore before P1 Fraction/hook controls. Full candidate trace exists before native binding. P1 method is installed before phase wrapping, constructor captures finish the original constructors, seal follows all class/phase wrappers, and arm/disarm bracket the authenticated CLI.

Pending: fresh revision 4 immutable source freeze; combined normal/optimized old-and-new finite union; actual complete combined output/coverage and cost receipts; fresh predeclared B1 C1 C2 B2 B3 C3 medians and noise gates; hosted/delivery/publication checks. The combined finite-union source gate is granted, but complete qualification may proceed only after both finite modes pass. Combined call accounting must add ExtendedGuard's base-check dispatch and encoder-owner checks, plus lease/source/control/portability work. Preserve all failed and superseded stages and charge their costs. The parent remains the sole runner under the declared 180-second, 1-GiB per-process and 600-second initial/1,500-second total campaign limits. No component percentages may be added. The goal still requires at least 15% complete wall and CPU improvement, each saving exceeding both within-arm ranges. This review does not claim that target has been achieved.
