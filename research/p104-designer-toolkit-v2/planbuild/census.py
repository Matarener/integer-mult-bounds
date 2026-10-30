"""PLANBUILD census.py: realisability census of a pick's options against the transposition realiser's exact identifications.
usage: census.py PICK ...   (no env)"""
import os
import sys, collections, pickle, io, contextlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/planbuild')
import plan
with contextlib.redirect_stdout(io.StringIO()): B = plan.population()
N, DN = B['N'], B['DN']
bsrc = {o[1] for o in N.ops}; dsrc = {o[1] for o in DN.ops}
regrects = collections.Counter(DN.rects[r]['reg'] for r in DN.live)
print('dual regs owning >1 live rect:', sum(1 for v in regrects.values() if v > 1), '| piece regs owning >1 live rect:', sum(1 for v in collections.Counter(N.rects[r]['reg'] for r in N.live).values() if v > 1))
for f in sys.argv[1:]:
    pk = pickle.load(open(f, 'rb')); c = collections.Counter()
    for k, o in pk.items():
        prid, drid, dk = B['arr'][k]; p = N.rects[prid]['reg']; d = DN.rects[drid]['reg']
        if o[0] == 'd':
            pp, dd = o[1][1], o[2][1]
            c[('d', 'own' if (pp, dd) == (p, d) else 'alt', 'dsrc' if dd in dsrc else 'dsink', 'psrc' if pp in bsrc else 'psink', N.regs[pp]['role'], DN.regs[dd]['role'])] += 1
        elif o[0] == 'a':
            c[('a', 'own' if o[1][1] == p else 'alt', N.regs[o[1][1]]['role'], 'psrc' if o[1][1] in bsrc else 'psink')] += 1
        elif o[0] == 'b':
            c[('b', 'own' if o[1][1] == d else 'alt', DN.regs[o[1][1]]['role'])] += 1
        else: c[('c',)] += 1
    print('==', f)
    for kk, v in sorted(c.items()): print('  ', kk, v)

def per_dual(pick_file, eff_file):
    """per dual s (G_s of the block's hp, cb1.py EXACT): arrivals, input options, and how many the realiser kept vs re-planned"""
    import json
    CB1 = pickle.load(open(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/CLASSBREAK/cb1.pkl', 'rb'))
    pk = pickle.load(open(pick_file, 'rb')); eff = json.load(open(eff_file))['eff']
    rows = collections.defaultdict(collections.Counter)
    for k, o in pk.items():
        prid, drid, dk = B['arr'][k]; mt = B['meta'][B['dmeta'][dk][1]]
        s = CB1[(mt[1], mt[2])]['Gs'][0] if mt[0] == 'b' else 'coset'
        e = eff[str(k)]; same = (e[0] == o[0] and e[1:] == [str(x) for x in o[1:]])
        rows[s]['n'] += 1; rows[s]['kept' if same else 'replanned'] += 1; rows[s]['in_' + o[0]] += 1
    for s in sorted(rows, key=str): print('  dual', s, dict(rows[s]))
