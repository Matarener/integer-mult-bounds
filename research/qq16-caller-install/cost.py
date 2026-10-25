# SPDX-License-Identifier: Apache-2.0
"""Independent local QQ16 invoice and fixed-grid admission arithmetic.

The caller authenticates all supplied source objects before calling audit.
Counts are not tape-action prices. A charge-screen failure is not a lower
bound on runtime. Chris R / Clear1nsight with OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gamma():
    result = 1 << 1296
    for i in range(1, 37):
        result *= (1 << (2 * i)) - 1
    return result


def ceil_log2_ratio(x):
    x = Q(x)
    need(x >= 1, 'growth factor at least one')
    k = max(0, x.numerator.bit_length() - x.denominator.bit_length())
    while Q(1 << k) < x:
        k += 1
    return k


def decoder_census(word):
    count = Counter()
    for event in word:
        kind = event[0]
        if kind == 'line':
            need(event[3] in (-1, 1), 'signed line')
            count['native_rank_one'] += 1
        elif kind == 'map':
            count['map'] += 1
        elif kind == 'clear':
            count['clear'] += 1
        elif kind == 'add':
            q = Q(event[3])
            need(abs(q) in (1, Q(1, 4)), 'known decoder ADD')
            count['unit_add' if abs(q) == 1 else 'quarter_add'] += 1
        else:
            need(kind in ('begin', 'end', 'checkpoint'), 'complete frozen decoder alphabet')
    need(tuple(count[k] for k in ('native_rank_one', 'map', 'clear', 'unit_add', 'quarter_add'))
         == (224, 352, 416, 1820, 896), 'complete frozen decoder census')
    count['wrapper'] = 2 * count['native_rank_one']
    count['scalar_allowance'] = 8 * count['unit_add'] + 12 * count['quarter_add'] + 2 * count['clear']
    return dict(count)


def native_screen(producer_lines=32, decoder_lines=224, return_lines=112,
                  removed_rank_eight=16):
    need(all(type(x) is int and x >= 0 for x in
             (producer_lines, decoder_lines, return_lines, removed_rank_eight)), 'nonnegative occurrence counts')
    need(removed_rank_eight > 0, 'positive removed native charge')
    added = producer_lines + decoder_lines + return_lines
    ratio_zero = Q(added, 8 * removed_rank_eight)
    need(added > 8 * removed_rank_eight, 'strict endpoint screen')
    return {'added_rank_one': added, 'removed_rank_eight': removed_rank_eight,
            'added_width_sum_over_lambda': added,
            'removed_width_sum_over_lambda': 8 * removed_rank_eight,
            'minimum_added_over_removed_charge_alpha_0_to_1': str(ratio_zero),
            'ratio_at_alpha_1': str(Q(added, removed_rank_eight)),
            'positive_charge_difference_at_alpha_0_over_lambda': added - 8 * removed_rank_eight,
            'zero_native_repair_added_rank_one': producer_lines + decoder_lines,
            'zero_native_repair_deficit_alpha_0': producer_lines + decoder_lines - 8 * removed_rank_eight,
            'formula': '(added - removed*8**(1-alpha))*73**(alpha-1)',
            'scope': 'Isolated same-volume homogeneous native-component tariff, alpha in [0,1]. Does not reject whole-connection affordability: changed retained-root protocols may supply compensating credit. No runtime lower bound or exponent claim.'}


def literal_height(events, lam):
    """Conservative growth/debt of an authenticated physical producer code.

