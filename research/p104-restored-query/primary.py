"""Source-bound producer, first collector, and selective return composition.

The inherited PR3467 encoder and PR3382 arithmetic are reused with attribution.
This new composition does not execute the omitted full-prefix recipients.
Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
"""

from collections import Counter
from fractions import Fraction


class CallerError(ValueError):
    """A chronological, arithmetic, restoration or observation check failed."""


def require(condition, message):
    if not condition:
        raise CallerError(message)


def setup(context):
    word, native = context["word"], context["native"]
    source, model = context["source"], context["model"]
    structure = source.structure(word, native)
    collector = list(range(2025, 2040))
    require([word["program"][e][0] for e in collector] ==
            ["zero"] + ["add"] * 5 + ["transport", "add", "transport"]
            + ["add"] * 5 + ["erase"], "literal first collector shape")
    compensation = [e for e, _ in structure["q_reads"]]
    require(compensation == [908, 910, 912, 914, 916], "five dirty compensations")
    require(structure["cut_paths"]["Q7"] == [972], "actual Q frame path")
    slots = [i for i, row in enumerate(structure["gaps"])
             if row["kind"] == "terminal"]
    require(slots == [2, 9, 16, 27, 51], "source-derived terminal slot indices")
    plans = source.native_plans(word, native, structure["selected"] + collector, model)
    return {**context, "structure": structure, "plans": plans,
            "collector": collector, "compensation": compensation,
            "terminal_slots": slots}


def steps(context, full_inverse=False, omit_return_frame=False):
    selected = context["structure"]["selected"]
    result = [(e, False, "producer") for e in selected]
    result += [(e, False, "collector") for e in context["collector"]]
    result += [(e, True, "return") for e in reversed(selected)
               if (full_inverse or e not in context["compensation"])
               and not (omit_return_frame and e == 972)]
    return result


def wrapper_inventory(plan, inverse):
    permutation = [target for target, _ in plan]
    require(sorted(permutation) == list(range(512)), "wrapper permutation")
    visited = set()
    cycles = 0
    for start in range(512):
        if start in visited:
            continue
        cycles += 1
        current = start
        while current not in visited:
            visited.add(current)
            current = permutation[current]
    phases = Counter(str((-phase if inverse else phase) % 4)
                     for _, phase in plan)
    return {"gaussian_swaps": 512 - cycles, "cycles": cycles,
            "phase_histogram": {str(i): phases[str(i)] for i in range(4)}}


def inventory(context):
    word = context["word"]["program"]
    counts = Counter()
    phases = Counter()
    event_rows = []
    for event, inverse, leg in steps(context):
        record = word[event]
        counts["events"] += 1
        counts[record[0]] += 1
        event_rows.append([event, inverse, leg])
        if record[0] == "transport":
            rank = record[4]
            counts["rank_mass"] += rank
            counts["native_pairs"] += rank * 256
            counts["native_inverse_pairs" if inverse else "native_forward_pairs"] += rank * 256
            for side in ("left", "right"):
                item = wrapper_inventory(context["plans"][event][side], inverse)
                counts["wrapper_occurrences"] += 1
                counts["wrapper_gaussian_swaps"] += item["gaussian_swaps"]
                counts["wrapper_cycles"] += item["cycles"]
                phases.update(item["phase_histogram"])
        if record[0] == "add":
            value = Fraction(str(record[3]))
            require(value.denominator in (1, 4), "caller scalar alphabet")
            counts["quarter_adds" if value.denominator == 4 else "unit_adds"] += 1
    counts["real_add_sub_before_wrapper_and_phase_lowering"] = (
        8 * counts["native_pairs"] + 1024 * counts["add"])
    counts["real_native_floor_halves"] = 4 * counts["native_pairs"]
    counts["real_exact_quarter_halves"] = 2048 * counts["quarter_adds"]
    counts["real_quarter_donor_restoration_doublings"] = 2048 * counts["quarter_adds"]
    counts["native_gaussian_quarter_turns"] = counts["native_pairs"]
    require((counts["events"], counts["transport"], counts["rank_mass"],
             counts["native_pairs"], counts["add"], counts["quarter_adds"]) ==
            (524, 402, 722, 184832, 120, 104), "complete literal caller inventory")
    return {"counts": dict(sorted(counts.items())),
            "wrapper_phase_histogram": {str(i): phases[str(i)] for i in range(4)},
            "events": event_rows,
            "scope": "Core only; both PR3467 codec directions are additional. "
                     "SWAP, phase, routing, ownership and recursive charges are separate."}


