"""synth.kernel2 -- KERNEL2 lane (see ../module docstring).  Scope [toolkit synth, unified generalised SA kernel].

frontgen hook `helpers: k2`.  Kernel ext/KERNEL2/k2.cpp (fork of FLAGS/fl.cpp = PARTIALTRIE/pt.cpp = JOINTFEED/jf.cpp = MAINHUB, runtime chain length K2_L).
Plan format = the shared mainhub/jointfeed/partialtrie text format (kernel stdout), so realisation is JOINTFEED's glue with its own plan and signal cache
(K2_PLAN=<file> or data/kernel2_plan.txt).  Module import has no side effects (no environment is set here).
Explicit-network layer (encode a word into per-register chains + rendezvous events, replay, exact R0): synth/kernel2net.py.
"""
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
DATA=os.path.join(HERE,'data','kernel2_plan.txt'); SIGDATA=os.path.join(HERE,'data','kernel2_signal.json')
def apply(bk,ctx,path=None):
    from synth import jointfeed as JF
    old=JF.SIGDATA; JF.SIGDATA=SIGDATA
    try: return JF.apply(bk,ctx,path=path or os.environ.get('K2_PLAN',DATA))
    finally: JF.SIGDATA=old
