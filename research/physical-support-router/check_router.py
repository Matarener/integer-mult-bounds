"""Checker-only indexed oracles, complete packets and rejection controls."""

from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from router_sources import active, authenticate, require


def descriptor(n, permutation):
    from records import Tape
    width = max(1, (n-1).bit_length())
    tape = Tape()
    for source, target in permutation:
        for value in (source, target):
            for bit in range(width):
                tape.append((value >> bit) & 1)
    tape.rewind()
    return tape


def make_router(policy="standard"):
    from macro_code import Code
    from router_engine import Router
    state = active()
    native = state.ordinary.Ordinary(
        2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
        (Code((("unreachable",),), 0),), capacity=64,
        profile=state.encoded.Profile(numerator=1, denominator=577))
    return Router(native, policy)


def program_oracle(plan, permutation):
    from check_support import inspect_count
    from compact_counts import read_fixed
    from router_plan import BATCH, CNOT, END, GROUP, SWAP, UNGROUP, read_opcode
    from words import BLANK
    n = inspect_count(plan.n)
    current = [1 << i for i in range(n)]
    suffix = None
    counts = dict(swaps=0, batches=0, cnots=0, groups=0, ungroups=0, pairs=0)
    batch_sizes, target_colors = [], []

    def number(width):
        value = read_fixed(plan.program, width)
        try:
            return inspect_count(value)
        finally:
            value.close()

    try:
        while True:
            op = read_opcode(plan.program)
            if op == END:
                require(suffix is None and plan.program.read() == BLANK, "oracle exact restored program")
                break
            if op == SWAP:
                a, b, h = (number(plan.width) for _ in range(3))
                require(a+h <= b and b+h <= len(current), "oracle complete disjoint swap fields")
                current[a:a+h], current[b:b+h] = current[b:b+h], current[a:a+h]
                counts["swaps"] += 1
            elif op == GROUP:
                require(suffix is None, "oracle one suffix group")
                ell = inspect_count(plan.ell)
                suffix, current = current[:ell], current[ell:]
                counts["groups"] += 1
            elif op == UNGROUP:
                require(suffix is not None, "oracle matching suffix ungroup")
                current, suffix = suffix+current, None
                counts["ungroups"] += 1
            elif op == CNOT:
                source, target = (number(plan.width) for _ in range(2))
                current[target] ^= current[source]
                counts["cnots"] += 1
            else:
                require(op == BATCH and suffix is not None, "oracle batch inside prefix")
                count = number(plan.width)
                pairs = [(number(plan.y_width), number(plan.y_width)) for _ in range(count)]
                H, Y, G, K = (inspect_count(v) for v in (plan.H, plan.Y, plan.G, plan.K))
                sources, targets = [x for x, _ in pairs], [y for _, y in pairs]
                require(count > 0 and count*G <= H and len(set(sources)) == count
                        and not set(sources) & set(targets) and targets == sorted(targets)
                        and all(0 <= x < Y and 0 <= y and y+K <= Y for x, y in pairs)
                        and all(a+K <= b for a, b in zip(targets, targets[1:])), "oracle sparse contract")
                require(len({y % K for y in targets}) == 1, "oracle post-placement target color")
                before = current[:]
                for source, target in pairs:
                    current[H+target] = before[H+target] ^ before[H+source]
                counts["batches"] += 1
                counts["pairs"] += count
                batch_sizes.append(count)
                target_colors.append(targets[0] % K)
        expected = [1 << i for i in range(n)]
        for source, target in permutation:
            expected[target] = 1 << source
        require(current == expected, "independent coordinate provenance for whole router program")
        return dict(mode=plan.mode, counts=counts, largest_batch=max(batch_sizes, default=0),
                    colors=sorted(set(target_colors)))
    finally:
        plan.program.rewind()


