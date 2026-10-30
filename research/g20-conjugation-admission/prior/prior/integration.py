"""Emit and audit Dugongue PR5665 late binding on the complete PR5667 word.

Retain all source and matcher credit. Ali Romman with substantial OpenAI
Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
import gzip,importlib.util,json,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
S=R/'prior/source/vendor/g20'
PARTIAL=frozenset([462,463,466,468])
LATE=frozenset([223,319,331,344,371,375,484,501,551])
RETIRED=PARTIAL|frozenset(range(469,478))|LATE


def need(condition,message):
    if not condition:raise ValueError(message)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def put(name,value):
    raw=(json.dumps(value,indent=2)+'\n').encode();path=R/name
    path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


for item in read(R/'INPUTS.json'):
    need(sha256((R/item['local']).read_bytes()).hexdigest()==item['sha256'],'Frozen input '+item['local'])
SOURCE=load('retained_g20_source',R/'prior/source/local_relations.py')
source=SOURCE.source


def matcher(frames,word):
    record=read(R/'prior/audited/RESULT.json')['matcher']
    w=[[F(x) for x in row] for row in record['forward']]
    wi=[[F(x) for x in row] for row in record['inverse']]
    frame=frames['506']
    need(w==list(map(list,zip(*[list(map(F,row)) for row in frame['B']+frame['A']]))),'Actual frame-506 basis')
    def product(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
    eye=[[F(i==j) for j in range(8)] for i in range(8)]
    need(product(w,wi)==eye and product(wi,w)==eye,'Both actual matcher directions')
    need(all(sum(F(x)*F(y) for x,y in zip(a,b))==0 for a in frame['A'] for b in frame['B']),'Orthogonal residual/complement')
    count=sum(e[0]=='Q' and e[2:]==[506,0,4] for e in word['records'])
    need(count==4 and record['common_denominator']==4,'New actual matcher occurrences and dyadic denominator')
    out=dict(record,local_occurrences=count,global_occurrences=18*count,
             paired_address_coefficient_terms_per_call=2*record['nonzero_coefficients'],
             pricing='Both directions and both paired address halves are charged inside the complete positive normalizer fee.')
    put('MATCHER.json',out);return out


def census(word,expected_positive):
    from collections import Counter
    es=word['records'];out=[]
    for h in sorted(set(range(222,658))-set(word['owned'])):
        refs=[(i,e) for i,e in enumerate(es) if e[1]==h or e[0]=='ADD' and e[2]==h]
        reads=[(i,e) for i,e in refs if e[0]=='ADD' and e[2]==h]
        if not reads:
            out.append(dict(helper=h,rejected='no outgoing ADD'));continue
        first,e=reads[0];y,f=e[1],e[3];lo,hi=first,first+1
        while lo and es[lo-1][0]=='ADD' and es[lo-1][1]==y and es[lo-1][3]==f:lo-=1
        while hi<len(es) and es[hi][0]=='ADD' and es[hi][1]==y and es[hi][3]==f:hi+=1
        nxt=next(((i,a) for i,a in enumerate(es[hi:],hi) if a[1]==y),None)
        if not nxt or nxt[1][0]!='Q':
            out.append(dict(helper=h,rejected='next receiver write is not a paid query'));continue
        before=[(i,a) for i,a in refs if i<first]
        need(all(a[1]==h and a[0] in ['Q','ADD'] for i,a in before),'Unobserved invertible helper prefix')
        qs=[a[4] for i,a in before if a[0]=='Q'];rank=nxt[1][4]
        out.append(dict(helper=h,receiver=y,frame=f,cut=first,block=[lo,hi],zero_query=nxt[0],
                        prefix_ranks=qs,receiver_rank=rank,rank_balance=sum(qs)+rank-8,
                        removed_prefix_events=[i for i,a in before]))
    positive=[a for a in out if a.get('rank_balance')==0]
    need({a['helper']for a in positive}==set(expected_positive),'Complete first-read candidate domain')
    need(all(a['prefix_ranks']==[1] and a['receiver_rank']==7 for a in positive),'Exact profitable split')
    need(all(a.get('rank_balance',-1)<=0 for a in out),'No omitted positive rank surplus')
    # For 0<C<1/100, 8^(1-C)>7. Integer exponent comparison avoids logs.
    need(8**99>7**100,'All negative-rank candidates lose throughout stated interval')
    return out,positive


def construct(old):
    allcuts,cuts=census(old,LATE);es=old['records'];skip=set();replacements={};zero=set();frames=old['start'][:]
    for c in sorted(cuts,key=lambda c:c['cut']):
        h,y,f=c['helper'],c['receiver'],c['frame'];lo,hi=c['block'];block=es[lo:hi]
        need(len(block)==3 and sum(e[2]==h for e in block)==1,'Literal three-donor cut')
        need(all(e[2] not in LATE-{h} for e in block),'Other cut donors remain retained')
        need(not set(range(lo,hi))&skip,'Disjoint reordered blocks')
        skip.update(c['removed_prefix_events']);skip.update(range(lo,hi));zero.add(c['zero_query'])
        replacements[lo]=[e[:] for e in block if e[2]!=h]+[['INIT',h,f],['ADD',h,y,f],['ADD',y,h,f]]
    result=[['ERASE',h,old['start'][h]] for h in sorted(LATE)]
    for i,e in enumerate(es):
        if i in replacements:result.extend(replacements[i])
        if i in skip:continue
        result.append(['ZERO_Q']+e[1:] if i in zero else e[:])
    result.extend([['ERASE',h,old['final'][h]] for h in sorted(LATE)])
    return dict(old,records=result,owned=sorted(set(old['owned'])|LATE)),allcuts,cuts


def source_rows(cuts):
    forward=read(R/'FORWARD.json.gz')['records']
    rows=[(185,371,599,9660,8562,8568,8565),(183,344,597,9637,8548,8552,8549),
          (177,484,591,9742,8506,8510,8507),(172,319,586,9618,8471,8476,8473),
          (171,331,585,9627,8464,8469,8466),(157,375,571,9662,8366,8370,8367),
          (133,551,547,9792,8198,8204,8201),(120,501,534,9753,8107,8113,8110),
          (114,223,528,9546,8065,8071,8068)]
    evidence=[]
    for y,h,f,terminal,main,first,nxt in rows:
        need(forward[first]==['ADD',y,h,f],'Literal proposal first read')
        need(forward[terminal]==['Q',h,f,1,1] and forward[main]==['Q',y,0,f,7], 'Literal removed queries')
        refs=[(i,e) for i,e in enumerate(forward) if e[1]==h or e[0]=='ADD' and e[2]==h]
        need(all(e[1]==h for i,e in refs if i>first),'No earlier inverse outgoing read')
        need([e for i,e in refs if i>first and e[0]=='Q']==[forward[terminal]],'Only one unobserved native query')
        need(forward[nxt][0]=='Q' and forward[nxt][1]==h and forward[nxt][3:]==[f,1],'Retained suffix query')
        evidence.append(dict(helper=h,receiver=y,frame=f,terminal=terminal,main=main,first_read=first,next_query=nxt))
    need({r['helper'] for r in evidence}=={r['helper']for r in cuts},'Proposal and executed census agree')
    return evidence


def run():
    import native
    old=read(R/'prior/WORD.json.gz');word,allcuts,cuts=construct(old);base,frames,_=source()
    source_evidence=source_rows(cuts)
    result=native.replay(base,frames,word['records'],set(word['owned']))
    physical=[native.replay(base,frames,word['records'],set(word['owned']),m) for m in (101,101**2)]
    need(result['paid']=={1:1279,2:1342,3:56,4:57,5:102,6:10},'Exact paid complement removal')
    need(len(word['owned'])==48 and result['retained_originals']==636,'Actual required owned reserve')
    m=matcher(frames,word);controls=[]
    for c in cuts:
        bad=[e[:]for e in word['records']];op=['ADD',c['helper'],c['receiver'],c['frame']];bad.pop(bad.index(op))
        try:native.replay(base,frames,bad,set(word['owned']),101)
        except ValueError:controls.append('missing_binding_'+str(c['helper']))
        else:raise ValueError('Missing binding accepted')
    for label,op in [('dirty_entrance',['ERASE',371,old['start'][371]]),('missing_return',['ERASE',371,old['final'][371]])]:
        bad=[e[:]for e in word['records']];bad.pop(bad.index(op))
        try:native.replay(base,frames,bad,set(word['owned']),101)
        except ValueError:controls.append(label)
        else:raise ValueError('Owned control accepted')
    after,_=census(word,set());put('WORD.json.gz',word);put('CUTS.json',dict(all_candidates=allcuts,selected=cuts,after_candidates=after,proposal_source_rows=source_evidence))
    data=dict(status='PASS_G20_LATE_BINDING_NATIVE_ALL684_COLUMNS',stats=result,native_moduli=[v['native_modulus']for v in physical],
              matcher=m,candidate_helpers=len(allcuts),profitable_cuts=len(cuts),rejected_controls=controls,
              canonical_word_sha256=sha256(json.dumps(word['records'],separators=(',',':')).encode()).hexdigest())
    put('LOCAL-RESULT.json',data);return data


if __name__=='__main__':print(json.dumps(run(),indent=2))
