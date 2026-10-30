"""Conditional one-mode endpoint identity, not a legal native construction.

The single extra operation deliberately grants a cross-frame transfer.  All
other source operations retain their literal scalar frame checks.  No source
scientific code is imported and no paid/native or caller replay is run.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import gzip, json, time

HERE = Path(__file__).resolve().parent
WP = CP = RP = None
WORD_SHA = '934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775'
R_SHA = '7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1'
CENTER_SHA = '5f2439d2f724f9f6fc6766bd74cd0885e923a0f8f3736d1eff6873c68d99279a'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def add(a, b, coefficient):
    out = dict(a)
    for k, v in b.items():
        v = out.get(k, F(0)) + coefficient*v
        if v:
            out[k] = v
        else:
            out.pop(k, None)
    return out

def index(ref):
    return ref[1] + (632 if ref[0] == 'C' else 0)

def scalar_contact(source_frame, destination_frame, claimed_frame):
    need(source_frame == destination_frame == claimed_frame, 'Literal scalar coframing')

def main():
    began = time.monotonic()
    need(sha256(WP.read_bytes()).hexdigest() == WORD_SHA, 'Frozen source WORD')
    need(sha256(RP.read_bytes()).hexdigest() == R_SHA, 'Frozen R source')
    need(sha256(CP.read_bytes()).hexdigest() == CENTER_SHA, 'Frozen mode5 suffix receipt')
    w = json.loads(gzip.decompress(WP.read_bytes()))
    center = json.loads(CP.read_bytes())
    R = [[F(x) for x in row] for row in json.loads(RP.read_bytes())]
    S = {int(i): F(c) for i, c in center['capture']['helper_terms']}
    mode = {112+i: a/4 for i, a in enumerate(R[5]) if a}
    es = w['programs']['backward']
    cut = 17978
    need(es[cut] == ['climb', 'scalar_refactor', 240, 280, 1, 1], 'Bound frozen cut')
    need(len(S) == 48 and len(mode) == 56 and S[240] == 1, 'Source mode/support inventory')
    need(es[511] == ['scalar', ['clear', ['C', 6]], 0], 'Exact owned mode capture start')
    capture = [['scalar', ['add', ['C', 6], ['L', i], a.numerator, a.denominator], 0]
               for i, a in sorted(mode.items())]
    need(es[512:568] == capture, 'Exact 56-term R5Y/4 source capture')
    precomp = [['scalar', ['add', ['L', i], ['C', 6], (-a).numerator, (-a).denominator], 0]
               for i, a in sorted(S.items())]
    need(es[568:616] == precomp, 'Exact existing 48-helper mode5 precompensation')
    need(not any(e[0] == 'warp' for e in es[cut+1:]), 'No downstream warp events')
    for i in S:
        need(w['canonical']['start'][i] == 0 and w['canonical']['final'][i] == 1,
             'All helper compensation sources start ground and end full')

    oracle_frames = []

    def replay(omit_precomp, injection):
        n = 633+w['owned_extra_slots_by_direction']['backward']
        rows = [{i: F(1)} for i in range(632)] + [{} for _ in range(n-632)]
        cur = w['canonical']['start'][:] + [None]*(n-632)
        for p, e in enumerate(es):
            if p == cut:
                need(rows[638] == mode and cur[638] == 0 and cur[240] == 280,
                     'Actual captured mode persists, but is NOT coframed with L240')
                oracle_frames.append((cur[638], cur[240]))
                # Deliberately nonphysical oracle operation.  It is the sole
                # relaxed premise of this endpoint calculation.
                rows[240] = add(rows[240], rows[638], F(injection))
            if omit_precomp and 568 <= p < 616:
                continue
            typ = e[0]
            if typ == 'physical_add':
                continue
            if typ == 'scalar':
                a, f = e[1:]
                d = index(a[1])
                if a[0] == 'clear':
                    need(d >= 632, 'No arbitrary-input erasure')
                    rows[d] = {}; cur[d] = f
                elif a[0] in ('copy', 'add'):
                    s = index(a[2])
                    scalar_contact(cur[s], cur[d], f)
                    if a[0] == 'copy':
                        need(d >= 632, 'No arbitrary-input overwrite')
                        rows[d] = dict(rows[s])
                    else:
                        need(d != s, 'Nonaliasing source ADD')
                        rows[d] = add(rows[d], rows[s], F(a[3], a[4]))
                else:
                    need(a[0] == 'scale' and cur[d] == f, 'Source scale contact')
                    factor = F(a[2], a[3])
                    rows[d] = {i: v*factor for i, v in rows[d].items() if v*factor}
            elif typ in ('warp', 'climb'):
                d = index(e[1]) if typ == 'warp' else e[2]
                need(cur[d] == e[3], 'Source transport entrance')
                cur[d] = e[4]
            else:
                need(typ in ('phase', 'adapter'), 'Known source metadata')
            need(time.monotonic()-began < 45, 'Bounded exact scalar replay')
        need(cur[:632] == w['canonical']['final'], 'All final public frames')
        need(all(not r for r in rows[632:]), 'All owned scratch restored to zero')
        return rows[:632]

    baseline = replay(False, 0)
    candidate = replay(True, -1)
    expected = []
    for i in range(632):
        row = {i: F(1)}
        if i < 112:
            row[i+112] = F(-1)
            for r in R:
                row = add(row, {112+j: a/4 for j, a in enumerate(r) if a}, r[i])
        need(baseline[i] == row, 'Every baseline arbitrary-input endpoint verified')
        wanted = add(row, mode, -R[5][i]) if i < 112 else row
        need(candidate[i] == wanted, 'Every conditional endpoint equals one-mode repaired target')
        expected.append(wanted)
    dirty = replay(False, -1)
    wrong_sign = replay(True, 1)
    need(any(dirty[i] != expected[i] for i in range(224, 632)), 'Uncompensated dirty-helper mutant rejected')
    need(any(wrong_sign[i] != expected[i] for i in range(112)), 'Wrong mode-injection sign mutant rejected')
    # The advertised oracle operation itself fails the literal source ABI.
    try:
        scalar_contact(0, 280, 280)
    except ValueError:
        pass
    else:
        raise ValueError('Illegal oracle ADD passed the ordinary scalar contact validator')
    out = {
        'status': 'PASS_CONDITIONAL_ONE_MODE_SCALAR_ENDPOINT_IDENTITY',
        'source_sha256': WORD_SHA, 'R_sha256': R_SHA,
        'center_suffix_sha256': sha256(CP.read_bytes()).hexdigest(),
        'word_cut_before': cut, 'original_cut_before': 17155,
        'owned_mode_capture_events_inclusive': [511, 567],
        'omitted_helper_precompensation_events_inclusive': [568, 615],
        'oracle_operation': 'L240 -= C6, where C6=R5Y/4',
        'oracle_source_frame': 0, 'oracle_destination_frame': 280,
        'oracle_destination_rank': 8, 'literal_coframing': False,
        'all632_arbitrary_input_columns': True, 'all408_helpers_identity': True,
        'all_owned_scratch_zero': True, 'all_public_final_frames': True,
        'endpoint_main': 'X-A*Y-(R5^T*R5*Y)/4',
        'endpoint_Y': 'Y', 'endpoint_helpers': 'H',
        'downstream_warp_events': 0,
        'physical_suffix_scope': 'A field already delivered to full frame1 after the selected climb propagates by the displayed scalar impulse. The chosen input payload must be supplied in frame280 with the required transported value.',
        'controls': {'uncompensated_helper_mutant_rejected': True,
                     'wrong_injection_sign_mutant_rejected': True,
                     'literal_cross_frame_ADD_rejected': True},
        'claim_limits': 'Conditional scalar identity only. No legal cross-frame transfer, physical source availability, query-cost saving, compiler/caller certificate or new bound is claimed.',
        'elapsed_seconds': time.monotonic()-began}
    (HERE/'direct-l240-repair.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
