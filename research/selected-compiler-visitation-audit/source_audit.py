"""Bounded public-source metadata/trace audit; never expand selected GL64.

Original compiler, factory and topology functions are not edited.  The tiny
trace supplies a test-only binding, NOT a selected numerical endpoint proof.
Apache-2.0; retains the source authors credited in README.md.
"""
import ast
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

PHYSICAL = 'research/selected-bit-physical-caller'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def function(tree, name, cls=None):
    body = tree.body
    if cls:
        body = next(n.body for n in body if isinstance(n, ast.ClassDef) and n.name == cls)
    return next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)


def call_names(node):
    return [ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)]


def compiler_shape(tree):
    node = function(tree, 'compile_node')
    sites = []
    def walk(n, loops=()):
        if isinstance(n, ast.For):
            loops = (*loops, (ast.unparse(n.target), ast.unparse(n.iter)))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'residual':
            sites.append((tuple(ast.unparse(a) for a in n.args), loops))
        for child in ast.iter_child_nodes(n):
            walk(child, loops)
    walk(node)
    prefix = (('event', 'topology.schedule'), ('replica', 'range(topology.replicas)'))
    local = prefix + (('low', 'topology.catalogue.low_classes()'),
                      ('(position, item)', 'enumerate(call.events)'))
    idle = prefix + (('identifier', "topology.idles[event['idx']]"),
                     ('low', 'topology.catalogue.low_classes()'))
    expected = [(('target', 'call.requests[position]', 'True', 'low'), local),
                (("'copy_source'", 'call.requests[position]', 'True', 'low'), local),
                (("'idle'", 'identifier', 'False', 'low'), idle)]
    need(sites == expected, 'compiler residual call sites and loop order changed')
    body = ast.unparse(node)
    for text in ('binding.residual(identifier, common, low, mode)',
                 "operations.append(('residual_begin', role, definition))",
                 "operations.append(('residual_end', role, definition))",
                 'return Code(tuple(operations), staged)'):
        need(text in body, 'compiler retention/factory structure changed: ' + text)
    return {'residual_sites': len(sites), 'local_order': 'replica/LOW/event',
            'idle_order': 'replica/request/LOW'}


def static_audit(root):
    p = root / PHYSICAL
    trees = {name: ast.parse((p / (name + '.py')).read_bytes())
             for name in ('macro_code', 'macro_binding', 'macro_machine')}
    shape = compiler_shape(trees['macro_code'])
    factory = function(trees['macro_binding'], 'residual', 'SelectedBinding')
    returns = [n for n in ast.walk(factory) if isinstance(n, ast.Return)]
    need(not factory.decorator_list and len(returns) == 1 and
         isinstance(returns[0].value, ast.Call) and
         ast.unparse(returns[0].value.func) == 'Residual', 'fresh public factory return')
    need(not any(isinstance(n, ast.Attribute) and n.attr in ('_definitions', 'registry', 'sync')
                 for n in ast.walk(factory)), 'public factory is not the hypothetical cache')
    runtime = next(n for n in trees['macro_machine'].body
                   if isinstance(n, ast.ClassDef) and n.name == 'Machine')
    methods = [n for n in runtime.body if isinstance(n, ast.FunctionDef)]
    for method in methods:
        need(not any(c == 'compile_node' or c.endswith(('.compile_node', '.residual', '.sync'))
                     for c in call_names(method)), 'unexpected direct setup call: ' + method.name)
    need('self.programs[self.mode].operations[self.pc]' in
         ast.unparse(function(trees['macro_machine'], 'run', 'Machine')), 'stored operation fetch')
    need('tuple(programs)' in ast.unparse(function(trees['macro_machine'], '__init__', 'Machine')),
         'programs supplied at construction')
    # Counts-preserving idle-loop and common-view mutants must not pass shape checks.
    mutants = []
    changed = deepcopy(trees['macro_code'])
    loops = [n for n in ast.walk(function(changed, 'compile_node')) if isinstance(n, ast.For)]
    outer = next(n for n in loops if ast.unparse(n.target) == 'identifier')
    inner = next(n for n in ast.walk(outer) if isinstance(n, ast.For) and ast.unparse(n.target) == 'low')
    outer.target, inner.target = inner.target, outer.target
    outer.iter, inner.iter = inner.iter, outer.iter
    mutants.append(changed)
    changed = deepcopy(trees['macro_code'])
    site = next(n for n in ast.walk(function(changed, 'compile_node'))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'residual')
    site.args[2] = ast.Constant(False)
    mutants.append(changed)
    for changed in mutants:
        try:
            compiler_shape(changed)
        except ValueError:
            continue
        raise ValueError('source-shape mutant was accepted')
    return dict(shape, public_factory='fresh Residual per successful call; no definition cache',
                runtime_methods_checked=len(methods), source_shape_mutants_rejected=len(mutants),
                runtime_cut='direct Machine method calls only; callbacks and total runtime cost excluded')