def plan_case(n, p, permutation, policy="standard"):
    from cardinal_counts import Count
    from check_support import no_decode, inspect_count
    from router_plan import Plan
    from scratch_pool import ScratchPool
    from session import OuterScope, sealed_constructors
    pool = ScratchPool(256)
    table = descriptor(n, permutation)
    inputs = tuple(Count.literal(v) for v in (n, p, len(permutation), max(1, (n-1).bit_length())))
    plan = None
    try:
        with sealed_constructors(), OuterScope(pool).installed():
            try:
                with no_decode():
                    plan = Plan(*inputs, pool.acquire, policy)
                    plan.compile(table)
                result = program_oracle(plan, permutation)
                result["geometry"] = {name: inspect_count(value) for name, value in plan.fields.items()}
            finally:
                if plan is not None:
                    plan.close()
            pool.empty()
        result["peak"] = pool.peak
        return result
    finally:
        table.clear()
        for value in inputs:
            value.close()


def metadata():
    cases = 0
    modes = set()
    for size in range(5):
        for image in permutations(range(size)):
            result = plan_case(6, 2, tuple(enumerate(image)))
            modes.add(result["mode"])
            cases += 1
    reduced = [
        (11, ((1, 2), (2, 3), (3, 1))),
        (11, ((0, 10), (10, 0))),
        (21, ((0, 1), (1, 7), (7, 15), (15, 20), (20, 0))),
        (31, ((0, 3), (3, 10), (10, 20), (20, 25), (25, 30), (30, 0))),
    ]
    fast_results = [plan_case(n, 2, pairs, "fixture-g1-k5") for n, pairs in reduced]
    require(all(x["mode"] == "fast" for x in fast_results), "reduced complete-router fast plans")
    # Large address geometry, standard guard policy. This checks encoded planning,
    # not an exponentially large physical packet.
    standard = plan_case(4096, 64, ((0, 1000), (1000, 2200), (2200, 3000), (3000, 4095), (4095, 0)))
    require(standard["mode"] == "fast" and standard["geometry"]["ell"] == 36
            and standard["geometry"]["G"] == 30 and standard["geometry"]["K"] == 1920,
            "encoded standard-policy geometry")
    require(fast_results[0]["counts"]["cnots"] > 0
            and any(x["largest_batch"] > 1 for x in fast_results), "tail and multiple-edge batch coverage")
    no_gap = plan_case(956, 65536, ((511, 766), (766, 511)))
    require(no_gap["mode"] == "literal" and no_gap["geometry"]["N"] == 10*no_gap["geometry"]["H"],
            "literal fallback when reservoir space exists but no untouched record block exists")
    return dict(status="PASS_ROUTER_METADATA", exhaustive_permutations=cases,
                small_modes=sorted(modes), reduced=fast_results, standard=standard, no_gap=no_gap)


def closed(router):
    from words import BLANK
    router.idle_child()
    require(router.closed and router.current is None and not router.pool.live, "closed router ownership")
    for engine in (router, router.sparse, router.binary):
        for tape in engine.pool.tapes:
            require(tape.head == 1 and all(bit == BLANK for bit in tape.cells), "blank owned router and child work")


