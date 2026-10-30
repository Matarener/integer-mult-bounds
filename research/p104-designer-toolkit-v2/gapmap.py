"""gapmap.py WORD_A WORD_B [--json] [--no-struct] [--bands]   component table of the R0 gap between two words (A = scratch/generator, B = swarm/reference).
Scope [toolkit analysis, read-only; GAPMAP lane Oct 27].  Words: paths to WORD.json[.gz] or aliases in words/ (e.g. 5907).  No env is set; no import-time side effects.

TKHYG2 (Oct 27): the DEFAULT table is now JUMP-LEVEL CUT ACCOUNTING (method of SPLICE/jumps.py + topcost.py): for each dimension cut c in 3..7, R0 of jumps (a>b dims, a<b)
with b<=c ('below c') and b>c ('at/above c': every jump that reaches past the cut, including jumps straddling it), per class X/Y/S/H and total, for both words and the delta.
A dimension cut is a clean physical split; the OLD mid-dim band table (bottom/centre/top by jump MID-dim, below) is NOT a cut and misattributes: the same structure lands in
different bins (#5907 routes 3>6 = 'centre'; ours 3>5 bottom + 5>7 top), so it claimed our top beats the swarm's while at every jump-level cut our top is worse.
The band table is kept behind --bands (labelled MID-DIM BAND TABLE -- NOT A CUT, MISLEADING FOR ATTRIBUTION); --json always carries both ('rows' = bands, 'cuts' = cut table).
R0 law (helper-cost law): R0 = sum over registers of  D ln D - sum_i r_i ln r_i  (D = dim span of the MOVE chain, r_i = jumps; kernel2net.r0).
It is exactly additive over jumps:  R0(reg) = sum_i r_i * ln(D/r_i), so every R0 unit can be attributed to one jump, hence to a dim band.
Components (one row each):
  X mains, Y mains          registers in `live` / live+112
  O owned                   owned scratch registers (tiny)
  H signal                  helpers that ever ADD from/to an owned register (STAR carriers / root readers).  In the swarm these also carry residual: a LOWER
                            bound on the swarm's signal cost (signal and residual are one network there).
  H residual bottom         remaining helpers, jumps with mid-dim < 4.5   (port side: the bottom half)
  H residual central        mid-dim == 4.5 exactly (jump symmetric about the transposition axis d <-> 9-d)
  H residual top            mid-dim > 4.5   (reader side: merges/landings per reader)
Also reports 'rungs' (residual helpers with <= 3 distinct dims), counts, events, and (unless --no-struct) value-level structure from an exact x-content replay:
landings per Y, pieces/landing, support per read, merge depth, reuse of shared signed sums, cancellation.
OWNED ROW (ENDANATOMY fix): 'owned (O)' = staged-descent entropy per owned descent, D ln D - sum r_i ln r_i over its owned MOVEs (owned_staging); #5907 40.15 (was 6.17 per register id), r104 0, m2 9.56.
Predicted kappa from the law 1/kappa = 130.27 + .02364 (R0 + 380 (owned_paid - 56)) (fit on 11 words, +-5e-5 relative)."""
import sys, os, json, gzip, math, collections
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, 'synth')):
    if p not in sys.path: sys.path.insert(0, p)
import kernel2net as K

def load(spec):
    for p in (spec, os.path.join(HERE, 'words', spec + '.json.gz'), os.path.join(HERE, 'words', spec)):
        if os.path.exists(p):
            return json.load(gzip.open(p, 'rt') if p.endswith('.gz') else open(p))
    raise SystemExit('gapmap: no such word %r' % spec)

LAW_C = 130.27; LAW_S = 0.02364; LAW_OWNED = 380.0; LAW_PAID0 = 56
def pred_kappa(R0, owned_paid=LAW_PAID0):
    """ENDANATOMY-corrected law: 1/kappa = 130.27 + .02364 (R0eq + 380 (owned_paid - 56)),  R0eq = components()['total'] (public tax + STAGED owned-descent entropy, see owned_staging).
    Fit on 11 words (#5811/5827/5907, o1y, o1, p4, q89, r104, m290, m479, m2): kappa within 5e-5 relative (the old law 131.2 + .02364 R0 with the per-register O row was off by 3.6e-4 (5907), 2.8e-3 (r104), 2.2e-3 (m2):
    the constant 131.2 silently absorbed the swarm's 40.15 staging, which r104 does not carry).  Valid for owned_paid = 56 in all fitted words; the 380/unit term is from SIGFUSE R1, not refitted."""
    return 1.0 / (LAW_C + LAW_S * (R0 + LAW_OWNED * (owned_paid - LAW_PAID0)))

