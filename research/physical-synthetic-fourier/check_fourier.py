"""Checker-only dense polynomial Fourier values and complete physical packets."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
from unittest.mock import patch

from fourier_sources import active, require


def tape(bits):
    from records import Tape
    result = Tape()
    for bit in bits:
        result.append(bit)
    result.rewind()
    return result


def decoded(value):
    from words import RIGHT
    answer, shift = 0, 0
    value.rewind()
    try:
        while value.read() != RIGHT:
            answer += value.read() << shift
            shift += 1
            value.step(1)
        return answer
    finally:
        value.rewind()


def natural_lengths(flags, ell):
    return [ell-1+bit for bit in flags]


def coordinates(address, lengths):
    result = []
    remaining = sum(lengths)
    for length in lengths:
        remaining -= length
        result.append((address >> remaining) & ((1 << length)-1))
    return result


def dense(values, flags, ell, rows, opposite):
    lengths = natural_lengths(flags, ell)
    M, r = 1 << sum(lengths), 1 << ell
    result = [(0, 0)] * len(values)
    for row in range(rows):
        for j in range(M):
            sums = [[0, 0] for _ in range(r)]
            out = coordinates(j, lengths)
            for k in range(M):
                incoming = coordinates(k, lengths)
                exponent = sum((2*r >> length)*a*b
                               for length, a, b in zip(lengths, out, incoming))
                if not opposite:
                    exponent = -exponent
                for coefficient in range(r):
                    quotient, destination = divmod(coefficient+exponent, r)
                    sign = -1 if quotient & 1 else 1
                    value = values[(row*M+k)*r+coefficient]
                    for component in range(2):
                        sums[destination][component] += sign*value[component]
            for coefficient, value in enumerate(sums):
                result[(row*M+j)*r+coefficient] = tuple(int(Fraction(v, M)) for v in value)
    return result


def metadata():
    from cardinal_counts import Count
    from fourier_plan import FourierPlan, batch_limit
    limits = 0
    for P in (2, 3, 4, 5, 8, 16, 255, 256, 555, 1024):
        incoming = Count.literal(P)
        cap = batch_limit(incoming)
        try:
            expected = 1 << (997*(P.bit_length()-1)//1000)
            require(decoded(cap) == expected and expected**1000 <= P**997
                    and (4*expected)**1000 > P**997, "encoded dyadic batch cap and exact admission")
            limits += 1
        finally:
            cap.close()
            incoming.close()
    total = 0
    for ell, flags in ((2, (0,)), (2, (1,)), (2, (1, 0)), (3, (0, 1)), (3, (1, 1))):
        descriptor = tape(flags)
        counts = tuple(Count.literal(v) for v in (len(flags), ell, 3, 1))
        plan = FourierPlan(descriptor, *counts)
        try:
            plan.compile()
            lengths = natural_lengths(flags, ell)
            n = sum(lengths)
            require(decoded(plan.n) == n and decoded(plan.P) == n+3, "encoded whole-transform lift")
            offsets = []
            offset = 0
            for length in reversed(lengths):
                offsets.append((offset, length))
                offset += length
            actual = [(decoded(a), decoded(b)) for a, b in plan.natural_axes()]
            require(actual == offsets, "natural named-axis offsets")
            for address, h, opposite in product(range(1 << n), range(ell), (False, True)):
                a, level = Count.literal(address), Count.literal(h)
                value = plan.exponent(a, level, opposite)
                try:
                    raw = sum(((address >> (offset+h)) & 1) * ((address >> offset) & ((1 << h)-1))
                              for offset, length in offsets if h < length)
                    expected = ((1 if opposite else -1)*(1 << (ell-h))*raw) % (1 << (ell+1))
                    require(decoded(value) == expected, "exact natural diagonal exponent")
                    total += 1
                finally:
                    value.close()
                    a.close()
                    level.close()
        finally:
            plan.close()
            for value in counts:
                value.close()
    # Metadata-only witness beyond both predecessor simulator admission caps.
    flags, ell = (1, 0)*8+(1,), 33
    descriptor = tape(flags)
    counts = tuple(Count.literal(v) for v in (len(flags), ell, 2, 1))
    plan = FourierPlan(descriptor, *counts)
    large = 0
    try:
        plan.compile()
        lengths = natural_lengths(flags, ell)
        n = sum(lengths)
        for address, h, opposite in product((0, (1 << n)-1), (0, 32), (False, True)):
            a, level = Count.literal(address), Count.literal(h)
            value = plan.exponent(a, level, opposite)
            try:
                xs = coordinates(address, lengths)
                raw = sum(((x >> h) & 1)*(x & ((1 << h)-1))
                          for x, length in zip(xs, lengths) if h < length)
                expected = ((1 if opposite else -1)*(1 << (ell-h))*raw) % (1 << (ell+1))
                require(decoded(value) == expected, "uncapped encoded diagonal descriptor")
                large += 1
            finally:
                value.close()
                a.close()
                level.close()
    finally:
        plan.close()
        for value in counts:
            value.close()
    return {"encoded_exponents": total, "axis_shapes": 5, "batch_caps": limits,
            "large_metadata_only": {"ell": ell, "axes": len(flags), "address_bits": n, "cases": large}}


def packet(flags, ell=2, p=2, rows=1, opposite=False, owner=None, batch_one=False,
           values=None, consume=True, expected=None):
    from cardinal_counts import Count
    from check_composed import body, encode, fixture
    from check_support import no_decode
    from fourier_engine import Fourier
    from fourier_plan import FourierPlan
    from session import erase_marker
    from words import BLANK
    machine = Fourier(fixture()[0]) if owner is None else owner
    n = sum(natural_lengths(flags, ell))
    size = rows*(1 << n)*(1 << ell)
    if values is None:
        values = [((i*3) % 5-2, (i*7) % 5-2) for i in range(size)]
    require(len(values) == size and all(a*a+b*b <= 1 << (2*p) for a, b in values),
            "complete Fourier fixture in unit disk")
    original = encode(values, p+2)
    expected_values = dense(values, flags, ell, rows, opposite) if expected is None else expected
    wanted = encode(expected_values, p+2)
    payload, descriptor = tape(original), tape(flags)
    counts = tuple(Count.literal(v) for v in (len(flags), ell, p, rows))
    saved = tuple((bytes(value.tape.cells), value.tape.head) for value in counts)
    before = dict(machine.calls)

    class OneBatch(FourierPlan):
        def compile(self):
            super().compile()
            self.cap.close()
            self.fields["cap"] = Count.literal(1)

    try:
        with patch("fourier_engine.FourierPlan", OneBatch if batch_one else FourierPlan), no_decode():
            returned = machine.run(payload, descriptor, *counts, opposite=opposite)
        actual = body(returned)
        require(actual == wanted, "complete physical Fourier packet equals dense polynomial oracle")
        require(body(payload) == original and body(descriptor) == bytes(flags), "preserved Fourier borrowed ports")
        require(saved == tuple((bytes(value.tape.cells), value.tape.head) for value in counts),
                "preserved Fourier numerical ports")
        require(machine.closed and machine.current is None and not machine.pool.live,
                "closed Fourier owner")
        machine.idle()
        require(all(item.head == 1 and all(bit == BLANK for bit in item.cells) for item in machine.pool.tapes),
                "erased Fourier pool and origin heads")
        evidence = {"axes": list(flags), "ell": ell, "p": p, "rows": rows,
                    "opposite": opposite, "gaussians": size, "bits": len(actual),
                    "sha256": sha256(actual).hexdigest(),
                    "calls": {key: machine.calls[key]-before[key] for key in before},
                    "pool_peak": machine.pool.peak, "reduced_batch_cap": batch_one}
        if consume:
            returned.clear()
            erase_marker(returned)
        return machine, evidence, expected_values
    finally:
        for value in counts:
            value.close()


def forward():
    _, result, _ = packet((1,))
    return result


def opposite():
    _, result, _ = packet((1,), opposite=True)
    return result


def batch():
    from cardinal_counts import Count
    from check_composed import fixture
    from fourier_engine import Fourier
    from session import borrowed_count, borrowed_tape

    class ReversalOnly(Fourier):
        """Checker boundary fixture: execute the paid B path without H/J rounds."""
        def execute(self, plan, _opposite):
            zero = Count.literal(0)
            try:
                with self.scope.suspended():
                    returned = self.grid.expand(borrowed_tape(self.current),
                        *(borrowed_count(v) for v in (plan.small, plan.n, zero, plan.gaussians)))
                self.accept(returned)
                self.calls["lifts"] += 1
                self.reversal(plan)
                with self.scope.suspended():
                    returned = self.grid.truncate(borrowed_tape(self.current),
                        *(borrowed_count(v) for v in (plan.wide, plan.n, plan.small, plan.gaussians)))
                self.accept(returned)
                self.calls["truncations"] += 1
            finally:
                zero.close()

    owner, first, _ = packet((1, 0), batch_one=True)
    _, second, _ = packet((0,), rows=2, opposite=True, owner=owner)
    values = [((i*3) % 5-2, (i*7) % 5-2) for i in range(64)]
    expected = [None]*64
    for address in range(16):
        destination = ((address & 5) << 1) | ((address & 10) >> 1)
        expected[4*destination:4*destination+4] = values[4*address:4*address+4]
    _, boundary, _ = packet((1, 1), owner=ReversalOnly(fixture()[0]),
                            batch_one=True, values=values, expected=expected)
    require(boundary["calls"]["reversals"] == 2 and boundary["calls"]["roots"] == 0,
            "two actual disjoint endpoint batches")
    return {"split_round": first, "same_owner_changed_shape": second,
            "reversal_only_two_batches": boundary}


def sources():
    import tempfile
    from pathlib import Path
    from fourier_sources import authenticate, opened
    rejected = 0
    with tempfile.TemporaryDirectory() as directory:
        altered = Path(directory) / "changed.tar"
        altered.write_bytes(b"changed")
        try:
            authenticate(altered)
        except ValueError:
            rejected += 1
    try:
        with opened():
            pass
    except ValueError:
        rejected += 1
    require(rejected == 2, "changed source and second-cohort controls")
    require(active().compact_counts == (21, 15), "retained complete Compact cohort")
    return {"rejections": rejected, "compact_internal_external": [21, 15]}


def round_oracle(values, flags, ell, premature=False):
    """Independent forward stage model, used only to select a rounding witness."""
    lengths = natural_lengths(flags, ell)
    n, r = sum(lengths), 1 << ell
    offsets = [sum(lengths[i+1:]) for i in range(len(lengths))]
    current = [tuple(Fraction(v) for v in pair) for pair in values]
    for h in reversed(range(ell)):
        for offset, length in zip(offsets, lengths):
            if h >= length:
                continue
            stride = 1 << (offset+h)
            for address in range(1 << n):
                if address & stride:
                    continue
                for coefficient in range(r):
                    a, b = address*r+coefficient, (address+stride)*r+coefficient
                    x, y = current[a], current[b]
                    current[a] = tuple((u+v)/2 for u, v in zip(x, y))
                    current[b] = tuple((u-v)/2 for u, v in zip(x, y))
        if premature:
            current = [tuple(Fraction(int(v)) for v in pair) for pair in current]
        following = [None]*len(current)
        for address in range(1 << n):
            exponent = -(1 << (ell-h))*sum(
                ((address >> (offset+h)) & 1)*((address >> offset) & ((1 << h)-1))
                for offset, length in zip(offsets, lengths) if h < length)
            for coefficient in range(r):
                quotient, destination = divmod(coefficient+exponent, r)
                sign = -1 if quotient & 1 else 1
                following[address*r+destination] = tuple(sign*v for v in current[address*r+coefficient])
        current = following
    result = [None]*len(current)
    for address in range(1 << n):
        destination = 0
        for coordinate, offset, length in zip(coordinates(address, lengths), offsets, lengths):
            destination |= int(f"{coordinate:0{length}b}"[::-1], 2) << offset
        for coefficient in range(r):
            result[destination*r+coefficient] = tuple(int(v) for v in current[address*r+coefficient])
    return result


def failures():
    from cardinal_counts import Count
    from check_composed import encode, fixture
    from fourier_engine import Fourier
    from session import borrowed_count, borrowed_tape, erase_marker
    from words import BLANK
    rejected = []
    # All these failures precede child payload calls; reuse the same owner afterward.
    owner = Fourier(fixture()[0])
    for name, flags, parameters, bits, message in (
        ("extra_flag", (1, 0), (1, 2, 2, 1), 128, "descriptor extent"),
        ("missing_flag", (), (1, 2, 2, 1), 128, "axis flags"),
        ("zero_axes", (), (0, 2, 2, 1), 128, "positive cardinality"),
        ("short_ell", (1,), (1, 1, 2, 1), 128, "at least two"),
        ("short_packet", (1,), (1, 2, 2, 1), 127, "complete opaque binary payload"),
        ("extra_packet", (1,), (1, 2, 2, 1), 129, "complete Fourier Gaussian packet"),
    ):
        counts = tuple(Count.literal(v) for v in parameters)
        try:
            try:
                owner.run(tape([0]*bits), tape(flags), *counts)
            except ValueError as error:
                require(message in str(error), "intended malformed rejection: " + name + ": " + str(error))
                rejected.append(name)
            else:
                raise ValueError("missing malformed Fourier rejection: " + name)
            require(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                    "malformed Fourier call restores owner")
        finally:
            for value in counts:
                value.close()

    values = [((i*3) % 5-2, (i*7) % 5-2) for i in range(16)]
    exact = dense(values, (1,), 2, 1, False)
    require(round_oracle(values, (1,), 2) == exact, "independent dense and stage Fourier agreement")
    premature = round_oracle(values, (1,), 2, premature=True)
    require(premature != exact, "nonzero whole-transform rounding witness")
    # The forward suite executes this exact positive packet. Reuse the mutant's
    # actual protected return below instead of executing that baseline twice.
    correct_hash = sha256(encode(exact, 4)).hexdigest()

    original_twiddle = Fourier.twiddle

    def premature_twiddle(self, plan, h, opposite):
        self.idle()
        with self.scope.suspended():
            returned = self.grid.truncate(borrowed_tape(self.current),
                *(borrowed_count(v) for v in (plan.wide, plan.n, plan.small, plan.gaussians)))
        self.accept(returned)
        zero = Count.literal(0)
        try:
            with self.scope.suspended():
                returned = self.grid.expand(borrowed_tape(self.current),
                    *(borrowed_count(v) for v in (plan.small, plan.n, zero, plan.gaussians)))
            self.accept(returned)
        finally:
            zero.close()
        original_twiddle(self, plan, h, opposite)

    with patch.object(Fourier, "twiddle", premature_twiddle):
        _, mutant, _ = packet((1,), owner=owner, values=values, expected=premature, consume=False)
    require(mutant["sha256"] != correct_hash, "physical premature-rounding mutant differs")
    rejected.append("physical_premature_truncation")
    counts = tuple(Count.literal(v) for v in (1, 2, 2, 1))
    try:
        try:
            owner.run(tape([0]*128), tape([1]), *counts)
        except ValueError as error:
            require("consume prior Fourier output" in str(error), "intended protected-output rejection")
            rejected.append("protected_output")
        else:
            raise ValueError("missing protected Fourier output rejection")
    finally:
        for value in counts:
            value.close()
        owner.output.clear()
        erase_marker(owner.output)

    basis = [(0, 0)]*16
    basis[4] = (4, 0)
    with patch.object(Fourier, "reversal", lambda _self, _plan: None):
        try:
            packet((1,), owner=owner, values=basis)
        except ValueError as error:
            require("dense polynomial oracle" in str(error), "endpoint order mutant reaches comparison")
            rejected.append("omitted_physical_reversal")
        else:
            raise ValueError("missing endpoint bit-reversal failure")
        finally:
            owner.output.clear()
            erase_marker(owner.output)
    return {"controls": rejected, "correct_sha256": correct_hash,
            "premature_sha256": mutant["sha256"], "exact": exact, "premature": premature}


def budget():
    alpha = Fraction(99827101, 100000000)
    tau = Fraction(332353, 332929)
    cap = Fraction(997, 1000)
    saving = cap*(1-alpha)
    require(saving == Fraction(172380303, 100000000000), "exact saturated Fourier saving")
    require(alpha > tau and cap*(1-tau) > saving, "strict routing absorption gap")
    cases = []
    for epsilon in (Fraction(1, 40), Fraction(1, 2), cap, Fraction(999, 1000)):
        s = min(epsilon, cap)
        root = 1-s*(1-alpha)
        route = 1-s*(1-tau)
        require(root > route and root > 1-epsilon, "strict root over routing and diagonal powers")
        cases.append({"epsilon": str(epsilon), "root_power": str(root), "saving": str(1-root)})
    # Complete rounding, including both signs, for grids before/after any prefix.
    divisibility = 0
    for p, A in product(range(2, 5), range(1, 7)):
        for used in range(A+1):
            for numerator in range(-7, 8):
                exact_scaled = Fraction(numerator*(1 << A), 1 << used)
                require(exact_scaled.denominator == 1, "whole-transform lifted divisibility")
                divisibility += 1
    return {"alpha": str(alpha), "tau": str(tau), "saturated_saving": str(saving),
            "exponent_cases": cases, "finite_divisibility_controls": divisibility,
            "universal_proof": "PROOF.md; these finite checks do not prove the inherited suppliers"}
