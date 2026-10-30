"""Signed native checker adapted from ywz65 PR2707 to the new224-event inventory.
The signed kernel construction and source conventions remain credited to that
work and Arham Tahir's retained native lineage. Chris R / OpenAI, Apache-2.0.
"""
def need(ok,why):
 if not ok:raise ValueError(why)

def kernel_checks(P, labels, word, wrong_negative_offset=False):
    recipes = []
    columns = 0
    for port, q in enumerate(labels):
        pivot = (q & -q).bit_length() - 1
        basis = (q,) + tuple(1 << i for i in range(9) if i != pivot)
        inverse = {P.act(basis, x): x for x in range(512)}
        need(len(inverse) == 512, 'line basis bijective')
        for sign in (1, -1):
            offset = q if sign == -1 else 0
            if wrong_negative_offset and sign == -1:
                offset = 0
            for x in range(512):
                middle = inverse[x]
                actual = {P.act(basis, middle) ^ offset: (1, 1),
                          P.act(basis, middle ^ 1) ^ offset: (1, -1)}
                expected = {x: (1, sign), x ^ q: (1, -sign)}
                need(actual == expected, 'signed line native kernel/global phase')
                columns += 1
            occurrences = [i for i, e in enumerate(word)
                           if e[0] == 'line' and e[2:] == [port, sign]]
            need(len(occurrences) == ((2 if port in P.A else 1) if sign == 1 else (0 if port in P.A else 1)), 'all line occurrences')
            recipes.append({'port': port, 'q': q, 'sign': sign, 'rank': 1,
                            'left_columns': list(basis), 'left_offset': offset,
                            'right_columns': [inverse[1 << j] for j in range(9)],
                            'events': occurrences})
    need(sum(len(r['events']) for r in recipes) == 224, 'complete native child coverage')
    return {'signed_rank_one_recipes': recipes, 'basis_columns': columns,
            'positive_children': 224, 'monomial_wrappers': 448,
            'spectator_action': 'identity outside first nine address coordinates'}
