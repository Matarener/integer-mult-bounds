# Selected-census certificate contract

Scope: the bridge between the public Python sources pinned by `../SOURCES.json`
and the Lean data module `CompilerAudit/SelectedData.lean`. All paths below are
relative to this `lean/` directory; `ROOT` is the repository or source-export root,
derived from `__file__`. Nothing depends on a private workspace or old census.

## Artifacts

| File | Role |
| --- | --- |
| `extract_census.py` | stdlib exporter/checker (this contract's subject) |
| `SelectedCensus.json` | compact certificate (generated from a successful explicit `--emit`) |
| `CompilerAudit/SelectedData.lean` | generated Lean DATA definitions, no proofs |

## Commands

```
python -I -B lean/extract_census.py [--check] [--json P] [--lean P]
python -I -B lean/extract_census.py --emit --json OUT.json --lean OUT.lean
```

* `--check` (default): recompute the census from source and require the
  committed certificate and Lean file to equal the freshly rendered bytes
  exactly. It never writes anything except an empty temporary pycache dir.
  `--json/--lean` may point check mode at other copies (e.g. fresh emits).
* `--emit`: both destinations must be explicit absolute paths, absent, outside
  `ROOT`, in existing directories, and outside every ancestor marked by
  `LOCAL-MANIFEST.json`, `EXPORT-MANIFEST.json` or `.git`. Files are opened with exclusive create (`xb`). Destinations are
  validated before the source run; all checks and the JSON->Lean regeneration
  round trip complete before the first byte is written. The maintainer then copies
  them to `SelectedCensus.json` and `CompilerAudit/SelectedData.lean`.
  (If the second exclusive create fails, the first file remains; delete it.)

## What the Python side checks

1. Fresh bytecode namespace (`dont_write_bytecode`, empty `pycache_prefix`).
2. `verify.export_integrity` and `verify.authenticate`: the 121 live inputs
   match SHA256 and Git blob pins in `SOURCES.json` and the `VERIFY.json`
   inventory, before and after extraction. SHA256s of `SOURCES.json`,
   `VERIFY.json`, `EXPECTED.json`, `source_audit.py`, `verify.py` are recorded
   (these package files are not themselves live pins) and must be stable.
3. Unmodified `source_audit.activate` (original loader activation and
   compatibility controls) and `source_audit.selected_census` -- metadata
   only; no full selected LOW enumeration, tiny trace or factory call.
4. Every repository module loaded is a live pin or a package file.
5. The returned census summary equals `EXPECTED.json` `source.census` field for
   field (sizes, kinds, SHA list, metadata-event and check counts, ...), and
   sizes equal `selected_coefficients_at_N_one.group_sizes`.
6. rho = 32, R = 28278, exactly 19 groups; per group `common == lowMajor ==
   (kind == local_cover_sweep)`.
7. Interval derivation only if each `request_ids` list equals
   `range(start, start+count)` with integer IDs; empty group gets canonical
   `start = R` (one such group, the final idle group). Each group SHA256 of the
   compact `json.dumps(ids)` must equal both the census SHA and the SHA of the
   regenerated range.
8. Non-empty intervals partition `range(R)` with no gap/overlap; counts sum to R.

Certificate fields: `schema`, `base_commit`, `live_pins`, `package_sha256`,
`replica_count`, `request_count`, `kinds`, `empty_groups`,
`empty_canonical_start`, `schedule_order_contiguous`, `groups[]`
(`index, schedule_index, kind, order, common, low_major, start, count,
sequence_sha256`). Lean module `CompilerAudit.SelectedData` defines
`replicaCount`, `requestCount`, `intervals : List (Nat Ã— Nat Ã— Bool Ã— Bool)`
with tuple `(start, count, common, lowMajor)`, `scheduleIndices`, `kinds`,
`sequenceSha256`. It imports nothing and contains no theorem or axiom.

## What this is NOT

* Not a verified Python parser or semantics: correctness of extraction rests on
  CPython executing the pinned sources and on this script; no formalization of
  Python is claimed.
* Hash equality (pins, SHA lists, byte comparison) shows the data came from
  the pinned sources under this run; it is not a semantic refinement theorem
  linking the Lean model to the Python compiler.
* The generated Lean module contains data only. `Selected.lean` defines the
  model's groups from those data and proves their partition/count properties.
  That definitional connection is kernel-checked; the external Python-to-data
  extraction is not a formal semantic-refinement theorem.
* Source premises remain outside Lean: LOW labels must correspond bijectively
  to the model indices below `N`; emitting positions and their request IDs must
  be independent of the LOW value; replica ID sequences must agree. GL64 LOW
  cardinality and the full
  selected numerical/native/runtime behavior are not checked here (the census
  is metadata only, N stays symbolic).