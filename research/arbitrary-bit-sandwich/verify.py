"""Verify the new boundary, using completed-child fixtures and real Tape owners.

Produced by Nick Petalas. Apache-2.0. No production numerical replay.
"""
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / "SOURCES.json").read_bytes())["files"]
    need(len(rows) <= 128, "bounded source inventory")
    for row in rows:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular input: " + str(path))
        need(path.stat().st_size <= 2**27, "bounded source input")
        need(sha256(path.read_bytes()).hexdigest() == row["sha256"],
             "authenticated input: " + row["path"])
    tree = ast.parse((HERE / "boundary.py").read_text())
    forbidden = {"cells", "head", "meter", "inspect", "bit_length"}
    need(not any(isinstance(node, ast.Attribute) and node.attr in forbidden
                 for node in ast.walk(tree)), "boundary uses only physical operations")
    return sum(row["usage"] == "input" for row in rows)


def bits(value, width):
    need(0 <= value < 1 << width <= 1 << 128, "bounded host fixture")
    return bytes((value >> i) & 1 for i in reversed(range(width)))


def meters(tapes):
    return tuple(sum(getattr(t.meter, field) for t in tapes)
                 for field in ("reads", "writes", "moves"))


def difference(after, before):
    return tuple(a - b for a, b in zip(after, before))


class FixtureChild:
    """An exact child oracle whose run is excluded and consume is charged.

    Host integers and direct tape inspection here are test-oracle work only.
    The real boundary never receives these integers or the oracle object state.
    """

    def __init__(self, api, n, b, x, y):
        self.api = api
        q = (n + b - 1) // b
        self.expected = tuple(bits(v, n)[::-1] + bytes(q*b-n) for v in (x, y))
        self.product = bits(x*y, 2*q*b)
        self.b, self.q = api.Count.literal(b), api.Count.literal(q)
        self.output = api.Tape()
        api.erase_marker(self.output)
        self.private = (self.output, self.b.tape, self.q.tape)
        self.closed, self.pending = True, False
        self.calls = self.consumed = 0
        self.work = (0, 0, 0)
        self.observed = ()
        self.mode = "ok"

    def run(self, first, second, catalogue, b, q):
        before = meters(self.observed)
        self.calls += 1
        try:
            need(self.closed and not self.pending, "fixture child idle")
            need(self.api.compare(b, self.b) == self.api.compare(q, self.q) == 0,
                 "actual encoded child shape")
            need(tuple(self.api.packet_bytes(t) for t in (first, second)) == self.expected,
                 "actual packed operand direction and padding")
            if self.mode == "raise":
                raise ValueError("injected completed child failure")
            self.api.initialize_marker(self.output)
            raw = self.product
            if self.mode == "prefix":
                raw = bytes([1]) + raw[1:]
            elif self.mode == "short":
                raw = raw[:-1]
            elif self.mode == "extra":
                raw += bytes([0])
            elif self.mode == "symbol":
                raw = raw[:-1] + bytes([self.api.RIGHT])
            for bit in raw:  # At most 129 fixed fixture cells.
                self.output.append(bit)
            self.output.rewind()
            self.pending = True
            return self.output
        finally:
            delta = difference(meters(self.observed), before)
            self.work = tuple(a+b for a, b in zip(self.work, delta))

    def consume(self):
        need(self.pending, "fixture pending return")
        self.output.clear()
        self.api.erase_marker(self.output)
        self.pending = False
        self.consumed += 1


def prepare(api, n, b, x, y):
    child = FixtureChild(api, n, b, x, y)
    wrapper = api.ArbitraryBits(child)
    ports = [api.tape(bits(x, n)), api.tape(bits(y, n)), api.tape(bytes([1]))]
    counts = api.Count.literal(n), api.Count.literal(b)
    tapes = (*wrapper.private, *ports, *(c.tape for c in counts))
    need(len({id(t) for t in tapes}) == len(tapes), "independent fixture inventory")
    child.observed = tapes
    return SimpleNamespace(child=child, wrapper=wrapper, ports=ports, counts=counts,
                           tapes=tapes, n=n, b=b, x=x, y=y)


def idle(case):
    w, child = case.wrapper, case.child
    need(w.closed and not w.pending and not w.pool.live, "idle complete boundary")
    need(child.closed and not child.pending, "child return released")
    for tape in (*w.resident, child.output):
        need(tape.head == 1 and all(v == case.child.api.BLANK for v in tape.cells),
             "erased resident body, marker and canonical head")


