#!/usr/bin/env python3
"""Literal four-way audit, no imports from the integration or predecessor builders.

Shared mathematical sources are deliberate: this is a separately written checker,
not independent discovery, formal verification or a physical-caller proof.
Apache-2.0; Chris R / Clear1nsight with OpenAI Codex assistance.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
PINS = {
 'r437-pooled-native-interface/inputs/geometry.json.gz': 'edcaebb35d313f403b2db45a2cf808617f921c83cf7a11dd5d74356570ede1a8',
 'r437-two-window-carrier/CANDIDATE.json': '0e4dc8bda7941b9c5bba2f7af9895544ca6f69666026e4835610b808c3d4d7f2',
 'r437-two-window-carrier/inputs/R437-COMPOSED-WORD.json.gz': 'e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e',
 'r437-two-window-carrier/inputs/OQ4-TEMPLATE.json.gz': '6e03c76f5a4227394ea57e901eb7e93f4d1ee411ccfecd483fd44ea043550494',
 'r437-pooled-native-interface/inputs/moves.json': '0a58b239795d213743b5654c59a3e4622a0ddd4a53d8dba3fa30dedef4558dff',
}

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def load(path):
    data = (RESEARCH/path).read_bytes()
    need(hashlib.sha256(data).hexdigest() == PINS[path], 'pinned input '+path)
    return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)

def row_basis(rows):
    pivots = {}
    for raw in rows:
        row = list(map(Fraction, raw))
        for i, old in sorted(pivots.items()):
            a = row[i]
            row = [x-a*y for x,y in zip(row, old)]
        if any(row):
            i = next(i for i,v in enumerate(row) if v)
            a = row[i]
            pivots[i] = [x/a for x in row]
    return pivots

def geometry(w):
    dims = []
    for frame in w['frames']:
        basis = row_basis([w['lines'][i] for i in frame])
        closed = []
        for i, raw in enumerate(w['lines']):
            row = list(map(Fraction, raw))
            for j, old in sorted(basis.items()):
                a = row[j]
                row = [x-a*y for x,y in zip(row, old)]
            if not any(row): closed.append(i)
        need(frame == closed, 'rationally closed frame')
        dims.append(len(basis))
    return dims

def emit(w, dims):
    """Independently expand four word sections into scalar chronological events."""
    current = w['start'][:]
    events = []
    provenance = []
    def push(event, origin):
        events.append(event); provenance.append(origin)
    def move(role, frame, origin):
        old = current[role]
        need(set(w['frames'][old]).issubset(w['frames'][frame]), 'monotone frame')
        if old != frame:
            push([0, role, old, frame, dims[frame]-dims[old], 0], origin)
            current[role] = frame
    for section in ['D','A','B','C']:
        if section == 'B':
            for k, role in enumerate(w['ret']):
                frame = current[role]
                push([2,role,659,frame,0,dims[frame],0], ['COPY',k])
                for target, sources in enumerate(w['scatter']):
                    if k in sources: push([1,111+target,659,1,0,0], ['SCATTER',k,target])
                push([3,role,659,frame,0,0,0], ['ERASE',k])
        for i,(frame,destination,sources) in enumerate(w[section]):
            origin = [section,i]
            for role in [destination]+sources: move(role,frame,origin)
            for source in sources: push([1,destination,source,1,frame,0], origin)
    for role,frame in enumerate(w['final']): move(role,frame,['FINAL',role])
    reverse = []
    for e in reversed(events):
        if e[0] == 0: reverse.append([0,e[1],e[3],e[2],e[4],1])
        elif e[0] == 1: reverse.append([1,e[1],e[2],-1,e[4],1])
        elif e[0] == 3: reverse.append([2,*e[1:5],dims[e[3]],1])
        else: reverse.append([3,*e[1:5],e[5],1])
    return {'forward':events,'reverse':reverse}, provenance

def replay(events):
    state = [1 << i for i in range(659)] + [0]
    opened = None
    captures, writes = [], []
    profile = Counter()
    for position,e in enumerate(events):
        kind,role = e[:2]
        if kind == 0: profile[e[4]] += 1
        elif kind == 1:
            need(role != opened and (e[2] != 659 or opened is not None), 'live COPY ownership')
            state[role] ^= state[e[2]]
            if role < 111: writes.append([role,hex(state[role])])
        elif kind == 2:
            need(opened is None and state[659] == 0, 'private COPY vacant')
            opened = role; state[659] = state[role]
            captures.append([role,e[3],hex(state[role])]); profile[e[5]] += 1
        elif kind == 3:
            need(opened == role and state[659] == state[role], 'exact protected return before ERASE')
            state[659] = 0; opened = None
        else: raise ValueError('event kind')
    want = [(1 << i)^((1 << (i-111)) if 111 <= i < 222 else 0) for i in range(659)] + [0]
    need(state == want and opened is None, 'all 659 independent columns and terminal restoration')
    return profile, captures, writes

def hosting(template, moves):
    """Use bit occupancy, absolute family slots, and schedule-derived idle windows."""
    previous = {}
    sweeps = []
    windows = {}
    for pos,event in enumerate(template['schedule']):
        kind = event['kind']
        if kind == 'local_cover_sweep':
            previous[event['pair']] = pos
            sweeps.append((pos,event['pair'],event['stage']))
        elif kind == 'bridge':
            previous[event['src']] = previous[event['dst']] = pos
        elif kind == 'idle':
            stages = [s for p,pair,s in sweeps if previous.get(event['pair'],-1) < p < pos and pair != event['pair']]
            if event['rank'] and stages: windows[str(event['idx'])] = [event['pair'],event['rank'],stages]
    need(windows == template['hosting']['windows'], 'literal untouched chronological hosting windows')
    calls = {(c['stage'],c['replica']):deepcopy(c) for c in template['calls']}
    need(len(calls) == 288 and set(calls) == {(s,r) for s in range(9) for r in range(32)}, 'unique full call domain')
    changed = set()
    for change in moves:
        key = change['stage'],change['call_replica'],222+change['helper']
        need(key not in changed, 'duplicate owner rewrite')
        changed.add(key)
        old,new = change['old'],change['new']
        owners = calls[key[:2]]['owners']
        need(owners[key[2]] == [old['family'],['hosted',old['child'],old['offset'],8]], 'literal old owner')
        owners[key[2]] = [new['family'],['hosted',new['child'],new['offset'],8]]
    occupied = {}
    owners_digest = hashlib.sha256()
    for (stage,replica),call in sorted(calls.items()):
        need(call['orientation'] == ('reverse' if stage%2 else 'forward'), 'orientation')
        for role,(family,route) in enumerate(call['owners']):
            if role < 222:
                side = role//111 ^ (stage%2)
                need([family,route] == [replica*888+222*call['pair']+111*side+role%111,['data',stage,role%111]], 'absolute data owner')
            else:
                need(route[0] == 'hosted', 'helper route')
                child,off,width = route[1:]
                pair,rank,stages = windows[str(child)]
                need(stage in stages and pair != call['pair'], 'owner lifetime')
                need(0 <= family < 28416 and (family%888)//222 == pair, 'owner family domain')
                need(width == 8 and 0 <= off <= rank-8, 'eight coordinate slot')
                bits = 255 << off
                used = occupied.get((child,family),0)
                need(not used & bits, 'disjoint pooled cells')
                occupied[child,family] = used|bits
            owners_digest.update(canonical([stage,replica,role,family,route])+b'\n')
    idle_profile = Counter(); idles = []
    for event in template['schedule']:
        if event['kind'] != 'idle' or not event['rank']: continue
        child,pair,capacity = event['idx'],event['pair'],event['rank']
        for replica in range(32):
            for cp in range(222):
                family = replica*888+222*pair+cp
                used = occupied.get((child,family),0)
                n = used.bit_count()
                need(used == (1 << n)-1, 'contiguous hosted prefix')
                rank = capacity-n
                if rank:
                    idle_profile[rank] += 1
                    idles.append([child,replica,cp,family,n,rank])
    return idle_profile, idles, owners_digest.hexdigest(), sorted(changed)

def inverse(matrix):
    n = len(matrix)
    rows = [list(row)+[Fraction(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    for j in range(n):
        pivot = next(i for i in range(j,n) if rows[i][j])
        rows[j],rows[pivot] = rows[pivot],rows[j]
        a = rows[j][j];rows[j] = [x/a for x in rows[j]]
        for i in range(n):
            if i != j:
                a = rows[i][j];rows[i] = [x-a*y for x,y in zip(rows[i],rows[j])]
    return [row[n:] for row in rows]

def native_digest(template, moves, w, dims, idles):
    """Literal Request.record reconstruction via Gram inverse, no catalogue import."""
    projectors = []
    for frame in w['frames']:
        rows = list(row_basis([w['lines'][i] for i in frame]).values())
        if not rows:
            projectors.append([[Fraction(0)]*8 for _ in range(8)]);continue
        gram = [[sum(a*b for a,b in zip(x,y)) for y in rows] for x in rows]
        inv = inverse(gram)
        p = [[sum(rows[a][i]*inv[a][b]*rows[b][j] for a in range(len(rows)) for b in range(len(rows))) for j in range(8)] for i in range(8)]
        projectors.append(p)
    bases = {}
    def local_base(a,b):
        lo,hi = (a,b) if dims[a] <= dims[b] else (b,a)
        key = lo,hi
        if key not in bases:
            rows = [[str(x-y) for x,y in zip(r,s)] for r,s in zip(projectors[hi],projectors[lo])]
            bases[key] = digest(['local',dims[hi]-dims[lo],rows])
        return bases[key]
    idle_events = {e['idx']:e for e in template['schedule'] if e['kind']=='idle'}
    def pending(child):
        e = idle_events[child];a,b = e['source_level'],e['target_level']
        return list(range(1 if a == -1 else 8+7*a,8+7*b))
    def chart(owner):
        family,route = owner
        if route[0] == 'data': return ['data',route[2],route[1],[]]
        _,child,offset,width = route
        axes = pending(child)[offset:offset+width]
        return ['host',family%111 if min(axes)<8 else -1,-1,axes]
    overlay = {(m['stage'],m['call_replica'],222+m['helper']):[m['new']['family'],['hosted',m['new']['child'],m['new']['offset'],8]] for m in moves}
    out = hashlib.sha256();kinds=Counter();count=0
    def add(replica,row):
        nonlocal count
        out.update(canonical(['pooled-replica-request-v1',replica]+row)+b'\n')
        kinds[row[0]] += 1;count += 1
    for call in template['calls']:
        stage,replica = call['stage'],call['replica']
        for pos,event in enumerate(template['local_programs'][call['orientation']]):
            op,role = event[:2]
            if op not in (0,2): continue
            owner = overlay.get((stage,replica,role),call['owners'][role])
            if op == 0:
                a,b,rank = event[2:5]
                row = ['MOVE',stage,pos,role,owner[0],a,b,local_base(a,b),rank,chart(owner),'owner',None]
            else:
                a,b,rank = event[3:6]
                row = ['COPY',stage,pos,role,template['live'],a,b,local_base(a,b),rank,['identity',-1,-1,[]],'common',chart(owner)]
            add(replica,row)
    for child,replica,cp,family,used,rank in idles:
        e=idle_events[child];axes=pending(child)[used:]
        need(len(axes)==rank,'idle native axes')
        add(replica,['IDLE',child,child,cp,family,e['source_level'],e['target_level'],digest(['idle',rank,axes]),rank,['family',cp%111,-1,[]],'owner',None])
    # Full GL64 vocabulary width, independently evaluated integer product.
    widths={}
    for q in [3,5]:
        size=1
        for k in range(64): size*=q**64-q**k
        widths[str(q)] = (2*count*size-1).bit_length()
    return {'ordered_request_sha256':out.hexdigest(),'request_kinds':dict(kinds),'request_count':count,'source_code_bits':widths,
            'local_base_labels':len(set(bases.values()))}

def slot_injections(template,moves,geometry_data):
    # Derive a common ambient family chart F_p. Actual owner chart is A*P,
    # where A is F_p exactly when the selected slot touches the first8 axes.
    # Otherwise F_p acts as identity on that slot, so the injections agree.
    for port in geometry_data['ports']:
        a = [[Fraction(port['q'][i],2)]+list(map(Fraction,port['complement_columns'][i])) for i in range(8)]
        inv = inverse(a)
        need(all(x.denominator & (x.denominator-1) == 0 for row in a+inv for x in row),'dyadic family chart and inverse')
        need(all(sum(a[i][k]*inv[k][j] for k in range(8)) == (i==j) for i in range(8) for j in range(8)), 'family chart inverse')
    idle_events={e['idx']:e for e in template['schedule'] if e['kind']=='idle'}
    pending={}
    by_pair={}
    for child,e in idle_events.items():
        a,b=e['source_level'],e['target_level'];axes=set(range(1 if a==-1 else 8+7*a,8+7*b))
        need(not axes & by_pair.get(e['pair'],set()),'different IDLE domains disjoint within each pair')
        by_pair.setdefault(e['pair'],set()).update(axes);pending[child]=sorted(axes)
    override={(m['stage'],m['call_replica'],222+m['helper']):[m['new']['family'],['hosted',m['new']['child'],m['new']['offset'],8]] for m in moves}
    occupied={};count=0;coordinates=0;touching=0;seen_slots=set()
    for call in template['calls']:
        for role,old in enumerate(call['owners'][222:],222):
            family,route=override.get((call['stage'],call['replica'],role),old)
            child,offset,width=route[1:];axes=pending[child][offset:offset+width]
            need(len(axes)==8,'complete slot dimension')
            permutation=list(range(64))
            for a,b in zip(sorted(set(range(8))-set(axes)),sorted(set(axes)-set(range(8)))):
                permutation[a],permutation[b]=b,a
            image=permutation[:8]
            need(set(image)==set(axes),'actual column permutation injection')
            # Actual owner A is identity off low8, while common F also is.
            if min(axes)>=8: need(all(k>=8 for k in image),'identity branch equals common-family injection')
            else: touching+=1
            previous=occupied.setdefault(family,set())
            need(not previous.intersection(axes),'global per-family slot direct sum')
            previous.update(axes);count+=1;coordinates+=8;seen_slots.add((family%111,tuple(image)))
    remainder_coordinates=0
    for e in template['schedule']:
        if e['kind']!='idle' or not e['rank']:continue
        child,pair=e['idx'],e['pair']
        for replica in range(32):
            for cp in range(222):
                family=replica*888+pair*222+cp
                remainder_coordinates+=len(set(pending[child])-occupied.get(family,set()))
    return {'helper_occurrences':count,'transported_slot_coordinates':coordinates,'distinct_port_slot_injections':len(seen_slots),
        'first8_touching_occurrences':touching,'remaining_IDLE_coordinates':remainder_coordinates,
        'family_charts_and_inverse_dyadic':111,'common_family_left_inverse':'L=E8^T P^-1 F_family^-1',
        'scope':'Exact rational injection/direct-sum identity; valid modulo every odd prime for these dyadic family charts. Local residual reduction still requires its own prime/domain guards. No physical primitive refinement is inferred.'}

def run():
    old = load('r437-two-window-carrier/inputs/R437-COMPOSED-WORD.json.gz')
    new = load('r437-two-window-carrier/CANDIDATE.json')
    original = load('r437-two-window-carrier/inputs/OQ4-TEMPLATE.json.gz')
    proposal = load('r437-pooled-native-interface/inputs/moves.json')
    need(digest(original) == proposal['template_content_sha256'], 'pool proposal exact original template')
    partroot = RESEARCH/'r437-two-window-carrier'
    manifest = json.loads((partroot/'CANDIDATE-TEMPLATE.json').read_bytes())
    parts = []
    for i,p in enumerate(manifest['parts']):
        need(p['path'] == 'candidate-template-chunks/part-%03d.bin'%i, 'ordered chunk path')
        data = (partroot/p['path']).read_bytes()
        need(len(data) == p['bytes'] and hashlib.sha256(data).hexdigest() == p['sha256'], 'chunk authentication')
        parts.append(data)
    compressed = b''.join(parts)
    need(hashlib.sha256(compressed).hexdigest() == '5fe2bffb2d4f67ef0937240cafc22cb55c29f51157810dc917464c7714ac7f74', 'exact carrier template')
    carrier = json.loads(gzip.decompress(compressed))
    dims = geometry(old)
    need(old['frames'] == new['frames'] and old['lines'] == new['lines'], 'same rational geometry')
    observations = {}; locals_ = {}; early = {}
    for name,w,t in [('old',old,original),('new',new,carrier)]:
        streams,origin = emit(w,dims)
        need(streams == t['local_programs'], 'literal local stream binding '+name)
        observations[name] = {}
        for direction,events in streams.items():
            profile,captures,writes = replay(events)
            locals_[name,direction] = profile
            observations[name][direction] = {'profile':dict(sorted(profile.items())), 'captures':captures, 'SOURCE_writes':writes,
                'ADDs':sum(e[0]==1 for e in events), 'events':len(events), 'stream_sha256':digest(events)}
        early[name] = [[i,origin[i],e[2],e[3],e[4]] for i,e in enumerate(streams['forward']) if e[0]==0 and e[1]==87]
    differences = {}
    mask = (1 << 111)-1
    for direction in ['forward','reverse']:
        a,b = observations['old'][direction],observations['new'][direction]
        need(a['SOURCE_writes'] == b['SOURCE_writes'], 'SOURCE write observations '+direction)
        need([[r,f,int(v,16)&mask] for r,f,v in a['captures']] == [[r,f,int(v,16)&mask] for r,f,v in b['captures']], 'COPY SOURCE rows and frames '+direction)
        differences[direction] = {'full_COPY_DIRTY_rows_changed':[i for i,(x,y) in enumerate(zip(a['captures'],b['captures'])) if x!=y],
            'SOURCE_writes_count':len(a['SOURCE_writes']), 'COPY_count':len(a['captures']),
            'changed_capture_witnesses':[{'ordinal':i,'role':x[0],'frame':x[1],'old_row':x[2],'new_row':y[2],'xor_row':hex(int(x[2],16)^int(y[2],16)), 'DIRTY_roles':[r for r in range(222,659) if (int(x[2],16)^int(y[2],16))>>r&1]} for i,(x,y) in enumerate(zip(a['captures'],b['captures'])) if x!=y]}
    owner_data = {}; profiles = {}; native = {}; slot_receipts = {}
    geometry_data = load('r437-pooled-native-interface/inputs/geometry.json.gz')
    for owner_name,moves in [('OQ4',[]),('pooled',proposal['moves'])]:
        before = hosting(original,moves); after = hosting(carrier,moves)
        slot_receipts[owner_name] = slot_injections(carrier,moves,geometry_data)
        need(before == after, 'word update leaves whole owner domain/lifetime untouched')
        idle,idles,owners,changed = before
        if owner_name == 'pooled':
            native['C'] = native_digest(original,moves,old,dims,idles)
            native['D'] = native_digest(carrier,moves,new,dims,idles)
        owner_data[owner_name] = {'idle_profile':dict(sorted(idle.items())), 'idle_records':len(idles), 'idle_records_sha256':digest(idles), 'owner_sha256':owners,'changed_owners':changed}
        for name,letter in [('old','A' if owner_name=='OQ4' else 'C'),('new','B' if owner_name=='OQ4' else 'D')]:
            total = Counter(idle)
            for s in range(9): total.update({r:n*32 for r,n in locals_[name,'reverse' if s%2 else 'forward'].items()})
            profiles[letter] = {'profile':dict(sorted(total.items())), 'requests':sum(total.values()), 'mass':sum(r*n for r,n in total.items())}
    delta = Counter(profiles['D']['profile']); delta.subtract(profiles['C']['profile'])
    delta = {r:n for r,n in delta.items() if n}
    need(delta == {1:288,2:-576,3:288}, 'pooled carrier rank delta')
    need(all(p['requests']==903456 and p['mass']==1808352 for p in profiles.values()), 'same four-way rank mass and requests')
    # Meaningful stale-source/owner controls, preserving immutable fixtures.
    controls = []
    stale = deepcopy(new); stale['D'] = old['D']
    try: replay(emit(stale,dims)[0]['forward'])
    except ValueError: controls.append('old_D_rejected_by_arbitrary_DIRTY_identity')
    else: raise ValueError('stale D accepted')
    badmoves = deepcopy(proposal['moves']); badmoves[0]['new']['family'] += 222
    try: hosting(original,badmoves)
    except ValueError: controls.append('wrong_destination_pair_rejected')
    else: raise ValueError('bad family accepted')
    try: hosting(original,proposal['moves']+[proposal['moves'][0]])
    except ValueError: controls.append('duplicate_owner_rewrite_rejected')
    else: raise ValueError('duplicate owner accepted')
    for name in observations:
        for direction in observations[name]:
            observations[name][direction].pop('captures');observations[name][direction].pop('SOURCE_writes')
    return {'status':'PASS_INDEPENDENT_LITERAL_FOUR_WAY','source_sha256':PINS,'local':observations,'COPY_and_SOURCE_comparison':differences,
        'early_SOURCE87_MOVE':early,'owners':owner_data,'four_way':profiles,'D_minus_C_profile':delta,
        'native_requests':native, 'slot_injection':slot_receipts, 'D_changed_rows':sum(a!=b for a,b in zip(old['D'],new['D'])), 'controls':controls,
        'scope':'Shared authenticated source words independently interpreted; GF2 arbitrary-DIRTY identity, rational frame closure, chronological pooled ownership. No numerical envelope or physical primitive refinement follows.'}

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run();path=HERE/'INDEPENDENT-RESULT.json'
    if args.write: path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: need(json.loads(json.dumps(result))==json.loads(path.read_text()),'immutable comparison receipt')
    print(result['status'])
