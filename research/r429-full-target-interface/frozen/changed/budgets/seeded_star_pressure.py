#!/usr/bin/env python3
"""Exact necessary pressure bound for the fixed three-seed BIT star.

This is a conditional rejection, not a complete supplier verification.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('/Users/ross/git/math')
SOURCE = ROOT / 'integer-mult-bounds/research/bit-r438-transport-rehost/verify_rehost.py'
WORD = SOURCE.parent / 'words/r438-t154.json.gz'
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
WORD_SHA = 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022'

def need(condition, message):
    if not condition:
        raise ValueError(message)

def log_lower(x):
    """For x>1, ln(x) > 2(z+z^3/3), z=(x-1)/(x+1)."""
    need(x > 1, 'positive atanh expansion argument')
    z = (x-1)/(x+1)
    return 2*(z+z**3/3)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    source_bytes = SOURCE.read_bytes()
    nodes = ast.parse(source_bytes).body
    assignments = [n for n in nodes if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'LOCAL_B' for t in n.targets)]
    need(len(assignments) == 1, 'unique source profile')
    profile = ast.literal_eval(assignments[0].value)
    need(profile == {1:1322, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:18}, 'fixed seed profile')
    need(hashlib.sha256(WORD.read_bytes()).hexdigest() == WORD_SHA, 'seed word source pin')
    mass = sum(r*c for r,c in profile.items())
    need(mass == 5121, 'seed rank mass')
    copies, exponent, min_arity, max_rank, deficit = 3, Q(1,500), 22, 7, 33
    lower = copies*mass*exponent*log_lower(Q(min_arity,max_rank))
    need(lower > deficit, 'strict contradiction to available deficit')
    # Controls test sensitivity of this specific witness. They are not positive
    # supplier claims when the sufficient rejection bound ceases to certify.
    need(2*mass*exponent*log_lower(Q(min_arity,max_rank)) < deficit,
         'omitting one charged seed destroys this rejection witness')
    need(copies*mass*exponent*log_lower(Q(min_arity,8)) < deficit,
         'relaxing maximum child rank to8 destroys this rejection witness')
    need(lower < 35, 'larger D35 is not rejected by this coarse witness')
    out = {
        'status':'PASS_ALL_L_FIXED_THREE_SEED_STAR_REJECTION',
        'scientific_pin':PIN,
        'profile_source':str(SOURCE),
        'profile_source_sha256':hashlib.sha256(source_bytes).hexdigest(),
        'seed_word_sha256':WORD_SHA,
        'seed_profile':profile,
        'one_seed_rank_mass':mass,
        'assumptions':[
            'Integer L>=3; parent arity m=1+7L; three unchanged R438 seed calls occur.',
            'Full candidate invoice has deficit D=mW-sum(c_r*r)<=33 after every cost is included.',
            'Every child rank r is at most m, so omitted pressure terms are nonnegative.',
            'The desired primitive supplier exponent a is at least1/500.'
        ],
        'scope':'Any completed invoice retaining these assumptions is rejected, irrespective of native or owner admission. The source-bound ideal D33 comes from N111:2*N-3*63. Added missing costs only strengthen rejection; a different seed, common coverage, rank profile or deficit is outside this theorem.',
        'necessary_condition':'For normalized moment sum(c_r/W)*(r/m)^(1-a)<1, pressure sum(c_r*r*((m/r)^a-1)) must be less than D.',
        'proof':'Keep only three seeds. For each r<=7 and m>=22, (m/r)^a-1 >= a*ln(m/r) >= (1/500)*ln(22/7). Use ln(22/7)>2*(15/29+(15/29)^3/3). All inequalities are monotone for a>=1/500.',
        'pressure_strict_lower':str(lower),
        'deficit_upper':deficit,
        'strict_excess':str(lower-deficit),
        'outer_transfer':'Tests primitive a=.002 directly. It does not assume kappa=a/(1+a) is the only available outer theorem. Both direct-target and retained-transfer routes to kappa>=.002 require a>=.002.',
        'negative_controls':['omit one seed','relax max child rank7 to8','increase available deficit33 to35'],
        'not_claimed':['universal BIT upper bound','independent replay of R438 native word','complete new-star owner allocation','new valid kappa'],
    }
    out = json.loads(json.dumps(out))
    target = HERE/'SEEDED-STAR-PRESSURE.json'
    if args.write:
        target.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads(target.read_text()) == out, 'stored exact receipt mismatch')
    print(out['status'])
    print(f'all L>=3, a>=1/500: pressure>{lower}>33; three controls PASS')

if __name__ == '__main__':
    main()
