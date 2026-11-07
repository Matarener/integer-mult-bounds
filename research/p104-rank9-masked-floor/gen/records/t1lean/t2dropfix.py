"""After a t2s.py run of type k: the items without a frame for pins (NOFRAME / ZKILL FAIL) have Gram only on their
record zm.  Add the lines of C missing from those record zm to t2hand/t2drop.json (the T2 target becomes C minus them).
usage: python3 t1lean/t2dropfix.py k LOG"""
import sys, os, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
k = int(sys.argv[1]); log = open(sys.argv[2]).read()
r = [r for r in json.load(open(os.path.join(BASE, 'orbitsW.json'))) if not r['frame']][k]; m0 = int(r['mask'])
Z = set(i for i in range(104) if m0 >> i & 1)
bad = sorted(set(int(i) for i in re.findall(r'^item (\d+) .*(?:NOFRAME|ZKILL FAIL)', log, re.M)))
miss = set()
for i in bad:
    zm = set(json.load(open(os.path.join(HERE, 'cert', 'T2O_%d_%d.json' % (k, i))))['ZM']); miss |= Z - zm
    print('item', i, 'missing', sorted(Z - zm))
f = os.path.join(BASE, 't2hand', 't2drop.json'); D = json.load(open(f))
D[str(k)] = sorted(set(D.get(str(k), [])) | miss); json.dump(D, open(f, 'w'))
print('type', k, 'drop', D[str(k)], '|C| after', len(Z) - len(D[str(k)]))
