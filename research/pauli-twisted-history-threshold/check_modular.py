#!/usr/bin/env python3
"""Independent finite-field oracle: no Gaussian engine imports or Kronecker code.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Finite fields exercise the same algebraic identities, not physical Q(i) inputs.
"""
import json


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def dimension(vectors, prime):
    a = [list(row) for row in vectors]
    pivot = 0
    for col in range(len(a[0])):
        chosen = next((j for j in range(pivot, len(a)) if a[j][col] % prime), None)
        if chosen is None:
            continue
        a[pivot], a[chosen] = a[chosen], a[pivot]
        inv = pow(a[pivot][col] % prime, -1, prime)
        a[pivot] = [x*inv % prime for x in a[pivot]]
        for j in range(pivot+1, len(a)):
            factor = a[j][col] % prime
            a[j] = [(x-factor*y) % prime for x, y in zip(a[j], a[pivot])]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def flatten(a):
    return sum(a, [])


def product(a, b, prime):
    n = len(a)
    return [[sum(a[i][k]*b[k][j] for k in range(n)) % prime
             for j in range(n)] for i in range(n)]


def run():
    cases, twists, projective, polynomial = 0, 0, 0, 0
    spectrum = {}
    for prime in (5, 13):
        for f in range(1, 5):
            n, full = 2**f, 2**f-1
            # Direct computational-basis action of X^u Z^v; independent of
            # the proof's X-eigenbasis and the primary Kronecker interpreter.
            ordinary = [[[((-1)**(v*s.bit_count())) % prime
                          if r == s^(full if u else 0) else 0
                          for s in range(n)] for r in range(n)]
                        for u, v in ((0, 0), (1, 0), (0, 1), (1, 1))]
            ident, p, c, pc = ordinary
            cp = product(c, p, prime)
            require(pc == [[(-1)**f*x % prime for x in row] for row in cp], 'twist')
            require(dimension([flatten(m) for m in ordinary], prime) == 4, 'image algebra')
            twists += 1
            quarter = pow(4, -1, prime)
            e = [[sum(g[r][s] for g in ordinary)*quarter % prime
                  for s in range(n)] for r in range(n)]
            for a in range(1, prime):
                for b in range(1, prime):
                    if (a*a-b*b) % prime == 0:
                        continue
                    # Each differing coordinate contributes b; each equal one a.
                    h = [[pow(a, f-(r^s).bit_count(), prime) *
                          pow(b, (r^s).bit_count(), prime) % prime
                          for s in range(n)] for r in range(n)]
                    targets = [product(g, h, prime) for g in ordinary]
                    union = dimension([flatten(m) for m in ordinary+targets], prime)
                    spectrum[str((prime, f, union))] = spectrum.get(str((prime, f, union)), 0)+1
                    if f == 1:
                        require(union == 4, 'ordinary width one')
                    elif f % 2:
                        require(union == 8, 'odd separation')
                    else:
                        require(product(e, e, prime) == e, 'even projector')
                        require(dimension([flatten(e), flatten(product(e, h, prime))], prime) == 2,
                                'even target character')
                    cases += 1
                    lp, lm = (a+b) % prime, (a-b) % prime
                    for width in (2, 3, 7, 8, 31, 32):
                        left = (pow(lp, width, prime)-pow(lp, width-2, prime)*lm*lm) % prime
                        right = 4*a*b*pow(lp, width-2, prime) % prime
                        require(left == right and right != 0, 'nonzero weight difference')
                        polynomial += 1
            # Counterexample to using h outside G as the target criterion.
            extra = [[2*x % prime for x in row] for row in p]
            require(dimension([flatten(m) for m in ordinary+[extra]], prime) == 4,
                    'ordinary scalar multiple')
            projective += 1
    return {'status': 'PASS_INDEPENDENT_MODULAR_PAULI_HISTORY',
            'literal_tensor_cases': cases, 'phase_twists': twists,
            'projective_controls': projective, 'separation_identities': polynomial,
            'rank_spectrum': spectrum,
            'limits': 'finite-field identity controls; all-width Q(i) theorem is PROOF.md'}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