class InventoryPath(type(Path())):
    """Only normalize relative inventory spelling for the pinned Windows loader."""
    def __str__(self):
        return super().__str__().replace('\\', '/')


def activate(root):
    p = root / PHYSICAL
    need('loader' not in sys.modules, 'fresh source namespace required')
    sys.path.insert(0, str(p))
    loader = importlib.import_module('loader')
    need(Path(loader.__file__).resolve() == (p / 'loader.py').resolve(), 'exact loader path')
    # Original authenticate() compares str(relative_path) to POSIX manifest names.
    # Keep every predicate/hash/function unchanged, and check path identity.
    for name in ('HERE', 'REPOSITORY', 'CALLER', 'PARKING'):
        original = getattr(loader, name)
        normalized = InventoryPath(original)
        need(Path(original).resolve() == Path(normalized).resolve(), 'same source pathname')
        setattr(loader, name, normalized)
    loader.activate()
    loader.compatibility_controls()
    modules = {name: importlib.import_module(name)
               for name in ('catalogue', 'topology', 'control', 'macro_code', 'macro_binding')}
    return modules


def selected_census(modules):
    cat = modules['catalogue'].Catalogue(7)  # metadata only; no LOW enumeration
    topo = modules['topology'].SelectedTopology(cat)
    State = modules['control'].LocalState
    groups, local_events, checks = [], 0, 0
    def check(ok, message):
        nonlocal checks
        checks += 1
        need(ok, message)
    for schedule_index, event in enumerate(topo.schedule):
        kind = event['kind']
        if kind not in ('local_cover_sweep', 'idle'):
            continue
        expected = None
        for replica in range(topo.replicas):
            ids = []
            if kind == 'local_cover_sweep':
                call = topo.call(event['stage'], replica)
                state = State(call)
                local_events += len(call.events)
                check(local_events <= 8_000_000, 'bounded metadata-event budget')
                for position, _ in enumerate(call.events):
                    op, _ = state.accept(position)
                    if op in (0, 2):
                        identifier = call.requests[position]
                        check(type(identifier) is int and 0 <= identifier < len(cat.requests), 'local request ID')
                        req = cat.requests[identifier]
                        check(req.kind == ('MOVE' if op == 0 else 'COPY') and
                              req.stage == event['stage'] and req.position == position, 'local source site')
                        ids.append(identifier)
                    else:
                        check(call.requests[position] is None, 'no residual at XOR/ERASE')
                state.finish()
            else:
                for identifier in topo.idles[event['idx']]:
                    check(type(identifier) is int and 0 <= identifier < len(cat.requests), 'idle request ID')
                    req = cat.requests[identifier]
                    check(req.kind == 'IDLE' and req.stage == event['idx'], 'idle source group')
                    check(0 <= topo.idle_family(identifier, replica) < topo.families, 'idle family')
                    ids.append(identifier)
            if expected is None:
                expected = ids
            else:
                check(ids == expected, 'all replicas have identical request sequences')
        check(len(expected) == len(set(expected)), 'distinct requests within group')
        common = kind == 'local_cover_sweep'
        check(all(common == (cat.requests[i].kind != 'IDLE') for i in expected), 'one common/native view')
        groups.append(dict(schedule_index=schedule_index, kind=kind,
                           order='low-major' if common else 'id-major', common=common, request_ids=expected))
    flat = [i for g in groups for i in g['request_ids']]
    check(len(flat) == len(set(flat)) == len(cat.requests), 'disjoint complete groups')
    check(set(flat) == set(range(len(cat.requests))), 'complete request interval')
    check(topo.replicas == cat.replicas == 32, 'selected replica count')
    check(groups[0]['request_ids'][0] == 0 and groups[0]['common'], 'ambient first request')
    sizes = [len(g['request_ids']) for g in groups]
    summary = dict(replicas=topo.replicas, requests=len(cat.requests),
                   kinds=dict(sorted(Counter(r.kind for r in cat.requests).items())),
                   group_sizes=sizes, sum_group_squares=sum(k*k for k in sizes),
                   local_metadata_events=local_events, explicit_metadata_checks=checks,
                   ambient_literal_event=cat.requests[0].position,
                   group_sequence_sha256=[sha256(json.dumps(g['request_ids'], separators=(',', ':')).encode()).hexdigest()
                                          for g in groups])
    return groups, summary, cat.old


