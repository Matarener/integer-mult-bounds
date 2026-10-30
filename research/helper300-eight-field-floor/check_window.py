#!/usr/bin/env python3
"""Independent exact source audit of one closed normalized-row window.

No source verifier, construction code, or other agent's functions are imported.
Physical all-width native semantics remain inherited.  This check reconstructs
the exact rational matrix between the pinned entry/exit charts and checks every
declared climb against the binary source frame spaces.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Source construction credit: Cao Yifan, Dillon Amburgey, Ali Romman,
Chris R/Clear1nsight and the retained native/compiler lineage.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORD = ROOT / 'research/coupled-helper-neutral-completion/capsule/workspace/swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/WORD.json.gz'
SOURCE = ROOT / 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
WORD_PAYLOAD = '05490717144b3e6c69c0cc9e5c5df5c69d841ca13bf29aabd1b0db180628f038'
SOURCE_PAYLOAD = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
FIRST, STOP = 9044, 9116
FIELDS = [19, 40, 288, 289, 295, 299, 300, 301]
ENTRY = [21, 42, 103, 103, 57, 42, 0, 0]
EXIT = [423, 422, 422, 423, 430, 419, 430, 419]
# Independently obtained by simplifying two signed-swap macros and four
# (u,v)->(u-v,(u+v)/2) butterflies, rather than serial row replay.
EXPECTED_TWICE = [
    [0,0,0,-2,0,0,0,2], [0,0,-2,0,0,2,0,0],
    [0,0,1,0,0,1,0,0], [0,0,0,1,0,0,0,1],
    [0,0,0,0,1,0,1,0], [1,1,0,0,0,0,-1,-1],
    [0,0,0,0,-2,0,2,0], [2,-2,0,0,0,0,-2,-2],
]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def load_pinned(path, expected):
    raw = path.read_bytes()
    data = gzip.decompress(raw)
    require(sha(data) == expected, 'source payload hash mismatch')
    return json.loads(data), {'path':path.relative_to(ROOT).as_posix(), 'compressed_sha256':sha(raw),
                             'payload_sha256':sha(data), 'payload_bytes':len(data)}

def touched(event):
    if event[0] == 'climb':
        return {event[2]}
    if event[0] == 'scalar':
        op = event[1]
        require(op[0] in ('add','scale'), 'unexpected scalar in local window')
        refs = op[1:3] if op[0] == 'add' else op[1:2]
        require(all(x[0] == 'L' for x in refs), 'nonpersistent local owner')
        return {x[1] for x in refs}
    raise ValueError('unexpected event in local window')

def closure(events):
    fields = {19,300,301}
    while True:
        expanded = set(fields)
        for _, event in events:
            support = touched(event)
            if support & fields:
                expanded |= support
        if expanded == fields:
            return sorted(fields)
        fields = expanded

def span(basis):
    result = {0}
    for x in basis:
        result |= {y ^ x for y in tuple(result)}
    return result

def prefix_frames(word, canonical):
    """Source bookkeeping only; no coefficient/operator execution."""
    f = {('L',i):x for i,x in enumerate(canonical['start'])}
    f.update({('C',i):0 for i in range(9)})
    for index,event in enumerate(word[:FIRST]):
        kind=event[0]
        if kind == 'climb':
            _,_,owner,a,b,_=event
            require(f[('L',owner)] == a, f'prefix climb chart at {index}')
            f[('L',owner)] = b
        elif kind == 'warp':
            _,owner,_,a,b=event
            require(f[tuple(owner)] == a, f'prefix warp chart at {index}')
            f[tuple(owner)] = b
        elif kind == 'scalar':
            op, chart = event[1:]
            owners=op[1:3] if op[0] in ('add','copy') else op[1:2]
            for owner in owners:
                # CLEAR resets an owned field to the declared chart; no CLEAR
                # or COPY occurs before this window in the selected source.
                require(f[tuple(owner)] == chart, f'prefix scalar chart at {index}')
        elif kind in ('phase','adapter'):
            pass
        else:
            raise ValueError(f'unhandled prefix event {kind}')
    return [f[('L',x)] for x in FIELDS]

def audit(events, frames):
    require(closure(events) == FIELDS, 'dependency closure mismatch')
    selected=[(i,e) for i,e in events if touched(e)&set(FIELDS)]
    f=dict(zip(FIELDS,ENTRY))
    mat={r:[Q(int(j==k)) for j in range(8)] for k,r in enumerate(FIELDS)}
    paid=[]
    for index,event in selected:
        require(touched(event)<=set(FIELDS),'external dependency')
        if event[0]=='climb':
            _,_,r,a,b,rank=event
            require(f[r]==a,f'climb input chart at {index}')
            sa,sb=span(frames[a]),span(frames[b])
            require(sa <= sb,f'nonmonotone climb at {index}')
            require(len(sa)==2**len(frames[a]) and len(sb)==2**len(frames[b]),'dependent frame basis')
            require(rank==len(frames[b])-len(frames[a]),f'wrong paid rank at {index}')
            f[r]=b
            paid.append({'event':index,'owner':r,'from':a,'to':b,'rank':rank})
        else:
            op,chart=event[1:]
            for r in touched(event):
                require(f[r]==chart,f'scalar operand chart at {index}')
            coefficient=Q(op[-2],op[-1])
            if op[0]=='add':
                dest,source=op[1][1],op[2][1]
                mat[dest]=[a+coefficient*b for a,b in zip(mat[dest],mat[source])]
            else:
                dest=op[1][1]
                mat[dest]=[coefficient*a for a in mat[dest]]
    require([f[x] for x in FIELDS]==EXIT,'exit charts mismatch')
    require(Counter(x['rank'] for x in paid)=={1:10},'paid profile mismatch')
    matrix=[mat[x] for x in FIELDS]
    require(matrix==[[Q(a,2) for a in row] for row in EXPECTED_TWICE], 'all-input transfer mismatch')
    require(len(selected)==28,'selected event count mismatch')
    return selected,paid,matrix

def replay_vector(selected, vector):
    values=dict(zip(FIELDS,vector))
    for _,event in selected:
        if event[0]!='scalar':
            continue
        op=event[1]
        r=op[1][1]
        if op[0]=='add':
            values[r] += (values[op[2][1]]*op[3])/op[4]
        else:
            values[r] = (values[r]*op[2])/op[3]
    return [values[x] for x in FIELDS]

def inverse_matrix(matrix):
    a=[row[:]+[Q(i==j) for j in range(8)] for i,row in enumerate(matrix)]
    determinant=Q(1)
    for col in range(8):
        pivot=next(i for i in range(col,8) if a[i][col])
        if pivot!=col:
            a[col],a[pivot]=a[pivot],a[col];determinant=-determinant
        factor=a[col][col];determinant*=factor
        a[col]=[x/factor for x in a[col]]
        for i in range(8):
            if i!=col:
                factor=a[i][col]
                a[i]=[x-factor*y for x,y in zip(a[i],a[col])]
    inverse=[row[8:] for row in a]
    for left,right in [(matrix,inverse),(inverse,matrix)]:
        require(all(sum(left[i][k]*right[k][j] for k in range(8))==int(i==j)
                    for i in range(8) for j in range(8)), 'two-sided inverse failure')
    return determinant,inverse

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    word,word_pin=load_pinned(WORD,WORD_PAYLOAD)
    source,source_pin=load_pinned(SOURCE,SOURCE_PAYLOAD)
    require(word['direction']=='backward' and word['source_sha256']==SOURCE_PAYLOAD,'source binding')
    canonical=source['canonical'];require(prefix_frames(word['word'],canonical)==ENTRY,'entry charts')
    events=list(enumerate(word['word']))[FIRST:STOP]
    selected,paid,matrix=audit(events,canonical['frames'])
    # Separate scalar-value implementation: each of eight arbitrary-input basis
    # columns and a signed rational vector, all compared with the matrix map.
    samples=[[Q(i==j) for i in range(8)] for j in range(8)]
    samples.append([Q((-1)**i*(i+1),i+2) for i in range(8)])
    for vector in samples:
        require(replay_vector(selected,vector)==[sum(a*b for a,b in zip(row,vector)) for row in matrix],
                'literal vector versus matrix disagreement')
    determinant,inverse=inverse_matrix(matrix)
    controls=[]
    def mutation(name,mutate):
        bad=deepcopy(events);mutate(bad)
        try:
            audit(bad,canonical['frames'])
        except (ValueError,IndexError,KeyError,ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError('accepted mutant: '+name)
    def item(events,index):
        return next(e for i,e in events if i==index)
    mutation('wrong_add_sign_9045',lambda e:item(e,9045)[1].__setitem__(3,1))
    mutation('wrong_half_butterfly_9079',lambda e:item(e,9079)[1].__setitem__(4,1))
    mutation('missing_dirty_partner_9114',lambda e:item(e,9114)[1].__setitem__(2,['L',300]))
    mutation('deleted_swap_scale_9063',lambda e:e.__setitem__(slice(None),[(i,x) for i,x in e if i!=9063]))
    mutation('undercharged_climb_9044',lambda e:item(e,9044).__setitem__(5,0))
    mutation('wrong_scalar_frame_9078',lambda e:item(e,9078).__setitem__(2,422))
    mutation('outside_dependency_9114',lambda e:item(e,9114)[1].__setitem__(2,['L',302]))
    mutation('short_window_missing_9115',lambda e:e.pop())
    mutation('reversed_swap_order',lambda e:e.__setitem__(slice(16,18),list(reversed(e[16:18]))))
    report={'status':'PASS_INDEPENDENT_EIGHT_FIELD_WINDOW',
        'scope':'Exact normalized-row transfer with source-bound charts; physical native semantics inherited.',
        'source_pins':[word_pin,source_pin],'interval':[FIRST,STOP],
        'closure_seed':[19,300,301],'fields':FIELDS,'interval_events':len(events),
        'selected_events':selected,'paid_climbs':paid,'paid_profile':{'1':10},
        'entry_frames':dict(zip(FIELDS,ENTRY)),'exit_frames':dict(zip(FIELDS,EXIT)),
        'frame_bases':{i:canonical['frames'][i] for i in sorted(set(ENTRY+EXIT))},
        'matrix':[[str(a) for a in row] for row in matrix],
        'determinant':str(determinant),'inverse':[[str(a) for a in row] for row in inverse],
        'basis_columns_checked':8,'signed_rational_vectors_checked':1,
        'mutation_controls_rejected':controls}
    if args.output:
        args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
