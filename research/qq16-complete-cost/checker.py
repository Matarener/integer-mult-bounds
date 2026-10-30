# SPDX-License-Identifier: Apache-2.0
"""Independent signed-interval arithmetic and physical-boundary checker.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance.
This module does not import the evaluator. Its arithmetic checks do not prove
that a supplied endpoint bounds an actual source interval: those endpoints must
be certified by the package's authenticated source derivation/calibration.
"""
from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(x, lower=None):
    require(type(x) is int, 'exact integer, excluding bool')
    require(lower is None or x >= lower, 'integer outside admitted range')
    return x


@dataclass(frozen=True)
class Bound:
    lo: int
    hi: int

    def __post_init__(self):
        integer(self.lo); integer(self.hi)
        require(self.lo <= self.hi, 'reversed interval')

    def plus(self, other):
        return Bound(self.lo + other.lo, self.hi + other.hi)

    def minus(self, other):
        # In particular, subtract the REMOVED upper endpoint for a lower bound.
        return Bound(self.lo - other.hi, self.hi - other.lo)

    def times(self, coefficient):
        integer(coefficient)
        a, b = coefficient * self.lo, coefficient * self.hi
        return Bound(min(a, b), max(a, b))

    def json(self):
        return {'lower': self.lo, 'upper': self.hi}


def exact(x):
    return Bound(x, x)


def triple(values):
    require(type(values) in (list, tuple) and len(values) == 3,
            'separate read/write/unit-move components')
    return tuple(Bound(*value) if type(value) in (list, tuple) else exact(value)
                 for value in values)


def add(a, b):
    return tuple(x.plus(y) for x, y in zip(a, b, strict=True))


def subtract(a, b):
    return tuple(x.minus(y) for x, y in zip(a, b, strict=True))


def scale(a, k):
    return tuple(x.times(k) for x in a)


def summed(a):
    result = exact(0)
    for x in a:
        result = result.plus(x)
    return result


CENSUS = {'original': 510662, 'same_payload': 503674, 'changed_core': 6972,
          'later': 493097, 'producer_added': 32, 'service_added': 336,
          'removed': 16}


def census_check(record):
    require(type(record) is dict and record == CENSUS and
            all(type(x) is int for x in record.values()), 'complete literal occurrence census')
    retained = record['same_payload'] + record['changed_core']
    require(retained + record['removed'] == record['original'], 'original partition')
    return {'retained': retained, 'candidate_external': retained +
            record['producer_added'] + record['service_added'],
            'retained_header_actions': 28 * retained,
            'later_header_actions': 28 * record['later']}


def volumes(*, gamma, prefixes, unused_rows, physical_component_bits,
            coefficients, address_bits, recorded=None):
    for value in (gamma, prefixes, unused_rows, physical_component_bits, coefficients):
        integer(value, 1)
    integer(address_bits, 0)
    # This is complete packet extent, not active rank or logical precision.
    row = 2 * physical_component_bits * coefficients * (1 << address_bits)
    owner = prefixes * unused_rows * row
    family = gamma * owner
    result = {'row_bits': row, 'owner_packet_bits': owner,
              'family_bits': family, 'bank_bits': 14336 * family,
              'service_bank_bits': 448 * family}
    require(result['bank_bits'] == 32 * result['service_bank_bits'], 'service bank extent')
    if recorded is not None:
        require(recorded == result and all(type(v) is int for v in recorded.values()),
                'complete compiler physical geometry, Gamma exactly once')
    return result


# A cost grouping must retain complete descriptors, original source binding,
# compiled program/recipe and marker class. History is removed only by #4172's
# paired successful-domain theorem; production-selector policy is not omitted.
GEOMETRY_FIELDS = ('prefixes', 'unused_rows', 'active_width', 'spectator_before',
                   'spectator_after', 'coefficients', 'physical_component_bits',
                   'spacing', 'root_width', 'address_guard', 'row_stock',
                   'compiled_recipe', 'source_binding', 'marker_class',
                   'ordinary_selection')


def geometry_key(record):
    require(type(record) is dict and set(record) == set(GEOMETRY_FIELDS),
            'complete cost-sensitive descriptor key')
    require(all(type(record[k]) in (int, str, tuple) for k in GEOMETRY_FIELDS),
            'canonical descriptor representation')
    return tuple(record[k] for k in GEOMETRY_FIELDS)


