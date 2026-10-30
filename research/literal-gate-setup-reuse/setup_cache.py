"""Bounded immutable literal P/D setup, using that literal compiler alone."""
import ast
from functools import lru_cache
from hashlib import sha256
import inspect
import textwrap

ORIGINAL_METHOD_SHA256 = 'ebb92d6870d73dc452faf6d8c3c62710539ffb9bae3a5588dc694fe2693c6509'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def frozen(value):
    if type(value) in (str, int):
        return value
    if type(value) in (tuple, list):
        return tuple(frozen(item) for item in value)
    raise ValueError('Exact setup key types')


class Setup:
    def __init__(self, compiler, capacity=512):
        require(type(capacity) is int and 1 <= capacity <= 512, 'Bounded setup capacity')
        self.mv = compiler.mv
        self.qvalue = compiler.qvalue
        self.cached = lru_cache(maxsize=capacity)(self._table)

    def __call__(self, width, gate):
        require(type(width) is int and 0 <= width <= 9, 'Exact bounded setup width')
        gate = frozen(gate)
        require(type(gate) is tuple and gate and gate[0] in ('P', 'D'), 'Literal setup gate')
        require(len(gate) == (2 if gate[0] == 'P' else 3), 'Complete setup gate fields')
        require(type(gate[1]) is tuple and len(gate[1]) == width and
                all(type(x) is int for x in gate[1]), 'Complete setup matrix')
        if gate[0] == 'D':
            require(type(gate[2]) is tuple and len(gate[2]) == width and
                    all(type(x) is int for x in gate[2]), 'Complete setup phase data')
        return self.cached(width, gate)

    def _table(self, width, gate):
        if gate[0] == 'P':
            return tuple(self.mv(gate[1], x) for x in range(1 << width))
        return tuple(self.qvalue(gate[1], gate[2], x, width) for x in range(1 << width))


def dump(node):
    return ast.dump(node, include_attributes=False)


def expression(text):
    return ast.parse(text, mode='eval').body


class Preparation(ast.NodeTransformer):
    def __init__(self):
        self.counts = {'P': 0, 'D': 0, 'mv': 0, 'qvalue': 0}

    def visit_Call(self, node):
        if dump(node) == dump(expression('mv(e[1], x)')):
            self.counts['mv'] += 1
            return ast.copy_location(expression('_setup_images[x]'), node)
        if dump(node) == dump(expression('qvalue(e[1], e[2], x, self.n)')):
            self.counts['qvalue'] += 1
            return ast.copy_location(expression('_setup_phases[x]'), node)
        return self.generic_visit(node)

    def visit_If(self, node):
        node = self.generic_visit(node)
        for tag, name in (('P', '_setup_images'), ('D', '_setup_phases')):
            if dump(node.test) == dump(expression("e[0] == '" + tag + "'")):
                self.counts[tag] += 1
                node.body.insert(0, ast.Assign([ast.Name(name, ast.Store())],
                                              expression('_literal_setup(self.n, e)')))
        return node


def bind(compiler, capacity=512):
    """Derive only two per-gate preparations and their two literal lookups."""
    original = compiler.Op.zero_state
    text = textwrap.dedent(inspect.getsource(original))
    require(sha256(text.encode()).hexdigest() == ORIGINAL_METHOD_SHA256, 'Exact original literal method')
    module = ast.parse(text)
    require(len(module.body) == 1 and isinstance(module.body[0], ast.FunctionDef), 'One literal method')
    transform = Preparation()
    prepared = ast.fix_missing_locations(transform.visit(module))
    require(transform.counts == {'P': 1, 'D': 1, 'mv': 1, 'qvalue': 1}, 'Exact literal preparation sites')
    setup = Setup(compiler, capacity)
    namespace = dict(compiler.__dict__, _literal_setup=setup)
    exec(compile(prepared, '<source-bound literal setup>', 'exec'), namespace)
    compiler.Op.zero_state = namespace['zero_state']
    return setup, original, {'sites': transform.counts,
                             'original_method_sha256': sha256(text.encode()).hexdigest(),
                             'prepared_ast_sha256': sha256(dump(prepared).encode()).hexdigest()}
