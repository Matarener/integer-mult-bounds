"""Source-bound conditional caller composition. Apache-2.0; Codex assistance."""
from pathlib import Path
import contextlib
import hashlib
import io
import itertools as it
import json

P = Path(__file__).resolve().parent
R = P.parent.parent
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
RULES = ('rank6_29', 'rank5_47', 'six_support20_30', 'beta7p2', 'common23', 'common24')
SOURCE_DIGEST = '16c1e48186e42951b1ec39a79b51b637a9b5c064bb446e318807e3c695d57815'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    raw = (P / 'SOURCES.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_DIGEST, 'source inventory changed')
    src = json.loads(raw)
    for rec in src['files'] + src['retained_files']:
        if rec['usage'] == 'provenance':
            continue  # Registered metadata verifies historical Git provenance.
        path = (P if rec in src['retained_files'] else R) / rec['path']
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == rec['sha256'], 'changed input: ' + rec['path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == rec['git_blob'], 'changed Git blob: ' + rec['path'])
    return SOURCE_DIGEST


def domain(t):
    return [w for n in range(5, 6 + t) for w in it.combinations_with_replacement(range(2, 8), n)]


def historical(w):
    require(tuple(sorted(w)) == tuple(w) and all(type(x) is int and x in CAP for x in w), 'invalid weights')
    if sum(x - 2 for x in w) >= 30:
        return False
    for k in range(1, 6):
        keep = w[:len(w) - 5 + k]
        g = sum(CAP[x] for x in keep)
        t = sum(32 if x == 7 else CAP[x] for x in keep)
        if k == 1 and g < 73 and t < 53 or k == 2 and g < 82 and t < 78:
            return False
        if k >= 3 and g < {3: 92, 4: 100, 5: 106}[k]:
            return False
    basis = w[:len(w) - 5]
    if sum(CAP[x] for x in basis) < 53:
        if sum(basis) <= 7:
            return False
        for bits in range(1 << len(basis)):
            a = sum(x for j, x in enumerate(basis) if bits >> j & 1)
            if a <= 6 and sum(basis) - a <= 6:
                return False
    return True


def attempt(w, rule):
    n = len(w)
    successes = []
    feasible_caps = []
    if rule in ('rank6_29', 'rank5_47', 'six_support20_30'):
        m, rank, bound = {'rank6_29': (3, 6, 29), 'rank5_47': (3, 5, 47), 'six_support20_30': (6, 6, 30)}[rule]
        for endpoints in it.combinations(range(n), m):
            if any(w[i] > rank for i in endpoints):
                continue
            for small in it.combinations([i for i in range(n) if i not in endpoints], n - 6):
                cap = sum(CAP[w[i]] for i in small)
                feasible_caps.append(cap)
                if cap <= bound:
                    successes.append({'endpoints': list(endpoints), 'small': list(small), 'deleted': [i for i in range(n) if i not in endpoints and i not in small], 'common_cap': cap, 'surviving_code_dimension': m - 1})
    else:
        for basis in it.combinations(range(n), n - 5):
            cap = sum(CAP[w[i]] for i in basis)
            feasible_caps.append(cap)
            if cap >= 53:
                continue
            if rule in ('common23', 'common24'):
                if cap <= int(rule[-2:]):
                    successes.append({'basis': list(basis), 'common_cap': cap, 'quotient_dimension': n - 5, 'required_directions': 5})
            else:
                for roles in it.product(range(3), repeat=len(basis)):
                    a = [i for i, role in zip(basis, roles) if role == 0]
                    b = [i for i, role in zip(basis, roles) if role == 1]
                    cut = [i for i, role in zip(basis, roles) if role == 2]
                    if sum(w[i] for i in a) <= 6 and sum(w[i] for i in b) <= 6 and sum(CAP[w[i]] for i in cut) <= 2:
                        successes.append({'basis': list(basis), 'roles': list(roles), 'basis_cap': cap, 'cut_cap': sum(CAP[w[i]] for i in cut), 'required_directions': 5, 'span_bound': 4})
    return {'successful_assignments': len(successes), 'minimum_capacity_sum': min(feasible_caps, default=None), 'witness': successes[0] if successes else None}


def compute():
    authenticate()
    original = {}
    source = R / 'research/p112-b6-t4-reconciliation/vendor/bk2b.py'
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(source.read_bytes(), str(source), 'exec'), original)
    cells = []
    for t in (5, 6):
        candidates = domain(t)
        accepted = [historical(w) for w in candidates]
        old = [sum(x - 2 for x in w) < 30 and original['feasible'](w, 5) and not original['killed'](w, 5) for w in candidates]
        require(accepted == old, 'historical filter disagreement')
        rows = []
        for w, keep in zip(candidates, accepted):
            if not keep:
                continue
            attempts = {rule: attempt(w, rule) for rule in RULES}
            primary = next((r for r in RULES if attempts[r]['successful_assignments']), None)
            rows.append({'weights': list(w), 'strict_excess_deficit': 30 - sum(x - 2 for x in w), 'required_code_dimension': 5, 'attempts': attempts, 'primary': primary})
        cells.append({'cell': [5, t], 'domain_multisets': len(candidates), 'historical_survivors': len(rows), 'certified': sum(row['primary'] is not None for row in rows), 'primary_counts': {rule: sum(row['primary'] == rule for row in rows) for rule in RULES}, 'uncertified': [row['weights'] for row in rows if row['primary'] is None], 'rows': rows})
    require([c['historical_survivors'] for c in cells] == [38, 77], 'historical cells changed')
    require([c['certified'] for c in cells] == [38, 76], 'fixed inventory coverage changed')
    gap = [2] * 5 + [6] + [7] * 5
    require(cells[1]['uncertified'] == [gap], 'wrong inventory gap')
    caps = [sum(CAP[gap[i]] for i in B) for B in it.combinations(range(11), 6)]
    return {'schema': 'p112-b5-caller-inventory/v1', 'source_manifest_sha256': SOURCE_DIGEST, 'conditional_contracts': list(RULES), 'scope': 'Fixed conditional inventory; uncertified does not mean globally open or realizable. Cells are nested, not 115 distinct rows.', 'cells': cells, 'remaining_interface': {'weights': gap, 'piece_dimension': 11, 'required_code_dimension': 5, 'forced_code_dimension': 5, 'forced_quotient_dimension': 6, 'preferred_basis_indices': list(range(6)), 'preferred_basis_cap': 30, 'all_six_piece_subsets': len(caps), 'minimum_six_piece_capacity_sum': min(caps), 'required_independent_rank7_directions': 5, 'actual_union_minimum_claimed': False}}


def main():
    require(compute() == json.loads((P / 'RESULT.json').read_text()), 'committed result disagrees')
    print('PASS_P112_B5_CALLER_INVENTORY 38/38 76/77')


if __name__ == '__main__':
    main()
