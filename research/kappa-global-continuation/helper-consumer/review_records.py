#!/usr/bin/env python3
"""Independent review of the routed alternating-record algebra and its scope.

Does not import the author's record construction or matrix functions. Exact
rational/free-word checks are supplemented by native source and private-stock
bindings. No new kappa or optimized native U/V tariff is certified.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum((x * y for x, y in zip(row, col)), Q()) for col in zip(*b)] for row in a]


def plus(a, b):
    return [[x + y for x, y in zip(row, other)] for row, other in zip(a, b)]


def mv(a, v):
    return [sum((x * y for x, y in zip(row, v)), Q()) for row in a]


def inverse(a):
    n = len(a)
    b = [row[:] + erow for row, erow in zip(a, eye(n))]
    for col in range(n):
        pivot = next(r for r in range(col, n) if b[r][col])
        b[col], b[pivot] = b[pivot], b[col]
        value = b[col][col]
        b[col] = [x / value for x in b[col]]
        for r in range(n):
            if r != col and b[r][col]:
                value = b[r][col]
                b[r] = [x - value * y for x, y in zip(b[r], b[col])]
    return [row[n:] for row in b]


def realify(packed):
    """Read Gaussian coefficients as exact real 2x2 blocks."""
    rows, cols = len(packed), len(packed[0])
    out = [[Q() for _ in range(2 * cols)] for _ in range(2 * rows)]
    for i, row in enumerate(packed):
        for j, value in enumerate(row):
            r, im = Q(value[0], value[1]), Q(value[2], value[3])
            need(r.denominator & (r.denominator - 1) == 0 and im.denominator & (im.denominator - 1) == 0,
                 "record left inverse must remain Gaussian dyadic")
            out[2*i][2*j], out[2*i][2*j+1] = r, -im
            out[2*i+1][2*j], out[2*i+1][2*j+1] = im, r
    return out


def action(columns, value):
    result = 0
    while value:
        low = value & -value
        result ^= columns[low.bit_length() - 1]
        value ^= low
    return result


def bank_factors(recipe):
    """Derive right factors directly from the ordinary actual bank schedule."""
    prefix, factors = eye(8), []
    for item in recipe:
        kind = item["kind"]
        if kind in ("exchange", "terminal"):
            break
        step = eye(8)
        if kind == "bridge":
            d, s, coefficient = item["dst"], item["src"], item["coefficient"]
            step[2*d][2*s] += coefficient
            step[2*s+1][2*d+1] -= coefficient
        else:
            need(kind == "local", "actual scalar bank recipe grammar")
            p, backwards = item["pair"], item["reverse"]
            left, right = [Q()] * 8, [Q()] * 8
            if backwards:
                step[2*p][2*p+1] -= 1
                left[2*p] = left[2*p+1] = right[2*p+1] = Q(1)
            else:
                step[2*p+1][2*p] += 1
                left[2*p] = right[2*p] = Q(1)
            ai = mv(inverse(prefix), left)
            bi = mm([right], prefix)[0]
            need(sum(x*y for x, y in zip(ai, bi)) == 1, "right bank factor is a projection")
            factors.append((ai, bi))
        prefix = mm(step, prefix)
    need(len(factors) == 9, "nine actual bank factors")
    return factors


def free_word_identity():
    # Expand E0...E8 without commuting factors. A nonempty word i0<i1<...<ik
    # becomes U_i0 G_i0,i1 ... G_ik-1,ik V_ik. Upper triangular paths are
    # exactly these words. This is a complete free-algebra identity.
    expanded = {()}
    for stage in range(9):
        expanded |= {word + (stage,) for word in tuple(expanded)}
    paths = {word for size in range(1, 10) for word in combinations(range(9), size)}
    need(expanded - {()} == paths and len(paths) == 511, "complete ordered free-word expansion")
    need(any(tuple(reversed(word)) not in paths for word in paths if len(word) > 1), "order is not silently commuted")
    return dict(nonempty_free_words=511,
        identity="E0 E1 ... E8 = I + U (I-G_upper)^-1 V over arbitrary noncommuting operator entries",
        inverse_reason="V_j U_j=-2I implies E_j^2=I; therefore the displayed product is the inverse of E8 ... E0.")


def noncommuting_fixture():
    n, blocks = 8, 9
    us, vs, es = [], [], []
    for j in range(blocks):
        transform = eye(n)
        for round_ in range(3):
            for r in range(n):
                source = (r + 1 + (j + round_) % (n - 1)) % n
                coefficient = Q((j + 2*r + round_) % 3 - 1)
                transform[r] = [x + coefficient*y for x, y in zip(transform[r], transform[source])]
        inv = inverse(transform)
        u = [row[:2] for row in transform]
        v = [[-2*x for x in row] for row in inv[:2]]
        need(mm(v, u) == [[Q(-2*(i == k)) for k in range(2)] for i in range(2)], "fixture diagonal Gram")
        e = plus(eye(n), mm(u, v))
        need(mm(e, e) == eye(n), "fixture local involution")
        us.append(u); vs.append(v); es.append(e)
    gram = [[mm(v, u) for u in us] for v in vs]
    all_blocks = [g for row in gram for g in row]
    need(any(mm(x, y) != mm(y, x) for x in all_blocks for y in all_blocks), "genuinely noncommuting block fixture")
    product = eye(n)
    for e in es:
        product = mm(e, product)
    def solve(output, reverse=True, all_outputs=True, arithmetic_erase=True):
        q = [mv(v, output) for v in vs]
        for i in (range(8, -1, -1) if reverse else range(9)):
            for j in range(i+1, 9):
                q[i] = [x+y for x, y in zip(q[i], mv(gram[i][j], q[j]))]
        restored = output[:]
        for u, value in zip(us, q):
            change = mv(u, value)
            restored = [x + (y if all_outputs or k < 4 else 0) for k, (x, y) in enumerate(zip(restored, change))]
        if arithmetic_erase:
            for i in range(8, -1, -1):
                for j in range(i):
                    q[i] = [x-y for x, y in zip(q[i], mv(gram[i][j], q[j]))]
            for i, v in enumerate(vs):
                q[i] = [x+y for x, y in zip(q[i], mv(v, restored))]
        return restored, q
    for column in range(n):
        initial = [Q(i == column) for i in range(n)]
        restored, q = solve(mv(product, initial))
        need(restored == initial and not any(x for block in q for x in block), "noncommuting full-state inverse and arithmetic query erasure")
    dirty = [Q(3*i - 8, i+1) for i in range(n)]
    output = mv(product, dirty)
    need(solve(output)[0] == dirty, "nonzero arbitrary data and extra state")
    need(solve(output, reverse=False)[0] != dirty, "wrong triangular order rejected")
    need(solve(output, all_outputs=False)[0] != dirty, "omitted dirty extra restoration rejected")
    need(any(x for block in solve(output, arithmetic_erase=False)[1] for x in block), "query cleanup is a real operation")
    return dict(state_columns=n, query_blocks=9, operator_block_dimension=2,
        gram_blocks_do_not_commute=True, all_state_columns_and_dirty_case_restored=True,
        arithmetic_cleanup="descending(I-G_lower) followed by V of the restored state gives exact zero",
        controls_rejected=["wrong upper solve order", "omitted dirty extra scatter", "omit query cleanup"],
        scope="Independent exact rational noncommuting fixture, not a simulation of the73-axis owner space.")


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument("--followup", type=Path, required=True)
    ap.add_argument("--package", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    package, src = a.package.resolve(), a.followup.resolve()
    transition = package.parent / "symmetric-transition"
    result_path = package / "evidence/ALTERNATING-RECORDS-RESULT.json"
    ir_path = package / "evidence/ALTERNATING-CONSUMER-IR.json.gz"
    author = read(result_path)
    ir_bytes = gzip.decompress(ir_path.read_bytes())
    need(sha256(ir_bytes).hexdigest() == author["consumer_ir_payload_sha256"], "complete author IR payload")
    ir = json.loads(ir_bytes)
    route_bytes = gzip.decompress((transition / "evidence/ROUTES.json.gz").read_bytes())
    need(sha256(route_bytes).hexdigest() == ir["routes_payload_sha256"], "actual routed record binding")
    routes = json.loads(route_bytes)
    alternate = read(transition / "evidence/ALTERNATING-RESULT.json")
    native_source = src / "artifact/recovered-involutory/modern_native_component.py"
    need(digest(native_source) == "f6769f1ecd6b2e582748805b3afcf4c65824ba108ce7f23a4d011c45f8b724de", "retained native grammar pin")
    template_path = src / "artifact/live-source/research/staged544-producer-return/inputs/TEMPLATE.json.gz"
    need(digest(template_path) == "21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e", "actual ordinary controller template")
    factors = bank_factors(read(template_path)["recipe"])
    for j, (ai, bi) in enumerate(factors):
        need(ai == ir["query_images"][j]["bank_vector"] and bi == ir["query_gather"][j]["bank_vector"], "independently derived actual bank factors")
    gram_bank = [[sum(x*y for x, y in zip(factors[i][1], factors[j][0])) for j in range(9)] for i in range(9)]
    expected_upper = [dict(target_query_block=i, source_solved_block=j, gram_bank_coefficient=int(gram_bank[i][j]))
                      for i in range(8, -1, -1) for j in range(i+1, 9) if gram_bank[i][j]]
    expected_lower = [dict(target_query_block=i, source_original_block=j, subtract_gram_bank_coefficient=int(gram_bank[i][j]))
                      for i in range(8, -1, -1) for j in range(i) if gram_bank[i][j]]
    need(ir["upper_triangular_word"] == expected_upper and ir["cleanup_lower_triangular_word"] == expected_lower,
         "actual routed upper and lower word ordering")
    r = [[Q(row.get(str(p), "0")) for p in range(112)] for row in ir["R"]]
    need(mm(r, list(map(list, zip(*r)))) == [[Q(56*(i == j)) for j in range(8)] for i in range(8)], "actual R Gram56I")
    for i in range(9):
        alpha = ir["query_gather"][i]["alpha_j"]
        need(alpha == (-4 if i % 2 else 4), "actual alternating sign")
        need(-gram_bank[i][i] * Q(56 + alpha*alpha - 64, 4) == -2, "all actual routed diagonal Gram blocks-2I")
    C, left = realify(ir["record_coefficient_matrix_C"]), realify(ir["record_left_inverse"])
    need(mm(left, C) == eye(18), "independent realified record left inverse")
    for j in range(9):
        rho = routes[f"{j}:112"]["owner_right_matrix_columns"]
        need(all(routes[f"{j}:{p}"]["owner_right_matrix_columns"] == rho for p in range(112, 128)), "common zero-port route")
        need(all(action(rho, action(rho, 1 << k)) == 1 << k for k in range(73)), "actual zero-port inverse")
    # Bind the proposed terminal query capacity to the retained private pool.
    inp = src / "artifact/recovered-involutory/modern-source/inputs"
    receipt = read(inp / "NATIVE-RECEIPT.json")
    programs_checked, release_counts = {}, {}
    for provider in ("base", "extra"):
        item = receipt["providers"][provider]
        word_path = inp / "native-cache" / item["word_sha256"] / "local/CANONICAL-WORD.json.gz"
        need(digest(word_path) == item["complete_native_files"]["local/CANONICAL-WORD.json.gz"], "native buffer role source")
        word = read(word_path)
        need(len(word["zero_buffers"]) == len(set(word["zero_buffers"])) == 91, "91 distinct retained owned zero roles")
        raw = gzip.decompress((transition / f"evidence/ALTERNATING-PROGRAMS-{provider}.json.gz").read_bytes())
        expected_hash = alternate["providers"][provider]["emitted_payload_sha256"]
        need(sha256(raw).hexdigest() == expected_hash == author["native_alternating_provider_payloads"][provider], "actual native alternating word")
        programs_checked[provider] = expected_hash
        for orientation, events in json.loads(raw).items():
            live, released = set(), set()
            for event in events:
                if event[0] != "zero_buffer":
                    continue
                _, action_, role = event
                if action_ == "alloc":
                    need(role in word["zero_buffers"] and role not in live, "private role allocation lifetime")
                    live.add(role)
                else:
                    need(role in live, "private role release lifetime")
                    live.remove(role); released.add(role)
            need(not live and released == set(word["zero_buffers"]), "all91 slots released before terminal reuse")
            release_counts[f"{provider}:{orientation}"] = len(released)
    clear = ir["admitted_owned_clear_alternative"]
    need(clear["events"] == [["scalar", ["clear", ["C", q]], 0] for q in range(72)], "72 literal owned query clear opcodes")
    need(clear["real_scalar_primitives"] == 2 * 72 == 144, "owned clear cost")
    need(clear["grammar_source_sha256"] == digest(native_source), "clear grammar source binding")
    # The checker source explicitly permits an arbitrary C index for core clear;
    # the older boundary helper is a serial C0 example, not a ban on other C's.
    native_text = native_source.read_text()
    need("need(target[0] == 'C', 'only query scratch cleared')" in native_text and
         "private.pop(target, None)" in native_text, "actual core admits owned scratch clear")
    allocation = read(package.parent / "invoice-analysis/evidence/RESULT.json")["m73_literal_allocation"]
    W, physical = allocation["productive_candidate"], allocation["physical_family_upper"]
    need(physical == W + 376 + 8 + 91 + 2, "actual retained private-stock envelope")
    binding = [dict(query=q, local_zero_role=word["zero_buffers"][q], physical_family=W + 384 + q) for q in range(72)]
    need(len({v["physical_family"] for v in binding}) == 72 and all(W <= v["physical_family"] < physical - 2 for v in binding),
         "explicit72-slot injection within existing private stock")
    need(clear["proposed_owned_field_map"] == [dict(query=q, retained_zero_buffer_role=word["zero_buffers"][q],
            physical_family_formula=f"W+384+{q}") for q in range(72)], "author proposed slot map agrees")
    out = dict(status="PASS_INDEPENDENT_ALTERNATING_RECORD_ALGEBRA_AND_SCOPED_HOSTING_REVIEW",
        reviewed_source_sha256=digest(package / "alternating_records.py"), reviewed_ir_payload_sha256=sha256(ir_bytes).hexdigest(),
        reviewer_sha256=digest(Path(__file__)), actual_native_program_payloads=programs_checked,
        free_noncommutative_identity=free_word_identity(), independent_noncommuting_fixture=noncommuting_fixture(),
        actual_bank_and_gram_checks=dict(bank_factors=9, diagonal_gram="-2I8", upper_entries=len(expected_upper), lower_entries=len(expected_lower)),
        record_left_inverse=dict(scalar_gaussian_rank=9, actual_field_rank=72, realified_identity_dimension=18,
            scope="The left inverse applies to the zero-coordinate image U_h, hence to a difference of final and initial dirty records. Final records alone are not silently assumed to equal that difference.",
            owner_identity="L C=I and per-stage inverse rho_i,zero exactly cancel; different stage maps are never commuted."),
        physical_gram=dict(identity="(V_i Gamma^-1)(Gamma U_j)=V_i U_j",
            conclusion="The common physical gauge cancels inside each Gram entry before either port route. This does not remove Gamma from the first V gather or final U scatter.",
            full_fallback="After448 positive C_q lines all1024 data fields share owner-independent C_FULL. Affine cover views and Gaussian scalar matrices commute with this convolution, so the middle needs no further recursive children. Restore the same448 gauges with inverse lines.",
            native_children_in_known_full_fallback=896,
            missing="The current IR does not emit or price an optimized physical V or U interface, nor a complete middle scalar/address/precision bill."),
        query_cleanup=dict(owned_clear_admitted=True, clear_real_primitives=144, clear_mode_boundary_passes={"V": 1, "U": 1},
            reversible_mode_boundary_passes={"V": 2, "U": 1}, reversible_mode_checked=True,
            conclusion="The second V pass is optional under the retained owned-clear grammar; it is required by the particular reversible arithmetic erasure word."),
        workspace=dict(owned_zero_slots=91, proposed_simultaneous_query_fields=72, local_releases=release_counts,
            physical_private_binding=binding, peak_query_fields=72, private_slots_remaining=19, no_productive_field_withdrawal=True,
            finite_lifetime_condition="Begin terminal queries after all preceding local/data-idle private lifetimes end; finish and clear before later private uses; execute terminal replicas serially.",
            conditional_capacity_conclusion="An explicit injective terminal slot assignment fits the retained91-slot physical envelope. Numerical cleanliness of released slots relies on the source-bound native local replays, not this independent lifetime walk.",
            missing="No new whole-family recursive hosting, tape realization, scalar prefix bound, or complete supplier admission is established by the capacity count."),
        conclusion="No algebraic error found in the updated ordered inverse, actual record left inverse, dirty-state restoration or either stated cleanup option. Optimized native U/V tariffs remain open; no kappa increase is certified.")
    (package / "evidence/RECORDS-REVIEW.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(out["status"], flush=True)


if __name__ == "__main__":
    main()
