"""SURGPREP regress: extract -> splice round trip on the 6030 word reproduces it bit-exactly (canonical bytes, same kappa, 0 pin mismatches) for several octets of both
port orbits; relabelled/renumbered column (reversed id allocation) stays legal with identical kappa; shrink path (drop an idle pool helper, compaction) legal; negative control
(a deleted contentful column event) is rejected by legality/pins/law.  usage: surgery_test.py [--fast] [--full]  -> 'ALL PASS' / 'FAIL ...'"""
import sys, os, json, copy, gzip, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'surgery'))
import swlib as S, extract as X, splice as SP, validate as V
C = S.C
fails = []
def need(c, m):
    print(('ok   ' if c else 'FAIL ') + m, flush=True)
    if not c: fails.append(m)
def roundtrip(w, k, base_bytes):
    col = X.extract(w, k, path='6030'); col = json.loads(json.dumps(col))        # through JSON like the CLI file
    nw, info = SP.splice(w, col); v = SP.verify(w, nw, col, info)
    ok = (v['legal'] and v['identical'] and v['kappa_new'] == v['kappa_base'] and v['pins']['mismatched'] == 0 and info['identity_layout']
          and C.canonical_bytes(S.norm(nw), gz=False) == base_bytes)
    return ok, col, v
def main():
    fast = '--fast' in sys.argv; full = '--full' in sys.argv
    path, w = S.load_word('6030'); base_bytes = gzip.open(path).read(); t0 = time.time()
    need(C.canonical_bytes(S.norm(w), gz=False) == base_bytes, 'words/6030.json.gz is canonical (byte base of the round trip)')
    octs = [9, 11, 0] if fast else ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] if full else [9, 11, 0, 5, 13])
    cols = {}
    for k in octs + [S.POOL]:
        ok, col, v = roundtrip(w, k, base_bytes); cols[k] = col
        need(ok, 'round trip octet %s: %d regs, %d internal / %d interface events, bit-exact, kappa %s, pins %d/%d' % ('pool' if k < 0 else k, len(col['regs']), len(col['events']), len(col['interface']), v['kappa_new'], v['pins']['checked'] - v['pins']['mismatched'], v['pins']['checked']))
    # partition property
    s = X.summary(w)
    need(sum(r['regs'] for r in s['rows']) == len(w['initial']) and s['internal_total'] + s['cross_column_events'] + s['owned_only'] <= s['events'], 'partition: 14 octets + pool cover every public register once; internal/cross/owned-only events disjoint')
    # renumbered layout: same column, new names, reversed allocation order -> permuted ids, same instance (kappa, legality, pins)
    k = 9; col = copy.deepcopy(cols[k]); hs = [nm for nm in col['regs'] if int(nm) >= S.PINNED]
    ren = {nm: 'h%d' % i for i, nm in enumerate(hs)}
    for nm in hs: col['regs'][nm]['as'] = int(nm)          # the relabelled register carries the same input identity
    items = [(ren.get(nm, nm), sp) for nm, sp in col['regs'].items()]
    col['regs'] = dict([x for x in items if x[0] not in ren.values()] + [x for x in reversed(items) if x[0] in ren.values()])      # helpers in REVERSED file order -> permuted ids
    def rn(x): return ren.get(str(x), x) if str(x) in ren else x
    for t, sub, e in col['events']:
        for p in ((1, 2) if e[0] in ('ADD', 'COPY') else (1,)): e[p] = rn(e[p])
    for i in col['interface']: i['col'] = rn(i['col'])
    nw, info = SP.splice(w, col); v = SP.verify(w, nw, col, info)
    need(v['legal'] and v['kappa_new'] == v['kappa_base'] and v['pins']['mismatched'] == 0 and not v['identical'], 'relabelled column (reversed id allocation): permuted ids, legal, kappa identical, pins hold')
    # shrink: drop idle pool helper 743 (no interface) -> compaction of ids, owned ids shift, still inside the 6030 public bound [767,770]
    col = copy.deepcopy(cols[S.POOL]); del col['regs']['743']; col['events'] = [x for x in col['events'] if x[2][1] != 743]
    nw, info = SP.splice(w, col); v0 = SP.verify(w, nw, col, info); v = SP.verify(w, nw, col, info, retarget=True)
    need((not v0['legal']) and 'inventories' in v0['violations'][0][1] and v['legal'] and info['n_new'] == len(w['initial']) - 1 and info['holes_compacted'] == 1 and v['pins']['mismatched'] == 0 and v['paid_delta'] == {7: -1} and v['helpers_delta'] == {7: -1} and len(nw['program']) == len(w['program']) - 1,
         'shrink: drop idle helper 743 (compaction, %s): only the profile inventory pin (770) objects, legal with --retarget-inventory, 769 regs, idle helper is invoice-neutral (paid[7] and helpers[7] both -1, kappa unchanged)' % info['holes_compacted'])
    # negative control
    col = copy.deepcopy(cols[9]); j = next(i for i, x in enumerate(col['events']) if x[2][0] == 'ADD'); del col['events'][j]
    nw, info = SP.splice(w, col); v = SP.verify(w, nw, col, info)
    need((not v['legal']) or v['pins']['mismatched'] > 0, 'negative control: deleting one column ADD is caught (legal=%s, pin mismatches %d)' % (v['legal'], v['pins']['mismatched']))
    # validators on base word: 0 violations at every frame (law lo=8) and every JR chart, changed-frame restriction works
    colw, info0 = cols[9], None
    nw0, info0 = SP.splice(w, cols[9]); r = V.run(w, nw0, cols[9], info0)
    need(r['law_bad'] == 0 and r['jr_bad_new'] == 0 and r['law_n_new'] > 0 and r['jr_n_new'] > 0, 'validate: span law + JR on changed frames of the unchanged octet-9 splice: %s' % V.fmt(r).replace('\n', ' | '))
    print('%.0fs' % (time.time() - t0)); print('ALL PASS' if not fails else 'FAILS %d: %s' % (len(fails), fails)); return 1 if fails else 0
if __name__ == '__main__': sys.exit(main())
