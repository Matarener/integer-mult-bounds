import sys, gzip, json
from collections import Counter, defaultdict
from pathlib import Path
w = json.loads(gzip.decompress((Path.home()/'imb-r13/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
c = w['canonical']; fr = c['frames']
side = sys.argv[1]; R = int(sys.argv[2])
prog = w['programs'][side]
print('start', c['start'][R], 'dim', len(fr[c['start'][R]]) if isinstance(c['start'][R], int) else c['start'][R], 'final', c['final'][R])
for i,e in enumerate(prog):
    s = json.dumps(e)
    if e[0]=='climb' and e[2]==R: print(i, 'CLIMB', e[3], '->', e[4], 'rank', e[5])
    elif e[0]=='scalar':
        g=e[1]; regs=[r for r in g[1:3] if isinstance(r,list)]
        if ['L',R] in regs: print(i, g, 'frame', e[2], 'dim', len(fr[e[2]]))
    elif e[0]=='warp' and e[1]==['L',R]: print(i, e)
