"""Independent rounded-operation envelopes and a concrete reassociation witness.

Input words and construction metadata must be authenticated by the caller.
This module imports no predecessor executable.  Fractions are exact.
"""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def plus(a, b):
    c = dict(a)
    for k, v in b.items():
        c[k] = c.get(k, Q(0)) + v
    return {k: v for k, v in c.items() if v}


def scale(a, c):
    return {k: v * c for k, v in a.items() if v * c}


def native(a):
    # x=2**lambda bounds a rank-one tensor Gaussian line in component infinity norm.
    return {(kind, degree + 1): v for (kind, degree), v in a.items()}


def encode(a):
    return [[kind, degree, str(v)] for (kind, degree), v in sorted(a.items())]


def envelope(word, with_peak=False):
    """Error <= E(x)*epsilon+A(x)*eta+H(x)*nu, x=2**lambda.

    epsilon bounds each borrowed input component error, eta each COMPLETE scalar
    ADD implementation residual relative to ideal dst+c*src, including product,
    division, addition and storage errors together, and nu each COMPLETE signed-
    native operation output residual. CLEAR, cover and signed monomials are exact.
    The reference coefficient is exact; no implementation scaling exactness is
    assumed. A one-rounding eta requires a separate implementation proof.
    The model is explicitly not a certificate for a concrete floating format.
    """
    values = {f'{s}{p}': {('entry', 0): Q(1)} for s in 'XY' for p in range(112)}
    values.update({f'{s}{p}': {} for s in 'ZW' for p in range(112)})
    active = set()
    peak = {}
    for i, e in enumerate(word):
        op = e[0]
        if op == 'clear':
            values[e[1]] = {}
        elif op == 'add':
            need(e[1] in values and e[2] in values, f'unknown ADD field at {i}')
            c = abs(Q(e[3]))
            need(c in (Q(1), Q(1, 4)), 'scalar alphabet')
            values[e[1]] = plus(plus(values[e[1]], scale(values[e[2]], c)), {('scalar', 0): Q(1)})
        elif op == 'line':
            need(e[1] in values and e[3] in (-1, 1), 'signed native alphabet')
            values[e[1]] = plus(native(values[e[1]]), {('native', 0): Q(1)})
        elif op == 'map':
            need(e[1] in values, 'map field')
        elif op == 'begin':
            need(not active, 'nested private scope')
            need(e[2] in (8, 16), 'private size')
            active = {f'F{k}' for k in range(8)}
            if e[2] == 16:
                active |= {f'G{k}' for k in range(8)}
            for key in active:
                values[key] = {('entry', 0): Q(1)}
        elif op == 'end':
            need(active, 'unopened private scope')
            for key in active:
                del values[key]
            active = set()
        elif op == 'checkpoint':
            pass
        else:
            raise ValueError(f'unknown opcode {op}')
        if op in ('clear', 'add', 'line'):
            for key, value in values[e[1]].items():
                peak[key] = max(peak.get(key, Q(0)), value)
    need(not active, 'private scope left live')
    outputs = {key: values[key] for key in values if key[0] in 'ZW'}
    return (outputs, peak) if with_peak else outputs


def round_binary(value, bits=2):
    """Unbounded-exponent binary rounding to nearest, ties to even."""
    value = Q(value)
    need(bits >= 2, 'significand width')
    if not value:
        return value
    sign = 1 if value > 0 else -1
    a = abs(value)
    exponent = a.numerator.bit_length() - a.denominator.bit_length()
    if a < Q(2) ** exponent:
        exponent -= 1
    quantum = Q(2) ** (exponent - bits + 1)
    scaled = a / quantum
    lo, rem = divmod(scaled.numerator, scaled.denominator)
    if 2 * rem > scaled.denominator or (2 * rem == scaled.denominator and lo % 2):
        lo += 1
    return sign * lo * quantum


def query_at_cut(word, construction, normalized, bits=2):
    """Execute actual frozen query scalar events, supplying exact normalized W.

    This deliberately isolates query arithmetic; it is not a full floating
    decoder execution.  Native/map normalization is an exact supplied premise.
    """
    aliases = construction['hosting']['aliases']
    query = {aliases[f'Q{k}']: Q(0) for k in range(8)}
    state = dict(query)
    query_names = set(query)
    start = next(i for i,e in enumerate(word) if e == ['clear', aliases['Q0'], 'query2'])
    response = next(i for i in range(start + 8, len(word))
                    if word[i] == ['clear', aliases['D'], 'query2'])
    observed_ports = []
    for i, e in enumerate(word[start:response], start):
        if e[0] == 'clear':
            state[e[1]] = Q(0)
        elif e[0] == 'line':
            need(e[3] == -1, 'normalizing negative line')
            state[e[1]] = Q(normalized.get(e[2], 0))
            observed_ports.append(e[2])
        elif e[0] == 'map':
            pass
        elif e[0] == 'add':
            if e[2].startswith('W'):
                state[e[1]] = Q(0)  # Replaced at the paid normalizer output.
            else:
                need(e[1] in state and e[2] in state, 'query scalar field')
                exact = state[e[1]] + Q(e[3]) * state[e[2]]
                state[e[1]] = exact if bits is None else round_binary(exact, bits)
        else:
            raise ValueError('unexpected query opcode')
    need(len(observed_ports) == len(set(observed_ports)) == 104, 'complete query normalization')
    return {'queries': [str(state[aliases[f'Q{k}']]) for k in range(8)],
            'start': start, 'response_start': response, 'normalized_ports': observed_ports}


