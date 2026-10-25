"""Actual selected q=3 identity-low source specialization, not payload execution."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from unittest.mock import patch
import fused_sources
from fused_adapter import fuse


def run():
    _source, retained, data = fused_sources.activate()
    from catalogue import Catalogue
    from compile_routes import selected_registry, matrix_key, inverse_word
    from routes import Route
    from words import need
    names = (retained.GEOMETRY, retained.TEMPLATE, retained.GLOBAL, retained.WORD,
             retained.EXPECTED, retained.ASSEMBLY)
    routes, receipt = retained.compile_catalog({name: data[name] for name in names})
    catalogue = Catalogue(3)
    chart_matrix = type(catalogue).chart_matrix.__wrapped__
    with patch.object(catalogue, 'chart_matrix', lambda chart: chart_matrix(catalogue, chart)):
        registry, binding = selected_registry(catalogue)
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    rows, digest = {}, sha256()
    for chart in sorted(registry.words, key=repr):
        target = tuple(tuple(v.numerator*pow(v.denominator, -1, 3) % 3 for v in row) for row in chart)
        route = Route(3, 64, identity, target, chart)
        old = registry.compile(route)
        new = fuse(old)
        need(fuse(new) == new, 'fusion idempotent')
        before = Counter(op[0] for op in old)
        after = Counter(op[0] for op in new)
        need(all(before[k] == after[k] for k in ('swap', 'add', 'negate')), 'same untouched factors')
        fragments = Counter(str((op[2], op[3], op[4])) for op in new if op[0] == 'affine')
        rows[chart] = (before, after, fragments)
        digest.update(json.dumps((old, new), separators=(',', ':')).encode())
        registry.compiled.clear()
    before, after, fragments = Counter(), Counter(), Counter()
    for key, row in sorted(routes.items()):
        word = tuple((k, t, c, F(v)) for k, t, c, v in row['word'])
        for oriented in (word, inverse_word(word)):
            old, new, pattern = rows[matrix_key(retained.replay(oriented, 64))]
            for output, inputs in ((before, old), (after, new), (fragments, pattern)):
                for name, count in inputs.items():
                    output[name] += count*row['occurrences']
    need(sum(before.values()) > sum(after.values()), 'nonzero actual selected fusion exposure')
    return dict(q=3, low='identity', chart_types=len(routes), registry_matrices=len(registry.words),
                orientations=2*len(routes), weighted_before=dict(sorted(before.items())),
                weighted_after=dict(sorted(after.items())), weighted_fragments=dict(sorted(fragments.items())),
                saved_high_kernel_invocations=sum(before.values())-sum(after.values()),
                operations_sha256=digest.hexdigest(), source_catalogue_sha256=receipt['catalogue_sha256'],
                bound_source_types=binding['source_types'])
