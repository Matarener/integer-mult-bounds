"""Guarded common-subexpression elimination for the actual encoded weight loop.

RETURN on the pending stack is a unary fixed-PAIR continuation. The existing
Stack already encodes this finite tag and one residue operand. VALUE remains a
pair of index words. No new tape, coordinate decoder, or runtime Python cache.
"""
import ast
from hashlib import sha256

WEIGHT_AST = '7dcdba608a913b57cf2cbd5c30efe7c4bac229397fe26c7e7d1536a0004e2ecb'

def install(base, path, namespace):
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Callback')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'weight')
    if sha256(ast.dump(method).encode()).hexdigest() != WEIGHT_AST:
        raise ValueError('exact reviewed Callback.weight AST')
    source = ast.unparse(method)
    before = "elif tag == PAIR:"
    after = '''elif tag == RETURN:
            coefficient, = operands
            value_tag, values = self.values.pop()
            need(value_tag == RETURN, 'fixed-pair value tag')
            value, = values
            inv = self.ring.inverse(value)
            need(inv is not None, 'generated pair denominator unit')
            product = self.ring.multiply(coefficient, value)
            result = self.ring.multiply(product, inv)
            self.values.push(RETURN, result)
            self.residue.free_many(coefficient, value, inv, product, result)
        elif tag == PAIR:'''
    if source.count(before) != 1: raise ValueError('PAIR continuation context')
    source = source.replace(before, after)
    old = 'self.pending.push(PAIR, diagonal[field])'
    new = '''fixed_head = field < 64 and permutation[field] == field
                    self.pending.push(RETURN if fixed_head else PAIR, diagonal[field])'''
    if source.count(old) != 1: raise ValueError('PAIR scheduling context')
    source = source.replace(old, new)
    old = 'for row in (field, permutation[field]):'
    new = 'for row in ((field,) if fixed_head else (field, permutation[field])):'
    if source.count(old) != 1: raise ValueError('ancestor scheduling context')
    source = source.replace(old, new)
    env = dict(namespace)
    exec(compile(source, '<guarded fixed-PAIR CSE>', 'exec'), env)
    class CSECallback(base): pass
    CSECallback.weight = env['weight']
    return CSECallback