def certify_same_geometry(a, b):
    require(geometry_key(a) == geometry_key(b), 'unsafe geometry grouping')


def complete_body(receipt):
    require(type(receipt) is dict and set(receipt) ==
            {'geometry', 'own_actions', 'descendant_actions', 'total_actions',
             'includes_descendants_once', 'successful_return'}, 'complete body receipt fields')
    geometry_key(receipt['geometry'])
    require(receipt['includes_descendants_once'] is True and
            receipt['successful_return'] is True, 'completed recursion and return required')
    own, descendants, total = (triple(receipt[k]) for k in
                              ('own_actions', 'descendant_actions', 'total_actions'))
    require(add(own, descendants) == total, 'omitted or double-counted descendants')
    require(all(x.lo >= 0 for part in (own, descendants) for x in part),
            'physical costs cannot be negative')
    return total


# Mandatory disjoint root intervals. 'body' is excluded here. The evaluator
# must derive both endpoints and the partition; the checker never supplies zero
# for a missing invoice. Exact common cancellation may legitimately have zero.
NONCHILD = ('producer_nonchild', 'acquisition_compiler', 'service_nonchild',
            'bank_scans_fences', 'extraction_publication_disposal',
            'constructor_startup_terminal')
SHELLS = ('producer_added_shells', 'service_added_shells', 'removed_B_shells')


def ledger_check(ledger):
    require(type(ledger) is dict and set(ledger) == set(NONCHILD + SHELLS),
            'complete disjoint nonchild and unmatched-shell ledger')
    return {key: triple(ledger[key]) for key in NONCHILD + SHELLS}


def compare(*, gamma, owner_packet_bits, rank_one, rank_eight, ledger,
            header_actions, census=None, variant='D_minus_Bstar'):
    """Bound the entire R/W/M difference from certified disjoint intervals.

    Nonchild entries are already signed WHOLE-ROOT differences, including Gamma.
    Added shell entries are whole-root positive bills; removed_B_shells is the
    positive baseline bill subtracted exactly once. Each native body is per call.
    Frozen D is the only implemented candidate admitted by this checker.
    Finite binding control is deliberately absent from the R/W/M currency.
    """
    integer(gamma, 1); integer(owner_packet_bits, 1)
    require(variant in ('D_minus_B', 'D_minus_Bstar'), 'unimplemented candidate adoption')
    counts = census_check(CENSUS if census is None else census)
    require(type(header_actions) is int and header_actions ==
            counts['retained_header_actions'] * gamma, 'retained headers including later calls')
    costs = ledger_check(ledger)
    a, b = complete_body(rank_one), complete_body(rank_eight)
    result = triple((0, 0, 0))
    for name in NONCHILD:
        result = add(result, costs[name])
    result = add(result, costs['producer_added_shells'])
    result = add(result, costs['service_added_shells'])
    result = subtract(result, costs['removed_B_shells'])
    result = add(result, scale(a, (32 + 336) * gamma))
    result = subtract(result, scale(b, 16 * gamma))
    # Source header_write+header_read+clear has slope (6,2,6) per bit;
    # D headers are two bits longer. This preserves the R/W/M distinction.
    header = scale(triple((12, 4, 12)), counts['retained'] * gamma)
    require(summed(header) == exact(header_actions), 'literal header R/W/M sum')
    result = add(result, header)
    # #4167 protocol.adoption_credit with both origin checks charged.
    adoption = scale(triple((5*owner_packet_bits+2, 2*owner_packet_bits,
                             4*owner_packet_bits+2)), 510662*gamma) if variant.endswith('Bstar') else triple((0,0,0))
    result = add(result, adoption)
    action_sum = summed(result)
    verdict = ('strict_action_improvement' if action_sum.hi < 0 else
               'no_strict_action_improvement' if action_sum.lo >= 0 else 'undecided')
    return {'variant': variant, 'RWM_difference': [v.json() for v in result],
            'retained_header_actions': header_actions,
            'credited_Bstar_adoption_actions': summed(adoption).lo,
            'action_difference': action_sum.json(),
            'verdict_from_certified_endpoints_only': verdict,
            'finite_control_difference': 'separate signed charge; not set to zero',
            'negative_control_threshold_for_full_step_exclusion': -action_sum.lo,
            'notes': 'No new evaluator prices are manufactured by this arithmetic checker.'}


