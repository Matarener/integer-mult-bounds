# Linear record admission for the physical child-program producer

This package derives the actual `SelectedBinding.child_program` record invoice
and supplies a package-local forward-only admission adapter. The unchanged
producer repeatedly scans earlier Program and raw-field records. The adapter
uses the existing encoded chronological loop to visit each record once, preserves
its arithmetic predicates, then restores the original random-access Program.
Frozen/shared sources and the selected frontier are unchanged.

For history h, index/residue widths I/L, source-code width Q, define
`n=h+1`, `r=2I+L+5`, `c=Q+2I+90`, `F=Q+2+4096(L+1)`, and `P=r+h*c`.
The complete adapted producer's record scans, including original-history copying
into the returned program, cost:

| Tape | Reads | Writes | Unit moves |
|---|---:|---:|---:|
| Parent Program | `5P+2hI+1` | 0 | `4P+8` |
| Fields | `n(3F-Q-2)+3` | 0 | `2nF+4` |
| Returned Program, `D=r+(h+1)c` | `2D+1` | D | `2D+2` |
| Empty continuation tapes | 2 | 0 | 4 |

The original Fields scans alone cost
`(3F-1)n(n+1)/2+n(2Q+4)+3` reads and
`F*n(n+1)+n(2Q+6)+4` moves. The full original Program invoice, numeric work
bound, root/history coupling and semantic induction are in [PROOF.md](PROOF.md).
This is a linear **record scan** improvement; binary arithmetic retains its
separate polynomial cost. No wall-clock measurement is substituted for tape work.

Both versions use exactly `P+D+nF+14` visited record cells, including LEFT,
adjacent blanks, returned output and four empty continuation tapes. The adapter
adds no numerical word or tape. A conservative numerical component bound and
64 additional words per bank are stated with source-loop derivations; backing,
slot metadata and fixed vocabulary control remain explicitly separate.

## Evidence and limits

`check.py` authenticates and executes the unchanged word/record/controller/child
implementations and the exact extracted `SelectedBinding.child_program` method.
Only the candidate adapter changes admission's monotone record access.
Six normal/adapted producer pairs exercise good, pair, unit and half children at
history depths 0,1,2,3,4,6, varying word/code widths. Three leaf-only pairs check
that leaf admission consumes h fields, while internal admission consumes h+1.
The variable-history pairs check exact source-derived record counts, identical output bytes or
leaf state, chronological decoded-word traces, unchanged residue counts, decreased
index work, preserved borrowed bytes/heads, ownership cleanup and visited spans.
Seven malformed-admission controls compare rejection and cleanup. A changed-admission-AST control fails closed. Exact source,
AST and receipt corruption controls remain active under optimized Python.

The six variable-history cases use synthetic admitted rank-seven source
projections. An additional source-shaped pair uses the exact 6,507-bit GL codes
and low hashes supplied by the same-session residual lane for current rank26
IDLE27776 and rank7 COPY1603 (PR3967 source identity). Canonical LowCodes decoding
checks both request/view tags and full low hashes, then the actual producer
builds 2048→832→91 at modulus9 with nonzero high fields. SOURCE_PROJECTION.json
retains the peer-derived metadata and provenance. This package does **not**
independently reconstruct those source plans or establish their good-class status;
that is an explicit fixture premise, not a hidden new admission certificate. They execute the actual generic producer and Callback acceptance,
not a generated R437 GL64 catalogue or payload. The uniform theorem is about
that source method under admitted specifications; it does not independently prove
matrix/low-class admission, high-digit validity, or the full selected source.
The adapter is opt-in research code, not installed into the shared physical caller.

Reproduce the bounded registered suite:

```sh
python3 -B scripts/research_package.py --package research/r437-source-preparation-bound
```

The direct verifier also works in a Git-free export with its declared inputs.
`RESULT.json` is an exact deterministic receipt, not a timing-derived bound.
`VALIDATION.json` and `REPLAY.log` record the frozen local replay. Hosted CI is
reported separately after publication. No full GL64 payload, historical cold
suite, Lean, Docker, new κ, independent human review or formal proof is claimed.

## Scope and coordination

Explicit donor assignment refines `selected-stock-envelope`: close a substantive
actual preparation component from [PR3983](https://github.com/CrocSwap/integer-mult-bounds/pull/3983).
This pairs amortized sequential-tape accounting with grammar/automata cursor
invariants. It extends PR3983's serialization-only experiment by executing
Callback admission and supplies a concrete removal of repeated producer work.
The remaining Pi components are stated in the proof and TASK.json.

Base canonical main is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision6.
Canonical team claim: https://github.com/CrocSwap/integer-mult-bounds/pull/3967#issuecomment-6263066320.
The local overlap helper had no remote cache; live PR search was additionally
checked. Adjacent PR3999 addresses interruption/abort recovery, and PR3995 pools
finite IR; this package optimizes normal unpooled source-program admission.
Neither result is treated as a prerequisite or a stock/cost theorem.

## Open next questions

See TASK.json for structured questions. Integrate the cursor at an actual complete
caller only after comparing its successful admission relation and physical
implementation tariff. Price the remaining child_extents/read_prefix/directory
producer, geometry/context and coefficient evaluation contributions. Combine
those charges with full lifetime role maxima and original-width stock before
claiming a complete reserve or caller recurrence. The history inequality alone
is not stock admission.

## Credit

Jose Manuel/jmbarrancoml: physical caller, SelectedBinding, encoded primitives.
David Arias/PR2753 and the retained Nick Petalas/controller/record/continuation
lineage: source grammar and callback. PR3983: checkpoint/serialization invoice
and explicit Pi gap. R437/OQ4 context retains ai-nanachi/3647, zxv/3690,
Ali Romman/1043, Sagar Thakrar/3700, the selected/native authors and
PR3936/3950/3967 attribution. New adapter, analysis and packaging by
Chris R/Clear1nsight with substantial OpenAI Codex assistance and same-session
AI review. Apache-2.0; predecessor results are not claimed as new.
