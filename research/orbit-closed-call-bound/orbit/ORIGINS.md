# Preserved sources and execution adaptations

`INPUTS.json` is the exact source inventory. The three original C09 files in
`frozen/history/` are copied without changes from the external
`kappa-major-20261018T1330Z/paired-bit` research run. The scientific root file,
its notice and license are copied without changes from commit
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, paths under
`research/e8-bit-carrier-skeleton/`. Both compressed transport and decompressed
root-data hashes and byte counts are recorded. The root transport Git blob is
`8bec1751f7e33c3a1e4673ef5dbc34d6f205321e`.

The root file's Apache-2.0 license, contributor notices and AI disclosure remain
in `frozen/source/`. The inherited E8 Hamming-chart lineage includes Dylan Crow /
utcorvusvolat-dotcom's PR370 material through eumemic's carrier-skeleton package;
the original notice is the authoritative detailed attribution. Only the JSON
`lines` field is consumed by this contribution. Retention of the whole compressed
source is provenance, not fresh validation of its R865 circuit.

`check.py` is the new adapter and formal-algebra checker. It authenticates all
captured input bytes before executing the historical source. It does not import
historical modules from ambient paths, consult Git, or load historical bytecode.
The historical source is compiled from the authenticated, adapted string with
`dont_inherit=True, optimize=0`. The immutable file itself is never rewritten.
The only adaptations are these:

1. Replace the absolute `SOURCE` declaration with a comment and replace both
   `SOURCE.read_bytes()` calls with already-authenticated `ROOT_BYTES`.
2. Remove the historical command-line parser for `--write`.
3. Replace the historical local receipt I/O and terminal print tail by
   `return out`.

Each replacement has an exact occurrence-count guard. The returned historical
record is compared to **all** fields of the frozen original receipt, recursively
including JSON types. The adapted string's hash appears in the fresh receipt
alongside the original source hash. Original source proof statements, historical
scope, notices, and original control fields are retained unchanged. New scope
and defect-sensitive checks are explicit separate additions.

The extension is a sharp formal-query result and a returned-scalar-spectator
generalization. The root census, first-variation argument and cover motivation
originate in the preserved C09 files. Earlier rank/specialization techniques are
not claimed as new; related-work attribution to the existing group-algebra
literature and repository contributions belongs to the parent package's source
audit. Ross Richardson with substantial OpenAI Codex assistance prepared the
new proof, checker, finite constructions and mathematical review.

For a standalone read-only export, run

```
python3.12 -B check.py --output /absolute/external/new-receipt.json.gz
```

The output must be absolute, external to this component, not a symlink and not
already present. It is created exclusively. `.gz` selects deterministic gzip
transport; other suffixes give UTF-8 JSON. Normal and `-O` Python3.12 executions
have been compared byte-for-byte, including the complete fresh receipt.
`PACKAGE-FILES.json` is the minimal handoff list. Scratch outputs and duplicate
normal/optimized receipts are excluded. `OUTPUT-INVENTORY.json` records the final
code, proof, input inventory, compressed receipt and raw receipt hashes.