def successful(api, case):
    w, child = case.wrapper, case.child
    snapshots = [(bytes(t.cells), t.head) for t in (*case.ports, *(c.tape for c in case.counts))]
    before, prior_work = meters(case.tapes), child.work
    with api.no_decode():
        result = w.run(*case.ports, *case.counts)
    run_delta = difference(meters(case.tapes), before)
    child_delta = difference(child.work, prior_work)
    own_delta = difference(run_delta, child_delta)
    need(all(x >= 0 for x in own_delta), "nonnegative complete boundary tariff")
    need(api.packet_bytes(result) == bits(case.x*case.y, 2*case.n),
         "exact 2n-bit integer product with leading zeroes")
    need([(bytes(t.cells), t.head) for t in (*case.ports, *(c.tape for c in case.counts))]
         == snapshots, "all five borrowed ports preserved")
    before_consume = meters(case.tapes)
    w.consume()
    consumption = difference(meters(case.tapes), before_consume)
    idle(case)
    return tuple(a+b for a, b in zip(own_delta, consumption))


def reject_case(api, case, message, preflight=False):
    before = [(bytes(t.cells), t.head) for t in case.tapes]
    try:
        with api.no_decode():
            case.wrapper.run(*case.ports, *case.counts)
    except ValueError as error:
        need(message in str(error), "expected rejection: " + str(error))
    else:
        raise ValueError("missing rejection: " + message)
    if preflight:
        need([(bytes(t.cells), t.head) for t in case.tapes] == before,
             "preflight rejection preserves physical state")
    else:
        idle(case)


def return_controls(api):
    checks = []
    messages = {"prefix": "zero discarded", "short": "binary product extent",
                "extra": "extra product", "symbol": "binary product extent",
                "raise": "injected completed"}
    for mode, message in messages.items():
        case = prepare(api, 5, 3, 29, 23)
        case.child.mode = mode
        reject_case(api, case, message)
        need(case.child.calls == 1 and case.child.consumed == int(mode != "raise"),
             "failed output validation consumes every completed child return")
        case.child.mode = "ok"
        successful(api, case)
        checks.append(mode)
    return checks


def input_controls(api):
    checks = []
    for raw, message in [(bytes([1, 0]), "binary input extent"),
                         (bytes([1, 0, 1, 0, 1, 0]), "extra input"),
                         (bytes([1, api.RIGHT, 0, 1, 0]), "binary input extent")]:
        for port in (0, 1):
            case = prepare(api, 5, 3, 29, 23)
            original = case.ports[port]
            case.ports[port] = api.tape(raw)
            reject_case(api, case, message)
            need(case.child.calls == 0, "validate both operands before child entry")
            case.ports[port] = original
            successful(api, case)
            checks.append((list(raw), port))
    for zero in (0, 1):
        case = prepare(api, 5, 3, 29, 23)
        values = list(case.counts)
        values[zero] = api.Count.literal(0)
        case.counts = tuple(values)
        reject_case(api, case, "positive cardinality")
        need(case.child.calls == 0, "zero parameter never reaches the child")
        checks.append(("zero", zero))
    return checks


def ownership_controls(api):
    checks = []
    for destination in (1, 2):
        case = prepare(api, 5, 3, 29, 23)
        case.ports[destination] = case.ports[0]
        reject_case(api, case, "five distinct", True)
        checks.append(("payload_alias", destination))
    for port in (0, 1, 2):
        for count in (0, 1):
            case = prepare(api, 5, 3, 29, 23)
            case.counts[count].tape = case.ports[port]
            reject_case(api, case, "five distinct", True)
            checks.append(("metadata_alias", port, count))
    for slot in (0, 32, 34, 35):
        case = prepare(api, 5, 3, 29, 23)
        case.ports[0] = case.wrapper.private[slot]
        reject_case(api, case, "external boundary", True)
        checks.append(("private_alias", slot))
    case = prepare(api, 5, 3, 29, 23)
    case.wrapper.run(*case.ports, *case.counts)
    for _ in range(2*case.n):
        case.wrapper.output.step(1)
    reject_case(api, case, "consume prior boundary", True)
    case.wrapper.consume()
    successful(api, case)
    checks.append(("pending_return_at_end",))
    try:
        case.wrapper.consume()
    except ValueError as error:
        need("pending boundary" in str(error), "double consume rejected")
    else:
        raise ValueError("double consume accepted")
    checks.append(("double_consume",))
    return checks


