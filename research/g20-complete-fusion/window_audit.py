"""Second block enumeration and low-pivot historical span check."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import fusion as L


def run():
    word,owned,_,_=L.baseline();base,frames,_=L.source()
    rows=[1<<i for i in range(660)];segments={i:[] for i in range(658) if i not in owned}
    blocks=[];starts={}
    for ix,e in enumerate(word):
        op,d=e[:2]
        if op=='ADD' and e[2] in segments:
            blocks.append(segments[e[2]]);segments[e[2]]=[]
        if d in segments:
            segments[d].append((ix,e,rows[e[2]] if op=='ADD' else 0))
        if op=='ADD':rows[d]^=rows[e[2]]
        elif op=='ERASE':rows[d]=0
    blocks.extend(segments.values())
    expected={}
    for block in blocks:
        queries=[k for k,(_,e,_) in enumerate(block) if e[0]=='Q']
        for left,position in enumerate(queries):
            for right in queries[left+1:]:
                part=block[position:right+1];a,first,_=part[0];b,last,_=part[-1]
                ranks=[e[4] for _,e,_ in part if e[0]=='Q']
                L.SOURCE.Geometry(frames).nested(first[2],last[3],sum(ranks))
                target=0
                for _,e,r in part:
                    if e[0]=='ADD':target^=r
                key=(first[1],a,b);expected[key]=(first[2],target)
                starts.setdefault(a,[]).append(key)
    stored=L.read(L.R/'WINDOWS.json')['candidates']
    L.need(set(expected)=={(c['helper'],c['queries'][0],c['queries'][-1]) for c in stored},'Separate complete block inventory')
    bases={};rows=[1<<i for i in range(660)];st=base['final']+[None,None]
    def reduce(frame,row):
        for pivot,v in sorted(bases.get(frame,{}).items()):
            if row>>pivot&1:row^=v
        return row
    def observe(d):
        if st[d] is None:return
        residual=reduce(st[d],rows[d])
        if residual:bases.setdefault(st[d],{})[(residual&-residual).bit_length()-1]=residual
    for d in range(660):observe(d)
    hits=[]
    for ix,e in enumerate(word):
        for key in starts.get(ix,[]):
            frame,target=expected[key]
            if not reduce(frame,target):hits.append(key)
        op,d=e[:2]
        if op=='ADD':rows[d]^=rows[e[2]]
        elif op=='ERASE':rows[d]=0;st[d]=e[2]
        elif op=='INIT':st[d]=e[2]
        else:st[d]=e[3]
        observe(d)
    L.need(sorted(hits)==[(444,16157,19363),(465,16172,19222),(467,16151,19220)],'Separate historical span survivors')
    result={'status':'PASS_G20_FUSION_SEPARATE_667_BLOCK_AUDIT','blocks':len(expected),'survivors':hits}
    L.put('WINDOW-AUDIT.json',result);print(result['status']);return result


if __name__=='__main__':run()
