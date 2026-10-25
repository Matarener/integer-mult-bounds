"""Independent request projection and uniform chart checks for the T35 pool.

Request construction reuses the selected native frame arithmetic. The separate
geometry inventories and sparse chart certificate check its changed binding.
This is finite native/interface verification, not a full GL64 payload replay.
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import time

import adapter

HERE = Path(__file__).resolve().parent


def run(pool, word=None, word_content_sha256=None):
    started = time.monotonic()
    kwargs = {'template_path':pool/'GLOBAL-TEMPLATE.json.gz'}
    if word is not None:
        kwargs.update(word_path=word,word_content_sha256=word_content_sha256)
    catalogue, topology = adapter.load(**kwargs)
    target = adapter.read(pool / 'RESULT.json')
    need = adapter.need
    need(catalogue.profile == Counter({int(k):v for k,v in target['profile'].items()}),
         'native catalogue agrees with the independent slot/IR invoice')
    geometry_idles = adapter.read(pool / 'IDLE-INVENTORY.json.gz')
    print('Native catalogue built; checking independent idle records and all chart labels.', flush=True)
    # The geometry builder's record schema is kept explicit in the receipt.
    idle_projection = []
    native_ids = set()
    for child in catalogue.idles:
        for replica in range(catalogue.replicas):
            for identifier in topology.idles_for(child, replica):
                need(identifier not in native_ids, 'one native identifier per absolute idle')
                native_ids.add(identifier)
                req = catalogue.requests[identifier]
                need(topology.idle_family(identifier, replica) == req.family,
                     'native idle targets its absolute family')
                capacity = catalogue.idles[child]['rank']
                idle_projection.append([child, replica, req.role, req.family,
                                        capacity-req.base.rank, req.base.rank])
    geometry_rows = geometry_idles['rows'] if isinstance(geometry_idles, dict) else geometry_idles
    need(sorted(idle_projection) == sorted(geometry_rows), 'all independently derived absolute idle records')
    local_count = 0
    for stage in range(9):
        for replica in range(catalogue.replicas):
            call = topology.call(stage, replica)
            for position, event in enumerate(call.events):
                if event[0] not in (0,2):
                    need(call.requests[position] is None, 'unpaid event has no residual identifier')
                    continue
                identifier = call.requests[position]
                request = catalogue.requests[identifier]
                need((request.stage, request.replica, request.position, request.role) ==
                     (stage, replica, position, event[1]), 'complete local semantic identity')
                need(request.base.rank == (event[4] if event[0] == 0 else event[5]),
                     'local IR paid rank equals native request rank')
                if event[0] == 0:
                    need(request.family == call.owners[event[1]].family and
                         request.chart == call.owners[event[1]].chart,
                         'MOVE uses the actual pooled native owner')
                else:
                    need(request.source_chart == call.owners[event[1]].chart,
                         'COPY binds its actual source chart')
                local_count += 1
    need(local_count + len(native_ids) == len(catalogue.requests), 'complete local and idle partition')
    transport = adapter.module('pool35_independent_sparse_charts', adapter.SCOPE /
        'sources/PR3980/research/r437-native-transport/check_transport.py')
    matrices, determinants, chart_rows = {}, Counter(), []
    charts = sorted(catalogue.charts, key=lambda x: adapter.canonical(x.key))
    for chart in charts:
        matrix = transport.reconstructed_chart(chart, catalogue.geometry)
        need(matrix == catalogue.chart_matrix(chart), 'independent sparse native chart reconstruction')
        need(all(transport.dyadic(x) for row in matrix for x in row), 'dyadic native chart')
        det = transport.determinant(matrix)
        need(transport.dyadic_unit(det), 'native chart invertible at every odd modulus')
        matrices[chart] = matrix
        determinants[str(det)] += 1
        chart_rows.append([chart.key, str(det)])
    old_transport = adapter.read(adapter.SCOPE / 'sources/PR3980/research/r437-native-transport/RESULT.json')
    chart_digest = hashlib.sha256(adapter.canonical(chart_rows).encode()).hexdigest()
    need(chart_digest == old_transport['chart_certificate_sha256'], 'unchanged complete1235-chart alphabet')
    witnesses, pair_cache, pair_counts = hashlib.sha256(), {}, Counter()
    for stage in range(9):
        for replica in range(catalogue.replicas):
            groups = defaultdict(list)
            for role, owner in enumerate(topology.call(stage, replica).owners):
                groups[owner.family].append((role, owner.chart))
            for family, roles in sorted(groups.items()):
                for i, (a, ca) in enumerate(roles):
                    for b, cb in roles[:i]:
                        key = (ca,cb)
                        if key not in pair_cache:
                            pair_cache[key] = transport.distinguishing_entry(matrices[ca], matrices[cb])
                        entry = pair_cache[key]
                        pair_counts[stage] += 1
                        witnesses.update((adapter.canonical([stage,replica,family,a,b,ca.key,cb.key,*entry])+'\n').encode())
    rejected = []
    def reject(label, action):
        try:
            action()
        except (ValueError, KeyError, TypeError):
            rejected.append(label)
        else:
            raise ValueError('accepted semantic control: '+label)
    idle_id = next(iter(native_ids))
    owner_replica = catalogue.requests[idle_id].replica
    reject('wrong_idle_caller_replica', lambda: topology.idle_family(idle_id, (owner_replica+1)%35))
    move = next(r for r in catalogue.requests if r.kind == 'MOVE')
    reject('wrong_local_kind', lambda: catalogue.identifier('COPY',move.stage,move.position,move.replica))
    # Removing caller replica must collapse distinct requests; the new key must not.
    r0 = catalogue.requests[catalogue.identifier('MOVE',move.stage,move.position,0)]
    r1 = catalogue.requests[catalogue.identifier('MOVE',move.stage,move.position,1)]
    need(catalogue.semantic_key(r0) != catalogue.semantic_key(r1), 'replica omitted from key is observable')
    reject('omitted_replica_key', lambda: need((r0.kind,r0.stage,r0.position) !=
                                             (r1.kind,r1.stage,r1.position), 'old key aliases actual requests'))
    reject('old_replica_multiplier', lambda: need(sum(catalogue.profile.values())*35 ==
                                                 target['paid_requests'], 'old count multiplier overcharges'))
    reject('omitted_replica_recipe', lambda: topology.recipe(0))
    rejected.extend(transport.finite_controls())
    receipt = catalogue.receipt()
    receipt.update({'all_call_records_checked':9*35, 'all_local_requests_checked':local_count,
                    'absolute_idle_records_checked':len(native_ids),
                    'chart_certificate_sha256':chart_digest, 'chart_determinants':dict(determinants),
                    'same_family_owner_pairs':sum(pair_counts.values()),
                    'per_stage_owner_pairs':dict(pair_counts), 'distinct_chart_pair_witnesses':len(pair_cache),
                    'owner_witness_sha256':witnesses.hexdigest(), 'controls_rejected':rejected,
                    'template_content_sha256':target['template_content_sha256'],
                    'all_odd_moduli_owner_separation':True,
                    'full_GL64_payload_executed':False, 'supplier_admission':False,
                    'scope':'Finite complete replica-indexed native requests and uniform dyadic owner separation; inherited physical primitive and all-size contracts remain conditional.'})
    paths = [Path(__file__),HERE/'adapter.py',pool/'GLOBAL-TEMPLATE.json.gz',pool/'RESULT.json',
             pool/'IDLE-INVENTORY.json.gz',adapter.SCOPE/'sources/PR3980/research/r437-native-transport/check_transport.py']
    if word is not None:
        paths.append(word)
    receipt['source_sha256'] = {p.resolve().relative_to(adapter.ROOT).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    print('Native request/chart review finished in %.2f seconds.' % (time.monotonic()-started), flush=True)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pool',type=Path,default=adapter.POOL)
    parser.add_argument('--word',type=Path)
    parser.add_argument('--word-content-sha256')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    adapter.need(__debug__, 'assertions must remain enabled')
    result = run(args.pool.resolve(),args.word.resolve() if args.word else None,args.word_content_sha256)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        adapter.need(result == adapter.read(HERE/'REVIEW.json'), 'exact retained native review receipt')
    print(json.dumps({k:result[k] for k in ('status','canonical_requests','same_family_owner_pairs','binding_sha256')}))
