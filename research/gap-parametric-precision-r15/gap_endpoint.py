#!/usr/bin/env python3
"""Gap-parametric precision/height certificate for the complete #5413 caller (numerical compiler headroom only).

#5413's precision checker and conjunction pin the strict compiler gap to 1/700000000000 and the height carrier to
(j, H) = (55099, 38569300000000000).  Its funding engine already derives the least height grid j from ANY unit gap
(least j with (H+1)^1000 < 2^j, H = j*den(gap)), and its written precision proof V16-APPLICATION-PROOF-v3.md is
symbolic in N = 2^H: the carrier appears only as recorded literals (sec. 5 H and gap lines, the sec. 6 NON-claim
"H*gap = j, H*r0 = j/10 < log2 D0", the sec. 8 endpoint pair).  This script
  1. authenticates #5413's capsule against its pinned SOURCE-BINDINGS.json and copies it into private scratch;
  2. reruns #5413's invoice/funding engine with only the two endpoint literals substituted, at the finer unit gap
     1/(7*10^16); the invoice is byte-identical, every downstream field except gap/j/H is unchanged, and j/H are
     re-derived here independently (least grid, preceding grid fails);
  3. generalises #5413's precision checker by replacing its single pinned-gap literal with "positive unit gap"
     (the H = j*den(gap) and (H+1)^1000 < 2^j obligations are unchanged), instantiates the written proof at the new
     carrier (the only edits are the four literal sites above, asserted unique), and checks:
       - conservativity: the generalised checker on #5413's own manifest reproduces #5413's expected receipt;
       - at the new carrier its receipt equals #5413's expected receipt except carrier_{H,j,gap}, expanded.{N,M},
         the proof/manifest/checker hashes and timing;
  4. reruns #5413's 25-premise conjunction with only endpoint/carrier literals moved;
  5. controls: #5413's pinned-gap precision checker and unsubstituted conjunction reject the new funding; the
     generalised checker rejects the old H with the new gap and a non-unit gap; tested values at/above the reserve
     bracket fail funded_alpha_reserve; a non-unit gap fails the engine's height grid; brackets; a gap sweep showing
     every unit gap 1/(7*10^m), m = 12..18, funds with its own least carrier.
Usage: python3 -I -B gap_endpoint.py [--write]
"""
import sys
import argparse, copy, hashlib, json, os, shutil, subprocess, tempfile
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = ROOT / 'research' / 'coupled-helper-neutral-completion'
BINDINGS_SHA256 = 'ea8ea2ff3db043d33ec3f4ea84f9ab760950eea1768f8a5ee9db91d0abb840e3'  # pinned in #5413 verify.py
OLD_K, OLD_S = '.003027288235', '.003027288245'
OLD_GAP, OLD_J, OLD_H = F(1, 700000000000), 55099, 38569300000000000
KAPPA, TESTED = '.0030272882489783', '.0030272882489784'
GAP = (F(TESTED) - F(KAPPA)) / 7
NEW_J, NEW_H = 72096, 5046720000000000000000  # recomputed below; recorded for review
R14_KAPPA = '.0030272882389'  # our #5462, same caller at the pinned gap
AGENTS = 'swarm-coupled-caller-sol-high-20261024/agents/'
INVOICE_DIR = AGENTS + 'invoice/'
PREC_DIR = AGENTS + 'precision/'
PROOF = PREC_DIR + 'V16-APPLICATION-PROOF-v3.md'
PROOF_SHA256_5413 = 'cda8f596f7854f42a228f757d5f8e68f6b2256a19c5ae3771fb40753cedc5b39'
NEW_PROOF = PREC_DIR + 'V16-APPLICATION-PROOF-v3-R15.md'
PINNED_GAP_LINE = "need(gap==(Q(fund['tested'])-Q(fund['kappa']))/7==Q(1,700000000000),'actual strict compiler gap')"
PARAMETRIC_GAP_LINE = ("need(gap==(Q(fund['tested'])-Q(fund['kappa']))/7 and gap>0 and gap.numerator==1,"
                       "'actual strict compiler gap (positive unit gap; gap-parametric)')")
RLIMIT = 'resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))'


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


