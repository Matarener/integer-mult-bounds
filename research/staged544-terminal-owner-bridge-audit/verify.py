"""Independent PR3945 owner bridge. Chris R/Clear1nsight, Codex; Apache-2.0.
No predecessor checker imports. Frames are explicit point sets; owner blocks
are coordinate bitmaps; free semantics are exact interleaved program identity.
"""
import argparse, gzip, hashlib, json
from pathlib import Path
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok: raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
@lru_cache(None)
def span(rows):
    points={0}
    for v in rows:
        need(type(v) is int and 0<=v<512,'frame alphabet')
        points|={x^v for x in points}
    return frozenset(points)
def space(rows):return span(tuple(rows))
def dim(s):
    n=len(s);need(n>0 and n&(n-1)==0,'subspace cardinality');return n.bit_length()-1
FULL=frozenset(range(512))
@lru_cache(None)
def permutation(columns):
    need(len(columns)==9,'matrix shape');out=[]
    for x in range(512):
        y=0
        for j,c in enumerate(columns):
            if x&(1<<j):y^=c
        out.append(y)
    need(set(out)==set(range(512)),'singular native matrix');return tuple(out)
def warp(w,g):
    _,r,i=g[:3];U=g[3];E=g[4] if len(g)==5 else U;p=permutation(tuple(w['warps'][abs(i)-1][2]))
    if i<0:
        inv=[0]*512
        for x,y in enumerate(p):inv[y]=x
        p=tuple(inv)
    return r,p,space(U),space(E)
def postcut(w):
    out=[]
    for i in range(len(w['B'])+1):
        for j,row in enumerate(w['warps']):
            if row[0]==i:out.append(['warp',row[1],j+1,row[3],row[4]])
        if i<len(w['B']):out.append(w['B'][i])
    return out+w['restore']
def tokens(w,seq):
    out=[]
    for g in seq:
        if g[0]=='warp':
            r,p,_,_=warp(w,g);out.append(['warp',r,list(p)])
        elif g[0]=='add':out.append(['add',g[1],g[2],str(Fraction(g[3],g[4]))])
        else:
            need(g[0]=='scale','opcode');q=Fraction(g[2],g[3])
            if q!=1:out.append(['scale',g[1],str(q)])
    return out
def identity(old,new):
    changes={'A','B','restore','cleanup','helper_final','warps','report'}
    need(set(old)==set(new),'word schema')
    for field in set(old)-changes:need(old[field]==new[field],'caller field '+field)
    a=[tokens(old,s) for s in [old['A'],postcut(old),old['cut'],old['cleanup']]]
    b=[tokens(new,s) for s in [new['A'],postcut(new),new['cut'],new['cleanup']]]
    need(a==b,'interleaved free program differs')
    return {'token_counts':list(map(len,a)),'program_sha256':sha(canon(a)),
      'scope':'Exact free program identity after deletion of identity scales; includes native permutations at actual cuts and private-buffer scalar cleanup. Native phases excluded.'}
def invoice(w):
    live=sorted(set(range(704))-set(w['removed']))
    start={r:space([w['ports'][r]]) if r<112 else space([]) for r in live}
    start.update({int(r):space(F) for r,F in w['start_extra'].items()})
    end={r:FULL if r<112 or r>=224 else frozenset(x for x in range(512) if (x&w['ports'][r-112]).bit_count()%2==0) for r in live}
    end.update({int(r):space(F) for r,F in w['helper_final'].items()})
    current=dict(start);paid=Counter();trace=[]
    def climb(r,F,label):
        need(current[r]<=F,'unpaid nonmonotone frame '+label)
        d=dim(F)-dim(current[r]);current[r]=F
        if d:paid[d]+=1;trace.append([label,r,d])
    def gate(g,label):
        if g[0]=='warp':
            r,p,U,E=warp(w,g);need(current[r]==U,'native entrance '+label)
            need(frozenset(p[x] for x in U)==E,'native transport '+label);current[r]=E
        else:
            need(g[0] in ('add','scale'),'scalar opcode')
            for r in g[1:3] if g[0]=='add' else g[1:2]:climb(r,space(g[-1]),label)
    for i,g in enumerate(w['A']):gate(g,'A:'+str(i))
    for r in range(112,224):need(current[r]==space(w['target_levels'].get(str(r-112),[])),'target cut')
    for r,F in zip(w['centers'],w['center_frames']):
        cursor=space(F);need(current[r]==cursor,'centre source')
        targets={space(w['target_levels'].get(str(g[1]-112),[])) for g in w['cut'] if g[2]==r}
        for target in sorted(targets,key=len,reverse=True):
            need(target<=cursor,'private descent');d=dim(cursor)-dim(target)
            if d:paid[d]+=1;trace.append(['private-centre',r,d])
            cursor=target
    for i,g in enumerate(postcut(w)):gate(g,'post-cut:'+str(i))
    for r in live:climb(r,end[r],'terminal')
    widths=[dim(end[r])-dim(start[r]) for r in live if r>=224]
    need(len(widths)==408 and min(widths)>0,'helper inventory')
    return paid,widths,{'trace_sha256':sha(canon(trace)),'paid_climbs':len(trace),'rank_mass':sum(r*n for r,n in paid.items()),'width_inventory':dict(sorted(Counter(widths).items()))},start,end

