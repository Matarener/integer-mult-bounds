#!/usr/bin/env python3
"""tk -- the designer toolkit.  See README.md.   Subcommands: see `tk --help` (31) and MAP.md"""
import sys,argparse
sys.dont_write_bytecode=True
import os as _os
# ENV GUARD: search-mode switches (TK_FREE_BOUNDS, TK_NATIVE_CORE) must come only from the USER's environment or from a search driver's own main(),
# never leak from a module imported for parser/screen registration (a leaked TK_FREE_BOUNDS made `tk check` skip the inventory bounds).
_USER_ENV={k:_os.environ.get(k) for k in ('TK_FREE_BOUNDS','TK_NATIVE_CORE')}
def _restore_user_env():
    for k,v in _USER_ENV.items():
        if v is None: _os.environ.pop(k,None)
        else: _os.environ[k]=v
def build():
    ap=argparse.ArgumentParser(prog='tk',description=__doc__); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('price',help='exact kappa (fast; --real = real verifier stack via hq)'); p.add_argument('word'); p.add_argument('--real',action='store_true'); p.add_argument('--wait',action='store_true'); p.add_argument('--json',action='store_true'); p.add_argument('--no-cache',action='store_true')
    p=sp.add_parser('check',help='legality oracle with error localisation'); p.add_argument('word'); p.add_argument('--native',action='store_true'); p.add_argument('--native-ref',action='store_true',help='use the unmodified reference vendor kernels (slow, ~150 s) instead of fastnative'); p.add_argument('--exact',action='store_true'); p.add_argument('--stack',action='store_true',help='also run the adopted PR profile\'s OWN local.py replay and report any disagreement with legal.py (MODEL_GAP)'); p.add_argument('--wait',action='store_true'); p.add_argument('--max',type=int,default=50); p.add_argument('--json',action='store_true')
    p=sp.add_parser('retime',help='exact lattice retime'); p.add_argument('word'); p.add_argument('--free',required=True,help='comma list of starts,finals,stops,mainstops,mainends'); p.add_argument('--pin',help='mainstops: keep main-register intermediate frames'); p.add_argument('--tl',type=float,default=900); p.add_argument('--out'); p.add_argument('--wait',action='store_true'); p.add_argument('--inline',action='store_true',help='run in this process (inside an hq job)'); p.add_argument('--name')
    p=sp.add_parser('diff',help='what changed between two words'); p.add_argument('a'); p.add_argument('b'); p.add_argument('--json',action='store_true')
    p=sp.add_parser('hops',help='hop/role/restore counts of a delivery program'); p.add_argument('matrix'); p.add_argument('--signed',action='store_true'); p.add_argument('--program'); p.add_argument('--points'); p.add_argument('--json',action='store_true'); p.add_argument('--recomb',action='store_true',help='submit CP-SAT recombination via hq')
    p=sp.add_parser('reframe',help='exact frame re-assignment (frames.assign), never worse than the input'); p.add_argument('word'); p.add_argument('--k',type=int,default=2); p.add_argument('--maxm',type=int,default=0); p.add_argument('--tl',type=float,default=600); p.add_argument('--out'); p.add_argument('--wait',action='store_true'); p.add_argument('--inline',action='store_true'); p.add_argument('--name')
    p=sp.add_parser('evretime',help='event-level exact retime, free ADD placement'); p.add_argument('word'); p.add_argument('--k',type=int,default=2); p.add_argument('--maxm',type=int,default=0); p.add_argument('--tl',type=float,default=900); p.add_argument('--out'); p.add_argument('--wait',action='store_true'); p.add_argument('--inline',action='store_true'); p.add_argument('--name')
    p=sp.add_parser('reorder',help='event-order + frame retime (commuting reads/writes may change places)'); p.add_argument('word'); p.add_argument('--k',type=int,default=2); p.add_argument('--maxm',type=int,default=0); p.add_argument('--tl',type=float,default=900); p.add_argument('--out'); p.add_argument('--window',nargs=2,type=int,metavar=('LO','HI')); p.add_argument('--wait',action='store_true'); p.add_argument('--inline',action='store_true'); p.add_argument('--name')
    p=sp.add_parser('pricer',help='rank-r owned-pivot pricing (PR5392 generalisation)'); p.add_argument('--synth',action='store_true',help='rank-8 synthetic (k=1,2 relations)')
    p=sp.add_parser('gen',help='S4GEN/GENX hub-partition generator for window B (#4610 word)'); p.add_argument('preset',nargs='?',default='full0'); p.add_argument('--realise',action='store_true',help='also run realise6 (about 220 s, via hq)'); p.add_argument('--wait',action='store_true'); p.add_argument('--tag'); p.add_argument('--env',action='append',default=[],help='extra KEY=VAL for gen_run3.py')
    p=sp.add_parser('sens',help='kappa marginals of the exact invoice'); p.add_argument('word'); p.add_argument('--calls',type=int,default=18); p.add_argument('--json',action='store_true')
    p=sp.add_parser('decompile',help='word -> value DAG'); p.add_argument('word'); p.add_argument('--out'); p.add_argument('--no-forms',action='store_true')
    p=sp.add_parser('realise',help='value DAG + schedule -> word (then check + price)'); p.add_argument('dag'); p.add_argument('--schedule',default='exact',help='exact | lazy | FILE.json'); p.add_argument('--drop-helper'); p.add_argument('--out'); p.add_argument('--no-verify',action='store_true'); p.add_argument('--no-price',action='store_true'); p.add_argument('--max',type=int,default=20)
    p=sp.add_parser('handoff',help='complete successor hand-off screen (tail retarget, multi-partner, scratch, relabel) + --apply'); p.add_argument('word'); p.add_argument('--apply',action='store_true'); p.add_argument('--inline',action='store_true'); p.add_argument('--out'); p.add_argument('--name'); p.add_argument('--wait',action='store_true'); p.add_argument('--tl',type=float,default=7200); p.add_argument('--top',type=int,default=40); p.add_argument('--threshold',default='.0030818185'); p.add_argument('--classes',default='SBC'); p.add_argument('--selftest',action='store_true'); p.add_argument('--fast',action='store_true',help='positive-only: price candidates with IncrWord first (15x faster on 20k-event words); only incremental dk>0 go to the exact path; non-positive legal candidates are not listed')
    p=sp.add_parser('split',help='independent helper-split screen + greedy apply (#5599 move class)'); p.add_argument('word'); p.add_argument('--apply',action='store_true'); p.add_argument('--max',type=int,default=40); p.add_argument('--out'); p.add_argument('--public-cap',type=int,default=750,help='package local.py bound on public registers (0 = off)'); p.add_argument('--event-cap',type=int,default=26000); p.add_argument('--free-decay',action='store_true',help='accept hits whose side check passes for some tail decay up to .99 (PARAMS)'); p.add_argument('--rate',action='store_true',help='rank by dkappa per added event'); p.add_argument('--list',type=int,default=0)
    p=sp.add_parser('accept',help='real price.run acceptance with cached native pairs / controller (seconds when warm)'); p.add_argument('word'); p.add_argument('--json',action='store_true'); p.add_argument('--native-ref',action='store_true',help='reference native kernels, bypass pair cache')
    p=sp.add_parser('adopt',help='derive + register + validate the verifier profile of a swarm PR (toolkit/profiles/PR.json); --list shows the adopted profiles'); p.add_argument('pr',nargs='?',type=int); p.add_argument('--head',help='commit SHA to adopt instead of refs/pr/N'); p.add_argument('--pkg',help='research/DIR (default: the package whose WORD the head commit touched)'); p.add_argument('--alias'); p.add_argument('--no-accept',action='store_true',help='skip the (slow) accept step'); p.add_argument('--no-vendor',action='store_true'); p.add_argument('--refetch',action='store_true'); p.add_argument('--json',action='store_true'); p.add_argument('--list',action='store_true')
    p=sp.add_parser('eval',help='bulk evaluator: check --native + price.run acceptance + exact price + handoff/evretime/retime fixed point -> JSON record per word')
    p.add_argument('words',nargs='*'); p.add_argument('--native-ref',action='store_true',help='reference native kernels (slow), no pair cache'); p.add_argument('--jobs',type=int,default=1); p.add_argument('--out'); p.add_argument('--summary',action='store_true'); p.add_argument('--force',action='store_true'); p.add_argument('--worker',help=argparse.SUPPRESS)
    p.add_argument('--no-pipeline',action='store_true',help='check + accept + price only'); p.add_argument('--screens',default='handoff,evretime,retime',help='comma list, run in order each round'); p.add_argument('--rounds',type=int,default=6)
    p.add_argument('--k',type=int,default=2); p.add_argument('--maxm',type=int,default=0); p.add_argument('--tl',type=float,default=900,help='per-screen CP-SAT/enumeration time limit'); p.add_argument('--threads',type=int,default=1); p.add_argument('--ev-threads',type=int,default=0,help='CP-SAT threads for evretime (default = --threads; single-thread evretime often times out FEASIBLE below the input)')
    p.add_argument('--accept',choices=['full','fast'],default='full',help='full = real price.run acceptance (cached parts); fast = native pairs + side/budgets only'); p.add_argument('--no-accept-each',action='store_true',help='re-check intermediate words with the fast mode only (final word always gets --accept)'); p.add_argument('--word-timeout',type=int,default=14400)
    p.add_argument('--candidates',help='dir: pipeline-produced words with kappa > --threshold are copied here as CANDIDATE-NAME.json.gz with price/check output'); p.add_argument('--threshold',default='.0030818950'); p.add_argument('--results',help='append one JSON line per finished word to this jsonl')
    import wsearch; wsearch.add_parsers(sp)      # SEARCHCORE: tk search
    import pscreen; pscreen.add_parsers(sp)      # P8GAP: tk pscreen (prims/prims_role/prims_extra/macros as eval screens)
    import movekit; movekit.add_parsers(sp)      # TKMOVES: ibase a2x blockmove split2 (move-class plugins)
    import synth; synth.add_parsers(sp)         # SYNTH: tk synth (spec -> DAG -> word, repair, sampler)
    import gensearch; gensearch.add_parsers(sp) # GENSEARCH: tk gensearch (spec-space search over the generator)
    import genpipe; genpipe.add_parsers(sp)     # GENPIPE: tk genpipe (generator pipeline orchestration)
    import genpipe2; genpipe2.add_parsers(sp)   # GENPIPE2: tk gen2 (from-scratch generator, stages 1-5 in one command)
    import genpipe3; genpipe3.add_parsers(sp)   # GENHUBS: tk gen3 (gen2 + Y-route stage + signal ledger + post fold,hoist + screens)
    import shipcheck; shipcheck.add_parsers(sp) # ADMITGEN: tk shipcheck (shippability of generated words)
    import rebuild; rebuild.add_parsers(sp)     # BULKGEN: tk rebuild (alignbuild/: the five pinned rule builders composed, exact kappa)
    import bulk; bulk.add_parsers(sp)           # BULKEVAL: tk bulk (corpus-wide evaluation table)
    import anatomy; anatomy.add_parsers(sp)     # BULKGEN: tk anatomy (per-side ledger of any word)
    ap.add_argument('--cap-free',action='store_true',help='CAPFREE: ignore the 26000 event cap (package declares its own operation bound, #5830); k2sa/split/incr/legal/admit see no event cap, evpen 0. Default unchanged.')
    ap.add_argument('--profile',help='verifier profile name (toolkit/profiles/NAME.json or built-in); default = auto from the word')
    return ap
def main():
    a=build().parse_args(); _restore_user_env()
    import os
    if getattr(a,'profile',None): os.environ['TK_PROFILE']=a.profile
    if getattr(a,'cap_free',False): os.environ['TK_EVENT_CAP']='0'      # CAPFREE: inherited by eval/pscreen worker subprocesses
    if getattr(a,'native_ref',False): os.environ['TK_NATIVE_REF']='1'      # inherited by eval worker subprocesses
    if a.cmd in ('eval',): import movekit; movekit.register_screens(); import pscreen; pscreen.register_screens(); _restore_user_env()      # TKMOVES: plugins join `tk eval --screens`
    import bitadapt; _r=bitadapt.dispatch(a)      # BITADAPT: BIT-side words / packages are routed to the BIT adapter
    if _r is not None: sys.exit(_r)
    import importlib; m=importlib.import_module({'search':'wsearch','plateau':'wsearch.plateau','gen2':'genpipe2','gen3':'genpipe3'}.get(a.cmd,a.cmd)); r=m.main(a); sys.exit(r or 0)
if __name__=='__main__': main()
