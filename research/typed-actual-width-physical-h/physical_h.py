"""Typed actual-width physical H and toward-zero rounded return.

The machine below is the object under test. It is not the PR #3623 arithmetic
oracle. Successful calls are data-independent in every tape and gate count.
"""

from __future__ import annotations


class Tape:
    """Unit-seek bit tape. Counters start after presentation."""

    def __init__(self, n):
        if n < 0:
            raise ValueError("tape length")
        self.cells = [0] * n
        self.head = 0
        self.read = 0
        self.write = 0
        self.move = 0

    def seek(self, pos):
        if not 0 <= pos <= len(self.cells):
            raise ValueError("tape boundary")
        self.move += abs(pos - self.head)
        self.head = pos

    def read_bit(self):
        if self.head >= len(self.cells):
            raise ValueError("tape boundary")
        self.read += 1
        return self.cells[self.head]

    def write_bit(self, bit):
        if self.head >= len(self.cells) or bit not in (0, 1):
            raise ValueError("tape boundary")
        self.write += 1
        self.cells[self.head] = bit

    def scan_read(self, pos, n):
        self.seek(pos)
        out = []
        for i in range(n):
            if i:
                self.seek(pos + i)
            out.append(self.read_bit())
        return out

    def scan_write(self, pos, bits):
        self.seek(pos)
        for i, bit in enumerate(bits):
            if i:
                self.seek(pos + i)
            self.write_bit(bit)

    def poke(self, pos, bits):
        for i, bit in enumerate(bits):
            self.cells[pos + i] = bit


def bits_from_int(value, width):
    if width < 1 or not isinstance(value, int):
        raise ValueError("bit word")
    if value < 0:
        value = (1 << width) + value
    if value < 0 or value >= 1 << width:
        raise ValueError("bit word")
    return [((value >> (width - 1 - i)) & 1) for i in range(width)]


def int_from_bits(bits):
    width = len(bits)
    value = 0
    for bit in bits:
        value = (value << 1) | bit
    if bits and bits[0]:
        value -= 1 << width
    return value


def add_bits(a, b, gates, cin=0):
    width = len(a)
    if len(b) != width or cin not in (0, 1):
        raise ValueError("adder width")
    carry = cin
    out = [0] * width
    for i in range(width - 1, -1, -1):
        gates[0] += 1
        total = a[i] + b[i] + carry
        out[i] = total & 1
        carry = total >> 1
    got = int_from_bits(out)
    expect = int_from_bits(a) + int_from_bits(b) + cin
    if got != expect:
        raise ValueError("work width")
    return out


def sub_bits(a, b, gates):
    flipped = [1 - bit for bit in b]
    gates[0] += len(b)
    return add_bits(a, flipped, gates, cin=1)


def slots_for(ell, flags, k):
    if not (ell >= 2 and flags and 1 <= k < ell):
        raise ValueError("layout domain")
    original = tuple((i, h) for i, long in enumerate(flags)
                     for h in range(ell - (not long) - 1, -1, -1))
    b, q = (ell - 1) % k, (ell - 1) // k
    prefix = [(i, ell - 1) for i, long in enumerate(flags) if long]
    prefix += [(i, h) for h in range(b - 1, -1, -1) for i in range(len(flags))]
    chunks = [(i, h) for j in range(q) for i in range(len(flags))
              for h in range(ell - 2 - j * k, ell - 2 - (j + 1) * k, -1)]
    changed = tuple(prefix + chunks)
    if len(set(changed)) != len(original) or set(changed) != set(original):
        raise ValueError("layout bijection")
    return original, changed


def selected_bits(slots, h):
    return tuple(len(slots) - 1 - j for j, item in enumerate(slots) if item[1] == h)


def bit_at(x, slots, named):
    return (x >> (len(slots) - 1 - slots.index(named))) & 1


