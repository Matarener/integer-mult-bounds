# Verification-key headroom: independent publication source review

Status: PASS_PUBLICATION_SOURCE_REVIEW_ONLY at the exact manifest below.
No remaining source blocker within the declared serial, stable-checkout scope.
Parent-owned execution and committed publication checks remain separate gates.

Reviewer: OpenAI Codex / Astra, separately from the publication-wrapper author.
The reviewer performed only source reading and standalone standard-library
file/hash/JSON/metadata comparisons. No package or scientific module was imported,
no compiler or corpus parser was run, and no numerical/timing, Git, or browser
operation was performed. This report is outside the proposed package; no measured
source, package source, data, prior receipt, or other agent's file was changed.

## Confirmed source and evidence findings

The independently checked `MEASURED-CONTEXT.json` census equals all 164 files in
the original frozen baseline and all 177 files in the measured actual-key stage,
including each byte count, SHA-256 and mode. Every file needed by the sparse
publication reconstruction is present with identical bytes. All original
baseline files use mode 0644; measured stage files use 0644 or 0664. Git's
executable-bit representation cannot retain the latter distinction, so the new
external reconstruction explicitly restores measured stage modes before checking
the complete census. It never changes the source checkout's modes.

All 47 `ARCHIVE-MAP.json` copied-file rows equal the corresponding original local
files by complete bytes, size and SHA-256. Reversing every declared capture edit
in reverse order, with unique seam checks, recovers the complete original
`native_cache.c` SHA-256
`78ed2e240ee40ce4989a4718e77e8b3967b092d2bf8c900124a26942c98a14cb`.
Only the capture C file and its native-loader hash are baseline overlays.

The finite wrapper calls the byte-identical historical `finite_controls` helper
from `run_pilot.py`; it does not call the timing/corpus entrypoint. That helper's
checks use explicit conditionals and exceptions, so normal and `-O` registered
commands can exercise the same 82 finite receipts and 50 natural rehashes.
Compilation uses a fresh external build directory, unchanged source loader,
existing Linux CPython 3.12 headers/compiler, warnings as errors, and no install.
Actual successful normal/optimized execution remains a parent-runner obligation.

The new data verifier implements a separate ordinary dict/deque FIFO oracle.
For all 2,579,750 seven-exact-int keys it checks every little-endian uint64 result
ID, every hit/miss/eviction flag, all 80-operation and final-partial cumulative
prefixes, and the final original counters. It compares full ordered values;
hashes do not replace the item comparisons. Transport hashes authenticate
immutable compressed inputs, while uncompressed hashes and complete values
are authoritative for regenerated output equality. The source-specific replay
preserved object identities only in the original in-memory timing run; the
archived block transport explicitly does not preserve cross-block identity.

The parent-owned `HEADROOM-EARLY-ANCESTRY.json` records successful ancestry checks
for base `19fdb086ea96af9a9f87936a2b888e10af4ed810`, own input commit
`f901e992a3846ff0351bfb0caf75b6167788cd74`, and official archive input commit
`ccb92b752ab31df4220780a580cc14d9e86ffeca` against the input head. This reviewer
read that receipt and did not perform Git operations. Final committed-byte and
source-history preflight remains separate and required before publication.

## Findings sent to the author before freeze

1. The initial `corpus_blocks` implementation attempted one extra pickle load and
   accepted `EOFError`. That does not establish exact absence of trailing bytes:
   an incomplete trailing pickle can terminate in EOFError. A strict raw-byte
   EOF check and safe opcode validation are required before final clearance.
   The initial `find_class` override alone also did not establish the claimed
   rejection of every unsafe pickle mechanism, particularly cached extension
   opcodes. The requested repair is confined to the new archive wrapper;
   historical measured source is retained verbatim.
2. The parent separately identified that an unconditional `TemporaryDirectory`
   cleanup discards finite-control compiler logs on failure. The new wrapper
   must preserve its external build directory on failure before registration.

The repaired wrapper now scans each bounded object with an explicit plain-only
opcode allowlist before unpickling, uses a fresh memo per object, and checks raw
decompressed EOF after the final expected object. GLOBAL, STACK_GLOBAL, REDUCE,
BUILD, OBJ, INST, NEWOBJ and EXT mechanisms are excluded before deserialization.
Because the scanner consumes exactly through STOP, an unpickler cannot hide
trailing bytes through source-stream read-ahead. This resolves finding 1 by
source inspection; parser execution remains with the parent. The finite wrapper
now uses an external mkdtemp directory, retains it plus FAILURE.json and an
exception evidence note on failure, and deletes it only on success, resolving
finding 2.

The parent also found that a fully read-only export leaves copied baseline modes
at 0444. The repaired reconstruction makes only its fresh external directories
writable, restores all original baseline file modes, and then restores all
measured stage modes. This resolves the read-only-source issue by source
inspection without chmod or writes to the source checkout.

## Final source and metadata clearance

