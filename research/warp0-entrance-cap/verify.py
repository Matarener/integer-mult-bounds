"""Point-set forward closure of the zero-based native warp0 entrance.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The backward checker uses separate binary Gaussian elimination and imports
neither this file nor any retained executable.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent
ZERO = 1
FULL = (1 << 512) - 1
BASE_BLOB = '674ea18ade4af85ca865fb08dc973637a09e30e6'


def need(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(maxsize=None)
def points(mask):
    answer = []
    while mask:
        low = mask & -mask
        answer.append(low.bit_length() - 1)
        mask ^= low
    return tuple(answer)


def dimension(mask):
    n = mask.bit_count()
    need(n > 0 and n & (n - 1) == 0, 'subspace size')
    return n.bit_length() - 1


@lru_cache(maxsize=None)
def span(vectors):
    current = {0}
    for v in vectors:
        need(type(v) is int and 0 <= v < 512, 'binary vector')
        current |= {x ^ v for x in current}
    return sum(1 << x for x in current)


@lru_cache(maxsize=None)
def join(a, b):
    if a & ~b == 0:
        return b
    if b & ~a == 0:
        return a
    for v in points(b):
        if not (a >> v) & 1:
            a |= sum(1 << (x ^ v) for x in points(a))
    return a


def basis(mask):
    out, seen = [], ZERO
    for x in points(mask):
        if not (seen >> x) & 1:
            out.append(x)
            seen = join(seen, span((x,)))
    need(seen == mask, 'basis spans frame')
    return out


@lru_cache(maxsize=None)
def images(columns):
    need(len(columns) == 9, 'native columns')
    out = [0] * 512
    for x in range(1, 512):
        low = x & -x
        out[x] = out[x ^ low] ^ columns[low.bit_length() - 1]
    need(len(set(out)) == 512, 'invertible native map')
    return tuple(out)


def image(columns, mask):
    table = images(tuple(columns))
    return sum(1 << table[x] for x in points(mask))


def touched(gate):
    need(gate[0] in ('add', 'scale'), 'scalar opcode')
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def load_word():
    origin = json.loads((ROOT / 'ORIGINS.json').read_text())
    need(origin['head'] == '0c0e31cf12e8f4f07e8419a6d33ae85129fb5a01', 'source head')
    for row in origin['files']:
        path = (ROOT / 'source' / row['path']).resolve()
        need(path.is_relative_to(ROOT / 'source') and path.is_file(), 'source path')
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash')
        need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'source blob')
    raw = (ROOT / 'source/inputs/BASE-WORD.json.gz').read_bytes()
    need(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == BASE_BLOB, 'immutable base')
    return json.loads(gzip.decompress(raw))


def endpoint_caps(word):
    caps = {r: FULL for r in range(704) if r not in word['removed']}
    for r in range(112, 224):
        port = word['ports'][r - 112]
        caps[r] = sum(1 << x for x in range(512) if (port & x).bit_count() % 2 == 0)
    for r, vectors in word['helper_final'].items():
        caps[int(r)] = span(tuple(vectors))
    return caps


def prefix(word):
    current = {r: span((word['ports'][r],)) if r < 112 else ZERO
               for r in range(704) if r not in word['removed']}
    for r, frame in word['start_extra'].items():
        current[int(r)] = span(tuple(frame))
    bill = Counter()
    def climb(r, frame):
        need(current[r] & ~frame == 0, 'frozen prefix containment')
        d = dimension(frame) - dimension(current[r])
        if d:
            bill[d] += 1
        current[r] = frame
    for gate in word['A']:
        if gate[0] == 'warp':
            _, r, op, before, after = gate
            need(current[r] == span(tuple(before)), 'prelude entrance')
            columns = word['warps'][abs(op) - 1][2]
            table = images(tuple(columns))
            if op < 0:
                inv = [0] * 512
                for x, y in enumerate(table):
                    inv[y] = x
                transformed = sum(1 << inv[x] for x in points(current[r]))
            else:
                transformed = image(columns, current[r])
            need(transformed == span(tuple(after)), 'prelude transport')
            current[r] = transformed
        else:
            for r in touched(gate):
                climb(r, span(tuple(gate[-1])))
    levels = {112 + int(r): span(tuple(f)) for r, f in word['target_levels'].items()}
    need(all(current[r] == levels.get(r, ZERO) for r in range(112, 224)), 'target cut')
    # Preserve source frame_bill's temporary-descent accounting convention.
    for r, vectors in zip(word['centers'], word['center_frames']):
        local = span(tuple(vectors))
        need(current[r] == local, 'centre entry')
        served = {levels.get(g[1], ZERO) for g in word['cut'] if g[2] == r}
        for frame in sorted(served, key=lambda f: -dimension(f)):
            need(frame & ~local == 0, 'centre nesting')
            d = dimension(local) - dimension(frame)
            if d:
                bill[d] += 1
            local = frame
    position = word['warps'][0][0]
    need(position == 916 and word['warps'][0][1] == 243, 'frozen selected warp')
    earlier = {}
    for k, record in enumerate(word['warps']):
        if record[0] < position:
            earlier.setdefault(record[0], []).append(k)
    for i, gate in enumerate(word['B'][:position]):
        for k in earlier.get(i, []):
            _, r, columns, before, after = word['warps'][k]
            need(current[r] == span(tuple(before)), 'earlier B native entrance')
            current[r] = image(columns, current[r])
            need(current[r] == span(tuple(after)), 'earlier B native exit')
        for r in touched(gate):
            climb(r, span(tuple(gate[-1])))
    need(current[243] == span(tuple(word['warps'][0][3])), 'warp0 original entrance')
    return current, bill


def closure(word, entrance):
    current, bill = prefix(word)
    at = {}
    for k, record in enumerate(word['warps']):
        at.setdefault(record[0], []).append(k)
    scalar_edits, warp_edits, identities = [], [], []
    def scalar(g, section, i):
        frame = span(tuple(g[-1]))
        for r in touched(g):
            frame = join(frame, current[r])
        if frame != span(tuple(g[-1])):
            scalar_edits.append({'section': section, 'index': i, 'old': g[-1], 'new': basis(frame)})
        for r in touched(g):
            d = dimension(frame) - dimension(current[r])
            if d:
                bill[d] += 1
            current[r] = frame
    for i in range(word['warps'][0][0], len(word['B']) + 1):
        for k in at.get(i, []):
            old = word['warps'][k]
            frame = entrance if k == 0 else join(span(tuple(old[3])), current[old[1]])
            need(current[old[1]] & ~frame == 0, 'entrance contains current')
            if frame != current[old[1]]:
                d = dimension(frame) - dimension(current[old[1]])
                bill[d] += 1
                identities.append({'warp': k, 'register': old[1], 'rank': d})
            exit_frame = image(old[2], frame)
            if frame != span(tuple(old[3])):
                warp_edits.append({'index': k, 'old': old[3:], 'new': [basis(frame), basis(exit_frame)]})
            current[old[1]] = exit_frame
        if i < len(word['B']):
            scalar(word['B'][i], 'B', i)
    for i, gate in enumerate(word['restore']):
        scalar(gate, 'restore', i)
    for r, cap in sorted(endpoint_caps(word).items()):
        if current[r] & ~cap:
            return {'accepted': False, 'failure_register': r,
                    'violating_vector': points(current[r] & ~cap)[0]}
        d = dimension(cap) - dimension(current[r])
        if d:
            bill[d] += 1
    return {'accepted': True, 'profile': dict(sorted(bill.items())),
            'recipe': {'scalar_edits': scalar_edits, 'warp_edits': warp_edits}, 'identities': identities}


def compute(word):
    u = span(tuple(word['warps'][0][3]))
    base = closure(word, u)
    need(base['accepted'] and base['recipe'] == {'scalar_edits': [], 'warp_edits': []}
         and not base['identities'], 'literal baseline control')
    representatives = {}
    for v in range(512):
        space = join(u, span((v,)))
        if dimension(space) == 5:
            representatives.setdefault(space, v)
    need(len(representatives) == 31, 'complete quotient line domain')
    rows, allowed = [], u
    for space, v in sorted(representatives.items(), key=lambda row: row[1]):
        result = closure(word, space)
        if result['accepted']:
            allowed = join(allowed, space)
        rows.append({'representative': v, 'entrance_points': list(points(space)), **result})
    accepted = [r for r in rows if r['accepted']]
    need(len(accepted) == 1 and accepted[0]['representative'] == 7, 'sole allowed direction')
    new = accepted[0]
    delta = {r: new['profile'].get(r, 0) - base['profile'].get(r, 0)
             for r in set(new['profile']) | set(base['profile'])}
    delta = {r: n for r, n in sorted(delta.items()) if n}
    need(delta == {1: 27, 2: -14, 3: -1, 4: 1}, 'canonical complete profile')
    need(sum(r * n for r, n in delta.items()) == 0, 'rank mass preserved')
    need(not any(e['section'] == 'restore' and e['index'] == 191
                 for e in new['recipe']['scalar_edits']), 'centre restore unchanged')
    # For q in (0,1): delta(q)=(2-2^q)(12-2^q)+(3-3^q)>0.
    need([2 * 12 + 3, -12 - 2, -1, 1] == [27, -14, -1, 1], 'factor identity')
    need(sum(n * min(r, 2) for r, n in delta.items()) == -1,
         'control: result does not imply every concave tariff loses')
    independent = json.loads((ROOT / 'INDEPENDENT-RESULT.json').read_text())
    need(span(tuple(independent['maximal_entrance'])) == allowed, 'independent backward cap')
    need(independent['rejected_quotient_lines'] == 30, 'independent exclusion count')
    independent_rows = {r['representative']: r for r in independent['extensions']}
    for row in rows:
        other = independent_rows[row['representative']]
        need(span(tuple(other['entrance'])) == span(tuple(row['entrance_points'])), 'independent domain')
        need(row['accepted'] == other['accepted'], 'independent directional outcome')
    # Gaussian binomial counts for subspaces of the five-dimensional quotient.
    subspace_counts = []
    for k in range(6):
        numerator = denominator = 1
        for i in range(k):
            numerator *= 2 ** (5 - i) - 1
            denominator *= 2 ** (k - i) - 1
        need(numerator % denominator == 0, 'integral subspace count')
        subspace_counts.append(numerator // denominator)
    need(subspace_counts == [1, 31, 155, 155, 31, 1], 'complete entrance lattice')
    return {'status': 'PASS_WARP_ZERO_ENTRANCE_CAP', 'source_blob': BASE_BLOB,
            'original_entrance_points': list(points(u)), 'maximal_entrance_points': list(points(allowed)),
            'maximal_dimension': dimension(allowed), 'quotient_lines': len(rows), 'rejected_lines': 30,
            'all_superframes_count': sum(subspace_counts), 'superframes_by_quotient_dimension': subspace_counts,
            'admissible_superframes_count': 2,
            'baseline_profile': base['profile'], 'canonical_profile': new['profile'], 'canonical_delta': delta,
            'canonical_recipe': new['recipe'], 'paid_identities': new['identities'],
            'restore191_unchanged': True, 'extensions': rows,
            'strict_all_power_loss': '27-14*2^q-3^q+4^q=(2-2^q)(12-2^q)+(3-3^q)>0 for0<q<1',
            'concave_countercontrol': {'tariff': 'min(rank,2)', 'new_minus_old': -1},
            'new_kappa': None}


def source_crosscheck(word, result):
    need(not any((ROOT / 'source').rglob('*.pyc')), 'untrusted source bytecode')
    sys.path.insert(0, str(ROOT / 'source'))
    spec = importlib.util.spec_from_file_location('source_frames', ROOT / 'source/frames.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    candidate = module.compile_frames(word, result['canonical_recipe'])
    bill, inventory, _, _, _ = module.audit.frame_bill(candidate, lagrangian=True)
    need(bill == result['canonical_profile'], 'source bill agrees')
    need(candidate['restore'][191] == word['restore'][191], 'actual centre frame preserved')
    need([r[1:] for r in candidate['warps']][1:] == [r[1:] for r in word['warps']][1:], 'later native boundaries unchanged')
    need(module.audit.endpoint_defects(candidate, module.audit.forward_rows(candidate, symbolic_buffers=True))
         == ([], [], [], True), 'arbitrary dirty forward endpoint')
    need(module.audit.endpoint_defects(candidate, module.audit.forward_rows(candidate, dual=True, symbolic_buffers=True), dual=True)
         == ([], [], [], True), 'arbitrary dirty dual endpoint')
    need(not module.audit.boundary_defects(candidate, module.audit.transpose(module.audit.reverse_columns(candidate, upto_cleanup=True))), 'dirty cleanup boundary')
    published_recipe = json.loads((ROOT / 'source/inputs/RECIPE.json').read_text())
    need(all(span(tuple(e['old'])) & ~span(tuple(e['new'])) == 0
             for e in published_recipe['scalar_edits']), 'published original-frame floors')
    published = module.compile_frames(word, published_recipe)
    published_bill, published_inventory, _, _, _ = module.audit.frame_bill(published)
    expected_published = json.loads((ROOT / 'source/RESULT.json').read_text())['profile']
    need({str(r): n for r, n in published_bill.items()} == expected_published, 'published profile binding')
    need(published_inventory == inventory, 'same native inventory')
    need(len(published['warps']) == len(candidate['warps']), 'same native count')
    for a, b in zip(candidate['warps'], published['warps']):
        need(a[:3] == b[:3] and span(tuple(a[3])) == span(tuple(b[3]))
             and span(tuple(a[4])) == span(tuple(b[4])), 'same native maps and boundary subspaces')
    strict_frames = 0
    for section in ('A', 'B', 'restore'):
        need(len(candidate[section]) == len(published[section]), 'same scalar word length')
        for a, b in zip(candidate[section], published[section]):
            need(a[:-1] == b[:-1], 'same scalar opcode and coefficients')
            if a[0] != 'warp':
                small, large = span(tuple(a[-1])), span(tuple(b[-1]))
                need(small & ~large == 0, 'published contains canonical frames')
                strict_frames += small != large
    need(strict_frames > 0, 'strictly nonminimal published frames')
    difference = {r: bill.get(r, 0) - published_bill.get(r, 0) for r in set(bill) | set(published_bill)}
    difference = {r: n for r, n in sorted(difference.items()) if n}
    need(difference == {1: -1, 2: 2, 3: 3, 4: -3}, 'nonminimal published price control')
    caps = [sum(n * min(r, t) for r, n in difference.items()) for t in range(1, 5)]
    need(caps == [1, 3, 3, 0], 'strict concavity cost countercontrol')
    return {'source_compiler_and_bill': True, 'forward_dual_cleanup': True,
            'native_phases_rerun': False, 'inventory': inventory,
            'published_profile': published_bill, 'canonical_minus_published': difference,
            'difference_capped_sums': caps,
            'strictly_larger_published_scalar_frames': strict_frames,
            'nonminimal_published_completion_strictly_cheaper_for_all_powers': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--geometry-only', action='store_true')
    args = parser.parse_args()
    word = load_word()
    result = compute(word)
    if not args.geometry_only:
        result['source_crosscheck'] = source_crosscheck(word, result)
    target = ROOT / 'RESULT.json'
    if args.write:
        need(not args.geometry_only, 'full crosscheck required')
        target.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        saved = json.loads(target.read_text())
        if args.geometry_only:
            saved.pop('source_crosscheck', None)
        need(json.dumps(saved, sort_keys=True) == json.dumps(result, sort_keys=True), 'complete result receipt')
    print(json.dumps({'status': result['status'], 'dimension': result['maximal_dimension'],
                      'rejected_lines': result['rejected_lines'], 'delta': result['canonical_delta']}, sort_keys=True))


if __name__ == '__main__':
    main()