def packet(n, p, permutation, R=1, C=1, policy="standard", router=None, consume=True, initial=None):
    from cardinal_counts import Count
    from check_support import bits, no_decode
    from provenance import Provenance
    from records import Tape
    from session import erase_marker
    router = make_router(policy) if router is None else router
    table = descriptor(n, permutation)
    source = Tape()
    length = C*(1 << n)*R
    require(initial is None or len(initial) == length, "complete checker input override")
    for index in range(length):
        source.append((index*11 ^ index//7 ^ 5) & 1 if initial is None else initial[index])
    source.rewind()
    inputs = tuple(Count.literal(v) for v in (n, p, len(permutation), max(1, (n-1).bit_length()), R, C))
    saved = tuple((bytes(x.tape.cells), x.tape.head) for x in inputs)
    saved_table = (bytes(table.cells), table.head)
    original = bits(source)
    expected, masks = bytearray(length), [0]*length
    for row in range(C):
        for old in range(1 << n):
            new = old
            for a, b in permutation:
                new = (new & ~(1 << b)) | (((old >> a) & 1) << b)
            for bit in range(R):
                origin, target = (row*(1 << n)+old)*R+bit, (row*(1 << n)+new)*R+bit
                expected[target], masks[target] = original[origin], 1 << origin
    observer = Provenance(length)
    observer.mark(source)
    before = dict(router.calls)
    sparse_before = dict(router.sparse.calls)
    profiles = []
    select = active().ordinary.select

    def observed_select(width, q, profile):
        profiles.append((profile.numerator, profile.denominator))
        return select(width, q, profile)

    try:
        with no_decode(), observer.installed(), patch.object(active().ordinary, "select", observed_select):
            returned = router.run(source, table, *inputs)
        require(bits(returned) == expected and observer.masks(returned, length) == tuple(masks),
                "physical router preserves each independent input bit at its specified destination")
        require(bits(source) == original and source.head == returned.head == 1,
                "borrowed router payload and protected output heads")
        require(saved == tuple((bytes(x.tape.cells), x.tape.head) for x in inputs)
                and saved_table == (bytes(table.cells), table.head), "borrowed router metadata unchanged")
        closed(router)
        calls = {key: router.calls[key]-before[key] for key in before}
        sparse_calls = {key: router.sparse.calls[key]-sparse_before[key] for key in sparse_before}
        require(sparse_calls == dict(ordinary=12*C*calls["batches"], rotations=10*C*calls["batches"],
                                     rows=C*calls["batches"]), "one actual shared sparse cohort per batch")
        require(not profiles or set(profiles) == {(1, 577)}, "actual retained ordinary profile")
        result = dict(n=n, p=p, record_bits=R, rows=C, payload_bits=length, mode=router.last_mode,
                      policy=policy, calls=calls, sparse_calls=sparse_calls, peak=router.pool.peak,
                      selector_calls=len(profiles), output_sha256=sha256(expected).hexdigest())
        if consume:
            returned.clear()
            erase_marker(returned)
        return router, result
    finally:
        source.clear()
        table.clear()
        for value in inputs:
            value.close()


def literal():
    router, first = packet(4, 2, ((0, 1), (1, 3), (3, 0)), R=4, C=3)
    _, identity = packet(3, 2, (), R=3, C=2, router=router)
    _, fixed = packet(1, 2, ((0, 0),), R=1, C=3, router=router)
    require(first["mode"] == "literal" and identity["mode"] == fixed["mode"] == "identity",
            "literal cycle and reused empty/fixed identity packets")
    return dict(status="PASS_ROUTER_LITERAL_PACKETS", cases=[first, identity, fixed])


def forward():
    _, result = packet(11, 2, ((1, 2), (2, 3), (3, 1)), policy="fixture-g1-k5")
    require(result["mode"] == "fast" and result["calls"]["batches"] > 0
            and result["calls"]["cnots"] > 0 and result["calls"]["groups"] == 1,
            "complete forward cycle covers preparation, sparse batches and tails")
    return dict(status="PASS_ROUTER_FAST_FORWARD_PACKET", result=result)


def inverse():
    from check_support import bits
    from session import erase_marker
    router, first = packet(11, 2, ((1, 2), (2, 3), (3, 1)), policy="fixture-g1-k5", consume=False)
    intermediate = bits(router.output)
    router.output.clear()
    erase_marker(router.output)
    _, second = packet(11, 2, ((1, 3), (2, 1), (3, 2)), policy="fixture-g1-k5",
                       router=router, initial=intermediate, consume=False)
    try:
        require(bits(router.output) == bytes((i*11 ^ i//7 ^ 5) & 1 for i in range(2048)),
                "actual forward output returns through inverse router on the same physical cohort")
        require(second["mode"] == "fast" and second["calls"]["ungroups"] == 1,
                "complete inverse cycle restores record interpretation")
    finally:
        router.output.clear()
        erase_marker(router.output)
    return dict(status="PASS_ROUTER_FAST_ROUNDTRIP_PACKET", cases=[first, second])


def failures():
    from check_support import reject
    rejected = []
    for label, n, pairs in (
        ("duplicate source", 4, ((0, 1), (0, 0))),
        ("duplicate image", 4, ((0, 1), (1, 1))),
        ("different image set", 4, ((0, 1),)),
        ("outside rectangle", 3, ((0, 3), (3, 0))),
        ("unsorted sources", 4, ((1, 0), (0, 1))),
    ):
        rejected.append(reject(lambda: plan_case(n, 2, pairs), label))
    from router_plan import Plan
    original = Plan.placed

    def omitted_reindex(self, position, reservoir):
        from cardinal_counts import Count
        return Count(position)

    with patch.object(Plan, "placed", omitted_reindex):
        rejected.append(reject(lambda: plan_case(11, 2, ((1, 2), (2, 3), (3, 1)), "fixture-g1-k5"),
                               "omitted post-placement reindex"))
    require(Plan.placed is original, "restore reindex implementation")
    from cardinal_counts import Count
    from compact_counts import write_fixed
    from router_metadata import Pairs
    for kind in ("short", "trailing", "noncanonical width"):
        table = descriptor(4, ((0, 1), (1, 0)))
        k, n, width = Count.literal(2), Count.literal(4), Count.literal(2 if kind != "noncanonical width" else 3)
        try:
            if kind == "short":
                table.clear()
            elif kind == "trailing":
                from words import BLANK
                while table.read() != BLANK:
                    table.step(1)
                extra = Count.literal(1)
                try:
                    write_fixed(extra, table, width)
                finally:
                    extra.close()
            rejected.append(reject(lambda: Pairs(table, k, width).validate(n), kind))
        finally:
            table.clear()
            for value in (k, n, width):
                value.close()
    router, _ = packet(3, 2, ((0, 1), (1, 0)), consume=False)
    rejected.append(reject(lambda: packet(3, 2, (), router=router), "protected output before reuse"))
    from session import erase_marker
    router.output.clear()
    erase_marker(router.output)
    _, reused = packet(2, 2, (), router=router)
    require(reused["mode"] == "identity", "consumed output permits reuse")
    from router_engine import Router
    from records import Tape

    def forbidden_allocation(*_args):
        Tape()

    with patch.object(Router, "execute", forbidden_allocation):
        rejected.append(reject(lambda: packet(2, 2, ()), "physical allocation during router call"))
    return dict(status="PASS_ROUTER_REJECTIONS", rejected=rejected)


def budget():
    tau = Fraction(332353, 332929)
    require(1-tau == Fraction(576, 332929), "retained ordinary exponent")
    require(Fraction(3, 1000) > Fraction(1, 512), "cutoff exponential slack")
    slope = (1-tau)*Fraction(997, 1000)*1024
    require(slope < 2, "fallback exponent grows slower than stated constant")
    for L in range(10, 129):
        X = 1024*(L+11)
        require(2**(L+22) > (X+1)**2, "cutoff base inequality")
        require((1-tau)*(1+Fraction(997, 1000)*X) <= 2*L+23,
                "exact rational fallback multiplier")
    checked = 0
    for p in (2, 3, 16, 64, 1024, 2**64):
        l = (p-1).bit_length()
        ell, G, K = l*l, 4*l+6, 64*(4*l+6)
        for k in (2, 3, 4, 17, 64):
            H = (k//2)*G
            require(H >= G and 10*H >= 3*3*H+H, "half-support capacity and back-field clearance")
            require(K == 64*G and ell >= 1, "standard policy")
            checked += 1
    return dict(status="PASS_ROUTER_FINITE_BUDGET_CONTROLS", checks=checked,
                cutoff_checks=119, tau=str(tau),
                scope="Finite arithmetic controls; all-size proof and conditional premises in PROOF.md.")


def sources():
    state = active()
    path = authenticate()
    require(len(state.compared_backend) == 23, "retained complete ordinary cohort comparison")
    require(Path(state.ordinary.__file__).resolve().parent == state.backend.resolve(), "same actual native cohort")
    from check_support import reject
    with tempfile.TemporaryDirectory(prefix="router-source-control-") as directory:
        altered = Path(directory) / "altered.tar"
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        altered.write_bytes(data)
        reject(lambda: authenticate(altered), "altered sparse source bytes")
        alias = Path(directory) / "alias.tar"
        alias.symlink_to(path)
        reject(lambda: authenticate(alias), "source symlink")
    return dict(status="PASS_ROUTER_SOURCE_COHORT", sha256=sha256(path.read_bytes()).hexdigest(),
                ordinary_files=len(state.compared_backend), rejected=["altered source", "source symlink"])
