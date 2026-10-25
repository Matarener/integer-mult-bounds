"""Independent structural and conditional cost audit for entrance completion.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
No predecessor executable is imported. The caller authenticates source bytes;
this module independently derives their closure, coefficient and rank invoice.
The consumer hypotheses retain Jose Manuel's observation and Vasek's PR2744
audit, including the credited Ross Richardson forward profile.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import json

BASIS = ('X0', 'X33', 'X101', 'X102', 'X11', 'X12', 'X15', 'X24')
FORWARD = {1: 1216, 2: 74, 3: 86, 4: 104, 5: 48, 6: 42, 7: 68, 8: 8}
KAPPA = Fraction(836330098538459, 500000000000000000)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def native_binding(word, native):
    """Bind every literal occurrence; this is not a Pauli/phase proof."""
    occurrence = {}
    for item in native['transports']:
        for event in item['events']:
            require(event not in occurrence, 'duplicate native event')
            occurrence[event] = item
    frames = {name: list(frame) for name, frame in word['initial_frames'].items()}
    count = 0
    for index, event in enumerate(word['program']):
        op, target = event[:2]
        if op == 'zero':
            require(target not in frames, 'private allocation collision')
            frames[target] = event[2]
        elif op == 'erase':
            require(frames.pop(target) == event[2], 'erase frame')
        elif op == 'transport':
            item = occurrence[index]
            require(type(event[4]) is int and 1 <= event[4] <= 9, 'native rank')
            require(frames[target] == event[2] == item['old'], 'native old frame')
            require(event[3] == item['new'], 'native new frame')
            require(event[4] == item['recipe']['rank'], 'native rank binding')
            frames[target] = event[3]
            count += 1
        elif op == 'add':
            require(frames[target] == frames[event[2]] == event[4], 'ADD common frame')
        elif op == 'sign':
            require(frames[target] == event[3], 'sign frame')
            require(Fraction(event[2]) == -1, 'sign coefficient')
        else:
            raise ValueError('unknown word opcode')
    require(frames == word['final_frames'], 'full final frame bindings')
    require(count == len(occurrence) == 2070, 'native coverage')
    return count


def history_graph(word):
    """State-version provenance uses disjoint bits for events and inputs."""
    program = word['program']
    initial = sorted(word['initial_frames'])
    offset = len(program)
    histories = {name: 1 << (offset+j) for j, name in enumerate(initial)}
    local = {f'Y{x}' for x in range(22, 33)} | {f'Y{x}' for x in range(63, 104)}
    local |= {f'{p}{x}' for p in ('D', 'G') for x in range(27, 32)} | {'Q7'}
    ports, recipients, starts, cleanup = [], set(), {}, {}
    for index, event in enumerate(program):
        op, target = event[:2]
        bit = 1 << index
        if op == 'zero':
            require(target not in histories, 'private history collision')
            histories[target], starts[target] = bit, index
        elif op == 'erase':
            cleanup[starts.pop(target)] = histories.pop(target) | bit
        elif op in ('transport', 'sign'):
            histories[target] |= bit
        elif op == 'add':
            source = event[2]
            histories[target] |= histories[source] | bit
            if index <= 4516 and source in local and target not in local and target != 'C':
                ports.append(histories[target])
                recipients.add(target)
        else:
            raise ValueError('history opcode')
    require(not starts and len(cleanup) == 8, 'private history lifetimes')
    return initial, histories, local, ports, recipients, cleanup


def derive_projection(word):
    initial, histories, local, ports, recipients, cleanup = history_graph(word)
    offset = len(word['program'])
    required = 0
    for history in ports:
        required |= history
    for name in local | recipients:
        required |= histories[name]
    for _ in range(len(initial)+len(cleanup)+1):
        before = required
        dependencies = required >> offset
        for j, name in enumerate(initial):
            if (dependencies >> j) & 1:
                required |= histories[name]
        for first, history in cleanup.items():
            if (required >> first) & 1:
                required |= history
        if before == required:
            break
    else:
        raise ValueError('closure did not stabilize')
    events = [i for i in range(offset) if (required >> i) & 1]
    inputs = [name for j, name in enumerate(initial) if (required >> (offset+j)) & 1]
    omitted = set(initial) - set(inputs)
    for i in events:
        event = word['program'][i]
        require(event[1] not in omitted, 'projection writes omitted bank')
        require(event[0] != 'add' or event[2] not in omitted, 'projection reads omitted bank')
    require(len(events) == 4027 and len(inputs) == 265 and len(ports) == 675, 'closure size')
    return events, inputs, sorted(omitted)


def inventory(program, indices):
    native, operations, coefficients = Counter(), Counter(), Counter()
    unit_adds = half_passes = 0
    for index in indices:
        event = program[index]
        operations[event[0]] += 1
        if event[0] == 'transport':
            native[event[4]] += 1
        elif event[0] == 'add':
            coefficient = Fraction(event[3])
            coefficients[str(coefficient)] += 1
            denominator = coefficient.denominator
            require(denominator in (1, 2, 4), 'scalar denominator')
            unit_adds += abs(coefficient.numerator)
            half_passes += denominator.bit_length()-1
    mass = sum(rank*count for rank, count in native.items())
    return {'operations': dict(sorted(operations.items())),
            'native_profile': dict(sorted(native.items())), 'native_calls': sum(native.values()),
            'native_rank_mass': mass, 'coordinate_C_pairs': 256*mass,
            'weighted_ADD_coefficients': dict(sorted(coefficients.items())),
            'scalar_unit_Gaussian_bank_ADDs': unit_adds,
            'scalar_real_ADDs': 1024*unit_adds,
            'scalar_exact_half_bank_passes': half_passes,
            'scalar_exact_real_halves': 1024*half_passes,
            'scalar_source_restoring_real_doublings': 1024*half_passes}


def factor_invoice(completion):
    A, C = completion['factor']['A'], completion['factor']['C']
    require(len(A) == 8 and len(C) == 52, 'factor dimensions')
    require(all(C[name] == [int(i == j) for j in range(8)]
                for i, name in enumerate(BASIS)), 'C basis block is not identity')
    a = [value for row in A for value in row.values()]
    c = [value for name, row in C.items() if name not in BASIS for value in row if value]
    require(all(type(v) is int and v for v in a+c), 'integer nonzero factor entries')
    active = sorted({name for row in A for name in row})
    require(set(active) == {f'Y{i}' for i in range(104)}-{'Y1'}, 'active Y columns')
    require(len(a) == 385 and len(c) == 201, 'factor nonzero counts')
    units = sum(map(abs, a)) + 2*sum(map(abs, c))
    require(units == 887, 'strict factor ADD invoice')
    return {'basis': list(BASIS), 'basis_identity_checked': True,
            'A_nonzeros': len(a), 'A_l1': sum(map(abs, a)),
            'C_nonbasis_nonzeros': len(c), 'C_nonbasis_l1': sum(map(abs, c)),
            'weighted_ADDs': len(a)+2*len(c), 'unit_Gaussian_bank_ADDs': units,
            'real_ADDs': 1024*units, 'temporarily_halved_restored_Y_banks': len(active),
            'inactive_Y': ['Y1'], 'exact_real_halves': 1024*len(active),
            'exact_real_doublings': 1024*len(active),
            'native_profile': {1: 52, 9: 93}, 'native_calls': 145, 'native_rank_mass': 889,
            'new_private_Gaussian_banks': 0,
            'schedule': 'Xnonbasis-=C_N*Xbasis; Xbasis+=A*Y/2 by source columns; Xnonbasis+=C_N*Xbasis'}


def fractional_sources(program, indices):
    found = {'N': set(), 'Y': set()}
    counts = Counter()
    for i in indices:
        event = program[i]
        if event[0] != 'add' or Fraction(event[3]).denominator == 1:
            continue
        family = event[2][0]
        require(family in found, 'unexpected fractional source family')
        require(Fraction(event[3]).denominator == {'N': 2, 'Y': 4}[family], 'fractional source denominator')
        found[family].add(event[2])
        counts[family] += 1
    return found, dict(counts)


def source_row_audit(word, indices, weights):
    """Only N/Y source rows are needed; all Y writes are native transports."""
    rows = {name: {name: Fraction(1)} for name in word['initial_frames'] if name.startswith(('N', 'Y'))}
    first_n, checked, row_digests = {}, 0, []
    for index in indices:
        event = word['program'][index]
        op, target = event[:2]
        if target.startswith('Y'):
            require(op == 'transport', 'Y numeric mutation in projection')
        if op != 'add':
            continue
        source, coefficient = event[2], Fraction(event[3])
        if coefficient.denominator != 1:
            require(source in rows, 'fractional source row absent')
            for name, value in rows[source].items():
                require((coefficient*value*weights[name]).denominator == 1,
                        f'unadmitted source increment at event {index} from {name}')
            checked += 1
            row_digests.append([index, {name: str(value) for name, value in rows[source].items()}])
            if source.startswith('N') and source not in first_n:
                require(rows[source] == {source: 1} and event[4] == [], 'first N half boundary')
                first_n[source] = index
        if target.startswith('N'):
            require(source in rows, 'N row update alphabet')
            updated = dict(rows[target])
            for name, value in rows[source].items():
                updated[name] = updated.get(name, 0)+coefficient*value
            rows[target] = {name: value for name, value in updated.items() if value}
    require(all(row == {name: 1} for name, row in rows.items()), 'N/Y source endpoint restoration')
    return {'fractional_increments_checked': checked, 'fractional_source_rows_sha256': digest(row_digests),
            'first_N_half_events': first_n,
            'N_and_Y_normalized_endpoints_restore': all(row == {name: 1} for name, row in rows.items())}


def expected_rejection(function):
    try:
        function()
    except ValueError as error:
        return str(error)
    raise ValueError('required rejection was accepted')


def domain_audit(word, selected):
    program = word['program']
    full_ids = list(range(len(program)))
    full, full_counts = fractional_sources(program, full_ids)
    part, part_counts = fractional_sources(program, selected)
    require(len(full['N']) == 78 and len(part['N']) == 38, 'N domain inventory')
    require(full['Y'] == part['Y'] == {f'Y{i}' for i in range(104)}, 'Y domain inventory')
    require(all(frame == [] for name, frame in word['initial_frames'].items() if name.startswith('Y')), 'Y entrance chart')
    def scales(n_sources):
        return {name: (4 if name.startswith('Y') else 2 if name in n_sources else 1)
                for name in word['initial_frames']}
    full_result = source_row_audit(word, full_ids, scales(full['N']))
    part_weights = scales(full['N'])
    part_result = source_row_audit(word, selected, part_weights)
    weak_n = dict(part_weights)
    weak_n['N100'] = 1
    weak_y = dict(part_weights)
    weak_y['Y1'] = 2
    return {'scope': 'Common sufficient B9-product entrance under inherited native/B9 covariance; no minimal-domain claim and all initial preparations remain unpaid',
            'common_original_and_new_caller': {'Y_4B9': 104, 'N_2B9': sorted(full['N']), 'other_B9': 176},
            'projection_fractional_N_sources': sorted(part['N']),
            'full_fractional_reads': full_counts, 'projection_fractional_reads': part_counts,
            'full_source_rows': full_result, 'projection_source_rows': part_result,
            'weak_N100_control': expected_rejection(lambda: source_row_audit(word, selected, weak_n)),
            'weak_Y1_control': expected_rejection(lambda: source_row_audit(word, selected, weak_y)),
            'qualification': 'Both original and changed callers are interpreted on the same strong product domain. The 38 projection N-source count is a read inventory, not a new minimal-domain theorem. Endpoint equality is proved separately.'}


def profile_comparison(old, new):
    old = {int(k): v for k, v in old.items()}
    new = {int(k): v for k, v in new.items()}
    count = sum(old.values())
    mass = sum(rank*n for rank, n in old.items())
    require(all(type(r) is int and 1 <= r <= 9 and type(n) is int and n >= 0
                for r, n in old.items()), 'chord rank/count domain')
    require(sum(r*n for r, n in new.items()) == mass, 'comparison rank mass changed')
    require(count == 473 and mass == 889 and new == {1: 52, 9: 93}, 'comparison profile')
    old_sorted = sorted((r for r, n in old.items() for _ in range(n)), reverse=True)
    new_sorted = sorted((r for r, n in new.items() for _ in range(n)), reverse=True)
    new_sorted += [0]*(len(old_sorted)-len(new_sorted))
    prefix, differences = 0, []
    for old_rank, new_rank in zip(old_sorted, new_sorted):
        prefix += new_rank-old_rank
        require(prefix >= 0, 'majorization prefix fails')
        differences.append(prefix)
    require(prefix == 0, 'majorization total fails')
    chord_one, chord_nine = Fraction(9*count-mass, 8), Fraction(mass-count, 8)
    require((chord_one, chord_nine) == (421, 52), 'chord weights')
    return {'equal_mass': mass, 'old_calls': count, 'new_calls': sum(new.values()),
            'majorization_prefixes_checked': len(differences),
            'prefix_difference_sha256': digest(differences),
            'old_tariff_lower_bound': '421 + 52*9^s',
            'new_tariff': '52 + 93*9^s',
            'old_minus_new_lower_bound': '41*(9-9^s)',
            'scope': 'Strict improvement for 0<=s<1; equality at s=1; native-only profile tariff, with monomials and all physical/outer charges separate',
            'positive_sqrt_chord_control': {'s': '1/2', 'old_lower': 577, 'new_exact': 331, 'certified_gain_at_least': 246}}


def exp_upper(value, terms):
    require(value >= 0 and value < terms+2, 'exponential tail ratio')
    term = total = Fraction(1)
    for k in range(1, terms+1):
        term = term*value/k
        total += term
    next_term = term*value/(terms+1)
    return total+next_term/(1-value/Fraction(terms+2))


def consumer_stop(new_profile):
    new = {int(k): v for k, v in new_profile.items()}
    require(sum(r*n for r, n in FORWARD.items()) == 3070, 'forward mass')
    require(sum(r*n for r, n in new.items()) == 3542 and max(new) == 9, 'new dual mass/rank')
    profile = {r: 5*FORWARD.get(r, 0)+4*new.get(r, 0) for r in set(FORWARD)|set(new)}
    profile[1] -= 4*416
    mass = sum(r*n for r, n in profile.items())
    require(profile[1] == 9680 and mass == 27854, 'forgiven profile')
    m, families, persistent = 73, 832, 3014
    remainder = 72*families-9*persistent
    require(remainder == 32778, 'coverage remainder')
    slope = 4*profile[1]+2*(mass-profile[1])
    require(slope == 75068, 'new-profile slope')
    e4, e2 = exp_upper(Fraction(4), 16), exp_upper(Fraction(2), 12)
    require(e4 < 73 and e2 < Fraction(73, 9), 'rational logarithm bounds')
    excess = slope*KAPPA-104
    require(excess > 0, 'selected target not excluded')
    return {'scope': 'Conditional new fixed-profile substitution under the retained PR2744 five-forward/four-dual coverage assumptions; not a universal P104 barrier',
            'm': m, 'W': families, 'forward_calls': 5, 'dual_calls': 4,
            'persistent_credit_per_call': persistent, 'remaining_coverage_mass': remainder,
            'rank_forgiveness_per_dual': 416, 'forgiven_profile': dict(sorted(profile.items())),
            'forgiven_rank_mass': mass, 'linear_lower_slope': slope,
            'kappa': str(KAPPA), 'slope_times_kappa_minus_104': str(excess),
            'no_bank_selected_lower_bound': str(1+excess/(m*families)),
            'fully_paid_B_lower_bound': '1 + (75068*a-104)/(73*(832+B))',
            'auxiliary_bank_scope': 'every finite B>=0; fixed m, fully paid 73 units per added bank',
            'unforgiven_zero_saving_bound': str(Fraction(5*3070+4*3542+remainder, m*families)),
            'forgiven_zero_saving_bound': str(Fraction(mass+remainder, m*families)),
            'exp4_rational_upper': str(e4), 'exp2_rational_upper': str(e2),
            'remaining_hypotheses': ['unchanged forward profile', 'new dual decomposition fixed apart from allowed rank deletion',
                'all other positive children rank<=73', 'coverage law and endpoint credit unchanged',
                'all other charges nonnegative; source admission and ownership not supplied']}


def analyze(word, native, completion, adapters, selected_events):
    """Return JSON-compatible exact evidence without mutating inputs."""
    require(len(word['program']) == 5398 and len(word['initial_frames']) == 358, 'word size')
    native_count = native_binding(word, native)
    selected, inputs, omitted_banks = derive_projection(word)
    require(list(selected_events) == selected, 'external selected-event list differs')
    require(digest(selected) == adapters['projection_event_sha256'] == completion['closure']['events_sha256'], 'projection digest')
    selected_set = set(selected)
    removed = [i for i in range(len(word['program'])) if i not in selected_set]
    full = inventory(word['program'], range(len(word['program'])))
    projection = inventory(word['program'], selected)
    omitted = inventory(word['program'], removed)
    require({str(r): n for r, n in omitted['native_profile'].items()} == adapters['omitted_original_transport_profile'], 'old omitted profile')
    factor = factor_invoice(completion)
    require(set(completion['factor']['C']) == {name for name in omitted_banks if name.startswith('X')}, 'omitted X target binding')
    require(all(len(word['initial_frames'][name]) == (1 if name.startswith('X') else 0)
                and word['final_frames'][name] == [256,128,64,32,16,8,4,2,1] for name in omitted_banks), 'omitted adapter frames')
    new = Counter(projection['native_profile'])+Counter(factor['native_profile'])
    require(sum(new.values()) == 1742 and sum(r*n for r, n in new.items()) == 3542, 'new full profile')
    comparison = profile_comparison(omitted['native_profile'], factor['native_profile'])
    bad_profile = {1: 52, 8: 1, 9: 92}
    undercharge = expected_rejection(lambda: profile_comparison(omitted['native_profile'], bad_profile))
    scalar_adds = projection['scalar_real_ADDs']+factor['real_ADDs']
    scalar_halves = projection['scalar_exact_real_halves']+factor['exact_real_halves']
    return {'schema_version': 1, 'status': 'PASS', 'native_occurrences_bound': native_count,
            'closure': {'events': len(selected), 'inputs': len(inputs), 'omitted_banks': len(omitted_banks),
                'event_sha256': digest(selected), 'projection_reads_or_writes_omitted': False},
            'original_full': full, 'projection': projection, 'removed_program': omitted,
            'entrance_completion': factor,
            'changed_full': {'native_profile': dict(sorted(new.items())), 'native_calls': sum(new.values()),
                'native_rank_mass': sum(r*n for r, n in new.items()), 'coordinate_C_pairs': 256*3542,
                'scalar_real_ADDs': scalar_adds, 'scalar_exact_real_halves': scalar_halves,
                'scalar_real_doublings': scalar_halves, 'original_private_C_lifetimes': 8, 'new_private_C_lifetimes': 0,
                'scalar_real_ADD_change': scalar_adds-full['scalar_real_ADDs'],
                'scalar_exact_half_and_double_change_each': scalar_halves-full['scalar_exact_real_halves']},
            'source_domain': domain_audit(word, selected), 'native_concavity_gain': comparison,
            'undercharged_profile_control': undercharge, 'conditional_consumer_stop': consumer_stop(new),
            'scalar_invoice_contract': 'Integer weighted ADDs repeat unit Gaussian ADDs. Each original fractional ADD temporarily divides its mutable source, performs its signed unit ADD, and restores the source by doubling before the next original event. The source-row audit proves exact divisibility at those reads. No new Gaussian workspace is used by the entrance completion.',
            'not_priced': ['actual source preparation', 'monomial swaps and phases', 'native-pair temporary implementation',
                'global ownership and routing', 'caller heights and widths', 'idle packing realization',
                'recursive/all-size transfer', 'actual physical-machine runtime'],
            'evidence_limits': 'Exact symbolic structure, coefficient and rational tariff checks; no native matrix/rounded replay or full-word endpoint proof is performed by this module.'}