def controls():
    """Arithmetic/schema rejection controls, not physical execution evidence."""
    rejected = []
    def fails(label, thunk):
        try:
            thunk()
        except (ValueError, TypeError):
            rejected.append(label)
        else:
            raise ValueError('accepted negative control: ' + label)
    require(Bound(3, 5).minus(Bound(7, 11)) == Bound(-8, -2), 'signed subtraction endpoints')
    require(Bound(3, 5).times(-2) == Bound(-10, -6), 'negative coefficient direction')
    fails('reversed signed bound', lambda: Bound(2, 1))
    fails('upper-minus-upper used as lower', lambda: require(
        Bound(3, 5).minus(Bound(7, 11)).lo == 5 - 11, 'invalid lower'))
    fails('omitted later-root census', lambda: census_check(dict(CENSUS, later=0)))
    fails('boolean multiplicity', lambda: integer(True, 1))
    g = dict(zip(GEOMETRY_FIELDS, (1, 2, 8, 0, 65, 1, 80, 3, 73, 4, 2,
                                  'original-C', '3385', 'warm-erased', 'production-select')))
    for key in GEOMETRY_FIELDS:
        bad = dict(g); bad[key] = str(g[key]) + '_changed'
        fails('false grouping: ' + key, lambda bad=bad: certify_same_geometry(g, bad))
    v = volumes(gamma=51, prefixes=1, unused_rows=2, physical_component_bits=80,
                coefficients=1, address_bits=3)
    bad = dict(v, bank_bits=v['bank_bits'] * 51)
    fails('double Gamma bank volume', lambda: volumes(gamma=51, prefixes=1, unused_rows=2,
          physical_component_bits=80, coefficients=1, address_bits=3, recorded=bad))
    fails('logical width replaces physical width', lambda: volumes(gamma=51, prefixes=1,
          unused_rows=2, physical_component_bits=79, coefficients=1, address_bits=3, recorded=v))
    body = dict(geometry=g, own_actions=[1, 2, 3], descendant_actions=[4, 5, 6],
                total_actions=[5, 7, 9], includes_descendants_once=True, successful_return=True)
    require(summed(complete_body(body)) == exact(21), 'complete synthetic body')
    fails('omitted descendants', lambda: complete_body(dict(body, total_actions=[1, 2, 3])))
    fails('doubled descendants', lambda: complete_body(dict(body, total_actions=[9, 12, 15])))
    fails('uncompleted child', lambda: complete_body(dict(body, successful_return=False)))
    zeros = {k: [0, 0, 0] for k in NONCHILD + SHELLS}
    fails('omitted shell', lambda: ledger_check({k:v for k,v in zeros.items() if k != SHELLS[0]}))
    fails('internal exchange negation charged twice', lambda: ledger_check(dict(zeros, internal_negations=[0,0,0])))
    kwargs = dict(gamma=51, owner_packet_bits=v['owner_packet_bits'], rank_one=body,
                  rank_eight=body, ledger=zeros, header_actions=14298088 * 51)
    fails('unimplemented Dstar adoption', lambda: compare(**kwargs, variant='Dstar_minus_Bstar'))
    base = compare(**kwargs, variant='D_minus_B')
    fair = compare(**kwargs)
    require(fair['action_difference']['lower'] - base['action_difference']['lower'] ==
            510662 * 51 * (11 * v['owner_packet_bits'] + 4), 'adoption credited once')
    return {'scope': 'independent arithmetic/schema controls; synthetic prices are not an admitted geometry',
            'rejections': rejected, 'passed': True}


