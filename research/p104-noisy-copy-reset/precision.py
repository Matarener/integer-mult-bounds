"""Exact transfer with additive COPY and bounded reset residuals.

Adapted from PR #5819. See PRECISION-EDITS.json and inputs/prior-NOTICE.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(dst, src, q):
    for i, v in src.items():
        value = dst.get(i, F(0)) + q*v
        if value:
            dst[i] = value
        else:
            dst.pop(i, None)


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def digest(value):
    return sha256(json.dumps(encode(value), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def binary_span(basis):
    result = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in result, 'Independent frame basis')
        result |= {x ^ v for x in tuple(result)}
    return result


def ideal(word):
    public = word['public']
    n = public + word['owned_fields']
    rows = [{i:F(1)} for i in range(n)]
    norms = [F(1)] * n
    frames = list(word['initial']) + [None]*(n-public)
    spaces = [binary_span(v) for v in word['frames']]
    live = set()
    peak_live = 0
    peak = dict(value=F(1), cut=0, role=0, row={0:F(1)})
    weights = []
    erasures = []
    counts = Counter()
    stream = sha256()
    for j, event in enumerate(word['program']):
        op, r = event[:2]
        need(0 <= r < n, 'Role index')
        counts[op] += 1
        a, c = norms[r], F(1)
        if op == 'MOVE':
            _, _, start, end, private = event
            need(frames[r] == start and private == (r in live), 'Native source and owner')
            need(spaces[end] < spaces[start] if private else spaces[start] < spaces[end], 'Nested native path')
            frames[r] = end
        elif op == 'INIT':
            need(r >= public and r not in live, 'Owned INIT')
            live.add(r)
            peak_live = max(peak_live, len(live))
            rows[r] = {}
            frames[r] = event[2]
        elif op == 'CLEAR':
            need(r in live and frames[r] == event[2], 'Owned CLEAR')
            erasures.append(dict(event=j, role=r, ideal_norm=norms[r], ideal_zero=not rows[r]))
            live.remove(r)
            rows[r] = {}
            frames[r] = None
        else:
            q, frame = F(event[-2]), event[-1]
            need(q and frames[r] == frame and q.denominator & (q.denominator-1) == 0, 'Dyadic scalar destination')
            if op == 'SCALE':
                a, c = abs(q)*norms[r], abs(q)
                rows[r] = {i:q*v for i,v in rows[r].items()}
            else:
                s = event[2]
                need(0 <= s < n and s != r and frames[s] == frame, 'Coframed scalar operands')
                if op == 'COPY':
                    need(r in live and not rows[r] and q == 1, 'Exact copy into cleared owned field')
                    a, c = abs(q)*norms[s], 1 + abs(q)
                    rows[r] = dict(rows[s])
                else:
                    need(op == 'ADD', 'Known scalar opcode')
                    a, c = norms[r] + abs(q)*norms[s], 1 + abs(q)
                    add(rows[r], rows[s], q)
        norms[r] = sum(map(abs, rows[r].values()), F(0))
        weights.append((a, c))
        stream.update((str(j)+':'+str(norms[r])+';').encode())
        if norms[r] > peak['value']:
            peak = dict(value=norms[r], cut=j+1, role=r, row=dict(rows[r]))
    need(not live and frames[:public] == word['final'], 'Public and owned exits')
    active = set(word['live'])
    for r, row in enumerate(rows):
        expected = {r:F(1)} if r < public else {}
        if r-112 in active:
            expected[r-112] = F(1)
        need(row == expected, 'Complete arbitrary-input endpoint')
    return dict(n=n, public=public, events=len(word['program']), counts=dict(counts),
                peak_owned=peak_live, input_peak=peak, erasures=erasures,
                norm_stream_sha256=stream.hexdigest()), weights


def update_hash(h, event, value):
    h.update((str(event)+':'+str(value.numerator)+'/'+str(value.denominator)+';').encode())


def error_trace(word, weights, rounded):
    n = word['public'] + word['owned_fields']
    rows = [{} for _ in range(n)]
    scores = [[F(0)]*3 for _ in range(n)]
    peaks = [dict(value=F(0), cut=0, role=0) for _ in range(3)]
    witness = {}
    pairs = []
    stream = sha256()
    sites = 0
    for j, event in enumerate(word['program']):
        op, r = event[:2]
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
            scores[r] = [F(0)]*3
        elif op == 'SCALE':
            q = F(event[-2])
            rows[r] = {i:q*v for i,v in rows[r].items()}
            scores[r] = [abs(q)*v for v in scores[r]]
        elif op in ('ADD', 'COPY'):
            q = F(event[-2])
            for i, v in rows[event[2]].items():
                old = rows[r].get(i, F(0))
                value = old + q*v
                change = abs(value)-abs(old)
                scores[r][0] += change*weights[i][0]
                scores[r][1] += change*weights[i][1]
                scores[r][2] += change
                if value:
                    rows[r][i] = value
                else:
                    rows[r].pop(i, None)
        if op in rounded:
            sites += 1
            rows[r][j] = F(1)
            scores[r][0] += weights[j][0]
            scores[r][1] += weights[j][1]
            scores[r][2] += 1
        pairs.append((*scores[r][:2], j+1, r))
        stream.update((str(j)+':'+','.join(map(str,scores[r]))+';').encode())
        for k, value in enumerate(scores[r]):
            if value > peaks[k]['value']:
                peaks[k] = dict(value=value, cut=j+1, role=r)
                witness[k] = dict(rows[r])
    pareto = []
    maximum = F(-1)
    for a,b,cut,r in sorted(pairs, reverse=True):
        if b > maximum:
            pareto.append([a,b,cut,r])
            maximum = b
    final_peaks = []
    for k in range(3):
        value, r = max((scores[r][k],r) for r in range(word['public']))
        final_peaks.append(dict(value=value,cut=len(word['program']),role=r))
        witness['final'+str(k)] = dict(rows[r])
    hashes = []
    for row in rows:
        h = sha256()
        for j in sorted(row, reverse=True):
            update_hash(h,j,row[j])
        hashes.append(h.hexdigest())
    return dict(rounded=sorted(rounded), sites=sites, peaks=peaks, pareto=pareto,
                final_peaks=final_peaks, final_scores=scores,
                final_coefficient_hashes=hashes, score_stream_sha256=stream.hexdigest()), witness


def reverse_all(word, weights, rounded):
    """Transpose the word and hash every final error coefficient separately."""
    n = word['public'] + word['owned_fields']
    columns = [{i:F(1)} for i in range(n)]
    scores = [[F(0)]*3 for _ in range(n)]
    hashes = [sha256() for _ in range(n)]
    for j in reversed(range(len(word['program']))):
        event = word['program'][j]
        op,r = event[:2]
        if op in rounded:
            for i,v in columns[r].items():
                scores[i][0] += abs(v)*weights[j][0]
                scores[i][1] += abs(v)*weights[j][1]
                scores[i][2] += abs(v)
                update_hash(hashes[i],j,v)
        if op in ('INIT','CLEAR'):
            columns[r] = {}
        elif op == 'SCALE':
            q = F(event[-2])
            columns[r] = {i:q*v for i,v in columns[r].items()}
        elif op in ('ADD','COPY'):
            add(columns[event[2]], columns[r], F(event[-2]))
    return scores, [h.hexdigest() for h in hashes]


def reverse_cut(word, rounded, cut, role):
    row = {role:F(1)}
    errors = {}
    for j in reversed(range(cut)):
        event = word['program'][j]
        op,r = event[:2]
        v = row.get(r,F(0))
        if op in rounded and v:
            errors[j] = v
        if op in ('INIT','CLEAR'):
            row.pop(r,None)
        elif op == 'SCALE':
            if v:
                row[r] = v*F(event[-2])
        elif op in ('ADD','COPY'):
            if v:
                add(row, {event[2]:F(1)}, v*F(event[-2]))
    return row, errors


def execute(word, initial, errors, cut):
    values = [F(0)]*(word['public']+word['owned_fields'])
    for r,v in initial.items():
        values[r] = v
    for j, event in enumerate(word['program'][:cut]):
        op,r = event[:2]
        if op in ('INIT','CLEAR'):
            values[r] = F(0)
        elif op == 'SCALE':
            values[r] *= F(event[-2])
        elif op == 'COPY':
            values[r] += F(event[-2])*values[event[2]]
        elif op == 'ADD':
            values[r] += F(event[-2])*values[event[2]]
        values[r] += errors.get(j,F(0))
    return values
