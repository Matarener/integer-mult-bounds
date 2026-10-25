#!/usr/bin/env python3
"""Exact, source-bound orbit tariff; formal calls, not a native supplier.

Prepared with substantial OpenAI Codex assistance. Standard library only.
"""
import argparse
import copy
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    'frozen/history/DERIVATIVE.md': 'ab4f11141fa44a87ee542056fbc217cdfe0ac059af4f37f8b1b5c850d14b4399',
    'frozen/history/geometry_derivative.py': '009332a9f7aa35d1e7c529531214c0d428e946041ca7fa9a589f56302144ec04',
    'frozen/history/GEOMETRY-DERIVATIVE.json': '7ff46e239a8ffdf2d621cf220aba155cbc5cbec94198de8fb15437278b63fb98',
    'frozen/source/bitE8-r865.json.gz': '1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55',
    'frozen/source/NOTICE.md': '5f4b7fcbf99f572be28b6da612ce775363908cdfc7810f7aca167be01c86e49a',
    'frozen/source/LICENSE': 'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4',
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def gate(ok, label, deleted=()):
    if label not in deleted:
        need(ok, label)


def reject_delete(name, label, probe):
    try:
        probe(())
    except ValueError as exc:
        need(str(exc) == label, 'wrong rejection: ' + name)
    else:
        raise ValueError('mutation survived: ' + name)
    probe((label,))
    return {'name': name, 'rejected_by': label, 'same_guard_deletion_accepts': True}


def captured_history(blobs):
    raw = blobs['frozen/history/geometry_derivative.py']
    source = raw.decode()
    replacements = [
        ("SOURCE = Path('/Users/ross/git/math/integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz')", '# SOURCE bytes captured and authenticated by the adapter.'),
        ("    ap=argparse.ArgumentParser(description=__doc__)\n    ap.add_argument('--write',action='store_true')\n    args=ap.parse_args()\n", ''),
        ("    path=HERE/'GEOMETRY-DERIVATIVE.json'\n    if args.write:\n        path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\\n')\n    else:\n        need(json.loads(path.read_bytes())==out,'complete receipt mismatch')\n    print(out['status'])\n    print('54 root lines, 18 orthogonal triples; orbit-closed B4 nine-call grammar needs at least 12 calls')", '    return out'),
    ]
    for old, new in replacements:
        need(source.count(old) == 1, 'unique historical adaptation')
        source = source.replace(old, new)
    need(source.count('SOURCE.read_bytes()') == 2, 'captured root read count')
    source = source.replace('SOURCE.read_bytes()', 'ROOT_BYTES')
    env = {'__name__': 'captured_geometry', '__file__': str(HERE/'frozen/history/geometry_derivative.py'),
           'ROOT_BYTES': blobs['frozen/source/bitE8-r865.json.gz']}
    exec(compile(source, '<authenticated-geometry-adapter>', 'exec', dont_inherit=True, optimize=0), env)
    actual = env['main']()
    expected = json.loads(blobs['frozen/history/GEOMETRY-DERIVATIVE.json'])
    gate(typed_equal(actual, expected), 'complete historical receipt')
    return env, actual, {'original_sha256': digest(raw), 'executed_sha256': digest(source.encode()),
                         'compile_optimize': 0, 'compile_dont_inherit': True,
                         'replacement_count': 3, 'captured_root_reads': 2}


def rank2(rows):
    pivots = {}
    for row in rows:
        while row:
            k = row.bit_length()-1
            if k in pivots:
                row ^= pivots[k]
            else:
                pivots[k] = row
                break
    return len(pivots)


