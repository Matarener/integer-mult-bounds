"""One-interval exact scalar exclusion. JoyboyBrian, OpenAI Codex assistance.
Apache-2.0; PR6069's accumulated-span argument is credited in PROOF.md.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
WORD_HASH = '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f'
WINDOWS = [('before', 7896, 14357, 3), ('after', 14418, 14850, 713)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode(row):
    return {str(k): str(v) for k, v in sorted(row.items()) if v}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def add(row, donor, c):
    for k, v in tuple(donor.items()):
        row[k] = row.get(k, 0) + c * v
        if not row[k]:
            del row[k]


def load_word():
    payload = (ROOT / WORD).read_bytes()
    require(sha256(payload).hexdigest() == WORD_HASH, 'Selected word source hash')
    return json.loads(gzip.decompress(payload))


def extract(word):
    """Reconstruct arbitrary-input rows and actual start/arrival donor versions."""
    program, public = word['program'], word['public']
    require(public == 770 and word['owned_fields'] == 29, 'Source dimensions')
    require(program[14357] == ['MOVE', 469, 3, 593, False], 'First MOVE')
    require(program[14380] == ['ADD', 469, 703, '2', 593], 'Interior ADD')
    require(program[14417] == ['MOVE', 469, 593, 713, False], 'Second MOVE')
    contacts = [i for i, e in enumerate(program) if e[1] == 469 or
                (e[0] in ('ADD', 'COPY') and e[2] == 469)]
    require([i for i in contacts if 7895 <= i <= 14850] ==
            [7895, 14357, 14380, 14417, 14850], 'Maximal contact-free windows')
    rows = [{r: Q(1)} for r in range(public)] + [{} for _ in range(word['owned_fields'])]
    charts = word['initial'][:] + [None] * word['owned_fields']
    generators, f, delta, target = [], None, None, None
    for slot, event in enumerate(program[:14850]):
        for side, lo, hi, frame in WINDOWS:
            if slot == lo:
                require(charts[469] == frame, 'Endpoint receiver chart')
                generators.extend((side, slot, r, dict(rows[r])) for r, chart in
                                  enumerate(charts) if chart == frame and r != 469)
            if (lo <= slot < hi and event[0] == 'MOVE' and event[3] == frame
                    and event[1] != 469):
                generators.append((side, slot + 1, event[1], dict(rows[event[1]])))
        if slot == 14357:
            f = dict(rows[469])
        if slot == 14380:
            delta = {k: 2 * v for k, v in rows[703].items()}
        op, r = event[:2]
        if op == 'MOVE':
            require(charts[r] == event[2] and event[4] == (r >= public), 'MOVE chart/ownership')
            charts[r] = event[3]
        elif op == 'INIT':
            require(r >= public and charts[r] is None, 'INIT lifetime')
            charts[r], rows[r] = event[2], {}
        elif op == 'CLEAR':
            require(r >= public and charts[r] == event[2], 'CLEAR lifetime')
            charts[r], rows[r] = None, {}
        else:
            c, chart = Q(event[-2]), event[-1]
            require(c and charts[r] == chart and chart is not None, 'Scalar destination')
            if op == 'SCALE':
                rows[r] = {k: c * v for k, v in rows[r].items()}
            else:
                require(op in ('ADD', 'COPY') and event[2] != r and
                        charts[event[2]] == chart, 'Scalar donor chart')
                require(op != 'COPY' or (r >= public and not rows[r]), 'COPY zero lifetime')
                add(rows[r], rows[event[2]], c)
        if slot == 14417:
            target = dict(rows[469])
    expected = dict(f)
    add(expected, delta, Q(1))
    require(expected == target == rows[469] and charts[469] == 713, 'Full receiver restoration target')
    require(f == {469: Q(1), 537: Q(1, 2)}, 'Receiver entry arbitrary-input row')
    return f, delta, generators


def certificate(word):
    f, delta, generators = extract(word)
    require(len(generators) == 569, 'Generator inventory')
    require(f.get(1, 0) == 0 and all(row.get(1, 0) == 0 for *_, row in generators),
            'Separator annihilates receiver and every donor generator')
    require(delta.get(1) == Q(1, 2), 'Separator detects required restoration')
    return {
        'status': 'EXCLUDED_ALL_RATIONAL_RECEIVER_MULTIPLIERS',
        'receiver': 469, 'moves': [14357, 14417], 'interior_add': 14380,
        'windows': [{'side': s, 'slots_inclusive': [a, b], 'chart': c} for s, a, b, c in WINDOWS],
        'receiver_entry': encode(f), 'required_interior_increment': encode(delta),
        'donor_generators': {'before': sum(s == 'before' for s, *_ in generators),
                             'after': sum(s == 'after' for s, *_ in generators),
                             'timestamped_rows_sha256': digest([[s, t, r, encode(v)] for s, t, r, v in generators])},
        'separator': {'public_input': 1, 'receiver_value': '0', 'every_donor_value': '0',
                      'required_increment_value': '1/2', 'feasible_lambda_set': 'empty'},
        'full_receiver_target_checked': True,
        'word_sha256': WORD_HASH,
        'scope': 'Only receiver469 interval14357..14417, unchanged donor programs and two maximal endpoint windows; no supplier or kappa claim.'}


def main():
    result = certificate(load_word())
    require(result == json.loads((PACKAGE / 'RESULT.json').read_text()), 'Committed exact certificate')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
