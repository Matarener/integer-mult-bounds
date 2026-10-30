"""Literal port9 low-cache frontend embedding and complete-owner carry leaf.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
Retains JoyboyBrian's PR5332 frontend and Ali Romman's PR5849 serialized
rotation/descriptor composition, including David Arias's local tape machine.
Program construction receives no runtime modulus, payload, low row, or carry.
"""
from contextlib import contextmanager
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOW = 'research/bit-low-carry-lowering/'
CARRY = 'research/runtime-quarter-carry/'
INPUT = CARRY + 'inputs/'
WEIGHTS = (-1, 0, -2, 0, -1, 0, 0, 0)
POSITIONS = tuple(range(8))
TAPE_MAP = (17, 18, 9, 5, 14)
KERNEL_WORK = (2, 3, 8, 10, 11, 12, 13, 15)
EXPECTED_INPUTS = {LOW + 'controller.py', LOW + 'offset.py', CARRY + 'TABLE.json.gz',
                   *(INPUT + name for name in ('counters.py', 'descriptor.py', 'independent.py',
                                               'machine.py', 'route-RESULT.json', 'shear.py'))}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows = [row for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']
            if row['usage'] == 'input']
    require(len(rows) == 9 and {row['path'] for row in rows} == EXPECTED_INPUTS,
            'exact adapter source inventory')
    raw = {}
    for row in rows:
        path = ROOT / row['path']
        require(not path.is_symlink(), 'adapter source symlink')
        value = path.read_bytes()
        require(hashlib.sha256(value).hexdigest() == row['sha256'], 'adapter source SHA256')
        blob = b'blob ' + str(len(value)).encode('ascii') + b'\0' + value
        require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'adapter source Git blob')
        raw[row['path']] = value
    return raw, rows


@contextmanager
def aliases(mapping):
    """Give frozen imports their original names without leaking module state."""
    absent = object()
    previous = {name: sys.modules.get(name, absent) for name in mapping}
    sys.modules.update(mapping)
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is absent:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def source_module(name, path, raw, imports=None):
    module = types.ModuleType('_port9_pinned_' + name)
    module.__file__ = str(ROOT / path)
    with aliases({**(imports or {}), module.__name__: module}):
        exec(compile(raw[path], str(ROOT / path), 'exec', optimize=0), module.__dict__)
    return module


def load():
    """Authenticate all nine inputs and compile the fixed frontend once."""
    raw, rows = authenticate()
    modules = {}
    for name in ('machine', 'counters', 'shear'):
        modules[name] = source_module(name, INPUT + name + '.py', raw, modules)
    dense = source_module('independent', INPUT + 'independent.py', raw)
    descriptor = source_module('descriptor', INPUT + 'descriptor.py', raw)
    offset = source_module('offset', LOW + 'offset.py', raw)
    controller = source_module('controller', LOW + 'controller.py', raw)
    with aliases({'offset': offset}):
        original = controller.compile_frontend(5, list(WEIGHTS), positions=POSITIONS, cells=64)
    require(original['bits'] == 3 and original['weights'] == list(WEIGHTS)
            and original['positions'] == list(POSITIONS) and original['cells'] == 64,
            'fixed actual-column frontend parameters')
    tables = json.loads(gzip.decompress(raw[CARRY + 'TABLE.json.gz']))
    for inverse in (False, True):
        dense.validate(tables['generic:' + str(inverse)])
    return dict(modules=modules, dense=dense, descriptor=descriptor, controller=controller,
                offset=offset, tables=tables, raw=raw, source_rows=rows, source_frontend=original)


def export(program):
    """JSON-compatible table for the independent interpreter."""
    return json.loads(json.dumps(dict(tapes=program.tapes, entry=program.entry,
                                     instructions=program.instructions)))


def from_table(machine, table):
    rows = []
    for row in table['instructions']:
        if row[0] == 'branch':
            rows.append((row[0], row[1], tuple(tuple(pair) for pair in row[2]), row[3]))
        else:
            rows.append(tuple(row))
    return machine.Program(tuple(rows), table['tapes'], table['entry'])


