"""Fresh bounded native/dense/source/fallback controls; no full timing claim."""
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
import tempfile

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / 'CODE-SOURCES.json').read_text())
for name, expected in manifest.items():
    path = HERE / name
    if path.is_symlink() or sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('exact native verifier source: ' + name)
with tempfile.TemporaryDirectory(prefix='gf2-side-finite-') as temporary:
    sys.argv = [str(HERE / 'compare_side_verifier.py'), '--mode', 'finite',
                '--output', str(Path(temporary) / 'evidence')]
    runpy.run_path(sys.argv[0], run_name='__main__')
print('PASS_GF2_SIDE_NATIVE_FINITE_SOURCE_CONTROLS')
