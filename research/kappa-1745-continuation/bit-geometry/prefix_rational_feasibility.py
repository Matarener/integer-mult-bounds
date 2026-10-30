#!/usr/bin/env python3
"""Complete entrance compatibility for equal-response prefix conjugations.

The predecessor report propagated a rational upper space for the proposed
helper entrance only. This screen also checks every prescribed SOURCE lower
space, which is necessary for the entire graph to have any nested-frame
realization. It then constructs the least rational frame walk when feasible.
The prefix circuit construction retains kappa-next-regime word-track credit.
Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OLD = REPO/'research/kappa-next-regime'
sys.path.insert(0,str(OLD/'word-search'))
from bit_prefix_gl import change,scalar


def need(ok,message):
    if not ok:
        raise AssertionError(message)


def rref(rows):
    rows = [list(map(Q,row)) for row in rows]
    rank = 0
    for column in range(8):
        pivot = next((j for j in range(rank,len(rows)) if rows[j][column]),None)
        if pivot is None:
            continue
        rows[rank],rows[pivot] = rows[pivot],rows[rank]
        divisor = rows[rank][column]
        rows[rank] = [x/divisor for x in rows[rank]]
        for j in range(len(rows)):
            if j != rank and rows[j][column]:
                coefficient = rows[j][column]
                rows[j] = [x-coefficient*y for x,y in zip(rows[j],rows[rank])]
        rank += 1
    return tuple(map(tuple,rows[:rank]))


@lru_cache(None)
def join(a,b):
    if not a:
        return b
    if not b or a == b:
        return a
    return rref(a+b)


@lru_cache(None)
def perp(space):
    pivots = [next(j for j,x in enumerate(row) if x) for row in space]
    result = []
    for free in range(8):
        if free not in pivots:
            row = [Q(int(j == free)) for j in range(8)]
            for pivot,equation in zip(pivots,space):
                row[pivot] = -equation[free]
            result.append(row)
    return rref(result)


def encode(space):
    return [[str(x) for x in row] for row in space]


def compatible(subspace,annihilator):
    return all(sum(x*y for x,y in zip(row,normal)) == 0 for row in subspace for normal in annihilator)


def check(word,p,q,cut,spaces,captures):
    candidate = change(word,p,q,cut)
    upper = [perp(spaces[f]) for f in candidate['final']]
    for section in ('B','A'):
        for _,destination,sources in reversed(candidate[section]):
            bound = upper[destination]
            for source in sources:
                bound = join(bound,upper[source])
            for role in [destination]+sources:
                upper[role] = bound
        if section == 'B':
            for role,frame in captures.items():
                upper[role] = join(upper[role],perp(frame))
    defects = []
    for role,start in enumerate(candidate['start']):
        if not compatible(spaces[start],upper[role]):
            for vector in spaces[start]:
                for normal in upper[role]:
                    pairing = sum(x*y for x,y in zip(vector,normal))
                    if pairing:
                        defects.append({'role':role,'start_frame':start,
                                        'start_vector':[str(x) for x in vector],
                                        'required_annihilator':[str(x) for x in normal],
                                        'nonzero_pairing':str(pairing)})
                        break
                if defects and defects[-1]['role'] == role:
                    break
    entrance = perp(upper[p])
    result = {'p':p,'q':q,'cut':cut,'helper_entrance_upper_dimension':len(entrance),
              'helper_entrance_upper_basis':encode(entrance),
              'SOURCE_entrance_violations':defects,'A_scalar_count':sum(len(ss) for _,_,ss in candidate['A'])}
    if defects:
        result['status'] = 'EXACT_RATIONAL_GRAPH_INFEASIBLE_AT_PRESCRIBED_SOURCE_ENTRANCES'
        return result,None
    if not entrance:
        result['status'] = 'NO_NONZERO_PROPOSED_HELPER_ENTRANCE'
        return result,None
    # Complete least join walk is a constructive feasibility witness. It does
    # not assert optimal tariff; arbitrary rational frames are kept explicit.
    current = [spaces[f] for f in candidate['start']]
    current[p] = entrance
    paths = [[space] for space in current]
    profile = Counter(); gates = {}; frames = set(spaces+[entrance])
    def move(role,frame):
        need(compatible(current[role],perp(frame)), 'nested rational forward walk')
        if current[role] != frame:
            profile[len(frame)-len(current[role])] += 1
            current[role] = frame; paths[role].append(frame)
        frames.add(frame)
    for section in ('D','A','B','C'):
        if section == 'B':
            for role,frame in captures.items():
                move(role,frame); profile[len(frame)] += 1
        output = []
        for old_frame,destination,sources in candidate[section]:
            frame = ()
            for role in [destination]+sources:
                frame = join(frame,current[role])
            if section in ('D','C'):
                fixed = spaces[old_frame]
                need(compatible(frame,perp(fixed)), 'D/C fixed native frame contains complete current state')
                frame = fixed
            for role in [destination]+sources:
                move(role,frame)
            output.append((frame,destination,sources))
        gates[section] = output
    for role,frame_id in enumerate(candidate['final']):
        move(role,spaces[frame_id])
    table = sorted(frames,key=lambda x:(len(x),x))
    numbers = {frame:i for i,frame in enumerate(table)}
    candidate['format'] = 'bitE8/explicit-rational-frame-bases/research-only'
    candidate['rational_frame_bases'] = [encode(frame) for frame in table]
    candidate['frames'] = [[j for j,line in enumerate(word['lines']) if compatible((tuple(map(Q,line)),),perp(frame))]
                           for frame in table]
    candidate['start'] = [numbers[spaces[f]] for f in word['start']]
    candidate['start'][p] = numbers[entrance]
    candidate['final'] = [numbers[spaces[f]] for f in word['final']]
    for section in gates:
        candidate[section] = [[numbers[f],d,ss] for f,d,ss in gates[section]]
    result.update(status='EXACT_SCALAR_AND_RATIONAL_FRAME_CANDIDATE_REQUIRES_NATIVE_GENERALIZATION',
                  local_profile=dict(sorted(profile.items())),helper_width=8-len(entrance),
                  explicit_rational_frames=len(table),
                  extra_capture_moves='already counted in profile; serialized separately as capture_frames',
                  scope='Least-frame walk, not tariff optimum or native owner admission')
    candidate['capture_frames'] = {str(role):numbers[frame] for role,frame in captures.items()}
    return result,candidate


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,default=OLD/'word-search/candidate/WORD.json.gz')
    ap.add_argument('--out',type=Path,default=HERE/'prefix-rational')
    args = ap.parse_args(); args.out.mkdir(parents=True,exist_ok=False)
    raw = args.word.read_bytes(); word = json.loads(gzip.decompress(raw))
    spaces = [rref([word['lines'][j] for j in frame]) for frame in word['frames']]
    current = word['start'][:]
    for section in ('D','A'):
        for f,d,ss in word[section]:
            for role in [d]+ss:
                current[role] = f
    captures = {role:spaces[current[role]] for role in word['ret']}
    flat = [(d,s) for _,d,ss in word['A'] for s in ss]
    results,found = [],[]
    for p,q in [(444,473),(473,444),(468,477),(477,468)]:
        cuts = sorted({0,len(flat)}|{j for i,pair in enumerate(flat) if p in pair or q in pair for j in (i,i+1)})
        for cut in cuts:
            result,candidate = check(word,p,q,cut,spaces,captures)
            if candidate is not None:
                payload = json.dumps(candidate,sort_keys=True,separators=(',',':')).encode()
                name = f'p{p}-q{q}-cut{cut}.json.gz'
                (args.out/name).write_bytes(gzip.compress(payload,mtime=0))
                result.update(word=name,canonical_sha256=sha256(payload).hexdigest())
                found.append(result)
            results.append(result)
            print(p,q,cut,result['helper_entrance_upper_dimension'],result['status'],len(result['SOURCE_entrance_violations']),flush=True)
    receipt = {'status':'COMPLETE_RATIONAL_SOURCE_ENTRANCE_COMPATIBILITY_FOR_NAMED_PREFIX_GRAPHS',
               'source_word_sha256':sha256(raw).hexdigest(),'source_word_canonical_sha256':sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
               'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
               'prefix_constructor_sha256':sha256((OLD/'word-search/bit_prefix_gl.py').read_bytes()).hexdigest(),
               'count':len(results),'cases':results,'candidates':found,
               'status_histogram':dict(Counter(row['status'] for row in results)),
               'scope':'All cuts immediately before/after contacts of the two equal-D-column pairs, both orientations; the full fixed SOURCE starts, target/COPY caps, and arbitrary rational frame spaces. Other basis maps and changed controllers remain outside.'}
    (args.out/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('DONE',receipt['status_histogram'],flush=True)


if __name__ == '__main__':
    main()
