# SPDX-License-Identifier: Apache-2.0
"""Changed T360 clock for PR3734: literal owner fill at the fixed-inventory packing ceiling,
and an exact certificate that the ceiling caps every owner fill of this inventory.

Standard library only. Checks, in order:
1. clock: inputs/ORDER.json is exactly clock.throttle(PR3734 ORDER.json), covers every call
   and keeps every replica's stage order 0..8;
2. owners: PR3734's unmodified owner_audit.py (byte-pinned) passes on the changed ORDER,
   FILL and PROFILE beside PR3734's unchanged DISPATCH, NATIVE, PLAN and TEMPLATE inputs,
   and rejects its three mutants;
3. blocknorm premise: no helper role of call (s, r) lands in owner r's pair stage_pair[s];
4. price: PR3734's rational_price.py encloses the root of the audited profile in
   PRICE.json's [root_lower, root_upper]; the root equals the ideal fixed-inventory root
   quoted by PR3734 PROOF.md and strictly exceeds PR3734's root_lower;
   ceiling_certificate.py: an exact dual over all 2551 bin patterns shows that every owner
   fill of this inventory, under any clock and any replica count, has root < root_upper;
   the recorded complete admission is bound to these inputs;
5. controls: PR3734's own clock with this FILL is rejected by the owner audit; a stage
   swap is rejected by the clock check; a shifted bracket and a moved idle child are
   rejected by the price check; the certificate does not clear root_lower and a dual
   perturbed by 1e-30 is infeasible.
"""
import gzip
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

P = Path(__file__).resolve().parent
S = P.parent / 'staged544-producer-return'
sys.path.insert(0, str(P))
import ceiling_certificate  # noqa: E402
import clock  # noqa: E402

UNCHANGED = ['DISPATCH.json', 'NATIVE-base.json.gz', 'NATIVE-extra.json.gz', 'PLAN.json.gz', 'TEMPLATE.json.gz']
STAGE_PAIR = [0, 0, 0, 1, 1, 2, 2, 3, 3]
IDEAL_DECIMAL = '0.001730578437266246818740'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def owner_audit(order_path):
    """Run PR3734's owner_audit.py, byte for byte, in a fresh directory."""
    tmp = Path(tempfile.mkdtemp(prefix='staged544-clock-'))
    try:
        (tmp / 'inputs').mkdir()
        shutil.copyfile(S / 'owner_audit.py', tmp / 'owner_audit.py')
        need((tmp / 'owner_audit.py').read_bytes() == (S / 'owner_audit.py').read_bytes(), 'audit bytes')
        for name in UNCHANGED:
            shutil.copyfile(S / 'inputs' / name, tmp / 'inputs' / name)
        shutil.copyfile(order_path, tmp / 'inputs/ORDER.json')
        for name in ('FILL.json.gz', 'PROFILE.json'):
            shutil.copyfile(P / 'inputs' / name, tmp / 'inputs' / name)
        r = subprocess.run([sys.executable, '-B', str(tmp / 'owner_audit.py')], capture_output=True, text=True)
        return r.returncode, r.stdout, r.stderr
    finally:
        shutil.rmtree(tmp)


