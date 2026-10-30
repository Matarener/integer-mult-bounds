"""Build the actual minimum pool after safe private lifetime trimming.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
P104 source and allocator credits remain in inputs/NOTICE and vendor files.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def roles(e):
    return e[1:3] if e[0] in ('ADD', 'COPY') else e[1:2]


def episodes(word):
    active, out, at = {}, [], {}
    for i, e in enumerate(word['program']):
        op, r = e[:2]
        if op == 'INIT':
            need(r not in active, 'fresh source lifetime')
            active[r] = len(out)
            out.append({'id': str(len(out)), 'role': r, 'begin': i, 'uses': []})
        elif op == 'CLEAR':
            need(r in active, 'source lifetime cleanup')
            out[active.pop(r)]['end'] = i
        else:
            for role in roles(e):
                if role >= word['public']:
                    need(role in active, 'owned access inside lifetime')
                    life = active[role]
                    out[life]['uses'].append(i)
                    at[i, role] = life
    need(not active, 'all source lifetimes closed')
    return out, at


def retain(word):
    """Keep all public operations and private operations with a later read."""
    wanted, kept = set(), set()
    for i in range(len(word['program'])-1, -1, -1):
        e = word['program'][i]; op, r = e[:2]
        if op in ('INIT', 'CLEAR'):
            wanted.discard(r)
            continue
        if r < word['public'] or r in wanted:
            kept.add(i)
            if op in ('ADD', 'COPY'):
                if op == 'COPY':
                    wanted.discard(r)
                if e[2] >= word['public']:
                    wanted.add(e[2])
    return kept


def construct(source, allocator):
    lives, at = episodes(source)
    kept = retain(source)
    intervals = []
    for life in lives:
        used = [i for i in life['uses'] if i in kept]
        if used:
            intervals.append({'id': life['id'], 'start': 2*used[0],
                              'end': 2*used[-1]+1, 'width': 1})
    problem = {'schema': 'integer-mult-helper-lifetimes/v1',
               'contract': 'One fixed-width field per retained P104 private episode; exact source operation boundaries.',
               'lifetimes': intervals}
    certificate = allocator.allocate(problem)
    slots = {int(k): source['public']+ranges[0][0]
             for k, ranges in certificate['allocations'].items()}
    # Multiple episodes can first or last touch the same COPY/ADD.
    starts, ends = {}, {}
    for row in intervals:
        starts.setdefault(row['start']//2, []).append(int(row['id']))
        ends.setdefault(row['end']//2, []).append(int(row['id']))
    program, source_indices = [], []
    for i, e in enumerate(source['program']):
        if i not in kept:
            continue
        frame = e[2] if e[0] == 'MOVE' else e[-1]
        for life in sorted(starts.get(i, [])):
            program.append(['INIT', slots[life], frame]); source_indices.append(None)
        new = list(e)
        for pos in ([1, 2] if e[0] in ('ADD', 'COPY') else [1]):
            if e[pos] >= source['public']:
                new[pos] = slots[at[i, e[pos]]]
        program.append(new); source_indices.append(i)
        frame = e[3] if e[0] == 'MOVE' else e[-1]
        for life in sorted(ends.get(i, [])):
            program.append(['CLEAR', slots[life], frame]); source_indices.append(None)
    result = deepcopy(source)
    result.update(owned_fields=certificate['capacity'], program=program)
    return result, problem, certificate, source_indices, sorted(set(range(len(source['program'])))-kept)


def trace(word, local):
    """Record each public observation and native query on exact public RAW rows."""
    rows = [{i: local.Q(1)} for i in range(word['public']+word['owned_fields'])]
    observations, native = [], []
    for e in word['program']:
        op, r = e[:2]
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
        elif op == 'MOVE':
            native.append([e[2:], sorted((i, str(v)) for i, v in rows[r].items())])
        else:
            q = local.Q(e[-2])
            if op == 'SCALE':
                rows[r] = {i:q*v for i,v in rows[r].items()}
            else:
                if r < word['public']:
                    observations.append([e[0], r, e[-2:], sorted((i, str(v)) for i,v in rows[e[2]].items())])
                if op == 'COPY':
                    rows[r] = {i:q*v for i,v in rows[e[2]].items()}
                else:
                    local.add(rows[r], rows[e[2]], q)
    return observations, native


def run(emit):
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for pin in sources['vendored_inputs']:
        need(sha256((HERE/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'frozen source '+pin['path'])
    source = json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))
    local = load(HERE/'inputs/local.py', 'pool_local')
    allocator = load(HERE/'vendor/allocate_helper_lifetimes.py', 'pool_allocator')
    word, problem, certificate, indices, omitted = construct(source, allocator)
    before, after = local.replay(source), local.replay(word)
    source_receipt = json.loads((HERE/'inputs/RESULT.json').read_text())
    need(canonical(before) == canonical(source_receipt['local']), 'published local receipt')
    transpose = local.reverse_columns(word)
    old_observation, old_native = trace(source, local)
    observation, native = trace(word, local)
    need(observation == old_observation, 'every public source observation')
    need(native == old_native, 'every exact native payload and frame')
    for key in ('paid', 'helpers', 'public_inputs', 'paid_rank_mass'):
        need(before[key] == after[key], 'retained profile '+key)
    need(after['real_scalar_allowance'] <= before['real_scalar_allowance'], 'complete local scalar cost')
    controls = []
    peak = certificate['peak']['ids']
    bad = deepcopy(certificate); bad['allocations'][peak[0]] = bad['allocations'][peak[1]]
    try:
        allocator.verify(problem, bad)
    except ValueError as error:
        controls.append(['colliding live slots', str(error)])
    else:
        raise ValueError('collision accepted')
    bad = deepcopy(word)
    first = next(i for i,e in enumerate(bad['program']) if e[0]=='INIT')
    del bad['program'][first]
    try:
        local.replay(bad)
    except ValueError as error:
        controls.append(['missing dirty-slot INIT', str(error)])
    else:
        raise ValueError('dirty input leak accepted')
    result = {'schema':'p104-compact-owned-pool/1', 'before':before, 'after':after,
              'source_operations':len(source['program']), 'operations':len(word['program']),
              'problem':problem, 'minimum_certificate':certificate, 'transpose':transpose,
              'native_payload_sha256':sha256(canonical(native)).hexdigest(),
              'public_observations':len(observation), 'public_observation_sha256':sha256(canonical(observation)).hexdigest(),
              'word_sha256':sha256(canonical(word)).hexdigest(),
              'source_index_map_sha256':sha256(canonical(indices)).hexdigest(),
              'omitted_source_indices':omitted, 'controls':controls}
    if emit:
        (emit/'RESULT.json').write_bytes(json.dumps(result,sort_keys=True,indent=1).encode()+b'\n')
        (emit/'WORD.json.gz').write_bytes(gzip.compress(canonical(word),mtime=0))
    else:
        need(canonical(result)==canonical(json.loads((HERE/'RESULT.json').read_text())), 'complete result receipt')
        need(canonical(word)==canonical(json.loads(gzip.decompress((HERE/'WORD.json.gz').read_bytes()))), 'complete emitted word')
    print('PASS_P104_COMPACT_OWNED_POOL', before['owned_fields'], after['owned_fields'],
          before['real_scalar_allowance'], after['real_scalar_allowance'])


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--emit', type=Path)
    run(ap.parse_args().emit)