def audit(baseline, candidate, construction):
    (eb, pb), (ec, pc) = envelope(baseline, True), envelope(candidate, True)
    need(eb == ec, 'endpoint envelope changed')
    need(pb == pc, 'whole-word logical-cut error envelope changed')
    pairs = construction['factoring']['pairs']
    multiplicity = [0] * 8
    for row in pairs:
        for k in row['same']:
            multiplicity[k] += 2  # shared sum residual plus channel deposit
        for k in row['different']:
            multiplicity[k] += 2
    need(multiplicity == [52] * 8, 'uniform query rounding envelope')
    supplied = {76: Q(4), 87: Q(1), 92: Q(1)}
    wb = query_at_cut(baseline, construction, supplied)
    wc = query_at_cut(candidate, construction, supplied)
    need(wb['queries'][0] == '4' and wc['queries'][0] == '6', 'rounded query reassociation witness')
    # Integer additions model a common fixed-point lattice without overflow.
    integer_checks = 0
    ports = sorted(wb['normalized_ports'])
    patterns = [{p: Q(1)} for p in ports]
    patterns += [{p: Q(((-1)**j) * (2**80 + j)) for j,p in enumerate(ports)},
                 {p: Q((j*j*17)%131 - 65) for j,p in enumerate(ports)}]
    for values in patterns:
        ib = query_at_cut(baseline, construction, values, None)['queries']
        ic = query_at_cut(candidate, construction, values, None)['queries']
        need(ib == ic, 'exact integer query identity')
        integer_checks += 1
    classes = {}
    for key, value in sorted(ec.items()):
        token = tuple(sorted(value.items()))
        classes.setdefault(token, []).append(key)
    return {
        'status': 'PASS_CONDITIONAL_ROUNDING_ENVELOPE_AND_CHANGED_DAG_WITNESS',
        'model': {'x': '2^lambda', 'entry': 'epsilon per borrowed input real/imaginary component',
                  'scalar': 'eta absolute residual of complete scalar ADD versus ideal dst+c*src, including product/division, addition and storage errors; ideal coefficient exact',
                  'native': 'nu per complete signed tensor-native output component',
                  'exact': ['CLEAR', 'cover permutations', 'signed monomial permutations'],
                  'restriction': 'No relation between eta/nu and a machine significand, nor an overflow guarantee, is inferred.'},
        'all_224_endpoint_envelopes_equal': True,
        'endpoint_envelope_classes': [{'fields': fields, 'polynomial': encode(dict(token))}
                                      for token, fields in classes.items()],
        'whole_word_logical_cut_coefficient_envelope_equal': True,
        'whole_word_logical_cut_coefficient_envelope': encode(pc),
        'peak_scope': 'Logical cuts only; internal approximate native arithmetic is supplied by the native contract, not inferred.',
        'query_accumulation_scalar_error_multiplicities': multiplicity,
        'correlation': 'Each shared pair residual is reused in all equal-sign channels; no independence or root-sum-square assumption.',
        'rounded_query_witness': {'bits': 2, 'rounding': 'nearest, ties to even, unbounded exponent',
                                  'normalized_component_values': {str(k): str(v) for k,v in supplied.items()},
                                  'all_other_normalized_components_at_observed_coordinate': '0',
                                  'baseline': wb, 'candidate': wc,
                                  'scope': 'Actual query scalar subsequences with exact supplied normalization outputs; not a full rounded-caller counterexample.'},
        'floating_no_automatic_bitwise_transfer': True,
        'fixed_point_query_regression_cases': integer_checks,
        'fixed_point_condition': 'Exact nonoverflowing integer unitADDs imply same queries for arbitrary supplied normalization outputs on a common lattice; deterministic isolated normalizers and unchanged response/suffix then imply relative bitidentity, including any common preexisting defects.',
        'restoration_boundary': 'Rounded envelope alone does not certify zero private-scratch restoration; exact-grid theorem or a native/private cleanup contract is needed.',
    }
