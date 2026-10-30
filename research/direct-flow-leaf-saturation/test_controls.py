#!/usr/bin/env python3
"""Mutation controls for the certificate boundary. DLamdata/Codex, Apache-2.0."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('certificate', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def require_rejection(argv, cwd, needle):
    run = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=60)
    if run.returncode == 0 or needle not in run.stderr:
        raise ValueError(f'control did not reject with {needle!r}: {run.returncode}, {run.stderr[-400:]}')


def repin(package, root, relative):
    manifest = json.loads((package / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['path'] == relative:
            row['sha256'] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    (package / 'SOURCES.json').write_text(json.dumps(manifest))


with tempfile.TemporaryDirectory(prefix='leaf-saturation-controls-') as directory:
    root = Path(directory)
    package = root / 'research/direct-flow-leaf-saturation'
    package.mkdir(parents=True)
    for name in ('verify.py', 'independent_source.py', 'SOURCES.json', 'RESULT.json'):
        shutil.copy2(HERE / name, package / name)
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            target = root / row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / row['path'], target)
    # Both standalone entry points must bind bytes before executing inputs.
    for relative in ('research/direct-flow-leaf-walk/verify.py', 'research/direct-mixed-flow/flow.py'):
        source = root / relative
        original = source.read_bytes()
        source.write_bytes(original + b'\n# corrupt-source control\n')
        for script in ('verify.py', 'independent_source.py'):
            for mode in ([], ['-O']):
                require_rejection([sys.executable, *mode, '-B', str(package / script)], root, 'source mismatch: ' + relative)
        source.write_bytes(original)

    # Exercise the actual source-histogram assertions. Re-pin mutant bytes so
    # a checksum failure cannot masquerade as a semantic rejection.
    relative = 'research/direct-flow-leaf-walk/diagnostics/overlap_flow.py'
    source = root / relative
    original = source.read_text()
    branch = '                    if d == G:\n                        add(X, rank, issued); continue'
    if original.count(branch) != 1:
        raise ValueError('source mutation anchor drift')
    mutations = {
        'empty_leaf': '                    if d == G:\n                        continue',
        'truncated_terminal': '                    if d == G:\n                        if m * rank <= N: add(X, rank, issued)\n                        continue',
    }
    probe = "import runpy,sys; v=runpy.run_path(sys.argv[1]); v['finite_law'](*v['bindings']())"
    for replacement in mutations.values():
        source.write_text(original.replace(branch, replacement))
        repin(package, root, relative)
        for mode in ([], ['-O']):
            require_rejection([sys.executable, *mode, '-B', '-c', probe, str(package / 'verify.py')], root, 'ordered words disagree with actual leaf exits')
            require_rejection([sys.executable, *mode, '-B', str(package / 'independent_source.py')], root, 'leaf histogram')
    source.write_text(original)
    shutil.copy2(HERE / 'SOURCES.json', package / 'SOURCES.json')

    # Corrupt only the original Flow class's returned boundary histogram, after
    # its own conservation checks. This reaches the independent comparison
    # instead of failing an earlier producer invariant or byte-authentication.
    relative = 'research/direct-mixed-flow/flow.py'
    source = root / relative
    original = source.read_text()
    field = "'boundary_exits': boundary,"
    if original.count(field) != 1:
        raise ValueError('original Flow mutation anchor drift')
    source.write_text(original.replace(field, "'boundary_exits': boundary + Counter({1: 1}),"))
    repin(package, root, relative)
    for mode in ([], ['-O']):
        require_rejection([sys.executable, *mode, '-B', str(package / 'independent_source.py')],
                          root, "(121, 'original Flow class')")
    source.write_text(original)
    shutil.copy2(HERE / 'SOURCES.json', package / 'SOURCES.json')

    expected = json.loads((package / 'RESULT.json').read_text())
    expected['parameters']['lambda'][0] = '0.0'
    receipt = package / 'corrupt-result.json'
    receipt.write_text(json.dumps(expected))
    require_rejection([sys.executable, '-O', '-B', str(package / 'verify.py'), '--expect', str(receipt)], root, 'expected receipt mismatch')

# These are regressions for this narrow pinned root bracket, not general
# coverage of enclosure arithmetic; test_enclosures.py checks that separately.
for name in ('paid', 'target'):
    P, W, M = v.bindings()
    histogram = P if name == 'paid' else W
    histogram[min(histogram)] += 1
    try:
        v.parameters(P, W, M)
    except ValueError as error:
        if 'invoice root bracket' not in str(error):
            raise
    else:
        raise ValueError('changed histogram passed fixed root certificate: ' + name)
print('PASS_MUTATION_CONTROLS both_standalone_pins_normal_and_optimized repinned_empty_and_truncated_leaf_sources_normal_and_optimized repinned_original_flow_return_normal_and_optimized corrupted_receipt fixed_bracket_count_regressions')