def shift(g, axis, order):
    step = order**axis
    return g + step if (g//step) % order < order-1 else g-(order-1)*step


def word(B, h):
    n = 6*B+h
    events = []
    for pair in range(B):
        for k in range(3):
            perm = list(range(n))
            inv = list(range(n))
            for bank in range(2):
                base = 6*pair+3*bank
                for j in range(3):
                    perm[base+j] = base+(j+k)%3
                    inv[base+j] = base+(j-k)%3
            if k:
                events.append({'op': 'permute', 'new_row_from_old': perm})
            events.append({'op': 'query', 'pair': pair})
            if k:
                events.append({'op': 'permute', 'new_row_from_old': inv})
    if h:
        # A nontrivial free spectator borrow/return pair supplies a dirt control.
        events.extend([{'op': 'add', 'dst': 6*B, 'src': 0, 'coefficient': 1},
                       {'op': 'add', 'dst': 6*B, 'src': 0, 'coefficient': -1}])
    return events


def ring_word(B, h, events, order=2):
    """Every coefficient in F2[C2^3] or Z[C4^3]; integer C4 is stronger here."""
    n = 6*B+h
    rows = [{(j, 0): 1} for j in range(n)]
    for e in events:
        if e['op'] == 'permute':
            gate(sorted(e['new_row_from_old']) == list(range(n)), 'scalar permutation admission')
            rows = [rows[j].copy() for j in e['new_row_from_old']]
        elif e['op'] == 'query':
            gate(type(e['pair']) is int and 0 <= e['pair'] < B, 'two-bank query admission')
            for j in range(6):
                r = 6*e['pair']+j
                axis = (2, 0, 1)[j%3]
                rows[r] = {(c, shift(g, axis, order)): a for (c, g), a in rows[r].items()}
        elif e['op'] == 'add':
            gate(0 <= e['dst'] < n and 0 <= e['src'] < n and e['dst'] != e['src'], 'scalar shear admission')
            for key, value in rows[e['src']].items():
                new = rows[e['dst']].get(key, 0)+e['coefficient']*value
                if order == 2:
                    new %= 2
                if new:
                    rows[e['dst']][key] = new
                else:
                    rows[e['dst']].pop(key, None)
        else:
            raise ValueError('unknown event')
    return rows


def target(B, h, order):
    t = 1+order+order*order
    return [{(r, t if r < 6*B else 0): 1} for r in range(6*B+h)]


def endpoint(rows, B, h, order, deleted=()):
    wanted = target(B, h, order)
    gate(rows[:6*B] == wanted[:6*B], 'public every-coefficient endpoint', deleted)
    gate(rows[6*B:] == wanted[6*B:], 'dirty spectator every-coefficient endpoint', deleted)


def coefficients(rows, order):
    n = len(rows)
    return [[[rows[r].get((c, g), 0) for c in range(n)] for r in range(n)]
            for g in range(order**3)]


def regular_columns(B, h, events):
    """Independent bit-vector execution of all 8N input columns."""
    n = 6*B+h
    columns = []
    for col in range(8*n):
        state = [0]*n
        state[col//8] = 1 << (col%8)
        for e in events:
            if e['op'] == 'permute':
                state = [state[j] for j in e['new_row_from_old']]
            elif e['op'] == 'query':
                for j in range(6):
                    r = 6*e['pair']+j
                    bit = (4, 1, 2)[j%3]
                    out = 0
                    for g in range(8):
                        if state[r] & (1 << g):
                            out ^= 1 << (g ^ bit)
                    state[r] = out
            else:
                if e['coefficient'] & 1:
                    state[e['dst']] ^= state[e['src']]
        columns.append(sum(v << (8*r) for r, v in enumerate(state)))
    wanted = [1 << (8*(c//8)+((c%8)^7 if c//8 < 6*B else c%8)) for c in range(8*n)]
    gate(columns == wanted, 'independent regular-action columns')
    return columns


def derivative(rows):
    # All y,z go to1, x goes to1+epsilon; a monomial has derivative its x parity.
    result = []
    for row in rows:
        packed = 0
        for (c, g), a in row.items():
            if g & 1 and a & 1:
                packed ^= 1 << c
        result.append(packed)
    return result


def augmentation(rows):
    result = []
    for row in rows:
        value = 0
        for (c, _), a in row.items():
            if a & 1:
                value ^= 1 << c
        result.append(value)
    return result


def binary_product(a, b):
    result = []
    for row in a:
        value = 0
        for j in range(len(b)):
            if row & (1 << j):
                value ^= b[j]
        result.append(value)
    return result


def derivative_replay(B, h, events, expected):
    n = 6*B+h
    zero, first = [1 << j for j in range(n)], [0]*n
    prefixes = []
    paid = 0
    for e in events:
        local = ring_word(B, h, [e])
        a, b = augmentation(local), derivative(local)
        gate(rank2(a) == n, 'invertible scalar specialization')
        gate(rank2(b) == (2 if e['op'] == 'query' else 0), 'literal event derivative rank')
        left, right = binary_product(b, zero), binary_product(a, first)
        first = [x ^ y for x, y in zip(left, right)]
        zero = binary_product(a, zero)
        paid += e['op'] == 'query'
        gate(rank2(first) <= 2*paid, 'telescoping prefix capacity')
        prefixes.append({'paid_queries':paid, 'event_derivative_rank':rank2(b),
                         'prefix_derivative_rank':rank2(first),
                         'prefix_derivative_rows_hex':[hex(v) for v in first]})
    gate(zero == augmentation(expected) and first == derivative(expected), 'independent derivative product rule')
    return prefixes


def homomorphisms():
    binary = []
    for a in range(8):
        for b in range(8):
            # (u,v) denotes u+epsilon*v; every group basis element has u=1.
            product = (1, (a & 1) ^ (b & 1))
            expected = (1, (a ^ b) & 1)
            gate(product == expected, 'dual-number multiplication homomorphism')
            binary.append([a,b,a^b,list(product)])
    gaussian = []
    powers = [(1,0),(0,1),(-1,0),(0,-1)]
    for a in range(64):
        for b in range(64):
            c = sum((((a//(4**k))%4+(b//(4**k))%4)%4)*(4**k) for k in range(3))
            product = gmul(powers[a%4], powers[b%4])
            gate(product == powers[c%4], 'C4 finite-evaluation homomorphism')
            gaussian.append([a,b,c,list(product)])
    return {'F2_dual_number_all_64_basis_products':binary,
            'C4_i_evaluation_all_4096_basis_products':gaussian}


def local_capacity(rows, deleted=()):
    gate(rank2(derivative(rows)) <= 2, 'local first-order capacity', deleted)


def gadd(a, b):
    return (a[0]+b[0], a[1]+b[1])


def gmul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def gdiv(a, b):
    d = b[0]*b[0]+b[1]*b[1]
    return (Fraction(a[0]*b[0]+a[1]*b[1], d), Fraction(a[1]*b[0]-a[0]*b[1], d))


def grank(matrix):
    a = [[(Fraction(x), Fraction(y)) for x, y in row] for row in matrix]
    rank = 0
    for c in range(len(a[0])):
        k = next((r for r in range(rank, len(a)) if a[r][c] != (0, 0)), None)
        if k is None:
            continue
        a[rank], a[k] = a[k], a[rank]
        pivot = a[rank][c]
        a[rank] = [gdiv(v, pivot) for v in a[rank]]
        for r in range(len(a)):
            if r != rank and a[r][c] != (0, 0):
                scale = a[r][c]
                a[r] = [gadd(v, tuple(-z for z in gmul(scale, w))) for v, w in zip(a[r], a[rank])]
        rank += 1
    return rank


def gaussian_word(B, h, events, phase, cover=False):
    n = 6*B+h
    width = 3 if cover else 1
    rows = [[(int(r == c), 0) for c in range(width*n)] for r in range(width*n)]
    for e in events:
        if e['op'] == 'permute':
            rows = [rows[width*j+k][:] for j in e['new_row_from_old'] for k in range(width)]
        elif e['op'] == 'query':
            for j in range(6):
                r = 6*e['pair']+j
                axis = (2, 0, 1)[j%3]
                for k in range(width):
                    factor = phase if (k == axis if cover else axis == 0) else (1, 0)
                    rows[width*r+k] = [gmul(factor, v) for v in rows[width*r+k]]
        else:
            for k in range(width):
                dst, src = width*e['dst']+k, width*e['src']+k
                rows[dst] = [gadd(a, (e['coefficient']*b[0], e['coefficient']*b[1]))
                             for a, b in zip(rows[dst], rows[src])]
    return rows


def gaussian_endpoint(rows, B, h, phase, cover=False, deleted=()):
    width = 3 if cover else 1
    n = width*(6*B+h)
    expected = [[phase if r == c and r < width*6*B else (1, 0) if r == c else (0, 0)
                 for c in range(n)] for r in range(n)]
    gate(rows == expected, 'finite complex full endpoint', deleted)


def difference(a, b):
    return [[gadd(x, (-y[0], -y[1])) for x, y in zip(r, s)] for r, s in zip(a, b)]


def cover_covariance(perm, deleted=()):
    # O e_j=e_(j+1); conjugation moves the unique nontrivial diagonal entry.
    need(sorted(perm) == [0, 1, 2], 'cover permutation admission')
    diagonals = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    actual = []
    for d in diagonals:
        a = [0]*3
        for j in range(3):
            a[perm[j]] = d[j]
        actual.append(a)
    gate(actual == [list(diagonals[1]), list(diagonals[2]), list(diagonals[0])], 'C3 covariance', deleted)
    return actual


def run():
    blobs = {p: (HERE/p).read_bytes() for p in PINS}
    for p, b in blobs.items():
        need(digest(b) == PINS[p], 'authenticated input: '+p)
    inventory = json.loads((HERE/'INPUTS.json').read_bytes())
    need(len(inventory['files']) == len(PINS), 'source inventory cardinality')
    need({x['path']: x['sha256'] for x in inventory['files']} == PINS, 'source inventory closure')
    for entry in inventory['files']:
        data = blobs[entry['path']]
        need(entry['bytes'] == len(data), 'source inventory byte count')
        if entry['path'].endswith('.gz'):
            raw = gzip.decompress(data)
            need(entry['raw_bytes'] == len(raw) and entry['raw_sha256'] == digest(raw), 'source raw transport closure')
    env, old, adaptation = captured_history(blobs)
    maps = homomorphisms()
    controls = []
    wrong = copy.deepcopy(old)
    wrong['orthogonal_orbits'] = True
    controls.append(reject_delete('typed_historical_count', 'complete historical receipt',
        lambda d: gate(typed_equal(old, wrong), 'complete historical receipt', d)))
    roots = sorted({env['canon'](p) for p in json.loads(gzip.decompress(blobs['frozen/source/bitE8-r865.json.gz']))['lines']})
    def geometry_gate(rot, deleted=()):
        gate(all(env['canon'](rot(p)) in roots and rot(rot(rot(p))) == p for p in roots), 'order3 root automorphism', deleted)
    geometry_gate(env['rotate'])
    controls.append(reject_delete('wrong_chart_rotation', 'order3 root automorphism',
        lambda d: geometry_gate(lambda p: (p[2],p[0],p[1],p[5],p[3],p[4],p[6],p[7]), d)))
    finite = []
    for B in (1, 2, 4):
        for h in (0, 1, 3):
            events = word(B, h)
            rows = ring_word(B, h, events)
            rows4 = ring_word(B, h, events, 4)
            endpoint(rows, B, h, 2)
            endpoint(rows4, B, h, 4)
            regular = regular_columns(B, h, events)
            gate(sum(e['op'] == 'query' for e in events) == 3*B, 'sharp query invoice')
            local = ring_word(B, h, [{'op':'query', 'pair':0}])
            local_capacity(local)
            derivative_prefixes = derivative_replay(B, h, events, rows)
            target_rank = rank2(derivative(rows))
            gate(target_rank == 6*B, 'restored target derivative rank')
            g0 = gaussian_word(B, h, events, (1,0))
            gi = gaussian_word(B, h, events, (0,1))
            gaussian_endpoint(g0, B, h, (1,0))
            gaussian_endpoint(gi, B, h, (0,1))
            complex_rank = grank(difference(gi, g0))
            gate(complex_rank == 6*B, 'complex target variation rank')
            local0 = gaussian_word(B,h,[{'op':'query','pair':0}],(1,0))
            locali = gaussian_word(B,h,[{'op':'query','pair':0}],(0,1))
            local_complex_rank = grank(difference(locali,local0))
            gate(local_complex_rank == 2, 'complex local variation rank')
            finite.append({'B': B, 'dirty_scalar_spectators': h, 'ordinary_column_order': list(range(6*B+h)),
                'events': events, 'paid_calls': 3*B, 'F2_all_8_coefficient_matrices': coefficients(rows, 2),
                'Z_C4_all_64_coefficient_matrices': coefficients(rows4, 4),
                'regular_action_column_order': [[r,g] for r in range(6*B+h) for g in range(8)],
                'regular_action_all_columns_hex': [hex(v) for v in regular],
                'derivative_rows_hex': [hex(v) for v in derivative(rows)], 'derivative_rank': target_rank,
                'literal_product_rule_prefixes':derivative_prefixes,
                'complex_evaluation_one': g0, 'complex_evaluation_i': gi,
                'complex_local_evaluation_one':local0,'complex_local_evaluation_i':locali,
                'complex_local_variation_rank':local_complex_rank,'complex_difference_rank': complex_rank})
            removed = copy.deepcopy(events)
            del removed[next(i for i,e in enumerate(removed) if e['op']=='query')]
            bad = ring_word(B, h, removed)
            controls.append(reject_delete('omit_query_B%d_h%d'%(B,h), 'public every-coefficient endpoint',
                lambda d, bad=bad, B=B, h=h: endpoint(bad, B, h, 2, d)))
            if h:
                bad = ring_word(B, h, events[:-1])
                controls.append(reject_delete('omit_dirty_return_B%d_h%d'%(B,h), 'dirty spectator every-coefficient endpoint',
                    lambda d, bad=bad, B=B, h=h: endpoint(bad, B, h, 2, d)))
    # Genuine full-common query exceeds the local alphabet capacity.
    controls.append(reject_delete('admit_paid_full_common_gate', 'local first-order capacity',
        lambda d: local_capacity(target(4, 3, 2), d)))
    bad_events = word(1, 1)
    # Replace a cyclic conjugation by identity; this preserves scalar invertibility.
    q = next(i for i,e in enumerate(bad_events) if e['op']=='permute')
    bad_events[q]['new_row_from_old'] = list(range(7))
    bad = ring_word(1, 1, bad_events)
    controls.append(reject_delete('wrong_cyclic_bridge', 'public every-coefficient endpoint',
        lambda d: endpoint(bad, 1, 1, 2, d)))
    controls.append(reject_delete('complex_phase_reversal', 'finite complex full endpoint',
        lambda d: gaussian_endpoint(gaussian_word(1, 1, word(1,1), (0,-1)), 1, 1, (0,1), False, d)))
    covariance = cover_covariance([1,2,0])
    controls.append(reject_delete('inverse_C3_covariance', 'C3 covariance',
        lambda d: cover_covariance([2,0,1], d)))
    cover_records = []
    for B in (1,2,4):
        h = 1
        events = word(B,h)
        one = gaussian_word(B,h,events,(1,0),True)
        imag = gaussian_word(B,h,events,(0,1),True)
        gaussian_endpoint(one,B,h,(1,0),True)
        gaussian_endpoint(imag,B,h,(0,1),True)
        local_one = gaussian_word(B,h,[{'op':'query','pair':0}],(1,0),True)
        local_i = gaussian_word(B,h,[{'op':'query','pair':0}],(0,1),True)
        local_rank = grank(difference(local_i,local_one))
        full_rank = grank(difference(imag,one))
        gate(local_rank == 6 and full_rank == 18*B, 'regular-cover variation ranks')
        derivative_cover = [0]*(3*(6*B+h))
        for j in range(6):
            r = 3*j+(2,0,1)[j%3]
            derivative_cover[r] = 1 << r
        gate(rank2(derivative_cover) == 6, 'BIT regular-cover local derivative')
        cover_records.append({'B':B,'dirty_scalar_spectators':h,'cover_dimension':3,
            'local_one':local_one,'local_i':local_i,'target_one':one,'target_i':imag,
            'local_variation_rank':local_rank,'target_variation_rank':full_rank,
            'BIT_local_derivative_rows_hex':[hex(r) for r in derivative_cover]})
    need(len(controls) == 21, 'complete semantic control census')
    return {'status':'PASS_SCOPED_SHARP_ORBIT_TARIFF', 'schema':1,
        'source_inventory':inventory, 'historical_adaptation':adaptation, 'complete_original_receipt':old,
        'specialization_homomorphisms':maps,
        'finite_cases':finite,'C3_covariance_images':covariance,'regular_cover_cases':cover_records,
        'semantic_controls':controls,'control_count':len(controls),'same_guard_deletion_count':len(controls),
        'theorem_domain':{'B':'every integer B>=1','h':'every finite integer h>=0',
            'f':'every f>=1 for the independent tensor-generator formal lift in PROOF.md',
            'alphabet':'constant invertible scalar bridges; local two-bank diag(z,x,y)',
            'target':'diag(xyz I_(6B), I_h), optionally multiplied by constant invertibles',
            'sharp_paid_query_calls':'3B','physical_supplier_admission':False,'new_kappa':False}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    need(args.output.is_absolute(), 'output must be absolute')
    need(not args.output.is_symlink(), 'output must not be a symlink')
    path = args.output.resolve()
    need(not path.is_relative_to(HERE), 'output must be external to package')
    need(not path.exists(), 'output must be new')
    result = run()
    raw = json.dumps(result,sort_keys=True,indent=2)+'\n'
    data = gzip.compress(raw.encode(),mtime=0) if path.suffix == '.gz' else raw.encode()
    with path.open('xb') as out:
        out.write(data)
    print('PASS: 9 full group-ring cases, 3 regular-cover cases; 21 defects and 21 guard deletions')


if __name__ == '__main__':
    main()
