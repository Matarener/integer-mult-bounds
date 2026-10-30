"""Constructive coordinates for the source-bound exact producer entrance.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
This is a parameterisation of new source values, not a repair of a caller's
existing values or a claim about any omitted prefix/recipient arithmetic.
"""


def encode_sources(structure, plans, model, source, classifier, parameters):
    source.require(type(parameters) is list and len(parameters) == 52,
                   "52 independent partial-sum coefficient banks")
    partials = []
    for gap, coefficients in zip(structure["gaps"], parameters):
        value = classifier.encode_profile(coefficients, gap["kind"])
        if gap["kind"] == "rank_one":
            plan = plans[gap["transport_event"]]
            value = source.apply_wrapper(value, plan["right"], model, inverse=True)
        if gap["kind"] != "terminal":
            value = source.apply_path(value, gap["path_to_read"], plans, model, inverse=True)
        partials.append(value)
    initial_y = {}
    offset = 0
    for bank in source.D_BANKS:
        rows = structure["groups"][bank]
        count = len(rows)
        values = classifier.prefix_difference(partials[offset:offset + count])
        initial_y.update((row["source"], value) for row, value in zip(rows, values))
        offset += count
    source.require(offset == 52 and set(initial_y) == set(source.YS), "complete source encoder")
    return initial_y


def decode_sources(structure, plans, model, source, classifier, initial_y):
    source.require(set(initial_y) == set(source.YS), "exact52 source roles")
    source.require(all(model.member(values) for values in initial_y.values()), "initial source B domain")
    partials = []
    for bank in source.D_BANKS:
        rows = structure["groups"][bank]
        partials.extend(classifier.prefix_sum([initial_y[row["source"]] for row in rows]))
    parameters = []
    for gap, value in zip(structure["gaps"], partials):
        if gap["kind"] != "terminal":
            value = source.apply_path(value, gap["path_to_read"], plans, model)
        if gap["kind"] == "rank_one":
            value = source.apply_wrapper(value, plans[gap["transport_event"]]["right"], model)
        parameters.append(classifier.decode_profile(value, gap["kind"]))
    return parameters


def dense_fixture(structure, plans, model, source, classifier):
    parameters = [source.coefficient_fixture(slot) for slot in range(52)]
    initial = encode_sources(structure, plans, model, source, classifier, parameters)
    for slot, name in enumerate(source.TARGETS, start=52):
        initial[name] = model.encode(source.coefficient_fixture(slot))
    recovered = decode_sources(structure, plans, model, source, classifier,
                               {name: initial[name] for name in source.YS})
    source.require(recovered == parameters, "all52 actual-path source codec inverses")
    return initial


def expected_cut(initial, structure, plans, model, source):
    """PR3426's inherited ideal rows, checked against the literal dense trace."""
    outputs = {}
    for bank in source.D_BANKS:
        total = [(0, 0)] * source.SIZE
        for row in structure["groups"][bank]:
            total = [model.add(a, b) for a, b in zip(total, initial[row["source"]])]
        source.require(all(x % 4 == 0 for value in total for x in value), "terminal quarter integral")
        normalised = [model.add(a, (b[0] // 4, b[1] // 4))
                      for a, b in zip(initial[bank], total)]
        outputs[bank] = source.apply_path(normalised, structure["cut_paths"][bank], plans, model)
    q = initial["Q7"][:]
    for bank in source.D_BANKS:
        q = [model.sub(a, b) for a, b in zip(q, initial[bank])]
    outputs["Q7"] = source.apply_path(q, structure["cut_paths"]["Q7"], plans, model)
    return outputs


def control_initials(structure, plans, model, source):
    first = min((gap for gap in structure["gaps"] if gap["kind"] == "rank_one"),
                key=lambda gap: gap["event"])
    rows = structure["groups"][first["bank"]]
    position = next(i for i, row in enumerate(rows) if row["event"] == first["event"])
    following = rows[position + 1]["source"]
    output = {}
    for kind in ("quarter", "native"):
        value = [(1, 0)] * source.SIZE if kind == "quarter" else [
            (-4, 0) if k & 1 else (0, 0) for k in range(source.SIZE)]
        if kind == "native":
            value = source.apply_wrapper(value, plans[first["transport_event"]]["right"],
                                         model, inverse=True)
        value = source.apply_path(value, first["path_to_read"], plans, model, inverse=True)
        initial = {name: [(0, 0)] * source.SIZE for name in structure["dependencies"]}
        initial[first["source"]] = value
        initial[following] = [(-a, -b) for a, b in value]
        source.require(all(model.member(v) for v in initial.values()), "control initial B domain")
        output[kind] = initial
    paired = {name: [(0, 0)] * source.SIZE for name in structure["dependencies"]}
    paired["Y27"][0] = (64, 0)
    paired["Y26"][0] = (-64, 0)
    output["paired64"] = paired
    return output
