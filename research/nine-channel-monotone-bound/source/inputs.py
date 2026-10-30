"""Authenticate the retained archive and exact imported code. Apache-2.0."""
from fractions import Fraction as F
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import sys
import tarfile
import types

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parents[1] / 'research/filtered-native-kappa004/inputs/original-packet.tar.gz'
ARCHIVE_SHA = '595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7'
PREFIX = 'filtered_native_implementation/'
MEMBERS = {
    'word': 'research/retained_state_next/F9-SOURCE-DAG-ALL8-WORD.json.gz',
    'original': 'research/native_contact/SCALED-GLOBAL-CANCEL-WORD.json.gz',
    'R': 'upstream/research/involutory-producer-raw-dual/inputs/R/R.json',
    'core': 'upstream/research/involutory-producer-raw-dual/inputs/core/native_core.py',
    'ce': 'research/tensor_obstruction/inputs/clifford_exact.py',
    'license': 'upstream/LICENSE',
}


def need(ok, message):
    if not ok: raise ValueError(message)


def module(name, raw, path):
    obj = types.ModuleType(name); obj.__file__ = str(path); sys.modules[name] = obj
    exec(compile(raw, str(path), 'exec'), obj.__dict__)
    return obj


def load():
    raw = ARCHIVE.read_bytes(); need(sha256(raw).hexdigest() == ARCHIVE_SHA, 'Pinned archive')
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        data = {}
        for key, name in MEMBERS.items():
            member = archive.getmember(PREFIX + name)
            need(member.isfile(), 'Regular archive input')
            data[key] = archive.extractfile(member).read()
    need(sha256(data['word']).hexdigest() == '934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775', 'Pinned word')
    for row in json.loads((ROOT / 'INPUTS.json').read_text()):
        need(sha256((ROOT / 'source' / row['local']).read_bytes()).hexdigest() == row['sha256'], 'Pinned source: ' + row['local'])
    word = json.loads(gzip.decompress(data['word']))
    original = json.loads(gzip.decompress(data['original']))
    modes = [[F(x) for x in row] for row in json.loads(data['R'])]
    core = module('delivery_core', data['core'], ROOT / 'source/native_core.py')
    ce = module('delivery_clifford', data['ce'], ROOT / 'source/clifford_exact.py')
    quad = module('delivery_quadratic', (ROOT / 'source/quadratic.py').read_bytes(), ROOT / 'source/quadratic.py')
    return word, original, modes, core, ce, quad


def index(ref):
    return ref[1] + (632 if ref[0] == 'C' else 0)


def add(dst, src, coefficient):
    for i, value in src.items():
        changed = dst.get(i, F(0)) + coefficient * value
        if changed: dst[i] = changed
        else: dst.pop(i, None)
