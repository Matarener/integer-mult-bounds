# merge classes_g*_*.json from all classify jobs into classes_all.json (one representative per class, smallest groups first)
import glob, json
allc = {}
for f in glob.glob('**/classes_g*_*.json', recursive=True):
    for h, (cnt, rep) in json.load(open(f)).items():
        if h in allc: allc[h][0] += cnt
        else: allc[h] = [cnt, rep]
L = sorted(({'count': c, 'rep': r, 'g': len(r)} for c, r in allc.values()), key=lambda x: (x['g'], -x['count']))
json.dump(L, open('classes_all.json', 'w'))
from collections import Counter
print('classes by size:', dict(Counter(x['g'] for x in L)), 'groups by size:', {g: sum(x['count'] for x in L if x['g'] == g) for g in (3, 4)})
