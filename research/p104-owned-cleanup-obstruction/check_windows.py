"""Exact fixed-contact common-chart obstruction for PR5569's owned-holder gap.

Standard library only. The entire source word is reconstructed with arbitrary
public inputs; neither a solver nor numerical parameter sampling is used.
"""
from bisect import bisect_right
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json

SOURCE_SHA256 = '12224e9a13a49c830b304338a8d31610fb43da15d1a650537733c27f7864310f'
CONTROL_SHA256 = 'b3701d78bee3661382ebe5414e678dfc9ee292e254cb9dc56339c2d2f45fdf44'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def decode(raw, expected):
    need(sha256(raw).hexdigest() == expected, 'authenticated source bytes')
    return json.loads(gzip.decompress(raw))


def binary_span(basis):
    result = {0}
    for value in basis:
        result |= {entry ^ value for entry in result}
    need(len(result) == 1 << len(basis), 'independent binary frame basis')
    return frozenset(result)


def operands(event):
    return (event[1],) if event[0] in ('INIT', 'CLEAR', 'MOVE', 'SCALE') else (event[1], event[2])


def public_window(chain, spans):
    need(chain and None not in chain, 'active public window')
    need(all(spans[a] < spans[b] for a, b in zip(chain, chain[1:])),
         'public transport direction')


def chronology(word):
    """Frames between adjacent scalar contacts, with exact contact indices."""
    public = word['public']
    count = public + 8
    indices = [[] for _ in range(count)]
    windows = [[] for _ in range(count)]
    chains = [[f] for f in word['initial']] + [[None] for _ in range(8)]
    for index, event in enumerate(word['program']):
        if event[0] == 'MOVE':
            need(chains[event[1]][-1] == event[2], 'window MOVE source')
            chains[event[1]].append(event[3])
            continue
        for role in operands(event):
            indices[role].append(index)
            windows[role].append(chains[role])
            chains[role] = [None if event[0] == 'CLEAR' else event[-1]]
    for role in range(count):
        windows[role].append(chains[role])
    spans = list(map(binary_span, word['frames']))
    for role in range(public):
        need(chains[role][-1] == word['final'][role], 'public final frame')
        for chain in windows[role]:
            public_window(chain, spans)
    return indices, windows, spans


def window(indices, windows, role, boundary):
    return windows[role][bisect_right(indices[role], boundary)]


def obstruction(public_bounds, frames, spans):
    """A pair A_left not subset B_right prevents every common chart F."""
    for left, low, _ in public_bounds:
        for right, _, high in public_bounds:
            for vector in frames[low]:
                if vector not in spans[high]:
                    return [left, right, low, high, vector]
    return None


def check_witness(witness, public_bounds, spans):
    left, right, low, high, vector = witness
    bound = {role: (a, b) for role, a, b in public_bounds}
    need(left in bound and right in bound, 'witness roles are required public holders')
    need(bound[left][0] == low and bound[right][1] == high, 'witness binds scalar windows')
    need(vector in spans[low] and vector not in spans[high], 'separating binary vector')


def apply(event, rows, current, active, spans, public):
    op, role = event[:2]
    if op == 'MOVE':
        _, role, left, right, private = event
        need(current[role] == left and (role in active) == private, 'MOVE chronology and ownership')
        need(spans[right] < spans[left] if private else spans[left] < spans[right], 'MOVE nesting')
        current[role] = right
    elif op == 'INIT':
        need(role >= public and role not in active, 'fresh owned lifetime')
        rows[role] = {}
        current[role] = event[2]
        active.add(role)
    elif op == 'CLEAR':
        need(role in active and current[role] == event[2], 'owned erasure boundary')
        rows[role] = {}
        current[role] = None
        active.remove(role)
    else:
        factor, frame = Q(event[-2]), event[-1]
        need(factor and current[role] == frame, 'scalar destination')
        if op == 'SCALE':
            rows[role] = {symbol: factor * value for symbol, value in rows[role].items()}
        else:
            source = event[2]
            need(source != role and current[source] == frame, 'common source chart')
            if op == 'COPY':
                need(role in active and not rows[role], 'COPY into empty owned field')
                rows[role] = {symbol: factor * value for symbol, value in rows[source].items()}
            else:
                need(op == 'ADD', 'known scalar opcode')
                target = dict(rows[role])
                for symbol, value in rows[source].items():
                    coefficient = target.get(symbol, Q(0)) + factor * value
                    if coefficient:
                        target[symbol] = coefficient
                    else:
                        target.pop(symbol, None)
                rows[role] = target


