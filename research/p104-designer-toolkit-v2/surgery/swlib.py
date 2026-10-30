"""SURGPREP shared library (toolkit/surgery): partition of a word into octet columns, interface classification, exact invoice slices,
numeric value fingerprints.  Pure functions; nothing is set in os.environ at import (tkcommon is imported for load/canonical dump only).
Conventions (P104 words): registers 0..n-1 public (X mains = live, Y mains = live+112, the rest helpers), n.. owned scratch (INIT/CLEAR lifetimes).
Event tuples: MOVE r a b pv | ADD d s q f | COPY d s q f | SCALE r q f | INIT r f | CLEAR r f   (f, a, b = frame indices)."""
import os, sys, io, gzip, json, math, pickle, random, hashlib, tempfile, contextlib, collections
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0, TK)
import tkcommon as C
W = TK
MODP = (1 << 61) - 1
PINNED = 224                  # ids < 224: X mains (r), Y mains (r+112) and the non-live main slots; never renumbered, never deleted
PAIRS = [(0, 27), (1, 26), (2, 3), (4, 5), (6, 17), (7, 16), (8, 25), (9, 22), (10, 24), (11, 23), (12, 15), (13, 14), (18, 21), (19, 20)]
POOL = -1                     # the SHARED bucket (registers with no octet evidence); extract with --octet pool

def load_word(spec):
    """-> (path, word) through tkcommon (alias or path); activates the word's data profile (runtime, not import time)"""
    return C.load(spec)
def canon_sha(w):
    """sha256 of the canonical (sorted keys, normalised flags) dump of a word; identical words (any file format) have identical sha"""
    return hashlib.sha256(C.canonical_bytes(json.loads(json.dumps(w)), gz=False)).hexdigest()
def norm(w):
    """deep copy through JSON with MOVE private flags as bool (tkcommon.normalise_flags): the form two words are compared in"""
    return C.normalise_flags(json.loads(json.dumps(w)))

def is_move(e): return e[0] == 'MOVE'
def regfields(e):
    """event -> register ids it touches: MOVE/SCALE/INIT/CLEAR (r,), ADD/COPY (d, s)"""
    return (e[1], e[2]) if e[0] in ('ADD', 'COPY') else (e[1],)
def framefields(e):
    """(index positions in the event tuple that hold frame indices)"""
    return (2, 3) if e[0] == 'MOVE' else (len(e) - 1,)

def roles_of(w):
    n = len(w['initial']); live = set(w['live']); ret = set(w.get('retired_public') or [])
    def role(r):
        if r >= n or r in ret: return 'O'
        if r in live: return 'X'
        if r - 112 in live: return 'Y'
        return 'H'
    return role

# ----------------------------------------------------------------------------------------- octets / census / ownership
def octet_table():
    """port index (position in live) -> octet 0..13 (QUADHUB T=384 pairs of the SUBOPT clus_7 D3-coset groups)"""
    cl = pickle.load(open(HERE + '/data/clus_7.pkl', 'rb'))['cls']
    oc = {}
    for k, (a, b) in enumerate(PAIRS):
        for c in cl[a] + cl[b]: oc[c] = k
    return oc
def census(w, workdir=None):
    """SUBOPT census (cen.run) of word w, quiet; returns the census dict R"""
    for p in (HERE,):
        if p not in sys.path: sys.path.insert(0, p)
    import cen
    fd, tmp = tempfile.mkstemp(suffix='.pkl', dir=workdir); os.close(fd)
    try:
        with contextlib.redirect_stdout(io.StringIO()): cen.run(w, tmp)
        return pickle.load(open(tmp, 'rb'))
    finally:
        try: os.remove(tmp)
        except OSError: pass
def _s5():
    if HERE not in sys.path: sys.path.insert(0, HERE)
    import s5lib
    return s5lib

