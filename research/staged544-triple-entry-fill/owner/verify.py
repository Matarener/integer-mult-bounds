"""Independent literal owner audit for the staged-entry providers (helpers 608, 609, 600 narrowed 8 -> 7).

The role walk is PR3945's owner/verify.py walk unchanged (window/family semantics of the retained PR3734 owner audit
and its credited PR3638 predicates).  Widths are read directly from the final canonical words.  Unlike PR3945, roles
do move: 70,876 of 1,321,920 roles change (owner, child, port) relative to PR3945's literal fill; every moved role is
checked by the same predicates as every other role.
Prepared by Rohan Arun with Anthropic Claude assistance (walk: Dugongue with OpenAI Codex assistance). Apache-2.0.
"""
from pathlib import Path
from collections import Counter, defaultdict
import json, gzip, hashlib, time, sys
ROOT = Path(__file__).resolve().parent; PACKAGE = ROOT.parent; IN = ROOT / 'inputs'
NEW_IDLE = {3: 22842, 5: 1890, 48: 138438}
PR3945_IDLE = {3: 23328, 5: 4320, 48: 137952}
LOCAL = {1: 2488, 2: 714, 3: 223, 4: 102, 5: 20, 8: 8}
INVENTORY = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}


def need(ok, why):
    if not ok: raise ValueError(why)
def read(path):
    raw = path.read_bytes(); return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dimension(rows):
    pivots = {}
    for vector in rows:
        while vector:
            leading = vector.bit_length()
            if leading not in pivots: pivots[leading] = vector; break
            vector ^= pivots[leading]
    return len(pivots)
def canonical_widths(word, origin):
    full = [1 << i for i in range(9)]
    return [dimension(word['helper_final'].get(str(r), full)) - dimension(word['start_extra'].get(str(r), [])) for r in origin]


