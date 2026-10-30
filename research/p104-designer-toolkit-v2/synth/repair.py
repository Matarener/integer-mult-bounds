"""synth.repair -- legaliser.  evaluate(word, profile) -> verdict dict (IncrWord = legal.check + native pairs + exact invoice).
repair(word, profile) -> (word', fixes, ok):  loop { IncrWord violations -> local fix by rule -> re-evaluate }, every fix logged as (round, rule, event, what).
Fix table (all are local MOVE edits; none changes a value, so the endpoint rows are untouched):
  Scalar destination and coefficient   register not at the op frame  -> insert the MOVE (ascending for public, descending for owned) just before the op
  Common scalar chart                  ADD/COPY source not at the op frame -> insert the MOVE of the source
  Nested chronological transport       MOVE between equal spans -> delete it;  descending public MOVE -> unrepairable (reported)
  Final frames                         register left below its declared final frame -> append the MOVE at the end
Everything else (inventory, owned lifetime census, endpoint rows, productive inputs, literal ports) is reported unrepaired: those are spec-level errors; the sampler counts them as illegal.
"""
import sys,os,collections
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from tkcommon import *
import incr
def evaluate(word,profile,iw_out=None):
    iw=incr.IncrWord(word,profile=profile)
    if iw_out is not None: iw_out.append(iw)
    return dict(legal=bool(iw.legal_all),kappa=iw.kappa,viol=[(v[0],v[1],str(v[2])[:120]) for v in iw.viol[:8]],n_viol=len(iw.viol),bad_pairs=len(iw.bad_pairs))
def _replay_cur(w,upto):
    cur=list(w['initial'])+[None]*64; owned=set()
    for e in w['program'][:upto]:
        if e[0]=='MOVE': cur[e[1]]=e[3]
        elif e[0]=='INIT': cur[e[1]]=e[2]; owned.add(e[1])
        elif e[0]=='CLEAR': cur[e[1]]=None; owned.discard(e[1])
    return cur,owned
def repair(word,profile,max_rounds=12,log=None):
    import copy
    w=dict(word); w['program']=[list(e) for e in word['program']]; w['frames']=[list(b) for b in word['frames']]
    fixes=[]
    for rnd in range(max_rounds):
        iw=incr.IncrWord(w,profile=profile)
        if iw.legal_all: return w,fixes,True
        sp=legal.spans(w); prog=w['program']; ed=[]       # (index, action, payload)
        for v in iw.viol:
            i,rule,det=v[0],v[1],v[2]
            if rule=='Scalar destination and coefficient':
                r,c,f=det
                if c is None: continue
                cur,owned=_replay_cur(w,i); pv=1 if r in owned else 0
                ok=(sp[f]<sp[c]) if pv else (sp[c]<sp[f])
                if ok: ed.append((i,'ins',['MOVE',r,c,f,pv],'MOVE reg %d %d->%d before op'%(r,c,f),r))
            elif rule=='Common scalar chart':
                r,s,cs,f=det
                if cs is None: continue
                cur,owned=_replay_cur(w,i); pv=1 if s in owned else 0
                ok=(sp[f]<sp[cs]) if pv else (sp[cs]<sp[f])
                if ok: ed.append((i,'ins',['MOVE',s,cs,f,pv],'MOVE src %d %d->%d before op'%(s,cs,f),s))
            elif rule=='Nested chronological transport' and i<len(prog):
                r,a,b,pv=det
                if sp[a]==sp[b]: ed.append((i,'del',None,'delete MOVE between equal spans reg %d'%r,('d',i)))
            elif rule=='Final frames' and False: pass
        # end-of-program: declared final frames
        cur,owned=_replay_cur(w,len(prog))
        for r in range(len(w['initial'])):
            if cur[r] is not None and cur[r]!=w['final'][r] and sp[cur[r]]<sp[w['final'][r]]:
                ed.append((len(prog),'ins',['MOVE',r,cur[r],w['final'][r],0],'final MOVE reg %d'%r,('f',r)))
        # native pair failures: merge  MOVE a->b ; MOVE b->c  (no event of the register in between) into  MOVE a->c
        if iw.bad_pairs:
            bad=set(iw.bad_pairs); drop=set(); done_regs=set()
            for i,e in enumerate(prog):
                if e[0]=='MOVE' and (e[2],e[3]) in bad and e[1] not in done_regs and i not in drop:
                    r=e[1]
                    for j in range(i+1,len(prog)):
                        f=prog[j]
                        if f[1]==r or (f[0] in('ADD','COPY') and f[2]==r):
                            if f[0]=='MOVE' and f[2]==e[3] and f[4]==e[4]:
                                ed.append((i,'set',['MOVE',r,e[2],f[3],e[4]],'merge MOVEs reg %d %d->%d->%d (native-bad pair %d->%d)'%(r,e[2],e[3],f[3],e[2],e[3]),('n',i)));
                                ed.append((j,'del',None,'  (second half)',('n',j))); done_regs.add(r)
                            break
        if not ed: return w,fixes,False
        first={}
        for e_ in sorted(ed,key=lambda x:x[0]): first.setdefault(e_[4],e_)       # one fix per register per round (later violations of the register are usually consequences)
        for i,act,pay,what,_k in sorted(first.values(),key=lambda x:-x[0]):
            if act=='ins': prog.insert(i,pay)
            elif act=='set': prog[i]=pay
            else: prog.pop(i)
            fixes.append((rnd,act,i,what))
    iw=incr.IncrWord(w,profile=profile); return w,fixes,bool(iw.legal_all)
