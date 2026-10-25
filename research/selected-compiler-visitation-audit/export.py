#!/usr/bin/env python3
"""Export only this audit and its exact source inputs, without Git/network access."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE_FILES = ('README.md', 'PROOF.md', 'VALIDATION.md', 'TASK.json', 'SOURCES.json',
                 'VERIFY.json', 'EXPECTED.json', 'verify.py', 'export.py',
                 'source_audit.py', 'accounting.py', 'test_accounting.py')
PACKAGE_FILES += ('lean/.gitignore', 'lean/README.md', 'lean/CERTIFICATE-CONTRACT.md', 'lean/SelectedCensus.json', 'lean/extract_census.py', 'lean/check.py', 'lean/lean-toolchain', 'lean/lakefile.toml', 'lean/lake-manifest.json', 'lean/CompilerAudit.lean', 'lean/CompilerAudit/Visit.lean', 'lean/CompilerAudit/Retention.lean', 'lean/CompilerAudit/Composition.lean', 'lean/CompilerAudit/Selected.lean', 'lean/CompilerAudit/SelectedData.lean', 'lean/CompilerAudit/Result.lean')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--destination', required=True, type=Path)
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    # Execute the authenticated checkout's verifier source directly, not a .pyc.
    spec = importlib.util.spec_from_loader('audit_export_checks', loader=None)
    checks = importlib.util.module_from_spec(spec)
    checks.__file__ = str(HERE/'verify.py')
    exec(compile((HERE/'verify.py').read_bytes(), str(HERE/'verify.py'), 'exec'), checks.__dict__)
    sources, replay = checks.read_json(HERE/'SOURCES.json'), checks.read_json(HERE/'VERIFY.json')
    live = checks.authenticate(ROOT, sources, replay)
    checks.export_integrity(ROOT)
    destination = args.destination.expanduser().resolve()
    checks.need(args.destination.is_absolute() and not destination.exists(), 'fresh absolute destination required')
    checks.need(not destination.is_relative_to(ROOT), 'export outside source tree')
    checks.need(not any((p/'LOCAL-MANIFEST.json').exists() for p in destination.parents), 'frozen destination prohibited')
    prefix = HERE.relative_to(ROOT).as_posix()
    names = sorted(live | {prefix+'/'+name for name in PACKAGE_FILES})
    data = {name: checks.regular(ROOT, name).read_bytes() for name in names}
    destination.mkdir(parents=True, exist_ok=False)
    for name, content in data.items():
        path = destination/name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(content)
    manifest = dict(schema='compiler-visitation-export-v1', base_commit=sources['base_commit'],
                    files={name: sha256(content).hexdigest() for name, content in data.items()})
    with (destination/'EXPORT-MANIFEST.json').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    checks.export_integrity(destination)
    print(json.dumps(dict(files=len(data), source_bytes=sum(map(len, data.values())),
                         destination=str(destination), network_used=False, git_used=False), indent=2))


if __name__ == '__main__':
    main()