def owned_staging(w):
    """OWNEDRANK/ENDANATOMY law fix.  The invoice charges every owned MOVE of rank r at the public weight (P_r += 18, no credit), so a STAGED owned descent costs its jump entropy
    D ln D - sum_i r_i ln r_i (D = total span of the descent, r_i its owned MOVE ranks) -- the same R0-eq as a public stop.  A descent is the set of owned lifetimes that MOVE and share
    frames (copy-handed stages touch the same frame; one root per frame, so frames separate descents).  Non-moving owned lifetimes cost 0 here.
    Returns dict(staging, descents, paid (sum of downward owned rank units), moves, up (ascending owned moves, normally 0)).
    #5907: 40.15 (8 descents, 20 moves), r104: 0, m2: 9.56.  The older per-register-id O row (6.17 on #5907) misses it: copies are fresh lifetimes with 0-1 stops each."""
    n = len(w['initial']); dim = [len(b) for b in w['frames']]; lid = {}; cnt = collections.Counter(); mv = collections.defaultdict(list)
    for e in w['program']:
        if e[0] == 'INIT' and e[1] >= n: cnt[e[1]] += 1; lid[e[1]] = (e[1], cnt[e[1]])
        elif e[0] == 'MOVE' and e[1] >= n: mv[lid[e[1]]].append((e[2], e[3]))
    uf = {l: l for l in mv}
    def find(x):
        while uf[x] != x: uf[x] = uf[uf[x]]; x = uf[x]
        return x
    fr = {}
    for l, L in mv.items():
        for a, b in L:
            for f in (a, b):
                if f in fr: uf[find(l)] = find(fr[f])
                else: fr[f] = l
    G = collections.defaultdict(list)
    for l in mv: G[find(l)].append(l)
    tot = 0.0; paid = 0; moves = 0; up = 0
    for L in G.values():
        rs = []; ds = []
        for l in L:
            for a, b in mv[l]:
                da, db = dim[a], dim[b]; ds += [da, db]; rs.append(abs(da - db)); moves += 1; paid += max(0, da - db); up += db > da
        D = max(ds) - min(ds)
        if D: tot += D * math.log(D) - sum(r * math.log(r) for r in rs if r)
    return dict(staging=tot, descents=len(G), paid=paid, moves=moves, up=up)

def components(w):
    n = len(w['initial']); role = K.roles(w); ch = K.chains(w); dim = [len(b) for b in w['frames']]
    owned_touch = set()
    for e in w['program']:
        if e[0] in ('ADD', 'COPY') and (e[1] >= n or e[2] >= n): owned_touch.add(e[1]); owned_touch.add(e[2])
    R = collections.defaultdict(float); cnt = collections.Counter(); rung_R0 = 0.0; rungs = 0
    jumps = collections.defaultdict(float)     # (class, mid) -> R0, for the dim histogram
    cutj = collections.defaultdict(float)      # (class S/X/Y/H, a, b) -> R0: jump-level (TKHYG2)
    for r, c in ch.items():
        cl = role(r); ds = [dim[f] for f in c]; sd = sorted(set(ds)); D = sd[-1] - sd[0]
        if cl == 'H' and r in owned_touch: cl = 'Hsig'
        cnt[cl if cl != 'H' else 'Hres'] += 1
        if cl == 'H' and len(sd) <= 3: rungs += 1
        if D == 0: continue
        for a, b in zip(sd, sd[1:]):
            v = (b - a) * math.log(D / (b - a)); mid = (a + b) / 2
            if cl == 'H':
                key = 'Hres_bottom' if mid < 4.5 else ('Hres_central' if mid == 4.5 else 'Hres_top')
                if len(sd) <= 3: rung_R0 += v
            else: key = cl
            R[key] += v; jumps[(cl, mid)] += v; cutj[('S' if cl == 'Hsig' else ('H' if cl == 'H' else cl), a, b)] += v
    names = {'X': 'X mains', 'Y': 'Y mains', 'O': 'owned (O)', 'Hsig': 'H signal (touch owned)', 'Hres_bottom': 'H residual bottom (mid<4.5)',
             'Hres_central': 'H residual central (mid=4.5)', 'Hres_top': 'H residual top (mid>4.5)'}
    os_ = owned_staging(w); legacy_O = R.get('O', 0.0); R['O'] = os_['staging']      # O row = staged-descent entropy (was: per-register-id tax, misses copies)
    return dict(R0={names[k]: R.get(k, 0.0) for k in names}, total=sum(R.values()), owned=os_, owned_legacy_O=legacy_O, counts=dict(cnt), rungs=rungs, rung_R0=rung_R0,
                jumps={'%s@%s' % k: v for k, v in jumps.items()}, cutj=dict(cutj), events=len(w['program']), regs=n, exact_total=K.r0(w)[1], owned_touch=len(owned_touch))