Uses literal op kinds from native_program.compile_local, not final norms.
Completed C tensor contributes rank*lambda; the unfinished native interior
is recorded separately by maximum rank. Horner scratch costs are included.
"""
    need(type(lam) is int and lam >= 1, 'positive lambda')
    growth = debt = maxrank = 0
    count = Counter()
    for op in events:
        kind = op[0]
        count[kind] += 1
        if kind == 'child':
            rank = op[3]
            need(type(rank) is int and 1 <= rank < 73, 'proper native rank')
            growth += rank * lam
            debt += rank * lam
            maxrank = max(maxrank, rank)
        elif kind == 'scalar':
            key = op[4]
            scalar, n, den = key
            q = Q(n, den)
            need(q.denominator & (q.denominator - 1) == 0, 'dyadic scalar')
            need(scalar in ('add', 'scale'), 'scalar operation')
            # Include the Horner scratch numerator before division, not only
            # the completed affine coefficient. Prefix size <= 2|n|+1.
            growth += ceil_log2_ratio(max(Q(1), Q(2 * abs(q.numerator) + 1)))
            debt += q.denominator.bit_length() - 1
        else:
            need(kind in ('marker', 'zero', 'copy', 'monomial', 'identity', 'exchange'), 'complete physical alphabet')
            # Monomials include Gaussian unit phases only. exchange changes a sign.
    return {'growth_bits': growth, 'denominator_bits': debt,
            'maximum_child_rank': maxrank, 'counts': dict(sorted(count.items()))}


def fixed_grid_admission(lam, d, producer_growth, producer_debt,
                         producer_maxrank=48, bridge_coefficient=1):
    """Exact symbolic-integer sufficient local admission; never executes payload.

