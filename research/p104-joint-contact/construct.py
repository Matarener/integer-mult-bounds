"""Six source-pinned ADD contact changes on Ali Romman's PR5545 word.

Prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
The P104 supplier and controller retain their predecessor attribution.
"""
from copy import deepcopy

EDITS = {
    10461: (['ADD',297,303,'1',335],17),
    10462: (['ADD',303,297,'-1/2',335],17),
    13970: (['ADD',152,297,'-1/2',335],17),
    15479: (['ADD',198,319,'1',915],207),
    15639: (['ADD',205,198,'1',915],207),
    15640: (['ADD',198,205,'-1/2',915],207),
}

def need(ok,why):
    if not ok:
        raise ValueError(why)

def span(basis):
    out={0}
    for v in basis:
        need(v not in out,'Independent frame basis')
        out|={x^v for x in tuple(out)}
    return frozenset(out)

def construct(source):
    need(len(source['program'])==25310 and len(source['frames'])==1027,'Pinned source dimensions')
    for i,(expected,_) in EDITS.items():
        need(source['program'][i]==expected,'Exact source ADD at '+str(i))
    frames=[span(b)for b in source['frames']]
    current=list(source['initial'])+[None]*8
    out=[]
    def move(r,b):
        a=current[r]
        if a==b:
            return
        need(a is not None,'Initialized operand')
        need(frames[b]<frames[a]if r>=735 else frames[a]<frames[b],'Nested retimed transport')
        out.append(['MOVE',r,a,b,r>=735]);current[r]=b
    for i,e in enumerate(source['program']):
        op,r=e[:2]
        if op=='MOVE':
            continue
        if op=='INIT':
            need(current[r]is None,'Fresh owned lifetime')
            out.append(list(e));current[r]=e[2]
        elif op=='CLEAR':
            need(current[r]==e[2],'Owned chronology unchanged')
            out.append(list(e));current[r]=None
        elif op=='SCALE':
            out.append([*e[:-1],current[r]])
        else:
            need(op in ('ADD','COPY'),'Scalar opcode')
            f=EDITS[i][1]if i in EDITS else e[-1]
            for s in e[1:3]:
                move(s,f)
            out.append([*e[:-1],f])
    for r,f in enumerate(source['final']):
        move(r,f)
    word=deepcopy(source);word['program']=out
    signature=lambda w:[e[:-1]for e in w['program']if e[0]!='MOVE']
    need(signature(word)==signature(source),'Every scalar/owned coefficient and order retained')
    need(len(out)==25310,'Fixed complete word length')
    return word
