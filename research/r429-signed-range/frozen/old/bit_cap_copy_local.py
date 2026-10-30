#!/usr/bin/env python3
"""Local-only exact native cap-copy audit, independent of any controller.

Inputs are the pinned R438 word and frozen signed six-copy local word.  The
16-column ADDRESS identities hold over every odd field where dyadic entries
are interpreted.  Scalar integer cleanup and rounded child errors are separate.
Apache-2.0; substantial OpenAI Codex assistance.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = Path('/Users/ross/git/math/integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz')
RAW_SHA = 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def rank(rows):
    basis = {}
    for row in rows:
        row = list(map(Q, row))
        for j, old in sorted(basis.items()):
            c = row[j]
            row = [x-c*y for x,y in zip(row,old)]
        j = next((j for j,x in enumerate(row) if x), None)
        if j is not None:
            c = row[j]
            basis[j] = [x/c for x in row]
    return len(basis)


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]


def exchange(u):
    c = [[Q(i == j)-u[i][j] for j in range(8)] for i in range(8)]
    return [c[i]+u[i] for i in range(8)]+[u[i]+c[i] for i in range(8)]


def address_identities(word):
    ident = identity(8)
    out = []
    for p, q in enumerate(word['lines']):
        need(sum(x*x for x in q) == 4, 'actual E8 root norm')
        start = [word['lines'][j] for j in word['frames'][word['start'][p]]]
        cap = [word['lines'][j] for j in word['frames'][word['final'][111+p]]]
        need(rank(start) == 1 and all(all(4*x == sum(a*b for a,b in zip(row,q))*y
             for x,y in zip(row,q)) for row in start), 'actual entrance is not P_p')
        need(rank(cap) == 7 and all(sum(x*y for x,y in zip(row,q)) == 0 for row in cap),
             'actual target cap is not K_p')
        proj = [[Q(x*y,4) for y in q] for x in q]
        complement = [[ident[i][j]-proj[i][j] for j in range(8)] for i in range(8)]
        need(multiply(proj,proj) == proj and rank(proj) == 1, 'actual P_p projector')
        need(multiply(exchange(ident),exchange(proj)) == exchange(complement),
             'D_I D_P differs from D_K')
        need(multiply(exchange(proj),exchange(proj)) == identity(16), 'D_P squared differs from I')
        encoded = [[[v.numerator,v.denominator] for v in row] for row in proj]
        out.append(sha256(canonical(encoded)).hexdigest())
    need(len(out) == 111, 'actual punctured root count')
    return out


def frame_replay(word, program, backward=False, fault=None):
    dims = [rank(word['lines'][j] for j in f) for f in word['frames']]
    masks = [sum(1 << j for j in f) for f in word['frames']]
    need(dims[1] == 8, 'named FULL is not full')
    frames = (word['final'] if backward else word['start'])[:]+[None]
    open_source, copies, erases = None, [], 0
    paid = Counter()
    rows = list(reversed(program['records'])) if backward else program['records']
    for raw in rows:
        op,x,y,c,f,phase = raw
        if op == 0:
            old,new = (c,y) if backward else (y,c)
            lo,hi = (new,old) if backward else (old,new)
            need(frames[x] == old, 'MOVE source frame')
            need(not masks[lo] & ~masks[hi] and dims[hi]-dims[lo] == f > 0, 'MOVE rank or containment')
            frames[x] = new
            paid[f] += 1
        elif op == 1:
            need(x < 660 and x != y and frames[x] == frames[y] == f, 'ADD common frame')
            need(open_source != x, 'immutable copied source changed')
        elif op == (3 if backward else 2):
            need(open_source is None and y == 660 and frames[660] is None, 'COPY fresh private field')
            if fault == 'copy_to_full':
                f = 1
            need(frames[x] == c == 1 and not masks[f] & ~masks[c], 'COPY source FULL and target nested')
            need(dims[c]-dims[f] == 1, 'COPY does not use rank-one cap descent')
            frames[660],open_source = f,x
            copies.append({'source':x,'source_frame':c,'private_frame':f,'rank':1})
            paid[1] += 1
        else:
            need(op == (2 if backward else 3), 'unknown native opcode')
            need(open_source == x and y == 660 and frames[x] == c and frames[660] == f,
                 'ERASE original snapshot source/frame')
            frames[660],open_source = None,None
            erases += 1
    need(open_source is None and frames[:660] == (word['start'] if backward else word['final']), 'native endpoint')
    need(len(copies) == erases == 6, 'six closed immutable snapshots')
    return {'copies':copies,'literal_erases':erases,'paid_profile':dict(sorted(paid.items())),
            'maximum_simultaneous_private_snapshots':1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    raw = RAW.read_bytes()
    need(sha256(raw).hexdigest() == RAW_SHA, 'R438 source pin')
    word = json.loads(gzip.decompress(raw))
    meta = json.loads((HERE/'BIT-SIGNED-INPUT.json').read_bytes())
    packed = (HERE/'BIT-SIGNED-INPUT-WORD.json.gz').read_bytes()
    decoded = gzip.decompress(packed)
    need(sha256(packed).hexdigest() == meta['word_gzip_sha256'] and
         sha256(decoded).hexdigest() == meta['word_canonical_sha256'], 'frozen signed word pin')
    program = json.loads(decoded)
    need(program['start'] == word['start'] and program['final'] == word['final'], 'retained native boundaries')
    projectors = address_identities(word)
    forward,backward = frame_replay(word,program),frame_replay(word,program,True)
    try:
        frame_replay(word,program,fault='copy_to_full')
    except ValueError as error:
        negative = str(error)
    else:
        raise ValueError('rank-zero FULL copy mutation escaped')
    receipt = {'status':'PASS_LOCAL_SIX_CAP_COPY_NATIVE_CONTRACT',
               'raw_R438_gzip_sha256':RAW_SHA,'signed_word_canonical_sha256':meta['word_canonical_sha256'],
               'actual_port_count':111,'actual_entrance_and_target_frames':222,
               'projector_sha256':projectors,'address_identity_columns':3552,
               'forward':forward,'literal_inverse':backward,'negative_control':negative,
               'domain':'Exact dyadic projectors and ADDRESS matrices; every odd modulus where their dyadic coefficients are interpreted. VALUE scalar identity and native recursive child errors are separate.',
               'source_role_rule':'COPY may read an actual source field or an arbitrary helper, provided the physical source stays unchanged until ERASE. No helper-only restriction is used.',
               'limits':['local native/frame contract only','no global controller, endpoint decoder, owner allocation, precision theorem, tape bound or kappa claim']}
    path = HERE/'BIT-CAP-COPY-LOCAL.json'
    if args.write:
        path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == json.loads(canonical(receipt)), 'complete cap-copy receipt differs')
    print(receipt['status'])


if __name__ == '__main__':
    main()
