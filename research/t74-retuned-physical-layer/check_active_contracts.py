"""Check the complete copied transitions against the authenticated source."""

import ast
import copy
import inspect
import textwrap

from active_sources import active, require


def syntax(function):
    return ast.parse(textwrap.dedent(inspect.getsource(function))).body[0]


def same(left, right):
    return ast.dump(left, include_attributes=False) == ast.dump(right, include_attributes=False)


def run():
    import machine
    import root_layer
    import root_plan
    import t74_machine
    import t74_root
    from active_plan import ActiveWidthPlan
    from active_root import ActiveWidthRoot
    from retuned_machine import RetunedMachine
    from retuned_native import profile
    require(RetunedMachine.STOP_POWER == 10**6, "certified fixed stopping power")
    expected, actual = syntax(machine.Machine.node), syntax(RetunedMachine.node)
    sites = [node for node in ast.walk(actual) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "fixed_power"]
    require(len(sites) == 1 and len(sites[0].args) == 3
            and same(sites[0].args[1], ast.parse("self.STOP_POWER", mode="eval").body), "one fixed cutoff delta")
    sites[0].args[1] = ast.Constant(1000)
    require(same(actual, expected), "complete retained node body apart from stopping power")
    require(RetunedMachine.run is t74_machine.T74Machine.run
            and RetunedMachine.release_zero_step is t74_machine.T74Machine.release_zero_step,
            "unchanged execution and private-release protocol")

    expected, actual = syntax(t74_root.T74RootLayer.__init__), syntax(ActiveWidthRoot.__init__)
    changed = []
    for node in ast.walk(actual):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "RetunedMachine":
                node.func.id = "T74Machine"
                changed.append("machine")
            elif node.func.id == "ActiveWidthPlan":
                node.func = ast.Attribute(ast.Name("retained", ast.Load()), "RootPlan", ast.Load())
                changed.append("plan")
    require(sorted(changed) == ["machine", "plan"] and same(actual, expected), "only two root constructor deltas")
    require(all(getattr(ActiveWidthRoot, name) is getattr(root_layer.RootLayer, name)
                for name in ("run", "fast_core", "reserved_leaves", "apply_phase", "apply_leaf")),
            "retained root endpoint and restoration methods")

    expected, actual = syntax(root_plan.RootPlan.compute), syntax(ActiveWidthPlan.compute)
    old_with = next(node for node in ast.walk(expected) if isinstance(node, ast.With))
    new_with = next(node for node in ast.walk(actual) if isinstance(node, ast.With))

    def assignment(statement, name):
        return (isinstance(statement, ast.Assign) and len(statement.targets) == 1
                and isinstance(statement.targets[0], ast.Name) and statement.targets[0].id == name)

    old_index = next(i for i, node in enumerate(old_with.body) if assignment(node, "d"))
    new_index = next(i for i, node in enumerate(new_with.body) if assignment(node, "limit"))
    declared = ast.parse('''limit = keep(floor_power(precision, 997, 1000))
need(compare(selected, limit) <= 0, "selected width within root domain")
d = save("d", literal(1) if selected.zero() else keep(Count(selected)))''').body
    require(all(same(a, b) for a, b in zip(new_with.body[new_index:new_index+3], declared))
            and len(new_with.body[new_index:new_index+3]) == 3, "exact active-width substitution")
    new_with.body[new_index:new_index+3] = copy.deepcopy(old_with.body[old_index:old_index+2])
    require(same(actual, expected), "complete retained planner after active-width substitution")
    require(profile() == active().encoded.Profile(numerator=1, denominator=577), "active cohort rate profile")
    return {"status": "PASS_ACTIVE_WIDTH_SOURCE_DELTAS", "backend_files": len(active().compared_backend),
            "node_deltas": 1, "root_constructor_deltas": 2, "planner_substitutions": 1,
            "scope": "Complete syntax/body and cohort binding; not a proof of the inherited source mathematics."}
