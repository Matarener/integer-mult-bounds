#!/usr/bin/env python3
"""Exact dirty covector and transposed receiver rewrites for the R437 bit word.

Only existing rational frames are used.  Observer-free clusters come from the
frozen adaptive source-covector catalogue; their elementary identity is over
F2 here.  Complete arbitrary-input checks and literal H1-H5 checks run on every
positive candidate.  No hosted/native/global claim follows from discovery.

Credit Nick Petalas for dirty shared covectors, dataisfire and the adaptive
continuation for its receiver transpose, ai-nanachi for the R437 composition,
Ali Romman for its helper470 source deletion, and all retained source notices.
Substantial OpenAI assistance. Apache-2.0.
"""
from bisect import bisect_left
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = ROOT / 'research/kappa-adaptive-continuation/native-alternatives'
sys.path.insert(0, str(FROZEN))
from fanout_search import pair_catalog, clusters

DEFAULT_SOURCE = ROOT / 'research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018'


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load_checker(path):
    spec = importlib.util.spec_from_file_location('pinned_r437_xcheck', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten(word):
    return {name: [['add', d, s, 1, 1, f]
                   for f, d, sources in word[name] for s in sources]
            for name in ('D', 'A', 'B', 'C')}


def transpose(events):
    return [['add', e[2], e[1], 1, 1, e[-1]] for e in reversed(events)]


class Frames:
    def __init__(self, word, checker):
        self.word = word
        self.checker = checker
        self.dim = checker.fdim
        self.masks = [sum(1 << i for i in f) for f in word['frames']]
        # Frame labels are closed in the supplied rational line set.  Inclusion
        # of their complete label sets exactly implies span inclusion; confirm
        # every inclusion queried below with the independent rational checker.
        self.inc = [[not (a & ~b) for b in self.masks] for a in self.masks]
        self.verified = set()

    def nested(self, a, b):
        answer = self.inc[a][b]
        if (a, b) not in self.verified:
            if answer != self.checker.nested(a, b):
                raise ValueError(('label/rational inclusion mismatch', a, b))
            self.verified.add((a, b))
        return answer

    def upper_frames(self, a, b):
        return [f for f in range(len(self.dim)) if self.inc[a][f] and self.inc[b][f]]

    def lower_frames(self, a, b):
        return [f for f in range(len(self.dim)) if self.inc[f][a] and self.inc[f][b]]


def trace(word, sections, frames):
    n = 2 * word['v'] + word['R']
    contacts = [[] for _ in range(n)]
    offset = {}
    pos = 0
    cur = list(word['start'])
    for name in ('D', 'A', 'B', 'C'):
        offset[name] = pos
        for e in sections[name]:
            f = e[-1]
            for r in e[1:3]:
                if not frames.nested(cur[r], f):
                    raise ValueError(('initial nonmonotone path', name, r, cur[r], f))
                contacts[r].append((2 * pos + 1, f))
                cur[r] = f
            pos += 1
        if name == 'A':
            # A mutation must reach each paid COPY at its actual existing frame.
            for r in word['ret']:
                contacts[r].append((2 * pos + 1, cur[r]))
            pos += 1
    for r, f in enumerate(word['final']):
        contacts[r].append((2 * pos + 1, f))
    return offset, contacts


def profile(start, contacts, frames):
    paid = Counter()
    cur = start
    for _, f in sorted(contacts):
        if not frames.nested(cur, f):
            raise ValueError('nonmonotone')
        jump = frames.dim[f] - frames.dim[cur]
        if jump:
            paid[jump] += 1
        cur = f
    return paid


def actual_profile(word, checker):
    cur = list(word['start'])
    out = Counter()
    for name in ('D', 'A', 'B', 'C'):
        for f, d, ss in word[name]:
            for r in [d] + ss:
                assert checker.nested(cur[r], f)
                jump = checker.fdim[f] - checker.fdim[cur[r]]
                if jump:
                    out[jump] += 1
                cur[r] = f
        if name == 'A':
            out.update(checker.fdim[cur[r]] for r in word['ret'])
    for r, f in enumerate(word['final']):
        assert checker.nested(cur[r], f)
        jump = checker.fdim[f] - checker.fdim[cur[r]]
        if jump:
            out[jump] += 1
    return out


def build(word, sections, name, drops, lo, hi, dst, src, entry, exit_):
    out = deepcopy(word)
    gates = []
    for i in range(len(sections[name]) + 1):
        if i == lo:
            gates.append([entry, dst, [src]])
        if i == hi:
            gates.append([exit_, dst, [src]])
        if i < len(sections[name]) and i not in drops:
            e = sections[name][i]
            gates.append([e[-1], e[1], [e[2]]])
    out[name] = gates
    # Preserve the literal all-dirty cleanup interface, including every new gate.
    v = word['v']
    out['C'] = [[1, d, list(ss)] for sec in ('A', 'B')
                for _, d, ss in out[sec] if not v <= d < 2 * v][::-1]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word', type=Path, default=DEFAULT_SOURCE / 'data/r0042/R437-COMPOSED-WORD.json.gz')
    ap.add_argument('--checker', type=Path, default=DEFAULT_SOURCE / 'vendor/xcheck_p.py')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--section', choices=('A', 'B'), required=True)
    ap.add_argument('--transpose', action='store_true')
    ap.add_argument('--max-gap', type=int, default=100000)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--limit', type=int, default=1000000)
    ap.add_argument('--endpoint', type=float, default=0.001736738651088946)
    args = ap.parse_args()
    word = read(args.word)
    module = load_checker(args.checker)
    checker = module.Word(word)
    assert checker.FULL == 1
    checker.full()
    initial_interface, conclusion, _ = checker.interface()
    assert all(initial_interface.values())
    sections = flatten(word)
    frames = Frames(word, checker)
    offset, contacts = trace(word, sections, frames)
    keys = [[i for i, f in row] for row in contacts]
    old = [profile(word['start'][r], contacts[r], frames) for r in range(checker.n)]
    old_profile = actual_profile(word, checker)
    ces = transpose(sections[args.section]) if args.transpose else sections[args.section]
    groups, reads, writes = pair_catalog(ces, args.max_gap)
    indexed = [(ar, br, chosen, lo, hi)
               for (ar, br, q, ae, be), pairs in groups.items()
               for chosen, lo, hi in clusters(pairs, ar, br, reads, writes)]
    args.out.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    positives = []
    t0 = time.monotonic()
    print('INDEXED', len(indexed), 'local profile', dict(old_profile), flush=True)
    for index, (ar, br, chosen, clo, chi) in enumerate(indexed):
        if not args.start <= index < args.start + args.limit:
            continue
        stats['attempted'] += 1
        if args.transpose:
            lo, hi = len(ces) - chi, len(ces) - clo
            drops = {len(ces) - 1 - p['drop'] for p in chosen}
            dst, src = br, ar
        else:
            lo, hi = clo, chi
            drops = {p['drop'] for p in chosen}
            dst, src = ar, br
        if not word['v'] <= dst < 2 * word['v'] and word['v'] <= src < 2 * word['v']:
            stats['target_to_nontarget_rejected'] += 1
            continue
        start_key = 2 * (offset[args.section] + lo)
        end_key = 2 * (offset[args.section] + hi)
        before = {}
        after = {}
        for r in (ar, br):
            i = bisect_left(keys[r], start_key)
            before[r] = contacts[r][i-1][1] if i else word['start'][r]
            j = bisect_left(keys[r], end_key)
            after[r] = contacts[r][j][1]
        entry_frames = frames.upper_frames(before[ar], before[br])
        exit_frames = frames.lower_frames(after[ar], after[br])
        affected = {ar, br}
        affected.update(r for i in drops for r in sections[args.section][i][1:3])
        removed_keys = {2 * (offset[args.section] + i) + 1 for i in drops}
        stripped = {r: [p for p in contacts[r] if p[0] not in removed_keys] for r in affected}
        # Every inherited interior frame bounds the two new gates.  Prune before
        # evaluating the exact resulting rank itinerary.
        interior = {r: [f for i, f in stripped[r] if start_key < i < end_key] for r in (ar, br)}
        entry_frames = [g for g in entry_frames if all(frames.inc[g][f]
                         for r in (ar, br) for f in interior[r])]
        exit_frames = [h for h in exit_frames if all(frames.inc[f][h]
                        for r in (ar, br) for f in interior[r])]
        best = None
        for g in entry_frames:
            for h in exit_frames:
                if not frames.inc[g][h]:
                    continue
                stats['feasible_frame_assignments'] += 1
                delta = Counter()
                for r in affected:
                    row = stripped[r]
                    if r in (ar, br):
                        row = row + [(start_key, g), (end_key, h)]
                    new = profile(word['start'][r], row, frames)
                    delta.update(new)
                    delta.subtract(old[r])
                delta = {r: n for r, n in delta.items() if n}
                saving = -sum(n * r ** (1 - args.endpoint) for r, n in delta.items())
                if best is None or saving > best[0]:
                    best = saving, g, h, delta
        if best is None:
            stats['no_feasible_existing_frames'] += 1
        elif best[0] > 1e-10:
            saving, entry, exit_, delta = best
            new_word = build(word, sections, args.section, drops, lo, hi, dst, src, entry, exit_)
            actual = module.Word(new_word)
            actual.full()
            interface, conc, _ = actual.interface()
            if not all(interface.values()):
                stats['interface_rejected'] += 1
                continue
            paid = actual_profile(new_word, actual)
            exact_delta = paid.copy()
            exact_delta.subtract(old_profile)
            assert {r: n for r, n in exact_delta.items() if n} == delta
            assert sum(r * n for r, n in delta.items()) == 0
            ident = f"{args.section}-{'receiver' if args.transpose else 'source'}-{index}"
            payload = canonical(new_word)
            path = args.out / (ident + '.json.gz')
            path.write_bytes(gzip.compress(payload, mtime=0))
            info = dict(id=ident, index=index, section=args.section,
                        transpose=args.transpose, dst=dst, src=src,
                        scalar_lo=lo, scalar_hi=hi, removed_scalar_indices=sorted(drops),
                        entry_frame=entry, exit_frame=exit_, chosen=chosen,
                        local_delta=delta, local_profile=dict(paid),
                        floating_saving=saving, word=path.name,
                        canonical_sha256=sha256(payload).hexdigest(),
                        complete_dirty_columns=actual.n, interface=interface,
                        scope='EXACT_LOCAL_CANDIDATE_REQUIRES_NATIVE_AND_COMPLETE_HOSTED_INVOICE')
            positives.append(info)
            (args.out / (ident + '.json')).write_text(json.dumps(info, sort_keys=True, indent=2) + '\n')
            print('FOUND', json.dumps(info, sort_keys=True), flush=True)
        if stats['attempted'] % 100 == 0:
            print('PROGRESS', index, dict(stats), 'seconds', round(time.monotonic() - t0, 2), flush=True)
    result = dict(status='BOUNDED_EXACT_DIRTY_BIT_PAIR_EXISTING_FRAME_SEARCH',
                  source_word_sha256=sha256(args.word.read_bytes()).hexdigest(),
                  checker_sha256=sha256(args.checker.read_bytes()).hexdigest(),
                  script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  catalogue_sha256=sha256((FROZEN/'fanout_search.py').read_bytes()).hexdigest(),
                  section=args.section, transpose=args.transpose, max_gap=args.max_gap,
                  start=args.start, limit=args.limit, total_indexed=len(indexed),
                  stats=dict(stats), candidates=positives, baseline_profile=dict(old_profile),
                  frames='Existing 636 rational frames only; no joint lowering of inherited contacts',
                  elapsed_seconds=time.monotonic() - t0)
    (args.out/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('DONE', dict(stats), 'positive', len(positives), flush=True)


if __name__ == '__main__':
    main()
