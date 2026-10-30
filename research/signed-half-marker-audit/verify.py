"""Independent marker machine audit. JoyboyBrian + OpenAI Codex. Apache-2.0."""
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def transition_table():
    """Each row reads only mode, symbol, two control bits and scanned data bit."""
    table = {}
    for mode, symbol, a, b, bit in itertools.product(
            ('F', 'FR', 'I', 'IR'), '<>LRABXCT', (0, 1), (0, 1), (0, 1)):
        out, da, db, dm, pm, ret, write = bit, a, b, 0, 0, False, False
        next_mode = mode
        if symbol == '>' and mode in ('F', 'I'):
            next_mode, pm = ('FR' if mode == 'F' else 'IR'), -1
        elif symbol == '<' and mode in ('FR', 'IR'):
            next_mode, pm, ret = ('F' if mode == 'FR' else 'I'), 1, True
        elif symbol in 'LRABXCT':
            pm = 1 if mode in ('F', 'I') else -1
            if mode in ('F', 'IR'):
                if symbol == 'L': dm = -1 if mode == 'F' else 1
                elif symbol == 'R': dm = 1 if mode == 'F' else -1
                elif symbol == 'A': da ^= bit
                elif symbol == 'B': db ^= bit
                elif symbol == 'X': out ^= 1; write = True
                elif symbol == 'C': out ^= a; write = True
                elif symbol == 'T': out ^= a & b; write = True
        else:
            continue
        table[mode, symbol, a, b, bit] = (next_mode, da, db, out, dm, pm, ret, write)
    return table


TABLE = transition_table()


def machine(initial, word, inverse=False, table=TABLE):
    # The host watchdog rejects a failure; only the literal '<' row returns.
    program = '<' + word + '>'
    cells = list(initial)
    pc, head, a, b, mode = 1, 0, 0, 0, 'I' if inverse else 'F'
    steps = moves = marker_steps = 0
    written = set()
    visited = {head}
    while True:
        need(0 <= pc < len(program) and 0 <= head < len(cells), 'head escaped')
        symbol = program[pc]
        row = table.get((mode, symbol, a, b, cells[head]))
        need(row is not None, 'undefined marker transition')
        mode, a, b, value, dm, pm, returned, write = row
        if write:
            cells[head] = value
            written.add(head)
        head += dm
        pc += pm
        visited.add(head)
        steps += 1
        moves += abs(dm)
        marker_steps += int(symbol in '<>')
        if returned:
            break
        need(steps <= 2 * len(word) + 2, 'watchdog: missing return')
    need((head, pc, a, b, mode) == (0, 1, 0, 0, 'I' if inverse else 'F'),
         'heads or finite control did not return')
    need(steps == 2 * len(word) + 2 and marker_steps == 2, 'wrong transition count')
    need(moves == word.count('L') + word.count('R'), 'wrong movement count')
    need(min(visited) >= 0 and max(visited) < len(cells), 'data extent')
    return cells, written, steps


