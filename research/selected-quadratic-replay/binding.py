"""Bind explicit derived files to the complete retained selected verifier.

Only the declared state methods, input paths, imports and CLI guards differ.
All remaining assertions become explicit failures so that -O retains them.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/p104-helper-subspace-splits'
PAIRS = {
    'clifford_fast.py': 'research/p104-native-channel/vendor/clifford_exact.py',
    'native_fast.py': 'research/p104-native-channel/vendor/native_verify.py',
    'local_fast.py': SOURCE + '/local.py',
    'verify_source.py': SOURCE + '/verify.py',
}


def replace(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError('Unexpected source integration site: ' + old)
    return text.replace(old, new)


class ExplicitAssertions(ast.NodeTransformer):
    def visit_Assert(self, node):
        args = [] if node.msg is None else [node.msg]
        return ast.copy_location(ast.If(ast.UnaryOp(ast.Not(), node.test),
            [ast.Raise(ast.Call(ast.Name('AssertionError', ast.Load()), args, []), None)], []), node)


def expected(filename):
    text = (ROOT / PAIRS[filename]).read_text(encoding='utf-8')
    if filename in ('local_fast.py', 'verify_source.py'):
        text = replace(text, 'ROOT = HERE.parents[1]',
                       "ROOT = HERE.parents[1]\nHERE = ROOT / '" + SOURCE + "'")
    if filename == 'local_fast.py':
        text = replace(text, 'research/p104-native-channel/vendor/clifford_exact.py',
                       'research/selected-quadratic-replay/clifford_fast.py')
        text = replace(text, 'research/p104-native-channel/vendor/native_verify.py',
                       'research/selected-quadratic-replay/native_fast.py')
    if filename == 'verify_source.py':
        text = replace(text, 'import local as L', 'import local_fast as L')
        text = replace(text, 'sys.path.insert(0, str(HERE))',
                       'sys.path.insert(0, str(HERE))\n    sys.path.insert(0, str(Path(__file__).resolve().parent))')
        text = replace(text, 'def main():', 'def main(argv=None):')
        text = replace(text, 'args = parser.parse_args()',
                       "args = parser.parse_args(argv)\n    need(not args.write, 'Derived replay cannot write source artifacts')")
    tree = ast.parse(text)
    if filename == 'clifford_fast.py':
        tree.body.insert(1, ast.parse('from state_adapter import dense_state').body[0])
        cls, = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Op']
        method, = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'zero_state']
        method.body = ast.parse('return dense_state(self.n, self.circuit, basis)').body
    if filename == 'native_fast.py':
        tree.body.insert(1, ast.parse('from state_adapter import sparse_state').body[0])
        method, = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'state']
        method.body = ast.parse('return sparse_state(circuit, basis)').body
    return ast.fix_missing_locations(ExplicitAssertions().visit(tree))


def check(overrides=None):
    result = {}
    for filename in PAIRS:
        raw = (overrides or {}).get(filename, (HERE / filename).read_text(encoding='utf-8'))
        if ast.dump(ast.parse(raw), include_attributes=False) != ast.dump(expected(filename), include_attributes=False):
            raise ValueError('Undeclared selected proof change: ' + filename)
        result[filename] = sha256(raw.encode('utf-8')).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-derived', action='store_true')
    args = parser.parse_args()
    if args.write_derived:
        for filename in PAIRS:
            (HERE / filename).write_text(ast.unparse(expected(filename)) + '\n', encoding='utf-8')
    print('PASS_SELECTED_SOURCE_BINDING', check())


if __name__ == '__main__':
    main()
