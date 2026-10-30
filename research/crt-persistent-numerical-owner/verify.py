"""Actual varying-precision calls, constructor seal and physical backing census."""
import argparse
from contextlib import contextmanager
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import types

P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok,why):
    if not ok:raise ValueError(why)


def load(name,path):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
    return m


@contextmanager
def sealed(w,e):
    old=e.Port.__init__;oldword=w.Word.__init__;oldarena=w.Arena.__init__
    def forbidden(*a,**k):raise ValueError('sealed physical constructor')
    e.Port.__init__=w.Word.__init__=w.Arena.__init__=forbidden
    try:yield
    finally:e.Port.__init__=old;w.Word.__init__=oldword;w.Arena.__init__=oldarena


def capacities(widths,level,start):
    n=1<<level;mid=start+n//2;stop=start+n
    left=sum(widths[start:mid]);right=sum(widths[mid:stop]);precision=1+left+right
    return ([precision+1,2*left+2*n+2,2*right+2*n+2]+
            [precision+2]*57+[n//2*(2*precision+4)+2]*3)


def run_case(helper,mod,bank,fixture,history):
    w,r,e,producer,caller_module,ref,bridge=mod
    moduli,widths,state,level,start,row=fixture;ell=max(widths)
    n=1<<level;middle=start+n//2;stop=start+n;precision=1+sum(widths[start:stop])
    source=helper.axis_stream(w,r,e,moduli,widths,state)
    dirty=[helper.port(w,e,helper.bits(3*i+1,precision)+[w.RIGHT]) for i in range(8)]
    for i,tape in enumerate(dirty):
        for _ in range(i%3):tape.step(1)
    borrowed=[source,*dirty];snapshot=helper.snapshot(borrowed)
    ids=tuple(id(p.cells) for p in bank.ports);before=helper.traffic([*borrowed,*bank.ports])
    with sealed(w,e):
        lease=bank.open(r,producer,bridge,source,dirty,widths,ell,level,start,row)
        actual=lease.actual
        if actual.active:
            stream=actual.result['stream'].cells;at=1;rows=[]
            for _ in range(n//2):
                need(stream[at]==r.ROOT,'result record');at+=1;pair=[]
                for _ in range(2):
                    pair.append(sum(stream[at+j]<<j for j in range(precision)));at+=precision
                    need(stream[at]==r.WORD_END,'result word delimiter');at+=1
                need(stream[at]==r.RECORD_END,'result record delimiter');at+=1;rows.append(pair)
            need(stream[at]==w.RIGHT,'result end')
            caller=caller_module.Caller(moduli,widths,ell,ref);offsets=caller.offsets(state,level)
            valid=all(state[i]<moduli[i] for i in range(start,middle))
            lower=ref.decode_group(state[start:middle],moduli[start:middle]) if valid else 0
            for key,value in [('lower',lower),('product',math.prod(moduli[start:middle]))]:
                word=actual.result[key]
                need(sum(word.cells[1+j]<<j for j in range(precision))==value,'actual current reconstruction')
            for i,(offset,value) in zip(range(middle,stop),rows):
                need(offset==offsets[i],'actual current offsets')
                need(value==((state[i]+offset)%moduli[i] if state[i]<moduli[i] else state[i]),'actual numerical endpoint')
            numerical=actual.context.arena.meter
        else:rows=[]
        lease.close()
        numerical_actions=(numerical.reads+numerical.writes+numerical.moves) if actual.active else 0
    need(ids==tuple(id(p.cells) for p in bank.ports),'same physical bank backing')
    need(helper.snapshot(borrowed)==snapshot,'all borrowed bytes and heads unchanged')
    need(all(p.head==1 and all(v==w.BLANK for v in p.cells) for p in bank.ports),'entire historical tails blank')
    cap=capacities(widths,level,start) if actual.active else [0]*63
    history[:]=[max(old,new) for old,new in zip(history,cap)]
    lengths=[len(p.cells) for p in bank.ports]
    need(all(size<=bound for size,bound in zip(lengths,history)),'source-derived rolewise capacity')
    actions=helper.traffic([*borrowed,*bank.ports])-before+numerical_actions
    L=2+sum(3*h+4 for h in widths)
    tariff=2**20*(precision+2)**4+2**16*(precision+2)**2+128*(L+precision+n+1)+4096
    need(actions<=tariff,'complete reentry local invoice')
    return dict(precision=precision,active=bool(actual.active),state=list(state),moduli=list(moduli),
                values=rows,role_lengths=lengths,role_grants=list(history),retained=sum(lengths),
                grant=sum(history),actions=actions,time_bound=tariff)


def controls(helper,mod,owner):
    w,r,e,producer,c,ref,bridge=mod
    left=((7,3),(3,2),(1,1),1,0,0)
    right=((3,7),(2,3),(1,1),1,0,0)
    singles=[]
    for fixture in (left,right):
        singles.append(run_case(helper,mod,owner.Bank(w,e),fixture,[1]*63)['retained'])
    bank=owner.Bank(w,e);history=[1]*63
    run_case(helper,mod,bank,left,history)
    combined=run_case(helper,mod,bank,right,history)['retained']
    need(combined>max(singles),'max aggregate capacity is unsound')
    control=['max standalone aggregate rejected']
    def rejects(fn,fragment):
        try:fn()
        except ValueError as error:need(fragment in str(error),'specific control rejection '+fragment)
        else:raise ValueError('undetected control '+fragment)
        control.append(fragment)
    source=helper.axis_stream(w,r,e,left[0],left[1],left[2])
    dirty=[helper.port(w,e,helper.bits(i,6)+[w.RIGHT]) for i in range(8)]
    with sealed(w,e):
        rejects(lambda:bridge.RowEntry(w,r,e,producer,source,dirty,left[1],3,1,0,0),
                'sealed physical constructor')
        lease=bank.open(r,producer,bridge,source,dirty,left[1],3,1,0,0)
        rejects(lambda:bank.open(r,producer,bridge,source,dirty,left[1],3,1,0,0),
                'previous result must retire first')
        lease.close();rejects(lease.close,'single row result retirement')
    class MissingMarker(owner.Bank):
        def take(self,words):
            port=self.ports[self.cursor];self.cursor+=1
            return port  # Actual code mutation: no paid LEFT reinstatement.
    rejects(lambda:run_case(helper,mod,MissingMarker(w,e),left,[1]*63),'unit local movement')
    prior=owner.Bank(w,e)
    prior.ports[1].cells.extend([w.BLANK]*200)  # Supplied initial blank capacity.
    initial=[len(p.cells) for p in prior.ports]
    prior_result=run_case(helper,mod,prior,left,initial)
    rejects(lambda:run_case(helper,mod,prior,left,[1]*63),'source-derived rolewise capacity')
    tail=owner.Bank(w,e)
    run_case(helper,mod,tail,((5,7,11,13),(3,3,4,4),(1,5,0,9),2,0,0),[1]*63)
    tail.ports[3].cells[-1]=w.ONE  # Mutated cleanup leaves a hidden old tail.
    rejects(lambda:run_case(helper,mod,tail,left,[1000]*63),'entire historical tails blank')
    return dict(controls=control,standalone=singles,combined=combined,
                prior_blank_capacity=201,prior_retained=prior_result['retained'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');args=parser.parse_args()
    pins={}
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            h=sha256((ROOT/row['path']).read_bytes()).hexdigest();need(h==row['sha256'],'source SHA256');pins[row['path']]=h
    helper=load('row_fixture',ROOT/'research/crt-mixed-row-entry/verify.py');mod=helper.modules();w,r,e,producer,c,ref,bridge=mod
    owner=load('persistent_owner',P/'owner.py');bank=owner.Bank(w,e);history=[len(p.cells) for p in bank.ports]
    small=((7,3),(3,2),(1,1),1,0,1)
    large=((5,7,11,13),(3,3,4,4),(1,5,0,9),2,0,0)
    fixtures=[small,large,small,((7,3),(3,2),(1,3),1,0,4),((7,3),(3,2),(7,1),1,0,1),((7,3),(3,2),(1,1),1,0,2)]
    rows=[run_case(helper,mod,bank,f,history) for f in fixtures]
    need(rows[0]['retained']<rows[1]['retained']==rows[2]['retained'],'growth then shrink retains backing')
    result=dict(status='PASS_PERSISTENT_NUMERICAL_OWNER',sources=pins,cases=rows,
                controls=controls(helper,mod,owner),
                owner_sha256=sha256((P/'owner.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed receipt drift')
    print(result['status'],[(x['precision'],x['retained'],x['actions']) for x in rows])


if __name__=='__main__':main()
