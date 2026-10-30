# SPDX-License-Identifier: Apache-2.0
"""Bounded standard-library replay of the staged-entry census findings on PR3734's word.

1. Rebuild the helper-472 staged word on both providers from PR3734's words, compare it with the
   frozen words, and run PR3734's frame bill, hygiene and full arbitrary-dirty semantics.
2. Controls on that word: a flipped release fails the semantics; releases after 472's producer
   fail; the pure retiming of 472's early target read is scalar-correct but frame-infeasible by the
   exact minimal assignment.
3. Positive controls of the constructor: 544 on PR3734's parent word (PR3682) and 644 / 660 on
   PR3605's parent word (PR3133) give the published inventories, with exact semantics.
4. Exact dual certificate (adapted from PR3815): every owner fill of the 472 inventory has its root
   below 0.0017305031, below the parent inventory's attained ceiling 0.001730578437266246818740.
5. Authenticate the recorded census results and recompute their summaries.
The census itself (pass5/7/8, numpy/scipy) is recorded, not rerun here; replay_subset.py reruns a
subset.
"""
import gzip
import hashlib
import io
import json
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path

P = Path(__file__).resolve().parent
S = P.parent / 'staged544-producer-return'
sys.path[:0] = [str(P / 'code'), str(S)]
import audit_core as C                      # noqa: E402  (PR3734, Sagar Thakrar)
import rational_price as R                  # noqa: E402  (PR3734)
from audit_verify import semantics          # noqa: E402  (PR3734, Sagar Thakrar)
from timeline import load, events           # noqa: E402
from construct import exact_fixed           # noqa: E402
from construct2 import assemble, fill_frames  # noqa: E402
from repair import repair                   # noqa: E402
from minimal_all import minimal_all         # noqa: E402
from ceiling import certify                 # noqa: E402

BILL472 = {1: 2455, 2: 716, 3: 222, 4: 104, 5: 20, 8: 8}
WIDTH472 = {4: 26, 5: 2, 6: 18, 7: 54, 8: 95, 9: 213}
BILL3734 = {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}
WIDTH3734 = {4: 26, 5: 2, 6: 18, 7: 53, 8: 96, 9: 213}
ATTAINED = Q('0.001730578437266246818740')  # parent inventory ceiling (PR3734 PROOF.md), attained by PR3802/PR3815
CEIL472 = Q('0.0017305031')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rejects(fn):
    try:
        fn()
    except (ValueError, C.AuditFailure, Exception):
        return True
    return False


def first_write(ev, h):
    return next(e['pos'] for e in ev if e['sec'] == 'B' and e['g'][0] == 'add' and e['g'][1] == h)


def build472(w, ev, place=None, coef628=Q(-1, 2)):
    prod = first_write(ev, 472)
    place = prod if place is None else place
    ins = [(place, ['add', 624, 472, -1, 1]), (place, ['add', 628, 472, coef628.numerator, coef628.denominator])]
    x, mark = assemble(w, ev, 472, C.span((429, 51)), prod, ins)
    return repair(x, mark)[0]


