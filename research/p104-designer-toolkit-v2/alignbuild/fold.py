"""RULEMINE fold.py: builder step R-FOLD (shadow-relay fold) as a post-pass on any word.  Copy-driver: shared builders untouched; the solve is
IOROOT2/iob2.py (called as a subprocess with derived argv); soundness is EXACT-CHECKED PER SITE (iob2 builds, value-replays with residual 0,
legal.check, exact kappa; a site is accepted only if LEGAL and kappa strictly up).  The census (census.py) is the sufficient-precondition test; the solve decides realisability.
usage: fold.py WORD OUT.json.gz [--sites root:H,..] [--max N] [--dry]   (heavy: run via hq)
Per site ladder: relocation of the root's landing lifetime (auto window [T1,T2]) tried first, then none.  After an accepted site the word is re-censused."""
import sys, os, json, gzip, re, subprocess, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); 
sys.path.insert(0, HERE)
import foldcensus as census
import sigside as sigb
PY = sys.executable; IOB = os.path.join(HERE, 'iob2.py')
FLAGS = '--flex --strip-sym --first-hop --root-frames-only --f0 --f0-wide --improve 0 --newton 8'.split()

def plan(path, site):
    _, w = sigb.S.load_word(path); prog = w['program']; n = len(w['initial'])
    L = sigb.lifetimes(w, prog); roots, _ = sigb.roots_of(w, prog, L)
    G = roots[site['root']]
    land = [i for i in G if any(f == site['b'] for f, _, _ in L[i]['stays'])]
    li = max(land, key=lambda i: L[i]['t0']); l = L[li]
    cnt = []; live = set()
    for t, e in enumerate(prog):
        if e[0] == 'INIT': live.add(e[1])
        cnt.append(len(live))                      # same convention as IOROOT2/peak.py (a register cleared at t still counts at t)
        if e[0] == 'CLEAR': live.discard(e[1])
    limit = max(13, max(cnt))                    # owned-register profile bound 13 (inventory (770,29,31,13)); legal.check is the judge
    hev = sorted(t for t, e in enumerate(prog) if e[0] in ('ADD', 'COPY') and e[2] == site['H'])   # receivers' reads of the relay
    return w, l, cnt, limit, hev

def variants(path, site):
    w, l, cnt, limit, hev = plan(path, site)
    reg = l['reg']; out = []
    for T2 in dict.fromkeys(min(len(w['program']) - 1, h + 32) for h in (hev[::-1][1:2] + hev[::-1][:1] + hev[::-1][2:3])):
        # exclude the lifetime's own contribution
        T1 = T2
        while T1 - 1 > l['t0'] and (cnt[T1 - 1] - (1 if l['t0'] <= T1 - 1 <= l['t1'] else 0)) <= limit - 1: T1 -= 1
        if T1 > l['t1']: out.append(['--relocate', '%d:%d:%d' % (reg, T1, T2)])
    out.append([])
    return reg, out

def prehoist(path, site, outp):
    """Gauge rung (IOROOT2 sec 3): every public reader p of the root at frame b whose MOVE ... -> b happens after the root has landed there is moved to just
    BEFORE the landing MOVE, if p has no non-MOVE event in between and its frame stays legal; exact value replay checked by rp (residual 0), else None."""
    import numpy as np
    rp = sigb.rp
    _, w = sigb.S.load_word(path); w = json.loads(json.dumps(w)); prog = w['program']; n = len(w['initial'])
    L = sigb.lifetimes(w, prog); roots, _ = sigb.roots_of(w, prog, L); G = set(roots[site['root']])
    land = None
    for i in G:
        for f, ta, tb in L[i]['stays']:
            if f == site['b']: land = ta if land is None else min(land, ta)
    if land is None: return None
    readers = sorted({e[1] for t, e in enumerate(prog) if e[0] == 'ADD' and e[1] < n and e[4] == site['b'] and e[1] != site['H'] and ((e[2] >= n and sigb.lid_at(L, e[2], t) in G) or e[2] == site['H'])})
    mv = {}
    for p in readers:
        ts = [t for t, e in enumerate(prog) if e[0] == 'MOVE' and e[1] == p and e[3] == site['b']]
        if not ts or ts[0] < land: continue
        t1 = ts[0]
        if any(prog[t][0] != 'MOVE' and p in sigb.S.regfields(prog[t]) for t in range(land, t1)): continue
        if any(prog[t][0] == 'MOVE' and prog[t][1] == p for t in range(land, t1)): continue
        mv[t1] = land
    if not mv: return None
    ins = {}
    for T, TT in mv.items(): ins.setdefault(TT, []).append(prog[T])
    out = []
    for t, e in enumerate(prog):
        out += ins.get(t, [])
        if t not in mv: out.append(e)
    w2 = dict(w); w2['program'] = out
    A0, _ = rp.replay(w, prog); A2, _ = rp.replay(w2, out); Tg = rp.target(w)
    if int(np.count_nonzero((Tg - A2) % rp.P)) != int(np.count_nonzero((Tg - A0) % rp.P)): return None
    sigb.S.C.activate(w2); rep = sigb.S.C.legal.check(w2)
    if not rep['ok']: return None
    with gzip.open(outp, 'wt') as fh: json.dump(w2, fh)
    return outp

