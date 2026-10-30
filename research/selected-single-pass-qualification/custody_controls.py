"""Reject actual proof-relevant source/export corruption before any import."""
from contextlib import contextmanager
import json
from pathlib import Path
import tarfile
import tempfile

import source
from orchestration import require


def run():
    here = source.HERE
    raw = (here / 'inputs/PR5757.tar').read_bytes()
    manifest = (here / 'INPUT-MANIFEST.json').read_bytes()
    paths = {
        'engine': 'research/exact-clifford-quadratic-replay/quadratic.py',
        'word': 'research/p104-helper-subspace-splits/WORD.json.gz',
        'compiler': 'research/p104-native-channel/vendor/clifford_exact.py',
        'cross_entry': 'research/selected-quadratic-replay/cross.py',
        'verify_entry': 'research/selected-quadratic-replay/verify.py',
        'expected_cross': 'research/selected-quadratic-replay/CROSS.json',
    }
    with tarfile.open(here / 'inputs/PR5757.tar', 'r:') as archive:
        offsets = {name: archive.getmember(path).offset_data for name, path in paths.items()}
    result = {}
    for name in [*paths, 'manifest']:
        with tempfile.TemporaryDirectory(prefix='single-pass-corruption-') as temporary:
            root = Path(temporary)
            (root / 'inputs').mkdir()
            changed = bytearray(raw)
            if name != 'manifest':
                changed[offsets[name]] ^= 1
            (root / 'inputs/PR5757.tar').write_bytes(changed)
            (root / 'INPUT-MANIFEST.json').write_bytes(manifest + (b'\n' if name == 'manifest' else b''))
            try:
                source.HERE = root
                try:
                    source.payload()
                except ValueError as error:
                    expected = 'Complete manifest hash' if name == 'manifest' else 'Official export hash'
                    require(str(error) == expected, 'Exact source corruption predicate')
                    result[name] = {'predicate': expected, 'scientific_import_started': False}
                else:
                    raise ValueError('Source corruption accepted: ' + name)
            finally:
                source.HERE = here
    require(len(result) == 7, 'All source custody controls')
    return result


if __name__ == '__main__':
    print('PASS_SINGLE_PASS_SOURCE_CONTROLS', json.dumps(run(), sort_keys=True))
