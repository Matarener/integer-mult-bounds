"""Direct emission of authenticated residual runs; outer factory visits unchanged.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from hashlib import sha256
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'selected-itinerary-compression'))
import itinerary


class RegionalSink(itinerary.Sink):
    """One immutable-plan scan, then one run per source factory return."""
    def append(self, operation):
        kind = operation[0]
        if kind == 'residual_begin':
            itinerary.need(self.active is None, 'nested residual')
            _, role, definition = operation
            plan = self.plans.get(id(definition.plan))
            if plan is None:
                plan = itinerary.PlanIndex.build(definition.plan)
                self.plans[id(definition.plan)] = plan
            self.active = role, itinerary.BlockRun(definition, plan, definition.axis), False
            self.retain(operation)
        elif kind == 'residual_end':
            itinerary.need(self.active is not None, 'end outside residual')
            role, run, emitted = self.active
            itinerary.need(operation[1] == role and operation[2] is run.definition, 'end identity')
            itinerary.need(emitted, 'missing direct run')
            self.active = None
            self.retain(operation)
        else:
            itinerary.need(self.active is None, 'operation inside residual')
            itinerary.need(kind != 'block', 'unexpected enumerated block')
            self.retain(operation)

    def append_run(self, definition):
        itinerary.need(self.active is not None, 'run outside residual')
        role, run, emitted = self.active
        itinerary.need(definition is run.definition and not emitted, 'duplicate or foreign run')
        if run.count:
            self.retain(run, run.count)
        self.active = role, run, True


_LOOP = '''if definition.axis is not None:
    operations.append(("block", definition, ("axis", definition.axis, 0)))
else:
    cursor = Cursor(definition.plan)
    while not cursor.done:
        operations.append(("block", definition, cursor.take()))
'''


def compiler(module, source, digest, observer=None):
    """Preserve optional append observers through the explicitly eager path."""
    if observer is not None:
        return itinerary.compiler(module, source, digest, observer)
    itinerary.need(sha256(source).hexdigest() == digest, 'emitter source hash')
    text = source.decode()
    boundaries = (('operations = [("node",)]', 'operations = _regional_sink([("node",)])'),
                  ('Code(tuple(operations), staged)', 'Code(operations.finish(), staged)'))
    for old, new in boundaries:
        itinerary.need(text.count(old) == 1, 'unsupported emitter shape')
        text = text.replace(old, new)
    tree = ast.parse(text)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'compile_node']
    itinerary.need(len(functions) == 1, 'unsupported emitter function')
    helpers = [n for n in functions[0].body if isinstance(n, ast.FunctionDef) and n.name == 'residual']
    itinerary.need(len(helpers) == 1 and len(helpers[0].body) == 4, 'unsupported residual helper')
    body = helpers[0].body
    itinerary.need(ast.dump(body[2]) == ast.dump(ast.parse(_LOOP).body[0]), 'unsupported Cursor loop')
    body[2] = ast.copy_location(ast.parse('operations.append_run(definition)').body[0], body[2])
    namespace = dict(module.__dict__)
    namespace['_regional_sink'] = RegionalSink
    replacement = ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[]))
    exec(compile(replacement, '<authenticated-direct-run-emitter>', 'exec'), namespace)
    return namespace['compile_node']