def main():
    begin = time.monotonic(); T = 360; N = 9 * T
    pins = read(ROOT / 'SOURCES.json')['files']
    for rel, digest in pins.items(): need(sha(ROOT / rel) == digest, 'source hash mismatch: ' + rel)
    fill = read(ROOT / 'FILL.json.gz'); oldfill = read(IN / 'PR3945-FILL.json.gz')
    order = read(IN / 'ORDER.json'); dispatch = read(IN / 'DISPATCH.json')
    need(len(order) == N and set(map(tuple, order)) == {(s, r) for s in range(9) for r in range(T)}, 'call coverage')
    clock = {tuple(call): t for t, call in enumerate(order)}
    need(all(all(clock[s, r] < clock[s + 1, r] for s in range(8)) for r in range(T)), 'per-replica source chronology')
    provider = {(s, r): tag for s, r, tag in dispatch}
    need(len(provider) == len(dispatch) == N and set(provider) == set(clock), 'dispatch coverage')
    template = read(IN / 'TEMPLATE.json.gz'); plan = read(IN / 'PLAN.json.gz')
    children = {row['child']: row['rank'] for row in template['idle_children']}; K = max(children) + 1
    pair = {row['stage']: row['pair'] for row in template['recipe'] if row['kind'] == 'local'}
    windows = {}
    for owner in range(T):
        touched = {}; tick = None
        for event in template['execution_schedule']:
            kind = event['kind']
            if kind in ('bank_padding_cover_sweep', 'translate_every_live_family'): continue
            if kind == 'local_cover_sweep': tick = clock[event['stage'], owner]; touched[pair[event['stage']]] = tick
            elif kind == 'bridge':
                need(tick is not None, 'bridge source'); touched[event['src']] = tick; touched[event['dst']] = tick
            elif kind == 'idle_cover_sweep':
                need(tick is not None, 'idle source')
                for child in event['child_indices']:
                    if child in children:
                        need((owner, child) not in windows, 'repeated owner child')
                        windows[owner, child] = (children[child], touched.get(event['pair'], -1), tick)
            else: need(kind in ('terminal_Y_translations', 'terminal'), 'unknown schedule event')
        need(all((owner, c) in windows for c in children), 'missing owner window')
    family = {c: 2 * plan['pairs'][str(c)] + plan['sides'][str(c)] for c in children}
    shared = defaultdict(list)
    for (o, c), (cap, lo, hi) in windows.items(): shared[o, family[c]].append((lo, hi))
    for intervals in shared.values():
        need(all(max(a, c) >= min(b, d) for j, (a, b) in enumerate(intervals) for c, d in intervals[j + 1:]), 'overlapping source-family windows')
    widths = {}; oldwidths = {}; local = {}; wordpins = {}
    for tag, pid in [('base', 'gauge44'), ('extra', 'extra')]:
        final_path = PACKAGE / 'inputs' / f'NEW-{tag}.json.gz'; old_path = PACKAGE / 'inputs' / f'OLD-{tag}.json.gz'
        word = read(final_path); oldword = read(old_path); origin = read(IN / f'old-NATIVE-{tag}.json.gz')['helper_origin']
        need(origin == sorted(set(range(224, 704)) - set(word['removed'])), 'helper origin changed')
        widths[pid] = canonical_widths(word, origin); oldwidths[pid] = canonical_widths(oldword, origin)
        need(Counter(widths[pid]) == INVENTORY, 'literal inventory')
        narrowed = [origin[h] for h in range(408) if widths[pid][h] != oldwidths[pid][h]]
        need(narrowed == [600, 608, 609] and all(oldwidths[pid][h] - widths[pid][h] == 1 for h in range(408) if widths[pid][h] != oldwidths[pid][h]), 'exactly helpers 600, 608, 609 narrowed by one')
        local[pid] = {int(r): n for r, n in word['report']['local_profile'].items()}
        need(local[pid] == LOCAL, 'literal local profile')
        wordpins[tag] = sha(final_path)
    rows = fill['rows']; oldrows = oldfill['rows']
    need(fill['columns'] == oldfill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'] and fill['dispatch_overrides'] == oldfill['dispatch_overrides'] == [], 'fill schema')
    need(len(rows) == len(oldrows) == N * 408, 'role coverage')
    def walk(data, charges):
        used = {}; families = set()
        for j, row in enumerate(data):
            need(len(row) == 6 and all(type(x) is int for x in row), 'noninteger owner role')
            t, h, o, c, p, z = row; need(t == j // 408 and h == j % 408, 'ordered helper identity')
            if h == 0: families = set()
            need((o, c) in windows and 0 <= p < 112, 'owner child/port range')
            cap, lo, hi = windows[o, c]; need(lo < t <= hi, 'owner chronology')
            f = o * 896 + family[c] * 112 + p
            need(f not in families, 'same-call family distinctness'); families.add(f)
            key = (o * K + c) * 112 + p; prefix = used.get(key, 0)
            need(z == prefix, 'compact chronological prefix')
            width = charges[provider[tuple(order[t])]][h]
            need(z + width <= cap, 'owner capacity')
            used[key] = prefix + width
        idle = Counter()
        for (o, c), (cap, lo, hi) in windows.items():
            for p in range(112):
                left = cap - used.get((o * K + c) * 112 + p, 0); need(left >= 0, 'negative bin idle')
                if left: idle[left] += 1
        return used, idle
    oldused, oldidle = walk(oldrows, oldwidths); newused, newidle = walk(rows, widths)
    need(oldidle == Counter(PR3945_IDLE), 'PR3945 idle source')
    need(newidle == Counter(NEW_IDLE), 'new idle exact')
    moved = sum(1 for a, b in zip(rows, oldrows) if a[:5] != b[:5])
    need(all(a[:2] == b[:2] for a, b in zip(rows, oldrows)), 'call/helper identities')
    profile = Counter(newidle)
    for call in order: profile.update(local[provider[tuple(call)]])
    need(dict(profile) == {int(r): n for r, n in read(ROOT / 'PROFILE.json').items()}, 'global paid histogram')
    need(sum(r * n for r, n in profile.items()) == 65088 * T, 'mass deficit')
    controls = []
    def reject(label, fragment, mutate, restore):
        mutate()
        try:
            try: walk(rows, widths)
            except ValueError as e: need(fragment in str(e), 'wrong rejection for ' + label); controls.append(label)
            else: raise ValueError(label + ' mutant accepted')
        finally: restore()
    saved = list(rows[1]); reject('same_call_family', 'same-call family', lambda: rows[1].__setitem__(slice(2, 5), rows[0][2:5]), lambda: rows[1].__setitem__(slice(None), saved))
    reject('offset_hole', 'compact chronological', lambda: rows[0].__setitem__(5, rows[0][5] + 1), lambda: rows[0].__setitem__(5, rows[0][5] - 1))
    saved0 = list(rows[0]); bad = next((o, c) for (o, c), (cap, lo, hi) in windows.items() if lo >= 0)
    reject('closed_owner_window', 'owner chronology', lambda: rows[0].__setitem__(slice(2, 4), list(bad)), lambda: rows[0].__setitem__(slice(None), saved0))
    firsttag = provider[tuple(order[0])]; savedw = widths[firsttag][0]
    reject('overflow', 'owner capacity', lambda: widths[firsttag].__setitem__(0, windows[rows[0][2], rows[0][3]][0] + 1), lambda: widths[firsttag].__setitem__(0, savedw))
    # restoring any narrowed helper's old width (offsets regenerated) must overflow some exactly packed bin
    for h in [h for h in range(408) if widths['gauge44'][h] != oldwidths['gauge44'][h]]:
        trial = {pid: list(widths[pid]) for pid in widths}
        for pid in trial: trial[pid][h] = oldwidths[pid][h]
        relaid = [list(r) for r in rows]; acc = defaultdict(int)
        for r in relaid:
            key = (r[2], r[3], r[4]); r[5] = acc[key]; acc[key] += trial[provider[tuple(order[r[0]])]][r[1]]
        try: walk(relaid, trial)
        except ValueError as e: need('owner capacity' in str(e), 'wrong rejection for restored width'); controls.append(f'restored_width_helper_index_{h}')
        else: raise ValueError('restored width accepted')
    result = {'status': 'PASS_LITERAL_STAGED_ENTRY_OWNER_FILL', 'replicas': T, 'calls': N, 'roles': len(rows), 'owner_windows': len(windows), 'physical_bins': len(windows) * 112,
              'roles_moved_vs_pr3945': moved, 'idle': dict(sorted(newidle.items())), 'pr3945_idle': dict(sorted(oldidle.items())), 'profile': dict(sorted(profile.items())),
              'controls_rejected': controls, 'fill_sha256': sha(ROOT / 'FILL.json.gz'), 'final_word_sha256': wordpins, 'checker_sha256': sha(Path(__file__)), 'seconds': time.monotonic() - begin,
              'scope': 'Exact full owner role, chronology, distinctness, capacity, compact-prefix and paid histogram audit of both PR3945 and the new literal fill. Native/caller/outer admission handled separately.'}
    if '--record' in sys.argv: (ROOT / 'CHECK.json').write_text(json.dumps(result, indent=2), encoding='utf8')
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__': main()
