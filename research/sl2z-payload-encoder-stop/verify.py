#!/usr/bin/env python3
"""The PR #3947 one-XOR carrier does not losslessly encode integer B=X^2 Y^2.

The stop rule on discussion comment 19032401 asks for a payload, an injective
encoder, and a price, and says to stop if that carrier's one-XOR endpoint
already implements the target. This verifier checks that stop.

Integer addresses, the mod-4 quotient (the largest modulus on which B^2 = I),
and the published three-bit representation are recomputed here. No predecessor
package is imported.
"""

from itertools import permutations, product

X = ((1, 1), (0, 1))
Y = ((1, 0), (1, 1))


def matmul(left, right):
    return tuple(
        tuple(left[i][0] * right[0][j] + left[i][1] * right[1][j] for j in range(2))
        for i in range(2)
    )


def matvec(matrix, vector):
    return tuple(
        sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix
    )


def matmul3(left, right):
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(3)) % 2 for j in range(3))
        for i in range(3)
    )


B = matmul(matmul(X, X), matmul(Y, Y))
B2 = matmul(B, B)
B2_MINUS_I = (
    (B2[0][0] - 1, B2[0][1]),
    (B2[1][0], B2[1][1] - 1),
)


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def check(condition, message="check failed"):
    if not condition:
        raise AssertionError(message)


def apply_b_mod(point, modulus):
    image = matvec(B, point)
    return (image[0] % modulus, image[1] % modulus)


def bits_of_pair(x, y):
    return (x & 1, (x >> 1) & 1, y & 1, (y >> 1) & 1)


def pair_of_bits(bits):
    return bits[0] + 2 * bits[1], bits[2] + 2 * bits[3]


def carrier_representation():
    """Projective action of X and Y mod 3, restricted to the sum-zero F2-plane."""
    points = ((1, 0), (0, 1), (1, 1), (1, 2))

    def normalize(u, v):
        u %= 3
        v %= 3
        if (u, v) == (0, 0):
            raise AssertionError("projective image hit zero")
        for scale in (1, 2):
            candidate = ((scale * u) % 3, (scale * v) % 3)
            if candidate in points:
                return points.index(candidate)
        raise AssertionError((u, v))

    def permutation(matrix):
        images = []
        for u, v in points:
            images.append(
                normalize(
                    matrix[0][0] * u + matrix[0][1] * v,
                    matrix[1][0] * u + matrix[1][1] * v,
                )
            )
        return tuple(images)

    def on_f2_4(permutation_images, vector):
        out = [0, 0, 0, 0]
        for source, dest in enumerate(permutation_images):
            out[dest] ^= vector[source]
        return tuple(out)

    def coordinates(vector):
        # w0=(0,1,0,1), w1=(1,1,1,1), w2=(0,1,1,0), in e0..e3 order.
        c1 = vector[0]
        c2 = (vector[2] + c1) % 2
        c0 = (vector[3] + c1) % 2
        if (c0 + c1 + c2) % 2 != vector[1] or (c0 + c1) % 2 != vector[3]:
            return None
        return (c0, c1, c2)

    def rho(permutation_images):
        columns = []
        basis = ((0, 1, 0, 1), (1, 1, 1, 1), (0, 1, 1, 0))
        for vector in basis:
            image = coordinates(on_f2_4(permutation_images, vector))
            if image is None:
                raise AssertionError("basis vector left the sum-zero plane")
            columns.append(image)
        return tuple(tuple(columns[j][i] for j in range(3)) for i in range(3))

    x_mod = tuple(tuple(entry % 3 for entry in row) for row in X)
    y_mod = tuple(tuple(entry % 3 for entry in row) for row in Y)
    rho_x = rho(permutation(x_mod))
    rho_y = rho(permutation(y_mod))
    rho_b = matmul3(matmul3(rho_x, rho_x), matmul3(rho_y, rho_y))
    return rho_x, rho_y, rho_b


def fixed_add(left, right, width):
    carry = 0
    total = 0
    for bit in range(width):
        xb = (left >> bit) & 1
        yb = (right >> bit) & 1
        partial = xb ^ yb
        summed = partial ^ carry
        carry = (xb & yb) | (carry & partial)
        total |= summed << bit
    return total, carry


def four_shears(x, y, width):
    """Y then Y then X then X, with the fixed widths proved for m-bit inputs."""
    a, b = x, y
    widths = (width + 1, width + 2, width + 2, width + 3)
    b, carry = fixed_add(b, a, widths[0])
    if carry:
        return None
    b, carry = fixed_add(b, a, widths[1])
    if carry:
        return None
    a, carry = fixed_add(a, b, widths[2])
    if carry:
        return None
    a, carry = fixed_add(a, b, widths[3])
    if carry:
        return None
    return a, b


def wiring_realizes(output_bits):
    """Bit placement into (a,b,c,p,q,r), constant scratch, then b ^= c.

    Encoder and decoder are wirings only: no XOR except the carrier instruction,
    and no AND. Scratch bits are constants and must be readable only as discarded
    positions. Returns one witness placement, or None.
    """
    for in_slots in permutations(range(6), 4):
        rest = [slot for slot in range(6) if slot not in in_slots]
        for constants in product((0, 1), repeat=2):
            for out_slots in permutations(range(6), 4):
                if _wiring_ok(output_bits, in_slots, rest, constants, out_slots):
                    return in_slots, constants, out_slots
    return None


def _wiring_ok(output_bits, in_slots, rest, constants, out_slots):
    for x in range(4):
        for y in range(4):
            state = [0] * 6
            for bit, slot in zip(bits_of_pair(x, y), in_slots):
                state[slot] = bit
            state[rest[0]] = constants[0]
            state[rest[1]] = constants[1]
            state[1] ^= state[2]
            if tuple(state[slot] for slot in out_slots) != output_bits(x, y):
                return False
    return True


