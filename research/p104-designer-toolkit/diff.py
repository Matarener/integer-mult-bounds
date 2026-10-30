"""tk diff A B [--json]   what changed between two words (aliases or paths).
Reports: sizes; kappa; invoice (paid-call histogram by rank, credited-helper rank histogram, fields/calls); event-level diff (events aligned by op/register/
coefficient ignoring frame labels): events added/removed by op and register role, MOVE stops deleted/added, scalar program identical or not; frame
relabels on aligned events (frames compared as SPANS, not ids); endpoint changes per role (X initial / X final / Y initial / Y final / helper start / helper final)
with start/final dimension histograms; number of distinct frame spans."""
import difflib,collections,json
from tkcommon import *
import price as PR
def sig(e):
    op=e[0]
    if op=='MOVE': return ('MOVE',e[1],e[4])
    if op in('INIT','CLEAR'): return (op,e[1])
    return tuple(e[:-1])                       # ADD/COPY/SCALE minus trailing frame label
def lab_fields(e):
    if e[0]=='MOVE': return (2,3)
    if e[0] in('INIT','CLEAR'): return (2,)
    return (len(e)-1,)
def hist(it): return dict(sorted(collections.Counter(it).items()))
def hdiff(a,b): return {k:(a.get(k,0),b.get(k,0)) for k in sorted(set(a)|set(b)) if a.get(k,0)!=b.get(k,0)}
def compare(wa,wb,pa,pb):
    ra,rb=roles(wa),roles(wb); na,nb=len(wa['initial']),len(wb['initial'])
    fa,fb=legal.spans(wa),legal.spans(wb)
    A,B=wa['program'],wb['program']; sa=[sig(e) for e in A]; sb=[sig(e) for e in B]
    sm=difflib.SequenceMatcher(None,sa,sb,autojunk=False)
    out=dict(sizes=dict(regs=(na,nb),events=(len(A),len(B)),frames_listed=(len(wa['frames']),len(wb['frames'])),
                        distinct_spans_used=(len({fa[i] for e in A for i in lab_fields(e) if e[0]!='MOVE' or True for i in [e[i]] }),len({fb[e[i]] for e in B for i in lab_fields(e)}))))
    ca,cb=PR.fast(pa,wa),PR.fast(pb,wb)
    out['kappa']=(ca['kappa'],cb['kappa'],float(cb['kappa'])-float(ca['kappa']))
    out['legal']=(ca['legal'],cb['legal'])
    out['invoice']=dict(paid_hist_changes=hdiff({int(k):v for k,v in ca['paid'].items()},{int(k):v for k,v in cb['paid'].items()}),
                        helper_rank_changes=hdiff({int(k):v for k,v in ca['helpers'].items()},{int(k):v for k,v in cb['helpers'].items()}),
                        fields=(ca['sumT'],cb['sumT']),paid_calls=(ca['sumP'],cb['sumP']),surplus=(ca['surplus'],cb['surplus']))
    rem=collections.Counter();add=collections.Counter();relab=collections.Counter();same=0
    mv_rem=collections.Counter();mv_add=collections.Counter()
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal':
            for i,j in zip(range(i1,i2),range(j1,j2)):
                e,f=A[i],B[j]; same+=1
                ch=[fa[e[k]]!=fb[f[k]] for k in lab_fields(e)]
                if any(ch): relab[(e[0],'main' if ra(e[1]) in('X','Y') else ra(e[1]))]+=1
        else:
            for e in A[i1:i2]:
                rem[e[0]]+=1
                if e[0]=='MOVE': mv_rem[ra(e[1])]+=1
            for e in B[j1:j2]:
                add[e[0]]+=1
                if e[0]=='MOVE': mv_add[rb(e[1])]+=1
    nonmove=lambda c:sum(v for k,v in c.items() if k!='MOVE')
    out['events']=dict(aligned=same,removed=dict(rem),added=dict(add),moves_removed_by_role=dict(mv_rem),moves_added_by_role=dict(mv_add),
                       scalar_program_identical=(nonmove(rem)==0 and nonmove(add)==0),aligned_events_relabelled=dict((f'{k[0]}:{k[1]}',v) for k,v in relab.items()))
    # endpoint changes
    ch=collections.Counter(); dims=dict(start_a=[],start_b=[],final_a=[],final_b=[])
    for r in range(min(na,nb)):
        role=ra(r)
        if fa[wa['initial'][r]]!=fb[wb['initial'][r]]: ch[role+' initial']+=1
        if fa[wa['final'][r]]!=fb[wb['final'][r]]: ch[role+' final']+=1
        if role=='helper':
            dims['start_a'].append(len(wa['frames'][wa['initial'][r]]));dims['start_b'].append(len(wb['frames'][wb['initial'][r]]))
            dims['final_a'].append(len(wa['frames'][wa['final'][r]]));dims['final_b'].append(len(wb['frames'][wb['final'][r]]))
    out['endpoints_changed']=dict(ch)
    out['helper_dims']=dict(start=hdiff(hist(dims['start_a']),hist(dims['start_b'])),final=hdiff(hist(dims['final_a']),hist(dims['final_b'])))
    out['budgets']=dict(event_slack=(ca['budgets']['event_slack'],cb['budgets']['event_slack']),scalar_slack=(ca['budgets']['scalar_budget_slack'],cb['budgets']['scalar_budget_slack']))
    return out
def main(a):
    pa,wa=load(a.a);pb,wb=load(a.b); o=compare(wa,wb,pa,pb)
    if a.json: print(json.dumps(o,indent=1,default=str)); return
    s=o['sizes']; print('regs %s  events %s  frames listed %s'%(s['regs'],s['events'],s['frames_listed']))
    k=o['kappa']; print('kappa %s -> %s  (delta %+.4e)   legal %s'%(k[0],k[1],k[2],o['legal']))
    i=o['invoice']; print('invoice: fields %s  paid calls %s  surplus %s'%(i['fields'],i['paid_calls'],i['surplus']))
    print('  paid-call histogram changes (rank:(A,B)):',i['paid_hist_changes']); print('  credited helper rank changes:',i['helper_rank_changes'])
    e=o['events']; print('events: aligned %d, removed %s, added %s; scalar program identical: %s'%(e['aligned'],e['removed'],e['added'],e['scalar_program_identical']))
    print('  MOVEs removed by role %s, added %s; aligned events with relabelled frames %s'%(e['moves_removed_by_role'],e['moves_added_by_role'],e['aligned_events_relabelled']))
    print('endpoint spans changed:',o['endpoints_changed']); print('helper start-dim changes',o['helper_dims']['start'],' final-dim changes',o['helper_dims']['final'])
    print('budget slack (A,B):',o['budgets'])
