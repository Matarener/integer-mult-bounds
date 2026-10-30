"""Independent marker audit through a joined, layered constraint graph.

Hiroki KUMAZAKI, with substantial OpenAI Codex assistance. Apache-2.0.

run(source) reads the authenticated predecessor package supplied by the caller.
It imports neither the proposer nor either predecessor dynamic program. Local
relations are built by joining G_j(input)=G_i(output), using literal G_rows.
Arc consistency retains precisely the source-to-terminal paths of this chain;
an exact DAG count and explicit surviving owner sequence complete the check.
The finite-state invariant is shared mathematics, not independent human review.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def row_image(rows, value):
    return sum(((row & value).bit_count() % 2) << bit
               for bit, row in enumerate(rows))


def load_tables(ports):
    need(len(ports) == 112, "all 112 source normalizers")
    forward, inverse = [], []
    for owner, port in enumerate(ports):
        rows = port['G_rows']
        need(port['port'] == owner and len(rows) == 9
             and all(type(row) is int and 0 <= row < 512 for row in rows),
             "literal nine-axis source rows")
        table = tuple(row_image(rows, x) for x in range(512))
        need(len(set(table)) == 512, "each literal source map is invertible")
        back = [0]*512
        for x, y in enumerate(table):
            back[y] = x
        forward.append(table)
        inverse.append(tuple(back))
    return forward, inverse


def chain_images(forward, inverse, owners, inputs):
    values = list(inputs)
    for stage, (left, right) in enumerate(zip(owners, owners[1:])):
        shift = 1+8*stage
        for position, value in enumerate(values):
            local = (value & 1) | (((value >> shift) & 255) << 1)
            image = inverse[right][forward[left][local]]
            values[position] = ((value & ~(1 | (255 << shift)))
                                | (image & 1) | ((image >> 1) << shift))
    return values


def central_mask(values):
    return sum((value & 1) << i for i, value in enumerate(values))


def joined_layers(forward, allowed, count, inputs, outputs):
    """Build complete relations, including unreachable states, by signature join."""
    multiplicity = 1 << len(inputs)
    layers = []
    for stage in range(count):
        shift = 1+8*stage
        source_private = [(x >> shift) & 255 for x in inputs]
        target_private = [(x >> shift) & 255 for x in outputs]
        target_signatures = defaultdict(list)
        for owner, table in enumerate(forward):
            for mask in range(multiplicity):
                signature = tuple(table[(value << 1) | ((mask >> i) & 1)]
                                  for i, value in enumerate(target_private))
                target_signatures[signature].append(owner*multiplicity+mask)
        edges = []
        for owner, table in enumerate(forward):
            for mask in range(multiplicity):
                signature = tuple(table[(value << 1) | ((mask >> i) & 1)]
                                  for i, value in enumerate(source_private))
                for target in target_signatures.get(signature, ()):
                    if allowed[target//multiplicity][owner]:
                        edges.append((owner*multiplicity+mask, target))
        layers.append(tuple(edges))
    return layers


def inspect_graph(layers, start, finish, multiplicity, total_owners=112):
    """Count paths in the complete graph after chain-constraint propagation."""
    count = len(layers)
    universe = set(range(total_owners*multiplicity))
    domains = [{start}]+[set(universe) for _ in range(count-1)]+[{finish}]
    changed, rounds = True, 0
    while changed:
        changed = False
        rounds += 1
        for stage, edges in enumerate(layers):
            surviving = [(left, right) for left, right in edges
                         if left in domains[stage] and right in domains[stage+1]]
            source_domain = {left for left, _ in surviving}
            target_domain = {right for _, right in surviving}
            if domains[stage] != source_domain or domains[stage+1] != target_domain:
                changed = True
                domains[stage], domains[stage+1] = source_domain, target_domain
    adjacency = []
    for stage, edges in enumerate(layers):
        by_source = defaultdict(list)
        for left, right in edges:
            if left in domains[stage] and right in domains[stage+1]:
                by_source[left].append(right)
        adjacency.append({left: tuple(sorted(rights)) for left, rights in by_source.items()})

    @lru_cache(None)
    def completions(stage, state):
        if stage == count:
            return int(state == finish)
        return sum(completions(stage+1, right)
                   for right in adjacency[stage].get(state, ()))

    path_count = completions(0, start) if start in domains[0] else 0
    witness = []
    if path_count == 1:
        state = start
        witness.append(state)
        for stage in range(count):
            choices = [right for right in adjacency[stage].get(state, ())
                       if completions(stage+1, right)]
            need(len(choices) == 1, "one successor on the recovered unique path")
            state = choices[0]
            witness.append(state)
        need(state == finish and all(len(domain) == 1 for domain in domains),
             "arc-consistent domains recover the sole complete witness")
    # This is a node-reachability count, separately checking the saved peak field.
    reachable, peak = {start}, 1
    for edges in layers:
        reachable = {right for left, right in edges if left in reachable}
        peak = max(peak, len(reachable))
    return {
        'paths': path_count,
        'owners': [state//multiplicity for state in witness],
        'central_masks': [state % multiplicity for state in witness],
        'complete_relation_edges': sum(map(len, layers)),
        'constraint_rounds': rounds,
        'prefix_reachable_peak': peak,
        'surviving_domain_sizes': [len(domain) for domain in domains],
    }


def audit_markers(forward, inverse, allowed, count, inputs, outputs=None):
    need(type(count) is int and count > 0, "positive fresh stage count")
    need(all(type(x) is int and 0 <= x < 1 << (8*count+1) for x in inputs),
         "marker inputs have exactly the declared shared/private geometry")
    owners = [stage % 2 for stage in range(count+1)]
    expected = chain_images(forward, inverse, owners, inputs)
    outputs = expected if outputs is None else outputs
    need(len(outputs) == len(inputs) and all(type(x) is int and 0 <= x < 1 << (8*count+1)
                                           for x in outputs), "marker output domain")
    multiplicity = 1 << len(inputs)
    layers = joined_layers(forward, allowed, count, inputs, outputs)
    report = inspect_graph(layers, central_mask(inputs),
                           (count % 2)*multiplicity+central_mask(outputs), multiplicity)
    report.update(stages=count, inputs=list(inputs), outputs=list(outputs), markers=len(inputs))
    return report


def bank_word(bank):
    word = bank['code_word_left_to_right']
    need(type(word) is list and word and all(
        type(term) is list and len(term) == 2 and type(term[0]) is int and term[0] >= 0
        and type(term[1]) is int and term[1] != 0 for term in word),
        "nonempty bank word with nonzero integer powers")
    stages = [stage for stage, _ in word]
    need(len(set(stages)) == len(stages), "distinct actual fresh private stages")
    need(type(bank['central_exponent']) is int and bank['central_exponent'] == -1
         and bank['operator'] == 'Q^-1 B D'
         and bank['gaussian_stages'] == stages
         and bank['plain_gaussian_after_free_postdecode'] is False,
         "actual negative-bank endpoint type")
    return word


def rejected(call):
    try:
        call()
    except ValueError:
        return True
    raise ValueError("expected malformed bank rejection")


def run(source: Path):
    source = Path(source)
    code = json.loads((source/'inputs/CODE.json').read_text())
    normalizers = json.loads((source/'inputs/NORMALIZERS.json').read_text())
    gauge = json.loads((source/'inputs/GAUGE.json').read_text())
    saved = json.loads((source/'MARKERS.json').read_text())
    a = [[Fraction(value) for value in row] for row in code['A']]
    need(len(a) == 112 and all(len(row) == 112 for row in a), "source coefficient dimensions")
    forward, inverse = load_tables(normalizers['ports'])
    # Include diagonals even when their particular source power has zero weight:
    # isolation in this larger graph is sufficient for every nonzero integer power.
    allowed = [[i == j or a[i][j] != 0 for j in range(112)] for i in range(112)]
    certificates, by_length = [], {}
    for candidate in saved['candidates']:
        count, inputs = candidate['stages'], candidate['markers']
        need(count not in by_length and type(inputs) is list and inputs, "distinct saved marker records")
        report = audit_markers(forward, inverse, allowed, count, inputs)
        need(report['paths'] == candidate['count'] == 1
             and report['prefix_reachable_peak'] == candidate['peak'], "saved count and reachable-peak claims")
        need(report['owners'] == [stage % 2 for stage in range(count+1)],
             "unique witness is the actual alternating owner chain")
        need(chain_images(forward, inverse, report['owners'], [1])[0] != 1,
             "isolated source path moves the shared central line")
        certificates.append(report)
        by_length[count] = report
    need(sorted(by_length) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 18, 19, 32, 64],
         "all thirteen frozen marker certificates are checked")

    banks = []
    negatives = [bank for bank in gauge['typed_caller']['endpoint'] if bank['central_exponent'] == -1]
    need([bank['role'] for bank in negatives] == list(range(16)), "all sixteen actual negative banks")
    for bank in negatives:
        word = bank_word(bank)
        report = by_length[len(word)]
        powers = [-power for _, power in word]
        coefficient = Fraction(1)
        for step, power in enumerate(powers):
            alpha = (1-Fraction(-13)**power)/14
            need(alpha != 0, "each inverse-decoder power has a nonzero off-diagonal coefficient")
            coefficient *= alpha*a[report['owners'][step+1]][report['owners'][step]]
        need(coefficient != 0, "recovered owner path has nonzero exact source coefficient")
        banks.append({'role': bank['role'], 'source_word': word,
                      'decoder_execution_stages': [stage for stage, _ in word],
                      'decoder_execution_powers': powers, 'stages': len(word),
                      'marker_count': report['markers'], 'surviving_paths': report['paths'],
                      'owners': report['owners'], 'selected_path_coefficient': str(coefficient),
                      'conjugated_decoder_add_offset': 3*report['markers']})

    empty = audit_markers(forward, inverse, allowed, 2, [])
    zero = audit_markers(forward, inverse, allowed, 2, [0])
    need(empty['paths'] == zero['paths'] > 1, "empty and zero markers fail to isolate")
    source_marker = by_length[2]['inputs']
    source_output = by_length[2]['outputs']
    impossible = None
    for bit in range(17):
        altered = source_output[:]
        altered[0] ^= 1 << bit
        result = audit_markers(forward, inverse, allowed, 2, source_marker, altered)
        if result['paths'] == 0:
            impossible = {'changed_output_bit': bit, 'outputs': altered, 'paths': 0}
            break
    need(impossible is not None, "perturbed literal endpoint admits no complete path")
    bad_power = dict(negatives[0], code_word_left_to_right=[[32, 0], [31, -1]])
    repeated_stage = dict(negatives[0], code_word_left_to_right=[[32, 1], [32, -1]], gaussian_stages=[32, 32])
    wrong_type = dict(negatives[0], operator='B^-1')
    controls = {'empty_marker_paths': empty['paths'], 'zero_marker_paths': zero['paths'],
                'impossible_output': impossible,
                'zero_power_rejected': rejected(lambda: bank_word(bad_power)),
                'repeated_stage_rejected': rejected(lambda: bank_word(repeated_stage)),
                'wrong_endpoint_type_rejected': rejected(lambda: bank_word(wrong_type))}
    return {'marker_certificates': certificates, 'negative_banks': banks, 'controls': controls,
            'normalizer_truth_table_entries': 112*512,
            'saved_certificate_count': len(certificates), 'actual_negative_bank_count': len(banks),
            'method': 'literal row-dot signature joins, complete layered relations, chain arc consistency, exact DAG count',
            'scope': 'finite path isolation and nonzero coefficients for the Q-conjugated inverse decoder; no lower bound asserted for bare B inverse',
            'independence_limit': 'separate code and transition construction; shared finite-state mathematical invariant, source data and Python'}
