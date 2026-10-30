"""Build the literal staged-entry RECORD from PR3945's NEW word and the staged word (provenance tool)."""
import sys, json, gzip, difflib
sys.path.insert(0, '/home/claude/pkg'); sys.path.insert(0, '/home/claude/adm/prep3945/inputs/source/new/borrow')
import staged_entries_applier as S

def slices(old, new):
    sm = difflib.SequenceMatcher(a=[json.dumps(g) for g in old], b=[json.dumps(g) for g in new], autojunk=False)
    return [{'slice': [i1, i2], 'old': old[i1:i2], 'new': new[j1:j2]} for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal']

def record(parent, w, entries):
    r = {'schema': 'staged-entries-literal-v1', 'source_canonical_sha256': S.canonical(parent), 'target_canonical_sha256': S.canonical(w),
         'sections': {sec: slices(parent[sec], w[sec]) for sec in ('A', 'B', 'restore') if parent[sec] != w[sec]},
         'entrances': [{'helper': h, 'old': parent['start_extra'][h], 'new': w['start_extra'][h]} for h in sorted(w['start_extra'], key=int) if parent['start_extra'].get(h) != w['start_extra'][h]],
         'warps': w['warps'], 'report': {k: w['report'][k] for k in ('local_profile', 'width_inventory')}, 'entries': entries}
    assert S.apply(parent, r) == w
    return r

if __name__ == '__main__':
    old, new, out = sys.argv[1:4]
    entries = json.loads(open(sys.argv[4]).read())
    r = record(json.load(gzip.open(old)), json.load(gzip.open(new)), entries)
    open(out, 'w').write(json.dumps(r, indent=1, sort_keys=True) + '\n')
    print('record', out, {s: len(v) for s, v in r['sections'].items()}, 'entrances', [(e['helper'], e['old'], e['new']) for e in r['entrances']])
