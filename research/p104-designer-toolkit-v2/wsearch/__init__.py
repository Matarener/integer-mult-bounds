"""tk search -- word-search driver + result store (SEARCHCORE).  See drive.py, canon.py, store.py and module docstring."""
def add_parsers(sp):
    from . import plateau; plateau.add_parsers(sp)      # PLATEAU: tk plateau
    p=sp.add_parser('search',help='local search over P104-family words: greedy|beam|anneal|lns over move-class plugins + screens; SQLite store; --report; resumable')
    p.add_argument('--from',dest='src',help='start word: alias / path / adopted PR number (e.g. 5718)')
    p.add_argument('--strategy',default='greedy',choices=['greedy','beam','anneal','lns'])
    p.add_argument('--classes',default='a2x,ibase,blockmove,split2',help='comma list: plugin classes (ibase a2x blockmove split2) and screens (handoff evretime reorder split retime) used as large moves')
    p.add_argument('--budget',type=float,default=0.05,help='CPU hours for this call (user+sys incl. children)'); p.add_argument('--seed',type=int,default=0)
    p.add_argument('--run-id'); p.add_argument('--store',help='SQLite path (default ext/SEARCH/store.sqlite)'); p.add_argument('--frontier',default='.0031130160',help='kappa above this is validated and flagged CANDIDATE')
    p.add_argument('--evaluator',default='incr',choices=['full','incr'],help='incr (default): incr.IncrWord try_edit/commit with periodic full resync; full: legal.check + price per edit'); p.add_argument('--resync',type=int,default=200,help='incr: full-check resync (assert agreement) every N commits'); p.add_argument('--prefilter',default='auto',choices=['auto','quick','none'],help='anneal: Metropolis on quick() kappa before the exact check (auto: quick for --evaluator full, none for incr)'); p.add_argument('--no-incremental-pools',action='store_true',help='rebuild site pools instead of update_sites'); p.add_argument('--relax',action='store_true',help='ignore the toolkit-unmodelled public-bound (>750) and side rule (words of #5751): the PR stack decides at validation')
    p.add_argument('--pool-cap',type=int,default=0,help='max sites enumerated per class per pool (0 = class default)'); p.add_argument('--max-steps',type=int,default=0)
    p.add_argument('--temp',default='2e-7,2e-9',help='anneal: start,end temperature (kappa units)'); p.add_argument('--beam-width',type=int,default=3); p.add_argument('--beam-children',type=int,default=3)
    p.add_argument('--lns-window',default='400,3000'); p.add_argument('--lns-drop',type=float,default=3e-7,help='lns perturbation: max kappa loss accepted per perturbing edit'); p.add_argument('--lns-price-cap',type=int,default=300,help='lns repair: max window edits tried (incr: exact first-improvement) or quick-priced (full) per class and iteration'); p.add_argument('--screen-tl',type=float,default=60,help='time limit (s) of screens used as moves')
    p.add_argument('--s2s',action='store_true',help='GENSPLICE: compact the start word state-to-state (synth/s2s.py, kappa identical, ~3.3k fewer events) and use s2s window re-synthesis as an extra LNS repair step')
    p.add_argument('--no-validate',action='store_true',help='do not run tk accept on frontier hits (they stay UNVALIDATED)')
    p.add_argument('--report',action='store_true',help='top-k by kappa with lineage (no search)'); p.add_argument('-k',type=int,default=10); p.add_argument('--validate',help='re-validate the stored word with this canonical hash (prefix ok)')
    p.add_argument('--cpuq',help='write W/jobs/pending/NAME.sh running this exact search (resumable) instead of running it')
def main(a):
    a.incremental_pools=not getattr(a,'no_incremental_pools',False)
    from . import drive; return drive.main(a)
