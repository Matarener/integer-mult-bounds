#!/usr/bin/env python3
"""GENPIPE2 regress: `tk gen2` (from-scratch generator, stages 1-5).
  --fast   stage-level smoke (~10 s): gen2 modules import without touching os.environ; routeb -> b0 and ylate -> yl1 reproduce kappa and content sha
  --chain  full chain relaytop, routeb, ylate, order, purex: every intermediate and r104 (.0030170593878) bit-exact (decompressed-JSON sha256 equal to the lane words)
Content sha = sha256 of the decompressed JSON (gzip headers carry a time stamp, so the FILE sha of a regenerated word differs; the content does not)."""
import sys, os, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); TK = HERE + '/..'
EXP = {   # name: (kappa str of tk price, content sha[:16]) -- read from the lane words MARKETS/PUREX/SIGFUSE/JOINTFRAMES/RELAYTOP
    'allh_d3': ('0.0025498457553', 'bf2cc8f106d00ce7'), 'b0': ('0.0029000603871', '91c230db76659821'), 'yl1': ('0.0029031190012', 'e24a69114d6cbd00'),
    'o1': ('0.0029461448190', '5cd4a131bcc23a2b'), 'o1y': ('0.0029493782308', '7de42ba0ef644036'), 'r104': ('0.0030170593878', 'a691733502945e0a'),
    'px': ('0.0030089352115', '8e65827f99aaf07c')}      # px = polish sub-step 1: purex2 on o1y (== B0POLISH/o1y_purex); the k2sa and eval sub-steps are hq jobs (module docstring: polished 572225ad597054c7 = B0POLISH/best_px, .0030571699219)
fails = []
def need(c, what):
    print(('PASS ' if c else 'FAIL ') + what, flush=True)
    if not c: fails.append(what)
def gen2(stages, out, *extra):
    r = subprocess.run([sys.executable, '-B', TK + '/tk.py', 'gen2', '--out', out, '--stages', stages, '--expect'] + list(extra), capture_output=True, text=True)
    recs = [json.loads(l) for l in open(out + '/stages.jsonl')] if os.path.exists(out + '/stages.jsonl') else []
    if r.returncode: print(r.stdout[-1500:], r.stderr[-800:])
    return r.returncode, {x['word']: x for x in recs}
def check(recs, names):
    for n in names:
        k, sh = EXP[n]; x = recs.get(n)
        need(x is not None and abs(x['kappa'] - float(k)) < 1e-13, '%s kappa %s' % (n, k))
        if sh: need(x is not None and x['content_sha'] == sh, '%s content sha %s (bit-exact vs lane word)' % (n, sh))
def main():
    A = sys.argv[1:]; tmp = tempfile.mkdtemp()
    if '--fast' in A or not A:
        before = dict(os.environ)
        sys.path.insert(0, TK); sys.path.insert(0, TK + '/gen2')
        import genpipe2, rt, geo, edges, hgreedy, allh, late, jsupp, ylate, purex, purex2, valcheck, grp, route_b, relaytop
        need(dict(os.environ) == before, 'gen2 modules import without changing os.environ')
        rc, recs = gen2('routeb,ylate', tmp + '/fast')
        need(rc == 0, 'tk gen2 routeb,ylate exit 0 (--expect)'); check(recs, ['b0', 'yl1'])
    if '--chain' in A:
        rc, recs = gen2('relaytop,routeb,ylate,order,purex', tmp + '/chain')
        need(rc == 0, 'tk gen2 full chain exit 0 (--expect)'); check(recs, ['allh_d3', 'b0', 'yl1', 'o1', 'o1y', 'r104'])
        need(all(os.path.exists(tmp + '/chain/%s.canon.json.gz' % n) for n in EXP if n != 'px'), 'canonical (mtime-0) copy written for every stage word')
        rc, recs = gen2('polish', tmp + '/chain', '--polish-steps', 'purex')
        need(rc == 0, 'tk gen2 polish --polish-steps purex exit 0'); check(recs, ['px'])
    print('\n%d failed' % len(fails)); print('ALL PASS' if not fails else 'FAILED'); sys.exit(1 if fails else 0)
main()
