"""Compare actual encoded root plans with a separate integer specification."""

from active_sources import require


def run():
    from active_plan import ActiveWidthPlan
    from cardinal_counts import Count
    from check_support import no_decode
    from root_plan import FIELDS, RootPlan
    from words import BLANK, RIGHT

    def value(count):
        result = 0
        for index, bit in enumerate(count.tape.cells[1:]):
            if bit == RIGHT:
                return result
            require(bit in (0, 1), "canonical observed Count")
            result += bit << index
        raise ValueError("unterminated observed Count")

    def oracle(p, g, left, right, coefficients, rows, residue):
        d = max(1, g)
        K = 1
        while (K+1)**500 <= d:
            K += 1
        G = 4*(p-1).bit_length()+6
        H = d*G
        depth, cursor = 0, d
        while cursor >= 2:
            cursor //= 2
            depth += 1
        q0 = 2*depth
        qF, qB = -(-2*H//K), -(-H//K)
        Q0 = q0+qF+qB
        require(g <= Q0, "bounded planning fixture uses the production fallback formula")
        result = dict(precision=p, selected=g, left=left, right=right, coefficients=coefficients,
                      outer_rows=rows, residue=residue, zero=0, d=d, K=K, G=G, H=H, depth=depth,
                      q0=q0, qF=qF, qB=qB, Q0=Q0, delta=4*d, input_bits=p+2,
                      work_bits=p+8*d+3, gaussians=(1 << (left+g*K+right))*coefficients*rows,
                      core_width=0, core_front=0, core_back=0, row_bits=0,
                      prefixes=1, original_rows=1, padded_rows=1, stock=1)
        require(set(result) == set(FIELDS), "complete independent plan specification")
        return result

    plan = ActiveWidthPlan(2, 1, 4, guard_exponent=2)
    reports = []
    comparison_raw = (5, 2, 1, 0, 2, 1, 0)
    comparison = None
    for raw in ((2, 0, 1, 2, 3, 2, 0), (2, 1, 0, 1, 1, 1, 0),
                comparison_raw, (8, 6, 0, 2, 1, 3, 0)):
        counts = tuple(Count.literal(x) for x in raw)
        before = tuple(bytes(x.tape.cells) for x in counts)
        with no_decode():
            plan.compute(*counts)
        observed = {name: value(plan.count(name)) for name in FIELDS}
        require(observed == oracle(*raw) and not plan.fast, "literal actual-width plan")
        require(tuple(bytes(x.tape.cells) for x in counts) == before and not plan.pool.live,
                "planner borrows inputs and closes scratch")
        reports.append({"precision": raw[0], "selected": raw[1], "d": observed["d"],
                        "H": observed["H"], "gaussians": observed["gaussians"]})
        if raw == comparison_raw:
            comparison = observed
        plan.clear()
        require(all(t.read() == BLANK for t in plan.roles.values()), "plan role cleanup")
        for count in counts:
            count.close()
    require(comparison is not None, "observed actual-width comparison plan")
    counts = tuple(Count.literal(x) for x in comparison_raw)
    old = RootPlan(2, 1, 4, guard_exponent=2)
    with no_decode():
        old.compute(*counts)
    require(value(old.count("d")) == 4 and comparison["d"] == 2
            and value(old.count("H")) > comparison["H"], "old precision-width plan differs")
    old.clear()
    for count in counts:
        count.close()
    counts = tuple(Count.literal(x) for x in (2, 2, 0, 0, 1, 1, 0))
    before = tuple(bytes(x.tape.cells) for x in counts)
    try:
        with no_decode():
            plan.compute(*counts)
    except ValueError as exc:
        require(str(exc) == "selected width within root domain", "specific root cap rejection")
    else:
        raise ValueError("out-of-domain selected width accepted")
    require(tuple(bytes(x.tape.cells) for x in counts) == before and plan.closed
            and not plan.pool.live and all(t.read() == BLANK for t in plan.roles.values()),
            "rejected plan preserves borrowed inputs and clears owned work")
    for count in counts:
        count.close()
    return {"status": "PASS_ACTIVE_WIDTH_ENCODED_PLANS", "plans": reports,
            "old_planner_control": {"precision": 5, "selected": 2, "old_d": 4, "new_d": comparison["d"]},
            "root_cap_rejected": True,
            "scope": "Actual formulas with reduced fixed constants; no production fast payload."}