The independent static check rehashed all 252 protected rows in the final
`CODE-SOURCES.json`, verified their byte lengths and Git executable-bit
semantics, and found no discrepancy. Its source census covers all 52 `.py`,
`.c` and `.inc` files. The 254 package files differ from that manifest only by
its own file and the explicitly excluded `VALIDATION.json` receipt. The latter
is a pending-status record, not a proof-relevant numerical/source input or
substitute for actual execution receipts. New wrappers, unchanged scientific
context, DATA/FORMAT/MEASURED metadata, original evidence and all immutable
corpus/canonical streams are protected. Registered entrypoints authenticate
those inputs before decoding or source loading and again before success.

All eight SOURCES rows match retained local file bytes by SHA-256 and a separately
computed Git blob SHA-1 (standard-library hashing, no Git invocation). All six
live input paths appear in VERIFY; those input sets are equal. The recorded base,
own input commit, official archive head pin and early ancestry receipt agree.
The original task card equals the full card in the exact pinned local catalogue.
These static comparisons do not replace the parent's final committed-byte and
source-history checks against the actual publication commit.

VERIFY registers exactly four commands: fresh finite controls under normal
Python, the same controls under deliberate `-O`, the complete streaming data
oracle, and exact context reconstruction. Their per-command bounds are 60, 60,
180 and 60 seconds. There are no required package installations and no timing or
capture rerun in registered checks or CI. Optional `replay_capture.py` is separate,
explicit, single-shot and guarded; its new timings cannot replace the retained
samples. It compares all regenerated key values/order rather than requiring new
gzip container bytes to match.

README and TASK explicitly preserve the negative conditional result and unmet
complete target, scope the task's completed outcome to the archive/cost audit,
and keep the separate matrix result outside this performance claim. They retain
the zero-reserve sensitivity result, cross-run/clock-overhead limitations,
nonzero unpriced retained work and complete future bill, original callback/Fraction
integration obligations, predecessor attribution and Apache-2.0/AI disclosure.
The original nested NOTICE is byte-identical. Their open question requires new
source/cost evidence before any further construction or scientific run.

The parent-owned freeze receipt records all 254 package files plus the official
archive in a Git-free stage with files 0444 and directories 0555. Source review
confirms that fresh external reconstruction restores destination-only modes,
finite build failures retain external evidence, and no registered source writes
or historical benchmark execution are required. Actual read-only-export success,
finite normal/optimized controls, full data equality and context execution are
not claimed by this reviewer; they remain parent-runner checks.

### Exact reviewed publication identities

| File | SHA-256 |
|---|---|
| CODE-SOURCES.json | `9b3c05b97f926c2c767ad394a399554cd4034a86526dead247251e0921c697d5` |
| verify.py | `e6218ee4d0dc1154c5d6cc90a20405dbbf0d753ba39ddffeeb29b4f9fda0b39e` |
| archive_support.py | `5d9db9496e040adac339bcbfdaf97e3561592a6f814b11a455bf700e64406fec` |
| replay_capture.py | `226aa76079545339cdc72ac65483628db8e7a42a071bbae21bf17baad5fc9126` |
| MEASURED-CONTEXT.json | `c0586ccf6b21ee92015ea7d6a3d88a672f21d556b09332cd6d4502730b074789` |
| FORMAT.json | `baf52afe2d0446706cd3c415ad59b603fb1f4f42b7b7d5c518dfe5d9693fda33` |
| SOURCES.json | `2806dd664a5af54719fc41f648025e231de5cf917f464393dffe276fdb40e559` |
| VERIFY.json | `1ffed66e98ce509f3b06e07aa6ab5f437ca9a3fea17f29870cf2fbce7b58596f` |
| TASK.json | `29a16369f5762f07e98df4ea91816232545744751610e262453f6528d417eab7` |
| README.md | `910241eb8d4968a97f168f4b54832b1dc66e8fa3fb230a5020a823e5455b81b3` |
| NOTICE | `5745bd98e57fa8bed84dc589cabbe34a23541c88aa6c9877633ee37bc923ad0d` |
| VALIDATION.json (pending receipt) | `e527f5abd9fa9a3d1e42c8e14751484b28d97ec3038b99f704ea868e5eb1ee83` |

The measured comparator remains `ee3fb2af131878fa2065d1b50d02f2f865c0ac61c9ec0a3d66b15c910f3d9cf6`,
its loader `d6912e01fafa7a79a635812e4884d776757f2e24996850b692f0eb8825bf7968`,
and its finite helper `e02ebb21c4985001f57d947414c52366de77e8db5dfe713440a921e5f4cb1c8e`.
The unchanged captured corpus remains `660e3f8d6dcd147c97a5691feab301e558cc70097c7d4c3d00e4f116482d2699`.
No claim here supplies a new execution result or independent full C memory-safety
proof. A proof-relevant edit after these pins requires renewed review of that edit.

## Admission boundary

The retained actual-key conditional nomination remains rejected in both wall
and CPU, including its zero-reserve sensitivity calculation. The earlier integer
gross anchor is from another run and is not an achieved saving; residual integer
work and the complete integration/build/validation bill remain unpriced and
nonzero. Publication cannot admit the further complete PR5864 15% target, a GMP
or private-integer construction, full Fraction/API/GC integration, a new kappa,
or a universal impossibility claim. The separately qualified matrix result does
not contribute to this target.
