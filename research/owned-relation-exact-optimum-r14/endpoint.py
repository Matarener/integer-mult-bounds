#!/usr/bin/env python3
"""Part A: re-fund the complete #5413 caller at a higher endpoint inside its own funded reserve (numerical only).

Nothing scientific in #5413 changes: the same B/F packets, controller, invoice, outer engine, height carrier
(gap 1/700000000000, j = 55099, H = 38569300000000000) and precision proof.  Only the claimed/tested pair moves from
(.003027288235, .003027288245) to (KAPPA, TESTED) below.  The script
  1. authenticates #5413's capsule against its own SOURCE-BINDINGS.json (whose SHA256 its verify.py pins) and copies it
     into private scratch;
  2. reruns #5413's invoice/funding engine with exactly the two endpoint literals substituted (asserted unique) and
     checks that the regenerated invoice equals #5413's expected invoice byte-for-byte in JSON;
  3. checks that every field the precision checker reads from the funding file (status, gap, H, j, paid, targets) is
     unchanged, then reruns #5413's precision checker on a manifest whose funding row points to the new receipt and
     compares its output with #5413's expected precision receipt (only the manifest hash may differ);
  4. reruns #5413's 25-premise conjunction with the endpoint gate literals substituted, on a manifest with the new
     funding/precision rows; requires PASS and 25 premises;
  5. live controls: the unsubstituted conjunction rejects the new funding; the endpoint arithmetic rejects tested
     .00302728825 (alpha reserve), tested .00302728824898 (alpha reserve) and an off-grid gap; exact brackets for the
     raw root and the reserve-limited tested saving are recomputed with #5413's directed moment engine.
Usage: python3 -I -B endpoint.py [--write]
"""
import sys
import argparse, hashlib, json, os, shutil, subprocess, tempfile
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = ROOT / 'research' / 'coupled-helper-neutral-completion'
BINDINGS_SHA256 = 'ea8ea2ff3db043d33ec3f4ea84f9ab760950eea1768f8a5ee9db91d0abb840e3'  # pinned in #5413 verify.py
OLD_K, OLD_S = '.003027288235', '.003027288245'
KAPPA, TESTED = '.0030272882389', '.0030272882489'
AGENTS = 'swarm-coupled-caller-sol-high-20261024/agents/'
INVOICE_DIR = AGENTS + 'invoice/'
PREC_DIR = AGENTS + 'precision/'


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def substitute(text, pairs):
    for old, new in pairs:
        require(text.count(old) == 1, 'unique substitution site: ' + old)
        text = text.replace(old, new)
    return text