def apply_native(values, event, inverse, context, counters, phase_mutant=False):
    model, source = context["model"], context["source"]
    plan = context["plans"][event]
    out = source.apply_wrapper(values, plan["left" if inverse else "right"], model, inverse)
    bits = reversed(range(plan["rank"])) if inverse else range(plan["rank"])
    for bit in bits:
        stride = 1 << bit
        for address in range(512):
            if address & stride:
                continue
            other = address | stride
            a, b = out[address], out[other]
            twice = model.ideal_pair_numerators(a, b, inverse=inverse)
            require(all(x % 2 == 0 for value in twice for x in value),
                    "nonintegral ideal native pair at event " + str(event))
            ideal = tuple((a // 2, b // 2) for a, b in twice)
            actual = model.lift_pair(a, b, inverse=inverse)
            require(actual == ideal, "literal/ideal native mismatch")
            out[address], out[other] = actual
            counters["native_pairs"] += 1
    out = source.apply_wrapper(out, plan["right" if inverse else "left"], model, inverse)
    if phase_mutant:
        out = [(-a, -b) for a, b in out]
    counters["native_occurrences"] += 1
    return out


def execute(context, initial, *, full_inverse=False, omit_return_frame=False,
            collector_phase_mutant=False, return_sign_mutant=False):
    source, model, word = context["source"], context["model"], context["word"]["program"]
    require(set(initial) == set(context["structure"]["dependencies"]), "exact initial roles")
    require(all(type(values) is list and len(values) == 512 for values in initial.values()),
            "all initial banks must have exactly512 Gaussian entries")
    require(all(type(value) in (tuple, list) and len(value) == 2
                and all(type(x) is int for x in value)
                for values in initial.values() for value in values),
            "exact Gaussian integer component types")
    require(all(model.member(value) for value in initial.values()), "initial B9 admission")
    state = {name: values[:] for name, values in initial.items()}
    frames = {name: [] for name in initial}
    counters = Counter()
    cut = None
    max_component = max(abs(x) for values in state.values() for value in values for x in value)
    for event, inverse, leg in steps(context, full_inverse, omit_return_frame):
        record = word[event]
        opcode, bank = record[:2]
        if event == 2025:
            cut = {name: state[name][:] for name in source.TARGETS}
        if opcode == "zero":
            require(not inverse and bank not in state, "fresh private zero")
            state[bank], frames[bank] = [(0, 0)] * 512, record[2][:]
        elif opcode == "erase":
            require(not inverse and frames[bank] == record[2], "private erase frame")
            require(all(value == (0, 0) for value in state[bank]), "private C not zero at erase")
            del state[bank], frames[bank]
            counters["literal_zero_erases"] += 1
        elif opcode == "transport":
            old, new = (record[3], record[2]) if inverse else (record[2], record[3])
            require(frames[bank] == old, "native chronological entrance frame")
            state[bank] = apply_native(state[bank], event, inverse, context, counters,
                                      collector_phase_mutant and event == 2031)
            frames[bank] = new[:]
        else:
            require(opcode == "add", "caller opcode")
            donor, raw, frame = record[2:]
            require(frames[bank] == frames[donor] == frame, "common physical ADD frame")
            factor = Fraction(str(raw)) * (-1 if inverse else 1)
            if return_sign_mutant and leg == "return" and event == 1831:
                factor = -factor
            p, q = factor.numerator, factor.denominator
            require(all(p * x % q == 0 for value in state[donor] for x in value),
                    "unavailable exact fractional ADD at event " + str(event))
            state[bank] = [(a + p * c // q, b + p * d // q)
                           for (a, b), (c, d) in zip(state[bank], state[donor])]
            counters["weighted_adds"] += 1
        if bank in state:
            max_component = max(max_component, *(abs(x) for value in state[bank] for x in value))
        counters["events"] += 1
    require(cut is not None, "producer cut was observed")
    return {"state": state, "frames": frames, "cut": cut,
            "counts": dict(counters), "max_component": max_component}


def endpoint(context, execution, initial, parameters):
    source, model = context["source"], context["model"]
    state = execution["state"]
    require(set(state) == set(initial), "returned public roles and erased private role")
    require(all(frame == [] for frame in execution["frames"].values()), "empty returned frames")
    require(all(state[name] == initial[name] for name in source.YS + source.D_BANKS),
            "source or dirty D restoration failed")
    total = [(0, 0)] * 512
    for slot in context["terminal_slots"]:
        total = [model.add(a, b) for a, b in zip(total, parameters[slot])]
    expected = [model.add(a, b) for a, b in zip(initial["Q7"], model.encode(total))]
    require(state["Q7"] == expected, "Q coefficient intertwiner failed")
    recovered = context["admission"].decode_sources(
        context["structure"], context["plans"], model, source, context["classifier"],
        {name: state[name] for name in source.YS})
    require(recovered == parameters, "all52 coefficient banks must return")
    return recovered


def negative_controls(context, initial, parameters, result):
    """Named dense controls; their witnesses must have nonzero readouts."""
    source, model = context["source"], context["model"]
    bad = execute(context, initial, full_inverse=True)
    dirty_sum = [(0, 0)] * 512
    for name in source.D_BANKS:
        dirty_sum = [model.add(a, b) for a, b in zip(dirty_sum, initial[name])]
    difference = [model.sub(a, b) for a, b in zip(bad["state"]["Q7"], result["state"]["Q7"])]
    require(difference == dirty_sum and any(x != (0, 0) for x in difference),
            "full inversion must expose the nonzero exact dirty-sum error")
    controls = {"full_inverse_dirty_error": {"difference_sha256": source.digest(difference),
                 "nonzero_coordinates": sum(v != (0, 0) for v in difference)}}
    for name, kwargs in (("missing_Q_return_frame", {"omit_return_frame": True}),
                         ("wrong_collector_global_phase", {"collector_phase_mutant": True}),
                         ("wrong_return_quarter_sign", {"return_sign_mutant": True})):
        try:
            mutated = execute(context, initial, **kwargs)
            endpoint(context, mutated, initial, parameters)
        except CallerError as error:
            controls[name] = {"rejected": True, "reason": str(error)}
        else:
            raise CallerError("semantic mutation was accepted: " + name)
    return controls


def analyze(raw_context, parameters=None, initial_dirty=None, *, run_negative_controls=False):
    """Execute valid inputs; enable witness-dependent controls only for the dense gate."""
    context = setup(raw_context)
    source, model = context["source"], context["model"]
    if parameters is None:
        parameters = [source.coefficient_fixture(slot) for slot in range(52)]
    if initial_dirty is None:
        initial_dirty = {name: model.encode(source.coefficient_fixture(slot))
                         for slot, name in enumerate(source.TARGETS, start=52)}
    initial_y = context["admission"].encode_sources(
        context["structure"], context["plans"], model, source,
        context["classifier"], parameters)
    initial = {**initial_y, **{name: value[:] for name, value in initial_dirty.items()}}
    result = execute(context, initial)
    coefficients = endpoint(context, result, initial, parameters)
    require(result["cut"] == context["admission"].expected_cut(
        initial, context["structure"], context["plans"], model, source),
        "all six full-array cut equations")
    controls = negative_controls(context, initial, parameters, result) if run_negative_controls else {}
    return {"receipt": {
                "status": "PASS_SOURCE_BOUND_RESTORED_QUERY",
                "terminal_slots": context["terminal_slots"],
                "terminal_sources": [context["structure"]["gaps"][i]["source"]
                                     for i in context["terminal_slots"]],
                "cut_frames": context["structure"]["cut_frames"],
                "compensation_events_not_reversed": context["compensation"],
                "counts": result["counts"],
                "observed_core_bank_event_boundary_component_max": result["max_component"],
                "initial_sha256": source.digest(initial),
                "cut_sha256": source.digest(result["cut"]),
                "output_q_sha256": source.digest(result["state"]["Q7"]),
                "returned_coefficients_sha256": source.digest(coefficients),
                "full_array_cut_equations_checked": 6,
                "returned_coefficient_banks": 52, "returned_dirty_D_banks": 5,
                "negative_controls_executed": run_negative_controls,
                "controls": controls, "inventory": inventory(context)},
            "initial_y": initial_y, "initial_dirty": initial_dirty,
            "returned_y": {name: result["state"][name] for name in source.YS},
            "cut": result["cut"],
            "returned_coefficients": coefficients,
            "returned_dirty": {name: result["state"][name] for name in source.D_BANKS},
            "output_q": result["state"]["Q7"], "parameters": parameters,
            "context": context}
