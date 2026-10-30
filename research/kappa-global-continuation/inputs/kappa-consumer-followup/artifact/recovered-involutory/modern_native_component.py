#!/usr/bin/env python3
"""Independently reconstruct the PR3734 involution and bind intrinsic lines.

Apache-2.0. New work used substantial OpenAI Codex assistance. The original
supplier, native recipe interpreter and recipes retain their own notices.
This is a finite local component check, not a supplier or kappa admission.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import copy
import gzip
import json
import platform

PIVOTS = (0, 7, 20, 27, 36, 46, 57, 111)
NATIVE_RECEIPT_SHA = '7ddf3f80b2fa61d1ab12035da9ef1c95d43f76077df819d7683144d7862a3f93'
LEGACY_SHA = {
    'native_verify.py': '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38',
    'certificate.json': 'f9ab470df50d7a9f9bc1e03fc0c1d30976c8f45f7bcbc0fb3ee371befdced652',
    'unit-transfer-certificate.json': '6f9a382f600e74fa5b20b458097a0038405028156fc49eec3366e8e52de7ebbe',
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def add(dst, src, factor=Q(1)):
    for key, val in src.items():
        value = dst.get(key, Q(0)) + factor * val
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def warp(row, op):
    out = {}
    for (var, word), value in row.items():
        new = word[1:] if word and word[0] == -op else (op,) + word
        add(out, {(var, new): value})
    return out


def replay(events, n=632):
    """Literal linear propagation over free noncommuting warp words."""
    state = {('L', i): {(i, ()): Q(1)} for i in range(n)}
    for index, event in enumerate(events):
        tag = event[0]
        if tag == 'warp':
            reg = tuple(event[1])
            state[reg] = warp(state[reg], event[2])
        elif tag == 'zero_buffer':
            reg = ('Z', event[2])
            if event[1] == 'alloc':
                state[reg] = {}
            else:
                need(not state[reg], f'zero buffer dirty at {index}')
        elif tag == 'scalar':
            gate = event[1]
            op, target = gate[0], tuple(gate[1])
            if op == 'clear':
                state[target] = {}
            elif op == 'copy':
                state[target] = state[tuple(gate[2])].copy()
            elif op == 'scale':
                q = Q(gate[2], gate[3])
                state[target] = {key: q * value for key, value in state[target].items() if q * value}
            else:
                need(op == 'add', 'unknown scalar')
                add(state.setdefault(target, {}), state[tuple(gate[2])], Q(gate[3], gate[4]))
        else:
            need(tag in ('phase', 'adapter', 'residual_adapter', 'climb', 'center', 'intrinsic_line'), tag)
    return state


def matmul(left, right):
    out = []
    for row in left:
        result = {}
        for j, value in row.items():
            add(result, right[j], value)
        out.append(result)
    return out


def scalar(target, source, value, frame):
    value = Q(value)
    return ['scalar', ['add', list(target), list(source), value.numerator, value.denominator], frame]


def clear(frame):
    return ['scalar', ['clear', ['C', 0]], frame]


def source_code(R, A, bank, frame):
    result = []
    for k, query in enumerate(R):
        result.append(clear(frame))
        for p, value in sorted(query.items()):
            result.append(scalar(('C', 0), ('L', bank + p), value, frame))
        for p, row in enumerate(A):
            if k in row:
                result.append(scalar(('L', bank + p), ('C', 0), row[k], frame))
        result.append(clear(0))
    return result


def repair(C, word, backward):
    result = []
    for p in PIVOTS:
        frame, bank = (0, 112) if backward else (1, 0)
        target = p if backward else 112 + p
        sign = 1 if backward else -1
        target_frame = word['start'][p] if backward else word['final'][112 + p]
        result.append(clear(frame))
        for j, value in sorted(C[p].items()):
            result.append(scalar(('C', 0), ('L', bank + j), sign * value, frame))
        result.append(['intrinsic_line', p, word['ports'][p], sign, frame, target_frame, 1])
        result.append(scalar(('L', target), ('C', 0), 1, target_frame))
        result.append(clear(0))
    return result


def clean_reconstruction(word, programs):
    n, v = len(word['start']), word['v']
    need((n, v, word['R'], word['h']) == (632, 112, 408, 9), 'supplier dimensions')
    omitted = {}
    for name, program in programs.items():
        begin, end = program.index(['phase', 'centers']), program.index(['phase', 'B'])
        omitted[name] = program[:begin] + [['phase', 'centers']] + program[end:]
    fw = replay(omitted['forward'], n)
    dirt = []
    J = []
    for p in range(v):
        row = fw['L', v + p].copy()
        need(row.pop((v + p, ()), None) == 1, 'target identity')
        J.append({var: a for (var, w), a in row.items() if var < v and not w})
        need(not any(w or v <= var < 2*v for (var, w) in row), 'noncanonical missing-center endpoint')
        dirt.append({var: a for (var, _), a in row.items() if var >= 2*v})
    need(all(fw['L', p] == {(p, ()): Q(1)} for p in list(range(v)) + list(range(2*v, n))), 'omission changed source/helper')
    before = replay(programs['forward'][:programs['forward'].index(['phase', 'centers'])], n)
    R = [{var: a for (var, w), a in before['L', c].items() if var < v and not w} for c in word['centers']]
    need(all(not w for c in word['centers'] for (var, w) in before['L', c] if var < v), 'warped source query')
    H = [{var: a for (var, w), a in before['L', c].items() if var >= 2*v and not w} for c in word['centers']]
    need(all(not w for c in word['centers'] for (var, w) in before['L', c]), 'warped centre query')
    K = [{k: R[k][p]/4 for k in range(8) if p in R[k]} for p in range(v)]
    P = [row.copy() if p in PIVOTS else {} for p, row in enumerate(K)]
    need(matmul(R, P) == [{k: Q(1)} for k in range(8)], 'RP identity')
    need(matmul(R, K) == [{k: Q(14)} for k in range(8)], 'RK identity')
    KR = matmul(K, R)
    expected_J = []
    for p, row in enumerate(KR):
        target = {p: Q(1)}
        add(target, row, Q(-1))
        expected_J.append(target)
    need(J == expected_J, 'clean J = I-KR')
    need(dirt == [{j: -a for j,a in row.items()} for row in matmul(K, H)], 'complete dirty endpoint = -KH')
    dirty_events = {}
    clean = {}
    for name in programs:
        back = name == 'backward'
        es = []
        for k, row in enumerate(H):
            es.append(clear(0))
            need(all(word['start'][h] == 0 for h in row), 'dirty correction helper not initially I')
            if back:
                for p, image in enumerate(K):
                    if k in image:
                        es.append(scalar(('C', 0), ('L', v+p), image[k], 0))
                for h, value in sorted(row.items()):
                    es.append(scalar(('L', h), ('C', 0), -value, 0))
            else:
                for h, value in sorted(row.items()):
                    es.append(scalar(('C', 0), ('L', h), value, 0))
                for p, image in enumerate(K):
                    if k in image:
                        es.append(scalar(('L', v+p), ('C', 0), image[k], 0))
            es.append(clear(0))
        # The endpoint derivation already includes all retained entry precondition
        # effects, so its correction is placed at the physical entrance.
        dirty_events[name] = es
        clean[name] = es + omitted[name]
        actual = replay(clean[name], n)
        for p in range(n):
            expected = {(p, ()): Q(1)}
            if back and p < v:
                add(expected, {(v+j, ()): a for j, a in J[p].items()}, Q(-1))
            elif not back and v <= p < 2*v:
                add(expected, {(j, ()): a for j, a in J[p-v].items()})
            need(actual['L', p] == expected, f'clean-J endpoint {name}:{p}')
    return R, K, P, J, clean, dirty_events


def contains(small, large):
    pivots = {}
    for value in large:
        while value:
            i = value.bit_length()-1
            if i in pivots:
                value ^= pivots[i]
            else:
                pivots[i] = value
                break
    for value in small:
        while value:
            i = value.bit_length()-1
            if i not in pivots:
                return False
            value ^= pivots[i]
    return True


def core_frame_check(word, events):
    """Independently check actual modern persistent/owned frame chronology."""
    n = len(word['start'])
    cur = word['start'].copy()
    frame = word['frames']
    private, zlive = {}, set()
    hpe = {r for r in range(224,n) if word['final'][r] != 1}
    wrapped = {r for r in range(224,n) if word['start'][r] != 0} | hpe
    pre, post = set(), set()
    phase = None
    hist = Counter()
    for index, event in enumerate(events):
        tag = event[0]
        if tag == 'phase':
            phase = event[1]
            need(not private, f'private across phase {phase}')
        elif tag == 'climb':
            _, part, r, old, new, rank = event
            need(not private and part == phase and cur[r] == old, 'climb chronology')
            need(contains(frame[old], frame[new]) and rank == len(frame[new])-len(frame[old]) > 0, 'climb rank')
            cur[r] = new
            hist[rank] += 1
        elif tag == 'adapter':
            _, side, r, f = event
            need(f == (word['start'] if side == 'old_to_new' else word['final'])[r], 'adapter boundary frame')
            need(r not in (wrapped if side == 'old_to_new' else hpe), 'incorrect ordinary adapter')
        elif tag == 'residual_adapter':
            _, side, r, f, *end = event
            need(r in wrapped and f == word['start'][r], 'helper wrapper entrance')
            need(end == ([word['final'][r]] if r in hpe else []), 'helper wrapper terminal')
            selected = pre if side == 'pre' else post
            need(r not in selected and phase == ('entry_adapters' if side == 'pre' else 'full_frame_cleanup'), 'helper wrapper chronology')
            selected.add(r)
        elif tag == 'warp':
            _, reg, op, old, new = event
            need(op and not private and len(frame[old]) == len(frame[new]), 'warp rank/owned work')
            if reg[0] == 'L':
                r = reg[1]
                need(cur[r] == old and (r not in wrapped or r in pre-post), 'warp common frame/hosting')
                cur[r] = new
            else:
                need(reg[0] == 'Z' and reg[1] in zlive and old == new == 1, 'warp private buffer')
        elif tag == 'zero_buffer':
            _, side, z = event
            need(phase == 'full_frame_cleanup' and z in word['zero_buffers'], 'zero buffer phase')
            if side == 'alloc':
                need(z not in zlive, 'buffer already live')
                zlive.add(z)
            else:
                need(z in zlive, 'buffer not live')
                zlive.remove(z)
        elif tag == 'scalar':
            gate, f = event[1:]
            op, target = gate[0], tuple(gate[1])
            source = tuple(gate[2]) if op in ('add','copy') else None
            if op == 'clear':
                need(target[0] == 'C', 'only query scratch cleared')
                private.pop(target, None)
                continue
            for r in (target, source):
                if r is None:
                    continue
                if r[0] == 'L':
                    need(cur[r[1]] == f, f'scalar common frame at {index}: {r}')
                    need(r[1] not in wrapped or r[1] in pre-post, 'scalar helper wrapper chronology')
                elif r[0] == 'Z':
                    need(r[1] in zlive and f == 1, 'scalar zero buffer frame')
                else:
                    need(r[0] == 'C', 'unknown private register')
                    if r == target and r not in private:
                        private[r] = f
                    need(private.get(r) == f, 'private scalar frame')
        else:
            need(False, 'unexpected clean core event '+tag)
    need(cur == word['final'] and pre == post == wrapped and not private and not zlive, 'complete core exit')
    return dict(sorted(hist.items()))


def boundary_check(events, word, backwards, block):
    """Boundary scalar additions act in literal external native gauges."""
    before = backwards or block == 'dirty'
    types = {}
    for p in range(112):
        types['L',p] = ('C',word['ports'][p]) if before else ('FULL',)
        types['L',112+p] = ('I',) if before else ('HOLE',word['ports'][p])
    for r in range(224,632):
        # Only ordinary unwrapped I helpers occur in the dirty correction.
        types['L',r] = ('I',) if word['start'][r] == 0 and word['final'][r] == 1 else ('HELPER',r)
    types['C',0] = ('I',)
    used = []
    for event in events:
        if event[0] == 'intrinsic_line':
            _, p, label, sign, old, new, rank = event
            need(p in PIVOTS and label == word['ports'][p] and rank == 1, 'line port and rank')
            need(sign == (1 if backwards else -1), 'line orientation')
            need(old == (0 if backwards else 1) and new == (word['start'][p] if backwards else word['final'][112+p]), 'line event frame binding')
            need(types['C',0] == (('I',) if backwards else ('FULL',)), 'line input gauge')
            types['C',0] = ('C',label) if backwards else ('HOLE',label)
            used.append(p)
            continue
        need(event[0] == 'scalar', 'unknown boundary event')
        gate, f = event[1:]
        op, target = gate[0], tuple(gate[1])
        if op == 'clear':
            need(target == ('C',0) and f in (0,1), 'owned scratch reset')
            types[target] = ('I',) if f == 0 else ('FULL',)
            continue
        need(op == 'add', 'unpriced boundary gate')
        source = tuple(gate[2])
        need(target != source and types[target] == types[source], 'boundary addition crosses native gauges')
        expected = types[target]
        if expected in (('I',),('FULL',)):
            need(f == (0 if expected == ('I',) else 1), 'boundary common frame ID')
        else:
            p = target[1] if backwards else target[1]-112
            need(source == ('C',0) and p in PIVOTS, 'repair uses selected target only')
            need(f == (word['start'][p] if backwards else word['final'][112+p]), 'repair target frame')
    need(types['C',0] == ('I',), 'query accumulator not returned to I zero')
    need(used == (list(PIVOTS) if block == 'repair' else []), 'complete selected native inventory')


def load_native(legacy):
    for basename, expected in LEGACY_SHA.items():
        need(digest(legacy/basename) == expected, 'retained native source pin '+basename)
    module_path = legacy/'native_verify.py'
    spec = spec_from_file_location('retained_exact_native_interpreter', module_path)
    native = module_from_spec(spec)
    spec.loader.exec_module(native)
    cert, ext = read(legacy/'certificate.json'), read(legacy/'unit-transfer-certificate.json')
    return native, cert, ext


def native_line_checks(word, native, cert, ext):
    positive = {r['port']:r for r in cert['input_recipes']}
    negative = {r['port']:r for r in ext['inverse_exit_recipes']}
    need(set(positive) == set(negative) == set(PIVOTS), 'retained recipe support')
    results = []
    full = native.fourier(9)
    endpoint = []
    for p in PIVOTS:
        q = word['ports'][p]
        need(word['frames'][word['start'][p]] == [q], 'modern start line subspace')
        hole = word['frames'][word['final'][112+p]]
        need(len(hole) == 8 and contains(hole,hole) and all((a&q).bit_count()%2 == 0 for a in hole), 'modern output hole subspace')
        for sign, inventory in ((1,positive),(-1,negative)):
            record = inventory[p]
            need(record['label'] == q and record['recipe']['rank'] == 1, 'modern line label binding')
            actual, expected = native.recipe(record['recipe']), (('C',q,sign),)
            native.equal(actual, expected, f'new line {p}:{sign}')
            for column in range(512):
                need(native.state(actual,column) == native.state(expected,column), f'exact Gaussian line {p}:{sign}:{column}')
            need(native.state(actual+(('phase',1),)) != native.state(expected), 'phase mutation not rejected')
            need(native.state(actual) != native.state((('C',q,-sign),)), 'direction mutation not rejected')
            if sign == -1:
                native.equal(full+actual, expected+full, 'FULL-to-native-hole integration')
            results.append({'port':p,'q':q,'sign':sign,'rank':1,'gaussian_columns':512})
        endpoint.append({'port':p,'entry_frame':word['start'][p],'output_frame':word['final'][112+p]})
    return {'exact_line_recipes':len(results),'exact_gaussian_columns':512*len(results),'phase_mutations_rejected':len(results),'direction_mutations_rejected':len(results),'full_to_hole_compositions':len(PIVOTS),'modern_frame_binding':endpoint}


def scalar_bill(events):
    macros = Counter()
    cost = 0
    for event in events:
        if event[0] != 'scalar':
            continue
        e = event[1]
        macros[e[0]] += 1
        if e[0] in ('clear','copy'):
            cost += 2
            continue
        q = Q(e[3],e[4]) if e[0] == 'add' else Q(e[2],e[3])
        a,b = abs(q.numerator),q.denominator
        need(a > 0 and b & (b-1) == 0, 'dyadic scalar bill')
        if e[0] == 'scale':
            need(a & (a-1) == 0, 'nonbinary scale')
            cost += 2*(abs(a.bit_length()-b.bit_length())+int(q < 0))
        else:
            cost += 2*(3+a.bit_length()-1+a.bit_count()+b.bit_length()-1)
    return {'real_primitives':cost,'macros':dict(sorted(macros.items()))}


def scalar_prefix(events):
    """The inherited cancellation-free scalar triangle bound, including codes."""
    norms = {('L',r):Q(1) for r in range(632)}
    peak = Q(1)
    for event in events:
        if event[0] == 'zero_buffer' and event[1] == 'alloc':
            norms['Z',event[2]] = Q(0)
        elif event[0] == 'scalar':
            e = event[1]
            target = tuple(e[1])
            if e[0] == 'clear':
                norms[target] = Q(0)
            elif e[0] == 'copy':
                norms[target] = norms[tuple(e[2])]
            elif e[0] == 'scale':
                norms[target] *= abs(Q(e[2],e[3]))
            else:
                q, source = Q(e[3],e[4]), tuple(e[2])
                peak = max(peak,abs(q.numerator)*norms[source])
                norms[target] = norms.get(target,Q(0))+abs(q)*norms[source]
            peak = max(peak,norms[target])
    bits = peak.numerator.bit_length()-peak.denominator.bit_length()
    if Q(2)**bits < peak:
        bits += 1
    need(peak < 2**192, 'retained 192-bit scalar prefix cap exceeded')
    return {'l1_upper':str(peak),'ceiling_log2':bits,'retained_cap_bits':192,
            'scope':'Scalar/free-monomial triangle bound; complete recursive native precision/tape theorem remains inherited.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    ap.add_argument('--inputs', type=Path, default=here/'modern-source/inputs')
    ap.add_argument('--legacy', type=Path, default=here.parent/'integer-mult-bounds/research/native-source-codes')
    ap.add_argument('--out', type=Path, default=here/'modern-native-results')
    args = ap.parse_args()
    receipt = read(args.inputs/'NATIVE-RECEIPT.json')
    need(digest(args.inputs/'NATIVE-RECEIPT.json') == NATIVE_RECEIPT_SHA, 'PR3734 native receipt pin')
    native, cert, ext = load_native(args.legacy)
    out = {'status': 'PARTIAL', 'python': platform.python_version(), 'providers': {}}
    args.out.mkdir(exist_ok=True)
    for name, item in receipt['providers'].items():
        loc = args.inputs/'native-cache'/item['word_sha256']/'local'
        for basename in ('CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json'):
            need(digest(loc/basename) == item['complete_native_files']['local/'+basename], 'native cache source pin '+basename)
        word, programs = [read(loc/f) for f in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz')]
        R, K, P, J, clean, dirty = clean_reconstruction(word, programs)
        A = []
        for k, p in zip(K, P):
            row = {j: -a for j, a in k.items()}
            add(row, p, Q(12))
            A.append(row)
        need(matmul(R, A) == [{k: Q(-2)} for k in range(8)], 'RA=-2I')
        G = matmul(A, R)
        for p, row in enumerate(G):
            add(row, {p: Q(1)})
        C = [{j: 12*a for j, a in row.items()} for row in matmul(P, R)]
        need(matmul(G, G) == [{p: Q(1)} for p in range(112)], 'involution')
        actual_c = matmul(J, G)
        for p, row in enumerate(actual_c):
            add(row, {p: Q(1)}, Q(-1))
        need(actual_c == C, 'sparse target repair')
        changed = {}
        profiles, bills, prefixes = {}, {}, {}
        for orientation in ('forward', 'backward'):
            back = orientation == 'backward'
            code = source_code(R, A, 112 if back else 0, 0 if back else 1)
            patch = repair(C, word, back)
            core_profile = core_frame_check(word, clean[orientation])
            boundary_check(dirty[orientation], word, back, 'dirty')
            boundary_check(code, word, back, 'code')
            boundary_check(patch, word, back, 'repair')
            profile = Counter(core_profile)+Counter({1:8})
            need(profile == Counter({1:2448,2:725,3:224,4:102,5:20}), 'conditional local native profile')
            profiles[orientation] = dict(sorted(profile.items()))
            changed[orientation] = patch + code + clean[orientation] if back else clean[orientation] + code + patch
            final = replay(changed[orientation])
            for p in range(632):
                expected = {(p, ()): Q(1)}
                if back and p < 112:
                    add(expected, {(112+p, ()): Q(-1)})
                elif back and p < 224:
                    expected = {(112+j, ()): a for j, a in G[p-112].items()}
                elif not back and p < 112:
                    expected = {(j, ()): a for j, a in G[p].items()}
                elif not back and p < 224:
                    add(expected, {(j, ()): a for j, a in G[p-112].items()})
                need(final['L', p] == expected, f'changed endpoint {orientation}:{p}')
            need(all(not row for r, row in final.items() if r[0] in 'CZ'), 'private dirty')
            bills[orientation] = scalar_bill(changed[orientation])
            prefixes[orientation] = scalar_prefix(changed[orientation])
            missing = [e for e in patch if e[0] != 'intrinsic_line']
            try:
                boundary_check(missing,word,back,'repair')
            except ValueError:
                pass
            else:
                need(False, 'missing intrinsic-line mutation accepted')
        encoded = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
        (args.out/f'PROGRAMS-{name}.json.gz').write_bytes(gzip.compress(encoded, mtime=0))
        lowering = []
        for sign, records in ((1,cert['input_recipes']),(-1,ext['inverse_exit_recipes'])):
            for record in records:
                p = record['port']
                recipe = record['recipe']
                lowering.append({'port':p, 'label':word['ports'][p], 'sign':sign, 'owned_register':['C',0], 'from_boundary':'I' if sign == 1 else 'FULL', 'to_boundary':'C_q' if sign == 1 else 'FULL C_q^-1', 'rank':1,
                    'operations_in_execution_order':[
                        {'kind':'native_monomial','record':recipe['right']},
                        {'kind':'native_C_child','rank':1,'axes':[1]},
                        {'kind':'native_monomial','record':recipe['left']},
                    ]})
        (args.out/f'NATIVE-LINE-LOWERING-{name}.json').write_text(json.dumps(lowering,indent=2)+'\n')
        out['providers'][name] = {'word_sha256': item['word_sha256'], 'program_sha256': digest(loc/'LOCAL-PROGRAMS.json.gz'), 'changed_payload_sha256': sha256(encoded).hexdigest(), 'dirty_compensation_adds': sum(e[0]=='scalar' and e[1][0]=='add' for e in dirty['forward']), 'source_adds': sum(e[0]=='scalar' and e[1][0]=='add' for e in source_code(R,A,0,1)), 'repair_adds': sum(e[0]=='scalar' and e[1][0]=='add' for e in repair(C,word,False)), 'input_columns':632, 'arbitrary_helpers_restored':408, 'profiles':profiles, 'scalar_invoice':bills, 'scalar_prefix_bounds':prefixes, 'native_boundary_checks':native_line_checks(word,native,cert,ext)}
        print('PASS_MODERN_INVOLUTION_LOCAL_NATIVE_BOUNDARIES', name,
              'columns=632 helpers=408 zero_buffers=91 native_line_columns=8192 mass=5078 scalar_primitives=179900', flush=True)
    out['status'] = 'PASS_MODERN_INVOLUTION_LOCAL_NATIVE_BOUNDARIES'
    out['inherited_native_scope'] = 'Native cache sources are authenticated and all changed persistent event/frame chronology is independently replayed. Existing Clifford/warp/residual recipe mathematical certificates are retained, not freshly regenerated. The 16 added positive/inverse line recipes are freshly checked on all 8192 Gaussian columns and composed at the actual modern boundary.'
    out['remaining_obligations'] = ['routed controller and terminal decoder', 'complete helper ownership and hosting for changed consumer', 'full precision/tape/address cost and all-size supplier admission']
    out['legacy_sources'] = {f:digest(args.legacy/f) for f in ('native_verify.py','certificate.json','unit-transfer-certificate.json')}
    (args.out/'RESULT.json').write_text(json.dumps(out, indent=2)+'\n')


if __name__ == '__main__':
    main()