CUTS = (3, 4, 5, 6, 7); CLS = ('X', 'Y', 'S', 'H')
def cut_table(cj):
    """cj = components()['cutj'] -> {cut: {class: (below, above)}}; below = jumps with b<=c, above = jumps with b>c (SPLICE/topcost.py convention). O (owned) is in no class: totals add it back via 'O'."""
    out = {}
    for c in CUTS:
        row = {cl: (sum(v for (k, a, b), v in cj.items() if k == cl and b <= c), sum(v for (k, a, b), v in cj.items() if k == cl and b > c)) for cl in CLS}
        row['ALL'] = (sum(x[0] for x in row.values()), sum(x[1] for x in row.values())); out[c] = row
    return out

def struct(w):
    """exact x-content replay: per ADD with a register whose x-content is non-empty."""
    n = len(w['initial']); live = set(w['live']); role = K.roles(w); dim = [len(b) for b in w['frames']]
    ys = {r + 112 for r in live}
    form = {r: ({r: Q(1)} if r in live else {}) for r in range(n)}
    lvl = collections.defaultdict(int)           # merge depth of helper value
    ev = collections.Counter(); reads_Y = collections.defaultdict(list); h_readers = collections.defaultdict(set)
    seen = collections.Counter(); cancel = 0; cancelled_syms = 0; supp_hist = collections.Counter(); hh = 0; hh_supp = 0
    band = collections.Counter(); bandsup = collections.Counter()
    def key(f):
        if not f: return None
        it = sorted(f.items()); q0 = it[0][1]
        return tuple((k, v / q0) for k, v in it)
    for e in w['program']:
        o = e[0]
        if o in ('ADD', 'COPY'):
            d, s, q = e[1], e[2], Q(e[3]); fs = form.get(s, {}); fd = form.setdefault(d, {})
            if o == 'COPY': fd.clear()
            if not fs:
                ev['junk_or_empty_src'] += 1; continue
            rd, rs = role(d), role(s); fdim = dim[e[4]]
            before = len(fd)
            ov = [c for c in fs if c in fd]
            for c, v in fs.items():
                x = fd.get(c, 0) + q * v
                if x == 0: fd.pop(c, None)
                else: fd[c] = x
            cl = sum(1 for c in ov if c not in fd)
            if cl: cancel += 1; cancelled_syms += cl
            kd = 'Y' if d in ys else ('X' if d in live else ('O' if d >= n else 'H'))
            ks = 'Y' if s in ys else ('X' if s in live else ('O' if s >= n else 'H'))
            ev[(kd, ks)] += 1
            if ks == 'H' and fdim >= 1:
                seen[key(fs)] += 1; h_readers[s].add(d)
            if kd == 'Y':
                reads_Y[d].append((fdim, len(fs), ks))
            if kd == 'H' and ks in ('H', 'X'):
                bd = 'bot' if fdim < 4.5 else ('top' if fdim > 4.5 else 'mid')
                band[(ks + '>H', bd)] += 1; bandsup[(ks + '>H', bd)] += len(fs)
            if kd == 'H' and ks == 'H':
                lvl[d] = max(lvl[d], lvl[s] + 1); hh += 1; hh_supp += len(fs)
        elif o in ('INIT', 'CLEAR'): form[e[1]] = {}
        elif o == 'SCALE':
            for c in form.get(e[1], {}): form[e[1]][c] *= Q(e[2])
    ny = len(ys)
    real = {y: [t for t in v if t[2] in ('H', 'O')] for y, v in reads_Y.items()}
    landings = [t for v in real.values() for t in v]
    big = [t for t in landings if t[1] >= 8]
    hd = collections.Counter(lvl.values())
    reuse = sum(seen.values()) / max(1, len(seen))
    return dict(adds_by_kind={'%s<-%s' % k: v for k, v in ev.items() if isinstance(k, tuple)}, empty_src_adds=ev['junk_or_empty_src'],
                Y_real_reads_per_Y=len(landings) / ny, Y_big_reads_per_Y=len(big) / ny, Y_mean_support=sum(t[1] for t in landings) / max(1, len(landings)),
                Y_mean_support_big=sum(t[1] for t in big) / max(1, len(big)), Y_read_dims=dict(sorted(collections.Counter(t[0] for t in landings).items())),
                HH_adds=hh, HH_mean_support=hh_supp / max(1, hh), merge_depth_hist=dict(sorted(hd.items())), max_merge_depth=max(lvl.values() or [0]),
                distinct_signed_sums_read=len(seen), reads_of_helper_sums=sum(seen.values()), reuse_per_sum=reuse,
                helpers_with_ge2_readers=sum(1 for v in h_readers.values() if len(v) >= 2), helpers_read=len(h_readers),
                mean_readers_per_read_helper=sum(len(v) for v in h_readers.values()) / max(1, len(h_readers)),
                helper_adds_by_band={'%s@%s' % k: (v, round(bandsup[k] / v, 1)) for k, v in sorted(band.items())},
                cancelling_adds=cancel, cancelled_symbols=cancelled_syms)

