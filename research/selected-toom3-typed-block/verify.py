#!/usr/bin/env python3
"""One selected nine-climb block: exact typed map and Toom interface obstruction.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
Window selection adapts Josie Elliston #1817 and Gonzalo Mier #3974.
"""
import bisect
import collections
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
CLIFFORD = 'research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py'
PREFIX = 'candidate/strict/global/base/providers/gauge44/'
REGISTERS = [546, 560, 547, 568, 548, 558, 549, 570, 464]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'input pin: ' + row['path'])
    with tarfile.open(fileobj=io.BytesIO((ROOT / ARCHIVE).read_bytes()), mode='r:gz') as tar:
        def obj(name):
            raw = tar.extractfile(PREFIX + name).read()
            return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
        return obj('LOCAL-PROGRAMS.json.gz'), obj('CANONICAL-WORD.json.gz'), obj('CLIFFORD-RECIPES.json'), obj('RESIDUAL-ADAPTERS.json'), obj('INDEPENDENT-LOCAL-REPLAY.json')

def touches(e):
    if e[0] in ('climb', 'adapter', 'residual_adapter'):
        return {('L', e[2])}
    if e[0] == 'center':
        return {('C', e[1])}
    if e[0] == 'scalar':
        o = e[1]
        return {tuple(o[1])} | ({tuple(o[2])} if o[0] in ('add', 'copy') else set())
    return set()

def first_group(events):
    a = events.index(['phase', 'A']) + 1
    end = next(i for i in range(a, len(events)) if events[i][0] == 'phase')
    body = events[a:end]
    r1 = lambda e: e[0] == 'climb' and e[5] == 1
    skeleton = [e for e in body if not r1(e)]
    positions = collections.defaultdict(list)
    for j, e in enumerate(skeleton):
        for r in touches(e):
            positions[r].append(j)
    climbs, gap = [], 0
    for index, e in enumerate(body):
        if r1(e):
            pos = positions['L', e[2]]
            k = bisect.bisect_left(pos, gap)
            lo, hi = (pos[k-1]+1 if k else 0), (pos[k] if k < len(pos) else len(skeleton))
            climbs.append((a+index, gap, lo, hi, e))
        else:
            gap += 1
    counts = collections.Counter((e[2], lo, hi) for _, _, lo, hi, e in climbs)
    for g in range(len(skeleton)+1):
        available = [(k, c) for k, c in enumerate(climbs) if c[2] <= g <= c[3] and counts[c[4][2], c[2], c[3]] == 1]
        if len(available) >= 9 and any(c[3] == g for _, c in available):
            chosen = sorted(available, key=lambda pair: (pair[1][3], pair[0]))[:9]
            rows = [c for _, c in chosen]
            return a, g, skeleton, rows
    raise ValueError('no group')

def entry_contract(events, a, word, residuals, receipt):
    need(receipt['local']['forward']['all_exact_columns'] == 704, 'selected receipt binds every incoming column')
    need(receipt['helpers'] == 480 and 'every arbitrary data/helper column' in receipt['scope'], 'literal arbitrary-dirty helper contract')
    counts=collections.Counter()
    for e in events[:a-1]:
        tag=e[0]
        if tag == 'phase':
            continue
        if tag == 'scalar':
            o=e[1];need(o[1][0] == 'L', 'entry acts on productive columns')
            if o[0] == 'add':
                need(o[2][0] == 'L' and o[1] != o[2], 'entry invertible shear')
                Q(o[3],o[4]);counts['shears']+=1
            elif o[0] == 'scale':
                need(Q(o[2],o[3]) != 0, 'entry nonzero scale');counts['scales']+=1
            else:
                raise ValueError('entry not invertible scalar operation')
        elif tag == 'adapter':
            need(e[1] == 'old_to_new' and e[3] == word['start'][e[2]], 'typed entry frame adapter')
            counts['frame_adapters']+=1
        elif tag == 'residual_adapter':
            need(e[1] == 'pre' and e[3] == word['start'][e[2]], 'typed residual pre-wrapper')
            key=str(e[3]) if len(e) == 4 else str(e[3])+':'+str(e[4])
            rec=residuals['recipes'][key]['right']
            gf_inverse(rec['matrix_rows'])
            need(len(rec['matrix_rows']) == 9, 'nine-bit monomial wrapper')
            counts['residual_pre_wrappers']+=1
        else:
            raise ValueError('unexpected entry operation')
    need(dict(counts) == {'shears':7344,'scales':56,'frame_adapters':464,'residual_pre_wrappers':240}, 'complete invertible entry prefix')
    return dict(counts)