def root_leaf_domain_witness(columns=5):
    """Exact host certificate for a real RootPlan descriptor domain.

    No giant physical packet is allocated. This follows the named RootPlan
    formulas and certifies a nonempty fast-root, lambda=5 descriptor domain;
    actual source numerical/hosting/stock implementation remains inherited.
    """
    from math import isqrt, prod
    integer(columns, 5)
    require(columns <= 44, 'certified concrete terminal-root family')
    core_width = 73 * columns
    precision = 1 << 8500
    # precision**(997/1000)=2**8474.5 exactly.
    d = isqrt(1 << 16949)
    require(d*d <= (1 << 16949) < (d+1)*(d+1), 'exact root width')
    low, high = 1, 1 << 17
    while low + 1 < high:
        mid = (low + high) // 2
        if pow(mid, 500) <= d:
            low = mid
        else:
            high = mid
    spacing = low
    require(pow(spacing, 500) <= d < pow(spacing+1, 500), 'actual spacing floor')
    guard = 4 * 8500 + 6
    address_guard = d * guard
    gamma = (1 << 1296) * prod((1 << (2*j)) - 1 for j in range(1, 37))
    divisor = 14336 * gamma
    depth, width = 0, d
    while width >= 73:
        width = 48 * (width // 73)
        depth += 1
    q0 = depth * (divisor - 1).bit_length()
    qF = (2 * address_guard + spacing - 1) // spacing
    qB = (address_guard + spacing - 1) // spacing
    threshold = q0 + qF + qB
    selected = threshold + core_width
    require(selected <= d and selected > threshold, 'actual fast-root branch')
    require(d <= core_width**1000, 'post-remainder source nonleaf admission')
    require(8*columns < 73 or pow(8*columns, 1000) < d, 'both unmatched bodies take the actual terminal C branch')
    physical_bits = precision + 2 * ((1 << 210000) * d) + 3
    row_axes = q0 * spacing
    # stock<=2^(q0*K), so padded rows<2^(q0*K+1).
    require(depth * divisor.bit_length() <= row_axes, 'original rows dominate stock')
    front, back = qF * spacing - 2 * address_guard, qB * spacing - address_guard
    require(0 <= front < spacing and 0 <= back < spacing, 'root guards fit')
    address_bits = 3 * address_guard + front + core_width * spacing + back
    require(address_bits == (selected - q0) * spacing, 'complete root rectangle')
    lengths = []
    for rank in (1, 8):
        known = (1, front, address_guard, 0, rank*columns, (73-rank)*columns*spacing,
                 back, spacing, guard, 0, physical_bits, 1, d)
        # The sole huge unmaterialized field is rows=U; its bit length is at
        # most row_axes+1 because U<=padded_rows<2^(row_axes+1).
        lengths.append(16 + address_bits + row_axes + 1 +
                       sum(max(1, x.bit_length()) for x in known))
    descriptor_bound = max(lengths) + (1 << 20)  # parent/shell/header envelope slack
    require(pow(descriptor_bound, 4) <= physical_bits, 'physical width absorbs descriptor fourth power')
    require(columns < 73, 'rank-one child row stock exponent zero')
    def coarse_depth(w):
        answer = 0
        while w >= 73:
            w = 48*(w//73)
            answer += 1
        return answer
    parent_coarse = coarse_depth(core_width)
    rank_eight_coarse = coarse_depth(8*columns)
    require(depth >= parent_coarse and depth-1 >= rank_eight_coarse,
            'inherited root stock supplies both actual child geometries')
    return {'precision': '2^8500', 'root_width': 'floor(sqrt(2^16949))',
            'root_width_bit_length': d.bit_length(), 'spacing': spacing,
            'guard': guard, 'lambda': columns, 'core_width': core_width,
            'selected': 'q0+qF+qB+73*lambda', 'source_depth': depth,
            'row_axis_count': row_axes, 'front_back_less_than_spacing': True,
            'address_bits_bit_length': address_bits.bit_length(),
            'leaf_descriptor_bound_bit_length': descriptor_bound.bit_length(),
            'H_b_ge_leaf_descriptor_bound_fourth_power': True,
            'root_stock_depth': depth, 'rank_one_coarse_stock_depth': 0,
            'parent_coarse_stock_depth': parent_coarse,
            'rank_eight_coarse_stock_depth': rank_eight_coarse,
            'actual_rank_eight_terminal_body_depth': 0,
            'row_stock': '(14336*Gamma)^source_depth',
            'padded_rows': 'ceil(2^(q0*K)/row_stock)*row_stock',
            'component_bits_bit_length': physical_bits.bit_length(),
            'gamma_bit_length': gamma.bit_length(), 'fast_root_and_post_remainder_tests': True,
            'rank_eight_terminal_branch': 'width<73' if 8*columns<73 else 'width^1000<d',
            'packet_executed': False,
            'remaining': 'inherited exact arithmetic, native, chronological hosting and long-record premises'}


def owner_gate_cover_certificate(owner_calls=736, deficits=None):
    """Exact independent arithmetic for the written O(73,2) completion proof.

    This checks the counting inequalities, not a formal-kernel Witt extension.
    The source census must independently justify owner_calls and the deficit
    geometry keys. Uniform inversion of owner matrices is permitted.
    """
    from fractions import Fraction
    integer(owner_calls, 1)
    require(owner_calls == 736, 'literal paid owner basis call census')
    expected = {('add', 6, 8): 4, ('add', 8, 6): 1}
    if deficits is not None:
        require(deficits == expected and all(type(v) is int for v in deficits.values()),
                'literal uncovered gate geometries')
    tail_fraction = Fraction(1)
    for i in range(9):
        choices = 1 << (63-i)
        forbidden = 1 << (i+1)
        require(choices > forbidden, 'tail extension room')
        tail_fraction *= Fraction(choices-forbidden, choices)
    require(tail_fraction > Fraction(1, 2), 'head fibre density')
    require(sum(63-i for i in range(9)) == 531 and
            sum(72-i for i in range(9)) == 612, 'head/tail constraint exponents')
    events = {}
    for size, key in ((6, ('add', 8, 6)), (8, ('add', 6, 8))):
        gl = Fraction(1)
        for j in range(1, size+1):
            gl *= 1-Fraction(1, 1 << j)
        require(gl > Fraction(1, 4), 'invertible leading-block probability')
        event = gl / 4  # two independent prescribed Schur/column bits
        require(event > Fraction(1, 16), 'literal elimination event probability')
        cover = tail_fraction * event
        require(cover > Fraction(1, 32), 'uniform orthogonal cover gate frequency')
        require(Fraction(owner_calls, 32) >= expected[key], 'paid owner gates cover deficit')
        events[str(key)] = {'leading_block_size': size,
                           'cover_frequency_strictly_above': '1/32',
                           'paid_available_per_Gamma_strictly_above': str(Fraction(owner_calls, 32)),
                           'required_per_Gamma': expected[key]}
    return {'all_9_by_9_heads_supported': True,
            'minimum_head_mass_strictly_above': '2^-82',
            'tail_solution_exponent': 531, 'full_frame_upper_exponent': 612,
            'events': events, 'owner_calls_per_Gamma': owner_calls,
            'premises': 'written characteristic-vector/symplectic extension proof; literal paid source census; complete uniform O73 cover',
            'formal_kernel_verification': False}


def normalized_terminal_exclusion(columns=5):
    """Independent signed lower-bound arithmetic on the stated source domain.

    Source premises: actual installed fast-root admission; columns>=5; actual terminal C8 branch;
    physical Hb>=complete leaf/count envelope L^4; v>=2685; the literal
    monomial/base/scalar injection and extra-only gather partition proved in
    NONCHILD.md; original common startup matched, with B extra retirement
    bounded by66496. No E1 upper price is needed in this exclusion: all added
    native bodies are nonnegative and may be dropped from a LOWER bound.
    """
    from math import prod
    from fractions import Fraction
    integer(columns, 5)
    gamma = (1 << 1296) * prod((1 << (2*j)) - 1 for j in range(1, 37))
    require(gamma % 51 == 0, 'complete cover denominator')
    volume_per_gamma_v = Fraction(281593, 816) * 14336 * gamma
    require(volume_per_gamma_v.denominator == 1, 'integer added gather volume')
    volume = int(volume_per_gamma_v)
    scan = 2 * volume
    # Source C upper, removed with the correct sign. It is per R/W/M.
    body_upper_per_v = (1 << 33) * (8*columns+1)
    # Since Hb>=L^4 and v>=2Hb and v>=header_bits, each entire local
    # expression v+1+L^4(+header_bits) is <=4v.
    copies_upper_per_v = 8 * (1 << 22)
    shells_upper_per_v = 16 * (1 << 26)
    removed_per_gamma_v = 16*body_upper_per_v + copies_upper_per_v + shells_upper_per_v
    maximum_columns = (volume + 2*510662 - 16*(1 << 33) -
                       copies_upper_per_v - shells_upper_per_v - 1) // (128*(1 << 33))
    require(columns <= maximum_columns, 'exact positive-slope column threshold')
    # Frozen D receives no additional child-return adoption. B* does.
    slope = (scan + 5*510662 - removed_per_gamma_v,
             volume + 2*510662 - removed_per_gamma_v,
             scan + 4*510662 - removed_per_gamma_v)
    constant_per_gamma = (12*510646 + 2*510662,
                          4*510646,
                          12*510646 + 2*510662)
    # A known total upper66496 also bounds each nonnegative R/W/M component.
    # Subtracting it in every component is safe and deliberately loose.
    startup_per_component = 66496
    require(min(slope) > 0, 'strict normalized R/W/M slopes; no unlimited column extrapolation')
    # v>=2685, Gamma>=1 gives a finite strict sign, including all displayed
    # constants and the conservative triple startup subtraction.
    minimal_total = gamma * (2685 * sum(slope) + sum(constant_per_gamma)) - 3*startup_per_component
    require(minimal_total > 0 and all(gamma*(2685*x+y)-startup_per_component>0
            for x,y in zip(slope,constant_per_gamma)), 'complete componentwise lower bounds including once-only startup')
    return {'variant': 'frozen D minus Bstar', 'columns': columns,
            'maximum_columns_from_action_inequality': maximum_columns,
            'maximum_columns_bit_length': maximum_columns.bit_length(),
            'domain': 'actual fast-root; C8 width<73 or width^1000<d; Hb>=L^4; v>=2685; stated positive slope test; proved gate/base/scalar injection and disjoint interval partition',
            'lower_bound_RWM': {'Gamma_times_v_coefficients': list(slope),
                                'Gamma_constant_coefficients': list(constant_per_gamma),
                                'subtract_once_per_component': startup_per_component},
            'strict_total_action_exclusion': True,
            'minimal_total_lower_bound_bit_length': minimal_total.bit_length(),
            'sum_slope_bit_length': sum(slope).bit_length(),
            'gamma_bit_length': gamma.bit_length(),
            'all_RWM_components_strictly_positive': min(slope) > 0,
            'finite_control': 'signed total control difference must be at least minus the action lower bound for total-step exclusion',
            'source_proof_required': True, 'production_payload_executed': False}


# Compatibility name for integration code written before the height-stop branch
# was included. The result always reports its exact terminal-branch domain.
def normalized_leaf_exclusion(columns=5):
    return normalized_terminal_exclusion(columns)


def check():
    basic = controls()
    witnesses = [root_leaf_domain_witness(i) for i in (5, 9, 10, 44)]
    for i in range(5,45):
        root_leaf_domain_witness(i)
        normalized_terminal_exclusion(i)
    first = normalized_terminal_exclusion(5)
    limit = first['maximum_columns_from_action_inequality']
    normalized_terminal_exclusion(limit)
    rejected = []
    for label, call in (
        ('empty actual fast-root lambda4', lambda: root_leaf_domain_witness(4)),
        ('first uncovered concrete nonterminal lambda45', lambda: root_leaf_domain_witness(45)),
        ('next integer beyond signed column threshold', lambda: normalized_terminal_exclusion(limit+1)),
        ('omitted paid owner bases', lambda: owner_gate_cover_certificate(735)),
        ('wrong uncovered gate geometry', lambda: owner_gate_cover_certificate(deficits={('add',6,7):4,('add',8,6):1})),
    ):
        try: call()
        except ValueError: rejected.append(label)
        else: raise ValueError('accepted domain control: '+label)
    return {'arithmetic_controls': basic, 'root_domain_witnesses': witnesses,
            'all_40_concrete_terminal_geometries_checked': True,
            'owner_cover': owner_gate_cover_certificate(),
            'first_geometry_exclusion': first,
            'exact_action_column_threshold_and_next_integer_checked': True,
            'domain_rejections': rejected,
            'scope': 'independent integer/rational arithmetic and source-bound parameter certificates; no new physical payload replay'}


if __name__ == '__main__':
    import json
    print(json.dumps(check(), sort_keys=True))
