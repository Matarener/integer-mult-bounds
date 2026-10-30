"""Independent small-dimension absolute-phase checks for a native K conjugate.

No large-dimensional state-vector check or supplier theorem is claimed.
"""
from pathlib import Path
from hashlib import sha256
from itertools import product
import importlib.util
import json
import random
import sys

PIN = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
SOURCE = Path(__file__).resolve().parent/'inputs/clifford_exact.py'

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

require(sha256(SOURCE.read_bytes()).hexdigest() == PIN, 'exact Clifford source')
spec = importlib.util.spec_from_file_location('independent_dense_ce', SOURCE)
C = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = C
spec.loader.exec_module(C)

def case(G):
    n = len(G)
    gi = C.inv(G, n)
    columns = C.transpose(gi, n)
    Q = tuple((1 << i) ^ sum(((x & y).bit_count() & 1) << j
                 for j, y in enumerate(columns)) for i, x in enumerate(columns))
    K = C.perm(n, G).then(C.diag(n, Q))
    R = C.fourier(n)
    T = R.adjoint().then(K).then(R)
    require(all(x == 0 for x, z, p in T.tab[n:]), 'conjugate must be monomial')
    d = sum(((x.bit_count() // 2) & 1) << j for j, x in enumerate(columns))
    vec, den = T.zero_state()
    require(den == 0, 'integer anchor denominator')
    expected = [(0, 0)] * (1 << n)
    expected[d] = C.mul_i((1, 0), -d.bit_count())
    require(vec == expected, 'analytic native K anchor differs from independent dense column')
    # The functional phase equation is also checked independently, for every y.
    for y in range(1 << n):
        lhs = (C.mv(gi, y).bit_count() + C.qvalue(Q, tuple((Q[i] >> i) & 1 for i in range(n)), y, n)) % 4
        rhs = (y.bit_count() + 2 * ((d & y).bit_count() & 1)) % 4
        require(lhs == rhs, 'native K quadratic identity')
    return sha256(json.dumps([G, d, vec[d]], separators=(',', ':')).encode()).hexdigest()

out = []
by_n = {}
for n in range(1, 4):
    count = 0
    for G in product(range(1 << n), repeat=n):
        if C.rank(G) == n:
            out.append(case(G))
            count += 1
    by_n[n] = {'all_GL_matrices': count}

rng = random.Random(20261025)
for n in range(4, 9):
    count = 0
    while count < 20:
        G = tuple(rng.randrange(1 << n) for _ in range(n))
        if C.rank(G) == n:
            out.append(case(G))
            count += 1
    by_n[n] = {'seeded_random_GL_matrices': count}

result = {'status': 'PASS', 'exact_clifford_sha256': PIN,
          'coverage': by_n, 'case_count': len(out),
          'case_digest': sha256(''.join(out).encode()).hexdigest(),
          'anchor': 'T|0> = (-i)^wt(d)|d>, d_j=floor(wt(G^-1 e_j)/2) mod 2',
          'T': 'R K R^-1 with K=D_(I+G^-T G^-1) P_G and R=product C_ej',
          'large_dimension_dense_check': False}
print(json.dumps(result, sort_keys=True))
