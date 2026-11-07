"""Write one T1 record (Lean `RankNine.T2.T1D`, decoder `T1Decode.lean`) as a stream of naturals from the closure
certificate (t1case.py) and the zero tables (emit_t2zero.py with ZJSON).  Field order = `T1Decode.parse`.
usage: python3 t1lean/wdata.py cert.json zero.json out.txt"""
import json, sys
c = json.load(open(sys.argv[1])); z = json.load(open(sys.argv[2])); out = []
def nat(x): out.append(int(x))
def lst(l): nat(len(l)); out.extend(int(v) for v in l)
def btn(entries):   # BT ℕ from (index, value) pairs
    entries = list(entries); nat(len(entries))
    for i, v in entries: nat(i); nat(v)
def btl(entries):   # BT (List ℕ)
    entries = list(entries); nat(len(entries))
    for i, v in entries: nat(i); lst(v)
tab = lambda d, dflt: sorted((int(k), v) for k, v in d.items() if v != dflt)
EDG = c['EDG']
# Cert
btl([(i, r) for i, r in enumerate(c['RS'])])
btn(tab(c['OD'], 1000000000)); btn(tab(c['MK'], 0))
lst(c['RT']); lst(c['CO']); lst(c['FO'])
btn(tab(c['PD'], 1000000000)); btn(tab(c['PR'], 0)); btn(tab(c['SG'], 0))
btl([(i, s) for i, s in enumerate(c['ST']) if s is not None])
nat(c['L']); lst(c['GA']); lst(c['NE']); nat(c['n'])
# edge tables, descriptors
btn(sorted((104 * x + y, e) for e, (x, y) in enumerate(EDG) if e != 0))
btn([(e, x) for e, (x, y) in enumerate(EDG) if x != 0])
btn([(e, y) for e, (x, y) in enumerate(EDG) if y != 0])
btl([(i, d) for i, d in enumerate(c['DESC'])])
nat(c['E']); nat(sum(1 << r for r in c['ROWS'])); nat(sum(1 << r for r in c['ZM']))
nat(len(c['TT']))
for e, b in c['TT']: nat(e); nat(1 if b else 0)
nat(c['ROOT'])
# zero certificate
assert z['m'] == sum(1 << r for r in c['ROWS'])
nat(z['G']); btl(tab(z['VT'], None)); btl(tab(z['FT'], None)); btl(list(enumerate(z['EN']))); nat(z['n'])
btn(tab(z['GV'], 0))
open(sys.argv[3], 'w').write(' '.join(map(str, out)) + '\n')
print('wrote', sys.argv[3], len(out), 'numbers')
