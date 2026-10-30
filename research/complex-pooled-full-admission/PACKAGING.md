# Lossless receipt storage and pinned input reuse

This packaging change does not alter a mathematical proof, interval engine,
primitive tariff, rejection predicate or retained premise. The optional B2
ordinary-bootstrap calculation is a separate draft contribution. The main
`kappa=1/580` composition continues to use B1.

## Receipt bytes and history

`evidence/PREFIX-AND-INVOICE.json.gz`, `evidence/SPEC.json.gz` and
`evidence/MIXED-CONTRACT.json.gz` contain the complete original JSON bytes.
No field, coefficient, owner entry or rejection case is dropped.
[PACKAGING.json](PACKAGING.json) commits both the stored container and the
decompressed byte count and SHA256. The decompressed hashes must equal the
original commitments in the unchanged [EVIDENCE.json](EVIDENCE.json).
Regenerated scientific products still compare by their complete JSON values,
rather than requiring a particular gzip encoding.

For example, this reads every original invoice entry:

```sh
python3.12 -c 'import gzip,json; print(json.loads(gzip.decompress(open("research/complex-pooled-full-admission/evidence/PREFIX-AND-INVOICE.json.gz","rb").read())))'
```

`EVIDENCE.json` records the historical complete finite release. It does not
claim that the new packaging code executed that historical run. Its original
`INPUT-PINS.json` bytes are retained in `frozen/RECORDED-INPUT-PINS.json.gz`;
the other four recorded execution sources remain byte-for-byte unchanged.
The verifier authenticates all five historical source commitments, all fourteen
receipt commitments and the complete recorded release chain.

## Reused canonical inputs

Two redundant local copies have been replaced by their identical pinned files
at canonical base `12fa8c5c844be21bfefb38a19503fbd867a11244`:

| Former package address | Declared repository input |
| --- | --- |
| `frozen/selected/ASSEMBLY.json` | `research/community-frontier1094-audit/ASSEMBLY.json` |
| `frozen/selected/BIT-EXPECTED.json` | `research/e8-bit-p111-tuned/tune/EXPECTED.json` |

The current `INPUT-PINS.json` must equal the historical document with exactly
these two path/kind substitutions. Their SHA256 commitments stay unchanged.
Both are explicit `VERIFY.json` inputs with canonical `SOURCES.json` bindings,
so a Git-free export includes them without network or predecessor Git objects.

`joint_bound.py` remains the exact recorded interval engine. Its direct readers
retain the historical addresses. Use `joint_bound_inputs.py` to run its complete
CLI with the two canonical addresses: the adapter compiles the authenticated
engine bytes, changes only those two reader addresses, and retains every
arithmetic function and predicate. All other paths, including `--release-work`,
use the original readers. The physical/global and successor admission checks
continue to compile the unchanged engine for its pure interval arithmetic.

## Checks and scope

The normal and optimized registered regressions authenticate containers and
original payloads, compare the complete current and historical input sets,
recompute all original operator/arithmetic controls, and reject missing or
changed containers, payload commitments and symlinked inputs. Local/global
physical, outer and successor admission checks retain their existing domains.
All registered commands also run from an isolated committed export without Git.

These fresh bounded checks are distinct from the preserved historical complete
release. The packaging change supplies no new production multiplication run,
formal-kernel proof, premise admission or selected-frontier update.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
Apache-2.0; retained source notices continue to apply.