def dec(x):
    x = F(x)
    for e in range(40):
        if (x * 10 ** e).denominator == 1:
            return '.' + str(x.numerator * 10 ** e // x.denominator).rjust(e, '0') if e else str(x)
    return str(x)


def wins(den, j):
    return (den * j + 1) ** 1000 < 2 ** j


def least_grid(den):
    lo, hi = 1, 2
    while not wins(den, hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if wins(den, mid) else (mid, hi)
    return hi


def proof_substitutions(gap, j, H, k, s):
    r0 = f'{j // 10}.{j % 10}' if j % 10 else str(j // 10)  # H*r0 = j/10 since r0 = gap/10
    return [('H=38569300000000000, N=2^H,', f'H={H}, N=2^H,'),
            ('The fresh strict tested/claim gap is1/700000000000.',
             f'The fresh strict tested/claim gap is1/{gap.denominator}.'),
            ('log2D0=1048576, while H*gap=55099 and H*r0=5509.9.', f'log2D0=1048576, while H*gap={j} and H*r0={r0}.'),
            ('The independent funding file uses K=.003027288235 and tested C=.003027288245,',
             f'The independent funding file uses K={k} and tested C={s},')]


def run(workspace, engine, argv):
    adapter = SRC / 'engine_adapter.py'
    env = {k: v for k, v in os.environ.items() if not k.startswith('PYTHON')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    r = subprocess.run([sys.executable, '-I', '-B', str(adapter), str(workspace), engine, *argv], cwd=workspace,
                       env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
    return r.returncode, r.stdout.decode(), r.stderr.decode()


def load(path):
    return json.loads(Path(path).read_bytes())


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def build():
    require(GAP > 0 and GAP.numerator == 1 and GAP == F(1, 7 * 10 ** 16), 'new unit gap 1/(7*10^16)')
    require(sha(SRC / 'SOURCE-BINDINGS.json') == BINDINGS_SHA256, '#5413 SOURCE-BINDINGS.json is the pinned one')
    bindings = load(SRC / 'SOURCE-BINDINGS.json')['files']
    scratch = Path(tempfile.mkdtemp(prefix='r15-gap-')).resolve()
    try:
        shutil.copytree(SRC / 'capsule', scratch, dirs_exist_ok=True)
        checked = 0
        for row in bindings:
            if row['path'].startswith('capsule/'):
                require(sha(scratch / row['path'][8:]) == row['sha256'], 'authenticated capsule byte ' + row['path'])
                checked += 1
            if row['path'] == 'engine_adapter.py':
                require(sha(SRC / 'engine_adapter.py') == row['sha256'], 'authenticated engine adapter')
        ws = scratch / 'workspace'
        expected = {name: load(SRC / 'reports' / 'expected' / name) for name in
                    ('invoice.json', 'funding.json', 'precision.json', 'conjunction.json')}

        # 2. invoice + funding at the new endpoint and finer unit gap
        lit = ws / INVOICE_DIR / 'check_neutral_literal.py'
        (lit.parent / 'check_neutral_literal_r15.py').write_text(substitute(lit.read_text(), [
            (f"F('{OLD_K}'),F('{OLD_S}')", f"F('{KAPPA}'),F('{TESTED}')")]))
        code, out, err = run(ws, INVOICE_DIR + 'check_neutral_literal_r15.py', [
            '--backward', AGENTS + 'caller/NEUTRAL-BACKWARD-v16c.json', '--forward', AGENTS + 'caller/NEUTRAL-FORWARD-v16c.json',
            '--output-dir', INVOICE_DIR + 'R15-RUN'])
        require(code == 0, 'funding run: ' + err[-800:])
        require(load(ws / INVOICE_DIR / 'R15-RUN/INVOICE-NEUTRAL-LITERAL.json') == expected['invoice.json'],
                'regenerated invoice equals #5413 expected invoice')
        rel_fund = INVOICE_DIR + 'R15-RUN/FUNDING-NEUTRAL-LITERAL.json'
        fund_path = ws / rel_fund
        new, old = load(fund_path), expected['funding.json']
        require(new['status'] == old['status'] == 'PASS_CONDITIONAL_COMPLETE_PROFILE_ENDPOINT_ARITHMETIC_ONLY', 'funding PASS')
        require(F(new['kappa']) == F(KAPPA) and F(new['tested']) == F(TESTED), 'new endpoint recorded')
        for key in ('paid', 'targets', 'reserve', 'tuple', 'invoice_sha256', 'ordinary_BIT', 'controls',
                    'strict_minimum_rounding_reserve', 'predicates', 'source_predicates'):
            require(new[key] == old[key], 'funding field unchanged: ' + key)
        j = least_grid(GAP.denominator)
        H = j * GAP.denominator
        require(F(new['gap']) == GAP and new['j'] == j == NEW_J and new['H'] == H == NEW_H, 'recomputed carrier')
        require(wins(GAP.denominator, j) and not wins(GAP.denominator, j - 1) and H > 8 * 1024, 'least height grid')
        require(j < 1048576, 'sec. 6 non-claim still holds: H*gap = j < log2 D0')
        changed = sorted(k for k in set(new) | set(old) if new.get(k) != old.get(k))

        # 3. gap-parametric precision checker and carrier-instantiated proof
        pdir = ws / PREC_DIR
        orig_checker = (pdir / 'check_v16_precision_v3.py').read_text()
        darwin = sys.platform == 'darwin'  # macOS cannot lower RLIMIT_AS; Linux runs the checker text unchanged there

        def shimmed(text):
            if not darwin:
                return text
            return substitute(text, [(RLIMIT, RLIMIT + ' if sys.platform!="darwin" else None')]).replace(
                'import argparse,copy,', 'import sys,argparse,copy,', 1)
        parametric = substitute(orig_checker, [(PINNED_GAP_LINE, PARAMETRIC_GAP_LINE)])
        (pdir / 'check_precision_gap_parametric.py').write_text(shimmed(parametric))
        (pdir / 'check_precision_pinned.py').write_text(shimmed(orig_checker))
        stored_proof = (HERE / 'V16-APPLICATION-PROOF-v3-R15.md').read_text()
        require(sha(ws / PROOF) == PROOF_SHA256_5413, '#5413 accepted written proof bytes')
        proof_text = substitute((ws / PROOF).read_text(), proof_substitutions(GAP, j, H, KAPPA, TESTED))
        require(proof_text == stored_proof, 'stored instantiated proof equals the four-literal substitution of #5413 proof')
        for literal in ('38569300000000000', 'is1/700000000000.', '55099', '5509.9', OLD_K, OLD_S):
            require(literal not in proof_text, 'no old carrier/endpoint literal left in instantiated proof: ' + literal)
        (ws / NEW_PROOF).write_text(proof_text)
        pman_path = pdir / 'V16-SOURCES-v3.json'
        pman_orig = load(pman_path)
        pman_raw = pman_path.read_bytes()

        def precision_manifest(funding_rel, proof_rel, name):
            m = copy.deepcopy(pman_orig)
            for r in m['rows']:
                if r['id'] == 'funding':
                    r['path'], r['sha256'] = funding_rel, sha(ws / funding_rel)
                if r['id'] == 'application_proof':
                    r['path'], r['sha256'] = proof_rel, sha(ws / proof_rel)
            m['by_id']['funding'], m['by_id']['application_proof'] = funding_rel, proof_rel
            dump(pdir / name, m)
            return pdir / name

        def run_checker(checker, manifest, output):
            # the checker reads the fixed name V16-SOURCES-v3.json next to itself
            pman_path.write_bytes(Path(manifest).read_bytes())
            try:
                return run(ws, PREC_DIR + checker, ['--root', '.', '--output', PREC_DIR + output])
            finally:
                pman_path.write_bytes(pman_raw)
        volatile = {'seconds', 'checker_sha256', 'input_manifest_sha256'}
        # 3a. conservativity: at #5413's own carrier the generalised checker gives #5413's receipt
        code, _, err = run_checker('check_precision_gap_parametric.py', pdir / 'V16-SOURCES-v3.json', 'R15-PREC-OLD.json')
        require(code == 0, 'generalised checker on #5413 manifest: ' + err[-800:])
        prec_old = load(pdir / 'R15-PREC-OLD.json')
        require({k: v for k, v in prec_old.items() if k not in volatile} ==
                {k: v for k, v in expected['precision.json'].items() if k not in volatile},
                'generalised checker reproduces #5413 expected precision receipt at the pinned gap')
        # 3b. new carrier
        new_pman = precision_manifest(rel_fund, NEW_PROOF, 'R15-SOURCES.json')
        code, _, err = run_checker('check_precision_gap_parametric.py', new_pman, 'R15-PRECISION.json')
        require(code == 0, 'generalised precision run: ' + err[-800:])
        prec = load(pdir / 'R15-PRECISION.json')
        require(prec['carrier_H'] == H and prec['carrier_j'] == j and F(prec['carrier_gap']) == GAP, 'precision carrier')
        require(prec['expanded']['N'] == f'2^{H}' and prec['expanded']['M'] == f'F16(2^{H})', 'symbolic N, M at new H')
        require(prec['mathematical_application']['proof_sha256'] == sha(ws / NEW_PROOF), 'instantiated proof bound')
        require(prec['input_manifest_sha256'] == sha(new_pman), 'precision bound to the new manifest')
        diff = sorted(k for k in set(prec) | set(expected['precision.json'])
                      if prec.get(k) != expected['precision.json'].get(k) and k not in volatile)
        require(diff == ['carrier_H', 'carrier_gap', 'carrier_j', 'expanded', 'mathematical_application'], 'diff ' + str(diff))
        for key in ('expanded', 'mathematical_application'):
            a, b = prec[key], expected['precision.json'][key]
            require(sorted(x for x in set(a) | set(b) if a.get(x) != b.get(x)) ==
                    (['M', 'N'] if key == 'expanded' else ['proof_sha256']), 'only carrier/proof fields differ in ' + key)

        # 4. conjunction with endpoint/carrier literals moved
        gain = F(KAPPA) - F('.00302728823')
        clo = ws / INVOICE_DIR / 'check_neutral_closure.py'
        (clo.parent / 'check_neutral_closure_r15.py').write_text(substitute(clo.read_text(), [
            (f"k==Q('{OLD_K}')", f"k==Q('{KAPPA}')"), (f"c==Q('{OLD_S}')", f"c==Q('{TESTED}')"),
            ("gap==(c-k)/7==Q(1,700000000000)", f"gap==(c-k)/7==Q(1,{GAP.denominator})"),
            ("k-Q('.00302728823')==Q(1,200000000000)", f"k-Q('.00302728823')==Q({gain.numerator},{gain.denominator})"),
            ("H==38569300000000000 and j==55099", f"H=={H} and j=={j}"),
            # the accepted written proof is bound by hash; its carrier instance is the four-literal substitution above
            (f"digest('precision_proof')=='{PROOF_SHA256_5413}'", f"digest('precision_proof')=='{sha(ws / NEW_PROOF)}'")]))
        cman = load(ws / INVOICE_DIR / 'NEUTRAL-CLOSURE-INPUTS-v1.json')
        for r in cman['rows']:
            if r['id'] == 'funding':
                r['path'], r['sha256'] = rel_fund, sha(fund_path)
            elif r['id'] == 'precision':
                r['path'], r['sha256'] = PREC_DIR + 'R15-PRECISION.json', sha(pdir / 'R15-PRECISION.json')
            elif r['id'] == 'precision_manifest':
                r['path'], r['sha256'] = PREC_DIR + 'R15-SOURCES.json', sha(new_pman)
            elif r['id'] == 'precision_proof':
                r['path'], r['sha256'] = NEW_PROOF, sha(ws / NEW_PROOF)
        dump(ws / INVOICE_DIR / 'R15-CLOSURE-INPUTS.json', cman)
        code, out, err = run(ws, INVOICE_DIR + 'check_neutral_closure_r15.py', ['--root', '.', '--manifest',
                             INVOICE_DIR + 'R15-CLOSURE-INPUTS.json', '--output', INVOICE_DIR + 'R15-CONJUNCTION.json'])
        require(code == 0, 'conjunction run: ' + err[-1500:])
        conj = load(ws / INVOICE_DIR / 'R15-CONJUNCTION.json')
        require(conj['status'] == 'PASS_CONDITIONAL_MATHEMATICAL_KAPPA_CONJUNCTION' and conj['premise_count'] == 25
                and all(conj['premises'].values()), 'all 25 conjunction premises PASS')
        require(set(conj['premises']) == set(expected['conjunction.json']['premises']), 'same 25 premise names as #5413')

        # 5. controls
        controls = {}
        code, _, err = run_checker('check_precision_pinned.py', new_pman, 'R15-CTL-PINNED.json')
        controls['pinned_gap_5413_precision_checker_rejects_new_funding'] = code != 0 and 'actual strict compiler gap' in err
        code, _, err = run(ws, INVOICE_DIR + 'check_neutral_closure.py', ['--root', '.', '--manifest',
                           INVOICE_DIR + 'R15-CLOSURE-INPUTS.json', '--output', INVOICE_DIR + 'R15-CTL-CONJ.json'])
        controls['unsubstituted_5413_conjunction_rejects_new_funding'] = code != 0 and 'exact_new_positive_endpoint_gap' in err

        def mutated_funding(name, **fields):
            m = dict(new, **fields)
            dump(ws / INVOICE_DIR / name, m)
            return precision_manifest(INVOICE_DIR + name, NEW_PROOF, 'R15-' + name)
        code, _, err = run_checker('check_precision_gap_parametric.py', mutated_funding('MUT-OLD-H.json', H=OLD_H, j=OLD_J),
                                   'R15-CTL-OLDH.json')
        controls['parametric_checker_rejects_old_carrier_with_new_gap'] = code != 0 and 'actual funded carrier rank' in err
        code, _, err = run_checker('check_precision_gap_parametric.py', mutated_funding('MUT-NONUNIT.json',
                                   kappa=str(F(TESTED) - 3 * F(1, 10 ** 16)), gap=str(F(3, 7 * 10 ** 16))), 'R15-CTL-NONUNIT.json')
        controls['parametric_checker_rejects_non_unit_gap'] = code != 0 and 'actual strict compiler gap' in err
        sys.path.insert(0, str(ws / INVOICE_DIR))
        from fund_uniform_endpoint import evaluate_profiles
        from exact_moments import moment, minus
        P = {int(k): v for k, v in new['paid'].items()}; T = {int(k): v for k, v in new['targets'].items()}

        def funded(k, s):
            try:
                r = evaluate_profiles(P, T, F(k), F(s), 1000, {})
            except ValueError as e:
                return str(e)
            return r
        e1 = funded('.00302728824', '.00302728825')
        e2 = funded('.0030272882489784', '.0030272882489785')
        e3 = funded('.0030272882489781', TESTED)
        controls['tested_.00302728825_rejected_alpha_reserve'] = isinstance(e1, str) and 'funded_alpha_reserve' in e1
        controls['tested_.0030272882489785_rejected_alpha_reserve'] = isinstance(e2, str) and 'funded_alpha_reserve' in e2
        controls['engine_non_unit_gap_rejected'] = isinstance(e3, str) and 'unit height grid' in e3
        require(all(controls.values()), 'controls: ' + json.dumps(controls))

        def alpha_ok(s):
            return moment(P, 1 - s)[1] / moment(T, 1 - s)[0] < 1 - F(1, 10 ** 12)
        require(minus(moment(T, 1 - F('.0030272882499')), moment(P, 1 - F('.0030272882499')))[0] > 0 and
                minus(moment(T, 1 - F('.00302728825')), moment(P, 1 - F('.00302728825')))[1] < 0, 'raw root bracket')
        require(alpha_ok(F('.003027288248978444')) and not alpha_ok(F('.003027288248978445')), 'reserve-limited tested bracket')
        # gap sweep: each finer unit gap 1/(7*10^m) funds with its own least carrier
        sweep = []
        s_floor = F('.003027288248978444')  # inside the reserve bracket (checked above)
        for m in range(12, 19):
            s = F(int(s_floor * 10 ** m), 10 ** m)  # largest tested value on the 10^-m grid below the bracket
            k = s - F(1, 10 ** m)
            r = funded(k, s)
            require(not isinstance(r, str), f'sweep m={m}: {r}')
            g = F(r['gap']); jj = least_grid(g.denominator)
            require(g == F(1, 7 * 10 ** m) and r['j'] == jj and r['H'] == jj * g.denominator, f'sweep carrier m={m}')
            sweep.append(dict(gap=f'1/{g.denominator}', kappa=dec(k), tested=dec(s), j=jj, H=str(r['H']),
                              min_strict_outer=str(r['outer']['minimum_strict'])))
        return dict(
            scope='numerical compiler headroom only: same complete #5413 caller, invoice and profiles; zero economic gain',
            previous=dict(pr5413=dict(kappa=OLD_K, tested=OLD_S), pr5462=dict(kappa=R14_KAPPA, tested='.0030272882489')),
            kappa=KAPPA, tested=TESTED, gain_over_5413=str(F(KAPPA) - F(OLD_K)), gain_over_5462=str(F(KAPPA) - F(R14_KAPPA)),
            carrier=dict(gap=str(GAP), j=j, H=str(H)), old_carrier=dict(gap=str(OLD_GAP), j=OLD_J, H=str(OLD_H)),
            authenticated_capsule_files=checked, funding_changed_fields=changed,
            precision_checker_change=dict(pinned=PINNED_GAP_LINE, parametric=PARAMETRIC_GAP_LINE),
            precision_receipt_differs_only_in=diff, proof_literal_sites=4,
            raw_root_bracket=['.0030272882499', '.00302728825'],
            reserve_limited_tested_bracket=['.003027288248978444', '.003027288248978445'],
            supremum_note='every positive unit gap is admissible; kappa < tested < .003027288248978445 is the only bound',
            fixed_profile_ceiling_U='.00302728825 (#5409); kappa stays below it',
            conjunction=dict(status=conj['status'], premise_count=conj['premise_count'],
                             gain_over_prior_comparison=str(conj['gain_over_prior_comparison'])),
            gap_sweep=sweep, controls=controls)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); args = ap.parse_args()
    result = build()
    path = HERE / 'RESULT-GAP-PARAMETRIC.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT equals the rebuild')
    print('PASS_5413_CALLER_GAP_PARAMETRIC_PRECISION_AT_KAPPA_0.0030272882489783')


if __name__ == '__main__':
    main()
