#!/usr/bin/env python3
"""Fast exact physical replay of the separate balanced eight-bank trial.

The complete literal source circuits are converted independently into exact
X-character monomials, retaining their once-per-field Gaussian phases.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse, copy, hashlib, importlib.util, json, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent/'root-chronology'
from encoded_physical import produce as prefix_source
from quadratic_model_review import qc, literal_x_action

def need(ok,msg):
    if not ok:raise ValueError(msg)

def bridge(left,right,middle,label):
    return [{'kind':'ADD','dst':left,'src':right,'coefficient':'1','label':label+' Hinv sum'},
            {'kind':'SCALE','bank':right,'coefficient':'-2','label':label+' Hinv difference scale'},
            {'kind':'ADD','dst':right,'src':left,'coefficient':'1','label':label+' Hinv difference'},
            {'kind':'SCALE','bank':left,'coefficient':'1/2','label':label+' Hinv left half'},
            {'kind':'SCALE','bank':right,'coefficient':'1/2','label':label+' Hinv right half'},middle,
            {'kind':'ADD','dst':left,'src':right,'coefficient':'1','label':label+' H sum'},
            {'kind':'SCALE','bank':right,'coefficient':'-2','label':label+' H difference scale'},
            {'kind':'ADD','dst':right,'src':left,'coefficient':'1','label':label+' H difference'}]

def bind(e,n):
    if e['kind']in('ADD','SCALE','BANK_SWAP'):return
    op=e.get('exact_operator',e.get('operator'))
    circuit=op.get('one_coordinate_literal_circuit',op.get('one_bit_circuit'))
    need(circuit is not None,'every balanced unary retains a complete literal circuit')
    off,basec=literal_x_action(circuit,n,0)
    cols=[literal_x_action(circuit,n,1<<i)[0]^off for i in range(n)]
    rows=tuple(sum(((col>>i)&1)<<j for j,col in enumerate(cols))for i in range(n))
    if 'global_i_exponent_by_f_mod4'in op:
        globals_=op['global_i_exponent_by_f_mod4']
    else:
        s=2 if op['global_sign']==-1 else 0
        r=op['phase_exponent']
        globals_=[(s+r*(1-f))%4 for f in range(4)]
    g0,delta=globals_[0],(globals_[1]-globals_[0])%4
    need(all((g0+f*delta)%4==globals_[f]for f in range(4)),'literal family has an affine whole-field phase')
    mono=qc.from_function(rows,off,lambda x:literal_x_action(circuit,n,x)[1]+delta,g0)
    for x in[0,(1<<n)-1]+[1<<j for j in range(n)]+[(1<<j)|(1<<k)for j in range(n)for k in range(j+1,n)]:
        y,p=literal_x_action(circuit,n,x)
        need(mono.act(x)==y and mono.q(x)==(p+delta)%4,'literal all-coordinate monomial phase/address')
    rank=qc.rank(mono.polar())
    declared=e.get('native_arity_per_f',e.get('operator',{}).get('native_arity'))
    need(declared is not None and rank==declared,'physical polar rank equals complete native receipt')
    e['x_monomial']=mono.data()
    e['rank_per_f']=rank

def invert(e,n):
    out=copy.deepcopy(e)
    if e['kind']=='ADD':out['coefficient']=str(-F(e['coefficient']))
    elif e['kind']=='SCALE':out['coefficient']=str(1/F(e['coefficient']))
    elif e['kind']=='BANK_SWAP':pass
    else:
        # The exact inverse is fully determined by the complete saved unary,
        # including its once-per-bank phase. Literal circuits invert in reverse.
        out['x_monomial']=qc.decode(e,n).inv().data()
        op=out.get('exact_operator',out.get('operator'))
        key='one_coordinate_literal_circuit'if'one_coordinate_literal_circuit'in op else'one_bit_circuit'
        inv=[]
        for t in reversed(op[key]):
            k=t[0]
            if k=='P':inv.append(['P',list(qc.inverse(tuple(t[1])))])
            elif k=='C':inv.append(['C',t[1],-t[2]])
            elif k=='D':inv.append(['D',t[1],[(-v)%4 for v in t[2]]])
            elif k=='phase':inv.append(['phase',(-t[1])%4])
            else:raise ValueError(k)
        out['inverse_literal_circuit']=inv
    return out

def produce():
    initial=hashlib.sha256((ROOT/'quadratic_charts.py').read_bytes()).hexdigest()
    pref=prefix_source();old=pref['events'];n=pref['ambient_arity'];banks=pref['banks']
    at=next(i for i,e in enumerate(old)if e['label']=='changed cut5 U-=V')
    middle=copy.deepcopy(old[at+1]);middle['label']='balanced cut5 partial-plane R'
    prefix=copy.deepcopy(old[:at])+bridge(1,4,middle,'balanced cut5')+copy.deepcopy(old[at+3:])
    tailpath=HERE.parent/'native-frames'/'ENCODED-STAGE-TAIL.json'
    tail=copy.deepcopy(json.loads(tailpath.read_text())['events'])
    at=next(i for i,e in enumerate(tail)if e.get('label')=='Q')
    need(tail[at-1]['kind']=='ADD'and tail[at-1]['dst']==3 and tail[at-1]['src']==1 and F(tail[at-1]['coefficient'])==-1,
         'direct triangular inverse first cross exact')
    need(tail[at+1]['kind']=='ADD'and tail[at+1]['dst']==3 and tail[at+1]['src']==1 and F(tail[at+1]['coefficient'])==1,
         'direct triangular inverse second cross exact')
    Q=tail[at];Q['bank']=3
    tail=tail[:at-1]+bridge(1,3,Q,'balanced inverse W(Q)')+tail[at+2:]
    events=prefix+tail
    for index,e in enumerate(events):e['event_index']=index;bind(e,n)
    # Full independent original columns, retaining all coefficients at each f
    # residue. Equal normal-form sums imply actual equality; independence of
    # distinct Clifford summands is not assumed.
    actual=qc.replay(events,banks,n)
    E=qc.old_operator({'operator':{'block_permutation':list(range(n//2)),'native_blocks':list(range(n//2)),'sign':1}},n)
    expected=qc.replay([{'kind':'NATIVE','bank':j,'x_monomial':E.data()}for j in range(banks)],banks,n)
    need(actual==expected,'every original input column finishes at the actual full native E for all f')
    inverse=[invert(e,n)for e in reversed(events)]
    Id=qc.replay([],banks,n)
    need(qc.replay(events+inverse,banks,n)==Id==qc.replay(inverse+events,banks,n),'literal complete inverse both orders on every input')
    hist={str(r):sum(e.get('rank_per_f',0)==r for e in events)for r in(2,4)}
    need(hist=={'2':67,'4':1},'complete balanced native bill')
    need(initial==hashlib.sha256((ROOT/'quadratic_charts.py').read_bytes()).hexdigest(),'retimer core stable during independent physical replay')
    return {'status':'PASS_BALANCED_PHYSICAL_EIGHT_BANK_ALL_COLUMNS_ALL_F_BOTH_INVERSES',
            'scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90','width':banks,'banks':banks,'ambient_arity':n,
            'events':events,'prefix_event_count':len(prefix),'tail_event_count':len(tail),
            'histogram':hist,'native_rank_mass':138,'stock':128,'D':-10,
            'literal_inverse':'Reverse events; negate ADD; reciprocate SCALE; invert every full unary monomial and its literal circuit; swaps self inverse.',
            'all_f_phase_binding':'Every literal P/C/even-linear-D/unit circuit is evaluated independently on X characters. Its global fmod4 phase is written as g0+f*delta; Mono represents i^g0 times the tensor of the per-coordinate operator with phase shifted by delta. All complete original columns and both inverse orders are checked in this exact tensor family.',
            'all_input_proof':'A separate all-f lifted Clifford proof for the balanced prefix is in BALANCED-STAGE-TRIAL.json. The present proof directly replays the actual complete physical event word, including SCALE scans and the one-child Q lowering.',
            'source_pins':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in
                           (HERE/'encoded_physical.py',HERE/'ENCODED-PHYSICAL-PREFIX.json',HERE/'encoded_stage.py',
                            HERE/'BALANCED-STAGE-TRIAL.json',tailpath,ROOT/'quadratic_charts.py',HERE/'quadratic_model_review.py')],
            'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'limits':['Direct word has negative stock deficit; no exponent gain is claimed.',
                      'A retimed word needs literal selected-native child lowerings, all-f adapters and contraction-cap splitting.',
                      'No owner, precision, finite-tape or joint BIT contract is supplied.'],
            'no_new_kappa':True}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(produce()));path=HERE/'BALANCED-PHYSICAL-REPLAY-Q3.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_text())==out,'saved balanced physical replay differs')
    print(out['status'])

if __name__=='__main__':main()
