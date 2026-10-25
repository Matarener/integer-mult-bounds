"""Checker-only natural-coordinate reference; no physical numerical calls."""
from math import isqrt
from tensor_sources import require


def tz(value, divisor):
    return (abs(value)//divisor)*(-1 if value < 0 else 1)


class Cursor:
    def __init__(self, raw):
        self.raw, self.position = raw, 0

    def take(self, length):
        end = self.position+length
        require(end <= len(self.raw), "reference page extent")
        result = self.raw[self.position:end]
        self.position = end
        return result

    def count(self):
        from words import RIGHT
        bits = []
        while True:
            value = self.take(1)[0]
            if value == RIGHT:
                break
            require(value in (0, 1), "reference count alphabet")
            bits.append(value)
        require(bits and (len(bits) == 1 or bits[-1]), "reference canonical count")
        return sum(bit << i for i, bit in enumerate(bits))

    def integer(self):
        sign = self.take(1)[0]
        require(sign in (0, 1), "reference signed origin")
        value = self.count()
        require(not sign or value, "reference canonical signed zero")
        return -value if sign else value

    def word(self, width):
        bits = self.take(width)
        require(all(bit in (0, 1) for bit in bits), "reference signed data word")
        value = sum(bit << i for i, bit in enumerate(bits))
        return value-(1 << width) if bits[-1] else value

    def frame(self):
        return Cursor(self.take(self.count()))

    def header(self, names):
        return {name: self.count() for name in names.split()}

    def end(self):
        require(self.position == len(self.raw), "reference complete page consumption")


def expansion_page(page):
    tile = page.header("version p P sigma s t alpha radius source_count input_capacity target_length blocks")
    tile["source_start"], tile["target_start"] = page.integer(), page.integer()
    blocks = []
    for _ in range(tile["blocks"]):
        frame = page.frame()
        block = frame.header("version p P width sigma s t alpha radius n m nc")
        block["source_start"], block["target_start"] = frame.integer(), frame.integer()
        for name, length in (("A", block["n"]), ("K", block["nc"]), ("B", block["m"])):
            block[name] = [frame.word(block["width"]) for _ in range(length)]
        block["c"] = frame.word(block["width"])
        frame.end()
        blocks.append(block)
    page.end()
    return tile, blocks


def compression_page(page):
    header = page.header("version p P width m target_length core_offset core_length boundary_length band cell_count")
    header["selection"] = [page.count() for _ in range(header["m"])]
    diagonal = []
    for _ in range(header["cell_count"]):
        size, inside, boundary = page.count(), page.count(), page.count()
        require(inside == 0 and boundary == size, "declared two-axis fixture has only boundary cells")
        diagonal.extend(page.word(header["width"]) for _ in range(size))
    require(len(diagonal) == header["m"] == header["boundary_length"], "reference complete boundary-only source rows")
    header["diagonal"] = diagonal
    band, width, m = header["band"], header["width"], header["m"]
    header["lower"] = [[page.word(width) for _ in range(band)] for _ in range(m)]
    header["upper"] = list(reversed([[page.word(width) for _ in range(band+1)] for _ in range(m)]))
    page.end()
    return header


def catalogue(raw):
    source = Cursor(raw)
    header = source.header("version mode p ell axes alpha inner_bits P sigma radius expansion_capacity halo w")
    header["flags"] = tuple(source.take(header["axes"]))
    D = header["axes"]+1
    header["sources"] = [sum(bit << j for j, bit in enumerate(source.take(header["ell"]))) for _ in range(D)]
    profiles = []
    for _ in range(D):
        profile = source.frame()
        row = profile.header("s t width tiles")
        for name in ("expansion_windows", "compression_windows", "cores", "compression_sources"):
            frame = profile.frame()
            row[name] = [(frame.integer(), frame.count()) for _ in range(row["tiles"])]
            frame.end()
        for name, parse in (("expansion_pages", expansion_page), ("compression_pages", compression_page)):
            frame = profile.frame()
            row[name] = [parse(frame.frame()) for _ in range(row["tiles"])]
            frame.end()
        profile.end()
        profiles.append(row)
    source.end()
    return header, profiles


def expand(line, profile):
    result = [None]*profile["t"]
    for tile, blocks in profile["expansion_pages"]:
        for block in blocks:
            p, P, n, Q = block["p"], block["P"], block["n"], 1 << block["P"]
            data = [line[(block["source_start"]+i) % len(line)] for i in range(n)]
            for z in range(block["m"]):
                pair = []
                for c in (0, 1):
                    weighted = [tz(block["A"][i]*(data[i][c] << (P-p)), Q) for i in range(n)]
                    convolution = tz(sum(weighted[i]*block["K"][n-1+z-i] for i in range(n)), Q)
                    post = tz(block["B"][z]*convolution, Q)
                    fine = tz(block["c"]*post, Q)
                    pair.append(tz(fine, 1 << (P-p-2*block["sigma"])))
                position = block["target_start"]+z
                require(result[position] is None, "reference expansion has unique natural target positions")
                result[position] = tuple(pair)
    require(all(value is not None for value in result), "reference complete expanded axis")
    return result


def compress(line, profile):
    result = [None]*profile["s"]
    for page, (start, length), (core, count) in zip(profile["compression_pages"], profile["compression_windows"], profile["cores"]):
        p, P, m, band = (page[name] for name in ("p", "P", "m", "band"))
        Q = 1 << P
        components = []
        for component in (0, 1):
            selected = [line[(start+offset) % len(line)][component] << (P-p) for offset in page["selection"]]
            y, x = [0]*m, [0]*m
            for i in range(m):
                total = sum(coefficient*y[j] for coefficient, j in zip(page["lower"][i], range(i-band, i)) if j >= 0)
                y[i] = tz(selected[i]*Q-total, Q)
            for i in reversed(range(m)):
                total = sum(coefficient*x[j] for coefficient, j in zip(page["upper"][i][:-1], range(i+1, i+band+1)) if j < m)
                x[i] = tz((y[i]*Q-total)*page["upper"][i][-1], Q*Q)
            offset = page["core_offset"]
            j = (32*p-1).bit_length()
            components.append([tz(page["diagonal"][i]*x[i], 1 << (2*P-p+j)) for i in range(offset, offset+count)])
        for i, pair in enumerate(zip(*components)):
            require(result[core+i] is None, "reference source cores have unique natural positions")
            result[core+i] = tuple(pair)
    require(all(value is not None for value in result), "reference complete compressed source axis")
    return result


def roots16(p):
    B, U = 1 << p, 1 << (2*p-1)
    m = isqrt(1 << (4*p-3))
    c, s, h = isqrt(U+m), isqrt(U-m-1), isqrt(U)
    return ((B, 0), (c, s), (h, h), (s, c), (0, B), (-s, c), (-h, h), (-c, s))


def middle(values, p):
    from check_fourier import dense
    from chirp_check_middle import conjugate, multiply
    from ring_check_product import oracle
    fine_p = p+6
    fine = roots16(fine_p)
    basis = fine[1], fine[2], fine[4], (-(1 << fine_p), 0)
    kernel = []
    for i in range(8):
        for j in range(8):
            exponent = (-7*i*i-7*j*j) % 16
            phase = 1 << fine_p, 0
            for bit in range(4):
                if exponent & (1 << bit):
                    phase = multiply(phase, basis[bit], fine_p)
            kernel.append(tuple(tz(value, 64) for value in phase))
    twists = roots16(p)
    incoming = [multiply(conjugate(a), b, p) for a, b in zip(kernel, values)]
    left = [multiply(twists[i % 8], a, p) for i, a in enumerate(kernel)]
    right = [multiply(twists[i % 8], a, p) for i, a in enumerate(incoming)]
    first, second = dense(left, (1,), 3, 1, False), dense(right, (1,), 3, 1, False)
    multiplied = oracle(first, second, 3, p, 3, 1)
    opposite = dense(multiplied, (1,), 3, 1, True)
    cyclic = [multiply(conjugate(twists[i % 8]), (8*a, 8*b), p) for i, (a, b) in enumerate(opposite)]
    return [multiply(conjugate(a), b, p) for a, b in zip(kernel, cyclic)]


def axis_apply(data, shape, axis, profile, operation):
    rows, columns = shape
    lines = [[data[i*columns+j] for i in range(rows)] for j in range(columns)] if axis == 0 else [data[i*columns:(i+1)*columns] for i in range(rows)]
    result = [operation(line, profile) for line in lines]
    if axis == 0:
        return [result[j][i] for i in range(len(result[0])) for j in range(columns)], (len(result[0]), columns)
    return [pair for line in result for pair in line], (rows, len(result[0]))


def full(values, raw_catalogue, opposite=False):
    header, profiles = catalogue(raw_catalogue)
    require(header["p"] == 48 and header["P"] == 80 and header["sources"] == [7, 7]
            and header["flags"] == (1,), "declared independent two-axis fixture")
    data = [(a, -b if opposite else b) for a, b in values]
    shape = (7, 7)
    for axis in (0, 1):
        data, shape = axis_apply(data, shape, axis, profiles[axis], expand)
    expanded = data
    data = middle(data, header["p"])
    middle_values = data
    for axis in (0, 1):
        data, shape = axis_apply(data, shape, axis, profiles[axis], compress)
    require(shape == (7, 7), "reference returns to the complete original source box")
    return [(a << 40, (-b if opposite else b) << 40) for a, b in data], expanded, middle_values
