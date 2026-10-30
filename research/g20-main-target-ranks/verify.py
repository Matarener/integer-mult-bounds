"""Independent MAIN-bank polynomial/rank audit. Dennis, with OpenAI Codex assistance.
Apache-2.0. No predecessor modules are imported; see README for the inherited contract.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = 'research/g20-conjugation-admission/'
CONTROLLER = PREFIX + 'prior/prior/prior/source/vendor/g20/inputs/CONTROLLER.json'
OTHER = 'research/g20-helper-split/'
OTHER_CONTROLLER = OTHER + 'prior/prior/source/vendor/g20/inputs/CONTROLLER.json'
PORTS = 111
BANKS = 32


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(root):
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    out = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        raw = (root / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == row['git_blob'], 'source blob: ' + row['path'])
        out[row['path']] = raw
    return out


def controller_ranks(c):
    """Rebuild the complete formal polynomial, then its stated coordinate action."""
    thick = c['invoice']['thick_stages']
    need(thick == sorted(set(thick)) and len(thick) == 18, 'distinct thick stages')
    need(c['ambient_rank'] == 1 + 7 * len(thick), 'ambient direct-sum dimension')
    need(c['pairs'] * 2 == BANKS and c['kind'] == 'bit', 'controller shape')
    stages = [e[1] for e in c['physical_events'] if e[0] == 'LOCAL']
    need(sorted(stages) == thick, 'physical LOCAL stages equal thick stages')
    # Each set element is (formal monomial, labeled input bank). Symmetric
    # difference adds coefficients over F2; monomial multiplication XORs bits.
    rows = [{(0, i)} for i in range(BANKS)]
    def add(d, s):
        need(type(d) is int and type(s) is int and 0 <= d < BANKS and 0 <= s < BANKS and d != s,
             'distinct in-range boundary banks')
        rows[d] = rows[d] ^ rows[s]
    def gate(e):
        need(len(e) == 3, 'boundary gate arity')
        op, d, s = e
        if op == 'ADD':
            add(d, s)
        else:
            need(op == 'SWAP', 'boundary opcode')
            # Physical XOR swap, not a free relabeling assumption.
            add(d, s); add(s, d); add(d, s)
    def shift(bank, monomial):
        rows[bank] = {(m ^ monomial, source) for m, source in rows[bank]}
    for e in c['boundaries']['right_program']:
        gate(e)
    for e in c['physical_events']:
        op = e[0]
        if op in ('LOCAL', 'QUERY_SHEAR'):
            need(len(e) == 4, 'local arity')
            _, stage, pair, reverse = e
            need(type(pair) is int and 0 <= pair < BANKS // 2 and type(reverse) is bool,
                 'local bank pair')
            need(type(stage) is int and 0 <= stage <= 32, 'stage index')
            if op == 'QUERY_SHEAR':
                need(stage not in thick, 'thin stage outside thick stages')
            x, y = 2 * pair, 2 * pair + 1
            if reverse:
                x, y = y, x
            rows[y] ^= {(m ^ 1, source) for m, source in rows[x]}
            if op == 'LOCAL':
                shift(x, 1 << (stage + 1)); shift(y, 1 << (stage + 1))
        elif op == 'IDLE':
            need(len(e) == 3, 'idle arity')
            _, pair, idle = e
            need(type(pair) is int and 0 <= pair < BANKS // 2, 'idle pair')
            need(len(idle) == len(set(idle)) and set(idle) <= set(thick), 'idle stage subset')
            monomial = sum(1 << (j + 1) for j in idle)
            shift(2 * pair, monomial); shift(2 * pair + 1, monomial)
        else:
            gate(e)
    for e in c['boundaries']['left_program']:
        gate(e)
    declared = c['diagonal']
    need(len(declared) == BANKS, 'diagonal length')
    need(rows == [{(m, i)} for i, m in enumerate(declared)], 'complete labeled polynomial endpoint')
    need(declared == c['boundaries']['diagonal_monomials'], 'boundary diagonal agrees')
    # Construct the retained direct-sum coordinate model: one central line and
    # 18 disjoint seven-dimensional stage spaces. Each generator reflects just
    # its own block. Evaluate all 127 signed coordinate columns separately.
    blocks = {1: {0}}
    for position, stage in enumerate(thick):
        blocks[1 << (stage + 1)] = set(range(1 + 7 * position, 8 + 7 * position))
    need(set.union(*blocks.values()) == set(range(c['ambient_rank'])), 'complete coordinate cover')
    need(sum(map(len, blocks.values())) == c['ambient_rank'], 'disjoint coordinate cover')
    ranks = []
    for row in rows:
        monomial, _ = next(iter(row))
        active = [bit for bit in blocks if monomial & bit]
        need(sum(active) == monomial and monomial & 1, 'only retained stage factors and central line')
        diagonal = []
        for coordinate in range(c['ambient_rank']):
            value = 1
            for bit in active:
                if coordinate in blocks[bit]:
                    value *= -1
            diagonal.append((1 - value) // 2)
        # This is a diagonal projector. Its unit entries give both an explicit
        # nonsingular identity minor and a spanning set of all nonzero columns.
        rank = sum(diagonal)
        need(rank == 1 + 7 * (len(active) - 1), 'coordinate rank versus stage formula')
        ranks.append(rank)
    return ranks


def check_targets(targets, invoice, ranks):
    main = [t for t in targets if t.get('matcher', '').startswith('MAIN_BANK_')]
    need(len(main) == BANKS * PORTS, 'MAIN target count')
    seen = set()
    for t in main:
        bank = int(t['matcher'].removeprefix('MAIN_BANK_'))
        port, owner = t['port'], t['original_owner']
        need(0 <= bank < BANKS and type(port) is int and 0 <= port < PORTS, 'target bank/port')
        need(type(owner) is int and owner == bank * PORTS + port, 'target owner identifies bank and port')
        need(owner not in seen, 'unique MAIN owner')
        seen.add(owner)
        need(t['operator'] == 'D_(P_line+selectedorthogonalstageblocks)' and
             t['route_pair_required_in_generic_job_matching'] is True, 'MAIN operator and route contract')
        need(t['rank'] == ranks[bank], 'derived MAIN target rank')
    need(seen == set(range(BANKS * PORTS)), 'every MAIN owner covered')
    derived = Counter(rank for rank in ranks for _ in range(PORTS))
    need(Counter(t['rank'] for t in main) == derived, 'per-owner rank histogram')
    # Current invoice target keys are disjoint from helper ranks 4 and 8.
    claimed = {int(k): v for k, v in invoice['targets'].items() if int(k) in set(ranks)}
    need(claimed == dict(derived), 'invoice MAIN histogram')
    return dict(sorted(derived.items()))


def checks(data):
    c = json.loads(data[CONTROLLER])
    need(data[CONTROLLER] == data[OTHER_CONTROLLER], 'both source controllers identical')
    ranks = controller_ranks(c)
    histograms = []
    for prefix in (PREFIX, OTHER):
        histograms.append(check_targets(json.loads(data[prefix + 'TARGET-OWNERS.json']),
                                       json.loads(data[prefix + 'INVOICE.json']), ranks))
    need(histograms[0] == histograms[1], 'both candidate inventories agree')
    need({int(k): v for k, v in c['invoice']['main'].items()} == histograms[0], 'controller MAIN histogram')
    return {'banks': BANKS, 'ports_per_bank': PORTS, 'MAIN_targets_per_candidate': BANKS * PORTS,
            'controller_physical_events': len(c['physical_events']), 'ambient_rank': c['ambient_rank'],
            'bank_ranks': ranks, 'MAIN_histogram': {str(k): v for k, v in histograms[0].items()},
            'rank_mass_per_candidate': sum(k * v for k, v in histograms[0].items())}


def controls(data):
    c = json.loads(data[CONTROLLER]); targets = json.loads(data[PREFIX + 'TARGET-OWNERS.json'])
    invoice = json.loads(data[PREFIX + 'INVOICE.json']); ranks = controller_ranks(c)
    rejected = []
    def reject(name, f):
        try:
            f()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control survived: ' + name)
    for name, mutate in [
        ('declared diagonal changed', lambda x: x['diagonal'].__setitem__(0, x['diagonal'][0] ^ 2)),
        ('missing thick call', lambda x: x['physical_events'].pop(0)),
        ('duplicate thick stage', lambda x: x['invoice']['thick_stages'].append(0)),
        ('wrong ambient dimension', lambda x: x.__setitem__('ambient_rank', 126)),
        ('wrong boundary gate', lambda x: x['boundaries']['right_program'].insert(0, ['ADD', 0, 1])),
        ('unknown physical opcode', lambda x: x['physical_events'].append(['FREE', 0, 1])),
    ]:
        x = deepcopy(c); mutate(x); reject(name, lambda: controller_ranks(x))
    for name, mutate in [
        ('wrong target rank', lambda x: x[0].__setitem__('rank', 16)),
        ('wrong MAIN operator', lambda x: x[0].__setitem__('operator', 'identity')),
        ('missing route obligation', lambda x: x[0].__setitem__('route_pair_required_in_generic_job_matching', False)),
        ('duplicate original owner', lambda x: x[1].__setitem__('original_owner', 0)),
        ('wrong target port', lambda x: x[0].__setitem__('port', 1)),
        ('equal-rank bank alias', lambda x: x[0].__setitem__('matcher', 'MAIN_BANK_1')),
        ('missing MAIN target', lambda x: x.pop(0)),
    ]:
        x = deepcopy(targets); mutate(x); reject(name, lambda: check_targets(x, invoice, ranks))
    x = deepcopy(invoice)
    for rank, count in [('15', -2), ('22', 4), ('29', -2)]:
        x['targets'][rank] += count
    reject('count-and-mass-preserving wrong invoice', lambda: check_targets(targets, x, ranks))
    # Source corruption must fail before any JSON parsing/controller execution.
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for path, raw in data.items():
            p = root / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        p = root / CONTROLLER; p.write_bytes(p.read_bytes() + b' ')
        reject('changed source bytes', lambda: load(root))
    return rejected


def main():
    data = load(ROOT)
    result = checks(data)
    result['rejected_controls'] = controls(data)
    path = HERE / 'RESULT.json'
    if sys.argv[1:] == ['--write-result']:
        path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        need(not sys.argv[1:], 'unexpected arguments')
        need(json.loads(path.read_text(encoding='utf-8')) == result, 'committed result equals fresh derivation')
    print(json.dumps(result, sort_keys=True))
    print('PASS_G20_MAIN_TARGET_RANKS')


if __name__ == '__main__':
    main()