def place(mask,z,w,cap):
    need(all(type(x)is int for x in (z,w,cap)) and z>=0 and w>0 and z+w<=cap,'coordinate capacity')
    bits=((1<<w)-1)<<z;need(mask&bits==0,'coordinate overlap')
    need(mask.bit_length()<=z,'coordinate chronology');return mask|bits

def windows(template,order,T):
    clock={tuple(call):i for i,call in enumerate(order)}
    need(len(order)==9*T and set(clock)=={(s,o) for s in range(9) for o in range(T)},'call coverage')
    need(all(clock[s,o]<clock[s+1,o] for s in range(8) for o in range(T)),'replica chronology')
    caps={}
    for row in template['idle_children']:
        c,cap=row['child'],row['rank'];need(c not in caps or caps[c]==cap,'child capacity per port');caps[c]=cap
    pair={r['stage']:r['pair'] for r in template['recipe'] if r['kind']=='local'}
    history=[];last=-1;out={}
    for event in template['execution_schedule']:
        kind=event['kind']
        if kind=='local_cover_sweep':last=event['stage'];history.append((last,{pair[last]}))
        elif kind=='bridge':history.append((last,{event['src'],event['dst']}))
        elif kind=='idle_cover_sweep':
            lo=next((s for s,p in reversed(history) if event['pair'] in p),None)
            for c in event['child_indices']:
                if c not in caps:continue
                for o in range(T):
                    need((o,c) not in out,'duplicate window');out[o,c]=(caps[c],-1 if lo is None else clock[lo,o],clock[last,o])
    need(len(out)==T*len(caps),'window coverage');return out,caps

