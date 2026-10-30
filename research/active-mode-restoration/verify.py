#!/usr/bin/env python3
"""Read-only source-bound replay of a scoped active-restoration gate.

Python standard library only. No native source program is imported. Temporary
replay artifacts are compared semantically, not by their gzip containers.
"""
from contextlib import redirect_stdout
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import gzip
import io
import json
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[1]/'research/filtered-native-kappa004/inputs/original-packet.tar.gz'
ARCHIVE_SHA = '595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7'
PREFIX = 'filtered_native_implementation/'
MEMBERS = {
    'word': ('research/retained_state_next/F9-SOURCE-DAG-ALL8-WORD.json.gz',
             '934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775'),
    'original': ('research/native_contact/SCALED-GLOBAL-CANCEL-WORD.json.gz',
                 'de4b75c106f8a3ebe1ee68b53fe7e64bd218120526e726d9bdfd4dab711dd4b2'),
    'R': ('upstream/research/involutory-producer-raw-dual/inputs/R/R.json',
          '7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1'),
    'center': ('research/retained_state_next/CENTER5-SUFFIX.json',
               '5f2439d2f724f9f6fc6766bd74cd0885e923a0f8f3736d1eff6873c68d99279a'),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def load_local(name):
    """Read committed Python source directly, ignoring all bytecode caches."""
    path = HERE/(name+'.py')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def independent_witness_check(record, observations, mode_values):
    """Direct pairings only: does not import or reuse search/elimination."""
    def decode(entries):
        indices = [int(i) for i, _ in entries]
        require(len(indices) == len(set(indices)), 'Unique sparse witness coordinates')
        require(all(0 <= i < 632 for i in indices), 'Original input coordinates')
        return {int(i): Q(v) for i, v in entries}

    def dot(a, b):
        return sum((v*b.get(i, Q(0)) for i, v in a.items()), Q(0))

    mode = {112+i: Q(v) for i, v in enumerate(mode_values) if Q(v)}
    negative = record['negative_certificate']
    z = decode(negative['Mz_equals_v'])
    u = decode(negative['Mu_equals0_mode5_u_equals1'])
    a = decode(negative['changed_observation_annihilator'])
    require(len(observations) == 4868, 'Observation inventory')
    require(dot(mode, u) == dot(mode, a) == 1 and a[240] == -1,
            'Both original targets separated')
    for item in observations:
        row, v = decode(item['row']), Q(item['v'])
        require(dot(row, z) == v, 'Direct Mz=v witness')
        require(dot(row, u) == 0, 'Direct Mu=0 witness')
        require(dot(row, a)+v*dot(mode, a) == 0, 'Direct changed-space annihilator')
    bad = dict(a)
    bad.pop(240)
    require(any(dot(decode(o['row']), bad)+Q(o['v'])*dot(mode, bad)
                for o in observations), 'Dropped helper coordinate must reject')
    return {'rows': len(observations), 'mode_pairing': str(dot(mode, a)),
            'original_helper240_pairing': str(a[240])}


def main():
    raw = ARCHIVE.read_bytes()
    require(sha256(raw).hexdigest() == ARCHIVE_SHA, 'Exact original source archive')
    with TemporaryDirectory(prefix='active-mode-restoration-') as directory:
        temporary = Path(directory)
        paths = {}
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
            inventory = archive.getmembers()
            for key, (name, digest) in MEMBERS.items():
                matches = [m for m in inventory if m.name == PREFIX+name]
                require(len(matches) == 1 and matches[0].isfile(), 'Unique regular retained member')
                data = archive.extractfile(matches[0]).read()
                require(sha256(data).hexdigest() == digest, 'Exact retained member: '+name)
                # No archive-controlled filesystem paths are extracted.
                paths[key] = temporary/(key+'.input')
                paths[key].write_bytes(data)
        gate = load_local('l240_extra_column_gate')
        gate.HERE, gate.SOURCE, gate.ORIGINAL, gate.RP = (
            temporary, paths['word'], paths['original'], paths['R'])
        with redirect_stdout(io.StringIO()):
            gate.main()
        sink = load_local('full_sink_gate')
        sink.HERE = temporary
        with redirect_stdout(io.StringIO()):
            sink.main()
        repair = load_local('direct_l240_repair')
        repair.HERE, repair.WP, repair.CP, repair.RP = (
            temporary, paths['word'], paths['center'], paths['R'])
        with redirect_stdout(io.StringIO()):
            repair.main()
        for name in ('l240-extra-column-gate.json', 'full-sink-gate.json',
                     'direct-l240-repair.json', 'l240-full-observations.json.gz'):
            actual, retained = read_json(temporary/name), read_json(HERE/name)
            if isinstance(actual, dict):
                actual.pop('elapsed_seconds', None)
                retained.pop('elapsed_seconds', None)
            require(actual == retained, 'Complete semantic artifact comparison: '+name)
        witness = independent_witness_check(
            read_json(temporary/'l240-extra-column-gate.json'),
            read_json(temporary/'l240-full-observations.json.gz'),
            json.loads(paths['R'].read_bytes())[5])
    print(json.dumps({'status': 'PASS_SCOPED_ACTIVE_MODE_RESTORATION',
                      'archive_sha256': ARCHIVE_SHA, 'independent_witness': witness,
                      'conditional_repair_inputs': 632, 'independent_helpers': 408,
                      'new_physical_construction': False, 'new_kappa_claim': False}, indent=2))


if __name__ == '__main__':
    main()
