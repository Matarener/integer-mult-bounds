"""Portable optional C++17 replay. No dependencies beyond Python and a C++ compiler.
Apache-2.0; Dugongue with substantial OpenAI assistance.
"""
from pathlib import Path
import argparse, gzip, itertools, os, random, shutil, subprocess, tempfile
HERE = Path(__file__).resolve().parent

def need(ok, why):
    if not ok: raise ValueError(why)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cxx', default='g++')
    ap.add_argument('--full', action='store_true', help='Also rerun the frozen alpha, swap and plateau searches')
    ap.add_argument('--work-dir', type=Path, help='Optional parent for temporary build/output directory')
    args = ap.parse_args()
    cxx = shutil.which(args.cxx)
    need(cxx is not None, 'C++17 compiler not found; pass --cxx /path/to/g++ or clang++')
    with tempfile.TemporaryDirectory(prefix='owned-query-', dir=args.work_dir, ignore_cleanup_errors=True) as folder:
        work = Path(folder)
        env = dict(os.environ, TMP=str(work), TEMP=str(work), TMPDIR=str(work))
        engines = ['port_alpha'] + (['port_swap','port_plateau_long'] if args.full else [])
        bins = {}
        for engine in engines:
            binary = work / (engine + ('.exe' if os.name == 'nt' else ''))
            subprocess.run([cxx,'-O3','-std=c++17',str(HERE/(engine+'.cpp')),'-o',str(binary)],check=True,timeout=120,env=env)
            bins[engine] = binary
        def run(labels, fixed, edges, name):
            graph = work / (name+'.txt')
            result = work / (name+'-candidate.txt')
            graph.write_text(f'{len(labels)} {len(edges)} 2\n'+''.join(f'{a} {int(b)}\n' for a,b in zip(labels,fixed))+''.join(f'{a} {b}\n' for a,b in edges)+'0 1\n1 0\n0 1\n',encoding='utf-8',newline='\n')
            # Every fixture has a fresh output path; no stale candidates are accepted.
            subprocess.run([str(bins['port_alpha']),str(graph),str(result)],check=True,capture_output=True,text=True,timeout=30,env=env)
            answer = list(map(int,result.read_text().split())) if result.exists() else list(labels)
            need(len(answer)==len(labels) and all(x in (0,1) for x in answer), 'Candidate labels')
            need(all(not f or a==b for a,b,f in zip(labels,answer,fixed)), 'Fixed input changed')
            return answer
        labels=[0,0,1,1,0,0];fixed=[1,1,1,1,0,0]
        edges=[(0,4),(1,4),(2,5),(3,5),(4,5)]
        score=lambda L,E:sum(L[a]!=L[b] for a,b in E)
        answer=run(labels,fixed,edges,'strict-adapter')
        need(score(labels,edges)==2 and score(answer,edges)==1, 'Strict adapter control')
        rng=random.Random(271828)
        for j in range(30):
            labels=[rng.randrange(2) for _ in range(8)]
            fixed=[1,1]+[0]*6
            edges=[(a,b) for a in range(8) for b in range(a) if rng.random()<.35]
            answer=run(labels,fixed,edges,'exhaustive-'+str(j))
            optimum=min(score(labels[:2]+list(t),edges) for t in itertools.product(range(2),repeat=6))
            need(score(answer,edges)==optimum, 'Cut disagrees with exhaustive binary optimum')
        print('PASS_CPP17_CONTROLS: strict split saving and 30 exhaustive binary optima',flush=True)
        if args.full:
            graph=work/'GRAPH.txt'
            graph.write_bytes(gzip.decompress((HERE/'GRAPH.txt.gz').read_bytes()))
            for engine in engines:
                out=work/(engine+'-result.txt')
                result=subprocess.run([str(bins[engine]),str(graph),str(out)],check=True,capture_output=True,text=True,timeout=600,env=env)
                print(engine+':\n'+result.stdout,flush=True)
                if out.exists():
                    print('DISCOVERY CANDIDATE: requires full physical, stock, invoice and outer verification; no bound is certified.',flush=True)

if __name__=='__main__':main()
