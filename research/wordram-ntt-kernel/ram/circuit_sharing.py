"""Small executable mirror of the used FastPoly Circuit fragment (not a Lean port).
Constructors preserve the exact `fork`/`bind` cost recurrence in the pinned source.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Circuit:
    op: str
    args: tuple


def wire(label): return Circuit('wire', (label,))
def mul(a, b): return Circuit('mul', (a, b))
def add(a, b): return Circuit('add', (a, b))
def sub(a, b): return Circuit('sub', (a, b))
def fork(a, b): return Circuit('fork', (a, b))
def bind(a, b): return Circuit('bind', (a, b))


def evaluate(c, environment, modulus=None):
    def normalize(v): return v if modulus is None else v % modulus
    if c.op == 'wire': return (environment[c.args[0]],)
    a, b = c.args
    if c.op == 'bind':
        producer = evaluate(a, environment, modulus)
        body_environment = {('inl', k): v for k, v in environment.items()}
        body_environment.update({('inr', i): v for i, v in enumerate(producer)})
        return evaluate(b, body_environment, modulus)
    x, y = evaluate(a, environment, modulus), evaluate(b, environment, modulus)
    if c.op == 'fork': return x + y
    if c.op == 'add': return (normalize(x[0] + y[0]),)
    if c.op == 'sub': return (normalize(x[0] - y[0]),)
    if c.op == 'mul': return (normalize(x[0] * y[0]),)
    raise ValueError(c.op)


def gates(c):
    if c.op == 'wire': return (0, 0)
    x, y = (gates(a) for a in c.args)
    return (x[0] + y[0] + int(c.op == 'mul'),
            x[1] + y[1] + int(c.op in ('add', 'sub')))


def butterfly_circuits():
    u, b, w = (wire(s) for s in ('u', 'b', 'w'))
    duplicated = fork(add(u, mul(b, w)), sub(u, mul(b, w)))
    v = wire(('inr', 0)); u_body = wire(('inl', 'u'))
    shared = bind(mul(b, w), fork(add(u_body, v), sub(u_body, v)))
    return duplicated, shared


def check():
    duplicated, shared = butterfly_circuits()
    assert gates(duplicated) == (2, 2)
    assert gates(shared) == (1, 2)
    for u in range(-6, 7):
        for b in range(-6, 7):
            for w in range(-6, 7):
                environment = {'u': u, 'b': b, 'w': w}
                assert evaluate(duplicated, environment) == (u + b*w, u - b*w)
                assert evaluate(shared, environment) == (u + b*w, u - b*w)
                assert evaluate(shared, environment, 65537) == ((u + b*w) % 65537, (u - b*w) % 65537)
    return {'status': 'PASS', 'triples': 2197, 'duplicated_gates_mul_add': gates(duplicated),
            'shared_gates_mul_add': gates(shared), 'formalization': 'not Lean checked'}

if __name__ == '__main__':
    import json
    print(json.dumps(check(), indent=2))
