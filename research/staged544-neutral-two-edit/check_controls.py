#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded assertion-disabled source, dirty-state and sign controls.

This does not regenerate the complete search censuses. verify.py does that.
"""
import hashlib,json
from pathlib import Path
import time,types

P=Path(__file__).resolve().parent
M=types.ModuleType('source_verifier');M.__file__=str(P/'verify.py')
exec(compile((P/'verify.py').read_bytes(),str(P/'verify.py'),'exec'),M.__dict__)
t=time.monotonic();report={}
for tag in ('base','extra'):
    expected=json.loads((P/f'CERTIFICATE-{tag}.json').read_text())
    w=M.S.load(tag);positive,_=M.positive_control(w)
    M.need(M.normal(positive)==expected['positive_control'],'positive control differs')
    controls=M.controls(w)
    M.need(controls==expected['controls'],'negative controls differ')
    n=0
    for key in ('frame_changing_first','adjacent_swapped_gate_seconds','adjacent_third_gate_new_middle'):
        for row in expected[key]['delta_types']:
            delta=tuple([0]+[row['delta'].get(str(k),0) for k in range(1,10)])
            M.need(M.R.all_power_nonnegative(delta),'sign certificate rejected')
            M.need(M.R.caps(delta)==row['caps'],'cap receipt differs')
            M.need([sum(row['caps'][:j]) for j in range(1,9)]==row['prefix_caps'],'prefix receipt differs')
            n+=1
    report[tag]={'dirty_positive_control_words':3,'rejection_controls':controls,
        'retained_delta_certificate_rows':n,'literal_recovery':'pinned source',
        'positive_control_sha256':hashlib.sha256(json.dumps(M.normal(positive),sort_keys=True).encode()).hexdigest()}
print(json.dumps({'status':'PASS_NEUTRAL_TWO_EDIT_CONTROLS','providers':report,
    'seconds':round(time.monotonic()-t,3),'full_search_repeated':False},sort_keys=True))
