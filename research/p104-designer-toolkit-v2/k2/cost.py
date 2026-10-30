"""k2.cost -- the pluggable cost-model registry of the unified k2net search (module docstring).  No side effects at import.
  'kappa' : complex words, exact invoice kappa (C++ engine default; maximise)         -> engine.run(net, opts=cost_opts('kappa'))
  'r0'    : complex words, chain tax R0 (C++ engine K2S_COST=r0; objective -R0)       -> engine.run(net, opts=cost_opts('r0'))
  'bit'   : G20 BIT words, rank-mass linear cost + exact crossing (python reference engine k2bit_search.S, CostModel plug synth/k2bit.BitCost); the C++ engine is complex-only
cost_opts(name) -> option dict for k2.engine.run; model(name, ...) -> synth.k2bit CostModel (legal / exact) for python-side validation."""
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
for p in (TK,os.path.join(TK,'synth')):
    if p not in sys.path: sys.path.insert(0,p)
def cost_opts(name):
    if name=='kappa': return {}
    if name=='r0': return {'cost':'r0'}
    raise ValueError('C++ engine supports kappa|r0; BIT runs in k2bit_search (python)')
def model(name,*a,**kw):
    from synth import k2bit
    return {'bit':k2bit.BitCost,'r0':k2bit.ComplexR0,'kappa':k2bit.ComplexR0}[name](*a,**kw)
def bit_search(alias='bit5708',secs=60,seed=1,T=0.0,moves=('reloc','conj','merge')):
    """python reference engine for BIT words (same move vocabulary as the C++ engine's shift/ret/split/cadd/cdel)"""
    import k2bit_search as KS; return KS.run(alias,secs=secs,seed=seed,T=T,moves=moves)
