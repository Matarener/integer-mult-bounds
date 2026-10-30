#!/usr/bin/env python3
"""Independent scope, emitted-column, control-word, and invoice binding review.

Apache-2.0; substantial OpenAI assistance. Retained arithmetic is source-bound,
not independently reimplemented. Native-boundary authorship is disclosed.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def digest(p, payload=False):
    b = p.read_bytes()
    return sha256(gzip.decompress(b) if payload and p.suffix == '.gz' else b).hexdigest()


def module(p, name):
    spec = importlib.util.spec_from_file_location(name, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def controls(template):
    stages = []
    for e in template['recipe']:
        if e['kind'] == 'local':
            stages.append([e, []])
        elif e['kind'] == 'bridge':
            stages[-1][1].append(e)
    identity = tuple(tuple(int(i == j) for j in range(8)) for i in range(8))
    target = tuple(tuple(-1 if i % 2 == 0 and j == i+1 else
                         1 if i % 2 == 1 and j == i-1 else 0
                         for j in range(8)) for i in range(8))
    count = hits = max_entry = 0

    def step(m, stage, pre, post, d):
        e, bridges = stages[stage]
        m = list(m)
        k = 2*e['pair']
        x, y = m[k], tuple((d if pre else 1)*v for v in m[k+1])
        if e['reverse']:
            x, y = tuple(a-b for a, b in zip(x,y)), tuple(d*v for v in y)
        else:
            x, y = tuple(d*v for v in x), tuple(d*a+b for a,b in zip(x,y))
        m[k], m[k+1] = tuple((d if post else 1)*v for v in x), y
        for b in bridges:
            t, s, q = 2*b['dst'], 2*b['src'], b['coefficient']
            m[t] = tuple(a+q*v for a,v in zip(m[t],m[s]))
            m[s+1] = tuple(a-q*v for a,v in zip(m[s+1],m[t+1]))
        return tuple(m)

    def visit(stage, m):
        nonlocal count, hits, max_entry
        if stage == 9:
            count += 1
            hits += m == target
            max_entry = max(max_entry, max(abs(v) for row in m for v in row))
            return
        for pre in range(2):
            for post in range(2):
                visit(stage+1, step(m,stage,pre,post,-1))
    visit(0,identity)
    positive = identity
    for j in range(9):
        positive = step(positive,j,0,0,1)
    need(positive == target and count == 4**9 and hits == 0, 'independent direct control enumeration')
    return dict(patterns=count, solutions=hits, integer_arithmetic='Python unbounded integers',
                maximum_final_entry=max_entry, positive_control=True,
                scope='Exactly two binary controls, pre-Y D and post-X D, per stage of the retained common-involution nine-call recipe. No other scalar controller is excluded.')


def scalar_column(w, h):
    """Independent forward affected-column replay with ordered free warp words."""
    s = {h: {(): F(1)}}
    def event(e):
        kind, r = e[:2]
        if kind == 'warp':
            op = e[2]
            s[r] = {(ww[1:] if ww and ww[0] == -op else (op,)+ww):v
                    for ww,v in s.get(r,{}).items()}
        elif kind == 'scale':
            q = F(e[2],e[3])
            s[r] = {ww:q*v for ww,v in s.get(r,{}).items() if q*v}
        else:
            need(kind == 'add', 'scalar event grammar')
            dst = s.setdefault(r,{})
            for ww,v in list(s.get(e[2],{}).items()):
                q = dst.get(ww,F())+F(e[3],e[4])*v
                if q: dst[ww] = q
                else: dst.pop(ww,None)
    for part in ('precondition','compensation','A'):
        need(all(h not in (e[1:3] if e[0] == 'add' else [e[1]]) for e in w[part]), 'released helper untouched before B')
    need(all(h not in (e['source'],e['target']) for e in w['initial_corrections']), 'released helper absent from initial corrections')
    warps = {}
    for op,entry in enumerate(w['warps'],1):
        warps.setdefault(entry[0],[]).append(['warp',entry[1],op])
    for j in range(len(w['B'])+1):
        for e in warps.get(j,[]): event(e)
        if j < len(w['B']): event(w['B'][j])
    for part in ('restore','cleanup'):
        for e in w[part]: event(e)
    return {r:row for r,row in s.items() if row}


def joint_review(scope, followup, I):
    """Rebuild both provider words, bind profiles, and reprice all 31 subsets."""
    combo_path = scope/'coupled-boundary/combined-subsets/COMBINED-SUBSETS.json'
    price_path = scope/'invoice-experiments/JOINT-PROFILE-SCREEN.json'
    combo, prices = read(combo_path), read(price_path)
    inv = scope/'invoice-experiments'
    need(prices['script_sha256'] == digest(inv/'joint_profile_screen.py'), 'joint price generator binding')
    need(prices['shared_utility_sha256'] == digest(inv/'local_repack.py'), 'joint shared utility binding')
    need(prices['supplied_profile_source']['sha256'] == digest(combo_path), 'joint supplied census binding')
    need(prices['frozen_invoice_receipt_sha256'] == digest(scope.with_name('kappa-global-continuation')/'invoice-analysis/evidence/RESULT.json'), 'joint frozen receipt binding')
    specs = combo['specs']
    need([s['h'] for s in specs] == [484,508,532,556,584], 'exact five-generator family')
    C = module(scope/'entry-retiming/complete_candidate.py','review_native_frame_profile')
    sources = {}
    for tag in ('base','extra'):
        p = followup/f'artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43{tag}.json.gz'
        sources[tag] = read(p), digest(p)
    by_helpers = {tuple(r['helpers']):r for r in prices['cases']}
    need(len(by_helpers) == len(combo['candidates']) == 31, '31 distinct joint cases')
    blo,bhi = I.moment(I.BASE,73,896*360,I.TARGET)
    checks = []
    affected_columns = 0
    for wanted_mask, case in enumerate(combo['candidates'],1):
        mask = case['mask']
        need(mask == wanted_mask, 'all nonempty subsets in order')
        chosen = [s for i,s in enumerate(specs) if mask >> i & 1]
        helpers = [s['h'] for s in chosen]
        need(helpers == case['helpers'], 'subset identity binding')
        common_profile = {int(r):n for r,n in case['local_profile'].items()}
        for tag,(source,pin) in sources.items():
            w = deepcopy(source)
            inserts = {}
            for s in chosen:
                h = s['h']
                w['start_extra'][str(h)] = list(s['frame'])
                e = w['B'][s['read']]
                need(e[0] == 'add' and e[2] == h, 'literal removed early read')
                w['B'][s['read']] = ['scale',e[1],1,1,e[-1]]
                inserts.setdefault(s['cut'],[]).extend(
                    ['add',int(r),h,F(q).numerator,F(q).denominator,list(s['frame'])]
                    for r,q in sorted(s['release'].items(),key=lambda item:int(item[0])))
            new_b = []
            for j in range(len(w['B'])+1):
                new_b.extend(inserts.get(j,[]))
                if j < len(w['B']): new_b.append(w['B'][j])
            w['B'] = new_b
            for warp in w['warps']:
                old_pos = warp[0]
                warp[0] = old_pos+sum(len(gates) for pos,gates in inserts.items() if pos <= old_pos)
            # Native monotone paths are recounted with the bound shared
            # compiler; the composition and affected-column replay are new.
            profile,widths = C.profile(w)
            need(profile == common_profile, 'both provider native path profiles agree with census')
            need(widths == {int(r):n for r,n in case['width_inventory'].items()}, 'both provider width inventories')
            w['report']['local_profile'],w['report']['width_inventory'] = profile,widths
            payload = json.dumps(w,sort_keys=True,separators=(',',':')).encode()
            need(case['providers'][tag]['source_sha256'] == pin, 'joint provider source pin')
            need(case['providers'][tag]['word_payload_sha256'] == sha256(payload).hexdigest(), 'independently rebuilt provider word payload')
            for s in chosen:
                expected = {s['h']:{():F(1)}}
                expected.update({int(r):{():F(q)} for r,q in s['release'].items()})
                need(scalar_column(w,s['h']) == expected, 'joint ordered affected-column replay, including shared donors')
                affected_columns += 1
        priced = by_helpers[tuple(helpers)]
        need(priced['supplied_provider_word_references'] == case['providers'], 'price to both provider payload bindings')
        need({int(r):n for r,n in priced['actual_local_profile_hypothesis'].items()} == common_profile, 'joint local tariff binding')
        h = Counter(I.BASE)
        h.subtract({r:3240*n for r,n in I.LOCAL.items()})
        h.update({r:3240*n for r,n in common_profile.items()})
        stock = priced['old_remainder_and_joint_multiplicity']
        need(sum(k*n for old,k,n in stock) == 3240*len(helpers), 'all changed owner occurrences accounted once')
        for old,k,n in stock:
            need(old >= 0 and k > 0 and n > 0, 'joint owner multiplicity domain')
            if old: h[old] -= n
            h[old+k] += n
        h = +h
        need(dict(sorted(h.items())) == {int(r):n for r,n in priced['complete_profile'].items()}, 'shared owner-bin remainder profile composition')
        need(sum(r*n for r,n in h.items()) == 65088*360, 'joint unchanged raw bill')
        lo,hi = I.moment(h,73,896*360,I.TARGET)
        need(lo > bhi and lo > 1, 'each joint subset strictly worse than baseline and target')
        need(I.interval(lo-1,hi-1) == priced['target_residual'], 'joint exact residual equality')
        need(I.interval(lo-bhi,hi-blo) == priced['moment_difference_from_actual_baseline'], 'joint exact baseline difference')
        a,b = map(F,priced['root']['rational'])
        need(I.moment(h,73,896*360,a)[1] < 1 < I.moment(h,73,896*360,b)[0], 'joint exact root bracket')
        checks.append(dict(mask=mask,helpers=helpers,both_provider_payloads=True,
                           common_profile=common_profile,strictly_worse_with_free_completion=True))
    need(affected_columns == 160, 'all 160 selected helper/provider/subset columns')
    return dict(status='PASS_ALL_31_COMBINED_SUBSETS_BOTH_PROVIDERS_AND_EXACT_PRICES',
        subset_count=31,provider_words_rebuilt=62,affected_columns_replayed=affected_columns,
        h556_extra_provider_checked=True,shared_donor616_joint_cases_checked=True,
        census_sha256=digest(combo_path),price_receipt_sha256=digest(price_path),
        compose_generator_sha256=digest(scope/'coupled-boundary/combine_releases.py'),
        native_profile_compiler_sha256=digest(scope/'entry-retiming/complete_candidate.py'),
        joint_price_generator_sha256=digest(inv/'joint_profile_screen.py'),cases=checks,
        scope='Independent word composition, payload binding, affected-column propagation, stock-to-profile composition, and exact repricing. Native frame recount reuses the bound shared compiler; individual physical owners are represented by the authenticated joint stock census, not replayed anew here. All native HPE dirt completion remains unpaid.')


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--scope',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--out',type=Path,default=Path(__file__).resolve().with_name('REVIEW.json'))
    args = ap.parse_args()
    scope = args.scope.resolve()
    repo = scope.parents[1]
    frozen = scope.with_name('kappa-global-continuation')
    followup = frozen/'inputs/kappa-consumer-followup'
    template_path = followup/'artifact/live-source/research/staged544-producer-return/inputs/TEMPLATE.json.gz'
    review_controls = controls(read(template_path))
    old_control = read(scope/'control-search/CONTROLS.json')
    need((old_control['num_patterns'],old_control['solution_count']) == (review_controls['patterns'],0), 'control receipt agreement')
    I = module(frozen/'invoice-analysis/invoice.py','review_invoice')
    frozen_receipt = read(frozen/'invoice-analysis/evidence/RESULT.json')
    need(frozen_receipt['script_sha256'] == digest(Path(I.__file__)), 'frozen invoice binding')
    need(frozen_receipt['arithmetic_engine_sha256'] == digest(I.ENGINE_PATH), 'exact arithmetic engine binding')
    inv = scope/'invoice-experiments'
    partial = read(inv/'PARTIAL-TARIFFS.json')
    need(partial['frozen_invoice_receipt_sha256'] == digest(frozen/'invoice-analysis/evidence/RESULT.json'), 'partial frozen receipt binding')
    need(partial['source_template_sha256'] == digest(template_path), 'partial actual template binding')
    need(partial['script_sha256'] == digest(inv/'partial_tariffs.py'), 'partial tariff generator binding')
    need(partial['source_census_sha256'] == digest(scope/'native-boundary/evidence/PARTIAL-GEOMETRY-CENSUS.json'), 'partial census payload binding')
    need(partial['source_census_script_sha256'] == digest(scope/'native-boundary/partial_geometry.py'), 'partial census generator binding')
    partial_pass = []
    for row in partial['patterns']:
        h = {int(r):F(n) for r,n in row['optimistic_complete_profile'].items()}
        lo,hi = I.moment(h,row['dimension'],1024,I.TARGET)
        need(I.interval(lo-1,hi-1) == row['target_residual_without_consumer'], 'each outward-rational partial price')
        if hi < 1: partial_pass.append(row['common_stages'])
    need(len(partial['patterns']) == 256 and partial_pass == [[]], '255 nonempty patterns fail')
    actual = read(inv/'ACTUAL-PROFILE-SCREEN.json')
    census = read(inv/'RETIMING-SCREEN.json')
    need(actual['script_sha256'] == digest(inv/'actual_profile_screen.py'), 'actual profile generator binding')
    need(actual['owner_tail_census_sha256'] == digest(inv/'RETIMING-SCREEN.json'), 'actual owner-tail binding')
    need(actual['frozen_invoice_script_sha256'] == digest(Path(I.__file__)), 'actual frozen arithmetic interface binding')
    need(census['frozen_invoice_receipt_sha256'] == digest(frozen/'invoice-analysis/evidence/RESULT.json'), 'owner-tail frozen receipt binding')
    need(census['script_sha256'] == digest(inv/'retiming_invoice.py'), 'owner-tail generator binding')
    need(census['shared_utility_sha256'] == digest(inv/'local_repack.py'), 'owner-tail shared utility binding')
    need(all(len(set(r['borrowed_word_origin_by_provider'].values())) == 1
             for r in census['cases_sorted_by_exact_price']), 'provider helper identity agreement')
    cases = {next(iter(set(r['borrowed_word_origin_by_provider'].values()))):r for r in census['cases_sorted_by_exact_price']}
    source = followup/'artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz'
    old = read(source)
    rows = []
    source_files = {}
    for item in actual['cases']:
        helper = item['borrowed_helper']
        paths = list((scope/'coupled-boundary/projected-release-raised-all-cuts').glob(f'RELEASE-{helper}-*.json.gz'))
        need(len(paths) == 1, 'one bound emitted candidate per priced helper')
        p = paths[0]
        w = read(p)
        delta = Counter({int(r):n for r,n in w['report']['local_profile'].items()})
        delta.subtract(I.LOCAL)
        delta = {r:n for r,n in delta.items() if n}
        need(delta == {int(r):n for r,n in item['actual_local_profile_delta_hypothesis'].items()}, 'price hypothesis matches emitted local tariff')
        need(len(w['start_extra'][str(helper)]) == len(old['start_extra'][str(helper)])+1, 'literal entry rank increases one')
        need(w['helper_final'][str(helper)] == old['helper_final'][str(helper)], 'helper final frame unchanged')
        before,after = scalar_column(old,helper),scalar_column(w,helper)
        need(before == {helper:{():F(1)}}, 'original arbitrary-helper endpoint column')
        dirt = {r:row for r,row in after.items() if r != helper}
        need(after.get(helper) == {():F(1)}, 'changed helper restored algebraically')
        protected = set(range(112,224))|set(map(int,w['helper_final']))
        need(not (set(dirt)&protected) and all(r < 704 for r in dirt), 'protected projection exact; no owned-query residual')
        c = cases[helper]
        complete = Counter(I.BASE)
        complete.update({int(r):n for r,n in c['complete_profile_delta'].items()})
        complete[1] += 3240
        complete.update({r:3240*n for r,n in delta.items()})
        need(dict(sorted(complete.items())) == {int(r):n for r,n in item['complete_profile'].items()}, 'complete actual-owner profile binding')
        lo,hi = I.moment(complete,73,896*360,I.TARGET)
        blo,bhi = I.moment(I.BASE,73,896*360,I.TARGET)
        need(lo > bhi and I.interval(lo-1,hi-1) == item['target_residual'], 'bare candidate strictly worse with free completion')
        rows.append(dict(helper=helper, local_delta=delta, full_dirt_rows=sorted(dirt),
                         exact_affected_column_replayed=True, free_completion_already_loses=True))
        source_files[str(p.relative_to(repo))] = digest(p,True)
    need(len(rows) == 5, 'all five actual HPE tariff cases')
    uniform = read(scope/'native-boundary/evidence/UNIFORM81-RESULT.json')
    need(45630+1792+112*488+16*486-26910 == 81*1024 == uniform['complete_preconsumer_rank_mass'], 'uniform raw invoice')
    envelope = read(scope/'native-boundary/evidence/QUERY-ENVELOPE-RESULT.json')
    need(envelope['minimum_scalar_pregather_envelope'] == 112 and envelope['scalar_query_rank'] == 8, 'restricted envelope receipt')
    joint = joint_review(scope,followup,I)
    result = dict(status='PASS_SCOPED_CONTROL_PROJECTION_AND_INVOICE_BINDING_REVIEW',
        controls=review_controls, partial_patterns=256, nonempty_partial_failures=255,
        joint_retimings=joint,
        hpe_candidates=rows, candidate_payload_sha256=source_files,
        reviewed_code_sha256={str(p.relative_to(repo)):digest(p) for p in
            [scope/'control-search/search_controls.py',scope/'coupled-boundary/projected_release.py',
             scope/'coupled-boundary/retime_return.py',inv/'actual_profile_screen.py',inv/'retiming_invoice.py',
             inv/'partial_tariffs.py',Path(I.__file__),I.ENGINE_PATH]},
        independent_scope='Direct Python-integer enumeration uses the actual template and no producer control-matrix functions. Affected helper columns are independently propagated through ordered free warp words. Actual emitted profiles are bound to the prices. Rational arithmetic reuses the authenticated retained engine.',
        authorship_disclosure='The reviewer authored native-boundary generators. Their prior fresh-output replay and the independent invoice review are reported, not represented as a second independent native compiler.',
        limitations=['No complete changed native HPE program or profitable residual consumer.',
            'The initial five single-case bindings use base-provider words. The subsequent combined census is rebuilt and checked on both providers, including h556; native HPE completion is still not supplied.',
            'Broad projected release discovery was interrupted; hit count is not an exhaustive barrier.',
            'The 4^9 search excludes only its specified binary controls.',
            'The 255 price rejections concern the specified partial chart formulas and retained invoice.',
            'The scalar envelope bound excludes only fixed scalar pregather before source-dependent native lines.',
            'No new kappa or selected-frontier change.'],
        portable_shared_source_files=['research/complex-local-word-ceiling/ceiling.py'],
        frozen_dependency='research/kappa-global-continuation, including its inputs/kappa-consumer-followup payload')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
