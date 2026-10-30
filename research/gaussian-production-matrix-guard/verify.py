"""Source-bound finite corroboration; the universal result is in PROOF.md."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        if item['usage'] == 'input':
            need(sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'],
                 'source mismatch: ' + item['path'])


def identities():
    cases = same = wrapped = ties = 0
    for s, t, w in ((8, 9, 2), (13, 14, 2), (11, 13, 3)):
        rho, theta = Q(t, s), Q(t-s, s)
        q = [(2*t*j+s)//(2*s) for j in range(s)]
        beta = [rho*j-q[j] for j in range(s)]
        ties += sum(b == -Q(1, 2) for b in beta)
        for i in range(s):
            for j in range(s):
                if i == j:
                    continue
                delta = j-i
                direct = abs(delta) <= w
                if not direct:
                    delta += -s if delta > 0 else s
                if abs(delta) > w:
                    continue
                argument = (rho*delta+beta[i])**2-beta[j]**2
                need(0 < argument <= (rho*w+Q(1, 2))**2, 'decay argument bound')
                if direct and q[i]-i == q[j]-j:
                    similarity = (beta[j]**2-beta[i]**2)/theta+rho*delta**2
                    need(similarity == argument, 'original-coordinate identity')
                    same += 1
                if not direct:
                    wrapped += 1
                cases += 1
    need(same and wrapped and ties, 'all geometry boundaries present')
    # Dropping a denominator lower bound destroys uniform absolute stability.
    eta, y = Q(1, 1024), Q(1, 1024)
    y_hat = y/1000
    need(y-y_hat < 2*eta and abs(1/y_hat-1/y) > 1000, 'denominator failure control')
    need(Q(1, 4)*Q(1, 8)/Q(1, 2) != Q(1, 8), 'bare kernel failure control')
    need(Q(1, 4)/Q(1, 8) > Q(1, 4)/Q(1, 4), 'ratio is not downward')
    need(Q(round(4*Q(3, 16)), 4) > Q(3, 16), 'nearest rerounding may exceed exact coefficient')
    # Same lifted phase across the physical cut does not license the raw ratio.
    rho, theta = Q(9, 8), Q(1, 8)
    beta_i, beta_j, delta = Q(-1, 8), Q(0), 1
    actual = (rho*delta+beta_i)**2-beta_j**2
    raw_delta = -7
    wrong = (beta_j**2-beta_i**2)/theta+rho*raw_delta**2
    need(actual != wrong, 'physical-period raw-displacement failure control')
    return {'retained_pairs': cases, 'same_cell_pairs': same, 'wrapped_pairs': wrapped,
            'half_ties': ties, 'failure_controls': 5}


def ratio_controls():
    cases = 0
    # Independent exact scalar cubes exercise denominator-sensitive propagation.
    for k in range(1, 6):
        lower = Q(1, 2**k)
        eta = lower/16
        for x in (lower, Q(1, 2), Q(1)):
            for y in (lower, Q(1, 2), Q(1)):
                for g in (Q(0), Q(1, 8), Q(1)):
                    for ex in (Q(0), eta, 3*eta/2):
                        for ey in (Q(0), eta, 3*eta/2):
                            for eg in (Q(0), eta, 3*eta/2):
                                hx, hy, hg = max(0, x-ex), y-ey, max(0, g-eg)
                                need(hy > lower/2, 'protected denominator')
                                error = abs(hx*hg/hy-x*g/y)
                                need(error < 8*eta/lower+4*eta/lower**2,
                                     'independent ratio error envelope')
                                cases += 1
    return cases


def consumer():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_axis import Axis
    from gaussian_matrix import Matrix
    from gaussian_rationals import Rational
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, sealed_constructors
    from words import BLANK

    def make(value):
        value = Q(value)
        return Rational(Signed(Count.literal(abs(value.numerator)), value < 0),
                        Count.literal(value.denominator))

    def number(value):
        return Q((-1 if value.numerator.negative else 1)*decode(value.numerator.magnitude),
                 decode(value.denominator))

    class SuppliedCoefficient:
        def __init__(self):
            self.arguments = []

        def coefficient(self, argument):
            self.arguments.append(argument.copy())
            return Count.literal(3)

        def close(self):
            for argument in self.arguments:
                argument.close()

    pool = ScratchPool(256)
    scope = OuterScope(pool)
    s, t, w = 8, 9, 2
    rho = Q(t, s)
    q = [(2*t*j+s)//(2*s) for j in range(s)]
    beta = [rho*j-q[j] for j in range(s)]
    weights = [Q(j+2, 32) for j in range(s)]
    kernels = [Q(1), Q(1, 4), Q(1, 8)]
    counts = {name: 0 for name in ('diagonal', 'hole', 'same', 'cross', 'wrapped')}
    with sealed_constructors(), scope.installed():
        axis = Axis.__new__(Axis)
        axis.fields = {}
        axis.weights = axis.kernel = axis.matrix = axis.exponentials = None
        try:
            for name, value in (('s', s), ('w', w), ('unit', 16), ('zero', 0)):
                axis.keep(name, Count.literal(value))
            axis.keep('rho', make(rho))
            axis.keep('u_rational', make(1))
            with owned(Count.literal(s), Count.literal(5), Count.literal(3), Count.literal(1)) as (rows, cols, kr, kc):
                axis.weights = Matrix(rows, cols, pool)
                axis.kernel = Matrix(kr, kc, pool)
            for j in range(s):
                for k, value in enumerate((weights[j], beta[j], q[j]-j, 0, q[j])):
                    with owned(Count.literal(j), Count.literal(k), make(value)) as (row, col, entry):
                        axis.weights.set(row, col, entry)
            for j, value in enumerate(kernels):
                with owned(Count.literal(j), Count.literal(0), make(value)) as (row, col, entry):
                    axis.kernel.set(row, col, entry)
            axis.exponentials = SuppliedCoefficient()
            for i in range(s):
                for j in range(s):
                    before = len(axis.exponentials.arguments)
                    with owned(Count.literal(i), Count.literal(j)) as (row, col):
                        with no_decode():
                            result = axis.matrix_entry(row, col)
                        with owned(result):
                            actual = number(result)
                    delta = j-i
                    direct = abs(delta) <= w
                    if not direct:
                        delta += -s if delta > 0 else s
                    if i == j:
                        branch, expected = 'diagonal', Q(1)
                    elif abs(delta) > w:
                        branch, expected = 'hole', Q(0)
                    elif direct and q[i]-i == q[j]-j:
                        branch = 'same'
                        expected = weights[i]*kernels[abs(delta)]/weights[j]
                    else:
                        branch, expected = ('cross' if direct else 'wrapped'), Q(3, 16)
                        need(len(axis.exponentials.arguments) == before+1, 'one cross coefficient call')
                        need(number(axis.exponentials.arguments[-1]) ==
                             (rho*delta+beta[i])**2-beta[j]**2, 'actual encoded cross argument')
                    if branch not in ('cross', 'wrapped'):
                        need(len(axis.exponentials.arguments) == before, 'coefficient bypass')
                    need(actual == expected, 'unchanged matrix consumer: '+branch)
                    counts[branch] += 1
            need(all(counts.values()), 'all actual consumer branches executed')
        finally:
            axis.close()
            pool.empty()
    for tape in pool.tapes:
        erase_marker(tape)
        need(tape.head == 1 and all(v == BLANK for v in tape.cells), 'scratch restored')
    return counts


def main():
    authenticate()
    geometry = identities()
    ratio_cases = ratio_controls()
    sys.path.insert(0, str(ROOT / 'research/physical-gaussian-core'))
    from gaussian_sources import opened
    with opened():
        actual = consumer()
        from gaussian_check_production import run
        metadata = run()
    print(json.dumps({'status': 'PASS', 'geometry': geometry, 'ratio_cases': ratio_cases, 'consumer': actual,
                      'production_metadata': metadata,
                      'scope': 'supplied-coefficient consumer and metadata only; universal proof is written'},
                     sort_keys=True))


if __name__ == '__main__':
    main()
