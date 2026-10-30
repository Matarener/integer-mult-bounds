"""Independent literal candidate walk and focused actual invalid-word controls.

No constructor imports, source search, native engine, or pricing dependencies.
Prepared with substantial OpenAI Codex assistance for flyingviper. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction

def need(ok,message):
    if not ok:raise ValueError(message)

def binary_span(basis):
    result={0}
    for x in basis:
        need(type(x) is int and 0<x<512 and x not in result,'Independent binary frame')
        result|={v^x for v in tuple(result)}
    return result

def audit(word):
    n=word['public'];owned=word['owned_fields'];size=n+owned
    need(n==744 and owned==9,'Exact independent/owned inventory')
    need(len(word['initial'])==len(word['final'])==n,'Boundary inventory')
    frames=[binary_span(x) for x in word['frames']]
    charts=word['initial']+[None]*owned
    values=[{i:Fraction(1)} for i in range(size)]
    active=set();unwritten=set();lifetimes=peak=scalar=0;paid=Counter()
    for e in word['program']:
        op,dst=e[:2]
        need(type(dst) is int and 0<=dst<size,'Destination inventory')
        if op=='INIT':
            need(dst>=n and charts[dst] is None,'Owned INIT uses an inactive owned label')
            active.add(dst);unwritten.add(dst);charts[dst]=e[2];values[dst]={}
            lifetimes+=1;peak=max(peak,len(active));scalar+=2
        elif op=='CLEAR':
            need(dst in active and charts[dst]==e[2],'Matching owned CLEAR')
            active.remove(dst);unwritten.discard(dst);charts[dst]=None;values[dst]={};scalar+=2
        elif op=='MOVE':
            _,_,a,b,private=e
            need(charts[dst]==a and private==(dst in active),'MOVE source and ownership')
            need(frames[b]<frames[a] if private else frames[a]<frames[b],'Strict native containment')
            charts[dst]=b;paid[abs(len(word['frames'][a])-len(word['frames'][b]))]+=1
        else:
            need(op in ('ADD','COPY','SCALE') and charts[dst]==e[-1],'Scalar destination coframe')
            q=Fraction(e[-2]);a,b=abs(q.numerator),q.denominator
            need(q and b&(b-1)==0 and abs(q)+1<2**16,'Literal dyadic coefficient allowance')
            if op=='SCALE':
                need(a&(a-1)==0,'Dyadic unit SCALE')
                values[dst]={i:q*x for i,x in values[dst].items()}
                scalar+=2*(abs(a.bit_length()-b.bit_length())+(q<0))
            else:
                src=e[2]
                need(type(src) is int and 0<=src<size and src!=dst and charts[src]==e[-1], 'Scalar source coframe')
                if op=='COPY':
                    need(dst in unwritten and dst in active,'COPY into a newly initialized owned field')
                    values[dst]={}
                for i,x in tuple(values[src].items()):
                    value=values[dst].get(i,Fraction(0))+q*x
                    if value:values[dst][i]=value
                    else:values[dst].pop(i,None)
                scalar+=2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)
            unwritten.discard(dst)
    need(not active and charts[:n]==word['final'],'All declared final charts and owned exits')
    for r,value in enumerate(values):
        expected={r:Fraction(1)} if r<n else {}
        if r-112 in word['live']:expected[r-112]=Fraction(1)
        need(value==expected,'Exact arbitrary-input endpoint row '+str(r))
    main=set(word['live'])|{r+112 for r in word['live']}
    targets=Counter(len(word['frames'][word['final'][r]])-len(word['frames'][word['initial'][r]]) for r in range(n) if r not in main)
    need(lifetimes==11 and peak==2,'Retained owned lifetime and peak contract')
    need(paid==Counter({1:2184,2:459,3:495,4:92,5:159,6:22,7:15}),'Complete local paid inventory')
    need(targets==Counter({1:2,2:5,4:91,5:6,7:6,8:15,9:411}),'Complete local target inventory')
    need(scalar==221474,'Literal ordinary scalar allowance')
    return dict(status='PASS_ALL_SCALAR_INPUTS_FRAMES_OWNERSHIP_INVOICES',columns=size,paid=dict(paid),targets=dict(targets),scalar=scalar,owned_lifetimes=lifetimes,owned_peak=peak)

def transpose_audit(word):
    public=word['public'];size=public+word['owned_fields']
    columns=[{r:Fraction(1)} for r in range(size)]
    for event in reversed(word['program']):
        op,target=event[:2]
        if op=='MOVE':continue
        if op in ('INIT','CLEAR'):columns[target]={}
        elif op=='SCALE':columns[target]={r:Fraction(event[-2])*x for r,x in columns[target].items()}
        else:
            source=event[2];coefficient=Fraction(event[-2])
            for row,value in tuple(columns[target].items()):
                result=columns[source].get(row,Fraction(0))+coefficient*value
                if result:columns[source][row]=result
                else:columns[source].pop(row,None)
            if op=='COPY':columns[target]={}
    for source,col in enumerate(columns):
        expected={source:Fraction(1)} if source<public else {}
        if source in word['live']:expected[source+112]=Fraction(1)
        need(col==expected,'Exact backward arbitrary-input column '+str(source))
    return dict(status='PASS_ALL_TRANSPOSE_COLUMNS',columns=size)

def negative_controls(word,witness):
    fresh=word['public']-1
    retirement=['ADD',708,154,'1/2',602]
    restore126=['ADD',126,fresh,'2',127]
    restore188=['ADD',188,fresh,'-2',127]
    inverse=['ADD',fresh,146,'-1/2',127]
    need(word['program'].count(retirement)==word['program'].count(restore126)==word['program'].count(restore188)==word['program'].count(inverse)==1,'Unique actual construction events')
    mutants={}
    x=deepcopy(word);x['program'].remove(retirement);mutants['omit_original_retirement']=x
    x=deepcopy(word);x['program'].remove(restore126);mutants['omit_early126_restoration']=x
    x=deepcopy(word);x['program'].remove(restore188);mutants['omit_early188_restoration']=x
    x=deepcopy(word);x['program'].remove(inverse);mutants['omit_current146_inverse']=x
    x=deepcopy(word);x['program'][x['program'].index(inverse)][3]='1/2';mutants['wrong_current146_inverse_sign']=x
    x=deepcopy(word);at=x['program'].index(restore126);x['program'][at:at+3]=[inverse,restore126,restore188];mutants['inverse_before_normalizing126188']=x
    x=deepcopy(word);x['program'].insert(x['program'].index(retirement)+1,['ADD',fresh,154,'-1/2',602]);mutants['reintroduce_obsolete_decoder']=x
    x=deepcopy(word);next(e for e in x['program'] if e[0]=='INIT')[1]-=1;mutants['omit_owned_identifier_shift']=x
    x=deepcopy(word);x['final'][708]=127;mutants['restore_uncharged_old_H9_target']=x
    x=deepcopy(word);x['initial'][fresh]=3;mutants['wrong_new_helper_boundary']=x
    reasons={}
    for name,mutant in mutants.items():
        try:audit(mutant)
        except ValueError as error:reasons[name]=str(error)
        else:raise ValueError('Invalid actual candidate accepted: '+name)
    return reasons
