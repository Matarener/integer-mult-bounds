"""tk surgery / splice: put a (possibly rebuilt) COLUMN back into its word, re-wire the interface, verify.
usage: splice.py WORD COLUMN.json[.gz] --octet K [--out NEW.json.gz] [--retarget-inventory] [--free-bounds] [--no-pins] [--allow-drift] [--validate]
Contract: the column file (extract.py) keeps the INTERFACE events at their original positions t; internal events carry sort keys [t, sub] (original t, or any
anchor with sub<0 to land just before the event at t, sub>0 just after); register names are source ids or new strings; frames are the local table.
Registers: members with id < 224 must remain; freed ids >= 224 are re-used by new registers (file order), extra new registers are appended after the last
public id (owned ids shift up), unfilled holes are compacted.  Unchanged column => word reproduced bit-exactly (same canonical bytes).
Checks: tk-check legality (profile of the BASE word pinned), exact kappa/side/budgets, interface pins (numeric value of every interface source before the
event == extraction), register/lifetime/peak inventory deltas (the adopted profile pins them: a changed public count is flagged by the 'Complete public and owned inventories' rule; --retarget-inventory judges it against the new count, --free-bounds relaxes the ranges only)."""
import sys, os, json, gzip, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swlib as S
C = S.C

def load_column(p):
    return json.load(gzip.open(p, 'rt')) if p.endswith('.gz') else json.load(open(p))

def _is_id(name): return str(name).lstrip('-').isdigit()

def splice(w, col, allow_drift=False):
    """-> (new word, info).  Pure: w is not modified.  Raises SystemExit on a malformed column."""
    n = len(w['initial']); NO = C.legal.nown(w); PIN = col.get('pinned', S.PINNED)
    for k in ('retired_public', 'independent_public', 'owned_roles', 'fields'):
        if k in w: raise SystemExit('splice: word carries %r (register-id keyed); not supported' % k)
    if col['source']['canon_sha'] != S.canon_sha(w) and not allow_drift: raise SystemExit('splice: column was extracted from a different word (canon sha); --allow-drift to override')
    M0 = set(col['orig_members']); regs = col['regs']
    names = list(regs)
    for nm in names:
        if _is_id(nm) and int(nm) not in M0: raise SystemExit('splice: register %s is not a member of the extracted column' % nm)
    for r in M0:
        if r < PIN and str(r) not in regs: raise SystemExit('splice: pinned register %d (main/slot < %d) cannot be removed' % (r, PIN))
    new_names = [nm for nm in names if not _is_id(nm)]
    # ---- id layout
    slots = []; holes = 0; it = iter(new_names); placed = {}
    for r in range(PIN, n):
        if r not in M0 or str(r) in regs: slots.append(('keep', r))
        else:
            nm = next(it, None)
            if nm is None: holes += 1
            else: slots.append(('new', nm))
    for nm in it: slots.append(('new', nm))
    name2new = {str(r): r for r in range(PIN) if str(r) in regs}
    old2new = {r: r for r in range(PIN)}
    for i, (kind, x) in enumerate(slots):
        if kind == 'keep': old2new[x] = PIN + i; name2new.setdefault(str(x), PIN + i) if str(x) in regs else None
        else: name2new[x] = PIN + i
    newn = PIN + len(slots)
    for j in range(NO): old2new[n + j] = newn + j
    ident = newn == n and all(old2new.get(r, r) == r for r in range(n + NO))   # ids of every surviving register unchanged (new registers may still be permuted)
    # ---- frames
    frames = [list(b) for b in w['frames']]; first = {}
    for i, b in enumerate(frames): first.setdefault(tuple(b), i)
    fmap = []
    for ent in col['frames']:
        b = list(ent['b']); fi = ent.get('fi')
        if fi is not None and fi < len(frames) and frames[fi] == b: fmap.append(fi)
        elif tuple(b) in first: fmap.append(first[tuple(b)])
        else: frames.append(b); first[tuple(b)] = len(frames) - 1; fmap.append(len(frames) - 1)
    # ---- program
    def nm2id(x):
        k = str(x)
        if k not in name2new: raise SystemExit('splice: unknown register name %r in a column event' % (x,))
        return name2new[k]
    keyed = []
    cls = S.classify(w, M0); iface = {i['t']: i for i in col['interface']}
    for t, e in enumerate(w['program']):
        k = cls.get(t)
        if k == 'int': continue
        if k:
            i = iface.get(t)
            if i is None: raise SystemExit('splice: interface event t=%d missing from the column' % t)
            if not allow_drift:
                c_old, x_old = (e[1], e[2]) if k == 'in' else (e[2], e[1])
                if str(c_old) != i['col'] and i['col'] not in regs: raise SystemExit('splice: interface t=%d column register %s no longer present' % (t, i['col']))
            c, x = nm2id(i['col']), old2new[i['ext']]
            ev = [i['op'], c, x, i['q'], fmap[i['frame']]] if i['kind'] == 'in' else [i['op'], x, c, i['q'], fmap[i['frame']]]
            keyed.append(((t, 0), ev, t)); continue
        ev = list(e)
        for pos in (1, 2) if e[0] in ('ADD', 'COPY') else (1,): ev[pos] = old2new[e[pos]]
        keyed.append(((t, 0), ev, None))
    nint = 0
    for t, sub, e in col['events']:
        ev = list(e)
        for pos in (1, 2) if ev[0] in ('ADD', 'COPY') else (1,): ev[pos] = nm2id(ev[pos])
        for pos in S.framefields(ev): ev[pos] = fmap[ev[pos]]
        keyed.append(((t, sub), ev, None)); nint += 1
    keyed.sort(key=lambda z: z[0])        # stable: complement/interface events precede column events with an equal key
    prog = [z[1] for z in keyed]; if_pos = {z[2]: j for j, z in enumerate(keyed) if z[2] is not None}
    # ---- arrays
    init = [None] * newn; fin = [None] * newn
    for r in range(n):
        if r in M0: continue
        init[old2new[r]] = w['initial'][r]; fin[old2new[r]] = w['final'][r]
    for nm, spec in regs.items():
        i = name2new[nm]; init[i] = fmap[spec['init']]; fin[i] = fmap[spec['final']]
    assert all(x is not None for x in init + fin)
    nw = {}
    for k, v in w.items(): nw[k] = v
    nw['frames'] = frames; nw['initial'] = init; nw['final'] = fin; nw['program'] = prog
    if w.get('public') == n: nw['public'] = newn
    keys = [None] * (newn + NO); bk = S.reg_keys(w)
    for r in range(n + NO):
        if r not in M0: keys[old2new[r]] = bk[r]
    for nm, spec in regs.items():
        keys[name2new[nm]] = ('p%d' % spec['as'] if spec.get('as') is not None else (bk[int(nm)] if _is_id(nm) else 'n:%s' % nm))
    info = dict(keys=keys, identity_layout=ident, n_old=n, n_new=newn, holes_compacted=holes, new_regs=len(new_names), removed_regs=len([r for r in M0 if str(r) not in regs]),
                frames_added=len(frames) - len(w['frames']), events_old=len(w['program']), events_new=len(prog), internal_events=nint,
                iface_pos=if_pos, name2new=name2new, old2new=old2new)
    return nw, info