PH_FIRST = False
def run(path, outp, site, tag, log):
    r = None if PH_FIRST else run1(path, outp, site, tag, log)
    if r and r['status'] == 'FOLDED': return r
    ph = prehoist(path, site, outp + '.ph.json.gz')
    if ph:
        log.write('  site %s: prehoist gauge rung applied (readers moved before the landing)\n' % tag); log.flush()
        r2 = run1(ph, outp, site, tag + '+ph', log)
        if r2 and r2['status'] == 'FOLDED': return r2
        if r2 and r is None: r = r2
    return r

def run1(path, outp, site, tag, log):
    reg, vs = variants(path, site)
    ins = []
    for f in site['mid'][::-1]: ins += ['--insert', '%d:%d:+0' % (reg, f)]
    seen = set(); res = None
    for v in vs:
        key = tuple(v)
        if key in seen: continue
        seen.add(key)
        cmd = [PY, '-B', IOB, path, outp, '--root', str(site['root']), '--strip-regs', str(site['H'])] + ins + v + FLAGS
        t0 = time.time()
        try: p = subprocess.run(cmd, capture_output=True, text=True, timeout=720)
        except subprocess.TimeoutExpired: log.write('  site %s variant %s -> TIMEOUT\n' % (tag, v)); continue
        last = [x for x in p.stdout.splitlines() if x.startswith('RESULT')]
        msg = last[-1] if last else 'NO RESULT: ' + (p.stderr.strip().splitlines() or ['?'])[-1][:160]
        log.write('  site %s variant %s -> %s (%.0fs)\n' % (tag, ' '.join(v) or 'norelocate', msg[:160], time.time() - t0)); log.flush()
        m = re.search(r'RESULT: LEGAL kappa ([0-9.]+) \(base ([0-9.]+), diff ([+-][0-9.e+-]+)\)', msg)
        if m and float(m.group(3)) > 0: return dict(site=tag, kappa=float(m.group(1)), base=float(m.group(2)), diff=float(m.group(3)), variant=v, status='FOLDED')
        if m: res = dict(site=tag, status='LEGAL-NOGAIN', diff=float(m.group(3)), variant=v)
        elif res is None: res = dict(site=tag, status=msg[:60])
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('out'); ap.add_argument('--sites', default=''); ap.add_argument('--max', type=int, default=99); ap.add_argument('--dry', action='store_true')
    ap.add_argument('--log', default=''); ap.add_argument('--ph-first', action='store_true')
    a = ap.parse_args(); global PH_FIRST; PH_FIRST = a.ph_first; log = open(a.log, 'a') if a.log else sys.stderr
    if not os.environ.get('TK_PROFILE'):      # folded words keep the input's inventory: judge them under the INPUT word's profile
        sys.path.insert(0, os.path.dirname(HERE)); import tkcommon as _C; os.environ['TK_PROFILE'] = _C.profile_of(_C.load(a.word)[1])[0]
    cur = a.word; done = []; fail = set(); step = 0
    while step < a.max:
        sites, _, dim = census.sites(cur)
        if a.sites: want = {tuple(map(int, s.split(':'))) for s in a.sites.split(',')}; sites = [s for s in sites if (s['root'], s['H']) in want or ('*', s['H']) in want or (-1, s['H']) in want]
        sites = [s for s in sites if s['H'] not in fail]
        if not sites: break
        s = sites[0]; step += 1; tag = 'H%d' % s['H']
        log.write('step %d word %s site %s root %d mid %s ceiling %.2f\n' % (step, os.path.basename(str(cur)), tag, s['root'], s['mid'], s['save'])); log.flush()
        if a.dry: log.write('  variants %s\n' % (variants(cur, s),)); fail.add(s['H']); continue
        nxt = a.out + '.step%d.json.gz' % step
        r = run(cur, nxt, s, tag, log)
        done.append(r)
        if r and r['status'] == 'FOLDED': cur = nxt
        else: fail.add(s['H'])
    if cur != a.word and not a.dry: os.replace(cur, a.out)
    print(json.dumps(dict(word=a.word, steps=done, final=a.out if cur != a.word else None)))
if __name__ == '__main__': main()
