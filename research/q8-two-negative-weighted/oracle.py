"""Faithful dirty-column action from an independent signed-axis Q8 rule."""

from tariff import require


def multiply(a, b):
    require(0 <= a < 8 and 0 <= b < 8, "group element")
    left, right = a // 2, b // 2
    sign = (a ^ b) & 1
    if left == 0:
        return 2 * right + sign
    if right == 0:
        return 2 * left + sign
    if left == right:
        return sign ^ 1
    axis = 6 - left - right
    positive = (left, right) in ((1, 2), (2, 3), (3, 1))
    return 2 * axis + (sign ^ int(not positive))


def columns(word, target):
    roles = len(target)
    require(2 <= roles <= 12 and len(word) <= 9, "oracle capacity")
    output = []
    for source in range(8 * roles):
        state = 1 << source
        for u, v, g in reversed(word):
            require(
                0 < u < 1 << roles and 0 < v < 1 << roles,
                "oracle vector",
            )
            require(g in (2, 4) and (u & v).bit_count() % 2 == 1, "oracle call")
            read = 0
            for role in range(roles):
                if v >> role & 1:
                    read ^= (state >> (8 * role)) & 255
            change = read
            for h in range(8):
                if read >> h & 1:
                    change ^= 1 << multiply(g, h)
            for role in range(roles):
                if u >> role & 1:
                    state ^= change << (8 * role)
        output.append(state)
    return tuple(output)


def expected(target):
    return tuple(
        1 << (8 * role + multiply(g, h))
        for role, g in enumerate(target)
        for h in range(8)
    )