def load_price_module():
    spec = importlib.util.spec_from_file_location('rational_price_3734', S / 'rational_price.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def root_signs(R, profile, low, high):
    signed = dict(profile)
    signed[73] = signed.get(73, 0) - 896 * 360
    return R.interval(signed, low)[1] < 0 < R.interval(signed, high)[0]


def decimal24(x):
    return '0.' + str((x.numerator * 10**24) // x.denominator).rjust(24, '0')


def main():
    need(__debug__, 'assertions enabled')
    # 1. clock
    old_order = read(S / 'inputs/ORDER.json')
    order = read(P / 'inputs/ORDER.json')
    clock.check_order(old_order)
    clock.check_order(order)
    need(clock.throttle(old_order) == order, 'changed clock is the stated rule')
    moved = sum(a != b for a, b in zip(order, old_order))
    need(moved == 727, 'moved call count')

    # 2. owners
    code, out, err = owner_audit(P / 'inputs/ORDER.json')
    need(code == 0, 'owner audit failed: ' + err[-800:])
    audit = json.loads(out)
    need(audit['positive']['status'] == 'PASS_STANDARD_LIBRARY_INDEPENDENT_LITERAL_AUDIT', 'owner audit status')
    need(audit['controls'] == ['same_call_family', 'duplicate_helper', 'unpaid_hole'], 'owner audit controls')
    profile = {int(r): n for r, n in audit['positive']['profile'].items()}
    need(profile == {int(r): n for r, n in read(P / 'inputs/PROFILE.json').items()}, 'audited profile file')

    # 3. blocknorm helper/data alias premise
    fill = read(P / 'inputs/FILL.json.gz')
    plan = read(S / 'inputs/PLAN.json.gz')
    pairs = {int(c): v for c, v in plan['pairs'].items()}
    sides = {int(c): v for c, v in plan['sides'].items()}
    template = read(S / 'inputs/TEMPLATE.json.gz')
    recipe = {x['stage']: x['pair'] for x in template['recipe'] if x['kind'] == 'local'}
    need([recipe[s] for s in range(9)] == STAGE_PAIR, 'recipe stage pairs')
    alias = 0
    for t, h, o, c, p, z in fill['rows']:
        s, r = order[t]
        alias += (896 * o + (2 * pairs[c] + sides[c]) * 112 + p) // 224 == 4 * r + STAGE_PAIR[s]
    need(alias == 0, 'helper/data alias')

    # 4. price
    R = load_price_module()
    price = read(P / 'PRICE.json')
    need({int(r): n for r, n in price['profile'].items()} == profile, 'priced profile is the audited profile')
    low, high = Q(price['root_lower']), Q(price['root_upper'])
    need(high - low == Q(1, 10**24) and root_signs(R, profile, low, high), 'exact root enclosure')
    need(decimal24(low) == price['lower_decimal'] == IDEAL_DECIMAL, 'root decimal')
    need(('ideal fixed-inventory packing root' + IDEAL_DECIMAL) in (S / 'PROOF.md').read_text(), 'PR3734 ideal root quote')
    old = Q(read(S / 'PRICE.json')['root_lower'])
    need(low > old and low - old == Q(price['gain_lower_over_predecessor']), 'strict gain over PR3734 root_lower')

    # 4a. ceiling: every owner fill of this inventory (any clock, any replica count) has root < root_upper
    cert = ceiling_certificate.certify(R, high)
    need(cert['patterns'] == 2551 and cert['dual_feasible'] and cert['lower_bound'] > 0, 'fixed-inventory ceiling certificate')
    idle_ideal = {1: 234, 3: Q(324, 5), 5: 12, 48: Q(1916, 5)}    # per owner replica
    need({int(r): Q(n, 360) for r, n in audit['positive']['idle'].items()} == idle_ideal, 'ideal idle histogram')

    # 4b. recorded complete admission is bound to these exact inputs (not rerun here)
    rel = read(P / 'evidence/RELEASE.json')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    headline = low - Q(1, 10**46) - Q(1, 10**70)
    need(rel['status'] == 'PASS_STAGED544_COMPLETE_CONDITIONAL_RELEASE'
         and rel['admission_status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'release status')
    need(Q(rel['kappa']) == headline and Q(rel['complex_lower']) == low, 'release headline is root_lower - 1e-46 - 1e-70')
    need({int(r): n for r, n in rel['profile'].items()} == profile, 'release profile')
    need(rel['order_sha256'] == sha(P / 'inputs/ORDER.json') and rel['fill_sha256'] == sha(P / 'inputs/FILL.json.gz'), 'release input binding')
    need(rel['dispatch_sha256'] == sha(S / 'inputs/DISPATCH.json'), 'release dispatch binding')
    need(all(s['exit_code'] == 0 for s in rel['admission_stages']), 'release stages')
    old_headline = old - Q(1, 10**46) - Q(1, 10**70)
    need(headline > old_headline > Q(rel['comparison_kappa']), 'strict headline gain over PR3734 and PR3682')

    # 5. controls
    rejected = []
    tmp = Path(tempfile.mkdtemp(prefix='staged544-clock-order-'))
    try:
        (tmp / 'ORDER.json').write_bytes((S / 'inputs/ORDER.json').read_bytes())
        code, out, err = owner_audit(tmp / 'ORDER.json')
        need(code != 0 and 'strict lower and closed upper window' in err, 'old clock must reject the new fill')
        rejected.append('predecessor_clock_with_new_fill')
    finally:
        shutil.rmtree(tmp)
    bad = [list(x) for x in order]
    r0 = bad[0][1]
    i, j = bad.index([0, r0]), bad.index([1, r0])
    bad[i], bad[j] = bad[j], bad[i]
    try:
        clock.check_order(bad)
    except ValueError as e:
        need('stage order' in str(e), 'wrong clock rejection')
        rejected.append('same_replica_stage_swap')
    else:
        raise ValueError('stage swap accepted')
    step = Q(1, 10**24)
    need(not root_signs(R, profile, low + step, high + step), 'shifted bracket accepted')
    rejected.append('bracket_shifted_up')
    moved_child = dict(profile)
    moved_child[48] -= 1
    moved_child[47] = moved_child.get(47, 0) + 1
    moved_child[1] += 1
    need(not root_signs(R, moved_child, low, high), 'moved idle child accepted')
    rejected.append('one_idle_rank48_split_47_1')
    need(ceiling_certificate.certify(R, low)['lower_bound'] <= 0, 'certificate must not clear root_lower')
    rejected.append('ceiling_certificate_at_root_lower')
    need(not ceiling_certificate.certify(R, high, perturb=Q(1, 10**30))['dual_feasible'], 'perturbed dual accepted')
    rejected.append('ceiling_dual_perturbed_1e-30')

    result = dict(status='PASS_STAGED544_CHANGED_CLOCK_CEILING_OWNERS_AND_PRICE', moved_calls=moved,
                  roles=audit['positive']['roles'], physical=audit['positive']['physical'],
                  idle=audit['positive']['idle'], profile={str(r): n for r, n in sorted(profile.items())},
                  root_lower=price['root_lower'], lower_decimal=price['lower_decimal'],
                  recorded_release_kappa=rel['kappa'],
                  ceiling_certificate=dict(at=price['root_upper'], patterns=cert['patterns'], dual_feasible=True,
                                           min_F_per_replica_lower_bound_positive=True),
                  gain_lower_over_pr3734=price['gain_lower_over_predecessor'], rejected_controls=rejected,
                  fill_payload_sha256=hashlib.sha256(gzip.decompress((P / 'inputs/FILL.json.gz').read_bytes())).hexdigest())
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