def tiny_trace(root, modules):
    path = root / PHYSICAL / 'inputs/pr2753/predecessor/model.py'
    spec = importlib.util.spec_from_file_location('compiler_audit_tiny_model', path)
    model = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = model
    spec.loader.exec_module(model)
    cat, State = model.Catalogue(), modules['control'].LocalState
    topo = model.Topology(cat)
    need(cat.q == 3 and cat.dimension == 2 and cat.codes.size == 48, 'tiny GL2(F3) bound before enumeration')
    lows = list(cat.low_classes())  # ONLY the original 48-element GL2 fixture
    ordinal = {low: i for i, low in enumerate(lows)}
    need(len(lows) == len(ordinal) == 48, 'genuine GL2 vocabulary')
    expected = []
    for event in topo.schedule:
        if event['kind'] == 'local_cover_sweep':
            for replica in range(topo.replicas):
                call = topo.call(event['stage'], replica)
                state, ids = State(call), []
                for pos, _ in enumerate(call.events):
                    op, _ = state.accept(pos)
                    if op in (0, 2):
                        ids.append(call.requests[pos])
                state.finish()
                expected.extend((identifier, True, i) for i in range(48) for identifier in ids)
        elif event['kind'] == 'idle':
            for replica in range(topo.replicas):
                expected.extend((identifier, False, i) for identifier in topo.idles[event['idx']] for i in range(48))
    plan = importlib.import_module('plan').compile_plan(((1, 0), (0, 0)), 1, 3, True)
    compiler = modules['macro_code']
    class TracingBinding:
        def __init__(self, axis):
            self.axis, self.calls = axis, []
        def residual(self, identifier, common, low, mode):
            need(mode == 0, 'tiny compiler mode')
            self.calls.append((identifier, common, ordinal[low]))
            return compiler.Residual(cat.codes.encode(identifier, common, low), plan,
                                     identifier, common, low, axis=0 if self.axis else None)
    results = []
    for axis in (True, False):
        binding = TracingBinding(axis)
        code = compiler.compile_node(topo, binding, 0)
        definitions = [op[2] for op in code.operations if op[0] == 'residual_begin']
        ends = [op[2] for op in code.operations if op[0] == 'residual_end']
        actual = [(d.identifier, d.common, ordinal[d.low]) for d in definitions]
        need(binding.calls == actual == expected, 'full original compiler visit order')
        need(len(definitions) == 672 and len({id(d) for d in definitions}) == 672, 'fresh retained fixture definitions')
        need(len(ends) == len(definitions) and all(a is b for a, b in zip(definitions, ends)), 'begin/end object identity')
        active, blocks = None, 0
        references = Counter()
        for op in code.operations:
            if op[0] == 'residual_begin':
                need(active is None, 'nonoverlapping tiny residual intervals')
                active = op[2]
            elif op[0] == 'block':
                need(active is not None and op[1] is active, 'block uses its active wrapper identity')
                blocks += 1
            elif op[0] == 'residual_end':
                need(active is not None and op[2] is active, 'end uses its active wrapper identity')
                active = None
            references.update(id(x) for x in op if isinstance(x, compiler.Residual))
        need(active is None and set(references) == {id(d) for d in definitions}, 'complete retained wrapper intervals')
        need(sum(references.values()) == 2*len(definitions) + blocks, 'exact 2T+B direct operation references')
        results.append(dict(axis=axis, calls=len(actual), operations=len(code.operations),
                            block_operations=blocks, wrapper_references=sum(references.values()),
                            visit_sha256=sha256(json.dumps(actual, separators=(',', ':')).encode()).hexdigest()))
    # Actual unmodified public factory body at a declared Specifications receiver
    # cut: validates allocation identity only, NOT numerical source admissibility.
    receiver = SimpleNamespace(catalogue=cat, specifications=SimpleNamespace(
        bind=lambda identifier, common, low: SimpleNamespace(code=cat.codes.encode(identifier, common, low)),
        plan=lambda code: plan))
    factory = modules['macro_binding'].SelectedBinding.residual
    a, b = (factory(receiver, 0, True, lows[0], 0) for _ in range(2))
    need(a == b and a is not b, 'public factory allocates anew even for the same key')
    return {'traces': results, 'public_factory_equal_key_fresh_instances': True,
            'scope': 'tiny tracing-binding / factory-receiver cuts, not selected plan or runtime validation'}


def run(root):
    static = static_audit(root)
    modules = activate(root)
    groups, census, old = selected_census(modules)
    traces = tiny_trace(root, modules)
    loaded = {}
    for name, module in list(sys.modules.items()) + [('catalogue.old', old)]:
        path = getattr(module, '__file__', None)
        if path:
            p = Path(path).resolve()
            if p.is_relative_to(root):
                loaded[name] = p.relative_to(root).as_posix()
    return groups, dict(static=static, census=census, tiny=traces, loaded_sources=loaded)