def run(workspace, engine, argv, darwin_shim=False):
    adapter = SRC / 'engine_adapter.py'
    env = {k: v for k, v in os.environ.items() if not k.startswith('PYTHON')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    r = subprocess.run([sys.executable, '-I', '-B', str(adapter), str(workspace), engine, *argv], cwd=workspace,
                       env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
    return r.returncode, r.stdout.decode(), r.stderr.decode()


def load(path):
    return json.loads(Path(path).read_bytes())


def build():
    require(sha(SRC / 'SOURCE-BINDINGS.json') == BINDINGS_SHA256, '#5413 SOURCE-BINDINGS.json is the pinned one')
    bindings = load(SRC / 'SOURCE-BINDINGS.json')['files']
    scratch = Path(tempfile.mkdtemp(prefix='r14-endpoint-')).resolve()
    try:
        shutil.copytree(SRC / 'capsule', scratch, dirs_exist_ok=True)
        checked = 0
        for row in bindings:
            if row['path'].startswith('capsule/'):
                require(sha(scratch / row['path'][8:]) == row['sha256'], 'authenticated capsule byte ' + row['path'])
                checked += 1
        for row in bindings:
            if row['path'] == 'engine_adapter.py':
                require(sha(SRC / 'engine_adapter.py') == row['sha256'], 'authenticated engine adapter')
        ws = scratch / 'workspace'
        expected = {name: load(SRC / 'reports' / 'expected' / name) for name in
                    ('invoice.json', 'funding.json', 'precision.json', 'conjunction.json')}
        # 2. invoice + funding at the new endpoint
        lit = ws / INVOICE_DIR / 'check_neutral_literal.py'
        (lit.parent / 'check_neutral_literal_r14.py').write_text(substitute(lit.read_text(), [
            (f"F('{OLD_K}'),F('{OLD_S}')", f"F('{KAPPA}'),F('{TESTED}')")]))
        code, out, err = run(ws, INVOICE_DIR + 'check_neutral_literal_r14.py', [
            '--backward', AGENTS + 'caller/NEUTRAL-BACKWARD-v16c.json', '--forward', AGENTS + 'caller/NEUTRAL-FORWARD-v16c.json',
            '--output-dir', INVOICE_DIR + 'R14-RUN'])
        require(code == 0, 'funding run: ' + err[-800:])
        inv = load(ws / INVOICE_DIR / 'R14-RUN/INVOICE-NEUTRAL-LITERAL.json')
        require(inv == expected['invoice.json'], 'regenerated invoice equals #5413 expected invoice')
        fund_path = ws / INVOICE_DIR / 'R14-RUN/FUNDING-NEUTRAL-LITERAL.json'
        new, old = load(fund_path), expected['funding.json']
        require(new['status'] == old['status'] == 'PASS_CONDITIONAL_COMPLETE_PROFILE_ENDPOINT_ARITHMETIC_ONLY', 'funding PASS')
        require(F(new['kappa']) == F(KAPPA) and F(new['tested']) == F(TESTED), 'new endpoint recorded')
        for key in ('gap', 'H', 'j', 'paid', 'targets', 'reserve', 'tuple', 'invoice_sha256', 'ordinary_BIT', 'controls'):
            require(new[key] == old[key], 'funding field read downstream is unchanged: ' + key)
        require(F(new['gap']) == F(1, 700000000000) and new['j'] == 55099 and new['H'] == 38569300000000000, 'carrier')
        changed = sorted(k for k in set(new) | set(old) if new.get(k) != old.get(k))
        # 3. precision on the new funding receipt
        pman_path = ws / PREC_DIR / 'V16-SOURCES-v3.json'
        pman = load(pman_path)
        rel_fund = INVOICE_DIR + 'R14-RUN/FUNDING-NEUTRAL-LITERAL.json'
        for r in pman['rows']:
            if r['id'] == 'funding':
                r['path'], r['sha256'] = rel_fund, sha(fund_path)
        pman['by_id']['funding'] = rel_fund
        pman_path.write_text(json.dumps(pman, indent=2, sort_keys=True) + '\n')
        checker = ws / PREC_DIR / 'check_v16_precision_v3.py'
        shim = sys.platform == 'darwin'  # macOS cannot lower RLIMIT_AS; Linux runs the frozen checker unchanged
        if shim:
            checker.write_text(substitute(checker.read_text(), [(
                'resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))',
                'resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2)) if sys.platform!="darwin" else None')]
            ).replace('import argparse,copy,', 'import sys,argparse,copy,', 1))
        code, out, err = run(ws, PREC_DIR + 'check_v16_precision_v3.py', ['--root', '.', '--output', PREC_DIR + 'R14-PRECISION.json'])
        require(code == 0, 'precision run: ' + err[-800:])
        prec = load(ws / PREC_DIR / 'R14-PRECISION.json')
        drop = {'seconds', 'input_manifest_sha256'} | ({'checker_sha256'} if shim else set())
        require({k: v for k, v in prec.items() if k not in drop} == {k: v for k, v in expected['precision.json'].items() if k not in drop},
                'precision receipt equals #5413 expected receipt except the manifest hash')
        require(prec['input_manifest_sha256'] == sha(pman_path), 'precision bound to the substituted manifest')
        # 4. conjunction with the endpoint gate moved to the new pair
        gain = F(KAPPA) - F('.00302728823')
        clo = ws / INVOICE_DIR / 'check_neutral_closure.py'
        original_closure = clo.read_text()
        (clo.parent / 'check_neutral_closure_r14.py').write_text(substitute(original_closure, [
            (f"k==Q('{OLD_K}')", f"k==Q('{KAPPA}')"), (f"c==Q('{OLD_S}')", f"c==Q('{TESTED}')"),
            ("k-Q('.00302728823')==Q(1,200000000000)", f"k-Q('.00302728823')==Q({gain.numerator},{gain.denominator})")]))
        cman_path = ws / INVOICE_DIR / 'NEUTRAL-CLOSURE-INPUTS-v1.json'
        cman = load(cman_path)
        for r in cman['rows']:
            if r['id'] == 'funding':
                r['path'], r['sha256'] = rel_fund, sha(fund_path)
            elif r['id'] == 'precision':
                r['path'], r['sha256'] = PREC_DIR + 'R14-PRECISION.json', sha(ws / PREC_DIR / 'R14-PRECISION.json')
            elif r['id'] == 'precision_manifest':
                r['sha256'] = sha(pman_path)
        new_cman = ws / INVOICE_DIR / 'R14-CLOSURE-INPUTS.json'
        new_cman.write_text(json.dumps(cman, indent=2, sort_keys=True) + '\n')
        code, out, err = run(ws, INVOICE_DIR + 'check_neutral_closure_r14.py', ['--root', '.', '--manifest',
                             INVOICE_DIR + 'R14-CLOSURE-INPUTS.json', '--output', INVOICE_DIR + 'R14-CONJUNCTION.json'])
        require(code == 0, 'conjunction run: ' + err[-800:])
        conj = load(ws / INVOICE_DIR / 'R14-CONJUNCTION.json')
        require(conj['status'] == 'PASS_CONDITIONAL_MATHEMATICAL_KAPPA_CONJUNCTION' and conj['premise_count'] == 25
                and all(conj['premises'].values()), 'all 25 conjunction premises PASS')
        require(set(conj['premises']) == set(expected['conjunction.json']['premises']), 'same 25 premise names as #5413')
        # 5. controls
        controls = {}
        code, _, err = run(ws, INVOICE_DIR + 'check_neutral_closure.py', ['--root', '.', '--manifest',
                           INVOICE_DIR + 'R14-CLOSURE-INPUTS.json', '--output', INVOICE_DIR + 'R14-CONTROL.json'])
        controls['unsubstituted_5413_conjunction_rejects_new_funding'] = code != 0 and 'exact_new_positive_endpoint_gap' in err
        sys.path.insert(0, str(ws / INVOICE_DIR))
        from fund_uniform_endpoint import evaluate_profiles
        from exact_moments import moment, minus
        P = {int(k): v for k, v in new['paid'].items()}; T = {int(k): v for k, v in new['targets'].items()}

        def rejected(k, s):
            try:
                evaluate_profiles(P, T, F(k), F(s), 1000, {})
            except ValueError as e:
                return str(e)
            return None
        e1 = rejected('.00302728824', '.00302728825')
        e2 = rejected('.00302728823898', '.00302728824898')
        e3 = rejected('.0030272882389', '.0030272882488')
        controls['tested_.00302728825_rejected_alpha_reserve'] = bool(e1) and 'funded_alpha_reserve' in e1
        controls['tested_.00302728824898_rejected_alpha_reserve'] = bool(e2) and 'funded_alpha_reserve' in e2
        controls['non_unit_gap_rejected'] = bool(e3) and 'unit height grid' in e3
        require(all(controls.values()), 'controls: ' + json.dumps(controls))

        def raw(s):
            return minus(moment(T, 1 - s), moment(P, 1 - s))

        def alpha_ok(s):
            return moment(P, 1 - s)[1] / moment(T, 1 - s)[0] < 1 - F(1, 10 ** 12)
        require(raw(F('.0030272882499'))[0] > 0 and raw(F('.00302728825'))[1] < 0, 'raw root bracket')
        require(alpha_ok(F('.00302728824897')) and not alpha_ok(F('.00302728824898')), 'reserve-limited tested bracket')
        return dict(
            scope='numerical compiler headroom only: same complete #5413 caller, invoice, carrier and precision proof',
            previous=dict(kappa=OLD_K, tested=OLD_S), kappa=KAPPA, tested=TESTED,
            gain_over_5413=str(F(KAPPA) - F(OLD_K)), gain_over_5398=str(gain),
            authenticated_capsule_files=checked, funding_changed_fields=changed,
            carrier=dict(gap=new['gap'], j=new['j'], H=new['H']),
            raw_root_bracket=['.0030272882499', '.00302728825'],
            reserve_limited_tested_bracket=['.00302728824897', '.00302728824898'],
            fixed_profile_ceiling_U='.00302728825 (#5409); kappa stays below it',
            conjunction=dict(status=conj['status'], premise_count=conj['premise_count'],
                             gain_over_prior_comparison=str(conj['gain_over_prior_comparison'])),
            precision_receipt='equal to #5413 expected receipt except input_manifest_sha256',
            controls=controls, macos_rlimit_shim_used=shim)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); args = ap.parse_args()
    result = build()
    result.pop('macos_rlimit_shim_used')
    path = HERE / 'RESULT-ENDPOINT.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT-ENDPOINT.json equals the rebuild')
    print('PASS_5413_CALLER_REFUNDED_AT_KAPPA_0.0030272882389')


if __name__ == '__main__':
    main()
