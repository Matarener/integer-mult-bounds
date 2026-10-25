#!/usr/bin/env python3
"""Pinned C02 paired endpoints, exact gauges and signed B4 controller.

Pure Gaussian convolution routines below retain the original paired_endpoint.py
formulas. Apache-2.0; substantial OpenAI Codex assistance. Native conventions
and B4 recipe retain the PR425/433/523/531 and supplier ancestry.
"""
from collections import Counter
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import sys
import types

class CheckFailure(ValueError):
    def __init__(self, code, witness=None):
        self.code, self.witness = code, witness
        super().__init__(code)

def need(ok, code, witness=None):
    if not ok:
        raise CheckFailure(code, witness)

def payload(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"))+"\n").encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

ONE = ({0:(1,0)},0)
ZERO = ({},0)

def ga(a, b):
    return (a[0]+b[0], a[1]+b[1])

def gm(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])

def gn(a):
    return (-a[0], -a[1])

def norm(p, e):
    p = {x:a for x,a in p.items() if a != (0, 0)}
    if not p:
        return ({}, 0)
    while e and all(not ((r|i)&1) for r,i in p.values()):
        p = {x:(r//2, i//2) for x,(r,i) in p.items()}
        e -= 1
    return (p, e)

def padd(a, b):
    ap, ae = a
    bp, be = b
    e = max(ae, be)
    p = {x:(r << (e-ae), i << (e-ae)) for x,(r,i) in ap.items()}
    for x,(r,i) in bp.items():
        p[x] = ga(p.get(x, (0,0)), (r << (e-be), i << (e-be)))
    return norm(p,e)

def pneg(a):
    return ({x:gn(z) for x,z in a[0].items()}, a[1])

def trans(a, mask):
    return ({x^mask:z for x,z in a[0].items()}, a[1])

def direction(a, mask, sign=1):
    """Apply C_mask^(sign) = ((1+sign*i)I+(1-sign*i)X)/2."""
    p,e = a
    q = {}
    for x,z in p.items():
        q[x] = ga(q.get(x,(0,0)), gm((1,sign),z))
        q[x^mask] = ga(q.get(x^mask,(0,0)), gm((1,-sign),z))
    return norm(q,e+1)

def kernels(axes):
    p = ONE
    for mask,sign in axes:
        p = direction(p,mask,sign)
    return p

def product(a,b):
    p={}
    for x,u in a[0].items():
        for y,v in b[0].items():
            p[x^y]=ga(p.get(x^y,(0,0)),gm(u,v))
    return norm(p,a[1]+b[1])

def conj(a):
    return ({x:(r,-i) for x,(r,i) in a[0].items()},a[1])

def phase_kernel(n, axes):
    """Independently form H diag(i^wt(P_U x)) H from the actual projector."""
    vals=[]
    units=((1,0),(0,1),(-1,0),(0,-1))
    for x in range(1<<n):
        projected=0
        for v in axes:
            if (v&x).bit_count()&1:
                projected ^= v
        vals.append(units[projected.bit_count()%4])
    for bit in range(n):
        step=1<<bit
        for base in range(0,1<<n,step*2):
            for j in range(base,base+step):
                a,b=vals[j],vals[j+step]
                vals[j],vals[j+step]=ga(a,b),ga(a,gn(b))
    return norm(dict(enumerate(vals)),n)

def orthobasis(q,n=9):
    z=next(i for i in range(n) if not(q>>i)&1)
    a=q^(1<<z)
    order=list(range(n));order[z],order[0]=order[0],order[z]
    b=[(1<<i)^(a if (a>>i)&1 else 0) for i in order]
    need(b[0]==q,'port first in chart')
    need(all((u&v).bit_count()%2==int(i==j)
             for i,u in enumerate(b) for j,v in enumerate(b)),'orthogonal chart')
    return b


PINS = {
    "ports": "addf598581d2a20e13d0c18110607515ad90b06125616a2349e53a47bb5b6c80",
    "template": "5b913207775fcd87090cfa8776e8bd2bb872426923345fe1a1a4e1ea84bfae2c",
    "geometry": "e5b1309edbeb5da14d79f1edf134c95593061666b796b5d532f00a4262533dd0",
    "compiler": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
}


def kernel_record(kernel):
    coefficients, denominator = kernel
    return {"denominator_exponent": denominator,
            "coefficients": [[address, real, imag]
                             for address, (real, imag) in sorted(coefficients.items())]}


def kernel_witness(actual, expected):
    difference = padd(actual, pneg(expected))
    need(bool(difference[0]), "missing_kernel_discrepancy")
    address = min(difference[0])
    return {"input_address": 0, "output_address": address,
            "difference_gaussian_numerator": list(difference[0][address]),
            "denominator_exponent": difference[1]}


def accept_kernel(actual, expected, code):
    if actual != expected:
        raise CheckFailure(code, kernel_witness(actual, expected))


def laurent_word(recipe, mutation=None):
    rows = [[{0: 1} if i == j else {} for j in range(8)] for i in range(8)]

    def add(dst, src, coefficient, exponent=0):
        for column, terms in enumerate(rows[src]):
            for power, value in terms.items():
                key = power + exponent
                new = rows[dst][column].get(key, 0) + coefficient * value
                if new:
                    rows[dst][column][key] = new
                else:
                    rows[dst][column].pop(key, None)

    for event in recipe:
        if event["kind"] == "terminal":
            break
        if event["kind"] == "local":
            x, y = 2 * event["pair"], 2 * event["pair"] + 1
            reverse = event["reverse"]
            exponent = -1 if reverse and mutation != "backward_inverse" else 1
            sign = -1 if reverse and mutation != "backward_sign" else 1
            add(x if reverse else y, y if reverse else x, sign, exponent)
        else:
            dst, src, coefficient = event["dst"], event["src"], event["coefficient"]
            add(2 * dst, 2 * src, coefficient)
            add(2 * src + 1, 2 * dst + 1,
                coefficient if mutation == "bridge_sign" else -coefficient)
    return rows


def laurent_target():
    rows = [[{} for _ in range(8)] for _ in range(8)]
    for pair in range(4):
        rows[2 * pair][2 * pair + 1] = {-1: -1}
        rows[2 * pair + 1][2 * pair] = {1: 1}
    return rows


def accept_laurent(actual, expected):
    for row in range(8):
        for col in range(8):
            for power in sorted(actual[row][col].keys() | expected[row][col].keys()):
                delta = actual[row][col].get(power, 0) - expected[row][col].get(power, 0)
                if delta:
                    raise CheckFailure("laurent_endpoint", {
                        "output_bank": row, "input_bank": col,
                        "power_of_z": power, "difference_integer_coefficient": delta})


def native_b4(recipe, k, mutation=None):
    """All convolution columns, with one fresh residual axis at each local call."""
    n = k + 9
    rows = [[ONE if i == j else ZERO for j in range(8)] for i in range(8)]
    frontiers = [-1] * 4
    event_bill = Counter()
    cp, cq = 1, (1 << k) - 2
    common = [(1, -1)] + [(1 << axis, 1) for axis in range(1, k)]

    def dirrow(dst, axes):
        for mask, sign in axes:
            rows[dst] = [direction(value, mask, sign) for value in rows[dst]]

    def align(pair, stage):
        for current in range(frontiers[pair] + 1, stage + 1):
            for bank in (2 * pair, 2 * pair + 1):
                dirrow(bank, [(1 << (k + current), 1)])
                event_bill["idle_residual_field_directions"] += 1
        frontiers[pair] = stage

    def add(dst, src, sign, axes=()):
        source = rows[src]
        for mask, native_sign in axes:
            source = [direction(value, mask, native_sign) for value in source]
        if sign == -1:
            source = [pneg(value) for value in source]
        rows[dst] = [padd(a, b) for a, b in zip(rows[dst], source)]

    for event in recipe:
        kind = event["kind"]
        if kind == "local":
            pair, stage, reverse = event["pair"], event["stage"], event["reverse"]
            align(pair, stage - 1)
            x, y = 2 * pair, 2 * pair + 1
            if reverse and mutation != "backward_translation":
                rows[x] = [trans(value, cp ^ cq) for value in rows[x]]
                event_bill["backward_translation_maps"] += 1
            add(x if reverse else y, y if reverse else x,
                -1 if reverse and mutation != "backward_sign" else 1, common)
            if reverse and mutation != "backward_translation":
                rows[x] = [trans(value, cp ^ cq) for value in rows[x]]
                event_bill["backward_translation_maps"] += 1
            for bank in (x, y):
                dirrow(bank, [(1 << (k + stage), 1)])
                event_bill["local_residual_field_directions"] += 1
            frontiers[pair] = stage
            event_bill["abstract_local_calls"] += 1
        elif kind == "bridge":
            dst, src, coefficient = event["dst"], event["src"], event["coefficient"]
            latest = max(frontiers[dst], frontiers[src])
            align(dst, latest)
            align(src, latest)
            add(2 * dst, 2 * src, coefficient)
            add(2 * src + 1, 2 * dst + 1,
                coefficient if mutation == "bridge_sign" else -coefficient)
            event_bill["bridge_signed_complex_ADDs"] += 2
        else:
            for pair in range(4):
                align(pair, 8)
                x, y = 2 * pair, 2 * pair + 1
                # Literal 3-ADD/NEG swap, then the required sign on old X.
                add(x, y, 1)
                add(y, x, -1)
                add(x, y, 1)
                rows[y] = [pneg(value) for value in rows[y]]
                rows[y] = [pneg(value) for value in rows[y]]
                event_bill["terminal_signed_complex_ADDs"] += 3
                event_bill["terminal_complex_NEGs"] += 2
                if mutation != "terminal_translation":
                    rows[x] = [trans(value, cp) for value in rows[x]]
                    rows[y] = [trans(value, cq) for value in rows[y]]
                    event_bill["terminal_translation_maps"] += 2
    need(frontiers == [8] * 4, "native_complete_residual_frontiers")
    full = kernels([(1 << axis, 1) for axis in range(n)])
    expected = [[full if i == j else ZERO for j in range(8)] for i in range(8)]
    return rows, expected, dict(sorted(event_bill.items()))


def accept_native(rows, expected):
    for output in range(8):
        for source in range(8):
            try:
                accept_kernel(rows[output][source], expected[output][source], "native_B4_endpoint")
            except CheckFailure as error:
                error.witness.update({"output_bank": output, "input_bank": source})
                raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("ports", "template", "geometry", "compiler", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), "output_already_exists")
    raw = {name: getattr(args, name).read_bytes() for name in PINS}
    need({name: sha(value) for name, value in raw.items()} == PINS, "input_byte_pins")
    ports = json.loads(gzip.decompress(raw["ports"]))["ports"]
    template = json.loads(gzip.decompress(raw["template"]))
    geometry = json.loads(raw["geometry"])
    recipe = template["recipe"]
    wanted_recipe = [
        {"kind": "local", "pair": 0, "reverse": False, "stage": 0}]
    for pair in range(4):
        wanted_recipe.append({"kind": "local", "pair": pair, "reverse": True, "stage": 2 * pair + 1})
        if pair < 3:
            wanted_recipe.append({"coefficient": 1, "dst": pair, "kind": "bridge", "src": pair + 1})
        wanted_recipe.append({"kind": "local", "pair": pair, "reverse": False, "stage": 2 * pair + 2})
        if pair < 3:
            wanted_recipe.append({"coefficient": -1, "dst": pair, "kind": "bridge", "src": pair + 1})
    wanted_recipe.extend({"coefficient": 1, "dst": pair + 1, "kind": "bridge", "src": pair}
                         for pair in reversed(range(3)))
    wanted_recipe.append({"kind": "terminal", "pairs": 4})
    need(recipe == wanted_recipe, "complete_signed_B4_source_recipe")
    contracts = [{"P": row["P"], "Q": row["Q"], "R": row["R"]}
                 for row in geometry["contracts"]]
    need(len(ports) == len(set(ports)) == len(contracts) == 112, "complete_port_coverage")
    need([row["P"] for row in contracts] == ports, "geometry_port_order")
    for row in contracts:
        basis = [row["P"], row["Q"]] + row["R"]
        need(len(basis) == 9 and all((u & v).bit_count() % 2 == int(i == j)
                                    for i, u in enumerate(basis) for j, v in enumerate(basis)),
             "geometry_orthonormal_contract")
    ce = types.ModuleType("c02_authenticated_clifford")
    ce.__file__ = "authenticated:clifford_exact.py"
    sys.modules[ce.__name__] = ce
    exec(compile(raw["compiler"], ce.__file__, "exec", dont_inherit=True, optimize=0), ce.__dict__)
    controls = []

    def expect_failure(name, thunk, expected_code):
        try:
            thunk()
        except CheckFailure as error:
            need(error.code == expected_code, "unexpected_control_failure", error.code)
            controls.append({"name": name, "expected_failure": expected_code, "witness": error.witness})
            return
        raise CheckFailure("expected_rejection_missing", name)

    def same(actual, expected, code, phase_guard=True):
        need(actual.tab == expected.tab, code + "_tableau")
        if phase_guard:
            av, ad = actual.zero_state()
            bv, bd = expected.zero_state()
            accept_kernel(norm(dict(enumerate(av)), ad), norm(dict(enumerate(bv)), bd),
                          code + "_phase")

    def chosen(axes):
        op = ce.ident(9)
        for vector in axes:
            need(vector.bit_count() % 2 == 1, "unit_chosen_axis")
            op = op.then(ce.cgate(9, vector, 1 if vector.bit_count() % 4 == 1 else -1))
        return op

    gauges, gauge_ops, endpoint_rows, projector_rows = {}, {}, [], []

    def gauge(axes):
        key = ",".join(map(str, axes))
        if key in gauges:
            return
        canonical, phase = ce.canonical_frame(9, axes), chosen(axes)
        delta = canonical.adjoint().then(phase)
        need(all(x == 0 for x, z, p in delta.tab[9:]), "left_gauge_rank_zero")
        literal, record = ce.monomial(delta)
        same(literal, delta, "left_gauge_lowering")
        same(canonical.then(literal), phase, "left_gauge_actual_bridge")
        same(phase.then(literal.adjoint()), canonical, "inverse_gauge_actual_bridge")
        state, den = phase.zero_state()
        accept_kernel(norm(dict(enumerate(state)), den), phase_kernel(9, axes),
                      "chosen_projector_phase")
        gauges[key] = {"axes": list(axes), "rank": 0, "left_monomial": record,
                       "literal_events": literal.circuit,
                       "inverse_literal_events": literal.adjoint().circuit,
                       "canonical_events": canonical.circuit,
                       "chosen_events": phase.circuit,
                       "zero_column": kernel_record(norm(dict(enumerate(state)), den))}
        gauge_ops[key] = literal

    # Independent projector definition versus native factors at both historic
    # common dimensions. These charts are distinct from the order-3 pairing.
    for port in ports:
        basis = orthobasis(port)
        for k in (2, 3):
            P, Q, R = basis[:1], basis[1:k], basis[k:]
            cp, cq, cr = [phase_kernel(9, axes) for axes in (P, Q, R)]
            full = phase_kernel(9, [1 << axis for axis in range(9)])
            for axes, kernel in ((P, cp), (Q, cq), (R, cr)):
                accept_kernel(kernel, kernels([(v, 1 if v.bit_count() % 4 == 1 else -1)
                                                for v in axes]), "projector_native_factorization")
            up, uq = phase_kernel(9, P + R), phase_kernel(9, Q + R)
            char_p = 0
            char_q = 0
            for vector in P:
                char_p ^= vector
            for vector in Q:
                char_q ^= vector
            kval = product(cq, conj(cp))
            identities = [
                (product(product(cp, cq), cr), full),
                (product(up, conj(cp)), cr), (product(uq, conj(cq)), cr),
                (product(uq, conj(cp)), trans(full, char_p)),
                (conj(kval), trans(kval, char_p ^ char_q)),
                (trans(kval, char_p), product(cp, cq)),
                (trans(conj(kval), char_q), product(cp, cq))]
            for actual, expected in identities:
                accept_kernel(actual, expected, "paired_projector_identity")
            projector_rows.append({"port": port, "common_dimension": k, "P": P, "Q": Q, "R": R,
                                   "source_characteristic": char_p, "target_characteristic": char_q,
                                   "residual_rank": 9 - k,
                                   "exterior_alignment_mask": sum(1 << j for j, v in enumerate(R)
                                                                   if v.bit_count() % 4 == 3)})
    need(len(projector_rows) == 224, "projector_contract_count")

    for index, row in enumerate(contracts):
        p, q, r = row["P"], row["Q"], tuple(row["R"])
        P, Q, U, V = (p,), (q,), (p,) + r, (q,) + r
        for axes in (P, Q, U, V, r):
            gauge(axes)
        cp, cq, cr = chosen(P), chosen(Q), chosen(r)
        native = ce.cgate(9, p)
        shift = p if p.bit_count() % 4 == 3 else 0
        adapter = native.adjoint().then(cp)
        same(adapter, ce.xgate(9, shift), "native_plus_adapter")
        source_residual, target_residual = cp.adjoint().then(chosen(U)), cq.adjoint().then(chosen(V))
        same(source_residual, cr, "source_residual")
        same(target_residual, cr, "target_residual")
        source_record, source_literal = ce.lower_child(source_residual)
        target_record, target_literal = ce.lower_child(target_residual)
        need(source_record["rank"] == target_record["rank"] == 7, "paired_child_rank_seven")
        same(source_literal, cr, "source_child_lowering")
        same(target_literal, cr, "target_child_lowering")
        for entrance, terminal, label in ((P, U, "source"), (Q, V, "target")):
            incoming = gauge_ops[",".join(map(str, entrance))]
            outgoing = gauge_ops[",".join(map(str, terminal))]
            canonical_residual = ce.canonical_frame(9, entrance).adjoint().then(
                ce.canonical_frame(9, terminal))
            wrapped = incoming.then(cr).then(outgoing.adjoint())
            same(wrapped, canonical_residual, "canonical_" + label + "_residual_bridge")
        native_state, native_den = native.zero_state()
        accept_kernel(norm(dict(enumerate(native_state)), native_den), kernels([(p, 1)]),
                      "independent_native_plus_normalization")
        if shift:
            # Actual retained native operator without the required adapter.
            expect_failure("port_" + str(index) + "_omit_native_plus_translation",
                           lambda native=native, cp=cp: same(native, cp, "native_adapter_omission"),
                           "native_adapter_omission_tableau")
        endpoint_rows.append({"port_index": index, "P": p, "Q": q, "R": list(r),
                              "native_plus_to_chosen_translation": shift,
                              "source_child": source_record, "target_child": target_record,
                              "canonical_residual_bridge_verified": True,
                              "source_literal": source_literal.circuit,
                              "target_literal": target_literal.circuit})
    need(len(gauges) == 456 and len(endpoint_rows) == 112, "complete_gauge_endpoint_census")

    # A global phase defect preserves the complete signed Pauli tableau.
    selected_axes = (contracts[0]["P"],) + tuple(contracts[0]["R"])
    canonical, target = ce.canonical_frame(9, selected_axes), chosen(selected_axes)
    delta = canonical.adjoint().then(target)
    phase_i = ce.Op(9, ce.identity(9), [("phase", 1)])
    bad_actual = canonical.then(delta.then(phase_i))
    expect_failure("actual_left_gauge_global_i", lambda: same(bad_actual, target, "gauge_phase"),
                   "gauge_phase_phase")
    same(bad_actual, target, "gauge_phase", phase_guard=False)
    try:
        expect_failure("phase_guard_deleted",
                       lambda: same(bad_actual, target, "gauge_phase", phase_guard=False),
                       "gauge_phase_phase")
    except CheckFailure as error:
        need(error.code == "expected_rejection_missing", "phase_deletion_wrong_failure")
        controls.append({"name": "phase_check_deletion_detected",
                         "expected_failure": error.code, "bad_phase_accepted": True})
    else:
        raise CheckFailure("phase_deletion_not_exercised")
    expect_failure("omit_actual_left_gauge", lambda: same(canonical, target, "gauge_omission"),
                   "gauge_omission_tableau")

    laurent = laurent_word(recipe)
    accept_laurent(laurent, laurent_target())
    for mutation in ("backward_inverse", "backward_sign", "bridge_sign"):
        expect_failure("laurent_" + mutation,
                       lambda mutation=mutation: accept_laurent(laurent_word(recipe, mutation), laurent_target()),
                       "laurent_endpoint")
    native_models = []
    for k in (2, 3):
        rows, expected, event_bill = native_b4(recipe, k)
        accept_native(rows, expected)
        native_models.append({
            "common_dimension": k, "residual_dimension_per_stage": 1, "address_dimension": k + 9,
            "arbitrary_banks": 8, "address_states": 1 << (k + 9),
            "covered_input_basis_columns": 8 * (1 << (k + 9)),
            "kernel_coefficient_positions": 64 * (1 << (k + 9)),
            "coverage_method": "all 8x8 convolution kernels; all translated address columns follow exactly",
            "event_bill_of_finite_model": event_bill,
            "endpoint_kernel_rows": [[kernel_record(value) for value in row] for row in rows]})
        for mutation in ("backward_translation", "backward_sign", "terminal_translation", "bridge_sign"):
            changed, target_rows, _ = native_b4(recipe, k, mutation)
            expect_failure("native_k" + str(k) + "_" + mutation,
                           lambda changed=changed, target_rows=target_rows: accept_native(changed, target_rows),
                           "native_B4_endpoint")
    result = {
        "schema": "paired_complex_endpoint.v1", "status": "PASS", "no_new_kappa": True,
        "scientific_pin": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "checker_sha256": sha(Path(__file__).read_bytes()), "input_sha256": PINS,
        "consumed_geometry_contracts": contracts,
        "geometry_contracts_sha256": sha(json.dumps(
            contracts, sort_keys=True, separators=(",", ":")).encode()),
        "geometry_consumption": "only ordered P,Q,R contracts; old edge census and source-batched DP are not replayed here",
        "data_phases_semantically_replayed": False,
        "data_phases_provenance_only_sha256": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
        "exact_source_recipe": recipe,
        "universal_laurent_endpoint": laurent,
        "laurent_scope": "formal identity over Z[z,z^-1], valid for every invertible endomorphism K; no finite-dimensional or K^2=I premise",
        "projector_models": projector_rows,
        "projector_kernel_factorizations": 672,
        "actual_paired_endpoints": endpoint_rows,
        "canonical_left_gauges": list(gauges.values()),
        "canonical_gauge_count": len(gauges),
        "rank_seven_residual_children": 224,
        "nonidentity_native_plus_adapters": sum(row["native_plus_to_chosen_translation"] != 0
                                               for row in endpoint_rows),
        "native_B4_models": native_models,
        "executed_controls": controls,
        "paid_obligations": {
            "canonical_gauges": "456 distinct phase-bearing left-monomial recipes; usage multiplicity and inverse occurrences must be charged in a local word",
            "canonical_residual_bridge": "For each of the 224 separate canonical residuals, M_E then T_R then M_U^-1 is verified; this unfused implementation adds 448 canonical interface map occurrences in addition to the 448 native-child monomial legs",
            "native_source_adapters": "112 explicit nonzero X_p maps; none is a free phase convention",
            "residual_lowerings": "both monomial legs of each of 224 rank-seven lowerings are retained",
            "backward_K_inverse": "two characteristic translations per abstract reverse call, unless an explicit paid fusion is provided",
            "terminal": "one literal 3-ADD/NEG pair swap plus a separate NEG, and two translations, per pair; no cancellation used in this invoice",
            "not_a_supplier_invoice": True},
        "limits": [
            "The Laurent proof is universal; the native B4 execution has dimensions 11 and 12 with one residual axis per stage.",
            "No execution of a 65-dimensional or 56-dimensional supplier is claimed.",
            "Convolution-kernel equality covers translated address columns; those columns are not separately enumerated program runs.",
            "The order-three geometry and isolated dirty contacts are separate reviewed obligations.",
            "No compatible cheaper whole local word, paid canonical/native adapter usage schedule, precision, helper owner, physical stock or kappa conclusion."
        ]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS: 112 paired ports; 456 exact gauges; 224 rank-7 residuals; universal Laurent B4; native dimensions 11/12")


if __name__ == "__main__":
    main()

