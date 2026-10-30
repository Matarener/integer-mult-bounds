"""Helper/main end slack: frame dims of start, first op, last op, final per register (#4610 word)."""
import sys, gzip, json
from collections import Counter, defaultdict
from pathlib import Path
w = json.loads(gzip.decompress((Path.home()/'imb-r13/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
c = w['canonical']; print('keys', list(c)[:30]); fr = c['frames']
print('nstart', len(c['start']), 'v', c['v'])
for side in ('forward','backward'):
    prog = w['programs'][side]
    print(side, Counter(e[0] for e in prog))
    print(' sample', [e for e in prog if e[0]=='scalar'][:2], [e for e in prog if e[0]=='climb'][:2], [e for e in prog if e[0]=='warp'][:1])
    break
def dim(f): return len(fr[f])
for side in ('forward','backward'):
    prog = w['programs'][side]
    ev = defaultdict(list)  # reg -> list of ('op',frame) / ('climb',a,b,rank)
    for e in prog:
        if e[0]=='climb': ev[e[2]].append(('climb',e[3],e[4],e[5]))
        elif e[0]=='scalar':
            g=e[1]
            regs=[r[1] for r in ([g[1],g[2]] if g[0] in ('add','copy') else [g[1]]) if r[0]=='L']
            for r in regs: ev[r].append(('op',e[2]))
        elif e[0]=='warp': ev[e[1][1]].append(('warp',e[2],e[3]))
    pre=Counter(); post=Counter(); kinds=Counter()
    for r in range(632):
        L=ev[r]; ops=[i for i,x in enumerate(L) if x[0]!='climb']
        if not ops: kinds['noop']+=1; continue
        a=[x[3] for x in L[:ops[0]] if x[0]=='climb']; b=[x[3] for x in L[ops[-1]+1:] if x[0]=='climb']
        if len(a)>0: pre[(r<224, tuple(a))]+=1
        if len(b)>0: post[(r<224, tuple(b))]+=1
    print(side,'climbs before first op (main?,ranks):',sorted(pre.items())[:20], 'total',sum(pre.values()))
    print(side,'climbs after last op:',sorted(post.items())[:20],'total',sum(post.values()), kinds)
