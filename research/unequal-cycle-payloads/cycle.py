"""Exact all-field query dimension for a C5 with unequal payload sizes.

Compressed construction uses five edge channels and five private channels.
Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dimensions(values):
    need(isinstance(values, (tuple, list)) and len(values) == 5,
         'five payload dimensions')
    need(all(type(x) is int and x >= 0 for x in values),
         'nonnegative integer payload dimensions')
    return tuple(values)


def minimum(values):
    d = dimensions(values)
    return max(max(d[i]+d[(i+2)%5] for i in range(5)), (sum(d)+1)//2)


def construct(values):
    """Return a constant-size exact recipe; never expand by payload dimension."""
    d = dimensions(values)
    total = sum(d)
    alpha, vertex = max((d[i]+d[(i+2)%5], i) for i in range(5))
    rank = max(alpha, (total+1)//2)
    edge, private = [0]*5, [0]*5
    if alpha >= (total+1)//2:
        # Saturate the complement of a maximum-weight independent pair.
        i = vertex
        edge[(i+2)%5] = d[(i+3)%5]
        edge[(i+4)%5] = d[(i+4)%5]
        edge[i] = min(d[i]-edge[(i+4)%5], d[(i+1)%5])
        edge[(i+1)%5] = d[(i+1)%5]-edge[i]
        private = [d[j]-edge[(j-1)%5]-edge[j] for j in range(5)]
        branch = 'dominant_pair'
    else:
        residual = list(d)
        if total % 2:
            i = next(i for i in range(5) if residual[i])
            residual[i] -= 1
            private[i] = 1
        half = sum(residual)//2
        edge = [half-residual[(i+2)%5]-residual[(i+4)%5] for i in range(5)]
        branch = 'balanced_odd' if total%2 else 'balanced_even'
    result = dict(dimensions=list(d), edge=edge, private=private, rank=rank, branch=branch)
    validate(result)
    return result


def validate(recipe):
    d = dimensions(recipe['dimensions'])
    edge, private = recipe['edge'], recipe['private']
    need(type(edge) is list and type(private) is list and len(edge) == len(private) == 5,
         'five edge and private channel counts')
    need(all(type(x) is int and x >= 0 for x in edge+private),
         'nonnegative integer channel counts')
    need(all(d[i] == edge[(i-1)%5]+edge[i]+private[i] for i in range(5)),
         'complete local coordinate coverage')
    need(type(recipe['rank']) is int and recipe['rank'] == sum(edge)+sum(private) == minimum(d),
         'sharp complete query dimension')


def channels(recipe):
    """Expand a small fixture into disjoint coordinate groups, for checking only."""
    validate(recipe)
    d, edge, private = recipe['dimensions'], recipe['edge'], recipe['private']
    offsets = [sum(d[:i]) for i in range(5)]
    used = [0]*5
    groups = []
    for i, count in enumerate(edge):
        j = (i+1)%5
        for _ in range(count):
            groups.append([offsets[i]+used[i], offsets[j]+used[j]])
            used[i] += 1; used[j] += 1
    for i, count in enumerate(private):
        for _ in range(count):
            groups.append([offsets[i]+used[i]])
            used[i] += 1
    need(used == d, 'expanded exact coordinate coverage')
    return groups


def matrix(recipe):
    n = sum(recipe['dimensions'])
    result = [[0]*n for _ in range(n)]
    for group in channels(recipe):
        for i in group:
            for j in group:
                result[i][j] = 1
    return result


def fits(matrix_value, values):
    d = dimensions(values)
    n = sum(d)
    need(len(matrix_value) == n and all(len(row) == n for row in matrix_value), 'rectangular block shape')
    offsets = [sum(d[:i]) for i in range(5)]
    for i in range(5):
        for j in range(5):
            if i == j or (i-j)%5 not in (1,4):
                for a in range(d[i]):
                    for b in range(d[j]):
                        need(matrix_value[offsets[i]+a][offsets[j]+b] == int(i == j and a == b),
                             'ordered complete block mask')