def compare(A, B, with_struct=True):
    ca, cb = components(A), components(B); rows = []
    tot = ca['total'] - cb['total']
    for k in ca['R0']:
        a, b = ca['R0'][k], cb['R0'][k]; rows.append(dict(component=k, A=a, B=b, delta=a - b, share=(a - b) / tot if tot else 0.0))
    cta, ctb = cut_table(ca['cutj']), cut_table(cb['cutj'])
    out = dict(cuts=dict(A=cta, B=ctb), rows=rows, A_total=ca['total'], B_total=cb['total'], delta_total=tot, A_kappa_pred=pred_kappa(ca['total'], ca['owned']['paid']), B_kappa_pred=pred_kappa(cb['total'], cb['owned']['paid']),
               A=dict(counts=ca['counts'], rungs=ca['rungs'], rung_R0=ca['rung_R0'], events=ca['events'], exact_total=ca['exact_total']),
               B=dict(counts=cb['counts'], rungs=cb['rungs'], rung_R0=cb['rung_R0'], events=cb['events'], exact_total=cb['exact_total']))
    if with_struct: out['struct_A'] = struct(A); out['struct_B'] = struct(B)
    return out

def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('A'); ap.add_argument('B')
    ap.add_argument('--json', action='store_true'); ap.add_argument('--no-struct', action='store_true')
    ap.add_argument('--bands', action='store_true', help='print the OLD mid-dim band table (NOT a cut; misattributes) instead of the jump-level cut table'); a = ap.parse_args(argv)
    out = compare(load(a.A), load(a.B), not a.no_struct)
    if a.json: print(json.dumps(out, indent=1, default=str)); return 0
    na, nb = 'A=' + os.path.basename(a.A)[:9], 'B=' + os.path.basename(a.B)[:9]
    if a.bands:
        print('== MID-DIM BAND TABLE (legacy; NOT a dimension cut -- misattributes top/bottom, see TKHYG2 / module docstring; use the default cut table) ==')
        print('%-34s %10s %10s %10s %7s' % ('component', na, nb, 'delta', 'share'))
        for r in out['rows']: print('%-34s %10.1f %10.1f %10.1f %6.1f%%' % (r['component'], r['A'], r['B'], r['delta'], 100 * r['share']))
    else:
        print('== JUMP-LEVEL CUT TABLE: R0 of jumps ending at dim <= c (below) / > c (at/above) ; delta = A - B ; all classes (X,Y,S=helpers touching owned,H=residual helpers) ==')
        print('%-4s %-5s %12s %12s %10s   %12s %12s %10s' % ('cut', 'class', na + ' bot', nb + ' bot', 'd.bot', na + ' top', nb + ' top', 'd.top'))
        for c in CUTS:
            for cl in CLS + ('ALL',):
                A_, B_ = out['cuts']['A'][c][cl], out['cuts']['B'][c][cl]
                print('%-4s %-5s %12.1f %12.1f %+10.1f   %12.1f %12.1f %+10.1f' % (c if cl == 'X' else '', cl, A_[0], B_[0], A_[0] - B_[0], A_[1], B_[1], A_[1] - B_[1]))
    print('%-34s %10.1f %10.1f %10.1f %6.1f%%' % ('TOTAL R0 (incl. owned)', out['A_total'], out['B_total'], out['delta_total'], 100.0))
    print('predicted kappa (law): A %.7f  B %.7f' % (out['A_kappa_pred'], out['B_kappa_pred']))
    print('counts A', out['A']['counts'], 'rungs', out['A']['rungs'], 'rung R0 %.0f' % out['A']['rung_R0'], 'events', out['A']['events'])
    print('counts B', out['B']['counts'], 'rungs', out['B']['rungs'], 'rung R0 %.0f' % out['B']['rung_R0'], 'events', out['B']['events'])
    if not a.no_struct:
        for k in ('struct_A', 'struct_B'):
            print(k); [print('  %s: %s' % (kk, vv)) for kk, vv in out[k].items()]
    return 0

if __name__ == '__main__': sys.exit(main())
