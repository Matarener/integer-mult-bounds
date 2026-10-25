#!/usr/bin/env python3
"""A changed-slot positive control with an unchanged complete idle bill.

Six initial idle residuals act before their stream's first observation.
Pulling any of them to the input and then past the scalar-convolution final
operator moves it to a new slot after the terminal exchange. This changes
chronology while preserving the full Fourier operator. No rank is eliminated
or merged; the fixed-capacity packing ceiling remains applicable.

Uses the credited PR3187 exact operator and PR3148 T740 fill. New bounded
retiming control with OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
AUDIT=HERE.parent/'operator-audit/checkout/research'
sys.path.insert(0,str(AUDIT/'rank7-idle-star-stream-obstruction'))
sys.path.insert(0,str(AUDIT/'pr3190-remainder-stream-obstruction'))
import source as S
import algebra as A
import obstruction as O


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=HERE/'RETIMED-INITIAL-SLOTS.json')
    args=ap.parse_args()
    ctx=S.load_context();blocks=A.stage_blocks(ctx['template'])
    residual,hosts=O.residual_and_hosts(ctx)
    initial=(0,2,4,6,8,10)
    streams={c:2*ctx['plan']['pairs'][str(c)]+ctx['plan']['sides'][str(c)] for c in initial}
    assert sorted(streams.values())==list(range(2,8))
    local={e['stage']:e for e in ctx['template']['recipe'] if e['kind']=='local'}
    seen=set();first_slots=[]
    for stage in range(9):
        for event in blocks[stage]:
            k=event['kind']
            if k=='idle_cover_sweep':
                for side,c in enumerate(event['child_indices']):
                    stream=2*event['pair']+side
                    if c in initial:
                        assert stream not in seen
                        first_slots.append(c)
            elif k=='local_cover_sweep':
                p=local[event['stage']]['pair'];seen|={2*p,2*p+1}
            elif k=='bridge':
                seen|={2*p+s for p in (event['src'],event['dst']) for s in (0,1)}
    assert sorted(first_slots)==sorted(initial)
    # Exact finite operator checks use the collapsed original frame phases;
    # CELLMAP-INVARIANCE establishes the time-resolved collapse on every row.
    original={c:list(map(int,e['orthogonal_axes'])) for c,e in enumerate(ctx['recipe']['idle_children'])}
    chars=[0]+[1<<k for k in range(73)]+[11,(1<<73)-1]
    tested=0
    for mask in range(1<<6):
        selected=[initial[j] for j in range(6) if mask>>j&1]
        changed={c:list(vs) for c,vs in original.items()}
        for c in selected:
            for axis in residual[c]:changed[c].remove(axis)
        for character in chars:
            matrix=A.identity()
            for stage in range(9):
                for event in blocks[stage]:A.data_event(matrix,event,ctx,changed,character)
            for c in selected:
                A.phase(matrix,streams[c],sum(A.dot(character,a) for a in residual[c]))
            assert matrix==O.scalar(character),(mask,character)
            tested+=1
    profile_before=Counter(len(vs) for vs in residual.values() if vs)
    profile_after=Counter(len(vs) for c,vs in residual.items() if c not in initial and vs)
    profile_after.update(len(residual[c]) for c in initial if residual[c])
    assert profile_before==profile_after
    manifest=HERE/'CELLMAP-INVARIANCE.json'
    chronology=json.loads(manifest.read_text())
    assert chronology['hosted_rows_checked']==2717280
    result={'status':'PASS_OPERATOR_PRESERVING_INITIAL_TO_ENDPOINT_RETIMING_WITH_ZERO_TARIFF_GAIN',
        'retimed_original_slots':list(initial),'new_slots_after_terminal':[[c,streams[c]] for c in initial],
        'all_slot_subsets_checked':64,'characters_per_subset':len(chars),'exact_matrix_checks':tested,
        'general_operator_argument':'Each selected phase precedes every scalar observation of its stream, so all selected phases F commute to the input. The original complete operator O is one common convolution times I_8. Writing O=G F gives G=O F^-1, which commutes with F. Moving F to the output therefore leaves F G=O.',
        'profile_before_owner0_port0':dict(sorted(profile_before.items())),
        'profile_after_owner0_port0':dict(sorted(profile_after.items())),
        'whole_allocation_rank_histogram_delta':{},
        'packing_scope':'Only the time of existing capacity/width bins changes; their multiset and local supplier are fixed. PR3148 already attains its capacity-only fractional relaxation, so rehosting with these same capacities cannot increase its exponent.',
        'native_scope':'Exact finite eight-stream operator and unchanged rank bill. A new physical-native caller at the moved endpoint slots was not built because the exact tariff gain is zero.',
        'new_kappa':False,
        'source_pins':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(S.__file__),Path(A.__file__),Path(O.__file__),manifest)}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'matrix_checks',tested)


if __name__=='__main__':main()
