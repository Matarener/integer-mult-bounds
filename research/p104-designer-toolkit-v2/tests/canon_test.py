#!/usr/bin/env python3
"""[toolkit hygiene] realised K2 words are byte-canonical: MOVE private flags are JSON bool, and dump == PKGPREP normalise.dump (sorted keys, indent 2, \\n, gzip mtime 0).
Realises K2PUSH/h1.net onto #5827 (synth.k2search_validate.realise + tkcommon.save_canonical), re-reads, checks round trip + legality of the first-pass check."""
import sys,os,gzip,json,tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE); sys.path[:0]=[TK,TK+'/infra',TK+'/synth']
import tkcommon, k2search_validate as V
W=TK; NET=W + '/ext/K2PUSH/h1.net'
fails=[]
def need(c,m):
    print(('PASS ' if c else 'FAIL ')+m,flush=True)
    if not c: fails.append(m)
# (a) unit: normalise_flags + canonical_bytes
w={'program':[['MOVE',0,1,2,1],['MOVE',1,1,2,0],['ADD',0,1,'x',1]],'b':1,'a':2}
raw=tkcommon.canonical_bytes(w); j=json.loads(gzip.decompress(raw))
need(all(type(e[4]) is bool for e in j['program'] if e[0]=='MOVE') and j['program'][2][4]==1 and type(j['program'][2][4]) is int,'unit: MOVE flags bool, ADD fields untouched')
need(raw==tkcommon.canonical_bytes(json.loads(gzip.decompress(raw))),'unit: canonical dump is a fixed point')
# (b) realised K2 word
if os.path.exists(NET):
    _,base=tkcommon.load('5827'); net=V.parse_net(NET); w,nn=V.realise(net,base)
    need(all(type(e[4]) is bool for e in w['program'] if e[0]=='MOVE'),'realise emits bool MOVE flags at the source')
    out=tempfile.mkdtemp()+'/h1.json.gz'; tkcommon.save_canonical(w,out); b=open(out,'rb').read()
    j=json.loads(gzip.decompress(b)); d=gzip.compress((json.dumps(j,sort_keys=True,indent=2)+'\n').encode(),mtime=0)
    need(d==b,'realised word is byte-canonical (== PKGPREP normalise dump)')
    need(not any(type(e[4]) is int for e in j['program'] if e[0]=='MOVE'),'no int 0/1 private flags in the file')
else: print('SKIP realised-word check (no',NET,')')
print('ALL PASS' if not fails else 'FAILS %d'%len(fails)); sys.exit(1 if fails else 0)