def owners(w, R=None):
    """Deterministic partition of the PUBLIC registers into octets 0..13 and POOL (-1).  Returns (owner dict r->k, why dict r->rule).
    Rules, first match wins:
      main     X main -> octet of its port; Y main -> octet of its reader (same indexing as ports)
      bottom   SPAN5 attr.py rule: octet of the first nonempty x-content (arrival or departure) at a bottom stop (dims 1..4), majority octet
      yread    helper read directly by Y mains: majority octet of the Ys that read it (top-type helpers)
      content  first nonempty x-content at ANY stop / final, majority octet
      nbr      majority owner among the registers it exchanges ADD/COPY events with (<= 6 rounds)
      pool     no evidence (content-free, Y-free junk); belongs to no octet"""
    R = R or census(w); s5 = _s5(); oc = octet_table(); n = R['n']; col = R['col']; ycol = R['ycol']
    B = s5.bottom(R); own = {}; why = {}
    for r in range(n):
        ro = R['roles'][r]
        if ro == 'X': own[r] = oc[col[r]]; why[r] = 'main'
        elif ro == 'Y': own[r] = oc[ycol[r]]; why[r] = 'main'
    def maj(it): return collections.Counter(it).most_common(1)[0][0]
    for r, I in B.items():
        if r in own: continue
        for (d, f, a, dp) in I['stops']:
            if d < 1: continue
            hit = None
            for v in (a, dp):
                if v: hit = maj(oc[x] for x in v); break
            if hit is not None: own[r] = hit; why[r] = 'bottom'; break
    yread = collections.defaultdict(collections.Counter)
    for rec in R['evrec']:
        t, op, d, s, q, fi, dm, rd, rs, ss, sb, sa, rem, add = rec
        if rd == 'Y' and rs == 'H' and ss: yread[s][oc[ycol[d]]] += 1
    for r in range(n):
        if r in own or r not in yread: continue
        own[r] = sorted(yread[r].items(), key=lambda kv: (-kv[1], kv[0]))[0][0]; why[r] = 'yread'
    for r in range(n):
        if r in own: continue
        S = R['stops'][r]
        for v in [s['arr'] for s in S] + [R['final'][r]]:
            xs = [c for c in v if isinstance(c, int)]
            if xs: own[r] = maj(oc[x] for x in xs); why[r] = 'content'; break
    nb = collections.defaultdict(collections.Counter)
    for rec in R['evrec']:
        d, s = rec[2], rec[3]
        if d < n and s < n: nb[d][s] += 1; nb[s][d] += 1
    for _ in range(6):
        new = {}
        for r in range(n):
            if r in own: continue
            c = collections.Counter()
            for o, k in nb[r].items():
                if o in own: c[own[o]] += k
            if c: new[r] = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        if not new: break
        for r, k in new.items(): own[r] = k; why[r] = 'nbr'
    for r in range(n):
        if r not in own: own[r] = POOL; why[r] = 'pool'
    return own, why
def members(own, k):
    return sorted(r for r, o in own.items() if o == k)

# ----------------------------------------------------------------------------------------- program classification
def classify(w, M):
    """program events vs register set M: dict t -> 'int' (all participants in M), 'in' (ADD/COPY d in M, s outside), 'out' (s in M, d outside); others absent."""
    out = {}; n = len(w['initial'])
    for t, e in enumerate(w['program']):
        f = regfields(e); ins = [x in M for x in f]
        if all(ins): out[t] = 'int'
        elif e[0] in ('ADD', 'COPY') and any(ins): out[t] = 'in' if ins[0] else 'out'
    return out

# ----------------------------------------------------------------------------------------- invoice / R0 slices
def tax(ds):
    d2 = []
    for d in ds:
        if not d2 or d != d2[-1]: d2.append(d)
    D = d2[-1] - d2[0]; H = lambda x: x * math.log(x) if x > 0 else 0.0
    return H(D) - sum(H(b - a) for a, b in zip(d2, d2[1:])) if D > 0 else 0.0
def chains(w, regs=None):
    """r -> list of dims visited (initial, then every MOVE target), public registers only"""
    dim = [len(b) for b in w['frames']]; n = len(w['initial']); ch = {r: [dim[w['initial'][r]]] for r in range(n) if regs is None or r in regs}
    for e in w['program']:
        if e[0] == 'MOVE' and e[1] in ch: ch[e[1]].append(dim[e[3]])
    return ch
def invoice_share(w, M):
    """EXACT slice of the invoice owned by registers M: paid[|dim b - dim a|] per MOVE, helpers[dim final - dim initial] per helper (the legal.check census),
    plus events, scalar cost (per-event, legal.check formula), and the R0 tax(ds) MODEL sum.  Owned-register MOVEs are never in M."""
    dim = [len(b) for b in w['frames']]; n = len(w['initial']); role = roles_of(w)
    paid = collections.Counter(); hel = collections.Counter(); ev = 0; scalar = 0
    for e in w['program']:
        if not all(x in M for x in regfields(e)): continue
        ev += 1
        if e[0] == 'MOVE': paid[abs(dim[e[3]] - dim[e[2]])] += 1
        elif e[0] in ('INIT', 'CLEAR'): scalar += 2
        else:
            q = Q(e[-2]); nn, d = abs(q.numerator), q.denominator
            if e[0] == 'SCALE': scalar += 2 * (abs(nn.bit_length() - d.bit_length()) + int(q < 0))
            else: scalar += 2 * (3 + nn.bit_length() - 1 + nn.bit_count() + d.bit_length() - 1)
    ret = set(w.get('retired_public') or [])
    for r in M:
        if r < n and role(r) == 'H' and r not in ret: hel[dim[w['final'][r]] - dim[w['initial'][r]]] += 1
    ch = chains(w, M); r0 = sum(tax(c) for c in ch.values())
    return dict(paid=dict(sorted(paid.items())), helpers=dict(sorted(hel.items())), events=ev, scalar=scalar, R0_model=round(r0, 4), regs=len(M))
