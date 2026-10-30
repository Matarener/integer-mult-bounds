"""Semantic failure controls; assertions are never used for acceptance."""
from copy import deepcopy
from hashlib import sha256
import json

import check


def rejects(fn, text):
    try:fn()
    except ValueError as error:
        check.need(text in str(error),'unexpected failure: '+str(error))
        return
    raise ValueError('negative control accepted: '+text)


def run():
    labels,old,meta=check.inputs()
    cert=json.loads((check.HERE/'CERTIFICATE.json').read_text())
    base=check.evaluate(labels,cert)
    bad=deepcopy(cert);bad['orthonormal_groups'][0][0]=bad['orthonormal_groups'][1][0]
    rejects(lambda:check.evaluate(labels,bad),'exact port partition')
    bad=deepcopy(cert);bad['orthonormal_groups'][0]=bad['orthonormal_groups'][0][:-1]
    rejects(lambda:check.evaluate(labels,bad),'even groups')
    # Preserve partition and group lengths while making one Gram entry illegal.
    bad=deepcopy(cert)
    bad['orthonormal_groups'][0][0],bad['orthonormal_groups'][1][0]=bad['orthonormal_groups'][1][0],bad['orthonormal_groups'][0][0]
    rejects(lambda:check.evaluate(labels,bad),'Gram identity')
    bad=deepcopy(cert);bad['clique_planes'][1]=bad['clique_planes'][0]
    rejects(lambda:check.evaluate(labels,bad),'sixteen clique planes')
    # Adjacent planes within the first eight-frame cannot belong to this clique.
    bad=deepcopy(cert);bad['clique_planes']=list(range(16))
    rejects(lambda:check.evaluate(labels,bad),'forced identity minor')
    wrong=[rank for rank in base['tariffs']]
    check.need(sum(wrong)==224,'full-plane tariff')
    singleton=[]
    for support in base['supports']:
        rows=[sum(((labels[i]&labels[j]).bit_count()%2)<<k for k,j in enumerate(support)) for i in support]
        singleton.append(check.rank2(rows))
    check.need(sum(singleton)==112<sum(wrong),'single-label tariff omits the other plane port')
    row=meta['files'][0]
    rejects(lambda:check.authenticate((check.ROOT/check.INPUT).read_bytes()+b'\n',row),'source SHA256')
    row=meta['retained_predecessor']
    rejects(lambda:check.authenticate((check.HERE/'PREDECESSOR.json').read_bytes()+b'\n',row),'source SHA256')
    return dict(partition_controls=2,gram_control=1,clique_controls=2,
                source_controls=2,underpriced_single_label_counterexample=112,
                complete_plane_tariff=224)
