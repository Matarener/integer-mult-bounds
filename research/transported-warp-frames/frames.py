"""Construct compatible BORROW-WORD native frame changes; no solver required.

Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
import audit_core as audit


def need(ok, why):
    if not ok:
        raise ValueError(why)


def compile_frames(source, recipe):
    """Apply guarded scalar/warp frame edits and emit every needed paid climb.

    The original opcode sequence, warp matrices, operator numbering and caller
    interfaces are retained. This function checks frame legality, not phases.
    The independent full free-operator and native checks are separate gates.
    """
    w = copy.deepcopy(source)
    seen = set()
    for edit in recipe['scalar_edits']:
        section, i = edit['section'], edit['index']
        need(section in ('A', 'B', 'restore'), 'invalid scalar section')
        need((section, i) not in seen, 'duplicate scalar edit')
        seen.add((section, i))
        g = w[section][i]
        need(g[0] != 'warp' and g[-1] == edit['old'], 'scalar source guard')
        g[-1] = list(edit['new'])
    edits = {}
    for edit in recipe['warp_edits']:
        k = edit['index']
        need(k not in edits, 'duplicate warp edit')
        need(source['warps'][k][3:] == edit['old'], 'warp source guard')
        edits[k] = edit['new']

    # The independent point-set walker establishes A, centre and final legality.
    cur = {r: audit.span((p,)) for r, p in enumerate(w['ports'])}
    cur.update({r: audit.ZERO for r in range(audit.V, audit.N)})
    for r, frame in w['start_extra'].items():
        cur[int(r)] = audit.span(frame)
    for g in w['A']:
        if g[0] == 'warp':
            cur[g[1]] = audit.span(g[4])
        else:
            for r in audit.touched(g):
                cur[r] = audit.span(g[-1])
    # Centre registers descend to the last served target level before B.
    levels = {audit.V + int(t): audit.span(f) for t, f in w['target_levels'].items()}
    for r in w['centers']:
        served = {levels.get(g[1], audit.ZERO) for g in w['cut'] if g[2] == r}
        for frame in sorted(served, key=lambda f: -audit.dim(f)):
            cur[r] = frame
    at = {}
    for k, record in enumerate(source['warps']):
        at.setdefault(record[0], []).append(k)
    out = []
    for i in range(len(w['B']) + 1):
        for k in at.get(i, ()):
            old = source['warps'][k]
            entrance, exit_frame = edits.get(k, old[3:])
            u, e = audit.span(entrance), audit.span(exit_frame)
            images = audit.warp_images(old[2])
            need(audit.image_mask(images, u) == e, 'incompatible transported frame')
            need(cur[old[1]] & ~u == 0, 'warp entrance would shrink')
            if cur[old[1]] != u:
                out.append(['scale', old[1], 1, 1, list(entrance)])
            w['warps'][k] = [len(out), old[1], copy.deepcopy(old[2]),
                             list(entrance), list(exit_frame)]
            cur[old[1]] = e
        if i < len(w['B']):
            g = w['B'][i]
            out.append(g)
            for r in audit.touched(g):
                cur[r] = audit.span(g[-1])
    w['B'] = out
    w['cleanup'] = audit.derive_cleanup(w)
    audit.hygiene(w)
    profile, inventory, _, _, _ = audit.frame_bill(w, lagrangian=True)
    w['report']['local_profile'] = {str(k): v for k, v in profile.items()}
    w['report']['width_inventory'] = {str(k): v for k, v in inventory.items()}
    return w
