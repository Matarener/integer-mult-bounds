"""T3.1 certificate: Gram identity M x y = d x * gam x y * g y on all of Z x Z from the T1 step-5 facts.
For every ordered pair (x, y) of Z: orthogonal (both sides 0), diagonal, a directed step-5 fact, or a frame F inside Z
for which every (x, f) and (f, y) is of the first three kinds (frame expansion; integer identity
18 dot(x,y) = sum_f dot(x,f) dot(f,y) holds for every frame).  usage: gram_cert.py rep step5.json out.json"""
import sys, json, os
sys.path.insert(0, '.')
from p104lib import frames, IDX, ORTH, N
k = int(sys.argv[1]); d5 = json.load(open(sys.argv[2])); outp = sys.argv[3]
FR = [tuple(IDX[q] for q in f) for f in frames()]
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
m = int(reps[k]['mask']); Z = [i for i in range(N) if m >> i & 1]
if os.environ.get('DROP'):
    _dr = set(map(int, os.environ['DROP'].split(','))); Z = [i for i in Z if i not in _dr]
Zs = set(Z); FZ = [fi for fi, f in enumerate(FR) if all(i in Zs for i in f)]
fid = {tuple(f): i for i, f in enumerate(d5['FS'])}
def basic(x, y):   # -> code: 65535 orth, 65534 diag, else fact index
    if x == y: return 65534
    if ORTH[x][y]: return 65535
    return fid.get((x, y))
ent = []; nfr = 0; bad = []
for x in Z:
    for y in Z:
        b = basic(x, y)
        if b is not None: continue
        for fi in FZ:
            F = FR[fi]; hs = [basic(x, f) for f in F] + [basic(f, y) for f in F]
            if all(h is not None for h in hs):
                ent.append([x, y, fi] + hs); nfr += 1; break
        else: bad.append((x, y))
json.dump({'rep': k, 'Z': Z, 'frames': ent, 'bad': bad}, open(outp, 'w'))
print('GRAM type %d Z %d facts %d frame pairs %d bad %d' % (k, len(Z), len(d5['FS']), nfr, len(bad)), flush=True)