Entry is an unchanged admitted source cut with component modulus <=2**(2Bd)
    and grid 2**(-p-2Bd). The inserted producer is charged in full afterwards.
    """
    need(type(lam) is int and type(d) is int and 1 <= 73 * lam <= d, 'actual parent width within root')
    need(all(type(x) is int and x >= 0 for x in (producer_growth, producer_debt)), 'producer literal heights')
    need(type(producer_maxrank) is int and 1 <= producer_maxrank < 73, 'producer maximum rank')
    B = 1041408 * gamma() + (1 << 100000)
    Delta = (1 << 210000) * d
    prior = 2 * B * d
    a = 2 * B * lam
    bridge_bits = ceil_log2_ratio(1 + abs(Q(bridge_coefficient)))
    # D whole-word completed bound: growth19+3t, denominator9+3t.
    # Actual current G uses two unit shears: growth2, no denominator debt.
    t = lam - 1
    completed_growth = prior + producer_growth + 19 + 3*t + 2 + lam + bridge_bits
    completed_debt = prior + producer_debt + 9 + 3*t + lam
    # Bound one unfinished callback at each possible stage, including producer.
    interior_growth = max(prior + producer_growth + 2*B*producer_maxrank*lam + 1,
                          prior + producer_growth + 20 + 3*t + a,
                          prior + producer_growth + 22 + 3*t + a)
    interior_debt = max(prior + producer_debt + 2*B*producer_maxrank*lam,
                        prior + producer_debt + 9 + 3*t + a,
                        prior + producer_debt + 9 + 3*t + a)
    growth = max(completed_growth, interior_growth)
    debt = max(completed_debt, interior_debt)
    admitted = growth <= Delta and debt <= Delta
    return {'admitted': admitted, 'lambda': lam, 'root_width': d,
            'producer_growth_bits': producer_growth, 'producer_denominator_bits': producer_debt,
            'bridge_growth_bits': bridge_bits, 'Delta_bit_length': Delta.bit_length(),
            'maximum_growth_bit_length': growth.bit_length(),
            'maximum_debt_bit_length': debt.bit_length(),
            'growth_strictly_below_Delta': growth < Delta,
            'debt_strictly_below_Delta': debt < Delta,
            'grid': '2**(-p-Delta)', 'physical_component_bits': 'p+2*Delta+3',
            'scope': 'Conditional all-size arithmetic admission at unchanged source entry. Physical lowering, producer correctness, long records and original source height theorem remain premises.'}


def module_invoice(word, rows=None):
    decoder = decoder_census(word)
    return {'decoder': decoder, 'reconnection': {
        'unit_add': 224, 'quarter_scale': 0, 'clear': 0,
        'affine_port_map': 0, 'native_rank_one': 112,
        'native_wrapper': 224, 'owner_basis_monomial': 224,
        'physical_line_monomial': 448, 'fixed_port_copyback': 224,
        'bridge_legs_retained': 2,
        'scalar_microinstructions_shear_only': 224*3,
        'scope': 'Actual G=(-y,x+y): W+=Z; Z-=W. Endpoint requires source lift and owner/frame proof. Copyback, disposal, bridge and routing priced separately.'},
        'recovery_and_reconnection': {
            'native_rank_one': decoder['native_rank_one'] + 112,
            'native_wrapper': decoder['wrapper'] + 224,
            'owner_basis_monomial': decoder['wrapper'] + 224,
            'physical_line_monomial': 4*(decoder['native_rank_one'] + 112),
            'maps': decoder['map'],
            'unit_add': decoder['unit_add'] + 224,
            'quarter_add': decoder['quarter_add'], 'quarter_scale': 0,
            'clear': decoder['clear'],
            'scalar_microinstructions_before_copyback':
                decoder['unit_add']*3 + decoder['quarter_add']*5 + decoder['clear'] + 672,
            'scalar_allowance': decoder['scalar_allowance'] + 8*224},
        'same_boundary_difference':
            'Compare N_inst + sum_root_inst(P_inst + A_external + Run_C_external + Z_external) '
            '+ T_service against N_base + sum_root_base(P_base + E_embedded + C_embedded + R_embedded). '
            'Apply at entry-through-bridge first, and retain the later-root protocol delta separately. '
            'Do not cancel retained children or their C execution contexts from equal ranks or outputs. '
            'Only the fixed/adopted variants of the same installation have the proved role-equivariant publication cancellation.',
        'separately_charged_source_tariff_terms': ['encoded descriptor work',
                          'actual C calls at each packet geometry', 'ordinary map/wrapper work',
                          'output fixed-port movement and disposal', 'private/engine inventory',
                          'long-record setup outside inherited rate domain'],
        'native_screen': native_screen(),
        'current_reconnection_bound': {'growth_bits': 2, 'denominator_bits': 0,
            'derivation': 'W+=Z gives at most2M; Z-=W prefix at most3M<4M, exact endpoint -oldW.'}}


def uniform_word_domain(events):
    """Finite source checks supporting the all-lambda inequality in COST.md."""
    need(0 < len(events) < 65536, 'source finite-PC program domain')
    for op in events:
        if op[0] == 'child':
            need(type(op[3]) is int and 1 <= op[3] <= 48, 'selected rank domain')
        if op[0] == 'scalar':
            kind, num, den = op[4]
            q = Q(num, den)
            need(abs(q.numerator) <= 65537 and q.denominator <= 65536,
                 'selected scalar literal domain')
    one = literal_height(events, 1)
    two = literal_height(events, 2)
    growth_slope = two['growth_bits'] - one['growth_bits']
    debt_slope = two['denominator_bits'] - one['denominator_bits']
    growth_constant = one['growth_bits'] - growth_slope
    debt_constant = one['denominator_bits'] - debt_slope
    need(max(growth_constant, debt_constant, growth_slope, debt_slope) < (1 << 22),
         'uniform conservative word-height bound')
    B = 1041408*gamma() + (1 << 100000)
    need(4*B + (1 << 24) < (1 << 210000), 'uniform numerical margin')
    return {'growth_constant': growth_constant, 'growth_lambda_slope': growth_slope,
            'debt_constant': debt_constant, 'debt_lambda_slope': debt_slope,
            'maximum_child_rank': one['maximum_child_rank'],
            'uniform_height_bound': '2**22*(lambda+1)',
            'fixed_grid_all_lambda_domain': 'd>=73lambda, lambda>=1, |bridge coefficient|<=1',
            'strict_margin': '4B+2**24 < 2**210000', 'counts': one['counts']}


def rejection_controls(word):
    rejected = []
    def reject(name, action):
        try:
            action()
        except (ValueError, ZeroDivisionError):
            rejected.append(name)
            return
        raise ValueError('accepted cost mutation: ' + name)
    removed = [list(e) for e in word]
    removed.pop(next(i for i,e in enumerate(removed) if e[0] == 'line'))
    reject('missing native occurrence', lambda: decoder_census(removed))
    wrong = [list(e) for e in word]
    next(e for e in wrong if e[0] == 'add')[3] = '1/3'
    reject('unsupported scalar tariff', lambda: decoder_census(wrong))
    reject('unknown decoder operation', lambda: decoder_census(word + [['teleport']]))
    reject('under-counted native screen', lambda: native_screen(0, 1, 0, 16))
    reject('parent narrower than prepared rank-one domain',
           lambda: fixed_grid_admission(2, 73, 0, 0))
    reject('non-dyadic producer arithmetic',
           lambda: literal_height([('scalar',0,0,1,('add',1,3))],1))
    fail = fixed_grid_admission(1,73,1 << 220000,0)
    need(not fail['admitted'], 'huge actual growth must reject fixed-grid admission')
    rejected.append('insufficient physical range')
    return rejected


def router_invoice(orders, nonzero_translation_maps=None):
    """Per-cover coefficients for source cycle groups; exact rational counts."""
    orders = {int(k): int(v) for k,v in orders.items()}
    need(orders and all(k>=1 and v>=0 for k,v in orders.items()), 'finite positive map orders')
    maps = sum(orders.values())
    translations = maps if nonzero_translation_maps is None else nonzero_translation_maps
    need(type(translations) is int and 0 <= translations <= maps, 'translation map census')
    groups = sum((Q(v,k) for k,v in orders.items()), Q(0))
    swaps = maps-groups
    return {'maps': maps, 'orders': dict(sorted(orders.items())),
            'owner_control_visits_per_Gamma': maps,
            'gather_scatter_commit_groups_per_Gamma': str(groups),
            'source_exchanges_per_Gamma': str(swaps),
            'extra_sign_scales_per_Gamma': str(swaps),
            'exchange_internal_scalar_negations_per_Gamma':str(swaps),
            'direct_dispatch_excludes_exchange_internal':True,
            'translation_monomials_per_Gamma': translations,
            'scope': 'Full-bank scans per emitted cycle. T_exchange includes its internal ScalarEngine negation and transfers; extra sign scale is an additional direct scalar dispatch. Do not charge the nested negation twice.'}


def physical_invoice(word):
    logical = module_invoice(word)
    producer = router_invoice({2:464,5:24,6:12,12:20,17:4,20:4})
    decoder = router_invoice({2:352})
    need(producer['gather_scatter_commit_groups_per_Gamma']=='12286/51', 'producer source map-group coefficient')
    return {'logical': logical, 'coefficient_unit': 'Multiply producer_outer and decoder_service occurrence coefficients by Gamma. Publication executes once per reached global service fence; B already includes the complete cover.',
        'producer_outer': {'unit_or_other_ADD':2200, 'private_CLEAR':32, 'SCALE':16,
            'rank_one_children':32,'intrinsic_wrappers':64,'owner_basis_monomials':64,
            'physical_line_monomials':128,'nonmap_groups':43,
            'all_gather_scatter_commit_groups':'14479/51',
            'original_replaced_group_coefficient':2,'map_router':producer},
        'decoder_service': {'rank_one_children':336,'physical_line_monomials':1344,
            'intrinsic_wrappers':672,'owner_basis_monomials':672,
            'public_CLEAR_scalar_calls':368,'private_zero_calls':48,
            'ADD_scalar_calls':2940,'map_router':decoder,
            'nonmap_groups':1846,'all_gather_scatter_commit_groups':2022,
            'all_monomial_calls_including_map_translations':1696,
            'scalar_engine_calls_including_map_sign_corrections':3484,
            'direct_dispatch_excludes_exchange_internal':True,
            'exchange_internal_scalar_calls':176,
            'exchange_charge_note':'Each source exchange_step has one internal ScalarEngine negation plus transfers; these are included in T_exchange, not in the direct-dispatch3484 or charged a second time.'},
        'bank_volumes': {'owner_packet_v':'P*U*row_bits', 'whole_family_V':'Gamma*v',
            'original_parent_B':'14336*V','service_source_S':'448*V',
            'service_protected_return':'448*V'},
        'service_assembly_extract_bound': '4096*(S+448P*(bE+1)+bP+D_service+1)',
        'selected_publication': {'protocol': 'whole-bank adoption',
            'frequency': 'once per completed global installation',
            'fixed_commit_cell_actions': '20B+30', 'adopt_cell_actions': '9B+26',
            'matched_cell_action_saving': '11B+4',
            'saving_with_additional_finite_control': '11B+4-c_R',
            'scope': 'Matched publication implementations only; all other local installation work identical. No original QQ16 arithmetic or kappa credit.'},
        'paid_service_boundaries': [
            'P-dependent assembly of224borrowed family fields plus initialization224owned zero fields',
            'service Machine.run source copy, encoded node setup, every group full-service-bank scan',
            'service protected return; compare all224borrowed fields; extract224owned fields',
            'erase service assembly bank and protected return',
            '224 fixed-destination transfers plus parent full-bank scatter/adopt/release; original fixed-copy commit retained as matched alternative'],
        'inventory': 'Existing modified producer Machine, separate decoder Machine, separate original recursive C Machine, plus acquisition/compiler/service roles. Separate Ordinary instances and protected-return backing are charged.',
        'scope': 'Constructive operation-sum invoice. Source authentication, map-order/census binding and exact operator refinement are required. No elapsed runtime claim.'}


def uniform_interval_domain(programs):
    """Aggregate source-bound height, including retained intervening groups.

    A supplied code list represents one per-owner complete group body. The
    integrator proves family uniqueness and owner-chart bijectivity, so one
    maximum-norm envelope charges each body once across a complete cover.
    Map cycles are unit-phase permutations and add no numerical height.
    """
    need(type(programs) in (tuple,list) and programs, 'complete source interval programs')
    certificates=[uniform_word_domain(program) for program in programs]
    keys=('growth_constant','growth_lambda_slope','debt_constant','debt_lambda_slope')
    total={key:sum(c[key] for c in certificates) for key in keys}
    need(max(total.values()) < (1 << 22), 'whole interval conservative height bound')
    total.update({'programs':len(programs),
        'maximum_child_rank':max(c['maximum_child_rank'] for c in certificates),
        'uniform_height_bound':'2**22*(lambda+1)',
        'strict_margin':'4B+2**24 < 2**210000',
        'scope':'Actual complete producer interval, per-owner source traversal with family/owner permutation proof; not just the largest one-group PC.'})
    return total


def publication_invoice(bank_bits):
    """Exact matched cell-action difference after common completed scatter.

    Actual operation counts/protocol correspondence are proved and metered in
    lifecycle.py; this independently checks subtraction and distinct units.
    Public ports are fixed, while all internal current-role bindings exchange.
    """
    need(type(bank_bits) is int and bank_bits > 0, 'positive complete bank extent')
    B=bank_bits
    fixed={'reads':9*B+13,'writes':3*B+1,'moves':8*B+16}
    adopted={'reads':4*B+11,'writes':B+1,'moves':4*B+14}
    saved={key:fixed[key]-adopted[key] for key in fixed}
    need(saved=={'reads':5*B+2,'writes':2*B,'moves':4*B+2}, 'literal matched action difference')
    need(sum(saved.values())==11*B+4, 'publication saving exactly once')
    return {'bank_bits':B,'fixed_commit':fixed,'adopted_commit':adopted,
            'saved_cell_actions_by_kind':saved,'saved_cell_actions':sum(saved.values()),
            'finite_control_charge':'c_R additional to tape actions',
            'complete_comparison':'T_install_adopt = T_install_fixed - (11B+4) + c_R',
            'scope':'Same read-complete/scattered state and same continuation, fixed public ports, all internal current bindings updated. No source arithmetic credit.'}


def root_protocol_invoice(census):
    """Bind independently checked counts to an authenticated actual source census.

    This enumerates operation sums; it does not estimate an unmeasured protocol
    delta or identify embedded and external C contexts from matching ranks.
    """
    def hist(name):
        row=census[name]
        h={int(k):v for k,v in row['rank_counts'].items()}
        need(all(type(v) is int and v>=0 for v in h.values()), 'root rank multiplicity')
        need(sum(h.values())==row['calls'], 'root call sum')
        need(sum(k*v for k,v in h.items())==row['rank_mass'], 'root rank mass')
        return Counter(h)
    baseline=hist('baseline_whole_root');installed=hist('installed_whole_root')
    prefix=hist('baseline_entry_through_bridge');newprefix=hist('installed_entry_through_bridge')
    suffix=hist('retained_later_source_7_481')
    need(baseline==Counter({1:349604,2:60192,3:62585,4:20448,5:11808,7:7,8:1152,48:4866}),
         'frozen original whole-root child census')
    need(baseline==prefix+suffix and installed==newprefix+suffix, 'prefix and later root partition')
    removed=Counter({8:16});added=Counter({1:32})
    need(installed==baseline-removed+added and newprefix==prefix-removed+added,
         'only named native replacements')
    need((sum(prefix.values()),sum(newprefix.values()),sum(suffix.values()))==(17565,17581,493097),
         'source boundary multiplicities')
    retained=baseline-removed
    return {'unit':'Each occurrence coefficient multiplies Gamma at this one modified outer root; original recursive descendants are inside their C execution terms.',
        'baseline_root_calls':sum(baseline.values()),
        'installed_root_calls':sum(installed.values()),
        'service_external_calls':336,
        'all_external_runs':sum(installed.values())+336,
        'retained_root_calls_with_changed_protocol':sum(retained.values()),
        'retained_prefix_calls_with_changed_protocol':sum((prefix-removed).values()),
        'later_root_calls_with_changed_protocol':sum(suffix.values()),
        'baseline_prefix_calls':sum(prefix.values()),
        'installed_prefix_and_service_calls':sum(newprefix.values())+336,
        'baseline_rank_counts':dict(sorted(baseline.items())),
        'installed_rank_counts':dict(sorted(installed.items())),
        'embedded_call_operation_sum':[
            'P_b: prepare_child arithmetic, capsule payload and descriptor copies, encoded header, Count closure',
            'E_b: primitive boundary and role origins, Parking.park on every live parked role, capsule-to-active transfers and child control setup',
            'C_emb: actual original child node/body and recursive descendants in embedded nonroot context; excludes its final parent return',
            'R_b: output transfer, active child role cleanup, Parking.restore, header read/clear, group reconstruction, output-to-parent target transfer and bank/head rebinding'],
        'external_call_operation_sum':[
            'P_i: actual prepare_child arithmetic, capsule copies, encoded header and Count closure, with installed event indices',
            'A_i: boundary/header/instruction checks and finite descriptor views',
            'Run_C_ext: complete separate original Machine.run, borrowed input and descriptor copies, node setup, body/descendants, root protected return and engine closure',
            'Z_i: protected output-to-target transfer, output-marker erase, all capsule and header cleanup and PC update'],
        'nonchild_operation_sum':[
            'N_b or N_i: root Machine.run input/descriptors/setup, all nonchild scalar/monomial/exchange and group bank operations, event/owner control, final root output/cleanup',
            'N_i includes every installed finish_group fence predicate, including after the local continuation',
            'T_service contains assembly/compiler/lifecycle, service nonchild Machine.run/setup/return, and all336 external service child sums exactly once'],
        'exact_execution_comparison':'N_i + sum_inst(P_i+A_i+Run_C_ext+Z_i) + T_service < N_b + sum_base(P_b+E_b+C_emb+R_b)',
        'retained_protocol_credit':'sum_retained[(P_b+E_b+C_emb+R_b)-(P_i+A_i+Run_C_ext+Z_i)]',
        'later_obligation':'493097*Gamma changed root child protocols plus any later nonchild/control/context delta; retained source instructions alone do not cancel these costs.',
        'component_screen_only':True,
        'body_context_cancellation_proved':False,
        'next_discriminator':'Meter paired source embedded versus external child calls with actual live parent bank/descriptors/dirty backing and descendant context; then compare the constructive protocol credit against all added bank scans and service costs.'}
