"""Independent P104 caller interface census for compact or retired public IDs.

No native or endpoint equations are relaxed. This module supplies the public
allocation, lifetime schedule and ordinary recount missing from the legacy
index-boundary adapter. All ordinary scalar coefficients are counted literally.
Prepared for flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q

def need(ok, message):
    if not ok:
        raise ValueError(message)

def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid interface control accepted')

def span(basis):
    values = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in values, 'Independent binary chart')
        values |= {x ^ v for x in tuple(values)}
    return values

def check_schedule(lifetimes, owned, independent, fields):
    boundaries = []
    for life in lifetimes:
        need(life['role'] in owned and life['role'] not in independent,
             'Owned schedule has no productive alias')
        need(0 <= life['start'] < life['end'] and type(life['slot']) is int and life['slot'] >= 0,
             'Owned lifetime interval')
        boundaries.extend([(life['start'], 1, life), (life['end'], 0, life)])
    active_roles, active_slots = {}, {}
    for _, begin, life in sorted(boundaries, key=lambda x:(x[0], x[1])):
        r, s = life['role'], life['slot']
        if begin:
            need(r not in active_roles and s not in active_slots, 'Overlapping owned lifetime alias')
            active_roles[r] = s
            active_slots[s] = r
        else:
            need(active_roles.get(r) == s and active_slots.get(s) == r, 'Matching owned lifetime exit')
            del active_roles[r], active_slots[s]
        need(all(fields + s >= fields for s in active_slots), 'Scratch outside productive allocation')
    need(not active_roles and not active_slots, 'Owned schedule fully closed')

def audit(word, source, *, _controls=True):
    public = word['public']
    need(len(word['initial']) == len(word['final']) == public, 'Legacy boundary inventory')
    independent = list(word.get('independent_public', range(public)))
    need(len(independent) == len(set(independent)) and all(type(r) is int and 0 <= r < public for r in independent),
         'Distinct independent public roles')
    retired = set(range(public)) - set(independent)
    if 'retired_public' in word:
        need(retired == set(word['retired_public']), 'Exact retired-public holes')
    owned_count = word.get('owned_fields', 8)
    fields = word.get('fields', public + owned_count)
    owned = list(word.get('owned_roles', range(public, fields)))
    need(len(owned) == len(set(owned)) and set(owned).isdisjoint(independent), 'Distinct owned roles')
    need(set(independent) | set(owned) == set(range(fields)), 'Every field is independent or owned')
    need(set(owned) & set(range(public)) == retired, 'All legacy public holes are owned')
    main = set(word['live']) | {r+112 for r in word['live']}
    need(len(word['live']) == len(word['ports']) == 104 and len(main) == 208 and main <= set(independent),
         'All104 main pairs are independent')
    helpers = [r for r in independent if r not in main]
    targets = Counter(len(word['frames'][word['final'][r]])-len(word['frames'][word['initial'][r]]) for r in helpers)
    need(targets and min(targets) > 0, 'Every independent helper has a positive target')
    charts = [span(f) for f in word['frames']]
    current = list(word['initial']) + [None]*(fields-public)
    for r in owned:
        current[r] = None
    active, lifetimes, scalar, paid, peak = {}, [], 0, Counter(), 0
    initialized = set()
    for index, event in enumerate(word['program']):
        op, r = event[:2]
        need(type(r) is int and 0 <= r < fields, 'Event destination inventory')
        if op == 'INIT':
            need(type(event[2]) is int and 0 <= event[2] < len(charts), 'Owned initial chart inventory')
            need(r in owned and r not in active and current[r] is None, 'Owned initialization chronology')
            slot = 0
            while slot in {life['slot'] for life in active.values()}:
                slot += 1
            life = dict(role=r, slot=slot, start=index, start_chart=event[2])
            active[r] = life
            current[r] = event[2]
            initialized.add(r)
            peak = max(peak, len(active))
            scalar += 2
        elif op == 'CLEAR':
            need(r in active and current[r] == event[2], 'Owned clear chronology and chart')
            life = active.pop(r)
            life.update(end=index, end_chart=event[2])
            lifetimes.append(life)
            current[r] = None
            initialized.discard(r)
            scalar += 2
        elif op == 'MOVE':
            _, _, a, b, private = event
            need(current[r] == a and type(private) is bool and private == (r in active), 'MOVE ownership')
            need(charts[b] < charts[a] if private else charts[a] < charts[b], 'Strict nested MOVE')
            current[r] = b
            paid[abs(len(word['frames'][a])-len(word['frames'][b]))] += 1
        else:
            q, f = Q(event[-2]), event[-1]
            need(current[r] == f and (r not in owned or r in active), 'Scalar destination is active and coframed')
            need(q and q.denominator & (q.denominator-1) == 0 and abs(q)+1 < 2**16, 'Literal dyadic coefficient bound')
            n, d = abs(q.numerator), q.denominator
            if op == 'SCALE':
                need(n & (n-1) == 0, 'SCALE is a dyadic unit')
                scalar += 2*(abs(n.bit_length()-d.bit_length())+int(q < 0))
            else:
                s = event[2]
                need(type(s) is int and 0 <= s < fields and s != r and current[s] == f,
                     'Scalar source is active and coframed')
                need(s not in owned or s in active, 'No inactive owned source')
                need(op in ('ADD','COPY'), 'Known scalar opcode')
                if op == 'COPY':
                    need(r in active and r in initialized, 'COPY follows an owned initialization')
                scalar += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
            initialized.discard(r)
    need(not active and all(current[r] == word['final'][r] for r in independent), 'All local public and owned exits')
    need(set(life['role'] for life in lifetimes) == set(owned), 'Every declared owned role has a lifetime')
    local = source['local']
    need(len(independent) == local['public_inputs'] and len(lifetimes) == local['owned_lifetimes'] and peak == local['peak_owned_fields'],
         'Independently recounted input and lifetime inventory')
    if 'owned_fields' in local:
        need(len(owned) == local['owned_fields'], 'Independently recounted owned fields')
    need(targets == Counter({int(k):v for k,v in local['helpers'].items()}) and
         paid == Counter({int(k):v for k,v in local['paid'].items()}), 'Independent paid and productive profiles')
    need(scalar == local['real_scalar_allowance'], 'Independent scalar allowance')
    productive_fields = 3328 + 18*len(helpers)
    check_schedule(lifetimes, set(owned), set(independent), productive_fields)
    routes = (sum(paid.values())+2*len(helpers)+208+4*104+4*len(lifetimes))*1000
    nr = source['complete_cost']['nonrecursive']
    need(nr['local_scalar'] == scalar and nr['local_routes'] == routes, 'Independent local ordinary allowance')
    need(nr['peak_owned_fields'] == peak, 'Ordinary ledger owned peak')
    controls = {}
    if _controls and peak > 1:
        bad = deepcopy(lifetimes)
        pair = next((a,b) for a in bad for b in bad if a is not b and a['start'] < b['start'] < a['end'])
        pair[1]['slot'] = pair[0]['slot']
        controls['overlapping_local_owned_alias'] = reject(lambda:check_schedule(bad,set(owned),set(independent),productive_fields))
    if _controls:
        bad_word = deepcopy(word)
        bad_word['independent_public'] = independent+[owned[0]]
        controls['owned_marked_productive'] = reject(lambda:audit(bad_word,source,_controls=False))
        bad_word = deepcopy(word)
        bad_word['independent_public'] = independent[:-1]
        controls['stale_independent_inventory'] = reject(lambda:audit(bad_word,source,_controls=False))
        bad_source = deepcopy(source)
        bad_source['local']['owned_lifetimes'] -= 1
        controls['stale_source_lifetime_inventory'] = reject(lambda:audit(word,bad_source,_controls=False))
        if len(lifetimes) > len(owned):
            role = next(r for r,n in Counter(life['role'] for life in lifetimes).items() if n>1)
            starts = [i for i,event in enumerate(word['program']) if event[:2] == ['INIT',role]]
            bad_word = deepcopy(word)
            later = bad_word['program'].pop(starts[1])
            bad_word['program'].insert(starts[0]+1,later)
            controls['reused_owned_label_before_clear'] = reject(lambda:audit(bad_word,source,_controls=False))
    return dict(public_slots=public,fields=fields,independent=independent,owned=owned,retired=sorted(retired),
                main=sorted(main),helpers=helpers,helper_count=len(helpers),productive_fields=productive_fields,
                paid=dict(paid),targets=dict(targets),scalar=scalar,routes=routes,lifetimes=lifetimes,
                lifetime_count=len(lifetimes),peak=peak,controls=controls)

def allocation(interface, full_calls, live):
    fields = []
    for site,event in enumerate(full_calls):
        mapping = {}
        for p,r in enumerate(live):
            mapping[r],mapping[r+112] = 2*event[2]*104+p,(2*event[2]+1)*104+p
        mapping.update({h:3328+site*interface['helper_count']+i for i,h in enumerate(interface['helpers'])})
        need(set(mapping) == set(interface['independent']) and len(mapping) == len(set(mapping.values())),
             'Injective full-call independent inventory')
        lives = [dict(x,global_field=interface['productive_fields']+x['slot']) for x in interface['lifetimes']]
        fields.append(dict(site=site,stage=event[1],local_to_global=[mapping.get(i) for i in range(interface['public_slots'])],
                           independent_mapping=mapping,owned_lifetimes=lives))
    return fields

def check_global_intervals(intervals, productive_fields):
    boundaries=[]
    for interval in intervals:
        need(interval['global_field'] >= productive_fields, 'Owned caller scratch outside productive fields')
        need(tuple(interval['start']) < tuple(interval['end']), 'Proper hierarchical owned interval')
        boundaries.extend([(tuple(interval['start']),1,interval),(tuple(interval['end']),0,interval)])
    active={}
    for _,begin,interval in sorted(boundaries,key=lambda item:(item[0],item[1])):
        field=interval['global_field']
        if begin:
            need(field not in active, 'Caller owned intervals cannot overlap on one field')
            active[field]=interval
        else:
            need(active.get(field) is interval, 'Caller owned interval closes its own field')
            del active[field]
    need(not active, 'No caller owned scratch remains live')

def caller_schedule(interface, controller, fields):
    # Addresses are (outer physical event, port subcall, local instruction).
    # A LOCAL's instructions are substituted at its own outer event; QUERY
    # recipes run sequentially by port at their distinct outer event.
    intervals=[];site=0
    for index,event in enumerate(controller['physical_events']):
        if event[0] == 'LOCAL':
            need(fields[site]['site'] == site and fields[site]['stage'] == event[1], 'Caller local-site order')
            for life in fields[site]['owned_lifetimes']:
                intervals.append(dict(kind='local',site=site,role=life['role'],global_field=life['global_field'],
                    start=[index,0,life['start']],end=[index,0,life['end']]))
            site+=1
        elif event[0] == 'QUERY_SHEAR':
            for port in range(104):
                intervals.append(dict(kind='query',port=port,global_field=interface['productive_fields'],
                    start=[index,port,0],end=[index,port,7]))
    need(site == len(fields) == 18, 'All local substitutions have closed owned schedules')
    check_global_intervals(intervals,interface['productive_fields'])
    bad=deepcopy(intervals)
    local=next(item for item in bad if item['kind']=='local')
    query=next(item for item in bad if item['kind']=='query')
    query.update(global_field=local['global_field'],start=local['start'][:],end=local['end'][:])
    controls={'thin_query_overlaps_local_owned':reject(lambda:check_global_intervals(bad,interface['productive_fields']))}
    return dict(intervals=intervals,controls=controls,address_order='physical event, sequential port, local instruction')
