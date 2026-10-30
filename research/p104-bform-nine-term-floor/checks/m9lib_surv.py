# survivors exactly as m9lib.py computes them (classes with propagation bound lb < 8), without the rest of m9lib.
import sys
_a = sys.argv; sys.argv = [_a[0], 'P104']
from m9lib import surv
sys.argv = _a