def verify(w, nw, col, info, pins=True, free_bounds=False, retarget=False):
    """legality (tk check oracle, base profile pinned), exact price, interface pins, inventory deltas.  -> dict"""
    pname = C.profile_of(w)[0]; out = dict(profile=pname)
    def run(word):
        with C.use_profile(pname):
            if free_bounds:
                with S.free_bounds_env(): rep = C.legal.check(word)
            else: rep = C.legal.check(word)
            T, P = C.X.invoice(rep); kd = C.X.kappa_dec(T, P, 50)
            side = C.side_of(T, P, C.profile_of(word, override=pname)[1])
            return rep, kd, side, C.X.budgets(rep)
    rb, kb, sb, bb = run(w)
    # retarget: the adopted profile pins the PUBLIC count exactly (profile 6030: 770); a column with a different register count is judged against its own count
    # (the literal a shipping package would retarget, cf. shipcheck); everything else in the profile stays pinned.
    nwc = dict(nw, verifier_profile=dict(nw.get('verifier_profile') or {}, public=len(nw['initial']))) if retarget else nw
    rn, kn, sn, bn = run(nwc)
    out.update(legal=rn['ok'], violations=[tuple(map(str, v)) for v in rn['violations'][:8]], kappa_base=str(kb)[:20], kappa_new=str(kn)[:20], dkappa=float(kn - kb),
               side_ok=sn['ok'], side=dict(alpha=sn['alpha'], gamma=sn['gamma'], delta=sn['delta']), event_slack=bn['event_slack'], scalar_slack=bn['scalar_budget_slack'],
               inventory=dict(public=(len(w['initial']), len(nw['initial'])), events=(len(w['program']), len(nw['program'])), lifetimes=(rb.get('lifetimes'), rn.get('lifetimes')),
                              peak=(rb.get('owned_peak'), rn.get('owned_peak'))),
               paid_delta={d: rn['paid'].get(d, 0) - rb['paid'].get(d, 0) for d in set(rn['paid']) | set(rb['paid']) if rn['paid'].get(d, 0) != rb['paid'].get(d, 0)},
               helpers_delta={d: rn['helpers'].get(d, 0) - rb['helpers'].get(d, 0) for d in set(rn['helpers']) | set(rb['helpers']) if rn['helpers'].get(d, 0) != rb['helpers'].get(d, 0)})
    out['identical'] = S.norm(nw) == S.norm(w) and C.canonical_bytes(S.norm(nw), gz=False) == C.canonical_bytes(S.norm(w), gz=False)
    if pins:
        ts = [info['iface_pos'][i['t']] for i in col['interface']]
        got = S.trace(nw, ts, info['keys']); gx = S.xparts(nw, ts); badx = []; bads = []
        for i in col['interface']:
            j = info['iface_pos'][i['t']]
            if i.get('x') != 'owned' and gx[j] != i['x']: badx.append(i['t'])
            if i['fp'] and list(got[j]) != i['fp']: bads.append(i['t'])
        out['pins'] = dict(checked=len(ts), mismatched=len(badx), first=badx[:10], strict_mismatched=len(bads),
                           note='mismatched = x-part (port content) of an interface source differs; strict = full numeric value incl. junk/owned (a rebuilt column may legitimately change junk)')
    return out

