# Another-platform native replay of the fixed GL3 RUP certificates

This contribution executes the unchanged length7/8 CNF and RUP certificates from [PR4211](https://github.com/CrocSwap/integer-mult-bounds/pull/4211) on another native platform, with exact source/input hashes, strict container checks, complete logs and decisive controls. It takes the explicit replay handoff left by the separate support (#4214), normalization (#4223) and direct-CNF semantics (#4230) audits. Those implications are not rerun or silently upgraded here. The original author already produced the proofs and ran this checker on Windows/MinGW; new execution uses the same official checker implementation, not a second checker algorithm.

## Exact scope and trust

Native success means the pinned C checker reports a verified RUP refutation core for the exact saved formula/proof bytes under `-U`. Its backward mode may skip unused proof additions; this is not a claim that each unused line individually passed a redundancy check. The harness additionally validates every ASCII record and its exact declared byte/line/hash container before execution. Standard compiler, native runtime, checker logic and the mathematical encoding remain trust links. Independent-human/formal-kernel acceptance, explicit model lower-bound admission, other models, physical compiler/caller/invoice, supplier/native outer theorem and a multiplication-bound improvement remain separate. No new kappa, frontier edit or merge.

The authenticated original source is `ca0002008b497428f0b651501c4a220a9d2785e7`. Fourteen original exports, including both saved CNFs, compressed proofs, checker source, declarations, logs, NOTICE and licenses, are retained unchanged through public ancestor `37fdc4122f84d80cccd85aa51f631acf79904003`. The actual saved CNF hashes also equal the formula hashes regenerated in the preceding semantic audit; no formula or proof is synthesized here. `SOURCE-PINS.json` records original paths, bytes, SHA256 and Git blobs. `SOURCES.json` binds cold Git history, including the dedicated native workflow; source-specific CRLF and compressed containers stay exact.

## Reproduction and resource gates

The retained macOS arm64 / Apple Clang21 run passes both proofs with exit0 and `s VERIFIED`, with zero RAT lemmas reported in each refutation core. Length7 checks the saved 18,882-variable /61,138-clause formula and3,657,455-byte /39,177-line proof; length8 checks30,591 variables /97,770 clauses and108,920,783 proof bytes /587,886 lines. Reported core counts are24,548 /62,813 input clauses and8,558 /216,900 learned lemmas. All six native controls pass. Local external checker times1.347s /86.566s are environment metadata, not a portable performance claim. Binary SHA256 is `b3c5aecc22d3f47f009dfbaea0f7c4429bcadaba6d918be2292f76025b4e9b2b`; the full compiler version and flags are retained in raw logs.

The ordinary registered commands are Python3.12 standard-library **evidence inspection**, not new native execution:

```sh
python3.12 -B scripts/research_package.py --package research/gl3-rup-native-replay
```

Fresh native execution needs a POSIX C99 compiler and an explicitly new output directory outside this package:

```sh
python3.12 -I -B research/gl3-rup-native-replay/native_replay.py --output /new/external/replay-directory
python3.12 -I -B research/gl3-rup-native-replay/verify.py --native-receipt /new/external/replay-directory/RESULT.json
```

The harness compiles the unchanged predecessor-vendored drat-trim bytes, SHA256 `78026871882de3f2fee66034e549e9c1a0a9a5291abd817d06f611f9ba0f355d`, with C99/O2 and the predecessor's compile-only `getc_unlocked=getc` alias. The predecessor retained CRLF containers; the official C and MIT license at `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` use LF. `UPSTREAM-LINE-ENDINGS.json` proves exact equality to the official Git blobs after only CRLF-to-LF comparison, without editing the bytes executed. It records actual compiler version/command, binary hash, platform, raw stdout/stderr and exact input hashes. It first calibrates six tiny controls: non-UP ASCII RUP and binary-parser positives; invalid empty-only and satisfiable wrong-formula rejections; and a required RAT-core proof accepted in default DRAT mode but rejected in RUP-only mode. Positive acceptance requires exit0 **and** the exact standalone `s VERIFIED` status, with no timeout/error/nonverification marker. The checker can exit0 on some errors; exit code alone never certifies success.

One proof process runs at a time. Each has internal wall limit300s, child CPU limit300s and external wall limit420s, with bounded termination/reaping; compile60s and tiny controls10s have separate caps. Stream decompression cannot exceed authenticated declared bytes. Free disk must remain above8GiB plus256MiB headroom, with additional materialization bytes reserved before each proof. These are disk checks; no hard RAM cap or reliable per-process peak RSS is claimed. The dedicated read-only Ubuntu24.04/Python3.12 workflow has a20minute job cap and retains raw logs even after failure. These limits bound failure, not a completion guarantee.

`NATIVE-RESULT.json` and `native-logs/` retain the local execution receipt. The generic verifier independently authenticates raw logs and all proof-relevant fields, and tests meaningful corruptions. A fresh receipt comparison excludes only documented runtime metadata such as compiler/binary/platform, absolute temporary paths and timings; all proof inputs, grammar counts, native status/core counters and control outcomes remain compared. Exact compressed input hashes matter; no regenerated gzip-container identity is used as mathematical evidence. Publication cold replay, hosted native execution and final preservation are separate receipts in the public handoff.

## Open next questions

The next useful check is a separately implemented RUP checker or formal-kernel translation on these exact inputs, followed by an explicit model lower-bound admission that names every semantic, normalization, support, padding and positive-witness dependency. First specify the proof semantics and trust boundary, refresh overlap, and budget the replay before executing it. This matters because another platform running the same C program does not remove its implementation/compiler trust. Independent human review is still absent. A physical or supplier application must separately identify its actual caller and fully charged invoice; these two fixed formula checks do not provide it.

## Credit

Brian Ross supplied the conceptual strategy, direction, oversight, encoding, certificates and original checker integration with substantial OpenAI Codex assistance. Retain Hanson Sun seed18 and Josie Elliston's length10/three-register lineage, James Reed's earlier finite pin/seal review, and the distinct #4214/#4223/#4230 audits. Marijn Heule and Nathan Wetzler's drat-trim retains its MIT notice; Glucose4/PySAT proof-production credit remains in the original certificate declarations. ToikY used substantial OpenAI Codex assistance for this native harness, receipt inspection and separate code/evidence reviews. These are not independent human reviews. New code/documentation are Apache-2.0; original NOTICE/licenses are retained unchanged.
