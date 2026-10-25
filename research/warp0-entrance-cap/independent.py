"""Independent backward frame-cap certificate for native warp zero.

No compiler/auditor/primary checker is imported. Binary Gaussian bases are
used rather than the source's point-set frame representation. Prepared for
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path


BASE_BLOB = '674ea18ade4af85ca865fb08dc973637a09e30e6'
FULL = (256, 128, 64, 32, 16, 8, 4, 2, 1)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def basis(vectors):
    rows = [0]*9
    for x in vectors:
        need(type(x) is int and 0 <= x < 512, 'binary vector')
        while x:
            p = x.bit_length()-1
            if rows[p]:
                x ^= rows[p]
            else:
                rows[p] = x
                break
    for p in range(9):
        if rows[p]:
            for q in range(p+1, 9):
                if rows[q] & (1 << p):
                    rows[q] ^= rows[p]
    return tuple(x for x in reversed(rows) if x)


def has(rows, x):
    for r in rows:
        if x & (1 << (r.bit_length()-1)):
            x ^= r
    return x == 0


def subset(a, b):
    return all(has(b, x) for x in a)


@lru_cache(maxsize=None)
def meet(a, b):
    return basis(x for x in range(512) if has(a, x) and has(b, x))


def joined(*spaces):
    return basis(x for space in spaces for x in space)


def image_vector(x, columns):
    y = 0
    for j, c in enumerate(columns):
        if x & (1 << j):
            y ^= c
    return y


@lru_cache(maxsize=None)
def inverse(columns):
    images = [image_vector(x, columns) for x in range(512)]
    need(len(set(images)) == 512, 'invertible native map')
    answer = [0]*512
    for x, y in enumerate(images):
        answer[y] = x
    return tuple(answer)


def operands(g):
    need(g[0] in ('add', 'scale'), 'scalar opcode')
    return g[1:3] if g[0] == 'add' else g[1:2]


def ends(word):
    live = set(range(704))-set(word['removed'])
    cap = {r: FULL for r in live}
    for r in range(112, 224):
        port = word['ports'][r-112]
        cap[r] = basis(x for x in range(512) if (x & port).bit_count() % 2 == 0)
    for r, frame in word['helper_final'].items():
        cap[int(r)] = basis(frame)
    return cap


def backward(word, freeze_later):
    cap = ends(word)
    checks = 0
    def scalar(g):
        nonlocal checks
        regs = operands(g)
        common = cap[regs[0]]
        for r in regs[1:]:
            common = meet(common, cap[r])
        need(subset(basis(g[-1]), common), 'original scalar lower frame exceeds future cap')
        for r in regs:
            cap[r] = common
        checks += 1
    for g in reversed(word['restore']):
        scalar(g)
    at = {}
    for k, rec in enumerate(word['warps']):
        at.setdefault(rec[0], []).append(k)
    records = []
    for p in range(len(word['B']), -1, -1):
        if p < len(word['B']):
            scalar(word['B'][p])
        for k in reversed(at.get(p, [])):
            _, r, columns, u, e = word['warps'][k]
            old_u, old_e = basis(u), basis(e)
            need(subset(old_e, cap[r]), 'original native exit exceeds future cap')
            inv = inverse(tuple(columns))
            pre = basis(inv[x] for x in cap[r])
            need(subset(old_u, pre), 'original native entrance exceeds pullback')
            records.append({'warp': k, 'register': r, 'post_cap': list(cap[r]), 'pre_cap': list(pre)})
            if k == 0:
                return {'maximal_entrance': list(pre), 'dimension': len(pre),
                        'scalar_constraints': checks, 'native_pullbacks': records}
            cap[r] = old_u if freeze_later else pre
    raise ValueError('missing warp zero')


def after_A(word):
    cur = {r: ((word['ports'][r],) if r < 112 else ())
           for r in set(range(704))-set(word['removed'])}
    for r, frame in word['start_extra'].items():
        cur[int(r)] = basis(frame)
    for g in word['A']:
        if g[0] == 'warp':
            cur[g[1]] = basis(g[4])
        else:
            for r in operands(g):
                frame = basis(g[-1])
                need(subset(cur[r], frame), 'A containment')
                cur[r] = frame
    # Centre descents are temporary billed calls and leave the persistent
    # main forward register at the declared centre entry, as in source audit.
    return cur


def forward(word, extra=None, frozen=False):
    cur, bill = after_A(word), Counter()
    scalar_changes = 0
    native_changes = []
    identities = []
    def scalar(g):
        nonlocal scalar_changes
        regs = operands(g)
        old = basis(g[-1])
        frame = old if extra is None else joined(old, *(cur[r] for r in regs))
        scalar_changes += frame != old
        for r in regs:
            need(subset(cur[r], frame), 'scalar containment')
            bill[len(frame)-len(cur[r])] += 1
            cur[r] = frame
    at = {}
    for k, record in enumerate(word['warps']):
        at.setdefault(record[0], []).append(k)
    for p in range(len(word['B'])+1):
        for k in at.get(p, []):
            _, r, columns, u, e = word['warps'][k]
            old = basis(u)
            frame = old if extra is None else joined(old, cur[r], (() if k else (extra,)))
            if frozen and k and frame != old:
                return {'accepted': False, 'failure_kind': 'native', 'failure_register': r, 'warp': k}
            need(subset(cur[r], frame), 'native entrance containment')
            if frame != cur[r]:
                identities.append([k, r, len(frame)-len(cur[r])])
                bill[len(frame)-len(cur[r])] += 1
            if frame != old:
                native_changes.append(k)
            cur[r] = basis(image_vector(x, columns) for x in frame)
            need(subset(basis(e), cur[r]), 'native exit lower frame')
        if p < len(word['B']):
            scalar(word['B'][p])
    for g in word['restore']:
        scalar(g)
    for r, end in sorted(ends(word).items()):
        if not subset(cur[r], end):
            bad = next(x for x in cur[r] if not has(end, x))
            return {'accepted': False, 'failure_kind': 'terminal',
                    'failure_register': r, 'violating_vector': bad,
                    'terminal_cap': list(end)}
        bill[len(end)-len(cur[r])] += 1
    bill.pop(0, None)
    return {'accepted': True, 'bill': dict(sorted(bill.items())),
            'scalar_changes': scalar_changes, 'native_changes': native_changes,
            'identities': identities}


def compute(path):
    compressed = path.read_bytes()
    actual = hashlib.sha1(b'blob '+str(len(compressed)).encode()+b'\0'+compressed).hexdigest()
    need(actual == BASE_BLOB, 'immutable compressed base word')
    word = json.loads(gzip.decompress(compressed))
    relaxed = backward(word, False)
    frozen = backward(word, True)
    need(relaxed['maximal_entrance'] == frozen['maximal_entrance'], 'fixed/relaxed cap mismatch')
    original = basis(word['warps'][0][3])
    expected = joined(original, (7,))
    cap = tuple(relaxed['maximal_entrance'])
    need(cap == expected and len(original) == 4 and len(cap) == 5, 'sharp entrance cap')
    representatives = {}
    for v in range(512):
        extension = joined(original, (v,))
        if len(extension) == 5:
            representatives.setdefault(extension, v)
    need(len(representatives) == 31, 'complete quotient lines')
    base = forward(word)
    need(base['accepted'] and not base['identities'] and not base['native_changes'], 'literal original baseline')
    rows = []
    for extension, v in sorted(representatives.items(), key=lambda item: item[1]):
        result = forward(word, v)
        need(result['accepted'] == subset(extension, cap), 'forward/backward equivalence')
        if result['accepted']:
            fixed_result = forward(word, v, True)
            need(fixed_result == result, 'sole admitted extension preserves later native frames')
            delta = {rank: result['bill'].get(rank, 0)-base['bill'].get(rank, 0) for rank in range(1, 10)}
            delta = {rank: count for rank, count in delta.items() if count}
            need(delta == {1: 27, 2: -14, 3: -1, 4: 1}, 'least-closure price')
            caps = [sum(count*min(rank, k) for rank, count in delta.items()) for k in range(1, 10)]
            prefix, prefixes = 0, []
            for value in caps[:-1]:
                prefix += value
                prefixes.append(prefix)
            need(sum(rank*count for rank, count in delta.items()) == 0 and
                 all(x >= 0 for x in prefixes) and any(x > 0 for x in prefixes), 'all-power non-improvement')
            result.update(delta=delta, capped_sums=caps, cap_prefixes=prefixes)
        rows.append({'representative': v, 'entrance': list(extension), **result})
    need(sum(row['accepted'] for row in rows) == 1, 'unique admitted extension')
    controls = []
    for value in (True, -1, 512):
        try:
            basis((value,))
        except ValueError:
            controls.append('invalid_binary_vector_rejected_'+str(value))
        else:
            raise ValueError('invalid vector accepted')
    try:
        inverse((1, 2, 4, 8, 16, 32, 64, 128, 128))
    except ValueError:
        controls.append('singular_native_map_rejected')
    else:
        raise ValueError('singular native map accepted')
    counterfactual = deepcopy(word)
    counterfactual['ports'] = [0]*112
    no_target_caps = backward(counterfactual, False)
    need(no_target_caps['dimension'] == 9, 'caller target caps are essential')
    controls.append('omitting_target_caps_expands_maximum_to_nine')
    forbidden = joined(original, (7, 1))
    need(len(forbidden) == 6 and not subset(forbidden, cap), 'forbidden extra quotient line')
    controls.append('dimension_six_extension_fails_cap')
    bad = next(row for row in rows if row['representative'] == 1)
    need(not bad['accepted'] and bad['failure_kind'] == 'terminal' and
         bad['failure_register'] == 112, 'wrong entrance reaches caller target')
    controls.append('wrong_direction_violates_target_112')
    return {'status': 'PASS_INDEPENDENT_WARP_ZERO_CAP',
            'compressed_base_git_blob': actual,
            'compressed_base_sha256': hashlib.sha256(compressed).hexdigest(),
            'original_entrance': list(original), 'maximal_entrance': list(cap),
            'maximal_dimension': len(cap), 'quotient_line_count': 31,
            'rejected_quotient_lines': 30, 'baseline_tail_bill': base['bill'],
            'backward_relaxed': relaxed, 'backward_frozen': frozen, 'extensions': rows,
            'semantic_controls': controls,
            'scope': 'Fixed literal scalar opcode word; monotone scalar-frame enlargement and compatible native transport; fixed caller cuts, A and terminal frames. No native phase rerun, global optimality or kappa claim.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = compute(args.word)
    text = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.check:
        saved = json.loads(args.check.read_text(encoding='utf-8'))
        encode = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'))
        need(encode(saved) == encode(result), 'complete independent receipt')
        print(result['status'])
        return
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
