"""Check that the explicit integration retains the full source proof.

Only the declared evaluator calls, source paths and standalone CLI differ.
Comments and module docstrings do not affect this syntax-tree comparison.
"""
import ast
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def replace(text, old, new, count=1):
    if text.count(old) != count:
        raise ValueError('Unexpected source integration site: ' + old)
    return text.replace(old, new)


def syntax(text):
    tree = ast.parse(text)
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        tree.body.pop(0)
    return ast.dump(tree, include_attributes=False)


def run(overrides=None):
    physical = (ROOT / 'source/physical.py').read_text()
    changes = [('import optimize as O', 'import optimize as O\nfrom quadratic import equal_operators'),
               ('ROOT = Path(__file__).resolve().parent', "ROOT = Path(__file__).resolve().parent / 'source'"),
               ('def decode_recipe(P, ce, recipe, op):', 'def decode_recipe(P, ce, recipe, op, equality=equal_operators):'),
               ('decoded.tab==op.tab and decoded.zero_state()==op.zero_state()', 'equality(decoded,op)'),
               ('actual.tab==positive.tab and actual.zero_state()==positive.zero_state()', 'equality(actual,positive)'),
               ('def build(folded, expected=None):', 'def build(folded, expected=None, equality=equal_operators):'),
               ("decode_recipe(P,ce,expected['maps'][key],op)", "decode_recipe(P,ce,expected['maps'][key],op,equality)"),
               ("decode_recipe(P,ce,recipe['factorization'],op)", "decode_recipe(P,ce,recipe['factorization'],op,equality)")]
    for old, new in changes:
        physical = replace(physical, old, new)
    verifier = (ROOT / 'source/verify.py').read_text()
    verifier = replace(verifier, 'ROOT=Path(__file__).resolve().parent', 'ROOT=Path(__file__).resolve().parent / "source"')
    verifier = replace(verifier, 'sys.path.insert(0,str(ROOT))', 'sys.path.insert(0,str(ROOT.parent))\nsys.path.insert(0,str(ROOT))')
    verifier = replace(verifier, 'import physical', 'import replay as physical')
    verifier = replace(verifier, 'def rejecting_controls(word,inv,cuts,plan,folded):',
                       'def rejecting_controls(word,inv,cuts,plan,folded,equality):')
    verifier = replace(verifier, 'physical.decode_recipe(P,ce,recipe,ce.canonical_frame(9,[]))',
                       'physical.decode_recipe(P,ce,recipe,ce.canonical_frame(9,[]),equality)')
    verifier = replace(verifier, 'def run():', 'def run(equality=physical.equal_operators):')
    verifier = replace(verifier, 'physical.build(set(folded),plan)', 'physical.build(set(folded),plan,equality)')
    verifier = replace(verifier, 'rejecting_controls(word,inv,cuts,plan,folded)',
                       'rejecting_controls(word,inv,cuts,plan,folded,equality)')
    verifier = verifier[:verifier.index("if __name__=='__main__':")]
    result = {}
    for filename, expected in [('replay.py', physical), ('verify_source.py', verifier)]:
        actual = syntax((overrides or {}).get(filename, (ROOT / filename).read_text()))
        if actual != syntax(expected):
            raise ValueError('Undeclared source proof change: ' + filename)
        result[filename] = sha256((ROOT / filename).read_bytes()).hexdigest()
    return result


if __name__ == '__main__':
    print('PASS_COMPLETE_SOURCE_CHECK_BINDING', run())
