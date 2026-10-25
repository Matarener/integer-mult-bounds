"""Independent dyadic chart and packet separation certificates for R437/OQ4.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
The source catalogue is reused; exact determinant and separation checks are new.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def power_two(n):
    return n > 0 and n & (n - 1) == 0

def dyadic(x):
    return power_two(F(x).denominator)

def dyadic_unit(x):
    x = F(x)
    return power_two(abs(x.numerator)) and power_two(x.denominator)

def determinant(matrix):
    """Exact elimination independent of predecessor chart/inverse routines."""
    a = [list(map(F, row)) for row in matrix]
    n, result = len(a), F(1)
    need(all(len(row) == n for row in a), 'square determinant')
    for col in range(n):
        pivot_row = next((i for i in range(col, n) if a[i][col]), None)
        if pivot_row is None:
            return F(0)
        if pivot_row != col:
            a[pivot_row], a[col] = a[col], a[pivot_row]
            result = -result
        pivot = a[col][col]
        result *= pivot
        for i in range(col + 1, n):
            if not a[i][col]:
                continue
            factor = a[i][col] / pivot
            for j in range(col + 1, n):
                if a[col][j]:
                    a[i][j] -= factor * a[col][j]
            a[i][col] = F(0)
    return result

def distinguishing_entry(a, b):
    for i, (ra, rb) in enumerate(zip(a, b)):
        for j, (x, y) in enumerate(zip(ra, rb)):
            if dyadic_unit(x - y):
                return i, j, str(x - y)
    raise ValueError('no universally nonzero dyadic-unit chart witness')

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))

def reconstructed_chart(chart, geometry):
    """Sparse coordinate specification; no catalogue matrix/route functions."""
    entries = {(i, i): F(1) for i in range(64)}
    if chart.kind == 'data' and chart.stage:
        axes = tuple(range(8)) + tuple(range(8 + 7*(chart.stage-1), 8 + 7*chart.stage))
        rho = geometry['ports'][chart.port]['rho15']
        for i, a in enumerate(axes):
            for j, b in enumerate(axes):
                entries[a,b] = F(rho[i][j])
    elif chart.kind == 'family' or chart.kind == 'host' and chart.port >= 0:
        port = geometry['ports'][chart.port]
        for i in range(8):
            entries[i,0] = F(port['q'][i], 2)
            for j in range(1,8):
                entries[i,j] = F(port['complement_columns'][i][j-1])
    else:
        need(chart.kind in ('identity','host','data'), 'known chart label')
    if chart.kind == 'host':
        support, native = set(chart.axes), set(range(8))
        need(len(support) == 8, 'eight owner axes')
        exchanges = dict()
        for a,b in zip(sorted(native-support), sorted(support-native)):
            exchanges[a], exchanges[b] = b,a
        entries = {(i, exchanges.get(j,j)): x for (i,j),x in entries.items()}
    return tuple(tuple(entries.get((i,j),F(0)) for j in range(64)) for i in range(64))

def source_certificate():
    import adapter
    catalogue, topology = adapter.load()
    charts = sorted(catalogue.charts, key=lambda x: canonical(x.key))
    chart_ids = {chart: i for i, chart in enumerate(charts)}
    matrices, determinants, chart_rows = {}, Counter(), []
    for chart in charts:
        matrix = reconstructed_chart(chart, catalogue.geometry)
        need(matrix == catalogue.chart_matrix(chart), 'independent exact chart reconstruction')
        need(all(dyadic(x) for row in matrix for x in row), 'dyadic chart entries')
        det = determinant(matrix)
        need(dyadic_unit(det), 'unit determinant at every odd modulus')
        matrices[chart] = matrix
        determinants[str(det)] += 1
        chart_rows.append([chart.key, str(det)])
    witnesses, difference_counts, stage_counts = [], Counter(), []
    for stage in range(9):
        call = topology.call(stage,0)
        groups = defaultdict(list)
        for role,owner in enumerate(call.owners):
            groups[owner.family].append((role,owner.chart))
        before = len(witnesses)
        for family, roles in sorted(groups.items()):
            for a, (role_a, chart_a) in enumerate(roles):
                for role_b,chart_b in roles[:a]:
                    entry = distinguishing_entry(matrices[chart_a],matrices[chart_b])
                    difference_counts[entry[2]] += 1
                    witnesses.append([stage,family,role_a,role_b,chart_ids[chart_a],chart_ids[chart_b],*entry])
        stage_counts.append(len(witnesses)-before)
        # Check the precise replica reduction, not only an aggregate histogram.
        for replica in range(32):
            other = topology.call(stage,replica)
            need(len(other.owners)==len(call.owners)==659, 'current complete role inventory')
            need(all(o.chart==b.chart and o.family==b.family+888*replica
                     for o,b in zip(other.owners,call.owners)), 'all actual replica owner labels')
    # A source-specific carry control at actual native IDLE27776/chart98.
    idle = catalogue.requests[27776]
    need(idle.kind == 'IDLE' and idle.base.rank == 26 and idle.chart.port == 98,
         'actual rank26 native chart')
    sigma = matrices[idle.chart]
    carry_cases = []
    for q,w in ((3,2),(5,3),(7,4)):
        modulus = q**w
        reduced = tuple(tuple(x.numerator*pow(x.denominator,-1,modulus)%modulus
                              for x in row) for row in sigma)
        low = tuple(tuple(x.numerator*pow(x.denominator,-1,q)%q
                          for x in row) for row in sigma)
        # Raw native identity has zero high digits, but rational chart entries carry.
        high = tuple(tuple((x-y)//q for x,y in zip(a,b)) for a,b in zip(reduced,low))
        need(all((x-y)%q == 0 and 0 <= h < q**(w-1)
                 for a,b,c in zip(reduced,low,high) for x,y,h in zip(a,b,c)),
             'complete canonical raw-to-high quotient')
        nonzero = sum(x != 0 for row in high for x in row)
        need(nonzero > 0, 'low-only chart retag loses actual native carry')
        carry_cases.append({'q':q,'w':w,'nonzero_high_entries':nonzero,
                            'raw_identity_high_zero':True})
    receipt = catalogue.receipt()
    kinds = receipt['request_kinds']
    local_roles = 9*32*659
    idles = kinds['IDLE']*32
    counts = {
        'local_gathers_per_low_class':local_roles,
        'local_scatters_per_low_class':local_roles,
        'local_routes_per_low_class':2*local_roles,
        'idle_gathers_per_low_class':idles,
        'idle_scatters_per_low_class':idles,
        'all_family_scans_per_low_class':2*(local_roles+idles),
    }
    need(receipt['binding_sha256']==adapter.REQUEST_DIGEST,'current complete source binding')
    need(len(charts)==1235 and len(witnesses)==5619,'frozen chart and pair inventory')
    return {
        'status':'PASS_CURRENT_R437_UNIFORM_OWNER_SEPARATION',
        'request_binding_sha256':receipt['binding_sha256'],
        'chart_labels':len(charts),'determinants':dict(sorted(determinants.items())),
        'chart_certificate_sha256':sha256(canonical(chart_rows).encode()).hexdigest(),
        'canonical_same_family_pairs':len(witnesses),'replicated_same_family_pairs':32*len(witnesses),
        'per_stage_pairs':stage_counts,'witness_differences':dict(sorted(difference_counts.items())),
        'witness_sha256':sha256(canonical(witnesses).encode()).hexdigest(),
        'request_kinds':kinds,'complete_transport_counts':counts,
        'actual_native_carry_controls':carry_cases,
        'quantifier':'Every odd prime q, every w>=1, every invertible common low, every high lift; algebraic owner/route interface only.',
        'full_GL64_physical_execution':False,'supplier_admission':False,
    }

def finite_controls():
    identity = ((F(1),F(0)),(F(0),F(1)))
    swap = ((F(0),F(1)),(F(1),F(0)))
    need(determinant(identity)==1 and determinant(swap)==-1,'determinant positive controls')
    rejected = []
    for label, action in [
        ('same_family_duplicate_chart',lambda:distinguishing_entry(identity,identity)),
        ('odd_prime_determinant',lambda:need(dyadic_unit(determinant(((3,0),(0,1)))),'odd determinant rejected')),
        ('odd_denominator',lambda:need(dyadic(F(1,3)),'odd denominator rejected')),
        ('difference_vanishes_mod_3',lambda:distinguishing_entry(identity,((F(4),F(0)),(F(0),F(1))))),
    ]:
        try: action()
        except ValueError: rejected.append(label)
        else: raise ValueError('control accepted: '+label)
    # Disjoint writes into the latest family compose; stale snapshots lose writes.
    original = [0,1,1,0,0,1]
    def scatter(state, index, values):
        result = state[:];result[2*index:2*index+2] = values;return result
    latest = scatter(scatter(original,0,[1,1]),2,[0,0])
    stale = scatter(original,2,[0,0])
    need(latest == [1,1,1,0,0,0] and stale != latest,'stale scatter semantic control')
    rejected.append('stale_scatter_snapshot')
    return rejected

def main():
    result = source_certificate()
    result['controls'] = finite_controls()
    target = HERE/'RESULT.json'
    if '--write' in sys.argv:
        target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(json.loads(target.read_text())==result,'frozen exact transport receipt')
    print(json.dumps(result,sort_keys=True))

if __name__ == '__main__':
    main()
