"""Independent G20 controller-query binding. Dennis / antunishdPursuit.
Substantial OpenAI Codex assistance. Apache-2.0; no predecessor imports.
"""
from collections import Counter
import hashlib
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def projector_rank(thick, stages, central=False):
    need(len(thick) == len(set(thick)), 'distinct thick stages')
    need(len(stages) == len(set(stages)) and set(stages) <= set(thick), 'idle stage subset')
    # Evaluate the literal diagonal reflection product on the retained address
    # model: one central coordinate plus disjoint seven-coordinate stage blocks.
    signs = [1] * (1 + 7 * len(thick))
    if central:
        signs[0] = -1
    for stage in stages:
        position = thick.index(stage)
        for coordinate in range(1 + 7 * position, 8 + 7 * position):
            signs[coordinate] *= -1
    # (I-R)/2 is a diagonal projector; its nonzero columns form an identity minor.
    return sum((1 - sign) // 2 for sign in signs)


def expected_queries(controller, ports):
    thick = controller['invoice']['thick_stages']
    need(controller['ambient_rank'] == 1 + 7 * len(thick), 'address dimension')
    expected = []
    for event in controller['physical_events']:
        op = event[0]
        if op == 'IDLE':
            _, pair, stages = event
            rank = projector_rank(thick, stages)
            need(rank > 0, 'nonempty idle')
            for bank in (2 * pair, 2 * pair + 1):
                for port in range(ports):
                    expected.append(('WHOLE_IDLE', tuple(stages), bank, port, rank, None))
        elif op == 'QUERY_SHEAR':
            _, stage, pair, reverse = event
            need(stage not in thick, 'thin stage outside thick blocks')
            x, y = 2 * pair, 2 * pair + 1
            if reverse:
                x, y = y, x
            for port in range(ports):
                expected.append(('THIN', stage, y, port, projector_rank(thick, [], central=True), x))
        else:
            need(op in ('LOCAL', 'ADD', 'SWAP'), 'controller opcode')
    for kind, scope, bank, port, rank, source in expected:
        need(0 <= bank < 2 * controller['pairs'], 'controller bank')
    idle = Counter(row[4] for row in expected if row[0] == 'WHOLE_IDLE')
    need(dict(idle) == {int(k): v for k, v in controller['invoice']['whole_idle'].items()},
         'derived controller idle invoice')
    need(sum(row[0] == 'THIN' for row in expected) == controller['invoice']['thin_queries'],
         'derived thin count')
    return expected


def audit(controller, records, originals, owned_count, ports=111):
    expected = expected_queries(controller, ports)
    owned = set(range(originals, originals + owned_count))
    zero = set()  # Owned entries are not granted zero until an explicit CLEAR.
    clean_copy = set()
    ordered = []
    for index, record in enumerate(records):
        op = record[0]
        if op == 'OWNED_CLEAR':
            need(record[1] in owned, 'clear only owned field')
            zero.add(record[1])
        elif op == 'ADD':
            d, s = record[1:3]
            if d in owned:
                if d in zero and s in zero:
                    pass
                else:
                    if d in zero:
                        clean_copy.add(index)
                    zero.discard(d)
        elif op == 'QUERY':
            detail = record[3]
            need(isinstance(detail, list) and detail, 'query descriptor')
            kind = detail[0]
            if kind.startswith('LOCAL_'):
                continue  # Local native queries remain outside this audit.
            need(kind in ('THIN', 'WHOLE_IDLE'), 'known controller query kind')
            need(len(ordered) < len(expected), 'extra controller query')
            wanted = expected[len(ordered)]
            k, scope, bank, port, rank, source = wanted
            need(kind == k and record[2] == rank, 'derived query kind and rank')
            if kind == 'WHOLE_IDLE':
                need(record[1] == bank * ports + port and detail == [kind, list(scope), port],
                     'idle bank, port and stage identity')
            else:
                center = record[1]
                need(center in owned, 'thin query uses owned scratch')
                need(detail == [kind, scope, port], 'thin stage and port')
                need(index >= 1 and index + 2 < len(records), 'complete thin episode')
                need(records[index - 1] == ['ADD', center, source * ports + port,
                                          ['THIN_COPY', scope, port]], 'literal thin copy')
                need(index - 1 in clean_copy, 'explicitly clean thin scratch before copy')
                need(records[index + 1] == ['ADD', bank * ports + port, center,
                                          ['THIN_DELIVER', scope, port]], 'literal thin delivery')
                need(records[index + 2] == ['OWNED_CLEAR', center, None, [kind, scope, port]],
                     'literal owned thin erasure')
            ordered.append(list(wanted[:-1]))
    need(len(ordered) == len(expected), 'every expected controller query')
    thin = Counter(row[4] for row in expected if row[0] == 'THIN')
    idle = Counter(row[4] for row in expected if row[0] == 'WHOLE_IDLE')
    raw = json.dumps(ordered, separators=(',', ':')).encode()
    return {'controller_queries': len(expected), 'thin_queries': sum(thin.values()),
            'whole_idle_queries': sum(idle.values()),
            'component_histogram': {str(k): v for k, v in sorted((thin + idle).items())},
            'component_rank_mass': sum(k * v for k, v in (thin + idle).items()),
            'ordered_controller_sha256': hashlib.sha256(raw).hexdigest()}
