#!/usr/bin/env python3
"""Full independent-input rows for the actual raw provider observation channel.

Native event/chart semantics adapted from Dillon Amburgey's canonical
native-rank8-helper-provider/verify.py; free-word observation question credited
to Mark/Matarener #5427 and THU New Media Research Center #5447.
New enlarged-channel witness and checks: JoyboyBrian, substantial OpenAI Codex
assistance. Apache-2.0. No numerical operator independence is assumed.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inputs():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    data = {}
    for pin in manifest['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT/pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source drift '+pin['path'])
        data[Path(pin['path']).name] = json.loads(gzip.decompress(raw) if pin['path'].endswith('.gz') else raw)
    return data


def address(ref):
    need(ref[0] in ('L', 'C'), 'role kind')
    n = ref[1] + (632 if ref[0] == 'C' else 0)
    need(0 <= n < 641, 'role range')
    return n


def plus(row, other, factor=F(1)):
    for key, value in tuple(other.items()):
        value = row.get(key, F()) + factor*value
        if value:
            row[key] = value
        else:
            row.pop(key, None)


def replay(canon, events):
    rows = [{(j, ()): F(1)} for j in range(641)]
    frames = list(canon['start'])+[None]*9
    full = {j for j, vectors in enumerate(canon['frames']) if len(vectors) == 9}
    need(full == {1} and not any(f in full for f in frames), 'full-frame entrance convention')
    histories, seen = [], set()
    touches = 0
    cleared_dirt = set()
    for event, e in enumerate(events):
        kind, touched = e[0], None
        if kind == 'scalar':
            op, frame = e[1:]
            dst = address(op[1]); touched = dst
            if op[0] == 'clear':
                need(dst >= 632, 'no persistent clear')
                if any(j >= 632 for j, word in rows[dst]):
                    cleared_dirt.add(dst)
                rows[dst], frames[dst] = {}, frame
            elif op[0] in ('add', 'copy'):
                src = address(op[2])
                need(frames[src] == frame, 'source frame')
                if op[0] == 'copy':
                    need(dst >= 632 and not rows[dst], 'copy into owned zero')
                    rows[dst], frames[dst] = dict(rows[src]), frame
                else:
                    need(frames[dst] == frame and dst != src, 'ADD frame and alias')
                    plus(rows[dst], rows[src], F(op[3], op[4]))
            else:
                need(op[0] == 'scale' and frames[dst] == frame, 'scale frame')
                q = F(op[2], op[3])
                rows[dst] = {key: q*v for key, v in rows[dst].items() if q*v}
        elif kind == 'warp':
            _, ref, op, old, new = e
            dst = address(ref); touched = dst
            need(frames[dst] == old and op, 'warp frame/symbol')
            out = {}
            for (j, word), q in rows[dst].items():
                reduced = word[1:] if word and word[0] == -op else (op,)+word
                plus(out, {(j, reduced): q})
            rows[dst], frames[dst] = out, new
        elif kind in ('climb', 'center'):
            if kind == 'climb':
                _, _, dst, old, new, rank = e
                expected = len(canon['frames'][new])-len(canon['frames'][old])
            else:
                _, slot, old, new, rank = e
                dst = 632+slot
                expected = abs(len(canon['frames'][new])-len(canon['frames'][old]))
            need(frames[dst] == old and rank == expected and rank > 0, 'paid chart transition')
            frames[dst], touched = new, dst
        elif kind == 'zero_retag':
            _, dst, old, new = e
            need(frames[dst] == old and not rows[dst], 'exact-zero retag')
            frames[dst], touched = new, dst
        else:
            need(kind in ('phase', 'adapter'), 'unknown event')
        if touched is not None and frames[touched] in full:
            touches += 1
            if rows[touched]:
                key = frozenset(rows[touched].items())
                if key not in seen:
                    seen.add(key)
                    histories.append((event, touched, dict(rows[touched])))
    need(cleared_dirt == set(range(632, 641)), 'all nine arbitrary owned inputs cleared')
    need(not any(j >= 632 for row in rows for j, word in row), 'owned dirt absent at exit')
    return histories, rows, frames, touches


def residual(row, displacement):
    out = {}
    for (owner, word), value in row.items():
        q = value*displacement.get(owner, F())
        if q:
            plus(out, {word: q})
    return out


def scalar_combine(coefficients, rows, offset):
    out = {}
    for j, c in coefficients:
        plus(out, rows[offset+j], F(c))
    return out


def table(word):
    """Literal phase-aware monomial action, adapted from zxv's consumer checker."""
    out = []
    for x in range(512):
        y, phase = x, 0
        for g in word:
            if g[0] == 'P':
                y = sum(((r & y).bit_count() % 2) << j for j, r in enumerate(g[1]))
            elif g[0] == 'D':
                phase += sum(c for j, c in enumerate(g[2]) if y >> j & 1)
                phase += 2*sum(((g[1][j] >> (j+1)) & (y >> (j+1))).bit_count() % 2
                               for j in range(9) if y >> j & 1)
            elif g[0] == 'X':
                y ^= g[1]
            else:
                need(g[0] == 'phase', 'monomial instruction')
                phase += g[1]
        out.append((y, phase % 4))
    need(len({y for y, phase in out}) == 512, 'monomial invertible')
    return out


