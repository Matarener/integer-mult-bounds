# SPDX-License-Identifier: Apache-2.0
"""Source-derived normalized complete signed lower certificate.

The three published prices are derived bounds, not unexplained oracle inputs.
This evaluator deliberately does not manufacture a price for recursive C.
"""
from fractions import Fraction
from math import prod

def need(ok,why):
    if not ok:raise ValueError(why)

def gamma():
    # Authenticated OrthogonalCover.group_orders recurrence, independently
    # checked against the source by gate_cover and the separate checker.
    return prod((1 << (k-1))-int(k>1 and k%2==1) for k in range(1,74))

def exclusion(columns=5):
    need(type(columns) is int and columns>=5,'exact installed column count')
    g=gamma()
    volume=Fraction(281593,816)*14336*g
    need(volume.denominator==1,'whole cover source group volume')
    a=int(volume)
    # Complete terminal C bound E_w <= 2^33(w+1)v in each component,
    # derived from the actual source with Hb>=L^4; all 16 removed calls.
    body=16*(1<<33)*(8*columns+1)
    copies=8*(1<<22)
    shells=16*(1<<26)
    debit=body+copies+shells
    ordinary_original_calls=510662
    retained=510646
    slope=[2*a+5*ordinary_original_calls-debit,
           a+2*ordinary_original_calls-debit,
           2*a+4*ordinary_original_calls-debit]
    constant=[12*retained+2*ordinary_original_calls,
              4*retained,
              12*retained+2*ordinary_original_calls]
    maximum=(a+2*ordinary_original_calls-16*(1<<33)-copies-shells-1)//(128*(1<<33))
    need(columns<=maximum and min(slope)>0,'complete positive signed bound domain')
    at_minimum=[g*(2685*x+y)-66496 for x,y in zip(slope,constant)]
    need(min(at_minimum)>0,'once-only startup and retirement debit')
    return {
        'variant':'frozen D minus Bstar','columns':columns,'gamma':g,
        'terminal_predicate':'8 lambda < 73 OR (8 lambda)^1000 < d',
        'parent_predicate':'actual RootPlan fast entry; e=73 lambda; d <= e^1000',
        'geometry_domain':'complete P,U,c,stored Hb,address b; Hb>=L^4; v>=2685; common admitted q/profile/programs/capacities',
        'body_removed_per_Gamma_v_upper_each':body,
        'copies_removed_per_Gamma_v_upper_each':copies,
        'shells_removed_per_Gamma_v_upper_each':shells,
        'added_groups_volume_per_Gamma_v':a,
        'lower_bound_RWM':{'Gamma_times_v_coefficients':slope,
                          'Gamma_constant_coefficients':constant,
                          'subtract_once_per_component':66496},
        'maximum_positive_columns':maximum,
        'strict_all_RWM_exclusion':True,
        'minimal_component_lower_bit_lengths':[x.bit_length() for x in at_minimum],
        'compiled_control':'separate signed difference; all-step exclusion requires control difference >= minus weighted action lower bound',
        'unknown_prices_used':False,
        'new_engine_tapes_or_reset':False,
        'production_payload_executed':False}

def controls():
    last=exclusion()['maximum_positive_columns'];bad=[]
    for label,value in [('bool columns',True),('unreachable small columns',4),
                        ('negative columns',-1),('first nonpositive bound',last+1)]:
        try:exclusion(value)
        except ValueError:bad.append(label)
        else:raise ValueError('accepted bound control:'+label)
    return {'last_positive_columns':last,'endpoint':exclusion(last),'rejections':bad}
