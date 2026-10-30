#!/usr/bin/env python3
"""Cheap source-specific census and majorants; no native/endpoint/flow replay."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
PINS = {
    'HILBERT-FIBER-REVIEW.md': '588743fb8890231da350fd86cef3fb6618769b953cdf20e2753e99d403ed54be',
    'CUT-STABILITY-RESULT.json': '7b1cf55ecd8d8aac08c24916fd477acf155a6f63fce1680f505266e8686f33f5',
    'PR5551-RESULT.json': '36a5680f43c7da67e570b6c919de2934c6a5ce46db002993ff162aa36972d0ba',
    'SELECTED-V16-APPLICATION-PROOF-v3.md': 'cda8f596f7854f42a228f757d5f8e68f6b2256a19c5ae3771fb40753cedc5b39',
    'WORD.json.gz': '48f8734ca9c5adf5d60ded3a5fefbc24894d2c358ed7cb30fcc0d71718599446',
    'caller.py': '300d40043953e4f6aecfde8f2d1004b8ad6dc5a79ec3c7666c9908c2466c91c8',
    'controller.json': 'a84f6bbd547379597464e56c420cc665f96bc43a9a1351eed4b7cd0fce3cc4b9',
    'local.py': '878734dfd64c4b9d362d0ae476cc5c2a19fe93e48b7378763b23f3e0dd0a5a71',
    'physical.json': 'b257eb40480269328821e334de3fef6c64a652ff4f0628411a98be398d4cfea0',
}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def read(name):
    raw = (HERE/'inputs'/name).read_bytes()
    need(sha256(raw).hexdigest() == PINS[name], 'Input pin: '+name)
    if name.endswith('.gz'):
        raw = gzip.decompress(raw)
    return json.loads(raw) if name.endswith(('.json', '.gz')) else raw.decode()

def ceil_log2(q):
    need(q > 0, 'Positive logarithm')
    a, b = q.numerator, q.denominator
    e = a.bit_length()-b.bit_length()
    if e >= 0:
        return e + (a > b << e)
    return e + ((a << -e) > b)

def derive():
    inputs = {name:read(name) for name in PINS}
    w, c, p, old, cut = (inputs[n] for n in (
        'WORD.json.gz', 'controller.json', 'physical.json',
        'PR5551-RESULT.json', 'CUT-STABILITY-RESULT.json'))
    need(w['public'] == 735 and len(w['live']) == len(w['ports']) == 104,
         'Actual public/port census')
    need(len(w['initial']) == len(w['final']) == 735, 'Every public role retained')
    need((c['kind'], c['pairs'], c['prefix_pairs'], c['ambient_rank']) ==
         ('complex',16,7,145), 'Actual controller class')
    ops = Counter(e[0] for e in w['program'])
    need(ops == Counter(ADD=20947,SCALE=715,MOVE=3624,INIT=8,COPY=8,CLEAR=8),
         'Actual local opcode inventory')
    dims = [len(f) for f in w['frames']]
    current = list(w['initial']) + [None]*8
    owned = set()
    paid, scalar = Counter(), 0
    growth = [0]*743
    den = [0]*743
    power, denmax, product_power, product_den = 0, 0, 0, 0
    maxq, maxqd, peak = Q(0), 0, 0
    maxdim = max(dims[i] for i in current if i is not None)
    for e in w['program']:
        op, r = e[:2]
        need(0 <= r < 743, 'Role range')
        if op == 'MOVE':
            _, r, a, b, private = e
            need(current[r] == a and private == (r in owned), 'Actual MOVE contact')
            paid[abs(dims[b]-dims[a])] += 1
            current[r] = b
        elif op in ('INIT','CLEAR'):
            if op == 'INIT':
                need(r >= 735 and r not in owned, 'Owned INIT')
                owned.add(r)
                current[r] = e[2]
                peak = max(peak,len(owned))
            else:
                need(r in owned and current[r] == e[2], 'Owned CLEAR')
                owned.remove(r)
                current[r] = None
            growth[r] = den[r] = 0
            scalar += 2
        else:
            q, frame = Q(e[-2]), e[-1]
            need(q and current[r] == frame, 'Scalar destination chart')
            n, d = abs(q.numerator), q.denominator
            need(d & (d-1) == 0 and abs(q)+1 < 2**16, 'Gaussian-dyadic scalar guard')
            qden, qgrowth = d.bit_length()-1, ceil_log2(abs(q))
            maxq, maxqd = max(maxq,abs(q)), max(maxqd,qden)
            product_power += ceil_log2(1+abs(q))
            product_den += qden
            if op == 'SCALE':
                need(n & (n-1) == 0, 'Dyadic-unit SCALE')
                growth[r] = max(0,growth[r]+qgrowth)
                den[r] += qden
                scalar += 2*(abs(n.bit_length()-d.bit_length())+int(q<0))
            else:
                s = e[2]
                need(s != r and current[s] == frame, 'Common-chart source')
                need(op in ('ADD','COPY'), 'Local scalar opcode')
                if op == 'COPY':
                    need(r in owned, 'COPY owns its destination')
                # Physical COPY is ADD into the initialized zero. Arbitrary
                # injected owned residuals are retained by this recurrence.
                growth[r] = max(growth[r],growth[s]+qgrowth)+1
                den[r] = max(den[r],den[s]+qden)
                scalar += 2*(3+n.bit_length()-1+n.bit_count()+qden)
            power, denmax = max(power,growth[r]), max(denmax,den[r])
        if current[r] is not None:
            maxdim = max(maxdim,dims[current[r]])
    need(not owned and current[:735] == w['final'] and peak == 1, 'All exits and local ownership')
    need(scalar == old['local']['real_scalar_allowance'] == 217428, 'Actual scalar tariff')
    need(dict(paid) == {int(k):v for k,v in old['local']['paid'].items()}, 'Actual paid profile')
    interval = cut['all_interval_majorant']
    need((power,denmax) == (interval['scalar_amplification_power_of_two'],
                           interval['scalar_denominator_exponent_upper']) == (296,54),
         'Independent linear-time all-interval DP')
    need(cut['word_sha256'] == PINS['WORD.json.gz'], 'All-cut source binding')
    need(Q(cut['prefix_max_row_l1']) == 2**17 and Q(cut['suffix_max_row_l1']) == Q(135415,4),
         'Retained exact all-cut endpoint bounds')
    need((product_power,product_den,maxq,maxqd,maxdim) == (27646,17032,Q(65537,2),16,9),
         'Independent product bound and source scalar/chart guards')
    event_ops = Counter(e[0] for e in c['physical_events'])
    side_ops = {side:Counter(e[0] for e in c['boundaries'][side+'_program'])
                for side in ('right','left')}
    need(event_ops == Counter(ADD=90,SIGNED_SWAP=48,Q_POWER=32,LOCAL=18,IDLE=15,QUERY_SHEAR=15),
         'Physical event species')
    for side in ('right','left'):
        for e in c['boundaries'][side+'_program']:
            need(e[0] in ('ADD','SWAP','SCALE'), 'Boundary species')
            if e[0] == 'ADD': need(abs(Q(e[3])) == 1,'Unit boundary ADD')
            if e[0] == 'SCALE': need(Q(e[2]) == -1,'Boundary sign')
    need(all(abs(Q(e[3])) == 1 for e in c['physical_events'] if e[0]=='ADD'), 'Unit physical ADD')
    locals_ = [e for e in c['physical_events'] if e[0]=='LOCAL']
    need(all(not e[3] for e in locals_), 'All-forward implementation')
    need(c['wrapper_sites'] == list(range(1,32,2)), 'Sixteen inverse wrappers')
    idle_lengths = [len(e[2]) for e in c['physical_events'] if e[0]=='IDLE']
    need(idle_lengths == list(range(2,10))+list(range(8,1,-1)), 'Actual idle sequence')
    idle_ranks = [8*n for n in idle_lengths]
    main_profile = Counter()
    for t in c['diagonal']:
        need(t[0] in (-1,1), 'Q exponent, not scalar sign')
        main_profile[1+8*sum(t[1:])] += 104
    need(dict(main_profile) == {int(k):v for k,v in p['main_targets'].items()}, '32-bank main targets')
    idle_profile = Counter()
    for r in idle_ranks: idle_profile[r] += 208
    need(dict(idle_profile) == {int(k):v for k,v in p['whole_idle_jobs'].items()}, 'Idle targets')
    boundary_adds = sum(x['ADD'] for x in side_ops.values())
    boundary_swaps = sum(x['SWAP'] for x in side_ops.values())
    boundary_signs = sum(x['SCALE'] for x in side_ops.values())
    outer_layers = boundary_adds + event_ops['ADD'] + 3*(boundary_swaps+event_ops['SIGNED_SWAP'])
    outer_signs = boundary_signs + boundary_swaps
    norm_const = outer_layers + 2*event_ops['QUERY_SHEAR']
    norm_N = 36*len(locals_) + event_ops['QUERY_SHEAR'] + sum(idle_ranks)
    whole_power, whole_den = norm_const+len(locals_)*power, len(locals_)*denmax
    need((outer_layers,outer_signs,norm_const,norm_N,whole_power,whole_den) == (486,64,516,1295,5844,972),
         'Whole declared-interface composition')
    main = set(w['live']) | {r+112 for r in w['live']}
    helpers = 735-len(main)
    helper_profile = Counter(dims[w['final'][r]]-dims[w['initial'][r]] for r in range(735) if r not in main)
    need(dict(helper_profile) == {int(k):v for k,v in old['local']['helpers'].items()}, 'All dirty helpers retained')
    owned_positions = 18*8+104
    productive = 32*104+18*helpers
    paid_count = 18*sum(paid.values()) + 15*104 + sum(idle_profile.values())
    paid_mass = 18*sum(r*n for r,n in paid.items()) + 15*104 + sum(r*n for r,n in idle_profile.items())
    target_mass = sum(r*n for r,n in main_profile.items()) + 18*sum(r*n for r,n in helper_profile.items())
    need((productive,owned_positions,paid_count,paid_mass,target_mass) == (12814,248,69912,239108,239868),
         'Whole productive/owned/paid inventory')
    local_maps = {
        'MOVE_two_sided_maps':2*ops['MOVE']*18,
        'source_helper_alias_maps':2*helpers*18,
        'intrinsic_main_maps':208*18,
        'stage_main_contacts':p['physical_contacts'],
        'controller_Q_POWER_X_maps':32*104,
    }
    added_maps = {
        'whole_main_layout_P':2*32*104,
        'whole_helper_layout_P':2*18*helpers,
        'whole_IDLE_layout_P':2*sum(idle_profile.values()),
        'negative_Q_final_X':16*104,
        'query_two_sided_layout_P':2*15*104,
        'query_inverse_Q_X':15*104,
    }
    need(sum(local_maps.values()) == 163996 and sum(added_maps.values()) == 38212, 'Charged monomial ledger')
    outer_scalar = 104*(8*outer_layers+2*outer_signs)
    query_scalar = 20*15*104 # COPY ADD8 + scatter ADD8 + two owned clears4
    initial_query_scalar = 2*104
    explicit_scalar = 18*scalar+outer_scalar+query_scalar+initial_query_scalar
    historical_raw = old['complete_cost']['nonrecursive']['raw_scalar_upper']
    need(historical_raw == 184647552 and explicit_scalar == 4362776, 'Fresh scalar bill')
    # Deliberately count the historical bound again as records; it cannot
    # supply missing normalization/query tariffs in this fresh inventory.
    I = (1+historical_raw+18*len(w['program'])+104*(len(c['physical_events'])+
         sum(sum(v.values()) for v in side_ops.values()))+
         4*(sum(local_maps.values())+sum(added_maps.values()))+
         owned_positions+paid_count+productive+6*15*104)
    axis_recipe = 64*(265+1)**3
    R = axis_recipe*I**3+explicit_scalar
    G = explicit_scalar+8*R
    need(max(I,R,G).bit_length() <= 128, 'Fresh raw fixed-recipe majorants')
    return {
        'status':'PASS_SOURCE_SPECIFIC_DECLARED_INTERFACE_MAJORANTS',
        'input_sha256':PINS,
        'word_canonical_sha256':sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'source':{'main_commit':'13be6ac685845c1ff671f5d26e7166165abd998e',
                  'execution_order':['RIGHT','physical_events','LEFT'],
                  'physical_axes':265,'pairs':16,'main_banks':32,
                  'selected_V16_proof_sections':[1,2,3,4,6,7,8],
                  'COPY_contract':'ADD into an initialized owned zero; arbitrary injected owned residual retained'},
        'local':{'ops':dict(ops),'instructions':len(w['program']),'roles_with_owned':743,
                 'initial_dim_histogram':dict(Counter(dims[i] for i in w['initial'])),
                 'input_max_chart_dim':5,'current_max_chart_dim':maxdim,
                 'max_abs_scalar':str(maxq),'max_scalar_denominator_exponent':maxqd,
                 'scalar_allowance':scalar,'paid_profile':dict(paid),'helper_targets':dict(helper_profile),
                 'all_interval_scalar_power':power,'all_interval_denominator_exponent':denmax,
                 'all_interval_meaning':'Upper bound, not the exact maximal interval norm',
                 'independent_product_power':product_power,'independent_product_denominator':product_den,
                 'prefix_declared_N_exponent':23,'suffix_declared_N_exponent':27,
                 'interval_declared_N_exponent':36},
        'caller':{'event_ops':dict(event_ops),'boundary_ops':{k:dict(v) for k,v in side_ops.items()},
                  'local_stages':[e[1] for e in locals_],'idle_lengths':idle_lengths,
                  'idle_sum_rank':sum(idle_ranks),'outer_lowered_ADD_layers':outer_layers,
                  'outer_sign_layers':outer_signs,'main_targets':dict(main_profile),
                  'idle_paid':dict(idle_profile),'query_uses':15*104},
        'reservation':{'main_fields':3328,'independent_helper_fields':18*helpers,
                       'productive_fields':productive,'occurrence_tagged_local_owned':144,
                       'reusable_query_owned_bank':104,'owned_positions':owned_positions,
                       'complete_raw_positions':productive+owned_positions,
                       'meaning':'Constructive reservation, not an observed simultaneous peak',
                       'separate_query_occurrences_overreservation':productive+144+1560,
                       'paid_jobs':paid_count,'paid_rank_mass':paid_mass,'target_rank_mass':target_mass},
        'ordinary':{'historical_source_raw_upper_diagnostic_only':historical_raw,
                    'source_map_ledger':local_maps,'additional_map_ledger':added_maps,
                    'outer_scalar_allowance':outer_scalar,'query_scalar_allowance':query_scalar,
                    'query_bank_initialization_allowance':initial_query_scalar,
                    'fresh_explicit_scalar_allowance':explicit_scalar,'raw_inventory_overestimate_I':I,
                    'raw_265_axis_recipe_factor':axis_recipe,'Rraw_upper':str(R),'Graw_upper':str(G),
                    'Rraw_bits':R.bit_length(),'Graw_bits':G.bit_length(),
                    'tensor_f_recipe_bound':'Rschema(f)<=Rraw*(f+1)^3; Gschema(f)<=Graw*(f+1)^3',
                    'scope':'Fixed primitive-schema/descriptor majorants under the selected finite physical compiler; not literal arbitrary-f tape-step counts'},
        'whole_declared_interface':{'norm':'realified coordinatewise sup norm',
            'maximum_individual_field_Hilbert_power_of_two':whole_power,
            'sharper_active_fiber_coordinate_bound':'2^(5844+ceil((265*f+1)/2))',
            'Hilbert_method_credit':'Ross Richardson / Adam Gall; retained p104-retimed-internal-grid lineage',
            'interval_prefix_suffix_row_sum_bound':{'power_of_two':whole_power,'N_exponent':norm_N},
            'coefficient_denominator_exponent':{'constant':whole_den,'f_coefficient':norm_N},
            'independent_product_crosscheck':{'power_of_two':norm_const+18*product_power,
                'N_exponent':norm_N,'denominator_constant':18*product_den},
            'storage_per_real_imag_component_bits':'b+d0+6818+2590*f',
            'raw_storage_bits':'2*13062*N^265*(b+d0+6818+2590*f), plus fixed descriptors and recursive child reservations',
            'input_output_error_ABI':'For every declared-interface interval, ||delta_out||inf <=2^5844*N^1295*||delta_in||inf; multiple site errors sum their separately transported contributions',
            'cut_scope':'Declared field operations and canonical native-C factors only; unmaterialized scalar/movement/recursive-child interiors require their retained primitive contracts'},
        'limits':['No new efficiency ratio, kappa, selected promotion, unconditional theorem or human/proof-kernel acceptance.',
                  'No materialized uniform word or rounded multiplier; no fresh literal tape microprogram.',
                  'The native/all-column, owned-erasure, finite-compiler, precision/tape and analytic-recovery premises remain.',
                  'Fresh constants belong in precision/storage/setup and outer domain thresholds, not absorption at the fixed carrier N.'],
    }

def main():
    result = json.loads(json.dumps(derive()))
    path = HERE/'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads(path.read_text()) == result, 'Exact saved receipt')
    print(result['status'])
    print('whole:2^5844*N^1295; denom:972+1295*f; raw slots:13062')
    print('fresh raw R/G bits:',result['ordinary']['Rraw_bits'],result['ordinary']['Graw_bits'])

if __name__ == '__main__':
    main()
