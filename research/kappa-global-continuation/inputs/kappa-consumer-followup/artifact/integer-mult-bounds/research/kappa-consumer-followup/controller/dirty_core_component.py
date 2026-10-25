#!/usr/bin/env python3
"""Exact zero-repair paired codes retaining the actual PR3734 dirty core.

Apache-2.0. Prepared with substantial OpenAI Codex assistance. This local
component deliberately changes data and helper contracts. The backward
transpose companion was proposed by the baseline-invoice investigator.
This is not a complete supplier and establishes no kappa.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import gzip
import json

from check_controller import inverse, load_module, need

HERE = Path(__file__).resolve().parent
PIVOTS = (224, 225, 227, 229, 240, 241, 256, 257)


def run(recovered, out):
    m = load_module(recovered/'modern_native_component.py')
    inp = recovered/'modern-source/inputs'
    receipt = m.read(inp/'NATIVE-RECEIPT.json')
    need(m.digest(inp/'NATIVE-RECEIPT.json') == m.NATIVE_RECEIPT_SHA, 'supplier receipt')
    result = {'status':'PASS_ZERO_REPAIR_PAIRED_DIRTY_CORE', 'providers':{},
              'helper_pivots':list(PIVOTS),
              'scope':'Both local changed contracts only; no physical retention allocation, terminal completion, or kappa admission.'}
    out.mkdir(parents=True, exist_ok=True)
    for name, item in receipt['providers'].items():
        loc = inp/'native-cache'/item['word_sha256']/'local'
        for file in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
            need(m.digest(loc/file) == item['complete_native_files']['local/'+file], 'supplier payload pin')
        word, programs = [m.read(loc/file) for file in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz')]
        R, K, _, J, clean, dirty = m.clean_reconstruction(word, programs)
        old = programs['forward']
        begin, end = old.index(['phase','centers']), old.index(['phase','B'])
        raw_core = old[:begin] + [['phase','centers']] + old[end:]
        before = m.replay(old[:begin])
        H = [{var:a for (var,w),a in before['L',c].items() if var >= 224 and not w} for c in word['centers']]
        query = []
        for r,h in zip(R,H):
            q = r.copy(); m.add(q,h); query.append(q)
        support = sorted({h for row in H for h in row})
        need(len(support) == 106, 'actual helper-query support')
        need(all(word['start'][h] == 0 and word['final'][h] == 1 for h in support), 'query helper native boundary')
        need(all(not any(e[0] == 'residual_adapter' and e[2] == h for e in old) for h in support), 'query helper wrapper')
        minor = [[row.get(h,Q(0)) for h in PIVOTS] for row in H]
        pinv = inverse(minor)
        pext = [{} for _ in range(632)]
        for h,row in zip(PIVOTS,pinv):
            pext[h] = {k:v for k,v in enumerate(row) if v}
        kext = K + [{} for _ in range(520)]
        need(m.matmul(query,pext) == [{k:Q(1)} for k in range(8)], 'helper right inverse')
        need(m.matmul(query,kext) == [{k:Q(14)} for k in range(8)], 'QKext=14I')
        aext = []
        for p,k in zip(pext,kext):
            row = {j:-v for j,v in k.items()}; m.add(row,p,Q(12)); aext.append(row)
        need(m.matmul(query,aext) == [{k:Q(-2)} for k in range(8)], 'QAext=-2I')
        gext = m.matmul(aext,query)
        for p,row in enumerate(gext):m.add(row,{p:Q(1)})
        need(m.matmul(gext,gext) == [{p:Q(1)} for p in range(632)], 'Gext involution')
        d = m.matmul(K,query)
        for p,row in enumerate(d):
            d[p] = {j:-v for j,v in row.items()}; m.add(d[p],{p:Q(1)})
        need(m.matmul(d,gext) == [{p:Q(1)} for p in range(112)], 'D Gext = S')
        code = m.source_code(query,aext,0,1)
        changed = raw_core + code
        native = m.core_frame_check(word,changed)
        need(native == {1:2440,2:725,3:224,4:102,5:20}, 'zero new child invoice')
        actual = m.replay(changed)
        for p in range(632):
            expected = {(j,()):v for j,v in gext[p].items()}
            if 112 <= p < 224:
                m.add(expected,{(j,()):v for j,v in gext[p-112].items()})
            need(actual['L',p] == expected, f'all-column endpoint {name}:{p}')
        need(all(not row for (kind,_),row in actual.items() if kind in 'CZ'), 'private output zero')
        twice = m.replay(code+code)
        need(all(twice['L',p] == {(p,()):Q(1)} for p in range(632)), 'literal code involution')
        payload = json.dumps(changed,sort_keys=True,separators=(',',':')).encode()
        (out/f'DIRTY-CORE-FORWARD-{name}.json.gz').write_bytes(gzip.compress(payload,mtime=0))
        # Actual omitted backward is the inverse transpose of the omitted
        # forward. Postapply D^T on (X,h), in their common FULL exit chart.
        # Since D^2=I, z-D^T E^T y is sent to D^T z-E^T y. The y bank is
        # left unchanged. This is the exact inverse transpose of forward.
        transpose_query = [{p:row[k] for p,row in enumerate(aext) if k in row} for k in range(8)]
        transpose_image = [{k:row[p] for k,row in enumerate(query) if p in row} for p in range(632)]
        transpose_code = m.source_code(transpose_query,transpose_image,0,1)
        gext_t = [{i:row[j] for i,row in enumerate(gext) if j in row}for j in range(632)]
        old_back = programs['backward']
        begin_back, end_back = old_back.index(['phase','centers']), old_back.index(['phase','B'])
        raw_back = old_back[:begin_back] + [['phase','centers']] + old_back[end_back:]
        changed_back = raw_back + transpose_code
        need(m.core_frame_check(word,changed_back) == native, 'backward zero-repair native invoice')
        actual_back = m.replay(changed_back)
        for p in range(632):
            expected = {(j,()):v for j,v in gext_t[p].items()}
            if p < 112:m.add(expected,{(112+p,()):Q(-1)})
            need(actual_back['L',p] == expected, f'backward all-column endpoint {name}:{p}')
        need(all(not row for (kind,_),row in actual_back.items() if kind in 'CZ'), 'backward private zero')
        twice_t = m.replay(transpose_code+transpose_code)
        need(all(twice_t['L',p] == {(p,()):Q(1)} for p in range(632)), 'literal transpose-code involution')
        payload_back = json.dumps(changed_back,sort_keys=True,separators=(',',':')).encode()
        (out/f'DIRTY-CORE-BACKWARD-{name}.json.gz').write_bytes(gzip.compress(payload_back,mtime=0))
        result['providers'][name] = {
            'word_sha256':item['word_sha256'], 'source_program_sha256':m.digest(loc/'LOCAL-PROGRAMS.json.gz'),
            'literal_input_columns':632, 'helper_query_support':support,
            'modified_helper_roles_forward':list(PIVOTS), 'unmodified_helper_roles_forward':400,
            'modified_helper_roles_backward':support, 'unmodified_helper_roles_backward':302,
            'all_query_helpers_I_to_FULL':True, 'new_native_children':0,
            'local_profile':native, 'local_rank_mass':sum(r*n for r,n in native.items()),
            'scalar_bill_forward':m.scalar_bill(changed), 'added_code_scalar_bill_forward':m.scalar_bill(code),
            'scalar_bill_backward':m.scalar_bill(changed_back), 'added_code_scalar_bill_backward':m.scalar_bill(transpose_code),
            'scalar_prefix_forward':m.scalar_prefix(changed), 'scalar_prefix_backward':m.scalar_prefix(changed_back),
            'helper_pivot_minor':[[str(v) for v in row]for row in minor],
            'helper_right_inverse':[[str(v)for v in row]for row in pinv],
            'endpoint_forward':'u=(x,h), q=Rx+Hh; x_out=x-Kq, h_out=h+12P_Hq, y_out=y+x_out',
            'endpoint_backward':'u=(x,h), E selects x; u_out=Gext^T u-E^T y, y_out=y',
            'paired_identity':'B_D=F_D^(-T)',
            'native_frame_chronology':'complete literal core plus terminal code independently checked'}
    (out/'DIRTY-CORE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--recovered',type=Path,default=HERE.parents[3]/'recovered-involutory')
    ap.add_argument('--out',type=Path,default=HERE/'evidence')
    args = ap.parse_args()
    result = run(args.recovered,args.out)
    print(result['status']+': both orientations and actual providers; 632 columns; profile5070; no supplier/kappa admission.',flush=True)