def report(v, info):
    L = ['profile %s | legal: %s %s' % (v['profile'], 'YES' if v['legal'] else 'NO', v['violations'][:4] if not v['legal'] else ''),
         'kappa base %s  new %s  (d %+.4g) | side %s | event slack %d' % (v['kappa_base'], v['kappa_new'], v['dkappa'], 'ok' if v['side_ok'] else 'FAIL', v['event_slack']),
         'layout: %s; regs %d -> %d (new %d, removed %d, holes compacted %d); frames added %d; events %d -> %d' % ('identity' if info['identity_layout'] else 'RENUMBERED', info['n_old'], info['n_new'], info['new_regs'], info['removed_regs'], info['holes_compacted'], info['frames_added'], info['events_old'], info['events_new']),
         'inventory (base,new): %s' % v['inventory'], 'invoice delta: paid %s helpers %s' % (v['paid_delta'], v['helpers_delta'])]
    if 'pins' in v: L.append('interface pins (x-part): %d checked, %d mismatched %s; strict full-value mismatches %d' % (v['pins']['checked'], v['pins']['mismatched'], v['pins']['first'], v['pins']['strict_mismatched']))
    L.append('bit-identical to the base word: %s' % v['identical'])
    return '\n'.join(L)

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('column'); ap.add_argument('--octet'); ap.add_argument('--out')
    ap.add_argument('--free-bounds', action='store_true'); ap.add_argument('--retarget-inventory', action='store_true', help='judge the public-register pin against the new count'); ap.add_argument('--no-pins', action='store_true'); ap.add_argument('--allow-drift', action='store_true')
    ap.add_argument('--validate', action='store_true', help='also run validate.py (SPAN5 law + JR) on the changed frames')
    a = ap.parse_args(argv); path, w = S.load_word(a.word); col = load_column(a.column)
    if a.octet is not None and str(col['octet']) != str(-1 if a.octet == 'pool' else a.octet): raise SystemExit('splice: column is octet %s, --octet %s' % (col['octet'], a.octet))
    nw, info = splice(w, col, a.allow_drift); v = verify(w, nw, col, info, pins=not a.no_pins, free_bounds=a.free_bounds, retarget=a.retarget_inventory)
    print(report(v, info))
    if a.out:
        C.save_canonical(S.norm(nw), a.out); print('wrote', a.out)
        if info['n_new'] != info['n_old']: print('NOTE: register count changed; run tk with TK_PROFILE=%s (the family lookup keys on the public count)' % v['profile'])
    if a.validate:
        import validate; rv = validate.run(w, nw, col, info); print(validate.fmt(rv))
        if rv['law_bad'] or rv['jr_bad_new'] > rv['jr_bad_base']: return 3
    ok = v['legal'] and v['side_ok'] and (a.no_pins or v['pins']['mismatched'] == 0)
    return 0 if ok else 2
if __name__ == '__main__': sys.exit(main())