def check_472():
    rows = []
    for tag in ('base', 'extra'):
        w = load(tag)
        ev = events(w)
        prod = first_write(ev, 472)
        need(ev[prod]['sec'] == 'B' and ev[prod]['idx'] == 538, 'producer of 472 is B538')
        v = {472: Q(1), 624: Q(-1), 628: Q(-1, 2)}
        need(exact_fixed(w, ev, prod, v)[0], 'exact prefix identity at the producer cut')
        x = build472(w, ev)
        frozen = load(str(P / 'words' / f'W472-{tag}.json.gz'))
        need(x == frozen, 'rebuilt 472 word equals the frozen word')
        C.hygiene(x)
        bill, widths, *_ = C.frame_bill(x)
        need(bill == BILL472 and widths == WIDTH472, 'bill and widths of the 472 word')
        need(C.frame_bill(w)[:2] == (BILL3734, WIDTH3734), 'PR3734 word bill and widths')
        sem = semantics(C, x)
        need(sem['forward'] == sem['dual'] == 'PASS', 'arbitrary-dirty semantics')
        # controls
        bad = build472(w, ev, coef628=Q(1, 2))
        need(rejects(lambda: semantics(C, bad)), 'flipped 628 release must fail the semantics')
        late = assemble(w, ev, 472, C.span((429, 51)), prod,
                        [(prod + 1, ['add', 624, 472, -1, 1]), (prod + 1, ['add', 628, 472, -1, 2])])
        late = repair(*late)[0]
        need(rejects(lambda: semantics(C, late)), 'releases after the producer must fail')
        # pure retiming of the early read 130 += 472/2: scalar-correct, frame-infeasible
        a0 = {130: Q(1, 2)}
        need(exact_fixed(w, ev, prod, {472: Q(1)})[0] is False, 'e_472 alone is not fixed')
        rt_sem, mark = assemble(w, ev, 472, C.span((429, 51)), prod, [(prod, ['add', 130, 472, 1, 2])])
        for g in mark:
            g.append(list(C.points(C.FULL)[1:2]))           # frames are irrelevant to the semantics
        rt_sem['cleanup'] = C.derive_cleanup(rt_sem)
        need(semantics(C, rt_sem)['forward'] == 'PASS', 'pure retiming is scalar-correct')

        def minimal():
            rt, mk = assemble(w, ev, 472, C.span((429, 51)), prod, [(prod, ['add', 130, 472, 1, 2])])
            y, _ = minimal_all(rt, mk)
            C.frame_bill(y)
        need(rejects(minimal), 'pure retiming is frame-infeasible (minimal assignment)')
        rows.append(dict(provider=tag, producer='B538', semantics='PASS', bill=bill, widths=widths,
                         controls=['flipped_release', 'release_after_producer', 'retiming_infeasible'],
                         retiming_release=str(a0)))
    return rows


def pre3605():
    arch = json.loads((S / 'REPLAY-INPUTS.json').read_text())
    raw = (S / 'REPLAY-INPUTS.tar.gz').read_bytes()
    need(sha(raw) == arch['archive_sha256'], 'PR3734 replay archive digest')
    name = 'source/new/borrow/inputs/PRE3605-base.json.gz'
    with tarfile.open(fileobj=io.BytesIO(raw)) as t:
        b = t.extractfile(name).read()
    need(sha(b) == arch['files'][name], 'PR3605 parent word digest in PR3734 archive')
    return json.loads(gzip.decompress(b))


def check_positive_controls():
    out = {}
    pre = load(str(S / 'staged544' / 'PRE-base.json.gz'))
    ev = events(pre)
    c247 = next(e['pos'] for e in ev if e['sec'] == 'B' and e['idx'] == 247)
    c693 = next(e['pos'] for e in ev if e['sec'] == 'B' and e['idx'] == 693)
    v = {544: Q(1), 672: Q(1, 2), 676: Q(-1, 2)}
    need(exact_fixed(pre, ev, c247, v)[0], '544 identity at cut 247')
    x, mark = assemble(pre, ev, 544, C.span((414, 51)), c247,
                       [(c693, ['add', 672, 544, 1, 2]), (c693, ['add', 676, 544, -1, 2])])
    x = fill_frames(x, mark)
    need(C.frame_bill(x)[:2] == (BILL3734, WIDTH3734), '544 rebuilt: PR3734 bill and widths')
    need(semantics(C, x)['forward'] == 'PASS', '544 rebuilt: semantics')
    out['544_on_PR3682_word'] = 'PR3734 bill and widths, semantics PASS'
    w = pre3605()
    ev = events(w)
    b0, i0, *_ = C.frame_bill(w)
    need(i0[7] == 50 and i0[8] == 99 and w['start_extra']['644'] == [30], 'PR3133 parent inventory')
    specs = {644: (10407, {496: (Q(-2), 10824), 640: (Q(2), 11304)}),
             660: (10439, {520: (Q(-2), 10874), 656: (Q(-1), 11352)})}
    for h, (cut, rel) in specs.items():
        v = {h: Q(1), **{d: q for d, (q, _) in rel.items()}}
        need(exact_fixed(w, ev, cut, v)[0], f'{h} identity')
        x, mark = assemble(w, ev, h, C.span((435, 30)), cut,
                           [(p, ['add', d, h, q.numerator, q.denominator]) for d, (q, p) in rel.items()])
        x = fill_frames(x, mark)
        bill, widths, *_ = C.frame_bill(x)
        need(widths[7] == 51 and widths[8] == 98, f'{h}: one helper 8 -> 7')
        need(semantics(C, x)['forward'] == 'PASS', f'{h}: semantics')
        out[f'{h}_on_PR3133_word'] = dict(bill=bill, widths=widths)
    return out


