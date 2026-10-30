#!/usr/bin/env python3
"""Audit the actual T360 owners for a specified dirty-record contract.

Apache-2.0. Substantial OpenAI Codex assistance. The window, width and physical
family predicates are adapted from the credited PR3734 owner_audit.py. This
script identifies exact existing trajectories; it does not forbid a changed
allocation, record moves, or a consumer that tracks subsequent data mixing.
"""
from bisect import bisect_right
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

from check_controller import load_module, need

HERE = Path(__file__).resolve().parent
HOSTS = (224,225,227,229,240,241,256,257)


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def rank(rows):
    piv = {}
    for x in rows:
        while x:
            bit = x.bit_length()
            if bit in piv:x ^= piv[bit]
            else:piv[bit] = x;break
    return len(piv)


def run(source, out):
    # Authenticate the complete literal premise with its retained independent
    # implementation before selecting particular record trajectories.
    retained = load_module(source/'owner_audit.py')
    parent_audit = retained.audit()
    need(parent_audit['roles'] == 1321920 and parent_audit['replicas'] == 360, 'actual T360 audit')
    inp = source/'inputs'
    order, dispatch = read(inp/'ORDER.json'), read(inp/'DISPATCH.json')
    fill, plan, template = [read(inp/file) for file in ('FILL.json.gz','PLAN.json.gz','TEMPLATE.json.gz')]
    clock = {tuple(call):i for i,call in enumerate(order)}
    providers = {(s,r):p for s,r,p in dispatch}
    children = {c['child']:c['rank'] for c in template['idle_children']}
    families = {c:2*plan['pairs'][str(c)]+plan['sides'][str(c)] for c in children}
    windows = {}
    for owner in range(360):
        touched, time = {}, None
        for event in template['execution_schedule']:
            kind = event['kind']
            if kind == 'local_cover_sweep':
                time = clock[event['stage'],owner]
                pair = next(e['pair']for e in template['recipe'] if e['kind']=='local' and e['stage']==event['stage'])
                touched[pair] = time
            elif kind == 'bridge':
                touched[event['src']] = touched[event['dst']] = time
            elif kind == 'idle_cover_sweep':
                for child in event['child_indices']:
                    if child in children:windows[owner,child] = (touched.get(event['pair'],-1),time)
    widths, eligible = {}, {}
    for tag,pid in [('base','gauge44'),('extra','extra')]:
        word = read(inp/f'NATIVE-{tag}.json.gz')
        widths[pid] = [rank(word['frames'][word['final'][h]])-rank(word['frames'][word['start'][h]]) for h in range(224,632)]
        eligible[pid] = {h-224 for h in range(224,632) if word['start'][h]==0 and word['final'][h]==1}
        need(len(eligible[pid]) == 213, 'I-to-FULL eligibility')
        need(sum(widths[pid]) == 3278, 'helper width invoice')
        need(all(h-224 in eligible[pid]for h in HOSTS), 'specified helper host frame')
    need(eligible['gauge44'] == eligible['extra'], 'provider role eligibility differs')
    calls = [set() for _ in order]
    candidates = [0 for _ in order]
    fixed_candidates = [0 for _ in order]
    selected, usage = [], defaultdict(list)
    host_ids = {h-224 for h in HOSTS}
    for time,h,owner,child,port,offset in fill['rows']:
        stage,replica = order[time]
        family = owner*896 + families[child]*112 + port
        lo,hi = windows[owner,child]
        usage[family].append((time,h,child,offset))
        if h in eligible[providers[stage,replica]]:
            calls[time].add(family)
            if hi >= clock[8,replica]:
                candidates[time] += 1
                if h in host_ids:fixed_candidates[time] += 1
        if h in host_ids:
            selected.append(dict(time=time,stage=stage,replica=replica,helper_role=h+224,
                physical_family=family,owner_replica=owner,child=child,port=port,
                offset=offset,paid_width=9,child_capacity=children[child],
                idle_window_open_after=lo,idle_window_closes_at=hi,
                capturing_replica_final_time=clock[8,replica],
                native_rank_remaining_in_bin=children[child]-offset-9,
                window_reaches_replica_final_call=hi>=clock[8,replica]))
    intersections = Counter()
    for replica in range(360):
        common = set.intersection(*(calls[clock[stage,replica]] for stage in range(9)))
        intersections[len(common)] += 1
    need(intersections == {0:360}, 'unexpected common nine-stage physical owner')
    reused_after = Counter()
    for record in selected:
        later = [r for r in usage[record['physical_family']] if r[0] > record['time']]
        record['later_helper_use_count'] = len(later)
        record['next_helper_use'] = (dict(time=later[0][0],helper_role=later[0][1]+224,
            child=later[0][2],offset=later[0][3]) if later else None)
        reused_after[len(later)] += 1
    census = []
    for stage in range(9):
        free = [candidates[clock[stage,r]] for r in range(360)]
        fixed = [fixed_candidates[clock[stage,r]] for r in range(360)]
        census.append(dict(stage=stage, any_8_eligible_hosts_reaching_final=sum(n>=8 for n in free),
            all_8_specified_hosts_reaching_final=sum(n==8 for n in fixed),
            eligible_host_count_min=min(free),eligible_host_count_max=max(free)))
    need([x['any_8_eligible_hosts_reaching_final'] for x in census] == [7,2,8,18,40,84,188,250,360], 'optimistic lifetime census')
    need([x['all_8_specified_hosts_reaching_final'] for x in census] == [7,0,8,18,29,66,178,234,360], 'specified lifetime census')
    result = dict(status='PASS_ACTUAL_T360_RETENTION_OWNER_SCREEN', source_audit=parent_audit,
        source_sha256={str(p.relative_to(source)):sha256(p.read_bytes()).hexdigest() for p in
            [source/'owner_audit.py']+[inp/f for f in ('ORDER.json','DISPATCH.json','FILL.json.gz','PLAN.json.gz','TEMPLATE.json.gz','NATIVE-base.json.gz','NATIVE-extra.json.gz')]},
        helper_roles=list(HOSTS), eligible_helpers_each_provider=213, helper_width_sum=3278,
        selected_literal_records=len(selected), nine_stage_owner_intersection=dict(intersections),
        later_helper_use_count_histogram=dict(reused_after), stage_lifetime_census=census,
        scope='The existing FILL does not supply an unchanged same-eight-family nine-stage record bank. Different hosts per stage remain possible with priced transport and restoration; later ordinary data contacts are not assumed absent.',
        census_optimism='A host is counted through its current idle-window close even if subsequent helper invocations change its native frame or capture more records. Thus these are necessary existing-window conditions for untouched retention, not a full feasibility certificate.',
        chronological_boundary='An idle window closes at the owner event immediately preceding its next ordinary data/bridge use. A consumer carrying records beyond it must track that data mixing explicitly.',
        metadata='ORDER, DISPATCH and FILL define T360. Ancestral T37 descriptive fields in TEMPLATE and PLAN are not interpreted as the current clock.')
    out.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(selected,sort_keys=True,separators=(',',':')).encode()
    (out/'RETAINED-OWNER-TRAJECTORIES.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    result['trajectory_payload_sha256'] = sha256(raw).hexdigest()
    (out/'OWNER-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=HERE.parents[3]/'live-source/research/staged544-producer-return')
    ap.add_argument('--out',type=Path,default=HERE/'evidence')
    args = ap.parse_args()
    result = run(args.source,args.out)
    print(result['status']+': 1321920 parent roles, 25920 selected trajectories; no unchanged nine-stage retained bank admitted.',flush=True)