def frontend(bundle=None):
    """Return the literal frontend and one-to-one source-PC embedding metadata.

    Tape14 is blank at its origin on entry. The paid prefix moves to origin+1;
    source offset code then puts LEFT at origin and returns at the first bit.
    Each source write/move gains one explicit goto, since the target ABI uses
    fall-through successors. All other rows keep one instruction and all source
    edges are relocated through row_starts, including rejection/default edges.
    """
    bundle = load() if bundle is None else bundle
    machine, old = bundle['modules']['machine'], bundle['source_frontend']
    symbols = {None: machine.BLANK, 0: machine.ZERO, 1: machine.ONE,
               2: machine.RIGHT, 3: machine.LEFT}
    starts, position = [], 2
    for row in old['code']:
        starts.append(position)
        position += 2 if row[0] in ('move', 'write') else 1
    rows = [('move', 14, 1), ('goto', starts[old['start']])]
    for pc, row in enumerate(old['code']):
        require(len(rows) == starts[pc], 'source-PC embedding position')
        op = row[0]
        if op == 'branch':
            rows.append(('branch', TAPE_MAP[row[1]],
                         tuple((symbols[symbol], starts[target]) for symbol, target in row[2]),
                         starts[row[3]]))
        elif op == 'move':
            rows.extend((('move', TAPE_MAP[row[1]], row[2]), ('goto', starts[row[3]])))
        elif op == 'write':
            rows.extend((('write', TAPE_MAP[row[1]], symbols[row[2]]), ('goto', starts[row[3]])))
        elif op == 'goto':
            rows.append(('goto', starts[row[1]]))
        elif op == 'halt':
            rows.append(('halt',))
        elif op == 'reject':
            rows.append(('reject', 'retained low-cache frontend rejected'))
        else:
            raise ValueError('unsupported retained frontend instruction')
    program = machine.Program(tuple(rows), 19)
    bundle['dense'].validate(export(program))
    metadata = dict(tape_map=TAPE_MAP, symbol_map=symbols, row_starts=tuple(starts),
                    row_stops=tuple(starts[1:] + [len(rows)]), source_frontend=old,
                    prefix_length=2, source_instructions=len(old['code']),
                    embedded_instructions=len(rows), descriptor_first_bit_offset=1)
    return program, metadata


def build(inverse=False, bundle=None):
    """Two fixed orientations: frontend, unchanged generic table, owned erasure."""
    require(type(inverse) is bool, 'fixed Boolean carry orientation')
    bundle = load() if bundle is None else bundle
    first, metadata = frontend(bundle)
    machine = bundle['modules']['machine']
    table = bundle['tables']['generic:' + str(inverse)]
    generic = from_table(machine, table)
    require(export(generic) == table, 'unchanged serialized generic table')
    cleanup = bundle['descriptor'].erase(bundle['modules'])
    components = {'frontend': first, 'generic': generic, 'cleanup': cleanup}
    require(all(p.tapes == 19 and p.entry == 0 for p in components.values()),
            'retained link entry contract')
    # The predecessor's linker changes only PC relocation and intermediate
    # halts to jumps. It does not choose any runtime carry or touch tape state.
    program = bundle['descriptor'].link(bundle['modules'], list(components.values()))
    boundaries, start = {}, 0
    for name, component in components.items():
        boundaries[name] = dict(start=start, stop=start + len(component.instructions),
                                entry=start + component.entry)
        start += len(component.instructions)
    require(start == len(program.instructions), 'component instruction inventory')
    bundle['dense'].validate(export(program))
    return program, dict(**metadata, inverse=inverse, components=boundaries,
                         component_programs=components, full_instructions=len(program.instructions),
                         generic_key='generic:' + str(inverse), kernel_work=KERNEL_WORK)


def resource_bounds(volume, modulus_bits):
    """Proof ledger for observers; never called by a machine instruction.

    D=64, b=3. Source frontend F<=64Db+256L+2048; embedding <=2F+2.
    Generic rotation <=393V; erasure of an n-bit C+1 costs 8n+8, n<=L.
    Adding visited intervals (including already erased cells) is conservative.
    The looser published bounds reserve margin rather than claim a sharp bill.
    """
    require(type(volume) is int and volume >= 3 and type(modulus_bits) is int
            and modulus_bits >= 2, 'positive complete volume and odd-modulus width')
    source = 64 * 64 * 3 + 256 * modulus_bits + 2048
    return dict(source_frontend_steps=source, embedded_frontend_steps=2 * source + 2,
                generic_steps=393 * volume, erase_steps=8 * modulus_bits + 8,
                composed_steps=393 * volume + 520 * modulus_bits + 28682,
                composed_span=43 * volume + 4 * modulus_bits + 418,
                published_steps=393 * volume + 600 * modulus_bits + 30000,
                published_span=43 * volume + 8 * modulus_bits + 500)
