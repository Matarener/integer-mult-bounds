#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only exact replay; --emit explicitly regenerates an external receipt."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import types
from collections import Counter
from copy import deepcopy
import time

P = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def module(name, path):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value

def authenticate(raw, row):
    require(len(raw) == row['bytes'], 'source length: ' + row['local'])
    require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['local'])
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == row['git_blob'], 'source Git blob: ' + row['local'])

def setup():
    sources = json.loads((P / 'SOURCES.json').read_text())
    for row in sources['snapshots']:
        authenticate((P / row['local']).read_bytes(), row)
    return (module('owned_search', P / 'search.py'),
            module('retained_auditor', P / 'vendor/audit_core.py'),
            module('retained_semantics', P / 'vendor/audit_verify.py'))

def load(tag):
    return json.loads(gzip.decompress((P / 'inputs' / f'BORROW-WORD-43{tag}.json.gz').read_bytes()))

def calculate(tag, progress=False):
    S, C, A = setup()
    word = load(tag)
    C.hygiene(word)
    bill, inventory, *_ = C.frame_bill(word)
    require(bill == {int(r): n for r, n in word['report']['local_profile'].items()}, 'source declared invoice')
    require(S.R.tracing(word)[2] == bill, 'source trace disagreement')
    require(C.derive_cleanup(word) == word['cleanup'], 'source inverse cleanup')
    baseline = S.R.census(word)
    expected = json.loads((P / 'inputs/SINGLE-CENSUS.json').read_text())[tag]
    require(json.loads(json.dumps(baseline)) == expected, 'predecessor single-move census differs')
    require(all(row['certificate'] for row in baseline['deltas']), 'single-move premise failed')
    result = S.compute(word, C, progress)
    proof_rows=result['variable_frame']['profiles']
    if not all(row['certificate'] for row in proof_rows):
        raise ValueError('unresolved combined signs; no obstruction claimed: '+repr(result['variable_frame']['uncertified_witnesses']))
    result['dirty_validation']=dirty_validation(S,C,A,word,result['variable_frame']['states'])
    result['ledger']=ledger(S,C,word,result)
    states=result['variable_frame'].pop('states')
    result['variable_frame']['state_stream_sha256']=S.digest(states)
    result['variable_frame']['first_state']=states[0]
    result['variable_frame']['last_state']=states[-1]

    return {'schema_version': 1, 'provider': tag, 'source_canonical': S.digest(word),
            'source_profile': bill, 'width_inventory': inventory,
            'single_move_candidates': baseline['candidates'],
            'single_census_digest': S.digest(baseline),
            'source_semantics': A.semantics(C, word), 'pair_census': result}

def normal(value):return json.loads(json.dumps(value,sort_keys=True))

def ledger(S,C,word,result):
    bill,widths,_,start,end=C.frame_bill(word)
    primitives={sec:dict(sorted(Counter(g[0] for g in word[sec]).items())) for sec in
                ('precondition','compensation','A','cut','B','restore','cleanup')}
    first=result['variable_frame']['states']
    masses={sum(int(r)*n for r,n in x['profile'].items()) for x in first}
    require(masses=={sum(r*n for r,n in bill.items())},'first rank masses')
    return {'baseline_local_profile':bill,'recursive_children':sum(bill.values()),
      'rank_mass':sum(r*n for r,n in bill.items()),'helper_width_inventory':widths,
      'helper_roles':sum(widths.values()),'dirty_buffers':len(word['helper_final']),
      'live_inputs':C.N-len(word['removed']),'primitive_inventory':primitives,
      'native_warps':len(word['warps']),'initial_operator_corrections':len(word['initial_corrections']),
      'first_recursive_children_range':[min(sum(x['profile'].values()) for x in first),max(sum(x['profile'].values()) for x in first)],
      'all_first_profiles':'Every first profile equals the baseline exactly; the deterministic full state stream is hashed in the receipt.',
      'all_combined_histograms_recorded':'pair_census.variable_frame.profiles',
      'entrance_frames_sha256':S.digest({str(k):str(v) for k,v in start.items()}),
      'exit_frames_sha256':S.digest({str(k):str(v) for k,v in end.items()}),
      'added_gates_helpers_buffers':0,'source_scalar_coefficient_bound':coefficient_bound(word),
      'first_scalar_coefficient_bound':result['dirty_validation']['coefficient_bound'],
      'proved':['Local chronological recursive invoices, fixed native maps/cuts and helper widths',
                'Exact rational first-block equality for every admitted first move on arbitrary dirty inputs',
                'Complete baseline free-operator replay and deterministic first/final replay controls',
                'Recomputed inverse cleanup and full first-word resource inventories in sampled whole-word controls'],
      'unknown':['Fresh native Gaussian/Clifford realization and phase','Physical hosting/allocation and complete owner chronology',
                 'Uniform coefficient/precision/stock/tape costs','All-size compiler, outer/supplier admission','Analytic transfer and BIT H1-H5'],
      'unknown_costs_are_zero':False,'new_supplier_or_kappa':False}

def coefficient_bound(word):
    a=[g for sec in ('A','B','restore') for g in word[sec] if g[0]=='add']
    return {'maximum_numerator_bits':max(abs(g[3]).bit_length() for g in a),
            'maximum_denominator_bits':max(g[4].bit_length() for g in a)}

