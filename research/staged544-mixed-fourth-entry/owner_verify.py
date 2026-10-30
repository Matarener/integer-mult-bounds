"""Complete literal mixed-provider owner audit; no optimizer is required.

Window and charge rules follow PR3945/4076; new mixed dispatch binding and
scan by Cinna Davis with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter,defaultdict
import sys,time
from verify import P,read,need,pins,I,reject

def context():
    order=read(P/'owner/ORDER.json');clock={tuple(v):t for t,v in enumerate(order)}
    need(len(order)==3240 and set(clock)=={(s,r) for s in range(9) for r in range(360)},'all calls')
    need(all(clock[s,r]<clock[s+1,r] for r in range(360) for s in range(8)),'source order')
    template=read(P/'owner/TEMPLATE.json.gz');plan=read(P/'owner/PLAN.json.gz')
    children={x['child']:x['rank'] for x in template['idle_children']}
    pair={x['stage']:x['pair'] for x in template['recipe'] if x['kind']=='local'}
    family={c:2*plan['pairs'][str(c)]+plan['sides'][str(c)] for c in children}
    windows={}
    for o in range(360):
        touched={};tick=None
        for e in template['execution_schedule']:
            k=e['kind']
            if k=='local_cover_sweep':tick=clock[e['stage'],o];touched[pair[e['stage']]]=tick
            elif k=='bridge':touched[e['src']]=tick;touched[e['dst']]=tick
            elif k=='idle_cover_sweep':
                for c in e['child_indices']:
                    if c in children:
                        need((o,c) not in windows,'duplicate owner child');windows[o,c]=(children[c],touched.get(e['pair'],-1),tick)
            else:need(k in ['bank_padding_cover_sweep','translate_every_live_family','terminal_Y_translations','terminal'],'schedule kind')
    shared=defaultdict(list)
    for (o,c),(_,lo,hi) in windows.items():shared[o,family[c]].append((lo,hi))
    need(all(all(max(a,c)>=min(b,d) for i,(a,b) in enumerate(xs) for c,d in xs[i+1:]) for xs in shared.values()),'same-family windows disjoint')
    old=read(P/'owner/DISPATCH.json');new=read(P/'owner/MIXED-DISPATCH.json')
    expected=[[s,r,pid+('-four' if clock[s,r]*109%324<109 else '')] for s,r,pid in old]
    need(new==expected,'exact mixed dispatch')
    provider={(s,r):pid for s,r,pid in new}
    need(len(provider)==3240 and set(provider)==set(clock),'dispatch coverage')
    widths={};local={}
    for tag,pid in [('base','gauge44'),('extra','extra')]:
        origin=read(P/f'owner/old-NATIVE-{tag}.json.gz')['helper_origin']
        for kind,suffix in [('THREE',''),('FOUR','-four')]:
            w=read(P/f'inputs/{kind}-{tag}.json.gz')
            need(origin==sorted(set(range(224,704))-set(w['removed'])),'native helper order')
            widths[pid+suffix]=[len(I.b(w['helper_final'].get(str(r),I.FULL)))-len(I.b(w['start_extra'].get(str(r),[]))) for r in origin]
            local[pid+suffix]={int(k):v for k,v in w['report']['local_profile'].items()}
    return order,provider,windows,family,widths,local

def walk(rows,ctx):
    order,provider,windows,family,widths,local=ctx
    need(len(rows)==3240*408,'role coverage');used={};families=set()
    for j,row in enumerate(rows):
        need(len(row)==6 and all(type(v) is int for v in row),'integer row')
        t,h,o,c,p,z=row;need(t==j//408 and h==j%408,'helper identity')
        if h==0:families=set()
        need((o,c) in windows and 0<=p<112,'owner bin')
        cap,lo,hi=windows[o,c];need(lo<t<=hi,'chronology')
        f=(o,family[c],p);need(f not in families,'same-call family');families.add(f)
        key=(o,c,p);prefix=used.get(key,0);need(z==prefix,'compact offset')
        width=widths[provider[tuple(order[t])]][h]
        need(prefix+width<=cap,'capacity');used[key]=prefix+width
    idle=Counter()
    for (o,c),(cap,lo,hi) in windows.items():
        for p in range(112):
            left=cap-used.get((o,c,p),0)
            if left:idle[left]+=1
    profile=Counter(idle)
    for call in order:profile.update(local[provider[tuple(call)]])
    need(sum(r*n for r,n in profile.items())==65088*360,'complete rank mass')
    return dict(sorted(profile.items())),dict(sorted(idle.items()))

def controls(rows,ctx):
    out=[]
    original=rows[0][5];rows[0][5]+=1
    try:out.append(reject('offset_hole',lambda:walk(rows,ctx)))
    finally:rows[0][5]=original
    original=rows[1][:];rows[1][2:5]=rows[0][2:5]
    try:out.append(reject('same_call_family',lambda:walk(rows,ctx)))
    finally:rows[1][:]=original
    original=rows[0][:];o,c=next(k for k,v in ctx[2].items() if v[1]>=0);rows[0][2:4]=[o,c]
    try:out.append(reject('closed_window',lambda:walk(rows,ctx)))
    finally:rows[0][:]=original
    provider=ctx[1];call=tuple(ctx[0][0]);old=provider[call];need(old.endswith('-four'),'control selects fourth call');provider[call]=old.removesuffix('-four')
    try:out.append(reject('omit_fourth_provider',lambda:walk(rows,ctx)))
    finally:provider[call]=old
    return out

def main():
    start=time.monotonic();pins();ctx=context();fill=read(P/'owner/FILL.json.gz');need(fill['dispatch_overrides']==[],'separate explicit dispatch')
    rows=fill['rows'];profile,idle=walk(rows,ctx);r=read(P/'RESULT.json')
    need(profile=={int(k):v for k,v in r['profile'].items()},'full paid histogram')
    need(idle=={int(k):v for k,v in r['idle'].items()},'idle histogram')
    out={'status':'PASS_MIXED_LITERAL_OWNER','calls':3240,'fourth_calls':sum(pid.endswith('-four') for pid in ctx[1].values()),'roles':len(rows),'physical_bins':len(ctx[2])*112,'profile':profile,'idle':idle,'controls':controls(rows,ctx) if '--controls' in sys.argv else [],'seconds':time.monotonic()-start}
    print(__import__('json').dumps(out,sort_keys=True))
if __name__=='__main__':main()