def kappa_probe(w, share, frac=0.01):
    """exact kappa of the word + MODEL ceiling probe: kappa if the column's R0 share were `frac` cheaper, via the R0 law 1/kappa = 130.27 + .02364*R0eq
    (MAP.md item 6; +-5e-5 rel).  Scaling the invoice slice directly is NOT used: T and P nearly cancel (rank surplus 760 of 13444 fields), so a uniform
    1% cut of a slice is not a design and overstates the gain ~60x."""
    import price_exact as X, legal
    rep = legal.check(w); T, P = X.invoice(rep); k0 = X.kappa(T, P)
    inv = 1.0 / k0 - 0.02364 * frac * share['R0_model']
    return dict(kappa=k0, kappa_if_R0_cheaper=1.0 / inv, frac=frac, model='R0 law')

# ----------------------------------------------------------------------------------------- numeric fingerprints (pins)
def reg_keys(w):
    """input-identity keys of a word's registers: public r -> 'p<r>', owned n+j -> 'o<j>' (splice maps surviving registers to their ORIGINAL keys)"""
    n = len(w['initial']); return ['p%d' % r for r in range(n)] + ['o%d' % j for j in range(C.legal.nown(w))]
def trace(w, ts, keys=None, K=3, seed=7):
    """value (mod 2^61-1, K random inputs, one per register KEY) of the SOURCE register (ADD/COPY e[2]) just before each event t in ts.  Probabilistic (error ~1e-18 per pin);
    independent of how owned symbols are labelled.  keys = per-register identity (reg_keys) so a renumbered word is evaluated on the same inputs as the original."""
    n = len(w['initial']); NR = n + C.legal.nown(w); keys = keys or reg_keys(w)
    val = [[random.Random('%d:%d:%s' % (seed, k, keys[r])).randrange(MODP) for r in range(NR)] for k in range(K)]
    ts = set(ts); out = {}
    for t, e in enumerate(w['program']):
        op, r = e[0], e[1]
        if op == 'MOVE': continue
        if op in ('INIT', 'CLEAR'):
            for x in val: x[r] = 0
            continue
        q = Q(e[-2]) if op != 'SCALE' else Q(e[2])
        qm = (q.numerator % MODP) * pow(q.denominator, MODP - 2, MODP) % MODP
        if op == 'SCALE':
            for x in val: x[r] = x[r] * qm % MODP
            continue
        s = e[2]
        if t in ts: out[t] = tuple(x[s] for x in val)
        if op == 'COPY':
            for x in val: x[r] = x[s] * qm % MODP
        else:
            for x in val: x[r] = (x[r] + qm * x[s]) % MODP
    return out
def xparts(w, ts):
    """x-part (port-coordinate content) of the SOURCE of each ADD/COPY at t in ts, exact, as {col: 'p/q'}; owned sources -> 'owned'"""
    n = len(w['initial']); live = w['live']; col = {r: c for c, r in enumerate(live)}
    loc = {r: ({col[r]: Q(1)} if r in col else {}) for r in range(n)}; ts = set(ts); out = {}
    for t, e in enumerate(w['program']):
        op = e[0]
        if op in ('MOVE',): continue
        if op in ('INIT', 'CLEAR'):
            if e[1] < n: loc[e[1]] = {}
            continue
        if op == 'SCALE':
            if e[1] < n: q = Q(e[2]); loc[e[1]] = {c: v * q for c, v in loc[e[1]].items()}
            continue
        d, s, q = e[1], e[2], Q(e[3])
        if t in ts: out[t] = 'owned' if s >= n else {str(c): str(v) for c, v in sorted(loc[s].items())}
        if d >= n: continue
        base = dict(loc[d]) if op == 'ADD' else {}
        if s < n:
            for c, v in loc[s].items():
                x = base.get(c, 0) + q * v
                if x: base[c] = x
                else: base.pop(c, None)
        loc[d] = base
    return out

def free_bounds_env():
    """context manager: TK_FREE_BOUNDS=1 for the duration of a check (restores env).  Runtime only."""
    @contextlib.contextmanager
    def cm():
        old = os.environ.get('TK_FREE_BOUNDS'); os.environ['TK_FREE_BOUNDS'] = '1'
        try: yield
        finally:
            if old is None: os.environ.pop('TK_FREE_BOUNDS', None)
            else: os.environ['TK_FREE_BOUNDS'] = old
    return cm()
