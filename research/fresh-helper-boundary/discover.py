"""Optional reconstruction of the floating min-cut discovery, not proof replay.

Needs a C++20 compiler. Writes only into a new requested output directory.
Scientific acceptance is exclusively through verify.py. Apache-2.0;
substantial OpenAI Codex assistance.
"""
import argparse
import json
from pathlib import Path
import subprocess
import native

HERE = Path(__file__).resolve().parent

def main(output):
    output.mkdir(parents=True,exist_ok=False)
    c = native.read(native.BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    program = native.read(native.BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')['forward']
    spaces = [native.span(b) for b in c['frames']]
    nodes, paths = [], [[] for _ in range(632)]
    def contact(old,new,roles,mutable=False,index=-1):
        i = len(nodes)
        nodes.append({'old':old,'new':new,'roles':roles,'mutable':mutable,'index':index})
        for r in roles: paths[r].append(i)
    for r,f in enumerate(c['start']): contact(f,f,[r])
    for i,e in enumerate(program):
        if e[0] == 'scalar':
            g = e[1]; rr = g[1:3] if g[0] in ('add','copy') else g[1:2]
            roles = [r[1] for r in rr if r[0] == 'L']
            if roles: contact(e[2],e[2],roles,all(r[0]=='L' for r in rr),i)
        elif e[0] == 'warp':
            contact(e[3],e[4],[e[1][1]],False,i)
    for r,f in enumerate(c['final']): contact(f,f,[r])
    edges = [(a,b) for path in paths for a,b in zip(path,path[1:])]
    executable = output/'discover-cut'
    subprocess.run(['g++','-O3','-std=c++20',str(HERE/'discover-cut.cpp'),'-o',str(executable)],check=True)
    for mode in ('entry','exit'):
        for r in range(224,632):
            nodes[r]['mutable'] = mode == 'entry'
            nodes[len(nodes)-632+r]['mutable'] = mode == 'exit'
        graph, solution = output/(mode+'.graph'), output/(mode+'.solution')
        with graph.open('w') as out:
            print(len(spaces),len(nodes),len(edges),file=out)
            for s in spaces:
                print(len(s).bit_length()-1,*[sum(1<<(v%64) for v in s if v//64==b) for b in range(8)],file=out)
            for n in nodes: print(int(n['mutable']),n['old'],n['new'],file=out)
            for a,b in edges: print(a,b,file=out)
            print(408,file=out)
            for r in range(224,632):
                print(r if mode=='entry' else len(nodes)-632+r,
                      nodes[len(nodes)-632+r]['old'] if mode=='entry' else nodes[r]['new'],file=out)
        with graph.open() as inp,(output/(mode+'.log')).open('w') as log:
            subprocess.run([str(executable),mode,str(solution)],stdin=inp,stdout=log,stderr=log,check=True)
        if solution.exists():
            for line in solution.read_text().splitlines():
                i,a,b = map(int,line.split());nodes[i]['old']=a;nodes[i]['new']=b
    keys = {i:key for key,i in native.gates(program).items()}
    changes = {'entrances':[],'exits':[],'gates':[]}
    for r in range(224,632):
        for field,i,key in [('start',r,'entrances'),('final',len(nodes)-632+r,'exits')]:
            if c[field][r] != nodes[i]['old']:
                changes[key].append([r,c[field][r],nodes[i]['old']])
    for n in nodes:
        i = n['index']
        if i in keys and n['old'] != program[i][2]:
            phase,ordinal = keys[i]
            changes['gates'].append([phase,ordinal,program[i][2],n['old']])
    (output/'CHANGES.json').write_text(json.dumps(changes,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'DISCOVERY_ONLY','output':str(output),
                      'counts':{k:len(v) for k,v in changes.items()},
                      'matches_submitted_patch':changes==native.read(HERE/'CHANGES.json')},sort_keys=True))

if __name__ == '__main__':
    p = argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    main(p.parse_args().output.resolve())