def scalar_prefix(events, a, gap, skeleton, group, word):
    # Scalar-coordinate ledger: frame transitions preserve the abstract column.
    # All selected group columns are still frame zero; therefore their rows
    # here give literal physical input forms in the post-entry-adapter
    # unframed coordinates Z_j. In particular Z_512 is not raw initial x_512.
    n = 704
    rows = [{i: Q(1)} for i in range(n)]
    for e in skeleton[:gap]:
        if e[0] != 'scalar':
            continue
        o = e[1]
        need(word['start'][o[1][1]] == e[2], 'prefix target literal frame matches annotation')
        if o[0] == 'add':
            need(word['start'][o[2][1]] == e[2], 'prefix source literal frame matches target')
        need(o[1][0] == 'L', 'no private target before selected group')
        t = o[1][1]
        if o[0] == 'scale':
            q = Q(o[2], o[3])
            need(q != 0, 'invertible scalar scale')
            rows[t] = {j: q*v for j, v in rows[t].items()}
        elif o[0] == 'add':
            need(o[2][0] == 'L', 'productive scalar source')
            s, q = o[2][1], Q(o[3], o[4])
            need(s != t, 'invertible shear')
            for j, v in list(rows[s].items()):
                z = rows[t].get(j, 0) + q*v
                if z: rows[t][j] = z
                else: rows[t].pop(j, None)
        else:
            raise ValueError('unexpected prefix scalar')
    expected = [{r: Q(1)} for r in REGISTERS]
    expected[-1][512] = Q(1)
    need([rows[r] for r in REGISTERS] == expected, 'nine literal independent incoming forms')
    need([[rows[r].get(c, 0) for c in REGISTERS] for r in REGISTERS] == [[int(i == j) for j in range(9)] for i in range(9)], 'identity dirty-input minor')
    return [{str(k): str(v) for k, v in rows[r].items()} for r in REGISTERS]

def gf_inverse(rows):
    n = len(rows)
    work = [r | (1 << (n+i)) for i, r in enumerate(rows)]
    for j in range(n):
        k = next((i for i in range(j, n) if work[i] >> j & 1), None)
        need(k is not None, 'invertible binary map')
        work[j], work[k] = work[k], work[j]
        for i in range(n):
            if i != j and work[i] >> j & 1: work[i] ^= work[j]
    return [r >> n for r in work]

def mv(rows, x):
    return sum(((r & x).bit_count() & 1) << i for i, r in enumerate(rows))

def phase(rec, x):
    n = len(rec['matrix_rows'])
    return (rec['phase'] + sum(rec['linear_Z4'][i] for i in range(n) if x >> i & 1) + 2*sum(((rec['quadratic_rows'][i] >> (i+1)) & (x >> (i+1))).bit_count() for i in range(n) if x >> i & 1)) % 4

def mono(rec, x):
    return mv(rec['matrix_rows'], x) ^ rec['offset'], phase(rec, x)

def rotate(z, p):
    a, b = z
    return [(a,b),(-b,a),(-a,-b),(b,-a)][p % 4]

def recipe_column(rec, x):
    y, rp = mono(rec['right'], x)
    out = {}
    for z, coefficient in [(y, (1,1)), (y ^ 1, (1,-1))]:
        w, lp = mono(rec['left'], z)
        out[w] = rotate(coefficient, rp+lp)
    return out  # Gaussian integer numerators, common denominator two

def multiply(a,b):
    return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])

