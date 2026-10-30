"""automacro_mine -- AUTOMACRO steps 2/3: mine recurring multi-step patterns (macros) and cluster the UNEXPLAINED residues from autodec output.

    python3 -B automacro_mine.py out/automacro/dec_all.json [--md out/automacro/MINE.md]

Macro = frequent abstracted cluster composition (tags with counts removed, plus role mix and dim-flow) or frequent ADJACENT cluster pair in program order inside one PR.
Gain apportioning: a PR's kappa gain (from corpus_kappa.json / profiles) is split over its clusters by changed-event share (approximation, stated in the report).
Rank = (#PRs it appears in) x (apportioned gain, summed).  Residue clusters are grouped by shape (ops added/removed, role mix, size bucket)."""
import sys,os,json,glob,collections,re
HERE=os.path.dirname(os.path.abspath(__file__))
def kappas():
    k={}
    try:
        for n,d in json.load(open(HERE+'/out/automacro/corpus_kappa.json')).items():
            if d.get('kappa'): k[n.split('_')[0]]=d['kappa']
    except Exception: pass
    for f in glob.glob(HERE+'/profiles/*.json'):
        p=json.load(open(f)); kd=p.get('expect',{}).get('kappa_decimal')
        if kd and p.get('alias') and '_' not in p['alias']:
            k[p['alias']]=float(kd) if len(kd)>12 or p['alias'] not in k else k[p['alias']]
    return k
def strip(t): return re.sub(r'x\d+$','',t.replace(' ','')).strip()
def abstract(cl):
    tags=[strip(t) for t in cl['tags']]
    flow=cl['par'].get('dimflow'); fl='/'.join(sorted(flow)) if flow else ''
    roles='+'.join('%s'%r for r in sorted(cl['roles']))
    return ' o '.join(tags)+('' if not fl else ' ['+fl+']')+' {'+roles+'}'
def size_bucket(n): return '1' if n<=1 else '2-3' if n<=3 else '4-9' if n<=9 else '10-49' if n<=49 else '50+'
def main(argv):
    path=argv[0]; md=None
    if '--md' in argv: md=argv[argv.index('--md')+1]
    D=json.load(open(path)); K=kappas(); out=[]
    P=lambda *x: out.append(' '.join(str(y) for y in x))
    P('## Per-PR decomposition table (base -> PR, kappa gain, clusters grouped by abstracted tag composition)')
    macro=collections.defaultdict(lambda:dict(prs=set(),n=0,gain=0.0,sizes=[],ex=None,dims=collections.Counter()))
    pair=collections.defaultdict(lambda:dict(prs=set(),n=0,gain=0.0))
    resid=collections.defaultdict(lambda:dict(prs=set(),n=0,ev=0,ex=[]))
    for d in D:
        if 'error' in d: P('- #%s <- #%s ERROR %s'%(d['pr'],d['base'],d['error'])); continue
        kb,kp=K.get(d['base']),K.get(d['pr']); gain=(kp-kb) if kb and kp else None
        tot=sum(c['size'] for c in d['clusters']) or 1
        agg=collections.Counter(abstract(c) for c in d['clusters'])
        top='; '.join('%s x%d'%(a,n) for a,n in agg.most_common(5))
        P('- #%s <- #%s  dk=%s  removed %d added %d relab %d moved %d newregs %d endpoints %s  clusters %d :: %s'%(d['pr'],d['base'],('%+.3e'%gain) if gain else '?',d['n_removed'],d['n_added'],d['n_relab'],d['n_moved'],d['newregs'],d['endpoints'],len(d['clusters']),top))
        prev=None
        for c in sorted(d['clusters'],key=lambda c:(c['pos'] or (0,0))[0]):
            a=abstract(c); m=macro[a]; m['prs'].add(d['pr']); m['n']+=1; m['sizes'].append(c['size'])
            g=(gain or 0)*c['size']/tot; m['gain']+=g
            if m['ex'] is None: m['ex']=(d['pr'],c['pos'],c['regs'][:4])
            if prev is not None and c['size']>=2 and prev['size']>=2:
                pa=abstract(prev)+'  ->  '+a; q=pair[pa]; q['prs'].add(d['pr']); q['n']+=1; q['gain']+=g
            prev=c
            if 'UNEXPLAINED' in c['tags'] or any(t.startswith('P1c-owned-corr') for t in c['tags']):
                key=(c['shape'].split(' regs')[0],size_bucket(c['size']),tuple(sorted(c['roles'])))
                r=resid[key]; r['prs'].add(d['pr']); r['n']+=1; r['ev']+=c['size']
                if len(r['ex'])<3: r['ex'].append((d['pr'],c['pos'],c['regs'][:4],c['tags']))
    P('\n## MACROS: abstracted cluster compositions, ranked by (#PRs x apportioned gain)')
    P('| rank | macro (tags o ... [dim flow] {roles}) | clusters | PRs | apportioned gain | cluster size med | example (PR, pos, regs) |'); P('|---|---|---|---|---|---|---|')
    rk=sorted(macro.items(),key=lambda x:-(len(x[1]['prs'])*abs(x[1]['gain'])+1e-12*x[1]['n']))
    for i,(a,m) in enumerate(rk[:25],1):
        sz=sorted(m['sizes']); P('| %d | %s | %d | %d | %+.3e | %d | %s |'%(i,a,m['n'],len(m['prs']),m['gain'],sz[len(sz)//2],m['ex']))
    P('\n## MACRO PAIRS (adjacent clusters of >=2 changed events inside one PR)')
    rk=sorted(pair.items(),key=lambda x:-(len(x[1]['prs'])*abs(x[1]['gain'])+1e-12*x[1]['n']))
    for a,m in rk[:12]: P('- x%d in %d PRs gain %+.3e :: %s'%(m['n'],len(m['prs']),m['gain'],a))
    P('\n## RESIDUE CLUSTERS (UNEXPLAINED / owned-correction), grouped by shape -> candidate new primitives')
    rk=sorted(resid.items(),key=lambda x:-(x[1]['ev']))
    for (shape,sz,roles),r in rk[:25]:
        P('- shape[%s] size %s roles %s :: %d clusters, %d events, PRs %s, e.g. %s'%(shape,sz,'+'.join(roles),r['n'],r['ev'],sorted(r['prs']),r['ex'][:2]))
    txt='\n'.join(out)
    if md: open(md,'w').write(txt)
    print(txt)
if __name__=='__main__': main(sys.argv[1:])
