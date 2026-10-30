# Parent-only actual-key freeze and single guarded attempt

This directory is source preparation only. No compiler, scientific import, captured corpus or replay was executed by its author. Independent source review and the parent's resource/ledger decision precede any execution. The earlier synthetic pilot remains closed.

From `/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453`, the parent can freeze this distinct source-only stage with file operations:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, shutil
base=Path('outputs/c-verification-all-opportunities-20261027')
source=base/'actual-key-pilot'
stage=base/'stages/actual-key-pilot-v1'
manifest=json.loads((source/'FROZEN-SOURCE.json').read_text())
for name,digest in manifest['files_sha256'].items():
    assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
for name,digest in manifest['reference_files_sha256'].items():
    assert hashlib.sha256((base/name).read_bytes()).hexdigest()==digest,name
assert not any(p.is_symlink() for p in source.rglob('*'))
shutil.copytree(source,stage)  # Must be new; preserves all 164 baseline file modes.
print('Frozen stage:',stage.resolve())
PY
```

Then, only if admitted by the parent, one execution:

```bash
/usr/bin/python3.12 outputs/c-verification-all-opportunities-20261027/run_guarded.py actual-key-pilot-v1 stages/actual-key-pilot-v1/stage_entry.py
```

No `--initial`, `--optimized`, alternate corpus, warmup or retry. The existing guard serializes execution, fixes PYTHONHASHSEED=0, retains the outer `/usr/bin/time` bill including compiler children, enforces 180 seconds / sampled 1-GiB process-group RSS, and charges the shared 1500-second ledger. It freezes every stage file plus the unchanged baseline/input closure. The wrapper writes only to a fresh `runtime/actual-key-pilot-v1-artifacts/` directory. A cap failure is a retained final failure of this nomination; no keys are sampled or deduplicated and the caps are not raised.

Retain the entire artifact directory and `runtime/runs/actual-key-pilot-v1/receipt.json`. Artifacts include original full-qualifier stdout, a capture receipt, native/key build receipts, finite controls, the complete `actual-keys-v1.pickle.gz` corpus, the oracle and all four full ID/flag/prefix outputs, and the final result or failure traceback. Successful corpus readback compares every value/order in bounded blocks. Performance replay uses the original live captured objects, not deserialized replacements; the persisted archive does not promise cross-block object identity. This report's file format is versioned explicitly: gzip with mtime 0, compression level 1, pickle protocol 5, one header, then outer tuple blocks of up to 4096 keys with pickler/unpickler memo cleared at block boundaries. All arbitrary-width signed exact integers remain values in each seven-field key.

The parent outer receipt is the authoritative cold cost. Capture and complete qualification are diagnostic and cannot be treated as a new baseline timing. The unchanged key-only comparator excludes descriptors/Fraction arithmetic/callbacks from both inner arms. A positive conditional budget still leaves actual complete integration, retained integer costs and all new bills unpriced; a negative budget stops this nomination.
