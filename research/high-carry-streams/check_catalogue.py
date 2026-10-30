"""Carry exposure in the actual selected registry at identity low class, q=3.

This is a finite source specialization, not a selected GL64 payload execution
or a distribution over every low class. Occurrence weights are source weights.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from unittest.mock import patch

import bindings


def run():
    _source,retained,data=bindings.activate()
    from catalogue import Catalogue
    from compile_routes import selected_registry,matrix_key,inverse_word
    from routes import Route
    from words import need
    names=(retained.GEOMETRY,retained.TEMPLATE,retained.GLOBAL,retained.WORD,retained.EXPECTED,retained.ASSEMBLY)
    routes,source_receipt=retained.compile_catalog({name:data[name] for name in names})
    catalogue=Catalogue(3)
    matrix=type(catalogue).chart_matrix.__wrapped__
    with patch.object(catalogue,'chart_matrix',lambda chart:matrix(catalogue,chart)):
        registry,binding_receipt=selected_registry(catalogue)
    identity=tuple(tuple(int(i==j) for j in range(64)) for i in range(64))
    histograms={}
    digest=sha256()
    for chart in sorted(registry.words,key=repr):
        target=tuple(tuple(v.numerator*pow(v.denominator,-1,3)%3 for v in row) for row in chart)
        route=Route(3,64,identity,target,chart)
        operations=registry.compile(route)
        carries=Counter(op[2] for op in operations if op[0]=='translate')
        need(all(type(a) is int and 0<abs(a)<=4 for a in carries),'entire compiled carry domain')
        histograms[chart]=carries
        digest.update(json.dumps(operations,separators=(',',':')).encode())
        registry.compiled.clear()
    total=Counter()
    for key,row in sorted(routes.items()):
        word=tuple((k,t,c,F(v)) for k,t,c,v in row['word'])
        for oriented in (word,inverse_word(word)):
            matrix=matrix_key(retained.replay(oriented,64))
            for carry,count in histograms[matrix].items():total[carry]+=count*row['occurrences']
    before=sum(count*(a if a>0 else -3*a) for a,count in total.items())
    after=sum(total.values())
    need(before>after,'nontrivial selected carry exposure')
    return dict(q=3,low='identity',chart_types=len(routes),registry_matrices=len(registry.words),
                orientations=2*len(routes),weighted_carries={str(k):v for k,v in sorted(total.items())},
                weighted_old_full_field_primitive_calls=before,weighted_new_kernel_calls=after,
                saved_primitive_calls=before-after,operations_sha256=digest.hexdigest(),
                source_catalogue_sha256=source_receipt['catalogue_sha256'],
                bound_source_types=binding_receipt['source_types'])