def owners(root,ow,nw,op,np,mutation=None):
    I=root/'owner/inputs';order=read(I/'ORDER.json');dr=read(I/'DISPATCH.json');dispatch={(s,r):p for s,r,p in dr}
    need(len(dr)==len(dispatch)==len(order) and set(dispatch)==set(map(tuple,order)),'dispatch')
    template,plan=read(I/'TEMPLATE.json.gz'),read(I/'PLAN.json.gz');win,caps=windows(template,order,360)
    old,new=read(I/'old-FILL.json.gz'),read(root/'owner/FILL.json.gz')
    if mutation:mutation(old,new,dispatch,win)
    need(len(dispatch)==len(order) and set(dispatch)==set(map(tuple,order)),'mutated dispatch coverage')
    grouped=defaultdict(list)
    for (o,c),(cap,lo,hi) in win.items():grouped[o,2*plan['pairs'][str(c)]+plan['sides'][str(c)]].append((lo,hi))
    for intervals in grouped.values():
        for i,(a,b) in enumerate(intervals):
            for c,d in intervals[i+1:]:need(max(a,c)>=min(b,d),'overlapping source-family windows')
    need(old['columns']==new['columns']==['time','helper','owner_replica','child','port','offset'],'fill columns')
    need(old['dispatch_overrides']==new['dispatch_overrides']==[],'dispatch overrides')
    ar,br=old['rows'],new['rows'];need(len(ar)==len(br)==3240*408,'role count')
    children=sorted(caps);ci={c:i for i,c in enumerate(children)};n=360*len(children)*112
    am,bm=[0]*n,[0]*n;changed_rows=0;by_helper=Counter();families=set();width_patterns={}
    for j,(a,b) in enumerate(zip(ar,br)):
        need(len(a)==len(b)==6 and all(type(x)is int for x in a+b),'role integers')
        need(a[:5]==b[:5],'owner identity changed');t,h,o,c,p,z=b
        need((t,h)==divmod(j,408),'time helper coverage');need((o,c) in win and 0<=p<112,'owner range')
        cap,lo,hi=win[o,c];need(lo<t<=hi,'strict owner window')
        if h==0:families.clear()
        family=(o,2*plan['pairs'][str(c)]+plan['sides'][str(c)],p)
        need(family not in families,'physical family collision');families.add(family)
        tag=dispatch[tuple(order[t])];before,after=ow[tag][h],nw[tag][h]
        k=(o*len(children)+ci[c])*112+p
        am[k]=place(am[k],a[5],before,cap);bm[k]=place(bm[k],z,after,cap)
        width_patterns[k]=width_patterns.get(k,0)+(1<<(before*4))
        if before!=after:
            need((before,after)==(4,5),'width delta');changed_rows+=1;by_helper[h]+=1
    ai,bi=Counter(),Counter();changed=[];patterns=Counter()
    for k,(a,b) in enumerate(zip(am,bm)):
        c=children[(k//112)%len(children)];cap=caps[c]
        need(a==(1<<a.bit_count())-1 and b==(1<<b.bit_count())-1,'noncompact occupied coordinates')
        x,y=cap-a.bit_count(),cap-b.bit_count()
        if x:ai[x]+=1
        if y:bi[y]+=1
        if a!=b:
            need((cap,x,y)==(32,1,0),'changed bin idle')
            need(width_patterns[k]==(1<<(4*4))+3*(1<<(9*4)),'changed bin width pattern')
            changed.append(k);patterns[cap,a.bit_count(),b.bit_count()]+=1
    need(changed_rows==len(changed),'one changed role per changed bin')
    ap,bp=Counter(ai),Counter(bi)
    for call in order:tag=dispatch[tuple(call)];ap.update(op[tag]);bp.update(np[tag])
    need(ap=={int(k):v for k,v in read(I/'old-PROFILE.json').items()},'old profile bridge')
    need(bp=={int(k):v for k,v in read(root/'owner/PROFILE.json').items()},'new profile bridge')
    delta={r:bp[r]-ap[r] for r in set(ap)|set(bp) if bp[r]!=ap[r]}
    return {'roles':len(ar),'physical_bins':n,'source_windows':len(win),'changed_rows':changed_rows,'changed_bins':len(changed),
      'changed_bin_ids_sha256':sha(canon(changed)),'changed_bin_patterns':[list(k)+[v] for k,v in sorted(patterns.items())],
      'changed_helper_indices':dict(sorted(by_helper.items())),'old_idle':dict(sorted(ai.items())),'new_idle':dict(sorted(bi.items())),
      'old_complete_profile':dict(sorted(ap.items())),'new_complete_profile':dict(sorted(bp.items())),'complete_delta':dict(sorted(delta.items())),
      'complete_rank_mass':sum(r*v for r,v in bp.items()),'rank_mass_delta':sum(r*v for r,v in delta.items())}

def controls(words=None):
    rejected=[]
    def bad(name,fn):
        try:fn()
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted control '+name)
    need(space([1,2])==space([3,2]) and len(space([1,2]))==4,'span positive')
    mask=0
    for z,w in [(0,5),(5,9),(14,9),(23,9)]:mask=place(mask,z,w,32)
    need(mask==(1<<32)-1,'bitmap positive')
    bad('overflow',lambda:place(0,28,5,32));bad('overlap',lambda:place(31,4,9,32))
    bad('reverse chronology',lambda:place(31<<9,0,9,32));bad('singular warp',lambda:permutation((1,)*9));bad('invalid frame',lambda:space([512]))
    if words:
        import copy
        for tag,(old,new) in words.items():
            z=copy.deepcopy(new);z['warps'][0][0]+=1
            bad(tag+':native cut moved',lambda:identity(old,z))
            z=copy.deepcopy(new);g=next(g for g in z['A'] if g[0]=='add');g[3]+=1
            bad(tag+':dirty scalar changed',lambda:identity(old,z))
            z=copy.deepcopy(new);g=next(g for g in z['A'] if g[0]=='scale' and g[-1]);g[-1]=[]
            bad(tag+':unpaid entrance',lambda:invoice(z))
    return {'positive':['equivalent explicit subspaces','5+9+9+9 full bitmap'],'rejected':rejected}

def owner_controls(root,ow,nw,op,np):
    rejected=[]
    def bad(name,mutate=None,profiles=None,expected=None):
        try:owners(root,ow,nw,op,profiles or np,mutation=mutate)
        except ValueError as e:
            need(expected is None or str(e)==expected,'wrong rejection for '+name+': '+str(e))
            rejected.append({'mutation':name,'rejection':str(e)})
        else:raise ValueError('accepted owner production control '+name)
    def identity_change(a,b,dispatch,win):b['rows'][0][4]+=1
    def family_collision(a,b,dispatch,win):
        for fill in (a,b):fill['rows'][1][2:5]=fill['rows'][0][2:5]
    def closed_window(a,b,dispatch,win):
        owner,child=next(key for key,(_,lo,hi) in win.items() if lo>=0)
        for fill in (a,b):fill['rows'][0][2:4]=[owner,child]
    def offset_hole(a,b,dispatch,win):b['rows'][0][5]+=1
    def dispatch_drop(a,b,dispatch,win):dispatch.pop(next(iter(dispatch)))
    bad('changed owner identity',identity_change,expected='owner identity changed')
    bad('duplicate physical family despite identical old/new identities',family_collision,expected='physical family collision')
    bad('closed source window',closed_window,expected='strict owner window')
    bad('shifted coordinate offset',offset_hole,expected='coordinate overlap')
    bad('missing dispatch',dispatch_drop,expected='mutated dispatch coverage')
    altered={tag:Counter(profile) for tag,profile in np.items()}
    for profile in altered.values():profile[1]+=1
    bad('width-to-complete-bill mismatch',profiles=altered,expected='new profile bridge')
    return rejected


def audit(root,full=True):
    manifest=read(HERE/'EXTERNAL-SOURCES.json')
    for rel,pin in manifest['files'].items():
        if full or rel.startswith('owner/inputs/old-WORD-') or rel.startswith('owner/inputs/WORD-'):
            need(sha((root/rel).read_bytes())==pin['sha256'],'source bytes '+rel)
    providers={};ow={};nw={};op={};np={};words={}
    for tag,pid in [('base','gauge44'),('extra','extra')]:
        old=read(root/f'owner/inputs/old-WORD-{tag}.json.gz');new=read(root/f'owner/inputs/WORD-{tag}.json.gz')
        ident=identity(old,new);a,b,c,s,e=invoice(old);d,f,g,u,v=invoice(new)
        changed=[r for r in e if e[r]!=v[r]]
        need(len(changed)==26 and all(e[r]<v[r] and dim(v[r])-dim(e[r])==1 for r in changed),'terminal extension')
        need(s==u,'initial dirty frame');ow[pid],nw[pid],op[pid],np[pid]=b,f,a,d;words[tag]=(old,new)
        providers[tag]={'operator':ident,'changed_terminals':changed,'old_local_profile':dict(sorted(a.items())),
          'new_local_profile':dict(sorted(d.items())),'old_invoice':c,'new_invoice':g}
    return {'status':'PASS_INDEPENDENT_TERMINAL_OWNER_BRIDGE' if full else 'PASS_LOCAL_BRIDGE_ONLY', 'source_head':manifest['head'],'providers':providers,
      'owners':owners(root,ow,nw,op,np) if full else 'NOT RUN: pass --source-root for full literal owner audit',
      'controls':controls(words),'owner_controls':owner_controls(root,ow,nw,op,np) if full else 'NOT RUN',
      'unverified':['native Clifford/Gaussian phase recipes','full ordinary/outer release','uniform all-size compiler','physical implementation and hosting hypotheses','precision stock tape recovery coefficients','analytic and BIT hypotheses','supplier admission']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source-root',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args()
    result=audit(args.source_root) if args.source_root else audit(HERE/'frozen',full=False)
    expected_path=HERE/('RESULT.json' if args.source_root else 'LOCAL-RESULT.json')
    need(expected_path.is_file(),'retained receipt missing')
    need(json.loads(canon(result))==read(expected_path),'fresh result differs from retained receipt')
    if args.output:
        need(not args.output.exists(),'output exists');args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
