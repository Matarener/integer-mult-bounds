"""tk surgery / extract: pull the dims-0..9 COLUMN of octet K out of a word.
usage: extract.py WORD --octet K|pool [--out COL.json.gz] [--members FILE.json] [--summary] [--no-fp]
       extract.py WORD --summary          (partition table of all 14 octets + POOL, exact invoice shares)
A column = a set of public registers (default: the OWNER partition of swlib.owners) + every event whose registers all lie in the set (INTERNAL, with
original program index t) + the INTERFACE (ADD/COPY events with exactly one end in the set, immutable positions t, with value fingerprints).
Frames are carried as a local table (basis lists, `fi` = index in the source word).  See module docstring for the file format."""
import sys, os, json, gzip, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swlib as S
C = S.C
SCHEMA = 'p104-surgery-column/1'

def kappa_of(w):
    rep = C.legal.check(w); T, P = C.X.invoice(rep)
    return str(C.X.kappa_dec(T, P, 50))[:20], rep

def extract(w, octet, members=None, path=None, R=None, own=None, why=None, fp=True):
    n = len(w['initial']); role = S.roles_of(w)
    if members is None:
        if own is None: own, why = S.owners(w, R)
        members = S.members(own, octet)
    M = set(members)
    if not M: raise SystemExit('extract: empty column')
    if any(r >= n for r in M): raise SystemExit('extract: owned registers cannot be column members (they are complement scratch)')
    klass = S.classify(w, M)
    ftab = []; fidx = {}
    def lf(gi):
        if gi not in fidx: fidx[gi] = len(ftab); ftab.append(dict(fi=gi, b=list(w['frames'][gi])))
        return fidx[gi]
    regs = {}
    ch = S.chains(w, M)
    for r in sorted(M):
        regs[str(r)] = dict(role=role(r), init=lf(w['initial'][r]), final=lf(w['final'][r]), dims=ch[r], tax=round(S.tax(ch[r]), 4), why=(why or {}).get(r, 'given'))
    events = []; iface = []
    ts_if = [t for t, k in klass.items() if k != 'int']
    fps = S.trace(w, ts_if) if fp else {}; xs = S.xparts(w, ts_if)
    for t, e in enumerate(w['program']):
        k = klass.get(t)
        if k == 'int':
            ev = list(e)
            for i in S.framefields(e): ev[i] = lf(e[i])
            events.append([t, 0, ev])
        elif k:
            d, s = e[1], e[2]; c, x = (d, s) if k == 'in' else (s, d)
            iface.append(dict(t=t, kind=k, op=e[0], col=str(c), ext=x, ext_role=role(x), q=e[3], frame=lf(e[4]),
                              fp=list(fps.get(t, ())), x=xs.get(t)))
    share = S.invoice_share(w, M); kp = S.kappa_probe(w, share)
    kap, rep = kappa_of(w)
    inv = dict(public=n, owned=C.legal.nown(w), lifetimes=rep.get('lifetimes'), peak=rep.get('owned_peak'), events=len(w['program']))
    return dict(schema=SCHEMA, octet=octet, policy='owner' if members is not None and own is not None else 'given',
                source=dict(path=path, canon_sha=S.canon_sha(w), kappa=kap, profile=C.profile_of(w)[0], inventory=inv, n_events=len(w['program'])),
                orig_members=sorted(M), pinned=S.PINNED, frames=ftab, regs=regs, events=events, interface=iface,
                accounting=dict(share, kappa_probe=kp, iface_in=sum(1 for i in iface if i['kind'] == 'in'), iface_out=sum(1 for i in iface if i['kind'] == 'out'),
                                iface_owned=sum(1 for i in iface if i['ext_role'] == 'O'), internal_events=len(events)),
                notes='events: [t, sub, event]; register fields = source ids (ints) or new names (strings); frames = local table indices. interface entries are immutable in position (t)')

def summary(w, R=None):
    """partition table: per octet registers by role, internal/interface event counts, exact invoice slice; disjointness/coverage assertions"""
    R = R or S.census(w); own, why = S.owners(w, R); n = len(w['initial'])
    rows = []; tot_int = 0
    for k in list(range(14)) + [S.POOL]:
        M = set(S.members(own, k)); kl = S.classify(w, M); sh = S.invoice_share(w, M)
        c = collections.Counter(kl.values()); rc = collections.Counter(S.roles_of(w)(r) for r in M)
        rows.append(dict(octet=k, regs=len(M), X=rc['X'], Y=rc['Y'], H=rc['H'], internal=c['int'], iface_in=c['in'], iface_out=c['out'], R0=sh['R0_model'], paid=sum(sh['paid'].values())))
        tot_int += c['int']
    # partition property: every public register has exactly one owner; internal events of different columns are disjoint by construction
    assert len(own) == n and sorted(own) == list(range(n))
    cross = sum(1 for e in w['program'] if len({own[x] for x in S.regfields(e) if x < n}) > 1)
    return dict(rows=rows, why=dict(collections.Counter(why.values())), internal_total=tot_int, cross_column_events=cross, events=len(w['program']),
                owned_only=sum(1 for e in w['program'] if all(x >= n for x in S.regfields(e))))

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('--octet'); ap.add_argument('--out')
    ap.add_argument('--members', help='JSON list of register ids (overrides the owner partition)'); ap.add_argument('--summary', action='store_true'); ap.add_argument('--no-fp', action='store_true')
    a = ap.parse_args(argv); path, w = S.load_word(a.word)
    if a.summary or a.octet is None:
        s = summary(w); print('%-6s %5s %4s %4s %4s %9s %6s %6s %9s %6s' % ('octet', 'regs', 'X', 'Y', 'H', 'internal', 'in', 'out', 'R0model', 'paid'))
        for r in s['rows']: print('%-6s %5d %4d %4d %4d %9d %6d %6d %9.1f %6d' % ('pool' if r['octet'] < 0 else r['octet'], r['regs'], r['X'], r['Y'], r['H'], r['internal'], r['iface_in'], r['iface_out'], r['R0'], r['paid']))
        print('owner rules', s['why'], '| events', s['events'], 'internal in columns', s['internal_total'], 'cross-column', s['cross_column_events'], 'owned-only', s['owned_only'])
        if a.octet is None: return 0
    k = S.POOL if a.octet == 'pool' else int(a.octet)
    mem = json.load(open(a.members)) if a.members else None
    col = extract(w, k, members=mem, path=path, fp=not a.no_fp)
    out = a.out or '%s.oct%s.col.json.gz' % (os.path.basename(path).split('.')[0], a.octet)
    with gzip.open(out, 'wt', compresslevel=6) as f: json.dump(col, f)
    ac = col['accounting']
    print('column octet %s: %d regs (%s), %d internal events, interface in %d / out %d (owned %d)  -> %s' % (a.octet, len(col['regs']), dict(collections.Counter(r['role'] for r in col['regs'].values())), ac['internal_events'], ac['iface_in'], ac['iface_out'], ac['iface_owned'], out))
    print('R0 share (MODEL tax) %.2f   invoice slice paid %s helpers %s   kappa %s -> %.6g if R0 share 1%% cheaper (R0-law MODEL)' % (ac['R0_model'], ac['paid'], ac['helpers'], col['source']['kappa'], ac['kappa_probe']['kappa_if_R0_cheaper']))
    return 0
if __name__ == '__main__': sys.exit(main())
