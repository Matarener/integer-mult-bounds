"""Exact component invoice and lifetime high water for the retained physical codecs.

The harness authenticates source before importing. The inert loader shim only
avoids loading the unrelated full selected compiler; the two tested codecs and
all record/Word/parking operations execute unchanged pinned source bodies.
"""
import ast
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CALLER = ROOT / 'research/selected-bit-physical-caller'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(root=ROOT):
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((root / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'changed source: ' + row['path'])


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def load():
    authenticate()
    words = module('words', CALLER / 'inputs/pr2769/vendor/words.py')
    records = module('records', CALLER / 'inputs/pr2753/predecessor/vendor/records.py')
    parking = module('parking_machine', CALLER / 'inputs/pr2769/vendor/parking_machine.py')
    codec = module('bank_codec', CALLER / 'inputs/pr2769/codec.py')
    shim = types.ModuleType('loader')
    shim.activate = lambda: None
    sys.modules['loader'] = shim
    roles = module('role_parking', CALLER / 'role_parking.py')
    return words, records, parking, codec, roles


WORDS, RECORDS, PARKING, CODEC, ROLES = load()


class ObservedMachine(PARKING.Machine):
    def __init__(self):
        super().__init__(packet={0: '^'}, heads=(0, 1))
        self.all_visited = [set(), set()]

    def observe(self):
        for k, position in enumerate(self.heads):
            self.all_visited[k].add(position)

    def step(self):
        self.observe()
        super().step()
        self.observe()


class ObservedCodec(CODEC.BankParking):
    def _read(self, tape):
        self.machine.observe()
        return super()._read(tape)

    def _write(self, tape, symbol):
        self.machine.observe()
        return super()._write(tape, symbol)

    def _move(self, tape, direction):
        self.machine.observe()
        super()._move(tape, direction)
        self.machine.observe()


class ObservedTape(RECORDS.Tape):
    def __init__(self):
        super().__init__()
        self.visited = {0, 1}

    def read(self):
        self.visited.add(self.head)
        return super().read()

    def write(self, symbol):
        self.visited.add(self.head)
        return super().write(symbol)

    def step(self, direction):
        self.visited.add(self.head)
        super().step(direction)
        self.visited.add(self.head)


def stream_invoice(length, roles, frames=1):
    return {'reads': 61*length+23*roles+14*frames,
            'writes': 26*length+6*roles+2*frames,
            'moves': 52*length+20*roles+10*frames}


def numeric_invoice(bits, word_bits, records, frames=1):
    return {'reads': 14*bits+10*word_bits+32*records+15*frames,
            'writes': 6*bits+3*word_bits+8*records+2*frames,
            'moves': 12*bits+10*word_bits+30*records+12*frames}


def add(a, b):
    return {k: a[k]+b[k] for k in a}


def subtract(a, b):
    return {k: a[k]-b[k] for k in a}


def snapshot(codec, roles, arenas):
    meters = [t.meter for t in roles] + [a.meter for a in arenas]
    return {k: sum(getattr(m, k) for m in meters) + codec.codec_counts[k]
            + codec.machine.counts[k] for k in ('reads', 'writes', 'moves')}


def exercise(role_count, forest, capacity=(8, 6), widths=(5, 7)):
    arenas = tuple(WORDS.Arena(b, capacity=c) for b, c in zip(widths, capacity))
    roles = tuple(ObservedTape() for _ in range(role_count))
    machine = ObservedMachine()
    codec = ObservedCodec(*arenas, machine=machine)
    streams = ROLES.RoleParking(codec, roles)
    expected = dict(reads=0, writes=0, moves=0)
    observed = dict(expected)
    active = maximum = record_max = total_weight = calls = 0
    peak_lengths = [0]*role_count
    rows = []
    total_p = 0

    def visit(node):
        nonlocal expected, observed, active, maximum, record_max, total_weight, calls, total_p
        lengths, counts, children = node
        need(len(lengths) == role_count, 'fixture arity')
        for i, (tape, length) in enumerate(zip(roles, lengths)):
            tape.rewind()
            need(tape.read() == WORDS.BLANK, 'empty reusable body')
            for j in range(length):
                tape.append(ROLES.BODY[(i+j) % len(ROLES.BODY)])
            tape.rewind()
            peak_lengths[i] = max(peak_lengths[i], length)
        saved = []
        for a, count in zip(arenas, counts):
            saved.append([a.literal((i+1) % (1 << a.bits)) for i in range(count)])
        saved_bytes = [[bytes(w.cells) for w in slots] for slots in saved]
        p = sum(counts)
        total_p += p
        B = sum(c*b for c, b in zip(counts, widths))
        S = sum(c*(1+ell+b) for c, ell, b in zip(counts, codec.slot_bits, widths))
        L = sum(lengths)
        A = 2 + role_count + 4*L + p + S
        active += A
        total_weight += A
        maximum = max(maximum, active)
        record_max = max(record_max, max((4*x for x in lengths), default=0),
                         max((1+ell+b for c, ell, b in zip(counts, codec.slot_bits, widths) if c), default=0))
        before = snapshot(codec, roles, arenas)
        streams.park()
        codec.park()
        observed = add(observed, subtract(snapshot(codec, roles, arenas), before))
        need(machine.heads[0] == active, 'weighted active stack equals actual physical head')
        for child in children:
            visit(child)
        before = snapshot(codec, roles, arenas)
        codec.restore()
        streams.restore()
        observed = add(observed, subtract(snapshot(codec, roles, arenas), before))
        active -= A
        calls += 1
        need(machine.heads[0] == active, 'matched return restores weighted stack origin')
        for i, (tape, length) in enumerate(zip(roles, lengths)):
            expected_body = bytes(ROLES.BODY[(i+j) % len(ROLES.BODY)] for j in range(length))
            need(tape.head == 1 and bytes(tape.cells[1:length+1]) == expected_body
                 and all(x == WORDS.BLANK for x in tape.cells[length+1:]), 'exact body and head restored')
            tape.clear()  # Caller-owned work, deliberately outside codec invoice.
        for a, slots, values in zip(arenas, saved, saved_bytes):
            need(all(a.words[w.slot] is w and w.slot in a.live for w in slots), 'original aliases restored')
            for w, value in zip(slots, values):
                need(bytes(w.cells) == value and w.head == 1, 'exact parent word bytes and head')
                a.free(w)  # Caller-owned cleanup outside invoice.
        expected = add(expected, add(stream_invoice(L, role_count), numeric_invoice(S, B, p)))
        rows.append({'roles': role_count, 'symbols': L, 'word_records': p,
                     'word_bits': B, 'serialized_word_bits': S, 'stack_weight': A})

    for root in forest:
        visit(root)
    need(calls > 0, 'nonempty complete call forest')
    need(observed == expected, 'exact complete stream plus numerical scan invoice')
    need(codec.codec_counts['slot_tests'] == sum(capacity)*calls, 'fixed inventory scan multiplicity')
    need(codec.codec_counts['commands'] == (2*role_count+4)*calls+2*total_p, 'complete command dispatch count')
    need(machine.tapes == [{}, {0: '^'}] and machine.heads == [0, 1], 'complete blank stack return')
    need(machine.all_visited[0] == set(range(maximum+1)), 'exact lifetime parking span')
    need(machine.all_visited[1] == set(range(record_max+2)), 'exact lifetime shared-port span')
    need(all(t.visited == set(range(m+2)) for t, m in zip(roles, peak_lengths)), 'per-role maximum backing spans')
    # A final empty backing map has forgotten every formerly parked cell.
    need(len(machine.tapes[0]) < len(machine.all_visited[0]), 'live-only reserve rejected')
    return {'calls': calls, 'roles': role_count, 'api_invoice': observed,
            'slot_tests': codec.codec_counts['slot_tests'], 'command_dispatches': codec.codec_counts['commands'],
            'maximum_active_weight': maximum, 'sum_all_call_weights': total_weight,
            'parking_visited': len(machine.all_visited[0]),
            'port_visited': len(machine.all_visited[1]),
            'canonical_visited': sum(map(len, (t.visited for t in roles))),
            'record_max_bits': record_max, 'rows': rows}


def preparation_checks():
    # This exact, hash-authenticated function needs only BLANK. Extracting its
    # AST isolates its tape scans; it is not a full directory-module replay.
    path = CALLER / 'inputs/pr2753/predecessor/vendor/directory.py'
    function = next(x for x in ast.parse(path.read_text()).body
                    if isinstance(x, ast.FunctionDef) and x.name == 'append_tape')
    namespace = {'BLANK': WORDS.BLANK}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
    append_tape = namespace['append_tape']
    samples = 0
    for length in (0, 1, 2, 7, 23, 127):
        source, target = ObservedTape(), ObservedTape()
        for i in range(length):
            source.append(ROLES.BODY[i % len(ROLES.BODY)])
        source.rewind()
        def total(ts):
            return {k: sum(getattr(t.meter, k) for t in ts) for k in ('reads', 'writes', 'moves')}
        before = total((source, target))
        need(target.read() == WORDS.BLANK, 'literal capsule empty guard')
        append_tape(source, target)
        target.rewind()
        need(subtract(total((source, target)), before) ==
             {'reads': 5*length+5, 'writes': length, 'moves': 4*length+6},
             'capsule copy including empty check and destination rewind')
        for old_length in (0, 1, 19):
            out = ObservedTape()
            for _ in range(old_length): out.append(1)
            out.rewind()
            before = total((target, out))
            ROLES.transfer(target, out)
            need(subtract(total((target, out)), before) ==
                 {'reads': 5*length+2*old_length+7, 'writes': 2*length+old_length,
                  'moves': 4*length+2*old_length+10}, 'exact result/adoption transfer')
            # Restore fixture data; this work is excluded from the invoice.
            append_tape(source, target); target.rewind()
            samples += 1
    for width in (2, 5, 13, 31):
        arena = WORDS.Arena(width, capacity=4)
        source = arena.literal(1)
        before = {k: getattr(arena.meter, k) for k in ('reads', 'writes', 'moves')}
        result = arena.copy(source)
        after = {k: getattr(arena.meter, k) for k in before}
        need(subtract(after, before) == {'reads': 8*width+9, 'writes': 2*width+1,
                                        'moves': 8*width+12}, 'exact grant copy')
        arena.free(result); arena.free(source)
    for bounds in ((2,), (2, 2, 8, 16, 16, 16, 8, 8), (2, 3, 100, 2**24, 2**24, 2**24, 2**24, 2**24)):
        schema = ROLES.FiniteFields(bounds)
        tape = ObservedTape()
        H = sum(schema.widths)
        before = {k: getattr(tape.meter, k) for k in ('reads', 'writes', 'moves')}
        schema.write(tape, [x-1 for x in bounds])
        need(schema.read(tape) == tuple(x-1 for x in bounds), 'finite header round trip')
        tape.clear()
        after = {k: getattr(tape.meter, k) for k in before}
        need(subtract(after, before) == {'reads': 6*H+9, 'writes': 2*H,
                                        'moves': 6*H+12}, 'exact header write/read/clear')
    return {'copy_transfer_length_pairs': samples, 'grant_widths': [2, 5, 13, 31],
            'header_schemas': 3, 'scope': 'exact component scans, excluded production of capsule data'}


def grant_check():
    arenas = (WORDS.Arena(7, capacity=8), WORDS.Arena(5, capacity=8))
    roles = (ObservedTape(), ObservedTape())
    for i in range(3): roles[0].append(i % 2)
    roles[0].rewind()
    parents = ([arenas[0].literal(3), arenas[0].literal(5)], [arenas[1].literal(4)])
    originals = [[bytes(w.cells) for w in slots] for slots in parents]
    grants = ([arenas[0].literal(7)], [arenas[1].literal(2), arenas[1].literal(3)])
    machine = ObservedMachine()
    codec = ObservedCodec(*arenas, machine=machine)
    streams = ROLES.RoleParking(codec, roles)
    before = snapshot(codec, roles, arenas)
    streams.park()
    codec.park(tuple(frozenset(w.slot for w in slots) for slots in grants))
    charged = subtract(snapshot(codec, roles, arenas), before)
    need(tuple(a.live for a in arenas) == tuple({w.slot for w in slots} for slots in grants),
         'only owned grants remain live while parent is parked')
    for a, slots in zip(arenas, grants):
        for w in slots: a.free(w)  # Child-owned closure, excluded from checkpoint.
    before = snapshot(codec, roles, arenas)
    codec.restore(); streams.restore()
    charged = add(charged, subtract(snapshot(codec, roles, arenas), before))
    B, S, p = 19, 31, 3
    need(charged == add(stream_invoice(3, 2), numeric_invoice(S, B, p)), 'ungranted-word invoice')
    need(len(machine.all_visited[0]) == 2+2+12+p+S+1, 'granted words absent from parent stack')
    for a, slots, values in zip(arenas, parents, originals):
        for w, value in zip(slots, values):
            need(a.words[w.slot] is w and bytes(w.cells) == value and w.head == 1, 'grant case parent restores')
            a.free(w)
    return {'grants': 3, 'parked_parent_words': p, 'word_bits': B, 'record_bits': S, 'api_invoice': charged}


def history_checks():
    path = CALLER/'inputs/pr2753/predecessor/vendor/children.py'
    function = next(x for x in ast.parse(path.read_text()).body
                    if isinstance(x, ast.FunctionDef) and x.name == 'extend')
    namespace = dict(vars(RECORDS)); namespace['need'] = WORDS.need
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
    extend = namespace['extend']
    results = []
    for h in (0, 1, 2, 4, 8):
        I, L, Q = 6*(h+2)+2, 5, 7
        for kind, half in (('good',False), ('pair',False), ('unit',False), ('unit',True)):
            index, residue = WORDS.Arena(I, capacity=128), WORDS.Arena(L, capacity=16)
            root_size = 64**(h+2)
            parent = RECORDS.Program.fixture(index,residue,root_size,2,[(2,19,1,0,0,0)]*h,code_bits=Q)
            before = bytes(parent.tape.cells)
            P = 2*I+L+6+h*(Q+2*I+90)
            need(len(before) == P, 'exact parent grammar length including LEFT')
            raw = WORDS.Unsigned(index)
            def plus(a,b):
                value, carry = raw.add(a,b)
                need(not carry,'fixture index margin');return value
            incoming = types.SimpleNamespace(program=parent,index=index,residue=residue,
                current_code=19,specifications={19:types.SimpleNamespace(template=types.SimpleNamespace(rank=7))},
                raw=raw,final_size=index.literal(4096),sixty_four=index.literal(64),two_index=index.literal(2),
                depth=index.literal(h),one_index=index.literal(1),root_size=index.literal(root_size),
                root_unit=residue.literal(2),plus=plus)
            coordinate=index.zero()
            request=types.SimpleNamespace(child_kind=kind,half=half,coordinate=coordinate,field=0,reverse=False)
            child=extend(incoming,request)
            expected=P+Q+2*I+90
            need(len(child.tape.cells)==expected, 'literal extend appends one STEP with fixed root extent')
            need(bytes(parent.tape.cells)==before and parent.tape.head==child.tape.head==1,
                 'literal extension preserves parent bytes and both heads')
            old_root=2*I+L+6
            need(bytes(child.tape.cells[old_root:P])==before[old_root:], 'all chronological STEP bytes copied')
            results.append({'history':h,'kind':kind,'half':half,'I':I,'L':L,'Q':Q,
                            'parent_symbols_including_LEFT':P,'child_symbols_including_LEFT':expected})
    for d in range(1,20):
        for h in range(5):
            I,L,Q=59,7,31
            exact=sum(4*(2*I+L+5+(h+j)*(Q+2*I+90)) for j in range(d))
            closed=4*d*(2*I+L+5)+4*(Q+2*I+90)*(d*h+d*(d-1)//2)
            need(exact==closed, 'weighted path history contribution')
    return {'literal_extensions':results,'scope':'Actual extend body with fixture incoming fields; Callback/source acceptance not executed'}


def main():
    rng = random.Random(4373967)
    def node(r, depth):
        lengths = [rng.randrange(0, 19) for _ in range(r)]
        counts = (rng.randrange(4), rng.randrange(4))
        children = [node(r, depth-1) for _ in range(rng.randrange(3))] if depth else []
        return lengths, counts, children
    cases = []
    for r in (0, 1, 4, 9):
        for _ in range(8):
            cases.append(exercise(r, [node(r, 3) for _ in range(3)]))
    # A wide root followed by many narrow siblings distinguishes max active
    # depth from cumulative traffic, with the exact same permanent tape bank.
    leaf = ([1, 0, 0, 0], (1, 0), [])
    siblings = exercise(4, [([23, 0, 0, 0], (2, 1), [leaf]*64)])
    need(siblings['maximum_active_weight'] < siblings['sum_all_call_weights'],
         'cumulative sibling storage is a strict overcount')
    # Actual current-source role inventory from PR3967, parameter-only: no
    # full-volume R437 packet or semantic child is represented by empty bodies.
    actual = exercise(29097, [([0]*29097, (0, 0), [])], capacity=(1, 1), widths=(2, 2))
    need(actual['maximum_active_weight'] == 29099, 'empty roles still pay physical frame cells')
    # Four-bit alphabets are finite-control assumptions, not arbitrary bytes.
    a, b = WORDS.Arena(2, capacity=1), WORDS.Arena(2, capacity=1)
    t = ObservedTape()
    t.append(2)  # LEFT inside a role body is invalid.
    t.rewind()
    # rewind would stop at the interior LEFT; restore the legal cut explicitly
    # in the rejection fixture, never as a production operation.
    t.head = 1
    try:
        ROLES.RoleParking(ObservedCodec(a, b, machine=ObservedMachine()), [t]).park()
    except ValueError:
        pass
    else:
        raise ValueError('interior marker admitted')
    result = {'scope': 'unchanged component codecs; no full production caller replay',
              'preparation_components': preparation_checks(), 'nonempty_grants': grant_check(), 'history': history_checks(),
              'random_seed': 4373967, 'random_cases': len(cases),
              'random_completed_calls': sum(x['calls'] for x in cases),
              'random_max_depth_at_most': 4, 'siblings': siblings,
              'actual_role_count_empty_body': actual,
              'indexed_role_candidate': {'R':29097,'label_bits':(29097-1).bit_length(),
                  'last_saving_K':(29097-1)//(1+(29097-1).bit_length()),
                  'full_family_K':28416,'indexed_overhead':28416*(1+(29097-1).bit_length()),
                  'original_overhead':29097,'scope':'this fixed-width indexed-record design only'},
              'controls': ['empty final stack does not imply zero visited backing',
                           'siblings add work but reuse backing',
                           'empty canonical roles retain delimiter cost',
                           'interior LEFT rejects']}
    output = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(output)
    else:
        need(json.loads((HERE / 'RESULT.json').read_text()) == result, 'committed exact receipt')
    print('PASS exact stream/numerical invoice and lifetime high water:', len(cases), 'forests,', result['random_completed_calls'], 'random calls')


if __name__ == '__main__':
    main()