def positive_cases(api):
    transcript = sha256()
    count = partial = 0
    max_peak = 0
    demonstration = None
    shapes = [(n, b, x, y) for n in range(1, 5) for b in range(1, 6)
              for x in range(1 << n) for y in range(1 << n)]
    for n in (5, 9, 17, 31, 32, 33):
        for b in (1, 2, 3, 7, 8, 16):
            top = (1 << n)-1
            for x, y in ((0, top), (1, top), (top, top), (top//3, top//5)):
                shapes.append((n, b, x, y))
    shapes.append((5, 3, 29, 23))
    need(len(shapes) <= 2048, "bounded complete positive fixture list")
    for n, b, x, y in shapes:
        case = prepare(api, n, b, x, y)
        tariff = successful(api, case)
        transcript.update(json.dumps([n, b, x, y, tariff]).encode()+b"\n")
        count += 1
        partial += int(n % b != 0)
        max_peak = max(max_peak, case.wrapper.pool.peak)
        if (n, b, x, y) == (5, 3, 29, 23):
            demonstration = dict(n=n, b=b, q=2, padding=1, x=x, y=y, product=x*y,
                                 packed=[list(s) for s in case.child.expected],
                                 output=list(bits(x*y, 2*n)),
                                 tariff=dict(zip(("reads", "writes", "moves"), tariff)),
                                 scratch_peak=case.wrapper.pool.peak)
    return dict(cases=count, nonmultiple_shapes=partial, scratch_peak=max_peak,
                transcript_sha256=transcript.hexdigest(), demonstration=demonstration)


def actual_child_policy(api):
    from crt_converter import Converter
    from sandwich import Sandwich
    from tensor_engine import Tensor
    from tensor_fixture import finite_chirp, literal_native
    from tensor_router import FullRouter
    child = Sandwich(Tensor(finite_chirp(), FullRouter(literal_native())),
                     Converter(FullRouter(literal_native())))
    wrapper = api.ArbitraryBits(child)
    raw = (ROOT / "research/physical-tensor-crt-sandwich-recovery/inputs/p48-5x7.bin").read_bytes()
    ports = [api.tape(bits(29, 17)), api.tape(bits(23, 17)), api.tape(raw)]
    case = SimpleNamespace(child=child, wrapper=wrapper, ports=ports,
                           counts=(api.Count.literal(17), api.Count.literal(8)))
    try:
        with api.no_decode():
            wrapper.run(*case.ports, *case.counts)
    except ValueError as error:
        need("production coefficient/locality contract required" in str(error),
             "the actual child's production guard remains mandatory")
    else:
        raise ValueError("reduced catalogue admitted production recovery")
    need(wrapper.closed and not wrapper.pending and not wrapper.pool.live,
         "actual-child policy rejection cleans boundary")
    need(child.closed and not child.pending and not child.pool.live,
         "actual child cleans its own failed entry")
    for tape in wrapper.resident:
        need(tape.head == 1 and all(v == api.BLANK for v in tape.cells),
             "actual-child failure erases every boundary role")
    return dict(recovery_policy="mandatory production admission", payload_executed=False)


def run():
    inputs = authenticate()
    sys.path[:0] = [str(HERE), str(ROOT / "research/physical-tensor-crt-sandwich-recovery")]
    from sandwich_sources import opened
    with opened():
        from boundary import ArbitraryBits
        from cardinal_counts import Count
        from check_support import no_decode
        from encoded import compare
        from expansion_check_block import packet_bytes
        from records import Tape
        from ring_check_words import tape
        from session import erase_marker, initialize_marker
        from words import BLANK, RIGHT
        api = SimpleNamespace(ArbitraryBits=ArbitraryBits, Count=Count,
                              no_decode=no_decode, compare=compare,
                              packet_bytes=packet_bytes, Tape=Tape, tape=tape,
                              erase_marker=erase_marker,
                              initialize_marker=initialize_marker,
                              BLANK=BLANK, RIGHT=RIGHT)
        result = positive_cases(api)
        result["return_controls"] = return_controls(api)
        result["input_controls"] = input_controls(api)
        result["ownership_controls"] = ownership_controls(api)
        result["actual_child"] = actual_child_policy(api)
    result["inputs_authenticated"] = inputs
    result["claim_type"] = "scoped caller construction under a completed-child contract"
    result["tariff_scope"] = "All wrapper work and both return consumptions; only child.run is excluded. Host oracle/output inspection is excluded."
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest()
                                for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps(result, sort_keys=True))
    print("PASS_ARBITRARY_BIT_SANDWICH")


if __name__ == "__main__":
    run()