def authenticate():
    source = json.loads((HERE / 'PREDECESSOR.json').read_text())
    need(source['head'] == '39df190f3a8a04cccb88ef1a6ca9aad39ed0364d', 'source head')
    for row in source['files']:
        data = (HERE / row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256')
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob')
    # Compile authenticated bytes directly: stale bytecode cannot replace the oracle.
    namespace = {'__name__': 'frozen_kernel'}
    exec(compile((HERE / 'predecessor/kernel.py').read_bytes(), 'frozen_kernel.py', 'exec'), namespace)
    return namespace


def check_case(source, width, sign, x, coin, gates, word, table=TABLE):
    initial = [(x >> j) & 1 for j in range(width)] + [0] * (width + 2)
    initial[width + 1] = coin
    output, written, steps = machine(initial, word, table=table)
    q, r = divmod(sign * x, 2)
    want = q + int(coin < r)
    value = sum(output[j] << j for j in range(width)) - (output[width - 1] << width)
    need((value, output[width]) == (want, r), 'integer endpoint')
    need(output[width + 1] == coin and width + 1 not in written, 'coin written')
    need(not any(output[width + 2:]), 'dirty work endpoint')
    need(output == source['execute_gates'](initial, gates), 'gate endpoint')
    restored, reverse_written, reverse_steps = machine(output, word, True, table)
    need(restored == initial, 'inverse failed to restore input and clear residue')
    need(width + 1 not in reverse_written, 'inverse coin written')
    need(reverse_steps == steps, 'direction invoice mismatch')
    return steps * 2


def macro_controls(source):
    cases = 0
    # All operand placements in four cells and all local payloads, including dirty controls.
    for op, arity in (('X', 1), ('C', 2), ('T', 3)):
        for operands in itertools.permutations(range(4), arity):
            gate = (op,) + operands
            word = source['compile_tape']([gate])
            for initial in itertools.product((0, 1), repeat=4):
                out, _, _ = machine(initial, word)
                want = list(initial)
                want[operands[-1]] ^= (1 if op == 'X' else initial[operands[0]] if op == 'C'
                                      else initial[operands[0]] & initial[operands[1]])
                need(out == want, 'independent macro endpoint')
                back, _, _ = machine(out, word, True)
                need(back == list(initial), 'macro inverse')
                cases += 1
    return cases


def reject_mutants(source):
    w, s, x, u = 2, -1, -1, 0
    gates = source['compile_gates'](w, s)
    word = source['compile_tape'](gates)
    mutants = {}
    no_turn = dict(TABLE)
    for key in list(no_turn):
        if key[0] == 'F' and key[1] == '>': del no_turn[key]
    mutants['missing-marker-turn'] = (word, no_turn)
    wrong_inverse = dict(TABLE)
    for key, row in list(wrong_inverse.items()):
        if key[0] == 'IR' and key[1] in 'LR':
            row = list(row); row[4] *= -1; wrong_inverse[key] = tuple(row)
    mutants['wrong-inverse-walk'] = (word, wrong_inverse)
    dirty = dict(TABLE)
    for key, row in list(dirty.items()):
        if key[1] == '<':
            row = list(row); row[1] = 1; dirty[key] = tuple(row)
    mutants['retained-accumulator'] = (word, dirty)
    no_rewind = dict(TABLE)
    for key, row in list(no_rewind.items()):
        if key[0] == 'F' and key[1] == '>':
            row = list(row); row[6] = True; no_rewind[key] = tuple(row)
    mutants['missing-rewind'] = (word, no_rewind)
    mutants['coin-write'] = (word + 'R' * (w + 1) + 'X' + 'L' * (w + 1), TABLE)
    reasons = {}
    for name, (bad_word, table) in mutants.items():
        try:
            check_case(source, w, s, x, u, gates, bad_word, table)
        except ValueError as error:
            reasons[name] = str(error)
        else:
            raise ValueError('undetected mutation: ' + name)
    return reasons


def main():
    source = authenticate()
    macro_cases = macro_controls(source)
    source_invoices = {(r['width'], r['sign']): r for r in
                       json.loads((HERE / 'predecessor/RESULT.json').read_text())['invoices']}
    cases = steps = 0
    fixtures = []
    for width in (2, 3, 4, 5, 6, 8, 16, 32, 64):
        low, high = -(1 << (width - 1)), (1 << (width - 1)) - 1
        values = range(low, high + 1) if width <= 6 else (low, high)
        for sign in (-1, 1):
            gates = source['compile_gates'](width, sign)
            word = source['compile_tape'](gates)
            counts = dict(Counter(g[0] for g in gates))
            want = ({'X': 2*width-2, 'C': 4*width+2, 'T': 2*width} if sign == 1 else
                    {'X': 5*width-2, 'C': 5*width, 'T': 4*width-2})
            need(counts == want, 'gate counts')
            d = 2*width+1
            bound = counts['X']*(2*d+1)+counts['C']*(4*d+3)+counts['T']*(6*d+5)
            need(len(word) <= bound, 'word bound')
            invoice = source_invoices.get((width, sign))
            if invoice:
                need(invoice['program_symbols'] == len(word) and
                     invoice['program_sha256'] == hashlib.sha256(word.encode()).hexdigest(),
                     'frozen word invoice')
            for x, coin in itertools.product(values, (0, 1)):
                steps += check_case(source, width, sign, x, coin, gates, word)
                cases += 1
            fixtures.append({'width': width, 'sign': sign, 'word_length': len(word),
                             'steps_per_direction': 2*len(word)+2})
    result = {'status': 'PASS', 'table_rows': len(TABLE), 'macro_cases': macro_cases,
              'half_round_trips': cases, 'half_transitions': steps,
              'mutations': reject_mutants(source), 'fixtures': fixtures}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
