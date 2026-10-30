"""PR-side verdicts for a list of mutant record lists (isolated python3.12 -I): native.replay base + mod-101 fields.  usage: bitmut_pr.py PKGDIR MUTANTS.json OUT.json [FIELDS 0|1]"""
import sys,json,os
D,inp,out=sys.argv[1:4]; fields=len(sys.argv)<5 or sys.argv[4]=='1'
sys.path.insert(0,D); os.chdir(D)
if os.path.exists(D+'/integration.py'):
    import integration as L, native
    word=L.read(L.R/'WORD.json.gz'); _,frames,_=L.source(); physical=dict(final=word['start'],start=word['final']); owned=set(word['owned'])
    REPLAY=lambda recs,m=None: native.replay(physical,frames,recs,owned,m)
else:      # 'nine' layout
    import local_relations as LR
    word=LR.read(LR.R/'WORD.json.gz'); base,frames,_=LR.source(); owned=set(word['owned'])
    REPLAY=lambda recs,m=None: LR.replay(base,frames,recs,owned,m)
muts=json.load(open(inp)); res=[]
for recs in muts:
    try:
        REPLAY(recs)
        if fields: REPLAY(recs,101)
        res.append(None)
    except BaseException as e: res.append(str(e)[:120])
json.dump(res,open(out,'w'))
