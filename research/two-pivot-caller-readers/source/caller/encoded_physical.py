#!/usr/bin/env python3
"""Full physical event interface for the changed native-zero carrier encoder.

Every unary carries its exact one-coordinate Clifford and the global tensor
phase rule. The independent retarded all-f matrix proof is pinned separately.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'native-frames'))
from native_model import Model,ce,mul,phase,need
from handoff_family import build


def produce():
    q=3;n,k=8,7
    _,_,_,base=build(q,True);model=Model(1,k)
    v=sum(1<<j for j in(0,1,2,4))
    rows=[(1<<j)^(v if v>>j&1 else 0)for j in range(model.n)]
    R=ce.perm(model.n,rows)
    addition=[{'kind':'ADD','dst':1,'src':4,'coefficient':'-1','label':'changed cut5 U-=V'},
              {'kind':'ADDRESS_LINEAR','bank':4,'operator':{'address_rows':rows,'native_arity':0},'label':'changed cut5 partial-plane reflection R'},
              {'kind':'ADD','dst':1,'src':4,'coefficient':'1','label':'changed cut5 U+=V'}]
    where=next(i for i,e in enumerate(base)if e['label']=='query5 retain other carrier in b accumulator')
    need(all('query5'not in e['label']or e['kind']!='NATIVE' or 'continuation'not in e['label']for e in base[:where]),
         'encoded bridge precedes the continuation')
    events=copy.deepcopy(base[:where]+addition+base[where:])
    need(events[:where]+events[where+3:]==base,'removing the three declared free events recovers exact baseline trace')
    for index,e in enumerate(events):
        e['event_index']=index
        if e['kind'] in('ADD','BANK_SWAP'):continue
        if e['kind']=='ADDRESS_LINEAR':op=R;exponent=0;global_sign=1
        else:
            data=e['operator'];global_sign=data['sign'];exponent=len(data['native_blocks']);op=model.I
            for j in data['native_blocks']:op=mul(op,model.N if j==0 else model.T[j-1])
            p=data['block_permutation'];rr=[]
            for out in range(k+1):
                inp=p.index(out)
                rr.extend((1<<(2*inp),1<<(2*inp+1)))
            # The event's p maps input plane to output plane; perm uses rows.
            op=mul(op,ce.perm(model.n,rr))
        e['exact_operator']={'one_coordinate_tableau':[list(x)for x in op.tab],
                             'one_coordinate_literal_circuit':op.circuit,
                             'tensor_lift':'global_sign * i^(phase_exponent*(1-f)) * op_1^(tensor f)',
                             'global_sign':global_sign,'phase_exponent':exponent,
                             'f1_native_arity':ce.rank(x for x,z,p in op.tab[model.n:])}
        need(e['exact_operator']['f1_native_arity']==e['operator']['native_arity'],'serialized physical operator rank')
    source=HERE/'ENCODED-STAGE.json'
    need(json.loads(source.read_text())['status']=='PASS_NATIVE_ZERO_ENCODED_STAGE_ALL_COLUMNS_ALL_F','exact source matrix proof exists')
    return {'status':'PASS_FULL_PHYSICAL_ENCODED_PREFIX_EVENT_INTERFACE',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
            'banks':n,'query_stages':k,'ambient_arity':16,'events':events,
            'native_histogram':{'2':61},'rank_mass':122,'stock_if_carriers_finish':128,'D_before_tail':6,
            'changed_cut':{'after_stage':5,'before_event':base[where]['label'],'banks':[1,4],
                           'actual_word':['ADD1-=4','ADDRESS R on4','ADD1+=4'],
                           'R_rows':rows,'retarded_word':'N^-1 R N onbank4 between the two ADDs',
                           'phase':'R is plain ADDRESS for support3p/1q; no Gaussian phase is dropped'},
            'covered_binding':'The original full physical source/fresh trace is pinned by HANDOFF-FAMILY; the only new three events have exactly the cut intertwiner verified in ENCODED-STAGE. The all-f public matrix and full literal inverse are proved there. This file emits actual event operators for independent full replay and retiming.',
            'limits':['This prefix has no cleanup included.','No retiming, extra child fusion or tail saving is claimed.','Any complete trace must include the actual native lowering of the encoded inverse stage and every public reader.'],
            'source_pins':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in(HERE/'handoff_family.py',HERE/'HANDOFF-FAMILY.json',HERE/'encoded_stage.py',source,HERE.parent/'native-frames'/'native_model.py')],
            'no_new_kappa':True}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=produce();out['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=json.loads(json.dumps(out));p=HERE/'ENCODED-PHYSICAL-PREFIX.json'
    if args.write:p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_text())==out,'saved physical encoded trace differs')
    print(out['status'])
if __name__=='__main__':main()
