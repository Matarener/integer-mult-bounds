# Local validation scope and findings

This is a fresh execution of supplied scientific programs and a local review
of their claim boundary. The separately implemented auditors were part of the
delivered research. Running them here does not create independent human
mathematical approval or a formal theorem proof.

## Source and result

Canonical main was fetched and the isolated `codex/conditional-kappa-0023`
branch rebased onto `12fa8c5c844be21bfefb38a19503fbd867a11244`.
The selected record continues to identify #1094 and its conditional
κ = 0.001672660197076918; its construction was not changed or cold-replayed.

The three delivered-file fingerprints match
[ARCHIVE-INTEGRITY.json](evidence/ARCHIVE-INTEGRITY.json).
Safe extraction authenticated 3,450 research paths in the cumulative overlay,
and all 240 current-round files matched the smaller new-research ZIP exactly.
The frozen `verify_scope.py` passes its 239 entries and 26 claim-source bindings.
Loose duplicate/downloaded files are not substituted for the authoritative ZIP.

The fresh scientific run passed all **23 stages**. All **59 regenerated
artifacts** have equal mathematical content under the comparison rules below.
The receipt is [VALIDATION.json](evidence/VALIDATION.json); its stage logs are
under [evidence/logs](evidence/logs). The host was macOS arm64, Python 3.14.5.
The receipt records the interpreter, platform, zlib, exact commands, scientific
source hashes, log hashes and each old/fresh artifact hash.

## Original replay-order failure

The delivered runner orders these stages as:

```text
p3_native_cover -> p3_independent_phases -> p3_independent_owners
```

`p3_native_cover.py` records the existing phase-audit digest in its `sources`.
Regenerating the phase audit afterward changes that digest, through regenerated
source-receipt metadata and compressed-container differences. The owner audit
correctly rejects the stale pin. The actual failure is retained in
[original-runner-stale-pin.log](evidence/original-runner-stale-pin.log).

The phase auditor reads the formal factorization and completed native receipts;
it does not require the generated p3 cover. Therefore the valid order is:

```text
p3_independent_phases -> p3_native_cover -> p3_independent_owners
```

The review runner uses this order and runs every original stage exactly once,
sequentially in the focused fresh replay. No scientific source or assertion is
patched. The earlier full-overlay attempt and its resumed stages were diagnostic;
the published 23-stage receipt comes from the focused input copy.

## Cross-environment comparison

The original comparison permits four named timing keys and exact old-to-fresh
hash references of the 59 regenerated artifacts. We preserve those rules.
Gzip containers differ across environments; their decompressed JSON is compared.
After all stages passed, the only remaining differences were host descriptions
in these three files:

- `complex/fresh-certificates/RESULT-H.json`
- `complex/fresh-certificates/RESULT-helpers.json`
- `complex/fresh-certificates/RESULT-logger.json`

Only `/environment/python` and `/environment/platform` in those named files
are excluded from mathematical equality, and both original and fresh values
are retained in the receipt. Fresh values must equal the executing interpreter
and platform. No other environment key is excluded. The old receipts describe
Linux/Python 3.12.14; the local run describes macOS/Python 3.14.5.

All 59 containers differ in this run, because source-receipt metadata and gzip
differences propagate through their exact hash references. Every remaining
mathematical field agrees. The final comparison was repeated after narrowing
these metadata exceptions; the successful scientific stages were not rerun
merely to change comparison policy. The receipt discloses that repair.

Four controls challenge that policy on the actual regenerated outputs:
changing the target κ, making a functional gap negative, adding an undeclared
environment field, and supplying a false fresh-interpreter description are
all rejected. Positive comparison succeeds before and after the challenges;
temporary output bytes are restored. See
[COMPARISON-CONTROLS.json](evidence/COMPARISON-CONTROLS.json).

```sh
python3 -B research/kappa-0023-productive-jobs/check_comparison.py \
  --repo /absolute/path/to/new-replay/repo \
  --report /absolute/path/to/comparison-controls.json
```

## Focused publication inputs

[IMPORT.json](IMPORT.json) binds the unchanged checkpoint, its executed inputs,
attribution and inherited written proof notes. It preserves all 240 current-round
files. Historical experiments outside this closure remain in the complete
cumulative Downloads archive. The focused replay needs no private archive.

The first replay copied 301 delivered files and 16 main inputs. Publication
then relocated an unexecuted historical README to preserve main's existing
README and added 65 unchanged inherited proof notes for review. Seven
`kappa-next-regime` dependency/notice files were moved under this review package;
`replay_path` maps them to their historical names inside the temporary execution
directory. These are byte-preserving layout changes; executed scripts and their
inputs are unchanged. [PUBLICATION-INPUTS.json](evidence/PUBLICATION-INPUTS.json)
records the mapping. The fresh execution hash and current publication manifest
hash are kept separately in the validation receipt.

Scoped root attributes disable text conversion only for the eight newly
introduced research prefixes. Without them Git would normalize CRLF in inherited
proof notes and invalidate their source hashes. Existing frozen packages and
unrelated source paths retain their prior attributes.

## Public context and attribution checks

The cached overlap search was run for `independent-moment`: its remote data was
from October 18 and was explicitly labelled stale. A live search of recent
conditional claims, relevant PR bodies, active Discussions and the board's
start-here post supplemented it. This is a scoped overlap check, not a novelty
certificate. Relevant live heads and authors are retained in
[PUBLIC-PREDECESSORS.json](evidence/PUBLIC-PREDECESSORS.json).

The draft uses @rohanarun's #4181 as its comparison point, giving approximately
32.8727% more exponent saving. This is the leading conditional κ claim located
in the checked public records. The chronologically newer #4270 claims the lower
κ = 1/580; #4326 improves a BIT supplier's c rather than claiming a higher κ.
The validation receipt already contains the exact comparison against #4181.
#4268's DFT figure is not an integer-multiplication κ.
Discussion #4337 is checking that PR's literal half-cut binding; this proposal
uses its own complete p3 words and adds a different finite compiler/outer argument.
The [PR submitter audit](evidence/PR-ATTRIBUTION-AUDIT.json) checks all 14
repository PRs linked in the newly authored narrative and bibliography against
GitHub's `author.login`. In particular, #4085 was submitted by @zxv, #1758 by
@jeremykothe2 and #1786 by @chafreaky. The draft uses verified handles for PR
submission credits and preserves source-authorship notices separately.
The initial draft incorrectly substituted Douglas Colkitt for @zxv and assigned
preparation of the submission to Douglas Colkitt without a verified basis.
Those unsupported attributions have been removed from the review narrative.

## Unrun obligations and limits

- Universal finite compilation, native tensor lift, common-weight cover,
  semantic precision and support-local transfer are written mathematical
  arguments supported by finite checks. They require external review.
- The inherited analytic decomposition, exact integer recovery, native ordered
  movement, fixed-tape model and prime-padding inputs remain conditional.
- Winning astronomical uniform words, covers and constants were not materialized.
  No practical cutoff or runtime advantage was measured.
- The exact private base ZIP is absent from Downloads. Its full application and
  idempotence receipt is preserved as supplied evidence, not independently rerun.
- No Lean, Docker, hosted CI, selected-frontier cold replay or complete replay
  of every auxiliary H/negative-search menu was run. Their retained receipts
  retain their original author-checked status.
- The historical reported 332-entry recovery gap is not resolved by fresh
  reconstruction. Missing originals are not claimed to have been recovered.

## Open next questions

The [PR description](PR-BODY.md#open-next-questions) gives feasible starting points and
blockers for independent review, smaller templates, geometry-aware boundary
decoding and an improved binding complex tariff.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