def origin_of_target(before, after):
    """original address x whose image is physical address y, matching reorder."""
    count = 1 << len(before)
    origin = [None] * count
    for x in range(count):
        y = 0
        for name in after:
            y = (y << 1) | bit_at(x, before, name)
        origin[y] = x
    if any(item is None for item in origin):
        raise ValueError("layout bijection")
    return tuple(origin)


def levels_for(ell, flags):
    levels = list(range(ell - 2, -1, -1))
    if any(flags):
        levels.insert(0, ell - 1)
    return tuple(levels)


def trunc_pow2(value, g):
    if g < 0:
        raise ValueError("shift")
    if value >= 0:
        return value >> g
    return -((-value) >> g)


def arithmetic_shift(value, g):
    return value >> g


class TypedActualWidthH:
    """One common or prefix round of matched-layout H, then Q_p.

    The borrowed cube is MSB-first two's complement of width w=p+2.
    The root return is LSB-first. The consumer return is MSB-first.
    Work width is W=p+g+2. Scratch is blanked. The object is one-shot.
    """

    def __init__(self, ell, flags, k, p):
        flags = tuple(bool(item) for item in flags)
        original, physical = slots_for(ell, flags, k)
        self.ell = ell
        self.flags = flags
        self.k = k
        self.p = p
        if not isinstance(p, int) or p < 1:
            raise ValueError("precision")
        self.original = original
        self.physical = physical
        self.levels = levels_for(ell, flags)
        self.w = p + 2
        self.used = False

    def matched_bits(self, h):
        if h not in self.levels:
            raise ValueError("round index")
        axes = len(self.flags)
        owned = sum(self.flags)
        b, q = (self.ell - 1) % self.k, (self.ell - 1) // self.k
        address_bits = len(self.physical)
        if b <= h < self.ell - 1:
            j, rho = (self.ell - 2 - h) // self.k, (h - b) % self.k
            left = owned + axes * b + j * axes * self.k
            right = (q - j - 1) * axes * self.k
            if left + axes * self.k + right != address_bits:
                raise ValueError("complete root extent")
            bits = tuple(right + rho + t * self.k for t in range(axes))
            literal = selected_bits(self.physical, h)
            if tuple(sorted(bits)) != tuple(sorted(literal)) or len(bits) != len(literal):
                raise ValueError("literal root selected positions")
            return bits
        return selected_bits(self.physical, h)

    def require_bits(self, h, bits):
        if tuple(bits) != self.matched_bits(h):
            raise ValueError("selected-bit descriptor")
        return self.matched_bits(h)

    def run(self, cube, h, source_order="physical"):
        if self.used:
            raise ValueError("one-shot physical H")
        self.used = True
        bits = self.matched_bits(h)
        if source_order not in ("physical", "original"):
            raise ValueError("source order")
        g = len(bits)
        width = self.w
        work = self.p + g + 2
        records = 1 << len(self.physical)
        coeffs = 1 << self.ell
        if len(cube) != records:
            raise ValueError("record count")
        bound = 1 << self.p
        for row in cube:
            if len(row) != coeffs:
                raise ValueError("coefficient count")
            for real, imag in row:
                if not isinstance(real, int) or not isinstance(imag, int):
                    raise ValueError("numerator")
                if abs(real) > bound or abs(imag) > bound:
                    raise ValueError("unit disk")
        source_slots = self.physical if source_order == "physical" else self.original
        origin = origin_of_target(source_slots, self.physical)
        sw = coeffs * 2 * width
        source = Tape(records * sw)
        scratch = Tape(records * coeffs * 2 * work)
        root = Tape(records * sw)
        consumer = Tape(records * sw)
        gates = [0]
        for x, row in enumerate(cube):
            _present_record(source, x * sw, row, width)
        invoice_before = (source.read, source.write, source.move)
        self._layout(source, scratch, origin, records, coeffs, width, work, gates)
        if (source.read, source.write, source.move) == invoice_before:
            raise ValueError("layout was not charged")
        for beta in bits:
            self._butterfly(scratch, records, coeffs, work, beta, gates)
            scratch.seek(0)
        decoded = self._round_and_bridge(
            scratch, root, consumer, records, coeffs, width, work, g, gates)
        self._blank(scratch)
        source.seek(0)
        root.seek(0)
        consumer.seek(0)
        if source.cells != _presented_cells(cube, width):
            raise ValueError("borrowed source")
        if any(scratch.cells) or scratch.head or root.head or consumer.head or source.head:
            raise ValueError("head return")
        shadow = _integer_h(cube, origin, bits)
        if decoded != shadow:
            raise ValueError("rounded return")
        ledger = {
            "read": source.read + scratch.read + root.read + consumer.read,
            "write": source.write + scratch.write + root.write + consumer.write,
            "move": source.move + scratch.move + root.move + consumer.move,
            "gate": gates[0],
        }
        return decoded, ledger, {
            "records": records,
            "coefficients": coeffs,
            "selected_bits": bits,
            "work_width": work,
            "packet_width": width,
        }

    def _layout(self, source, scratch, origin, records, coeffs, width, work, gates):
        sw = coeffs * 2 * width
        rw = coeffs * 2 * work
        bound = 1 << self.p
        for y in range(records):
            packed = source.scan_read(origin[y] * sw, sw)
            extended = []
            for index in range(coeffs * 2):
                word = packed[index * width:(index + 1) * width]
                value = int_from_bits(word)
                gates[0] += 1
                if abs(value) > bound:
                    raise ValueError("unit disk")
                sign = word[0]
                extended.extend([sign] * (work - width))
                gates[0] += work - width
                extended.extend(word)
            scratch.scan_write(y * rw, extended)
        source.seek(0)
        scratch.seek(0)

    def _butterfly(self, scratch, records, coeffs, work, beta, gates):
        """Move address bit beta to adjacent pairs, butterfly, and merge back.

        Every pass is a sequential scan. Partners are the records that differ
        only in bit beta, written back as sum on the clear bit and difference
        on the set bit.
        """
        rw = coeffs * 2 * work
        low = Tape((records // 2) * rw)
        high = Tape((records // 2) * rw)
        paired = Tape(records * rw)
        low_n = high_n = 0
        for x in range(records):
            record = scratch.scan_read(x * rw, rw)
            gates[0] += 1
            if (x >> beta) & 1:
                high.scan_write(high_n * rw, record)
                high_n += 1
            else:
                low.scan_write(low_n * rw, record)
                low_n += 1
        if low_n != records // 2 or high_n != records // 2:
            raise ValueError("address split")
        scratch.seek(0)
        low.seek(0)
        high.seek(0)
        for index in range(records // 2):
            left = low.scan_read(index * rw, rw)
            right = high.scan_read(index * rw, rw)
            paired.scan_write((2 * index) * rw, left)
            paired.scan_write((2 * index + 1) * rw, right)
        low.seek(0)
        high.seek(0)
        paired.seek(0)
        _adjacent_butterfly(paired, records, coeffs, work, gates)
        paired.seek(0)
        for index in range(records // 2):
            left = paired.scan_read((2 * index) * rw, rw)
            right = paired.scan_read((2 * index + 1) * rw, rw)
            low.scan_write(index * rw, left)
            high.scan_write(index * rw, right)
        low.seek(0)
        high.seek(0)
        paired.seek(0)
        low_n = high_n = 0
        for x in range(records):
            gates[0] += 1
            if (x >> beta) & 1:
                record = high.scan_read(high_n * rw, rw)
                high_n += 1
            else:
                record = low.scan_read(low_n * rw, rw)
                low_n += 1
            scratch.scan_write(x * rw, record)
        scratch.seek(0)
        low.seek(0)
        high.seek(0)
        paired.seek(0)
        for tape in (low, high, paired):
            _blank_tape(tape)
            if any(tape.cells) or tape.head:
                raise ValueError("auxiliary return")
        # Auxiliary invoices are part of this round. Fold them into scratch's
        # counters so the caller ledger stays four tapes plus these locals.
        for tape in (low, high, paired):
            scratch.read += tape.read
            scratch.write += tape.write
            scratch.move += tape.move

    def _round_and_bridge(self, scratch, root, consumer, records, coeffs, width, work, g, gates):
        decoded = []
        for record in range(records):
            row = []
            for coeff in range(coeffs):
                pair = []
                for part in range(2):
                    index = (record * coeffs + coeff) * 2 + part
                    word = scratch.scan_read(index * work, work)
                    signed = _q_component(word, g, width, gates)
                    root.scan_write(index * width, list(reversed(signed)))
                    consumer.scan_write(index * width, signed)
                    pair.append(int_from_bits(signed))
                row.append((pair[0], pair[1]))
            decoded.append(row)
        return decoded

    def _blank(self, scratch):
        scratch.seek(0)
        for pos in range(len(scratch.cells)):
            if pos:
                scratch.seek(pos)
            scratch.write_bit(0)
        scratch.seek(0)


def _present_record(tape, pos, row, width):
    bits = []
    for real, imag in row:
        bits.extend(bits_from_int(real, width))
        bits.extend(bits_from_int(imag, width))
    tape.poke(pos, bits)


def _presented_cells(cube, width):
    bits = []
    for row in cube:
        for real, imag in row:
            bits.extend(bits_from_int(real, width))
            bits.extend(bits_from_int(imag, width))
    return bits


def _blank_tape(tape):
    tape.seek(0)
    for pos in range(len(tape.cells)):
        if pos:
            tape.seek(pos)
        tape.write_bit(0)
    tape.seek(0)


def _adjacent_butterfly(paired, records, coeffs, work, gates):
    rw = coeffs * 2 * work
    for index in range(records // 2):
        left = 2 * index
        right = left + 1
        rec_a = paired.scan_read(left * rw, rw)
        rec_b = paired.scan_read(right * rw, rw)
        out_a, out_b = _mix(rec_a, rec_b, coeffs, work, gates)
        paired.scan_write(left * rw, out_a)
        paired.scan_write(right * rw, out_b)
    paired.seek(0)


def _mix(rec_a, rec_b, coeffs, work, gates):
    out_a, out_b = [], []
    for index in range(coeffs * 2):
        a = rec_a[index * work:(index + 1) * work]
        b = rec_b[index * work:(index + 1) * work]
        out_a.extend(add_bits(a, b, gates, cin=0))
        out_b.extend(sub_bits(a, b, gates))
    return out_a, out_b


def _q_component(word, g, width, gates):
    sign = word[0]
    magnitude = [bit ^ sign for bit in word]
    gates[0] += len(word)
    magnitude = add_bits(magnitude, [0] * len(word), gates, cin=sign)
    if int_from_bits(magnitude) < 0:
        raise ValueError("magnitude")
    narrowed = magnitude[:width]
    if int_from_bits(narrowed) != int_from_bits(magnitude) >> g:
        raise ValueError("shift wiring")
    signed = [bit ^ sign for bit in narrowed]
    gates[0] += width
    return add_bits(signed, [0] * width, gates, cin=sign)


def _integer_h(cube, origin, bits):
    records = [list(cube[origin[y]]) for y in range(len(origin))]
    for beta in bits:
        half = 1 << beta
        span = half << 1
        block = 0
        while block < len(records):
            for offset in range(half):
                left, right = block + offset, block + offset + half
                mixed_l, mixed_r = [], []
                for (ar, ai), (br, bi) in zip(records[left], records[right]):
                    mixed_l.append((ar + br, ai + bi))
                    mixed_r.append((ar - br, ai - bi))
                records[left], records[right] = mixed_l, mixed_r
            block += span
    denom = 1 << len(bits)
    return [[(trunc_pow2(real, len(bits)), trunc_pow2(imag, len(bits)))
             for real, imag in row] for row in records]


def closed_read_write_gate(records, coeffs, g, p):
    """Data-independent read, write and gate totals for one successful call.

    Layout reads each source bit once and writes the sign-extended work image.
    Each selected bit then uses five sequential work-length copies (split,
    interleave, adjacent butterfly, deinterleave, merge) and blanks the two
    half tapes plus the paired tape. Q_p reads the work image once and writes
    the LSB root word and the MSB consumer word. The work tape is blanked
    last. Gates are the sign fan-out, one disk test per component, two address
    tests per record per selected bit, three width-W add/invert steps per
    butterfly component pair, and the abs/resign pair.
    """
    work = p + g + 2
    width = p + 2
    components = records * coeffs * 2
    work_bits = components * work
    reads = components * width + g * 5 * work_bits + work_bits
    writes = (work_bits + g * 7 * work_bits
              + 2 * components * width + work_bits)
    gates = (components * (work - width) + components
             + g * 2 * records
             + g * (components // 2) * 3 * work
             + components * (2 * work + 2 * width))
    return {"read": reads, "write": writes, "gate": gates}


def itinerary_moves(records, coeffs, g, p, origin, betas):
    """Head travel of the successful-call schedule. Ignores coefficient values."""
    work = p + g + 2
    width = p + 2
    sw = coeffs * 2 * width
    rw = coeffs * 2 * work
    moves = 0
    head_s = 0
    head_w = 0

    def seek(head, pos):
        return head, abs(pos - head)

    for y in range(records):
        pos = origin[y] * sw
        head_s, delta = seek(head_s, pos)
        moves += delta
        if sw > 1:
            moves += sw - 1
            head_s = pos + sw - 1
        posw = y * rw
        head_w, delta = seek(head_w, posw)
        moves += delta
        if rw > 1:
            moves += rw - 1
            head_w = posw + rw - 1
    if len(betas) != g:
        raise ValueError("selected-bit count")
    moves += abs(0 - head_s)
    moves += abs(0 - head_w)
    for _beta in betas:
        moves += _linear_level_moves(records, rw)
    # Q_p sequential scans. Work, root and consumer each start at 0.
    work_bits = records * rw
    packet_bits = records * sw
    moves += _scan_moves(work_bits)  # read work
    moves += _scan_moves(packet_bits)  # write root
    moves += _scan_moves(packet_bits)  # write consumer
    if work_bits:
        moves += work_bits - 1  # rewind work from its last bit
    if packet_bits:
        moves += 2 * (packet_bits - 1)  # rewind root and consumer
    # Blank from 0 across the work tape and rewind.
    moves += _scan_moves(work_bits)
    if work_bits:
        moves += work_bits - 1
    # Final source/root/consumer seeks are already at 0. Caller seeks source
    # home at layout end. run() seeks source, root and consumer to 0 again.
    return moves


def _scan_moves(n):
    """Moves while scanning n contiguous bits starting at the current origin 0."""
    if n <= 1:
        return 0
    return n - 1


def _level_moves(records, rw, beta):
    """In-place pair schedule plus the homing seek back to 0."""
    moves = 0
    head = 0
    half = 1 << beta
    span = half << 1
    block = 0
    while block < records:
        for offset in range(half):
            for rec in (block + offset, block + offset + half,
                        block + offset, block + offset + half):
                pos = rec * rw
                moves += abs(pos - head)
                head = pos
                if rw > 1:
                    moves += rw - 1
                    head = pos + rw - 1
        block += span
    moves += abs(0 - head)
    return moves


def _scan_and_home(n):
    """Forward scan from cell 0, then rewind to 0."""
    if n <= 1:
        return 0
    return 2 * (n - 1)


def _linear_level_moves(records, rw):
    """Five sequential passes, one adjacent butterfly, and auxiliary blanking."""
    length = records * rw
    half = length // 2
    adjacent = _level_moves(records, rw, 0)
    return (5 * _scan_and_home(length) + 10 * _scan_and_home(half) + adjacent)
