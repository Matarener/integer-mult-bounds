"""Exact responses of the frozen word in the restored-Y quotient.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parents[1] / 'research/filtered-native-kappa004/inputs/original-packet.tar.gz'
ARCHIVE_SHA = '595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7'
MEMBERS = {
    'word': ('research/retained_state_next/F9-SOURCE-DAG-ALL8-WORD.json.gz',
             '934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775'),
    'R': ('upstream/research/involutory-producer-raw-dual/inputs/R/R.json',
          '7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1'),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    raw = ARCHIVE.read_bytes()
    need(sha256(raw).hexdigest() == ARCHIVE_SHA, 'Exact source archive')
    data = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for key, (path, digest) in MEMBERS.items():
            name = 'filtered_native_implementation/' + path
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), 'Unique regular input')
            value = archive.extractfile(matches[0]).read()
            need(sha256(value).hexdigest() == digest, 'Exact data member')
            data[key] = value
    return json.loads(gzip.decompress(data['word'])), [
        [F(v) for v in row] for row in json.loads(data['R'])]


def add(dst, src, coefficient):
    for i, v in list(src.items()):
        value = dst.get(i, F(0)) + coefficient * v
        if value:
            dst[i] = value
        else:
            dst.pop(i, None)


def reduce(v, basis):
    v = dict(v)
    for pivot, row in basis.items():
        if v.get(pivot):
            add(v, row, -v[pivot])
    return v


def insert(v, basis):
    v = reduce(v, basis)
    if v:
        pivot = min(v)
        value = v[pivot]
        basis[pivot] = {i: a / value for i, a in v.items()}


def span(vectors):
    basis = {}
    for v in vectors:
        insert(v, basis)
    return basis


def scan(word, modes, restore_y=True):
    """Visit every change to an impulse response or its available chart."""
    need(len(modes) == 8 and all(len(r) == 112 for r in modes), 'Mode dimensions')
    need(all(sum(modes[a][j] * modes[b][j] for j in range(112)) ==
             (56 if a == b else 0) for a in range(8) for b in range(8)), 'Mode Gram')
    need(all(any(row[i] for row in modes) for i in range(112)), 'Nonzero target rows')
    events = word['programs']['backward']
    frames = word['canonical']['frames']
    def owner(ref):
        need(ref[0] in ('L', 'C'), 'Owner kind')
        return ref[1] + (632 if ref[0] == 'C' else 0)
    n = 1 + max(owner(ref) for e in events if e[0] == 'scalar'
                for ref in e[1] if isinstance(ref, list))
    current = word['canonical']['start'][:] + [None] * (n - 632)
    changes = {}
    available = set(current) - {None}
    for at, event in enumerate(events):
        kind = event[0]
        need(kind in ('scalar', 'warp', 'climb', 'center', 'phase', 'adapter',
                      'residual_adapter', 'physical_add'), 'Known source opcode')
        destination = None
        if kind == 'scalar' and event[1][0] == 'clear':
            destination, frame = owner(event[1][1]), event[2]
        elif kind == 'warp':
            destination, frame = owner(event[1]), event[4]
        elif kind == 'climb':
            destination, frame = event[2], event[4]
        elif kind == 'center':
            destination, frame = 632 + event[1], event[3]
        if destination is not None:
            changes[at] = destination, current[destination]
            if kind in ('warp', 'climb'):
                need(current[destination] == event[3], 'Native chart source')
            current[destination] = frame
            available.add(frame)
    need(current[:632] == word['canonical']['final'], 'Final public charts')
    C = [{i: F(i == j) - sum(modes[k][i] * modes[k][j] for k in range(8)) / 4
          for i in range(112)} for j in range(112)]
    columns = [{i: F(1)} for i in range(112)] + [
        {i: v for i, v in row.items() if v} if restore_y else {} for row in C
    ] + [{} for _ in range(n - 224)]
    seen = defaultdict(dict)
    def capture(d, at):
        frame = current[d]
        if frame is not None and columns[d]:
            seen[frame].setdefault(tuple(sorted(columns[d].items())), (at, d))
    for d in range(n):
        capture(d, len(events))
    for at in reversed(range(len(events))):
        event = events[at]
        changed = []
        if event[0] == 'scalar':
            op = event[1]
            kind, d = op[0], owner(op[1])
            if kind == 'add':
                s = owner(op[2])
                need(s != d and current[s] == current[d] == event[2], 'Coframed ADD')
                add(columns[s], columns[d], F(op[3], op[4]))
                changed = [s]
            elif kind == 'copy':
                s = owner(op[2])
                need(s != d, 'Distinct COPY fields')
                add(columns[s], columns[d], F(1))
                columns[d] = {}
                changed = [s, d]
            elif kind == 'clear':
                columns[d] = {}
                changed = [d]
            elif kind == 'scale':
                columns[d] = {i: v * F(op[2], op[3]) for i, v in columns[d].items()}
                changed = [d]
            else:
                raise ValueError('Known scalar opcode')
        if at in changes:
            d, old = changes[at]
            current[d] = old
            changed.append(d)
        for d in set(changed):
            capture(d, at)
    if restore_y:
        need(all(columns[i] == {i: F(1)} for i in range(112)) and
             not any(columns[112:]), 'Complete initial restored-Y invariant')
    charts = {}
    for frame in sorted(available):
        values = [dict(v) for v in seen[frame]]
        charts[frame] = dict(rank=len(frames[frame]), basis=span(values),
                             support=set().union(*(set(v) for v in values)),
                             responses=len(values))
    target = [{i: v for i, v in enumerate(row) if v} for row in modes]
    return charts, target, dict(events=len(events), roles=n, charts=len(charts),
                               nonzero_charts=sum(bool(c['basis']) for c in charts.values()),
                               responses=sum(len(v) for v in seen.values()))


def rank_cut(charts, target, frame_ids):
    basis = span(v for frame in frame_ids for v in charts[frame]['basis'].values())
    target_rank = len(span(reduce(v, basis) for v in target))
    active = [f for f, chart in charts.items()
              if any(reduce(v, basis) for v in chart['basis'].values())]
    return target_rank, active
