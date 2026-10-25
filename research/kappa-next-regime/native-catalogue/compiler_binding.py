"""Source-bound replica lookup for the retained Driver and macro compiler.

The sole production change in each component is the idle collection lookup:
``topology.idles[event['idx']]`` becomes
``topology.idles_for(event['idx'], replica)``. All other AST nodes are retained.
This is an interface binding, not a proof of the physical primitive contracts.
Apache-2.0; credited retained caller authors and ChrisR PR3986.
"""
import ast
import copy
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CALLER = ROOT/'research/selected-bit-physical-caller'
SOURCES = {
    'Driver': CALLER/'inputs/pr2753/predecessor/driver.py',
    'compile_node': CALLER/'macro_code.py',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rewrite_idle_lookup(node):
    original = copy.deepcopy(node)
    old = ast.parse('topology.idles[event["idx"]]', mode='eval').body
    new = ast.parse('topology.idles_for(event["idx"], replica)', mode='eval').body
    count = 0
    for item in ast.walk(node):
        if isinstance(item, ast.For) and ast.dump(item.iter) == ast.dump(old):
            need(isinstance(item.target, ast.Name) and item.target.id == 'identifier',
                 'only the retained identifier loop is rebound')
            item.iter = copy.deepcopy(new)
            count += 1
    need(count == 1, 'exactly one replica-indexed idle lookup substitution')
    # Reversing the one lookup must restore every source AST node.
    back = copy.deepcopy(node)
    count = 0
    for item in ast.walk(back):
        if isinstance(item, ast.For) and ast.dump(item.iter) == ast.dump(new):
            item.iter = copy.deepcopy(old)
            count += 1
    need(count == 1 and ast.dump(back) == ast.dump(original),
         'all remaining compiler/Driver syntax and guards are unchanged')
    return ast.fix_missing_locations(node)


def source_node(name):
    need(name in SOURCES, 'known retained component')
    tree = ast.parse(SOURCES[name].read_text())
    return next(n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == name)


def bind(name, namespace):
    """Compile the retained component in its original runtime namespace."""
    node = rewrite_idle_lookup(source_node(name))
    env = dict(namespace)
    exec(compile(ast.fix_missing_locations(ast.Module([node], type_ignores=[])),
                 str(SOURCES[name]), 'exec'), env)
    return env[name]


def receipt():
    rows = {}
    for name, path in SOURCES.items():
        old = source_node(name)
        new = rewrite_idle_lookup(copy.deepcopy(old))
        rows[name] = {
            'source': path.relative_to(ROOT).as_posix(),
            'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'source_AST_sha256': hashlib.sha256(ast.dump(old).encode()).hexdigest(),
            'bound_AST_sha256': hashlib.sha256(ast.dump(new).encode()).hexdigest(),
            'idle_lookup_substitutions': 1,
            'all_other_AST_nodes_unchanged': True,
        }
    return rows