def dirty_validation(S,C,A,word,states):
    # Local block equality was checked for every first word during the census.
    # Whole-word samples additionally exercise the retained production interpreter.
    samples={0,len(states)-1}
    for sec in S.PHASES:
        group=[i for i,x in enumerate(states) if x['first'][0]==sec]
        if group:
            samples.update((group[0],group[len(group)//2],group[-1]))
    rows=[];bound=coefficient_bound(word);second_blocks=[]
    D=module('dirty_oracle',P/'dirty_blocks.py')
    for ordinal in sorted(samples):
        sec,i,cut,fr,delta=states[ordinal]['first']
        middle=S.R.apply_move(word,sec,i,cut,fr)
        middle['cleanup']=C.derive_cleanup(middle)
        bill,widths,*_=C.frame_bill(middle)
        middle['report']['local_profile']={str(r):n for r,n in bill.items()}
        C.hygiene(middle)
        semantic=A.semantics(C,middle)
        b=coefficient_bound(middle)
        bound={k:max(bound[k],b[k]) for k in bound}
        moved=cut-(cut>i)
        restored=S.R.apply_move(middle,sec,moved,i+(moved<i),word[sec][i][-1])
        restored[sec][i][-1]=deepcopy(word[sec][i][-1])
        restored['cleanup']=C.derive_cleanup(restored)
        restored['report']['local_profile']=deepcopy(word['report']['local_profile'])
        require(restored==word,'literal first undo differs')
        # Exercise an actual interacting second path, with its exact rational block,
        # fresh retained invoice and full arbitrary-dirty endpoint replay.
        registers=set(S.R.touched(word[sec][i]));second=None
        for section in S.PHASES:
            chosen=[j for j,g in enumerate(middle[section]) if g[0]=='add' and registers.intersection(S.R.touched(g))
                    and (section,j)!=(sec,moved)]
            for j,target,d,low,high,sd in S.candidates(middle,section,chosen):
                if target==j:continue
                frame=list(S.R.basis(low));mask=low
                for v in S.R.basis(high):
                    if len(frame)>=d:break
                    if not mask>>v&1:frame.append(v);mask=S.R.span(tuple(frame))
                require(len(frame)==d,'second frame realization')
                final=S.R.apply_move(middle,section,j,target,frame)
                try:fb,fw,*_=C.frame_bill(final)
                except C.AuditFailure:continue
                require(fw==widths,'second helper width drift')
                actual=tuple(fb.get(r,0)-bill.get(r,0) if r else 0 for r in range(10))
                require(actual==sd,'second real invoice differs')
                lo,hi=min(j,target),max(j+1,target)
                check=D.block_equal(middle[section][lo:hi],final[section][lo:hi])
                final['cleanup']=C.derive_cleanup(final);final['report']['local_profile']={str(r):n for r,n in fb.items()}
                C.hygiene(final)
                second={'section':section,'index':j,'cut':target,'frame':frame,'profile':fb,
                        'block':check,'semantics':A.semantics(C,final)}
                break
            if second:break
        require(second is not None,'no legal second control')
        rows.append({'first_state':ordinal,'semantics':semantic,'literal_undo':'PASS','second':second})
    # Meter all first scalar conjugations without replaying complete words.
    for state in states:
        sec,i,cut,fr,_=state['first'];g=word[sec][i]
        from fractions import Fraction
        coefficient=Fraction(g[3],g[4])
        crossed=word[sec][i+1:cut] if cut>i else word[sec][cut:i]
        for h in crossed:
            if h[0]=='scale' and h[1] in S.R.touched(g):
                power=(1 if h[1]==g[1] else -1)*(1 if cut>i else -1)
                coefficient*=Fraction(h[2],h[3])**power
        bound['maximum_numerator_bits']=max(bound['maximum_numerator_bits'],abs(coefficient.numerator).bit_length())
        bound['maximum_denominator_bits']=max(bound['maximum_denominator_bits'],coefficient.denominator.bit_length())
    return {'all_first_dirty_blocks':len(states),'whole_word_samples':rows,'coefficient_bound':bound,
      'proof':'Every first scalar block equals its source on independent rational symbols; unchanged surrounding free operators compose with that equality. Inverse cleanup is rederived; baseline and sampled complete words additionally replay all 723 symbolic inputs.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=('base', 'extra'), required=True)
    parser.add_argument('--emit', type=Path)
    parser.add_argument('--progress', action='store_true')
    args = parser.parse_args()
    result = calculate(args.provider, args.progress)
    if args.emit:
        require(not args.emit.resolve().is_relative_to(P), 'write regenerated receipt outside the package')
        args.emit.write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
    else:
        expected = json.loads((P / f'RESULT-{args.provider}.json').read_text())
        require(json.loads(json.dumps(result)) == expected, 'complete pair receipt differs')
    print(json.dumps({'status': 'PASS_STAGED544_NEUTRAL_FIXED_D2', 'provider': args.provider,
                      'first_counts': result['pair_census']['first_counts'],
                      'result_sha256': hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                      'new_supplier': False}, sort_keys=True))

if __name__ == '__main__':
    main()
