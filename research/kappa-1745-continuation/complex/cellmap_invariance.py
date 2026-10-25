#!/usr/bin/env python3
"""Check all T740 hosted intervals and eliminate a cell-selection ambiguity.

In PR3187's exact eight-stream Fourier operator, all phases of a hosted
owner-child lie in that child's observer-free interval. Therefore permuting
the allocation of its orthonormal axes between helper cells and the residual
cannot alter the combined child phase. A transfer changes the combined child
phase independently of that permutation. This is a scoped operator audit,
not a new supplier or an admission of arbitrary frame selection.

Credits: Nick Petalas / PR3187 operator and authenticated fill, Matarener /
PR3296 remainder projection, Rohan Arun / PR3955 data, Erwan and Claude /
PR4046 binding. New chronology proof/check with OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
AUDIT = HERE.parent/'operator-audit/checkout/research'
sys.path.insert(0,str(AUDIT/'rank7-idle-star-stream-obstruction'))
sys.path.insert(0,str(AUDIT/'pr3190-remainder-stream-obstruction'))
import source as S
import algebra as A
import obstruction as O


def touches(event, local_pairs):
    kind=event['kind']
    if kind=='local_cover_sweep':
        p=local_pairs[event['stage']]
        return (2*p,2*p+1)
    if kind=='bridge':
        return tuple(2*p+s for p in (event['src'],event['dst']) for s in (0,1))
    if kind=='terminal':
        return tuple(range(8))
    # All other data events are phases on individual streams.
    if kind in ('idle_cover_sweep','terminal_Y_translations',
                'bank_padding_cover_sweep','translate_every_live_family'):
        return ()
    raise AssertionError(kind)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=HERE/'CELLMAP-INVARIANCE.json')
    args=ap.parse_args()
    ctx=S.load_context()
    blocks=A.stage_blocks(ctx['template'])
    recipes=S.decode(S.read_bytes(S.ROOT/S.PHASES))['recipes']
    stage_time={(s,r):t for t,(s,r) in enumerate(ctx['order'])}
    local_pairs={e['stage']:e['pair'] for e in ctx['template']['recipe'] if e['kind']=='local'}
    windows={}
    for owner in range(740):
        last=[(-1,-1)]*8
        for stage in range(9):
            t=stage_time[stage,owner]
            for j,e in enumerate(blocks[stage]):
                if e['kind']=='idle_cover_sweep':
                    for side,child in enumerate(e['child_indices']):
                        stream=2*e['pair']+side
                        if str(child) in ctx['plan']['pairs']:
                            assert stream==2*ctx['plan']['pairs'][str(child)]+ctx['plan']['sides'][str(child)]
                        else:
                            assert all(r['idle_children'][child]['rank']==0 for r in recipes)
                        windows[owner,child]=(last[stream],(t,j),stream)
                for stream in touches(e,local_pairs):
                    last[stream]=(t,j)
    vendor=S.PACKAGE/'vendor'
    base=S.decode(S.read_bytes(vendor/'BASE-FILL.json.gz'))['rows']
    edits=S.journal_edits(base,S.decode(S.read_bytes(vendor/'EXCHANGE.json')))
    checked=0; hosted=Counter(); projection=[]
    for index in range(S.TOTAL_ROWS):
        row=edits[index] if index in edits else S.lifted_row(base,index)
        time,helper,owner,child,port,offset=row
        start,end,stream=windows[owner,child]
        assert start<(time,-1)<end,('intervening observation',index,row,start,end)
        stage,callrep=ctx['order'][time]
        width=ctx['providers'][ctx['dispatch'][stage,callrep%74]]['widths'][helper]
        assert 0<=offset and offset+width<=len(recipes[port]['idle_children'][child]['orthogonal_axes'])
        hosted[owner,port,child]+=width
        checked+=1
        if owner==port==0:projection.append(row)
    assert checked==2717280 and projection==ctx['rows']

    raw=S.read_bytes(AUDIT/'pr3934-pr3955-operator-replay/vendor/PR3955-MOVES.json.gz')
    assert hashlib.sha256(raw).hexdigest()=='01e8417b90783f707cd18871be7c615eb9162f356460f07963b5198522aa692b'
    moves=defaultdict(list)
    for owner,port,d,r,v in S.decode(raw)['moves']:
        if owner==0:moves[port].append((d,r,int(v)))

    def collapsed(port,axes,character):
        context=dict(ctx,recipe=recipes[port])
        mat=A.identity()
        for stage in range(9):
            for event in blocks[stage]:
                A.data_event(mat,event,context,axes,character)
        return mat

    witnesses=[]; basis_checks=0
    for port in range(112):
        original={c:list(map(int,e['orthogonal_axes'])) for c,e in enumerate(recipes[port]['idle_children'])}
        final={c:list(vs) for c,vs in original.items()}
        for d,r,v in moves[port]:
            assert v in final[d] and v not in final[r]
            final[d].remove(v);final[r].append(v)
        # Identity selection means the original compact remainder suffices.
        identity_selection=all(v in original[d][hosted[0,port,d]:] for d,r,v in moves[port])
        for bit in range(73):
            character=1<<bit
            before=collapsed(port,original,character)
            assert before==O.scalar(character),('baseline',port,bit)
            after=collapsed(port,final,character)
            basis_checks+=1
            diff=O.diff(before,after)
            if diff:
                witnesses.append({'port':port,'character':str(character),'bit':bit,
                    'identity_selection':identity_selection,'changed_entries':len(diff),
                    'first_changed_entry':diff[0]})
                break
        else:
            raise AssertionError(('no standard-character counterexample',port))
    assert len(witnesses)==112
    assert sum(w['identity_selection'] for w in witnesses)==55
    # The original time-resolved operator and collapsed operator agree on
    # an authenticated positive control, with the actual original host slices.
    residual,hosts=O.residual_and_hosts(ctx)
    original={c:list(map(int,e['orthogonal_axes'])) for c,e in enumerate(recipes[0]['idle_children'])}
    controls=[]
    for character in (0,1,11,1<<72,(1<<73)-1):
        assert O.replay(ctx,blocks,hosts,residual,character)==collapsed(0,original,character)
        controls.append(str(character))
    pins={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        Path(__file__), Path(S.__file__),Path(A.__file__),Path(O.__file__),
        AUDIT/'pr3934-pr3955-operator-replay/vendor/PR3955-MOVES.json.gz')}
    for p in sorted(AUDIT.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts:
            pins[str(p.relative_to(REPO))]=hashlib.sha256(p.read_bytes()).hexdigest()
    result={'status':'PASS_ALL_T740_HOSTED_INTERVALS_AND_ALL_112_OWNER0_PORT_COUNTEREXAMPLES',
        'hosted_rows_checked':checked,'owner_child_windows_checked':len(windows),
        'operator_fact':'Phases on one stream commute, and every hosted phase is after the preceding scalar observation and before its own residual phase. Thus the entire child phase is invariant under any bijection between hosted cells plus residual positions and the original child axes.',
        'consequence':'Every realizable PR3955 reselected cell map with unchanged helper use times has the same transferred-axis operator as the collapsed full-child overlay. All 112 owner-0 ports have exact counterexamples, including all 57 previously untested reselected ports.',
        'scope':'PR3187 exact eight-stream operator, original T740 call chronology, unchanged child event placement and orthonormal axis multiset, PR3955 literal moves. Different chronology, native corrections, changed circuit or non-permutation frames are not excluded.',
        'identity_selection_ports':55,'reselected_ports':57,'changed_ports':112,
        'standard_character_tests_executed':basis_checks,
        'time_resolved_positive_control_characters':controls,
        'port_witnesses':witnesses,'source_pins':pins,
        'new_supplier':False,'new_kappa':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],checked,'rows',len(witnesses),'changed_ports')


if __name__=='__main__':main()
