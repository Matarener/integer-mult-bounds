"""synth.partialtrie -- PARTIALTRIE lane (see ../module docstring).  Scope [toolkit synth, partial-root trie: root build doubling as residual supply].

frontgen hook `helpers: ptrie`.  Kernel ext/PARTIALTRIE/pt.cpp (fork of JOINTFEED/jf.cpp): root k's tree may be organised as a TRIE of S_k-signed partial roots at
frames l_k in F in H_k (virtual tops, plan top type -5 with basis tb), and every Y-side register may READ an S_k-signed root-tree hub (trie piece or X-stop-top root hub,
PT_ALLROOT) whose support lies in its target and whose content is proportional to its residual there (sign-consistent: U(j,.) ~ S_k).  Per-Y offer switches and the
trie frames are SA state; the objective is the joint R0 of root build + residual supply.  Plan = kernel stdout (PARTIALTRIE_PLAN=<file> or data/partialtrie_plan.txt).
Realisation is JOINTFEED's glue unchanged (validate: exact supports, nested rungs, sign consistency with the hub owner; pre-root hub seq in height order; feeders post-root;
SHAREDSUM relays + Z for the signal), with its own plan and signal cache.
"""
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
DATA=os.path.join(HERE,'data','partialtrie_plan.txt'); SIGDATA=os.path.join(HERE,'data','partialtrie_signal.json')
def apply(bk,ctx,path=None):
    from synth import jointfeed as JF
    old=JF.SIGDATA; JF.SIGDATA=SIGDATA
    try: return JF.apply(bk,ctx,path=path or os.environ.get('PARTIALTRIE_PLAN',DATA))
    finally: JF.SIGDATA=old
