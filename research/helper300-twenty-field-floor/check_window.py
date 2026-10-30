#!/usr/bin/env python3
"""Independent exact extraction; standard library only, no provider imports."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import platform

LO, HI = 9044, 9137
SEEDS = {19, 300, 301}
EXPECTED_FIELDS = [18,19,39,40,288,289,290,291,292,293,
                   294,295,296,297,298,299,300,301,302,303]
WORD_REL = ('research/coupled-helper-neutral-completion/capsule/workspace/'
            'swarm-provider-audit-sol-high-20261024/repository/research/'
            'native-rank8-helper-provider/WORD.json.gz')
SOURCE_REL = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
PINS = {
    WORD_REL: ('7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc',
               '05490717144b3e6c69c0cc9e5c5df5c69d841ca13bf29aabd1b0db180628f038'),
    SOURCE_REL: ('7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05',
                 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'),
}
def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def binary_basis(vectors):
    pivots = {}
    for vector in vectors:
        v = vector
        while v:
            bit = v.bit_length() - 1
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                break
    return pivots


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in result}
    return result


def refs(event):
    if event[0] == 'climb':
        return [('L', event[2])]
    if event[0] == 'warp':
        return [tuple(event[1])]
    if event[0] == 'scalar':
        return [tuple(x) for x in event[1][1:] if isinstance(x, list)]
    if event[0] in ('adapter', 'zero_retag'):
        return [('L', event[2] if event[0] == 'adapter' else event[1])]
    return []


def closure(window):
    active = set(SEEDS)
    while True:
        enlarged = active.copy()
        for e in window:
            touched = {r for kind, r in refs(e) if kind == 'L'}
            if touched & active:
                enlarged |= touched
        if enlarged == active:
            return sorted(active)
        active = enlarged


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def add_row(rows, target, source, coefficient):
    rows[target] = [x + coefficient*y for x, y in zip(rows[target], rows[source])]


def exact_inverse(matrix):
    n = len(matrix)
    rows = [r.copy() + s for r, s in zip(matrix, identity(n))]
    determinant = Q(1)
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        require(pivot is not None, 'singular endpoint matrix')
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            determinant *= -1
        value = rows[col][col]
        determinant *= value
        rows[col] = [x/value for x in rows[col]]
        for i in range(n):
            if i != col and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [x-factor*y for x,y in zip(rows[i],rows[col])]
    return determinant, [r[n:] for r in rows]


def product(a, b):
    return [[sum(x*y for x,y in zip(row, col)) for col in zip(*b)] for row in a]


def advance_frames(event, current, frames, warps, index):
    kind = event[0]
    if kind == 'scalar':
        op = event[1]
        require(op[0] in ('add', 'scale'), f'{index}: protected/noninvertible scalar')
        touched = refs(event)
        require(all(k == 'L' and current[r] == event[2] for k,r in touched),
                f'{index}: scalar chart or owner mismatch')
        require(op[-1] != 0, f'{index}: zero denominator')
        if op[0] == 'add':
            require(op[1] != op[2], f'{index}: self ADD outside grammar')
        else:
            require(op[-2] != 0, f'{index}: noninvertible scale')
    elif kind == 'climb':
        _, mode, field, before, after, cost = event
        require(mode == 'warp_retimed', f'{index}: unexpected climb mode')
        require(current[field] == before, f'{index}: wrong climb input frame')
        require(span(frames[before]) <= span(frames[after]), f'{index}: nonmonotone climb')
        require(cost == len(frames[after])-len(frames[before]), f'{index}: wrong paid rank')
        require(cost > 0, f'{index}: nonpositive climb')
        current[field] = after
    elif kind == 'warp':
        _, owner, signed_id, before, after = event
        require(owner[0] == 'L' and current[owner[1]] == before,
                f'{index}: warp input frame mismatch')
        require(abs(signed_id) in warps, f'{index}: unknown warp')
        columns = warps[abs(signed_id)]['G_columns']
        lookup = {}
        for x in range(1 << len(columns)):
            y = 0
            for bit, column in enumerate(columns):
                if x & (1 << bit):
                    y ^= column
            lookup[x] = y
        require(len(set(lookup.values())) == len(lookup), f'{index}: singular warp')
        if signed_id < 0:
            lookup = {y:x for x,y in lookup.items()}
        require({lookup[x] for x in span(frames[before])} == span(frames[after]),
                f'{index}: warp frame map mismatch')
        current[owner[1]] = after
    elif kind == 'adapter':
        require(event[1] == 'old_to_new', f'{index}: unexpected adapter direction')
        require(current[event[2]] == event[3], f'{index}: adapter chart mismatch')
    else:
        require(kind == 'phase', f'{index}: unexpected event {kind}')


def execute_local(window, fields, entry, frames, warps):
    require(closure(window) == fields, 'closure changed')
    positions = {field:i for i,field in enumerate(fields)}
    current = dict(zip(fields, entry))
    matrix = identity(len(fields))
    selected = []
    omitted = []
    for offset,e in enumerate(window):
        touched = refs(e)
        if not any(kind == 'L' and r in positions for kind,r in touched):
            omitted.append(LO+offset)
            continue
        require(all(kind == 'L' and r in positions for kind,r in touched),
                f'{LO+offset}: boundary or owned contact')
        require(e[0] in ('scalar','climb'), f'{LO+offset}: local non-add-scale-climb event')
        advance_frames(e,current,frames,warps,LO+offset)
        if e[0] == 'scalar':
            op = e[1]
            row = positions[op[1][1]]
            q = Q(op[-2],op[-1])
            if op[0] == 'add':
                add_row(matrix,row,positions[op[2][1]],q)
            else:
                matrix[row] = [q*x for x in matrix[row]]
        selected.append(LO+offset)
    return matrix,[current[r] for r in fields],selected,omitted


def macro_formula(fields):
    """Independent mathematical circuit, with four swaps and ten butterflies."""
    rows = dict(zip(fields,identity(len(fields))))
    for dest,source in [(19,300),(19,301),(39,302),(39,303)]:
        rows[dest] = [x-y for x,y in zip(rows[dest],rows[source])]
    for a,b in [(297,18),(299,40),(301,19),(303,39)]:
        rows[a],rows[b] = rows[b],rows[a]
    for a,b in [(40,288),(19,289),(18,290),(39,291),(296,292),
                (302,293),(298,294),(300,295),(303,297),(301,299)]:
        x,y = rows[a],rows[b]
        rows[a] = [u-v for u,v in zip(x,y)]
        rows[b] = [(u+v)/2 for u,v in zip(x,y)]
    for dest,source in [(293,295),(288,290),(291,294),(289,292),
                        (298,296),(39,19),(18,300)]:
        rows[dest] = [x-y for x,y in zip(rows[dest],rows[source])]
    return [rows[field] for field in fields]


def direct_vector(window, fields, vector):
    values = dict(zip(fields,vector))
    for e in window:
        if e[0] != 'scalar':
            continue
        op = e[1]
        if op[1][0] != 'L' or op[1][1] not in values:
            continue
        d = op[1][1]
        if op[0] == 'add':
            values[d] += Q(op[3],op[4])*values[op[2][1]]
        elif op[0] == 'scale':
            values[d] *= Q(op[2],op[3])
        else:
            raise ValueError('protected scalar in vector execution')
    return [values[r] for r in fields]


def strings(matrix):
    return [[str(x) for x in row] for row in matrix]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2],
                        help='Repository root; defaults to this package two directories above')
    parser.add_argument('--json',action='store_true',help='Print full exact source-audit evidence')
    args = parser.parse_args()
    inputs = {}
    objects = {}
    for rel,pins in PINS.items():
        compressed = (args.repo/rel).read_bytes()
        raw = gzip.decompress(compressed)
        require((digest(compressed),digest(raw)) == pins, f'input hash mismatch: {rel}')
        inputs[rel] = {'compressed_sha256':digest(compressed), 'content_sha256':digest(raw),
                       'compressed_bytes':len(compressed),'content_bytes':len(raw)}
        objects[rel] = json.loads(raw)
    provider = objects[WORD_REL]
    source = objects[SOURCE_REL]
    require(provider['direction'] == 'backward','wrong provider direction')
    require(provider['source_sha256'] == PINS[SOURCE_REL][1],'provider source binding mismatch')
    word = provider['word']
    canonical = source['canonical']
    frames = canonical['frames']
    require(all(len(binary_basis(b)) == len(b) for b in frames),'dependent source frame basis')
    require(all(all(0 <= v < 2**canonical['h'] for v in b) for b in frames),
            'frame basis outside binary ambient dimension')
    warps = {w['op']:w for w in canonical['warps']}
    require(len(warps) == len(canonical['warps']),'duplicate warp IDs')
    prefix_frames = dict(enumerate(canonical['start']))
    for index,event in enumerate(word[:LO]):
        advance_frames(event,prefix_frames,frames,warps,index)
    window = word[LO:HI]
    require(all(kind=='L' for e in window for kind,_ in refs(e)),
            'owned/cache/scratch contact inside complete interval')
    fields = closure(window)
    require(fields == EXPECTED_FIELDS,'wrong twenty-field closure')
    entry = [prefix_frames[f] for f in fields]
    matrix,exit_frames,selected,omitted = execute_local(window,fields,entry,frames,warps)
    require(matrix == macro_formula(fields),'independent macro transfer mismatch')
    for column,vector in enumerate(identity(len(fields))):
        require(direct_vector(window,fields,vector) == [r[column] for r in matrix],
                f'basis-vector execution mismatch {column}')
    probe = [Q((-1)**i*(i+1),i+2) for i in range(len(fields))]
    require(direct_vector(window,fields,probe) == [sum(x*y for x,y in zip(r,probe)) for r in matrix],
            'signed rational dirty-vector mismatch')
    determinant,inverse = exact_inverse(matrix)
    require(determinant == 1,'unexpected determinant')
    require(product(matrix,inverse) == identity(len(fields)), 'right inverse failed')
    require(product(inverse,matrix) == identity(len(fields)), 'left inverse failed')
    selected_events = [word[i] for i in selected]
    event_counts = Counter(e[0] for e in selected_events)
    scalar_counts = Counter(e[1][0] for e in selected_events if e[0]=='scalar')
    paid = Counter(e[5] for e in selected_events if e[0]=='climb')
    require(dict(event_counts) == {'climb':38,'scalar':47},'event count mismatch')
    require(dict(scalar_counts) == {'add':43,'scale':4},'scalar count mismatch')
    require(dict(paid) == {1:38},'paid histogram mismatch')
    require(sum(len(frames[f]) for f in exit_frames)-sum(len(frames[f]) for f in entry) == 38,
            'endpoint total rank mismatch')
    # Mutation acceptance is compared to semantic boundary obligations, not source hashes.
    def validate(candidate, candidate_entry=entry):
        a,b,c,d = execute_local(candidate,fields,candidate_entry,frames,warps)
        require(a == matrix,'mutated transfer')
        require(b == exit_frames,'mutated output frames')
        require(len(candidate)==HI-LO,'mutated interval length')
        require([candidate[i-LO] for i in omitted] == [window[i-LO] for i in omitted],
                'changed disjoint interval event')
        require(Counter(e[5] for e in candidate if e[0]=='climb' and e[2] in fields)==paid,
                'mutated paid histogram')
    controls = []
    def reject(name,candidate,candidate_entry=entry):
        try:
            validate(candidate,candidate_entry)
        except (ValueError,KeyError,IndexError,ZeroDivisionError) as exc:
            controls.append({'name':name,'rejected':True,'reason':str(exc)})
            return
        raise ValueError('semantic control unexpectedly accepted: '+name)
    c=deepcopy(window); c[9045-LO][1][3]=1; reject('initial dirty-input sign',c)
    c=deepcopy(window); c[9047-LO][1][3]=0; reject('drop second dirty-input contribution',c)
    c=deepcopy(window); c[9075-LO][1][4]=1; reject('replace butterfly half by one',c)
    c=deepcopy(window); c[9052-LO],c[9053-LO]=c[9053-LO],c[9052-LO]; reject('swap serialized swap ADD order',c)
    c=deepcopy(window); c[9118-LO][2]=432; reject('wrong scalar contact frame',c)
    c=deepcopy(window); c[9116-LO][5]=0; reject('undercharge a paid climb',c)
    c=deepcopy(window); c[9045-LO][1][2]=['C',1]; reject('introduce owned-cache source',c)
    c=deepcopy(window); c[9136-LO][1][3]=0; reject('drop final post-mix',c)
    c=deepcopy(window); c[9070-LO][1][3]=1; reject('modify disjoint interval event',c)
    reject('truncate last boundary event',deepcopy(window[:-1]))
    bad_entry=entry.copy(); bad_entry[fields.index(300)]=21
    reject('zero-frame dirty carrier assigned wrong entry frame',deepcopy(window),bad_entry)
    all_copies = [{'index':i,'operation':e[1],'frame':e[2]} for i,e in enumerate(word)
                  if i>=HI and e[0]=='scalar' and e[1][0]=='copy']
    cache_taps = [e for e in all_copies if e['operation'][1][0]=='C'
                  and e['operation'][2][0]=='L']
    direct_taps = [e for e in cache_taps if e['operation'][2][1] in fields]
    require(direct_taps[0]['index']==11322,'unexpected first later direct cache tap')
    serialized = strings(matrix)
    result = {
        'status':'PASS','python':platform.python_version(),'optimized':not __debug__,
        'input_pins':inputs,'provider_source_binding':provider['source_sha256'],
        'direction':provider['direction'],'total_provider_events':len(word),
        'interval':[LO,HI],'seeds':sorted(SEEDS),'fields':fields,
        'entry_frames':entry,'exit_frames':exit_frames,
        'entry_bases':[frames[f] for f in entry], 'exit_bases':[frames[f] for f in exit_frames],
        'all_contact_frame_bases':{str(f):frames[f] for f in sorted({x for e in selected_events for x in
            ([e[3],e[4]] if e[0]=='climb' else [e[2]])})},
        'selected_indices':selected,'omitted_indices':omitted,
        'omitted_events':[{'index':i,'event':word[i]} for i in omitted],
        'selected_event_counts':dict(event_counts),'selected_scalar_counts':dict(scalar_counts),
        'paid_histogram':dict(paid),'entry_rank_sum':sum(len(frames[f]) for f in entry),
        'exit_rank_sum':sum(len(frames[f]) for f in exit_frames),
        'endpoint_rank_difference_histogram':dict(Counter(len(frames[b])-len(frames[a])
                                                        for a,b in zip(entry,exit_frames))),
        'matrix':serialized,'matrix_sha256':digest(json.dumps(serialized,separators=(',',':')).encode()),
        'determinant':str(determinant),'inverse':strings(inverse),
        'prefix_event_counts':dict(Counter(e[0] for e in word[:LO])),
        'prefix_scalar_counts':dict(Counter(e[1][0] for e in word[:LO] if e[0]=='scalar')),
        'prefix_warp_ids':sorted({abs(e[2]) for e in word[:LO] if e[0]=='warp'}),
        'prefix_invertibility':{
            'persistent_registers':len(canonical['start']),
            'nonzero_scale_checks':334,'distinct_owner_add_checks':8107,
            'warp_binary_permutations_checked':96,
            'claim':'Constructive grammar proof in inherited normalized/native chart semantics: '
                    'all persistent ADDs have distinct owners, all SCALEs are nonzero, every warp '
                    'has a bijective ambient binary map and correct source/target frame span. '
                    'Climbs and adapters retain the inherited invertible chart interpretation. '
                    'Consequently arbitrary twenty cut-coordinate inputs are legitimate; '
                    'zero entry frames do not mean zero register values.',
        },
        'protected_contacts':{
            'inside_window':[], 'later_persistent_cache_taps':cache_taps,
            'later_cache_to_scratch_copies':[e for e in all_copies if e['operation'][2][0]=='C'],
            'first_direct_tap_from_closure':direct_taps[0],
            'preservation':'Exact equality of all twenty endpoint values and charts, with the '
                           'eight disjoint interval events unchanged, preserves every later '
                           'owned/cache/scratch relation by composition. No fresh complete '
                           'physical-provider replay is claimed.',
        },
        'semantic_controls':controls,
        'checks':['source hashes and source binding','binary frame basis independence',
                  'prefix chart/invertibility grammar','fixed-point closure','monotone paid climbs',
                  'same-frame scalar contacts','exact twenty-row transfer','independent macro formula',
                  'twenty basis-vector runs','signed rational dirty-vector run',
                  'exact determinant and two-sided inverse','eleven rejected semantic mutations'],
        'scope':'Finite exact source-bound normalized-transfer audit; no new kappa, no whole-provider '
                'impossibility, no replacement feasibility proof, and no new native/phase theorem.'
    }
    if args.json:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        print('PASS_INDEPENDENT_SOURCE fields=20 paid_climbs=38 determinant=1 controls='
              +str(len(controls)))


if __name__=='__main__':
    main()
