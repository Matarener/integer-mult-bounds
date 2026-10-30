#!/usr/bin/env python3
"""Bind the retained 63-row outer ledger to the minimum of both suppliers.

The predecessor ledger's literal bit endpoint and complex-binding assertion
are replaced by independently certified input endpoints. All exponent rows
and all17 rejecting variants are retained verbatim. This is conditional
arithmetic, not admission of either supplier's general physical hypotheses.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TASK = HERE.parent
PRIOR = ROOT/'research/kappa-adaptive-continuation/evidence/full-release/admission/package/outer'
COMPLEX = TASK/'sources/PR3959/research/rank7-idle-frame-select/CLAIM.json'
TARGET = F('0.001736738651088946052684')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n')


def edit(source, changes):
    text = source.read_text()
    for before, after in changes:
        need(text.count(before) == 1, 'unique source-bound replacement: '+before[:100])
        text = text.replace(before, after)
    return text


def prepare(invoice_path):
    invoice = json.loads(invoice_path.read_text())
    cx = json.loads(COMPLEX.read_text())
    bit = F(invoice['bit_lower'])
    complex_lower, complex_upper = map(F, cx['complex_root'])
    endpoint = min(bit, complex_lower)
    need(TARGET < endpoint and bit < complex_lower, 'new bit endpoint beats3959 and still binds')
    coefficient = invoice['coefficient_envelopes'][invoice['chosen_envelope']]
    need(coefficient['charged_two_level_bits'] < 210000,
         'explicit finite coefficient remains inside retained semantic umbrella')
    b = endpoint-F(1,10**104)
    kappa = endpoint-F(1,10**46)-F(1,10**70)
    spec = {'outer_refinement':{'endpoint_digits':24},
        'geometry':{'dimension':73,'replicas':cx['T']},
        'expected':{'complex_lower':str(complex_lower),'bit_lower':str(bit),
            'global_profile':cx['profile'],'live':896*cx['T'],'kappa':str(TARGET)},
        'finite_bit_coefficient_envelope':coefficient,
        'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (invoice_path,COMPLEX)}}
    claim = {'status':'conditional finite construction; source and all-size hypotheses retained',
        'binding':'bit','endpoint_lower':str(endpoint),'kappa':str(kappa),
        'target_displayed_endpoint':str(TARGET),'strict_gain_over_target':str(kappa-TARGET),
        'outer_loss':str(F(1,10**46)+F(1,10**70)),
        'inherited_hypotheses':[
            'R437 native packet, chart preparation, recursive-D and all-size source interfaces.',
            'Five-replica pooled helper ownership satisfies the retained native source contracts.',
            'PR3955 cell-to-axis frame freedom and its complete complex supplier realization.',
            'The retained fine-prime-padding, gauge-free and stopped-supplier composition theorems.'
        ],
        'nonclaims':[
            'No full GL64 physical payload enumeration.',
            'No maintainer admission, unconditional bound, or independent human review.'
        ]}
    work = HERE/'package'
    canonical_file(work/'new/SPEC.json', spec)
    canonical_file(work/'CLAIM.json', claim)
    canonical_file(work/'outer/B.json', {'b':str(b),'b_above_endpoint':str(complex_upper),
                                         'live':896*cx['T'],'profile':cx['profile']})
    changes = [
        ("bit=Q('0.001733427039589844234749')", "bit=Q(spec['expected']['bit_lower'])\ncertified_endpoint=min(certified_complex,bit)"),
        ('b=certified_complex-B_GAP', 'b=certified_endpoint-B_GAP'),
        ('assert b<certified_complex<bit', 'assert b<certified_endpoint<=certified_complex and b<bit'),
        ('assert (certified_complex*FLOOR).denominator==1 and 0<certified_complex-EPS*q<Q(1,FLOOR)',
         'assert (certified_endpoint*FLOOR).denominator==1 and 0<certified_endpoint-EPS*q<Q(1,FLOOR)'),
        ("assert row['kappa']==certified_complex-Q(1,FLOOR)-BACKOFF", "assert row['kappa']==certified_endpoint-Q(1,FLOOR)-BACKOFF"),
        ("'halo_umbrella':HALO_UMBRELLA,'complex_lower_short':b,'complex_lower_pinned':certified_complex,",
         "'halo_umbrella':HALO_UMBRELLA,'effective_common_lower':b,'complex_lower_pinned':certified_complex,\n     'bit_lower_pinned':bit,'binding_endpoint':certified_endpoint,"),
        ('Conditional fine-prime padding composition. Fresh native admission is required by verify.py. The cited prime theorem, written gauge-free theorem and inherited all-size interfaces are not proved by this arithmetic. No independent human review is claimed.',
         'Conditional fine-prime padding composition at the minimum of the certified bit and complex endpoints. This arithmetic does not admit either supplier or prove the cited prime theorem, written gauge-free theorem, or inherited physical and all-size interfaces. No independent human review is claimed.')
    ]
    independent_changes = [
        ("spec=json.loads(src.read_text());pinned=F(spec['expected']['complex_lower'])",
         "spec=json.loads(src.read_text());actual_bit=F(spec['expected']['bit_lower']);complex_pinned=F(spec['expected']['complex_lower']);pinned=min(actual_bit,complex_pinned)"),
        ("b=F(BJ['b']);q=b-F(1,T);eff=(q+b)/2;actual_bit=F('0.001733427039589844234749')",
         "b=F(BJ['b']);q=b-F(1,T);eff=(q+b)/2"),
        ('assert 0<q<eff<b<pinned<actual_bit',
         'assert 0<q<eff<b<pinned<=actual_bit and pinned<=complex_pinned'),
        ("the supplier native admission is bound by verify_release.py; inherited all-size assumptions remain.",
         'both supplier native admissions remain explicit hypotheses; this script proves only the exact finite balance equations.')
    ]
    variants = [('check_ledger.py',changes),('independent_check.py',independent_changes)]
    manifest = {}
    for name, pairs in variants:
        src = PRIOR/name
        text = edit(src,pairs)
        if name == 'independent_check.py':
            text = "if not __debug__: raise RuntimeError('Assertions must be enabled')\n"+text
        out = work/'outer'/name
        out.write_text(text)
        manifest[name] = {'original':src.relative_to(ROOT).as_posix(),
            'original_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'bound_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'source_replacements':[{'from':a,'to':b} for a,b in pairs],
            'added_assertions_enabled_guard':name=='independent_check.py'}
    canonical_file(HERE/'BINDING.json',manifest)
    return claim


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--invoice',type=Path,default=TASK/'COMPLETE-INVOICE.json')
    a=p.parse_args()
    result=prepare(a.invoice.resolve())
    print(json.dumps({'status':'PREPARED_MINIMUM_SUPPLIER_OUTER_LEDGER','kappa':result['kappa']}))