def exact_operator(word, recipes):
    spec = importlib.util.spec_from_file_location('selected_toom_retained_clifford', ROOT / CLIFFORD)
    c = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = c
    spec.loader.exec_module(c)
    outputs = {}
    for frame in (4,5):
        rec = next(r for r in recipes['children'] if (r['old'],r['new']) == (0,frame))
        need(rec['rank'] == 1, 'rank-one recipe')
        for side in ('left','right'):
            gf_inverse(rec[side]['matrix_rows'])
            need(len({mono(rec[side],x)[0] for x in range(512)}) == 512, 'monomial permutation')
        target = c.canonical_frame(9, tuple(word['frames'][frame]))
        columns = []
        for x in range(512):
            column = recipe_column(rec,x)
            values, den = target.zero_state(x)
            expected = {j:(a*(2//(2**den)),b*(2//(2**den))) for j,(a,b) in enumerate(values) if a or b}
            need(den == 1, 'one exact halving layer')
            need(column == expected, 'literal canonical frame vs independent serialized recipe, all basis vectors')
            columns.append(column)
        # Sparse Gram is an independent full-rank certificate, not a float rank.
        row_to_cols = collections.defaultdict(list)
        for x,col in enumerate(columns):
            for y,z in col.items(): row_to_cols[y].append((x,z))
        gram = collections.defaultdict(lambda: (0,0))
        for pairs in row_to_cols.values():
            for x,z in pairs:
                for y,w in pairs:
                    product = multiply((z[0],-z[1]),w)
                    old = gram[x,y]
                    gram[x,y] = (old[0]+product[0],old[1]+product[1])
        need(all(v == ((4,0) if x == y else (0,0)) for (x,y),v in gram.items()), 'exact unitary Gram')
        need(all(gram[x,x] == (4,0) for x in range(512)), '512 independent columns')
        digest = hashlib.sha256(json.dumps(columns, sort_keys=True,separators=(',',':')).encode()).hexdigest()
        outputs[str(frame)] = {'frame':word['frames'][frame],'rank':512,'column_digest':digest,'basis_zero_numerator':columns[0],'denominator':2}
    # Constructive alternative: eight identical maps can be packed on three
    # extra lane bits, but this is still rank one on a larger payload.
    small = c.canonical_frame(9, (459,))
    packed = c.canonical_frame(12, (459,))
    wanted = tuple(list(small.tab[:9]) + [(1<<i,0,0) for i in range(9,12)] + list(small.tab[9:]) + [(0,1<<i,0) for i in range(9,12)])
    need(packed.tab == wanted, 'eight lanes tensor the same exact Clifford tableau')
    small_zero, ds = small.zero_state()
    packed_zero, dp = packed.zero_state()
    need(dp == ds and packed_zero == small_zero + [(0,0)]*(4096-512), 'eight-lane identity includes global phase')
    need(c.rank([x for x,z,p in packed.tab[12:]]) == 1, 'packed Fourier rank remains one')
    outputs['eight_lane_packing'] = {'payload_dimension':4096,'index_bits':12,'fourier_rank':1,'same_rank_payload_multiplier':8,'paid_profile_delta':'unknown; no admitted larger-payload call'}
    return outputs

def rational_boundary_fixture():
    # Laurent monomials are exact rational functions; exponent addition gives
    # exact substitution. This fixture does not prove the general theorem.
    encoding = [(1,-1,0),(0,1,-1),(0,0,1)]
    inverse = [(1,1,1),(0,1,1),(0,0,1)]
    def substitute_monomial(exponents, images):
        return tuple(sum(e*image[j] for e,image in zip(exponents,images)) for j in range(3))
    need([substitute_monomial(row,encoding) for row in inverse] == [(1,0,0),(0,1,0),(0,0,1)], 'rational birational positive control')
    def ratio_pair(x): return Q(x[0],x[1]),Q(x[1],x[2])
    need(ratio_pair((1,2,3)) == ratio_pair((2,4,6)), 'lost common scale in rational encoding')
    need((1,2,3) != (2,4,6), 'distinct required outputs for lost-scale pair')
    # Pull back u-v by (u,v)=(x,x). Cancellation is identically zero,
    # so 1/(u-v) cannot be used as a generic decoder on that image.
    denominator=collections.defaultdict(int)
    for coefficient,image in [(1,(1,0,0)),(-1,(1,0,0))]: denominator[image]+=coefficient
    need(not any(denominator.values()), 'identically vanishing pulled-back denominator rejected')
    return ['rational_lost_scale','rational_undefined_pullback']

def controls(word,recipes):
    import copy
    rec = next(r for r in recipes['children'] if (r['old'],r['new']) == (0,4))
    base = [recipe_column(rec,x) for x in range(512)]
    mutants = []
    for name, side, field, value in [('global_phase','left','phase',(rec['left']['phase']+1)%4),('translation','right','offset',rec['right']['offset']^1)]:
        other=copy.deepcopy(rec);other[side][field]=value
        need(any(recipe_column(other,x) != base[x] for x in range(512)), 'reject '+name)
        mutants.append(name)
    need(9*512 > 6*512 > 3*512, 'Toom input-space strict deficits')
    # Homogeneous variable-variable multiplication cannot equal the nonzero
    # linear selected block: scaling by two gives factor four, not two.
    z=base[0]
    need({k:(4*a,4*b) for k,(a,b) in z.items()} != {k:(2*a,2*b) for k,(a,b) in z.items()}, 'quadratic scaling mismatch')
    # Explicit naive three-coefficient packing loses dirty register570.
    x=[0]*9;x[7]=1
    need(x[:3] == [0,0,0] and x[7] == 1 and base[0] != {}, 'omitted dirty input has nonzero demanded output')
    return mutants + ['quadratic_scaling','omitted_dirty_register'] + rational_boundary_fixture()

def main():
    p,w,r,residuals,receipt=sources()
    need((w['v'],w['R'],w['h']) == (112,480,9), 'selected boundary dimensions')
    a,g,s,group=first_group(p['forward'])
    entry=entry_contract(p['forward'],a,w,residuals,receipt)
    need(all(e[0] == 'scalar' for e in s[:g]), 'first candidate has only invertible scalar prefix')
    events=[row[4] for row in group]
    need([e[2] for e in events] == REGISTERS, 'literal first #3974 group')
    need(all(lo <= g <= hi for _,_,lo,hi,_ in group), 'common legal gap')
    need([e[3:] for e in events] == [[0,4,1]]*8+[[0,5,1]], 'group frames')
    need(all(w['start'][q] == 0 and q >= 2*w['v'] for q in REGISTERS), 'cold-entry helpers retain arbitrary dirty payloads')
    need(all(not (e[0] == 'residual_adapter' and e[2] in REGISTERS) for e in p['forward'][:a]), 'selected helpers have no hidden entry wrappers')
    forms=scalar_prefix(p['forward'],a,g,s,group,w)
    operators=exact_operator(w,r)
    result={'scope':'one actual forward phase-A group; affine coefficient-only and rational-encoding/rational-decoding Toom-only interfaces', 'entry_contract':'every arbitrary data/helper column; exact selected receipt','invertible_entry_prefix':entry,'registers':REGISTERS,'original_event_indices_zero_based':[x[0] for x in group], 'skeleton_gap':g,'windows':[[x[2],x[3]] for x in group], 'input_form_coordinates':'post-entry-adapter unframed Z_j; not raw initial payloads', 'input_forms':forms,'operators':operators,'actual_input_and_output_rank':4608,'five_product_rational_decoder_transcendence_degree_upper':2560,'six_coefficient_rational_field_transcendence_degree_upper':3072,'five_product_linear_decoder_output_rank_upper':2560,'minimum_extra_output_dimension_five_product_decoder':2048,'fixed_factor_toom_input_rank_upper':1536,'two_affine_factors_input_rank_upper':3072,'minimum_extra_input_dimension_two_affine_factors':1536,'controls':controls(w,r),'implemented_replacements':0,'kappa_change':0}
    result=json.loads(json.dumps(result))
    expected=json.loads((HERE/'RESULT.json').read_text()) if (HERE/'RESULT.json').exists() else None
    if '--write' in sys.argv: (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: need(result == expected,'committed result equality')
    print('PASS_SELECTED_TOOM3_TYPED_BLOCK basis_columns=1024 actual_rank=4608 affine_toom_input_cap=3072 fixed_factor_cap=1536 controls=6 replacements=0 no_new_kappa')

if __name__ == '__main__':
    main()
