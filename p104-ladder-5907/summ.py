import json,sys,collections,glob
rows=[json.loads(l) for f in sys.argv[1:] for l in open(f)]
print(len(rows), collections.Counter((r['ok'], r.get('why','')[:28]) for r in rows).most_common(10))
ok=[r for r in rows if r['ok']]
for r in sorted(ok,key=lambda r:-r['gain'])[:25]: print(r['reg'],r['stop'],r.get('pick'),'gain %.3e'%r['gain'],'dev',r['events_delta'])
