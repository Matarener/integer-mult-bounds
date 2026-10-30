# Parent-only single-run reproduction

Author performed source/text/AST/hash operations only. The C extension has NOT been compiled or imported and no control/corpus/timing has executed. Review and freeze first. This command is not authorization to repeat or refreeze after a failed run.

From the project directory `/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453`, the parent may create the new immutable stage using only file operations:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, shutil
base = Path('outputs/c-verification-all-opportunities-20261027')
source = base / 'cache-key-pilot'
stage = base / 'stages/cache-key-pilot-v1'
manifest = json.loads((source / 'FROZEN-SOURCE.json').read_text())
for name, digest in manifest['files_sha256'].items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest, name
for name, digest in manifest['reference_files_sha256'].items():
    assert hashlib.sha256((base / name).read_bytes()).hexdigest() == digest, name
stage.mkdir()
for name in [*manifest['files_sha256'], 'FROZEN-SOURCE.json']:
    shutil.copy2(source / name, stage / name)
print('Frozen stage:', stage.resolve())
PY
```

After independent clearance and the parent's ledger check, run exactly once through the existing serial guard:

```bash
/usr/bin/python3.12 outputs/c-verification-all-opportunities-20261027/run_guarded.py cache-key-pilot-v1 stages/cache-key-pilot-v1/stage_entry.py
```

Do not use `--initial`: the initial 600-second phase is closed. Do not add `--optimized`. The guard already fixes PYTHONHASHSEED=0, applies the 180-second wall / 1-GiB sampled process-group RSS limits, serializes execution, includes compiler children in its outer `/usr/bin/time` bill, and charges the 1500-second aggregate. It admits only scripts inside a newly frozen stage. The wrapper requires that exact stage name and writes only to a fresh `runtime/cache-key-pilot-v1-artifacts` directory. All four B,C,C,B samples use fresh state, and the extension is compiled in a fresh build directory. No warmup or answer/build reuse occurs.

Retain both `runtime/runs/cache-key-pilot-v1/receipt.json` and the whole `runtime/cache-key-pilot-v1-artifacts/` tree, including failed outputs/build diagnostics if any. The outer guard receipt, rather than the child's partial cold clock, determines the charged bill. An unsuccessful run stops this proposal; zero automatic retries.

Artifacts include `BUILD.json` and compiler logs in `build/`, `FINITE-CONTROLS.json`, oracle and all four full ordered `*-ids.u64` / `*-flags.u8` / `*-prefixes.json` files, and `RESULT.json`. The ID files use the recorded host byte order and exactly 8 bytes per ID; the flag byte is 0 for hit, 1 for miss, 3 for miss plus eviction. Prefix rows are calls/hits/misses/evictions/resident. The driver compares every ID, flag and prefix to the separate literal Python dict/deque oracle before any nomination screen.

Only the frozen synthetic key-only problem is tested. Passing its optimistic arithmetic does not satisfy complete PR5864 >=15% wall/CPU, the noise spread gate, full Fraction/API compatibility, the source-specific actual-trace cost, or the full new bill. No price from this pilot may be called an actual complete saving.
