#!/usr/bin/env python3
"""Bind a fixed-word T16 replay to the entire selected paid invoice.

This checks accounting and proof-scope continuity, not placement or root proofs.
"""
import argparse
import gzip
import hashlib
import json
import tarfile
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

BASE_ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
IDENTITIES = {'template_sha256', 'owner_audit_sha256', 'controller_audit_sha256'}
STAGES = ['restore-parent', 'bind8', 'lift16', 'bind', 'emit', 'audit', 'invoice',
          'assembly', 'admission-controls', 'bit-supplier-controls', 'independent-t16']
CONTROLS = {'admission': 69, 'bit_supplier': 12, 'independent_t16': 6, 'controller_mutations': 15}
LIMIT = 2 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    need(path.is_file() and path.stat().st_size <= 16 * LIMIT, 'file size: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    need(path.is_file() and path.stat().st_size <= LIMIT, 'JSON size: ' + str(path))
    return json.loads(path.read_bytes())


def selected(main):
    archive = main / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    need(sha(archive) == BASE_ARCHIVE_SHA, 'selected archive changed')
    names = ['global/audit/PREFIX-AND-INVOICE.json', 'global/audit/OWNERS-AND-PROFILE.json',
             'ASSEMBLY.json', 'REPLAY.json']
    result = {}
    with tarfile.open(archive) as source:
        for name in names:
            member = source.getmember('candidate/strict/' + name)
            need(member.isfile() and member.size <= LIMIT, 'selected member: ' + name)
            with source.extractfile(member) as stream:
                result[name] = json.loads(stream.read(LIMIT + 1))
    return result


def invoice_equal(old, new):
    need(set(old) == set(new), 'invoice field inventory changed')
    changed = [key for key in old if old[key] != new[key]]
    need(set(changed) <= IDENTITIES, 'unaccounted invoice delta: ' + ', '.join(changed))
    need(all(new['strict_checks'].values()), 'finite invoice obligation failed')
    need(new['physical'] == new['live'] + new['helpers'] + new['centres'] + 2, 'physical identity')
    need(new['physical_stock_identity'] == old['physical_stock_identity'], 'private stock changed')
    return sorted(changed)


def physical_margin(invoice, independent):
    actual = invoice['physical']
    conservative = independent['physical']
    need(actual == 14826 and conservative == 14850, 'actual versus conservative stock')
    need(conservative - actual == 24, 'inherited conservative namespace padding')
    group = 2 ** (36 * 36)
    for index in range(1, 37):
        group *= 2 ** (2 * index) - 1
    bits = [(group * count).bit_length() for count in (actual, conservative)]
    need(bits == [2642, 2642], 'physical stock rounding changed')
    row = 2 * bits[0] + 9909 + 252 + 2 * invoice['charged_prefix_bits']
    need(row == invoice['finite']['physical_row_coefficient'] == 16469 < 20161, 'row bill')
    need(independent['physical_row_coefficient'] == row, 'conservative row bill')
    return {'actual': actual, 'conservative': conservative, 'stock_bits': bits, 'row': row}


def intervals(assembly, baseline):
    need(assembly['surcharge_model'] == baseline['surcharge_model'], 'surcharge premise changed')
    need(assembly['bit_supplier'] == baseline['bit_supplier'], 'bit supplier changed')
    need(assembly['bit_lower'] == baseline['bit_lower'], 'bit endpoint changed')
    need(assembly['scope'] == baseline['scope'], 'weaker or changed proof scope')
    for key in ('controls', 'conservative_controls', 'model_controls'):
        need(assembly[key] == baseline[key], 'missing model control: ' + key)
    moments = assembly['moments'] + assembly['conservative_moments']
    need(len(moments) == 6, 'both supplier and conservative cap coverage')
    caps = [('bit', True, assembly['bit_lower']), ('complex', False, assembly['complex_lower']),
            ('conservative_complex', True, assembly['conservative_complex_lower'])]
    need(assembly['moments'][:2] == baseline['moments'][:2], 'unchanged bit moment invoice')
    for index, (side, surcharge, endpoint) in enumerate(caps):
        for advance in range(2):
            item = moments[2 * index + advance]
            need((item['side'], item['surcharge'], item['accept']) ==
                 (side, surcharge, advance == 0), 'cap model or rejection coverage')
            need(Fraction(item['endpoint']) == Fraction(endpoint) + advance * Fraction(1, 10**24),
                 'cap endpoint binding')
            for engine in ('mercator', 'base_two'):
                lo, hi = map(Fraction, item[engine])
                need(lo <= hi, 'reversed interval')
                need(hi < 0 if item['accept'] else lo > 0, 'unproved interval sign')
    for key in ('outer', 'conservative_outer'):
        need(set(assembly[key]) == set(baseline[key]) and len(assembly[key]) == 47, 'outer coverage')
        need(all(Fraction(value) > 0 for value in assembly[key].values()), 'nonpositive outer slack')
    for key in ('bootstrap', 'conservative_bootstrap'):
        need(len(assembly[key]) == 7, 'recursive bootstrap coverage')
        need(all(Fraction(step['gap']) > 0 and int(step['cutoff_log2']) > 0
                 for step in assembly[key]), 'recursive bootstrap margin')


def bind(strict, assembly, invoice, owner, controller, replay):
    paths = {'owner_audit': strict / 'global/audit/OWNERS-AND-PROFILE.json',
             'fresh_invoice': strict / 'global/audit/PREFIX-AND-INVOICE.json'}
    for key, path in paths.items():
        need(assembly['input_sha256'][key] == sha(path), 'assembly input: ' + key)
    need(invoice['owner_audit_sha256'] == sha(paths['owner_audit']), 'owner invoice binding')
    need(invoice['controller_audit_sha256'] == sha(strict / 'global/audit/ASYNC-AUDIT.json'),
         'controller invoice binding')
    need(owner['controller_audit_sha256'] == invoice['controller_audit_sha256'], 'controller owner binding')
    template = strict / 'global/hosted/GLOBAL-TEMPLATE.json.gz'
    need(template.stat().st_size <= 16 * LIMIT, 'compressed template size')
    with gzip.open(template, 'rb') as stream:
        payload = stream.read(64 * LIMIT + 1)
    need(len(payload) <= 64 * LIMIT, 'expanded template size')
    identity = hashlib.sha256(payload).hexdigest()
    need(all(item['template_sha256'] == identity
             for item in (assembly, invoice, owner, controller)), 'template content binding')
    profile = assembly['complex_profile']
    need(profile == owner['paid_profile'] == controller['complex_profile'] == replay['complex_profile'],
         'profile receipt binding')
    need(sum(int(rank) * count for rank, count in profile.items()) == 1041408, 'rank mass')
    need(owner['rank_mass'] == 1041408 and owner['deficit'] == 5120, 'recursive rank invoice')
    need(replay['roles'] == owner['hosted_residuals'] == 69120, 'whole helper role bill')
    need(replay['complete_invocations'] == controller['complete_invocations'] == 144, 'whole call bill')
    need(replay['controls'] == CONTROLS, 'strict controls')
    need(controller['actual_orthogonal_73column_maps'] == owner['actual_73column_sigmas']
         == replay['actual_73_axis_charts'], 'actual chart bill')
    stages = read(strict / 'STAGES.json')
    need(stages == replay['stages'] and [item['name'] for item in stages] == STAGES, 'stage coverage')
    for item in stages:
        need(item['exit_code'] == 0 and sha(strict / (item['name'] + '.log')) == item['log_sha256'],
             'completed stage log: ' + item['name'])


def data_binding(strict, replay):
    data = strict.parent / 'source/data'
    spec = read(data / 'SPEC.json')
    hashes = {name: sha(data / name) for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json')}
    need(replay['spec_sha256'] == hashes['SPEC.json'], 'actual nominated SPEC')
    need(spec['data']['owners_sha256'] == hashes['OWNERS.json.gz'], 'nominated owner bytes')
    need(spec['data']['plan_sha256'] == hashes['PLAN.json'], 'nominated plan bytes')
    need(spec['expected']['kappa'] == replay['kappa'], 'nominated headline')
    need(spec['expected']['global_profile'] == replay['complex_profile'], 'nominated paid profile')
    need(spec['expected']['actual_73column_sigmas'] == replay['actual_73_axis_charts'],
         'nominated chart count')
    return hashes


def score_fields(score, scorer, assembly, strict):
    need(score['status'] == 'PASS_INDEPENDENT_T16_EXACT_SCORE', 'independent score status')
    need(score['scorer_sha256'] == sha(scorer), 'independent scorer source')
    need(score['assembly_sha256'] == sha(strict / 'ASSEMBLY.json'), 'independent score revision')
    need(score['complex_profile'] == assembly['complex_profile'], 'independent score paid profile')
    need(Fraction(score['kappa']) == Fraction(assembly['kappa']), 'independent score headline')
    expected_sources = data_binding(strict, read(strict / 'REPLAY.json'))
    expected_sources.update({
        'PREFIX-AND-INVOICE.json': sha(strict / 'global/audit/PREFIX-AND-INVOICE.json'),
        'OWNERS-AND-PROFILE.json': sha(strict / 'global/audit/OWNERS-AND-PROFILE.json'),
        'PR589-EXPECTED.json': assembly['input_sha256']['package:inputs/PR589-EXPECTED.json']})
    need(score['source_sha256'] == expected_sources, 'independent score complete input closure')
    for report, bootstrap, outer in [('outer', 'bootstrap', 'outer'),
                                     ('conservative_outer', 'conservative_bootstrap', 'conservative_outer')]:
        need(score[report]['bootstrap'] == assembly[bootstrap], 'independent bootstrap revision')
        need(score[report]['slacks'] == assembly[outer], 'independent complete outer revision')
    for side, endpoint in [('bit', 'bit_lower'), ('complex', 'complex_lower'),
                           ('conservative_complex', 'conservative_complex_lower')]:
        need(Fraction(score[side][0]['endpoint']) == Fraction(assembly[endpoint]),
             'independent supplier cap: ' + side)
    return expected_sources


def score_binding(path, scorer, assembly, strict):
    score = read(path)
    sources = score_fields(score, scorer, assembly, strict)
    return {'score_sha256': sha(path), 'scorer_sha256': score['scorer_sha256'],
            'assembly_sha256': score['assembly_sha256'], 'source_sha256': sources}


def score_controls(path, scorer, strict):
    score, assembly = read(path), read(strict / 'ASSEMBLY.json')
    rejected = []
    cases = [('scorer_sha256', '0' * 64), ('assembly_sha256', '0' * 64),
             ('source_sha256', dict(score['source_sha256'], **{'OWNERS.json.gz': '0' * 64})),
             ('complex_profile', {'1': 1})]
    for key, value in cases:
        mutant = deepcopy(score)
        mutant[key] = value
        try:
            score_fields(mutant, scorer, assembly, strict)
        except ValueError:
            rejected.append(key)
    need(len(rejected) == 4, 'score revision controls did not reject all four faults')
    return rejected


def review(main, strict):
    baseline = selected(main)
    invoice = read(strict / 'global/audit/PREFIX-AND-INVOICE.json')
    assembly, replay = read(strict / 'ASSEMBLY.json'), read(strict / 'REPLAY.json')
    owner = read(strict / 'global/audit/OWNERS-AND-PROFILE.json')
    controller = read(strict / 'global/audit/ASYNC-AUDIT.json')
    independent = read(strict / 'INDEPENDENT-T16.json')
    need(independent['profile'] == assembly['complex_profile'], 'independent placement profile')
    need(independent['actual_73_axis_charts'] == replay['actual_73_axis_charts'],
         'independent placement charts')
    changed = invoice_equal(baseline['global/audit/PREFIX-AND-INVOICE.json'], invoice)
    intervals(assembly, baseline['ASSEMBLY.json'])
    old_inputs, new_inputs = baseline['ASSEMBLY.json']['input_sha256'], assembly['input_sha256']
    need(set(old_inputs) == set(new_inputs), 'assembly source inventory changed')
    for key in old_inputs:
        if key not in ('owner_audit', 'fresh_invoice'):
            need(old_inputs[key] == new_inputs[key], 'changed arithmetic or bit source: ' + key)
    old_owner = baseline['global/audit/OWNERS-AND-PROFILE.json']
    for key in ('provider_phase_semantic_sha256', 'provider_artifact_semantic_sha256'):
        need(owner[key] == controller[key] == old_owner[key], 'changed supplier program: ' + key)
    need(controller['all_provider_program_phase_and_wrapper_bindings'], 'unbound local realization')
    need(set(owner['source_artifacts']) == set(old_owner['source_artifacts']), 'provider source inventory')
    for name, digest in owner['source_artifacts'].items():
        path = (strict / 'global/base' / name).resolve()
        need(path.is_relative_to((strict / 'global/base').resolve()) and sha(path) == digest,
             'actual provider source: ' + name)
    bind(strict, assembly, invoice, owner, controller, replay)
    need(assembly['kappa'] == replay['kappa'], 'headline receipt binding')
    selected_kappa = Fraction(baseline['ASSEMBLY.json']['kappa'])
    kappa = Fraction(assembly['kappa'])
    need(kappa > selected_kappa, 'no improvement over selected')
    return {'status': 'PASS_T16_COMPLETE_INVOICE_AND_SCOPE_CONTINUITY',
            'kappa': str(kappa), 'selected_kappa': str(selected_kappa),
            'delta_selected': str(kappa - selected_kappa), 'changed_invoice_fields': changed,
            'physical_padding': physical_margin(invoice, independent),
            'frozen_data_sha256': data_binding(strict, replay),
            'assembly_sha256': sha(strict / 'ASSEMBLY.json'),
            'invoice_sha256': sha(strict / 'global/audit/PREFIX-AND-INVOICE.json'),
            'scope': 'Accounting and receipt-binding check only. Requires separately checked placement, '
                     'independent numerical scoring, source closure and inherited selected assumptions.'}


def controls(main, strict):
    baseline = selected(main)['global/audit/PREFIX-AND-INVOICE.json']
    actual = read(strict / 'global/audit/PREFIX-AND-INVOICE.json')
    rejected = []
    for field in ('selected_real_component_primitives', 'selected_coefficient_work_primitive_count',
                  'wrapper_elementary_factors_charged', 'conservative_pervertex_used', 'charged_prefix_bits'):
        mutant = deepcopy(actual)
        mutant[field] -= 1
        try:
            invoice_equal(baseline, mutant)
        except ValueError:
            rejected.append(field)
    mutant = deepcopy(actual)
    mutant['unpriced_charge'] = 0
    try:
        invoice_equal(baseline, mutant)
    except ValueError:
        rejected.append('unpriced_charge')
    need(len(rejected) == 6, 'invoice controls did not reject all six faults')
    assembly = read(strict / 'ASSEMBLY.json')
    baseline_assembly = selected(main)['ASSEMBLY.json']
    for field, value in [('surcharge_model', {'complex': False, 'bit': False}),
                         ('moments', assembly['moments'][2:]), ('scope', 'unconditional theorem')]:
        mutant = deepcopy(assembly)
        mutant[field] = value
        try:
            intervals(mutant, baseline_assembly)
        except ValueError:
            rejected.append(field)
    need(len(rejected) == 9, 'scope or cap controls did not reject all three faults')
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, required=True)
    parser.add_argument('--strict', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--score', type=Path, help='Worker3 code-disjoint exact score for this assembly')
    parser.add_argument('--scorer', type=Path, help='Exact scorer source named by that score')
    args = parser.parse_args()
    need(bool(args.score) == bool(args.scorer), '--score and --scorer are required together')
    result = review(args.main.resolve(), args.strict.resolve())
    result['reviewer_sha256'] = sha(Path(__file__).resolve())
    result['controls_rejected'] = controls(args.main.resolve(), args.strict.resolve())
    if args.score:
        result['independent_score_binding'] = score_binding(
            args.score.resolve(), args.scorer.resolve(), read(args.strict / 'ASSEMBLY.json'),
            args.strict.resolve())
        result['score_controls_rejected'] = score_controls(
            args.score.resolve(), args.scorer.resolve(), args.strict.resolve())
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['kappa'])


if __name__ == '__main__':
    main()
