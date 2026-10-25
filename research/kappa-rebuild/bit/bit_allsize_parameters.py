#!/usr/bin/env python3
"""Exact parameters for the delayed-cover BIT ordinary interface.

This records conditional all-size implications, not a materialized winning
uniform mixed-flow template. Apache-2.0; substantial OpenAI assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import mixed_productive_bit as B

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def run():
    profile_path=HERE/'MIXED-PRODUCTIVE-BIT.json'
    profile=json.loads(profile_path.read_text())
    case=next(c for c in profile['candidates']if c['pairs']==3)
    paid={int(k):v for k,v in case['paid'].items()}
    targets={int(k):v for k,v in case['targets'].items()}
    before,after=Q(69,25000),Q(11,4000)
    gap=before-after
    delta,old=Q(3,1000),Q(384599,10**10)
    raw=(1-delta)*after+delta*old
    admitted=Q(27,10000)
    margin=B.interval_row(B.margin_interval(paid,targets,before))
    B.need(margin['strict_positive'],'The exact mixed rule supports C0=.00276')
    B.need(gap==Q(1,100000) and before>after>0,'Strict precompile-to-cover gap')
    B.need(delta>raw>admitted>0 and delta<1-raw,'Adapter and borrowing powers fit')
    prime_coefficient=256/gap
    fallback_bound,power_lower=1+gap/4,1+gap/2
    B.need(fallback_bound<power_lower,'Positive cover moment slack')
    sources=[Path(__file__),profile_path,HERE/'BIT-P3-NATIVE-BINDING.json',
             HERE/'DELAYED-COVER-BRIDGE.md',HERE/'DELAYED-COVER-BRIDGE.json',
             ROOT/'notes/three-stage-cover-bit.tex',ROOT/'notes/three-stage-cover-rows.tex',
             ROOT/'notes/batched-bit-rows.tex']
    return {'schema':'conditional-delayed-cover-BIT-allsize-parameters/1',
            'status':'PASS_EXACT_PARAMETERS_CONDITIONAL_ON_FINITE_UNIFORM_PRECOMPILATION',
            'C0_before_cover':str(before),'C1_after_cover':str(after),'C0_minus_C1':str(gap),
            'mixed_margin_at_C0':margin,
            'finite_template_hypothesis':'Fixed integers N>=2,B>=1,P>=1 and a whole-cover native schematic uniform word, with P/B < N^(1-C0), final paid leaves of rank1, arbitrary productive inputs and separately owned storage.',
            'prime_rule':{'bound':'q > '+str(prime_coefficient)+' * N^5',
                          'also_required':'Odd prime avoiding every fixed rational denominator, matcher determinant and chosen rank witness of the entire compiled word.',
                          'good_moment_upper':'N^(-d), d=C0-C1',
                          'fallback_multiplier_upper':str(fallback_bound),
                          'N_to_d_lower':str(power_lower),
                          'complete_moment_upper':str(fallback_bound/power_lower),
                          'strict_moment_slack_lower':str(1-fallback_bound/power_lower)},
            'atom_power':str(delta),'old_ordinary_saving':str(old),
            'ordinary_saving_before_final_relaxation':str(raw),
            'ordinary_saving_display':float(raw),'ordinary_saving_admitted':str(admitted),
            'strict_power_gaps':{'linear_adapter':str(delta-raw),
                                 'borrowed_stock_log_absorption':str(1-raw-delta),
                                 'final_relaxation':str(raw-admitted)},
            'root_cost_terms':['e^(1-delta)',
                               'e^((1-delta)*(1-C1)+delta*(1-a_old))',
                               'e^delta * log(e)'],
            'stock':{'role_divisor':'W(w)=B*|GL_N(F_q)|*q^(N^2*(w-1))',
                     'depth_bound':'D_N(n)=floor(log_N n) for rank<=floor(n/N) children; any larger explicit integer bound is safe.',
                     'reserve':'S(e,w)=W(w)^D_N(ceil(e/w))*S_old(e,w)',
                     'borrowed_digits':'k <= D_N(ceil(e/w))*(N^2*(w-1)+ceil(log_q(B*|GL_N(F_q)|)))+ceil(log_q S_old)+1',
                     'asymptotic':'Fixed compiled N,B,P: k=O_(N,B,q)(w*log e)=o(e), w=ceil(e^(3/1000)); pad high rows once by factor<2.',
                     'descendant_weights':'Only final leaves are lowered. This outer cover row and role type become ancestor data; every next ordinary invocation has fresh disjoint role stock.'},
            'finite_constants_to_replace':{'productive_roles':'B, not3739 or661',
                                           'ambient_dimension':'N, not50 or64',
                                           'paid_leaf_count':'P, including copied-center descendants',
                                           'owned_storage':'C, bounded by one owned bank per allocated finite unit instance',
                                           'pointwise_and_copy_count':'L, literal compiled scalar/copy/erase records',
                                           'fixed_row_routes':'R, original port charts and every internal matcher/inverse',
                                           'generic_affine_work':'At most4*N^2-2*N basic shears per rank1 normalizer together with its inverse',
                                           'bad_fallback_children':'At most32*N^2 per bad final leaf',
                                           'coefficient_data':'Every fixed rational entry, inverse, determinant, prefix descriptor and height'},
            'new_kappa':False,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest()for p in sources}}

if __name__=='__main__':
    result=run()
    (HERE/'BIT-ALLSIZE-PARAMETERS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k]for k in ('status','C0_before_cover','C1_after_cover','ordinary_saving_before_final_relaxation','ordinary_saving_admitted')}))
