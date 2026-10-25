# Step 1b: ordered span pairs that are (nearly) tight for the 140 certificate; complementary slackness says
# every optimal primal skeleton lives on tight pairs.  Writes step1b_tight.json with progress to step1b.log.
import sys, json, time
sys.path.insert(0, r'D:\Math\imb-v4pr\research\plane-port-global-rank-dual')
import numpy as np, verify as V
T0 = time.time()
def log(*a):
    print('%6.0fs' % (time.time() - T0), *a, flush=True)
planes, pel, orth = V.geometry(); S = V.census(planes); n = len(S); size = S.sum(1)
dim = np.log2(size).round().astype(np.int64)
pmask = np.zeros((56, 512), bool)
for i, e in enumerate(pel): pmask[i, list(e)] = True
inside = (S.astype(np.int32) @ pmask.T.astype(np.int32)) == 4
Dm = np.array([[V.dot(x, y) for y in range(512)] for x in range(512)], dtype=np.float32)
perp = (S.astype(np.float32) @ Dm) == 0
Sp = np.packbits(S, axis=1, bitorder='little').view(np.uint64); Pp = np.packbits(perp, axis=1, bitorder='little').view(np.uint64)
cert = json.load(open(r'D:\Math\imb-v4pr\research\plane-port-global-rank-dual\CERTIFICATE.json'))
SC = cert['scale']; cols = cert['columns']; w = np.array([c['w'] for c in cols], float)
qm = np.zeros((len(cols), 56), bool)
for k, c in enumerate(cols): qm[k, c['clique']] = True
Tf = ((inside.astype(np.int32) @ qm.T.astype(np.int32)) > 0).astype(np.float64); TW = (Tf * w).T.copy()
THR = 0.05 * SC; out = []
for a0 in range(0, n, 64):
    rs = np.arange(a0, min(a0 + 64, n))
    cnt = np.bitwise_count(Sp[rs][:, None, :] & Pp[None, :, :]).sum(axis=2, dtype=np.int64)
    tar = dim[rs, None] - np.log2(cnt).round().astype(np.int64)
    slack = tar * SC - (Tf[rs] @ TW)
    ii, jj = np.nonzero(slack <= THR)
    for i, j in zip(ii, jj):
        out.append([int(rs[i]), int(j), int(tar[i, j]), float(slack[i, j] / SC)])
    if a0 // 64 % 100 == 0: log('rows', a0 + 64, '/', n, 'near-tight so far', len(out))
json.dump({'inside': [np.flatnonzero(r).tolist() for r in inside], 'pairs': out}, open('step1b_tight.json', 'w'))
log('done', len(out))
