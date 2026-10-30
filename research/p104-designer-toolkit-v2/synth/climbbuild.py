"""synth.climbbuild -- CLIMBBUILD lane (see ../module docstring).  Scope [toolkit synth, constructive multi-reader helper-climb builder].
Model-level builder (no word realisation yet): exact sign-gated multi-rung pieces over co-designed X/Y chains.  Implementation lives in ext/CLIMBBUILD
(cb.py core, cbr2.py beam/greedy, cbr3.py/cbr4.py butterfly pre-commit).  Import has no side effects beyond sys.path.
"""
import os,sys
WORK=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','ext','CLIMBBUILD')
def load():
    w=os.path.abspath(WORK)
    if w not in sys.path: sys.path.insert(0,w)
    import cb,cbr2,cbr3
    return cb,cbr2,cbr3
