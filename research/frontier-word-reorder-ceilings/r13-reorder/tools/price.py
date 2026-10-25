"""Float root for a local paid profile (centre 8x rank-8 appended), via PR4610 arithmetic.assemble."""
import sys, json, importlib.util
from pathlib import Path
ROOT = Path.home()/'imb-r13'
A = ROOT/'research/kappa-round6-compiler-tightening-20261022'
sys.path.insert(0, str(A))
spec = importlib.util.spec_from_file_location('ar', A/'arithmetic.py'); ar = importlib.util.module_from_spec(spec); sys.modules['ar'] = ar; spec.loader.exec_module(ar)
HEL = {4:28,7:7,8:47,9:326}
def margin(T, P, C): return sum(n*k**(1-C) for k, n in T.items())-sum(n*r**(1-C) for r, n in P.items())
def root(paid, helpers=HEL):
    paid = dict(paid); paid[8] = paid.get(8, 0)+8 if 8 not in paid or paid.get('_c') is None else paid[8]
    H, N, T, P, word = ar.assemble({'helpers': helpers, 'paid': paid})
    lo, hi = 0.0, 0.5
    for _ in range(200):
        m = (lo+hi)/2
        if margin(T, P, m) > 0: lo = m
        else: hi = m
    return lo
if __name__ == '__main__':
    prof = {int(k): v for k, v in json.loads(sys.argv[1]).items()}
    print(prof, 'mass', sum(k*v for k, v in prof.items()), 'root', root(prof))
