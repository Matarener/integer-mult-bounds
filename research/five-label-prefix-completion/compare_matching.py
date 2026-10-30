"""PR5001 comparison, transcribed from its stated matching-capacity theorem.
Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.
Ali Romman retains the theorem and original implementation credit.
"""


def splits(points, omitted):
    # This comparison is deliberately fixed to n=5, L=12.
    n, length = 5, 12
    mask = 31 ^ (1 << omitted)
    side = lambda x: (x & mask).bit_count() % 2
    remaining = length - len(points)
    sizes = [sum(side(x) == j for x in points) for j in (0, 1)]
    if remaining == 0:
        return {tuple(sizes)} if (points[0] ^ points[-1]).bit_count() == 1 else set()
    used = set(points)
    ends = {points[0], points[-1]}
    stay = [0, 0]
    for left, right in zip(points, points[1:]):
        if side(left) == side(right):
            stay[side(left)] += 1
    crossing = len(points) - 1 - sum(stay)
    pools = [{x for x in range(32) if x not in used and side(x) == j} for j in (0, 1)]
    one = [sum(x ^ (1 << omitted) in ends for x in pool) for pool in pools]
    two = [sum(x ^ (1 << omitted) in pool for x in pool) // 2 for pool in pools]
    answer = set()
    for added0 in range(remaining + 1):
        added = (added0, remaining - added0)
        if any(added[j] > len(pools[j]) for j in (0, 1)):
            continue
        totals = tuple(sizes[j] + added[j] for j in (0, 1))
        max_new_stay = [max(i + min(two[j], (added[j] - i) // 2)
                            for i in range(min(one[j], added[j]) + 1)) for j in (0, 1)]
        for final_crossing in range(0, length + 1, 2):
            if not crossing <= final_crossing <= crossing + remaining + 1:
                continue
            if min(totals) and final_crossing < 2:
                continue
            required_stay = [totals[j] - final_crossing // 2 for j in (0, 1)]
            if all(stay[j] <= required_stay[j] <= stay[j] + max_new_stay[j] for j in (0, 1)):
                answer.add(totals)
                break
    return answer