def check_ceiling():
    supply472 = WIDTH472
    hi = certify(R, CEIL472, supply472, BILL472)
    lo = certify(R, CEIL472 - Q(1, 10**10), supply472, BILL472)
    need(hi['dual_feasible'] and hi['lower_bound'] > 0, '472 inventory: every fill has root < 0.0017305031')
    need(not lo['lower_bound'] > 0, '472 bracket is tight to 1e-10')
    up = certify(R, ATTAINED + Q(1, 10**24), WIDTH3734, BILL3734)
    dn = certify(R, ATTAINED, WIDTH3734, BILL3734)
    need(up['dual_feasible'] and up['lower_bound'] > 0 and not dn['lower_bound'] > 0,
         'parent inventory ceiling bracket (control, equals PR3734 ideal root)')
    pert = certify(R, CEIL472, supply472, BILL472, perturb=Q(1, 10**30))
    need(not pert['dual_feasible'], 'perturbed dual must be infeasible')
    need(CEIL472 < ATTAINED, 'the 472 ceiling is below the attained parent ceiling')
    # The same comparison in PR3862's width-unit terms at its a_hi: an 8->7 unit is worth
    # (h(48)-h(3)-5h(5))/20 of idle cost; a staging pays only if its local saving exceeds that.
    a = ATTAINED + Q(1, 10**24)

    def h(r, side):
        return R.h_bounds(r, a)[side]
    price_lo = (h(48, 0) - h(3, 1) - 5 * h(5, 1)) / 20
    save472_hi = 9 * h(2, 1) + 2 * h(3, 1) - 15 * h(1, 0) - 2 * h(4, 0)    # -(15H1-9H2-2H3+2H4)
    save544_lo = 2 * h(3, 0) - 3 * h(1, 1) - h(2, 1)                         # -(3H1+H2-2H3)
    price_hi = (h(48, 1) - h(3, 0) - 5 * h(5, 0)) / 20
    need(save472_hi - price_lo < 0, '472 signature loses per width unit')
    need(save544_lo - price_hi > 0, '544 signature gains per width unit (control)')
    return dict(ceil472=str(CEIL472), attained_parent=str(ATTAINED), gap=float(ATTAINED - CEIL472),
                patterns=hi['patterns'], net_per_unit_472_at_most=float(save472_hi - price_lo),
                net_per_unit_544_at_least=float(save544_lo - price_hi))


def check_evidence():
    census = json.loads((P / 'evidence' / 'CENSUS.json').read_text())
    for name, rec in census['files'].items():
        raw = (P / 'evidence' / name).read_bytes()
        need(sha(raw) == rec['sha256'], 'evidence digest ' + name)
        rows = json.loads(gzip.decompress(raw))['results']
        st = {}
        for r in rows:
            k = r['status'] if 'kind' not in r else r['kind'] + ':' + r['status']
            st[k] = st.get(k, 0) + 1
        need(len(rows) == rec['rows'] and len({r['h'] for r in rows}) == rec['helpers'], 'row count ' + name)
        need(dict(sorted(st.items())) == rec['statuses'], 'status summary ' + name)
        need(sorted({r['h'] for r in rows if r['status'] == 'ok'}) == rec['ok_helpers'], 'feasible helpers ' + name)
        for r in rows:
            if name.startswith('RESOLVED-B') and r['status'] == 'ok':
                need(set(r['a']) == {'624', '628'}, 'the only feasible B-window construction is 472 via 624/628')
    return {k: v['statuses'] for k, v in census['files'].items()}


def main():
    need(__debug__, 'assertions enabled')
    result = dict(helper472=check_472(), positive_controls=check_positive_controls(),
                  ceiling=check_ceiling(), census=check_evidence())
    print(json.dumps(result, sort_keys=True, default=str))
    print('PASS_STAGED_ENTRY_CENSUS_NO_PROFITABLE_RAISE ceiling472<' + str(CEIL472), flush=True)


if __name__ == '__main__':
    main()
