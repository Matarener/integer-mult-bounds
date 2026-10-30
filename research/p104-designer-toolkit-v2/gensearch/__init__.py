"""tk gensearch -- search over the SPECS of the from-scratch generator (see ../module docstring).  space.py build.py run.py"""
def add_parsers(sp):
    p=sp.add_parser('gensearch',help='spec-space search over the from-scratch generator: random | evo | halving, L0 R0 / L1 fast invoice+admit / L2 exact IncrWord, resumable, results in GENSEARCH/cpu_results.jsonl + SEARCH store')
    p.add_argument('--strategy',default='random',choices=['random','evo','halving']); p.add_argument('--seed',type=int,default=0); p.add_argument('--minutes',type=float,default=5); p.add_argument('--run')
    p.add_argument('--store',help='SQLite store ("default" = SEARCH/store.sqlite): top legal words with lineage = spec'); p.add_argument('--frontier',default='.0031219213'); p.add_argument('--report',action='store_true',help='print the analysis of cpu_results.jsonl (correlations, fractions)')
    p.add_argument('--cpuq',help='write cpuq jobs NAME<k>_<strategy>_s<seed>.sh for --plan'); p.add_argument('--plan',default="[('evo',1,120),('halving',2,120),('random',3,120)]",help='python list of (strategy,seed,minutes) for --cpuq')
def main(a):
    from . import run; return run.main(a)