def verify():
    data = inputs()
    canon = data['ACTUAL-WORD.json.gz']['canonical']
    program = data['WORD.json.gz']['word']
    provider, normal = data['PROVIDER.json'], data['NORMALIZERS.json']
    kernel = json.loads((HERE/'KERNEL.json').read_text())
    displacement = {j: F(c) for j, c in kernel['original_input_displacement']}
    need(len(displacement) == len(kernel['original_input_displacement']) == 104,
         'unique nonzero 104-role witness')
    need(all(0 <= j < 632 and c for j, c in displacement.items()), 'original input domain')
    histories, rows, frames, touches = replay(canon, program)
    need(len(histories) == 4891, 'complete distinct full-frame history')
    need(all(not residual(row, displacement) for _, _, row in histories), 'full-frame witness kernel')
    need(all(rows[j] and len(canon['frames'][frames[j]]) == 8 for j in range(633, 641)),
         'all eight nonzero partial-frame caches included')
    need(all(not residual(rows[j], displacement) for j in range(633, 641)), 'endpoint cache kernel')
    m = normal['mode_columns']
    e = provider['canonical_retraction_E']
    image = [sum(F(c)*displacement.get(112+j, F()) for j, c in enumerate(row)) for row in m]
    need(image == [F(0), F(-4), *([F(0)]*6)], 'nonzero one-mode target image')
    helper_image = [sum(F(c)*displacement.get(224+j, F()) for j, c in row) for row in e]
    need(helper_image == image, 'original-helper compensation')
    for record in provider['mode_boundaries']:
        k, slot = record['mode'], record['cache_slot']
        factor = 1/(2*F(record['cache_scalar']))
        expected = {(j+224, ()): factor*F(c) for j, c in e[k]}
        plus(expected, {(j+112, ()): -factor*F(c) for j, c in enumerate(m[k]) if c})
        need(rows[slot] == expected and frames[slot] == record['frame'], 'complete cache formula/version')
    need(all(not scalar_combine(row, rows, 224) for row in e), 'current helper retraction is zero')

    # Exact physical input binding; no cost-free execution of these maps claimed.
    for port in normal['ports']:
        need(table(port['K_word']) == table(port['compiled_wrappers']['backward_input_Y']['word']),
             'BY equals Kp with absolute phase')
    controls = {}
    for name, mutant in [('helpers-frozen', {j:c for j,c in displacement.items() if j < 224}),
                         ('X-compensator-missing', {j:c for j,c in displacement.items() if j >= 112})]:
        failures = [event for event, _, row in histories if residual(row, mutant)]
        need(failures, 'control failed '+name)
        controls[name] = {'full_frame_failures': len(failures), 'first_event': failures[0]}
    # Each newly included cache defeats one old fixed-helper X=Y kernel direction.
    sensitivities = []
    for k in range(8):
        old = {j: F(m[k][j % 112]) for j in range(224) if m[k][j % 112]}
        need(all(not residual(row, old) for _, _, row in histories), 'old full-frame kernel')
        leaking = [r['mode'] for r in provider['mode_boundaries'] if residual(rows[r['cache_slot']], old)]
        need(leaking == [k], 'each cache contributes its specified new information')
        sensitivities.append(leaking)
    # Original helper modes reveal the ambiguity; post-word modes do not.
    need(helper_image[1] == -4 and not residual(scalar_combine(e[1], rows, 224), displacement),
         'stale helper version control')
    changed = list(normal['ports'][0]['compiled_wrappers']['backward_input_Y']['word'])+[['phase', 2]]
    need(table(changed) != table(normal['ports'][0]['K_word']), 'physical phase control')
    need(all(not residual(row, {}) for _, _, row in histories) and not any(
        sum(F(c)*{}.get(112+j, F()) for j, c in enumerate(row)) for row in m),
        'zero kernel cannot establish target ambiguity')
    return {'status': 'PASS_PARTIAL_CACHE_HISTORY_OBSERVER_KERNEL',
            'events': len(program), 'full_frame_touches_including_zero': touches,
            'distinct_nonzero_full_frame_histories': len(histories),
            'free_word_history_terms': sum(len(row) for _, _, row in histories),
            'cache_slots': list(range(633, 641)), 'cache_frames': frames[633:641],
            'witness_nonzero_original_roles': len(displacement),
            'raw_target_image': [str(x) for x in image],
            'original_helper_retraction_image': [str(x) for x in helper_image],
            'current_helper_retraction_is_zero': True,
            'phase_bound_Y_wrappers': 112, 'owned_inputs_cleared': 9,
            'negative_controls': controls, 'old_kernel_cache_sensitivities': sensitivities,
            'physical_target_mode1': '-2 Km_1^-1 R applied to arbitrary displacement field',
            'scope': 'all-width coefficientwise witness; no claim about whole machine state or new observations'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = verify()
    if not args.emit:
        need(json.dumps(result, sort_keys=True) == json.dumps(json.loads((HERE/'RESULT.json').read_text()), sort_keys=True), 'typed receipt mismatch')
    print(json.dumps(result, sort_keys=True, indent=2))