def analyze(word):
    public = word['public']
    need(public == 735 and len(word['program']) == 25140, 'source dimensions')
    indices, windows, spans = chronology(word)
    mains = set(word['live']) | {r + 112 for r in word['live']}
    rows = [{r: Q(1)} for r in range(public + 8)]
    current = list(word['initial']) + [None] * 8
    active = set()
    complete_states, public_states = set(), set()
    witnesses, examples = [], []
    by_owned, peak = Counter(), 0
    for boundary, event in enumerate(word['program']):
        apply(event, rows, current, active, spans, public)
        peak = max(peak, len(active))
        # This is deliberately every event boundary, including MOVE boundaries,
        # without the predecessor's touched-symbol or first/last-use filters.
        helpers = {h for owned in active for h in rows[owned] if h < public and h not in mains}
        for helper in sorted(helpers):
            holders = [r for r, row in enumerate(rows) if helper in row]
            required = sorted(set(holders) | {helper})
            all_bounds = [(r, window(indices, windows, r, boundary)[0],
                           window(indices, windows, r, boundary)[-1]) for r in required]
            bounds = [(r, left, right) for r, left, right in all_bounds if r < public]
            witness = obstruction(bounds, word['frames'], spans)
            need(witness is not None, 'public-only obstruction at every owned-holder state')
            check_witness(witness, bounds, spans)
            complete_states.add((helper, tuple(all_bounds)))
            public_states.add((helper, tuple(bounds)))
            owned_holders = [r for r in holders if r >= public]
            by_owned[','.join(map(str, owned_holders))] += 1
            witnesses.append([boundary, helper, witness])
            if len(examples) < 8:
                examples.append({'boundary': boundary, 'helper': helper,
                                 'public_bounds': [list(bound) for bound in bounds], 'witness': witness})
    need(not active and peak == 1 and current[:public] == word['final'], 'complete source boundaries')
    for role, row in enumerate(rows):
        target = {role: Q(1)} if role < public else {}
        if role - 112 in word['live']:
            target[role - 112] = Q(1)
        need(row == target, 'full arbitrary-input source transfer')
    return {
        'status': 'PASS_PUBLIC_WINDOW_OBSTRUCTION',
        'event_boundaries_with_helper_owned_pairs': len(witnesses),
        'distinct_full_holder_geometries': len(complete_states),
        'distinct_public_holder_geometries': len(public_states),
        'owned_holder_pairs_by_register': dict(sorted(by_owned.items())),
        'all_source_endpoint_rows': len(rows),
        'public_only_witnesses': True,
        'witnesses_sha256': sha256(canonical(witnesses)).hexdigest(),
        'witness_examples': examples,
        'source_role_173': 'productive helper; port61 is not live',
        'new_bound': False,
    }, witnesses


def positive_control(word):
    indices, windows, spans = chronology(word)
    public = word['public']
    rows = [{r: Q(1)} for r in range(public + 8)]
    current = list(word['initial']) + [None] * 8
    active = set()
    for event in word['program'][:15444]:
        apply(event, rows, current, active, spans, public)
    need(rows[706] == {706: Q(1), **{k: value / 2 for k, value in rows[173].items()}},
         'positive control cleanup identity')
    bounds = [(r, window(indices, windows, r, 15443)[0],
               window(indices, windows, r, 15443)[-1]) for r in (706, 173)]
    need(all(spans[left] <= spans[559] <= spans[right] for _, left, right in bounds),
         'published positive control has a common chart')
    need(obstruction(bounds, word['frames'], spans) is None, 'positive control not falsely rejected')
    need(len(word['frames'][word['initial'][706]]) < 8 < len(word['frames'][word['final'][706]]),
         'positive control is a strict interior helper split')
    return {'source': 'PR5561 headline word', 'boundary': 15443, 'helper': 706,
            'partner': 173, 'common_frame': 559, 'common_dimension': 8}


def rejection(action):
    try:
        action()
    except ValueError:
        return True
    return False


def run(source_raw, control_raw):
    word = decode(source_raw, SOURCE_SHA256)
    control = decode(control_raw, CONTROL_SHA256)
    result, witnesses = analyze(word)
    result['positive_control'] = positive_control(control)
    spans = list(map(binary_span, word['frames']))
    example = result['witness_examples'][0]
    bad_vector = example['witness'][:-1] + [0]
    missing_role = example['witness'][:]
    missing_role[0] = word['public']
    _, windows, _ = chronology(word)
    chain = next(ch for role in windows[:word['public']] for ch in role if len(ch) > 1)
    controls = {
        'changed_source_bytes': rejection(lambda: decode(source_raw + b' ', SOURCE_SHA256)),
        'zero_separating_vector': rejection(lambda: check_witness(bad_vector, example['public_bounds'], spans)),
        'owned_role_used_as_public_witness': rejection(lambda: check_witness(missing_role, example['public_bounds'], spans)),
        'reversed_public_window': rejection(lambda: public_window(list(reversed(chain)), spans)),
    }
    need(all(controls.values()), 'all semantic corruption controls rejected')
    result['corruption_controls'] = controls
    return result, witnesses