def hamming(left, right, width):
    distance = 0
    for value_l, value_r in zip(left, right):
        for bit in range(width):
            distance += ((value_l >> bit) ^ (value_r >> bit)) & 1
    return distance


def main():
    check(B == ((5, 2), (2, 1)), B)
    check(B2 == ((29, 12), (12, 5)), B2)
    check(B2_MINUS_I == ((28, 12), (12, 4)), B2_MINUS_I)
    modulus = 0
    for entry in (28, 12, 12, 4):
        modulus = gcd(modulus, entry)
    assert modulus == 4

    # (B^2 - I) p = 0 over Z has only p = 0. From 12x+4y = 0, y = -3x,
    # then 28x+12y = -8x = 0.
    for x in range(-12, 13):
        for y in range(-12, 13):
            image = matvec(B2_MINUS_I, (x, y))
            if image == (0, 0):
                check((x, y) == (0, 0), (x, y))
    check(matvec(B2_MINUS_I, (1, -3)) == (-8, 0))

    rho_x, rho_y, rho_b = carrier_representation()
    check(rho_x == ((0, 0, 1), (0, 1, 0), (1, 0, 1)), rho_x)
    check(rho_y == ((1, 0, 1), (1, 1, 0), (1, 0, 0)), rho_y)
    check(rho_b == ((1, 0, 0), (0, 1, 1), (0, 0, 1)), rho_b)
    check(matmul3(rho_b, rho_b) == ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    # Column vector (a,b,c) maps to (a, b+c, c): one XOR, and not the identity.
    check(matvec(rho_b, (0, 0, 1)) == (0, 1, 1))
    x_cubed = matmul(matmul(X, X), X)
    check(x_cubed == ((1, 3), (0, 1)))
    check(x_cubed != ((1, 0), (0, 1)))
    identity3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    check(matmul3(matmul3(rho_x, rho_x), rho_x) == identity3)

    # One application of a k-bit map distinguishes at most 2^k payloads.
    check(2 ** (2 * 2) > 8)  # m=2 box does not inject into the 3-bit block
    check(2 ** (2 * 4) > 64)  # m=4 box does not inject into the 6-bit caller

    distance = hamming((1, 0), matvec(B, (1, 0)), 4)
    check(matvec(B, (1, 0)) == (5, 2))
    check(distance == 2)

    # Largest modulus with B^2 = I is 4. Cycle type: 4 fixed points, 6 swaps.
    seen = set()
    fixed = transpositions = other = 0
    for x in range(4):
        for y in range(4):
            if (x, y) in seen:
                continue
            cycle = [(x, y)]
            nxt = apply_b_mod((x, y), 4)
            while nxt not in cycle:
                cycle.append(nxt)
                nxt = apply_b_mod(nxt, 4)
            seen.update(cycle)
            if len(cycle) == 1:
                fixed += 1
            elif len(cycle) == 2:
                transpositions += 1
            else:
                other += 1
    check((fixed, transpositions, other, len(seen)) == (4, 6, 0, 16))

    def target_bits(x, y):
        image = apply_b_mod((x, y), 4)
        return bits_of_pair(*image)

    check(wiring_realizes(target_bits) is None)

    def carrier_bits(x, y):
        # Identity placement of the low three bits, with the carrier XOR as the target.
        a, b, c, _p = bits_of_pair(x, y)
        b ^= c
        return (a, b, c, 0)

    check(wiring_realizes(carrier_bits) is not None)

    # Direct Boolean circuit for the mod-4 map. It does not use the carrier.
    # out = (x0, x1 XOR y0, y0, x0 XOR y1), and the zero constant term was checked.
    for x in range(4):
        for y in range(4):
            x0, x1, y0, y1 = bits_of_pair(x, y)
            got = pair_of_bits((x0, x1 ^ y0, y0, x0 ^ y1))
            check(got == apply_b_mod((x, y), 4), (x, y, got))

    # Exact m-bit integer caller: four additions, fixed full-adder widths.
    for width in range(1, 6):
        box = 1 << width
        for x in range(box):
            for y in range(box):
                got = four_shears(x, y, width)
                check(got == matvec(B, (x, y)), (width, x, y, got))
    corner = (1 << 8) - 1
    check(four_shears(corner, corner, 8) == matvec(B, (corner, corner)))

    def bill(width):
        bit_slots = (width + 1) + (width + 2) + (width + 2) + (width + 3)
        return {
            "xor": 2 * bit_slots,
            "and": 2 * bit_slots,
            "or": bit_slots,
            "copy_xor_if_source_restored": 2 * width,
            "stored_source_bits": 2 * width,
        }

    sample = bill(4)
    check(sample == {
        "xor": 48,
        "and": 48,
        "or": 24,
        "copy_xor_if_source_restored": 8,
        "stored_source_bits": 8,
    })
    # Dropping any one shear misses the witness.
    a, b = 1, 0
    b, _ = fixed_add(b, a, 8)
    b, _ = fixed_add(b, a, 8)
    a, _ = fixed_add(a, b, 8)
    check((a, b) != (5, 2))

    print(
        "PASS_SL2Z_PAYLOAD_ENCODER_STOP "
        "B=[[5,2],[2,1]] carrier_xor=b^=c order2=true "
        "integer_invariant_payload={0} hamming_1_0_to_5_2=2 "
        "mod4_cycle=4fixed+6swap wiring_hits=0 mod4_direct_xor=2 "
        "adder_xor=8m+16 adder_and=8m+16 adder_or=4m+8 "
        "no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
