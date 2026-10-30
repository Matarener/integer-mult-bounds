"""Construct shorter target-pair bases and check the complete G20 caller.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source archives retain all controller, native and synthesis credits.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def extract(path, target):
    with tarfile.open(path) as archive:
        for member in archive:
            rel = Path(member.name)
            need((member.isfile() or member.isdir()) and not rel.is_absolute()
                 and '..' not in rel.parts, 'Regular relative archive member')
            out = target/rel
            if member.isdir():
                out.mkdir(parents=True, exist_ok=True)
            else:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(archive.extractfile(member).read())


def matrix(word):
    rows = [1 << i for i in range(32)]
    for op, d, s in word:
        need(0 <= d < 32 and 0 <= s < 32 and d != s, 'Boundary owners')
        if op == 'ADD':
            rows[d] ^= rows[s]
        else:
            need(op == 'SWAP', 'Boundary opcode')
            rows[d], rows[s] = rows[s], rows[d]
    return rows


def cost(word):
    return sum(1 if e[0] == 'ADD' else 3 for e in word)


def normalize(word, mask):
    permutation = [i ^ ((mask >> (i // 2)) & 1) for i in range(32)]
    adds = []
    for op, d, s in word:
        if op == 'ADD':
            adds.append(['ADD', permutation[d], permutation[s]])
        else:
            need(op == 'SWAP', 'Normalization opcode')
            permutation[d], permutation[s] = permutation[s], permutation[d]
    state, swaps = list(range(32)), []
    for i, target in enumerate(permutation):
        if state[i] != target:
            j = state.index(target)
            state[i], state[j] = state[j], state[i]
            swaps.append(['SWAP', i, j])
    return adds + swaps


def verify_boundary(old, new, mask):
    diag = old['diagonal']
    need(all(diag[i] == diag[i ^ ((mask >> (i // 2)) & 1)] for i in range(32)),
         'Basis change commutes with the exact target diagonal')
    swaps = [['SWAP', 2*j, 2*j+1] for j in range(16) if mask >> j & 1]
    right, left = (new['boundaries'][side + '_program'] for side in ('right', 'left'))
    need(matrix(right) == matrix(swaps + old['boundaries']['right_program']), 'Exact new right map')
    need(matrix(left) == matrix(old['boundaries']['left_program'] + swaps), 'Exact new left map')
    need(matrix(right + left) == matrix(left + right) == [1 << i for i in range(32)], 'Both boundary inverse products')
    need(all(new[k] == old[k] for k in old if k != 'boundaries'), 'Unchanged physical core and target jobs')


def construct(old):
    histogram, best, winner = Counter(), 10**9, None
    original = old['boundaries']['right_program']
    need(all(old['diagonal'][2*j] == old['diagonal'][2*j+1] for j in range(16)),
         'All permitted pair orientations commute')
    for mask in range(1 << 16):
        word = normalize(original, mask)
        swaps = [['SWAP', 2*j, 2*j+1] for j in range(16) if mask >> j & 1]
        need(matrix(word) == matrix(swaps + original), 'Every normalized boundary matrix')
        count = cost(word)
        histogram[count] += 1
        if count < best:
            best, winner = count, (mask, word)
    # A second census uses permutation cycles, without the word constructor.
    base = [row.bit_length() - 1 for row in matrix([e for e in original if e[0] == 'SWAP'])]
    cycle_histogram = Counter()
    for mask in range(1 << 16):
        permutation = [i ^ ((mask >> (i // 2)) & 1) for i in base]
        seen, cycles = set(), 0
        for i in range(32):
            if i not in seen:
                cycles += 1
                while i not in seen:
                    seen.add(i)
                    i = permutation[i]
        cycle_histogram[14 + 3 * (32 - cycles)] += 1
    need(histogram == cycle_histogram, 'Separate complete orientation census')
    mask, right = winner
    new = deepcopy(old)
    new['boundaries']['right_program'] = right
    new['boundaries']['left_program'] = right[::-1]
    for side in ('left', 'right'):
        new['boundaries'][side + '_rows'] = matrix(new['boundaries'][side + '_program'])
    new['boundaries']['boundary_unit_ADDs_per_port'] = 2 * best
    verify_boundary(old, new, mask)
    return new, dict(mask=mask, candidates=1 << 16, cost_per_side=best,
                     histogram={str(k): v for k, v in sorted(histogram.items())},
                     minimum_attainers=histogram[best])


def permute_inputs(row, mask):
    blockmask = (1 << 111) - 1
    for j in range(16):
        if mask >> j & 1:
            a, b = 222*j, 222*j + 111
            difference = ((row >> a) ^ (row >> b)) & blockmask
            row ^= (difference << a) ^ (difference << b)
    return row


def fixed_points(word, trace, parent, tables):
    expanded = []
    for op, d, s in word:
        expanded.extend([['ADD', d, s, 0]] if op == 'ADD' else
                        [['ADD', d, s, 0], ['ADD', s, d, 0], ['ADD', d, s, 0]])
    first, a = trace.commute_pass(expanded, parent)
    second, b = trace.projection_pass(first, parent, tables)
    third, c = parent.pass_once(second, tables)
    need(not a and not b and not c and third == expanded, 'Exact local synthesis fixed point')
    return len(expanded)


def run(emit=None):
    for pin in read(HERE/'SOURCES.json')['vendored_inputs']:
        need(sha256((HERE/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Frozen source archive')
    with tempfile.TemporaryDirectory(prefix='g20-target-pairs-') as temp:
        root = Path(temp)
        extract(HERE/'inputs/PR5834.tar.gz', root/'parent')
        parent_dir = root/'parent/research/g20-global-trace-construction'
        args = [sys.executable, '-I', '-B'] + (['-O'] if sys.flags.optimize else [])
        completed = subprocess.run(args + [str(parent_dir/'verify.py')], capture_output=True, text=True, timeout=240)
        need(completed.returncode == 0, 'Full parent replay: ' + completed.stderr[-2000:])
        parent = load('boundary_global_checks', parent_dir/'verify.py')
        extract(parent_dir/'inputs/PR5708.tar.gz', root/'source')
        extract(parent_dir/'inputs/PR5828.tar', root/'local')
        source = root/'source/research/g20-conjugation-admission'
        local = root/'local/research/g20-trace-resynthesis'
        L = load('boundary_source', source/'integration.py')
        old = read(L.S/'inputs/CONTROLLER.json')
        controller, census = construct(old)
        spec = read(HERE/'ADAPTATION.json')
        compiler_text = (parent_dir/'compile.py').read_text()
        need(sha256(compiler_text.encode()).hexdigest() == spec['source_sha256'], 'Exact parent compiler')
        for before, after in spec['changes']:
            need(compiler_text.count(before) == 1, 'One explicit compiler parameter change')
            compiler_text = compiler_text.replace(before, after)
        need((HERE/'compile.py').read_text() == compiler_text, 'No other compiler changes')
        compiler = load('boundary_compiler', HERE/'compile.py')
        out = root/'output'
        out.mkdir()
        compiler.compile_global(L, read(parent_dir/'WORD.json.gz'), out, controller)
        program = parent.events(out/'GLOBAL.jsonl.gz')
        invoice, glob = read(out/'INVOICE.json'), read(out/'GLOBAL-RESULT.json')
        need(invoice == read(parent_dir/'INVOICE.json'), 'Unchanged complete signed invoice')
        need(read(out/'TARGET-OWNERS.json') == read(parent_dir/'TARGET-OWNERS.json'), 'Unchanged productive owners')
        desc = read(out/'SOURCE-DESCRIPTORS.json.gz')
        scan = parent.scan(program, desc, invoice)
        need([scan['stream_sha256'], scan['majorant'], scan['counts']] ==
             [glob['canonical_stream_sha256'], glob['majorant'], glob['operation_counts']], 'Separate complete stream receipt')
        prior_desc = read(parent_dir/'SOURCE-DESCRIPTORS.json.gz')
        need(len(desc) == len(prior_desc) == 56223, 'Every paid native input')
        changed = 0
        for before, after in zip(prior_desc, desc):
            need(all(before[k] == after[k] for k in ('owner', 'rank', 'detail')), 'Same native job and frame')
            expected = permute_inputs(int(before['RAW_hex'], 16), census['mask'])
            need(int(after['RAW_hex'], 16) == expected, 'Exact changed native input relation')
            changed += before['RAW_hex'] != after['RAW_hex']
        oldprogram = parent.events(parent_dir/'GLOBAL.jsonl.gz')
        strip = lambda xs: [e for e in xs if not (e[0] == 'ADD' and e[3] in ('RIGHT_BOUNDARY', 'LEFT_BOUNDARY'))]
        need(strip(program) == strip(oldprogram), 'Entire physical core remains literal')
        oldcalls, calls = read(parent_dir/'CALLS.json'), read(out/'CALLS.json')
        shift = 111 * (census['cost_per_side'] - cost(old['boundaries']['right_program']))
        for before, after in zip(oldcalls, calls):
            expected = dict(before, core_begin=before['core_begin'] + shift, core_end=before['core_end'] + shift)
            need(after == expected, 'Every changed call interval and owner')
        oldepisodes, episodes = read(parent_dir/'PRIVATE-EPISODES.json'), read(out/'PRIVATE-EPISODES.json')
        need(len(oldepisodes) == len(episodes) == 2529, 'All private lifetimes')
        for before, after in zip(oldepisodes, episodes):
            need(after == dict(before, begin=before['begin'] + shift, end=before['end'] + shift), 'Every private lifetime moves with the core')
        oldglob = read(parent_dir/'GLOBAL-RESULT.json')
        need(glob['physical_MAIN_coefficients'] == oldglob['physical_MAIN_coefficients'], 'All physical polynomial coefficients')
        need(scan['majorant_bits'] < 1024, 'Full retained precision envelope')
        fees = parent.fee(invoice, glob, read(source/'MATCHER.json'))
        oldfees = read(parent_dir/'RESULT.json')['new_fee']
        saved = 111 * (old['boundaries']['boundary_unit_ADDs_per_port'] - 2*census['cost_per_side'])
        need(len(oldprogram) - len(program) == saved and oldfees['total'] - fees['total'] == 2*saved,
             'Complete charged global savings')
        sys.path.insert(0, str(local/'vendor'))
        scalar = load('boundary_scalar_synthesis', local/'inputs/parent.py')
        trace = load('boundary_trace_synthesis', local/'verify.py')
        tables = scalar.tables()
        minima = [fixed_points(controller['boundaries'][side+'_program'], trace, scalar, tables)
                  for side in ('left', 'right')]
        controls = []
        bad = deepcopy(controller)
        bad['boundaries']['left_program'] = bad['boundaries']['left_program'][1:]
        try:
            verify_boundary(old, bad, census['mask'])
        except ValueError:
            controls.append('missing_boundary_operation')
        else:
            raise ValueError('Incomplete boundary accepted')
        badsource = deepcopy(old)
        badsource['diagonal'][2] ^= 2
        try:
            verify_boundary(badsource, controller, census['mask'])
        except ValueError as error:
            need(str(error) == 'Basis change commutes with the exact target diagonal', 'Expected target rejection')
            controls.append('unequal_target_pair')
        else:
            raise ValueError('Unequal target pair accepted')
        result = dict(status='PASS_G20_TARGET_PAIR_BOUNDARIES', census=census,
                      boundary_cost_before=old['boundaries']['boundary_unit_ADDs_per_port'],
                      boundary_cost_after=2*census['cost_per_side'], local_fixed_points=minima,
                      complete_stream=scan, changed_query_values=changed, invoice=invoice,
                      calls=len(calls), private_lifetimes=len(episodes), old_fee=oldfees, new_fee=fees,
                      saved_global_adds=saved, saved_finite_primitives=2*saved, negative_controls=controls)
        extra = {'CONTROLLER.json': controller, 'RESULT.json': result}
        names = parent.OUTPUTS
        if emit:
            emit.mkdir(parents=True, exist_ok=True)
            for name in names:
                (emit/name).write_bytes((out/name).read_bytes())
            for name, value in extra.items():
                (emit/name).write_text(json.dumps(value, indent=2) + '\n')
        else:
            for name, value in extra.items():
                need(read(HERE/name) == value, 'Complete retained artifact ' + name)
            for name in names:
                a, b = (p.read_bytes() for p in (HERE/name, out/name))
                if name.endswith('.gz'):
                    a, b = map(gzip.decompress, (a, b))
                need(a == b, 'Exact rebuilt artifact ' + name)
    print('PASS_G20_TARGET_PAIR_BOUNDARIES', saved, fees['total'], scan['majorant_bits'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', type=Path)
    run(parser.parse_args().emit)
