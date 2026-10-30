"""Reproduce the conditional kappa of one priced successor hand-off on PR5561's P104 word.  Apache-2.0.

Prepared for Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic), via Claude Code.
Checks:
 (1) byte pins of the inputs (SOURCES.json); handoff.py regenerates WORD.json.gz byte for byte;
 (2) edit inventory: the word differs from PR5561's headline word ONLY by moving one ADD
     (706 += -1/2*173) from event 17252 to directly after event 15443 with frame 127 -> 559,
     replacing the MOVE 706 549->127 by MOVE 706 549->559, and final[706] 127 -> 559;
     all other events, frames, ports, live list and endpoints (all 208 main registers) are equal;
 (3) the exact hand-off condition (exact rationals): after event 15443 no register but 706 holds
     symbol 706, row(706) = 706 + D with D = 1/2*row(173), row(173) is constant until event 17252,
     and 706 / 173 are idle at frames 549 < 559 (nested) at the insertion point;
 (4) UNMODIFIED PR5545 local.py replay, transposed columns, native maps; physical caller;
     PR5561's pricing.py with only the KAPPA/TESTED claim line and kappa_decimal label changed
     (LITERAL-CHANGES.diff); both moment engines; 54 strict + 4 functional outer checks; exact crossing;
 (5) mutation controls, each must be rejected by the unmodified local.py replay:
     no stop (ADD at 559 while 706 is still at 549), wrong coefficient, final not lowered,
     hand-off one event before the last read of 706.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import closure,need,load,read
import handoff as HO

INTERVAL=['154090925761/50000000000000','308181851523/100000000000000']
PINS={'inputs/pr5561-WORD.json.gz':'b3701d78bee3661382ebe5414e678dfc9ee292e254cb9dc56339c2d2f45fdf44',
      'inputs/pr5561-pricing.py':'701f87ebf3742d55f21ccdb2fd13d04fc2019a6b6190d8542bb7f5d477c71de5'}

def patch(text):
    for a,b in(("KAPPA, TESTED = Q('.00308142'), Q('.0030814205')","KAPPA, TESTED = Q('.00308181'), Q('.0030818105')"),
               ("'kappa_decimal':'.00308142'","'kappa_decimal':'.00308181'")):
        need(text.count(a)==1,'pinned pricing literal present once: '+a); text=text.replace(a,b)
    return text

def inventory(base,w):
    for k in('schema','public','live','ports','frames','initial'): need(base[k]==w[k],'unchanged '+k)
    diff=[r for r in range(base['public']) if base['final'][r]!=w['final'][r]]
    need(diff==[HO.H] and base['final'][HO.H]==127 and w['final'][HO.H]==HO.F,'only final[706] changes 127 -> 559')
    B,W=base['program'],w['program']
    need(len(B)==len(W),'same event count')
    need(W[:HO.T+1]==B[:HO.T+1],'prefix through event 15443 unchanged')
    need(W[HO.T+1:HO.T+3]==[['MOVE',HO.H,549,HO.F,False],['ADD',HO.H,HO.J,'-1/2',HO.F]],'inserted stop and moved ADD')
    need(W[HO.T+3:17253]==B[HO.T+1:17251] and W[17253:]==B[17253:],'all other events unchanged and in order')
    need(B[17251:17253]==[HO.OLD_MOVE,HO.OLD_ADD],'removed: MOVE 706 549->127 and its ADD @127')
    fr=[frozenset(_span(x)) for x in w['frames']]
    need(fr[549]<fr[HO.F]<fr[127],'549 < 559 < 127 strictly nested')
    return {'events':len(W),'changed_finals':diff,'moved_add':'17252 -> 15445','stop':'706: 549 -> 559 (dim 7 -> 8) replaces 549 -> 127 (dim 7 -> 9)'}

def _span(b):
    out={0}
    for v in b: out|={x^v for x in out}
    return out

def condition(w):
    """Exact rows of the pinned PR5561 word at the hand-off point."""
    P=w['program']; NP=w['public']
    rows=[{r:Q(1)} for r in range(NP+8)]; cur=list(w['initial'])+[None]*8
    snap=None
    for i,e in enumerate(P):
        op,r=e[:2]
        if op=='MOVE': cur[r]=e[3]
        elif op in('INIT','CLEAR'): rows[r]={}; cur[r]=e[2] if op=='INIT' else None
        elif op=='SCALE': rows[r]={k:Q(e[-2])*x for k,x in rows[r].items()}
        else:
            s=e[2];q=Q(e[-2])
            if op=='COPY': rows[r]={k:q*x for k,x in rows[s].items()}
            else:
                for k,x in rows[s].items():
                    v=rows[r].get(k,0)+q*x
                    if v: rows[r][k]=v
                    else: rows[r].pop(k)
        if i==HO.T:
            hold=[j for j in range(NP+8) if HO.H in rows[j]]
            need(hold==[HO.H],'no other holder of symbol 706 after its last read')
            D={k:x for k,x in rows[HO.H].items() if k!=HO.H}
            need(rows[HO.H].get(HO.H)==1 and D and D=={k:x/2 for k,x in rows[HO.J].items()},'row(706) = 706 + 1/2*row(173)')
            need(cur[HO.H]==549 and cur[HO.J]==HO.F,'706 at 549 and 173 at 559 at the hand-off point')
            snap=dict(rows[HO.J])
        if i==17251:
            need(rows[HO.J]==snap and cur[HO.J]==127,'row(173) unchanged until the original uncompute')
    return {'carried_symbols':len(D),'holders_of_706':1,'partner':'main register 173 (Y target of port register 61)'}

def chain(root,L,pricing_text,word,tag):
    sys.modules['local']=L;L.ROOT=root
    C=L.load(root/'research/p104-productive-controller/caller.py','p104_priced_handoff_caller_'+tag)
    tmp=HERE/('.pricing-'+tag+'.py');tmp.write_text(pricing_text)
    try: P=L.load(tmp,'p104_priced_handoff_pricing_'+tag)
    finally: tmp.unlink()
    loc=L.replay(word);print(tag,'PASS replay: paid',loc['paid'],'helpers',loc['helpers'],flush=True)
    L.reverse_columns(word);print(tag,'PASS transposed columns',flush=True)
    nat=L.native(word);print(tag,'PASS native maps',nat['distinct_maps'],'helpers',nat['helpers'],flush=True)
    ctl=C.construct();need(ctl==read(root/'research/p104-productive-controller/CONTROLLER.json'),'Exact complete caller')
    phys=C.physical(ctl,word);print(tag,'PASS physical caller',flush=True)
    return loc,P.run(loc,nat,ctl,phys)

def controls(L,base):
    bad={'no stop (ADD at 559 while 706 is at 549)':HO.handoff(base,stop=False),
         'wrong coefficient -1':HO.handoff(base,coef='-1'),
         'final not lowered':HO.handoff(base,lower_final=False)}
    early=HO.handoff(base); P=early['program']
    P.insert(HO.T,P.pop(HO.T+1)); P.insert(HO.T,P.pop(HO.T+2))   # stop and ADD before the last read
    bad['hand-off before the last read of 706']=early
    out={}
    for name,w in bad.items():
        try: L.replay(w)
        except ValueError as x: out[name]='rejected: '+str(x); print('control',name,'->',out[name],flush=True)
        else: raise ValueError('control accepted: '+name)
    return out

def main():
    for p,h in PINS.items(): need(sha256((HERE/p).read_bytes()).hexdigest()==h,'input pin '+p)
    base=read(HERE/'inputs/pr5561-WORD.json.gz'); word=read(HERE/'WORD.json.gz')
    need(HO.encoded(HO.handoff(base))==(HERE/'WORD.json.gz').read_bytes(),'handoff.py regenerates WORD.json.gz byte for byte')
    inv=inventory(base,word);print('PASS edit inventory',inv,flush=True)
    cond=condition(base);print('PASS exact hand-off condition',cond,flush=True)
    need((HERE/'pricing.py').read_text()==patch((HERE/'inputs/pr5561-pricing.py').read_text()),'pricing.py = PR5561 pricing.py + literal changes only')
    with closure() as root:
        L=load(root/'research/p104-productive-controller/local.py','local');L.ROOT=root
        ctl=controls(L,base)
        loc,res=chain(root,L,(HERE/'pricing.py').read_text(),word,'handoff')
    print('raw crossing interval',res['raw_root_interval'],flush=True)
    need(res['raw_root_interval']==INTERVAL,'exact crossing interval')
    need(res['productive_fields']==12814 and res['paid_calls']==66852 and res['rank_mass_surplus']==760,'invoice')
    need(len(res['outer']['strict_checks'])==54 and len(res['outer']['functional_checks'])==4,'outer inventory')
    need(all(Q(x)>0 for k in('strict_checks','functional_checks') for x in res['outer'][k].values()),'all outer checks strict')
    lo,hi=[Q(x) for x in INTERVAL]
    print('crossing kappa in (%.14f, %.14f); 54 strict + 4 functional outer checks pass'%(lo,hi),flush=True)
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps({'status':'PASS_P104_PRICED_HANDOFF_CONDITIONAL_KAPPA','inventory':inv,
            'condition':cond,'controls':ctl,'result':res},indent=1,sort_keys=True,default=str)+'\n')
    print('PASS P104_PRICED_HANDOFF')
main()
