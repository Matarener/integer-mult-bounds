# Synthetic: one relation with r_q=8 in the #5392 bill. Usage: python3 -B synth.py  (run from anywhere; no -I: loads package dir)
import sys, os, json, copy
from fractions import Fraction as Q
D = os.environ['TK_NTO']
sys.path.insert(0, D); sys.path.insert(0, D + '/source/cutoff'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import price_r as price
R = json.load(open(D + '/RESULT.json'))
nat = R['native']
b = {int(k) if k.isdigit() else k: v for k, v in nat['source_replay'].items()}
def fix(h): return {int(k): v for k, v in h.items()}
b = dict(nat['source_replay']); b['helpers'] = fix(b['helpers']); b['paid'] = fix(b['paid'])
f = dict(b, real_scalar_allowance=nat['real_scalar_allowance'], max_formal_prefix_l1=nat['transpose']['max_formal_prefix_l1'], max_denominator=nat['transpose']['max_denominator'])
def go(nq8):
    bb = copy.deepcopy(b); ff = copy.deepcopy(f)
    for x in (bb, ff):
        x['helpers'][9] += nq8; x['helpers'][8] -= nq8      # nq8 pivots of rank 8 are owned instead of rank 9
    piv = [8] * nq8 + [9] * (8 - nq8)
    out = price.run({'forward': ff, 'backward': bb}, piv)
    lo, hi = [Q(x) for x in out['raw_root_interval']]
    return out, lo, hi
base, lo0, hi0 = go(0)
assert base['raw_root_interval'] == R['arithmetic']['raw_root_interval'], 'baseline mismatch'
print('base root', float(lo0), float(hi0), 'surplus', base['rank_mass_surplus'])
for n in (1, 2):
    o, lo, hi = go(n)
    print(f'{n} relation(s) r_q=8: root [{float(lo):.14f},{float(hi):.14f}] delta_lo={float(lo-lo0):.4e} delta_hi={float(hi-hi0):.4e} per-inst={float((lo-lo0)/(18*n)):.4e} surplus={o["rank_mass_surplus"]} pivots={o.get("pivot_ranks")} kappa={o["kappa"]}')
    print('  targets', dict(sorted((int(k),v) for k,v in o['targets'].items())))
