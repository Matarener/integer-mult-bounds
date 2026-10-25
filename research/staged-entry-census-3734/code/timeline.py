"""Chronological event list of a BORROW-WORD scalar program, with frames and contacts.

Order = audit_core.program: corrections, precondition, compensation, A, cut, B+warps, restore.
Each event: dict(pos, sec, idx, g, kind, frame); frame is a point-set mask (None for cut/corr).
The frame bill and the semantics come from PR3734's audit_core.py (Sagar Thakrar), imported
from the stacked package, not copied.
"""
import gzip,json,sys
from pathlib import Path
PKG=str(Path(__file__).resolve().parents[2]/'staged544-producer-return')
sys.path.insert(0,PKG)
import audit_core as C

def load(tag):
    """'base' / 'extra' = PR3734's BORROW-WORD-43 provider words; otherwise a .json.gz path."""
    path=tag if tag.endswith('.gz') else f'{PKG}/words/BORROW-WORD-43{tag}.json.gz'
    return json.loads(gzip.decompress(open(path,'rb').read()))

def events(w):
    ev=[]
    def add(sec,idx,g,kind,frame):
        ev.append(dict(pos=len(ev),sec=sec,idx=idx,g=g,kind=kind,frame=frame))
    for i,c in enumerate(w['initial_corrections']):
        add('corr',i,c,'corr',None)
    for i,g in enumerate(w['precondition']): add('pre',i,g,g[0],C.ZERO)
    for i,g in enumerate(w['compensation']): add('comp',i,g,g[0],C.ZERO)
    for i,g in enumerate(w['A']):
        if g[0]=='warp': add('A',i,g,'awarp',None)
        else: add('A',i,g,g[0],C.span(g[-1]))
    for i,g in enumerate(w['cut']): add('cut',i,g,g[0],None)
    at={}
    for k,rec in enumerate(w['warps'],1): at.setdefault(rec[0],[]).append(k)
    for p in range(len(w['B'])+1):
        for k in at.get(p,()):
            rec=w['warps'][k-1]; add('warp',k,['warp',rec[1],k],'warp',None)
        if p<len(w['B']):
            g=w['B'][p]; add('B',p,g,g[0],C.span(g[-1]))
    for i,g in enumerate(w['restore']): add('restore',i,g,g[0],C.span(g[-1]))
    return ev

def touched(e):
    g=e['g']
    if e['kind']=='corr': return (g['target'],g['source'])
    if e['kind'] in ('warp','awarp'): return (g[1],)
    return C.touched(g)

def writes(e,r):
    """Does the event change the value of register r?"""
    g=e['g']
    if e['kind']=='corr': return g['target']==r
    if e['kind'] in ('warp','awarp'): return g[1]==r
    if g[0]=='add': return g[1]==r
    if g[0]=='scale': return g[1]==r and not (g[2]==g[3])
    return False

def contacts(ev):
    out={}
    for e in ev:
        for r in touched(e): out.setdefault(r,[]).append(e['pos'])
    return out
