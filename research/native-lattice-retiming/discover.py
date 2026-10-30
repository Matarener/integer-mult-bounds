"""Optional floating discovery; never mathematical acceptance.
Apache-2.0, Codex assistance. Min-cut base credited to Cinna Davis PR4441.
"""
import argparse
import json
from pathlib import Path
import subprocess
import native

def main(output):
    output.mkdir(parents=True,exist_ok=False)
    N,c,_,baseline=native.build()
    c['frames'].pop() # The explicit candidate must not seed its own discovery.
    program=baseline['forward'];nodes=[];paths=[[] for _ in range(632)]
    def contact(old,new,roles,mutable=False,index=-1):
        i=len(nodes);nodes.append(dict(old=old,new=new,roles=roles,mutable=mutable,index=index))
        for r in roles:paths[r].append(i)
    for r,f in enumerate(c['start']):contact(f,f,[r],r>=224)
    for i,e in enumerate(program):
        if e[0]=='scalar':
            g=e[1];rr=g[1:3] if g[0] in ('add','copy') else g[1:2];roles=[r[1] for r in rr if r[0]=='L']
            if roles:contact(e[2],e[2],roles,all(r[0]=='L' for r in rr),i)
        elif e[0]=='warp':contact(e[3],e[4],[e[1][1]],False,i)
    last=len(nodes)
    for r,f in enumerate(c['final']):contact(f,f,[r],r>=224)
    edges=[(a,b) for path in paths for a,b in zip(path,path[1:])]
    graph=output/'input.graph'
    with graph.open('w') as out:
        print(len(c['frames']),len(nodes),len(edges),file=out)
        for basis in c['frames']:
            sp=N.span(basis)
            print(len(basis),*[sum(1<<(v%64) for v in sp if v//64==b) for b in range(8)],file=out)
        for n in nodes:print(int(n['mutable']),n['old'],n['new'],file=out)
        for a,b in edges:print(a,b,file=out)
        print(408,file=out)
        for r in range(224,632):print(r,last+r,file=out)
    executable=output/'discover-lattice';solution=output/'solution.txt'
    subprocess.run(['c++','-O3','-std=c++20',str(native.HERE/'discover-lattice.cpp'),'-o',str(executable)],check=True,timeout=120)
    with graph.open() as inp,(output/'discovery.log').open('w') as log:
        subprocess.run([str(executable),str(solution)],stdin=inp,stdout=log,stderr=log,check=True,timeout=600)
    native.need(solution.exists(),'No improved candidate found')
    lines=solution.read_text().splitlines();F,M=map(int,lines[0].split());native.need(M==len(nodes),'Discovery dimensions')
    spaces=[]
    for line in lines[1:F+1]:
        d,*chunks=map(int,line.split());sp=frozenset(x for x in range(512) if chunks[x//64]>>(x%64)&1)
        native.need(len(sp)==1<<d,'Discovery subspace cardinality');spaces.append(sp)
    changed=[];keys={i:key for key,i in N.gates(program).items()}
    for line in lines[F+1:]:
        i,a,b=map(int,line.split());n=nodes[i]
        if spaces[a]!=N.span(c['frames'][n['old']]) or spaces[b]!=N.span(c['frames'][n['new']]):
            changed.append(dict(node=i,program_index=n['index'],contact=keys.get(n['index']),old_frame=n['old'],new_space=sorted(spaces[a])))
    patch=native.read(native.HERE/'PATCH.json')
    expected=(patch['phase'],patch['scalar_ordinal'])
    matches=len(changed)==1 and changed[0]['contact']==expected and set(changed[0]['new_space'])==N.span(patch['new_basis'])
    result=dict(status='FLOATING_DISCOVERY_ONLY',changed=changed,reproduces_explicit_contact=matches)
    (output/'DISCOVERY.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();main(args.output.resolve())
