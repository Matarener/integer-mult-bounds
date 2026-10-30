"""Check the exact scalar edit and its unchanged recursive invoice.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def plus(dst, src, coefficient):
    for k, value in src.items():
        value = dst.get(k, Q(0)) + coefficient * value
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)


def scalar(value):
    q = Q(value)
    need(q.denominator & (q.denominator - 1) == 0, 'Non-dyadic coefficient')
    return q


def source():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    pin = manifest['source_word']
    raw = (HERE / pin['local_path']).read_bytes()
    need(sha256(raw).hexdigest() == pin['sha256'], 'Source bytes')
    need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob'], 'Source Git blob')
    return json.loads(gzip.decompress(raw))


def construct(original, certificate, check_stages=False):
    word = deepcopy(original)
    for stage in certificate['stages']:
        need(digest(word) == stage['source_sha256'], 'Stage input')
        p = word['program']
        for edit in stage['edits']:
            for change in edit['changes']:
                i = change['index']
                need(p[i] == change['before'] and p[i][0] == 'ADD', 'Edit guard')
                scalar(change['coefficient'])
                p[i][-2] = change['coefficient']
        p = [e for e in p if not (e[0] == 'ADD' and Q(e[-2]) == 0)]
        omit = set()
        for lifetime in stage['unused_lifetimes']:
            r, a, b = lifetime['role'], lifetime['start'], lifetime['end']
            need(r >= word['public'], 'Owned lifetime')
            need(p[a][0:2] == ['INIT', r] and p[b][0:2] == ['CLEAR', r], 'Lifetime limits')
            need(not any(e[0] in ('INIT', 'CLEAR') and e[1] == r for e in p[a + 1:b]), 'Single lifetime')
            need(not any(e[0] in ('ADD', 'COPY') and e[2] == r for e in p[a:b + 1]), 'No lifetime read')
            events = [[i, p[i]] for i in range(a, b + 1) if p[i][1] == r]
            need(events == lifetime['events'], 'Lifetime events')
            need(all(e[0] != 'MOVE' for _, e in events), 'No removed native map')
            omit.update(i for i, _ in events)
        word['program'] = [e for i, e in enumerate(p) if i not in omit]
        need(digest(word) == stage['result_sha256'], 'Stage output')
        if check_stages:
            forward(word)
    need(digest(word) == certificate['final_word_sha256'], 'Final word')
    return word


def forward(word, check_example=False):
    public = word['public']
    n = public + word['owned_fields']
    spaces = []
    for frame in word['frames']:
        space = {0}
        for v in frame:
            need(0 < v < 512 and v not in space, 'Independent frame basis')
            space |= {x ^ v for x in tuple(space)}
        spaces.append(space)
    rows = [{r: Q(1)} for r in range(n)]
    frames = word['initial'][:] + [None] * word['owned_fields']
    active = set()
    peak = 0
    lifetimes = 0
    paid = Counter()
    example = {}
    example_weights = {14603: Q(1), 18890: Q(-1), 17482: Q(1), 17483: Q(1), 17484: Q(-1, 2)}
    for index, e in enumerate(word['program']):
        if check_example and index in example_weights:
            example[index] = rows[e[2]].copy()
        op, r = e[:2]
        need(0 <= r < n, 'Register range')
        if op == 'INIT':
            need(r >= public and frames[r] is None, 'Owned initialization')
            rows[r] = {}
            frames[r] = e[2]
            active.add(r)
            lifetimes += 1
            peak = max(peak, len(active))
        elif op == 'CLEAR':
            need(r in active and frames[r] == e[2], 'Owned erasure')
            rows[r] = {}
            frames[r] = None
            active.remove(r)
        elif op == 'MOVE':
            _, _, a, b, owned = e
            need(frames[r] == a and bool(owned) == (r >= public), 'Native source and owner')
            lo, hi = (b, a) if owned else (a, b)
            need(spaces[lo] < spaces[hi], 'Strict native inclusion')
            paid[len(word['frames'][hi]) - len(word['frames'][lo])] += 1
            frames[r] = b
        elif op in ('ADD', 'COPY'):
            _, _, s, q, f = e
            need(0 <= s < n and r != s and frames[r] == frames[s] == f, 'Scalar contact frame')
            q = scalar(q)
            need(q != 0, 'No zero ADD in emitted word')
            if op == 'COPY':
                need(r in active and not rows[r], 'Zero owned copy target')
            plus(rows[r], rows[s], q)
        else:
            need(op == 'SCALE' and frames[r] == e[-1], 'Scalar opcode and frame')
            q = scalar(e[-2])
            need(q != 0, 'Nonzero scale')
            rows[r] = {k: q * v for k, v in rows[r].items()}
    need(not active and frames[:public] == word['final'], 'All terminal frames')
    expected = [{r: Q(1)} for r in range(public)] + [{} for _ in range(n - public)]
    for r in word['live']:
        expected[r + 112][r] = Q(1)
    need(rows == expected, 'All 799 input columns at the complete endpoint')
    if check_example:
        relation = {}
        for i, q in example_weights.items():
            plus(relation, example[i], q)
        need(not relation, 'Written five-gate row relation')
    main = set(word['live']) | {r + 112 for r in word['live']}
    targets = Counter(len(word['frames'][b]) - len(word['frames'][a]) for r, (a, b) in enumerate(zip(word['initial'], word['final'])) if r not in main)
    return {'events': dict(sorted(Counter(e[0] for e in word['program']).items())), 'paid': dict(sorted(paid.items())), 'helpers': dict(sorted(targets.items())), 'owned_lifetimes': lifetimes, 'peak_owned': peak}


def transpose(word, check_example=False):
    public = word['public']
    n = public + word['owned_fields']
    columns = [{r: Q(1)} if r < public else {} for r in range(n)]
    example = []
    for index in range(len(word['program']) - 1, -1, -1):
        e = word['program'][index]
        op, r = e[:2]
        if check_example and index in (14603, 18890, 17482, 17483, 17484):
            example.append(columns[r].copy())
        if op == 'ADD':
            plus(columns[e[2]], columns[r], Q(e[-2]))
        elif op == 'COPY':
            plus(columns[e[2]], columns[r], Q(e[-2]))
            columns[r] = {}
        elif op == 'SCALE':
            columns[r] = {k: Q(e[-2]) * v for k, v in columns[r].items()}
        elif op in ('INIT', 'CLEAR'):
            columns[r] = {}
    expected = [{r: Q(1)} if r < public else {} for r in range(n)]
    for r in word['live']:
        expected[r][r + 112] = Q(1)
    need(columns == expected, 'Separate all-column transpose')
    if check_example:
        need(len(example) == 5 and all(c == example[0] for c in example), 'Written five-gate response columns')


def same_invoice(old, new, a, b):
    need({k: v for k, v in old.items() if k != 'program'} == {k: v for k, v in new.items() if k != 'program'}, 'All boundary data')
    need([e for e in old['program'] if e[0] == 'MOVE'] == [e for e in new['program'] if e[0] == 'MOVE'], 'Identical native event stream')
    need(a['paid'] == b['paid'] and a['helpers'] == b['helpers'], 'Identical signed recursive profiles')


def feedback_fixture():
    # Only z is observed in this two-input fixture.
    def endpoint(qs):
        x, z = [Q(1), Q(0)], [Q(0), Q(1)]
        z = [a + qs[0] * b for a, b in zip(z, x)]
        x = [a + qs[1] * b for a, b in zip(x, z)]
        return [a + qs[2] * b for a, b in zip(z, x)]
    q = [Q(1), Q(2), Q(1)]
    b, c = [Q(-3), Q(-6), Q(3)], [Q(3), Q(1), Q(1)]
    m = [[Q(0)] * 3, [Q(1), Q(0), Q(0)], [Q(2), Q(1), Q(0)]]
    delta = [b[j] / (c[j] + sum(b[i] * m[i][j] for i in range(j + 1, 3))) for j in range(3)]
    corrected = [x + y for x, y in zip(q, delta)]
    need(corrected == [0, Q(1, 2), 4], 'Feedback coefficients')
    need(endpoint(q) == endpoint(corrected) == [4, 3], 'Exact feedback endpoint')
    need(endpoint([q[j] + b[j] / c[j] for j in range(3)]) != endpoint(q), 'Omitted feedback control')


def rejects(fn, label):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('Control accepted: ' + label)


def main():
    old = source()
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())
    new = construct(old, certificate, check_stages=True)
    a, b = forward(old, check_example=True), forward(new)
    transpose(old, check_example=True)
    transpose(new)
    same_invoice(old, new, a, b)
    feedback_fixture()
    controls = []
    bad = deepcopy(certificate)
    bad['stages'][0]['edits'][0]['changes'][0]['before'][-2] = '17'
    controls.append(rejects(lambda: construct(old, bad), 'wrong edit source'))
    bad_word = deepcopy(new)
    next(e for e in reversed(bad_word['program']) if e[0] == 'ADD')[-2] = '17'
    controls.append(rejects(lambda: forward(bad_word), 'changed endpoint coefficient'))
    bad_word = deepcopy(new)
    bad_word['program'].remove(next(e for e in bad_word['program'] if e[0] == 'MOVE'))
    controls.append(rejects(lambda: same_invoice(old, bad_word, a, b), 'missing native job'))
    bad_word = deepcopy(new)
    next(e for e in bad_word['program'] if e[0] == 'ADD')[-1] = 127
    controls.append(rejects(lambda: forward(bad_word), 'wrong contact frame'))
    bad = deepcopy(certificate)
    bad['stages'][0]['unused_lifetimes'][0]['role'] = 0
    controls.append(rejects(lambda: construct(old, bad), 'public erasure'))
    result = {'schema': 1, 'source_head': '5ec9b6dafc1ec54e2c0ca0771e8ed032f7888417', 'old': a, 'new': b, 'old_events': len(old['program']), 'new_events': len(new['program']), 'all_input_columns': 799, 'separate_transpose': True, 'native_stream_identical': True, 'complete_recursive_invoice_change': 0, 'new_kappa': False, 'final_word_sha256': digest(new), 'feedback_fixture': 'PASS', 'rejection_controls': controls}
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if sys.argv[1:] == ['--write-result']:
        (HERE / 'RESULT.json').write_text(text)
    else:
        need(not sys.argv[1:], 'No unknown argument')
        need(json.loads((HERE / 'RESULT.json').read_text()) == json.loads(text), 'Committed receipt')
    print('PASS_P104_COMMON_RESPONSE_RESYNTHESIS_NO_KAPPA')
    print(json.dumps({'events_removed': len(old['program']) - len(new['program']), 'native_stream_identical': True, 'new_kappa': False}, sort_keys=True))


if __name__ == '__main__':
    main()
