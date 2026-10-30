"""Check the min-cut proof, actual program, phases and complete price.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import random
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import optimize as O
import physical


def check_plan(word,folded,plan):
    inv=O.inventory(word); c=word['canonical']; folded=set(folded)
    O.need(not folded.intersection(inv['anchored']),'Protected source coframe')
    frame=lambda f:0 if f in folded else f
    O.need(plan['folded_frames']==sorted(folded),'Exact coframe assignment')
    O.need(plan['main_normalizers']=='source/INTERSECTION153-ROUND3-MAIN-NORMALIZERS.json.gz','Retained actual main adapters')
    ledgers={}
    for direction,old in word['programs'].items():
        new=plan['programs'][direction];O.need(len(old)==len(new),'Every chronological source record')
        current={('L',i):frame(f)for i,f in enumerate(c['start'])};current['C',0]=None
        paid=Counter();passes=0;scalar=Counter();exponent=0
        for original,event in zip(old,new):
            kind=original[0]
            if kind=='scalar':
                gate=original[1];f=frame(original[2]);target=tuple(gate[1])
                O.need(event==['scalar',gate,f],'Unchanged scalar action at its new common coframe')
                scalar[gate[0]]+=1
                if gate[0]=='clear':O.need(target==('C',0),'Only the owned field is cleared');current[target]=f
                else:
                    O.need(current[target]==f,'Scalar target coframe')
                    if gate[0]in('copy','add'):O.need(current[tuple(gate[2])]==f,'Scalar source coframe')
                    if gate[0]=='copy':O.need(target==('C',0),'Only the owned field is overwritten');exponent+=1
                    else:
                        coefficient=Q(gate[3],gate[4])if gate[0]=='add'else Q(gate[2],gate[3])
                        bound=1+abs(coefficient);power=0
                        while Q(2)**power<bound:power+=1
                        exponent+=power
            elif kind in('climb','center'):
                if kind=='climb':role=['L',original[2]];a,b=original[3:5]
                else:role=['C',original[1]];a,b=original[2:4]
                a,b=frame(a),frame(b);key=direction+':transport:'+str(a)+':'+str(b)
                O.need(event==['transport',role,a,b,key],'Complete physical transport record')
                O.need(current[tuple(role)]==a,'Transport chronology');current[tuple(role)]=b
                rank=plan['maps'][key]['rank'];expected=abs(inv['dims'][b]-inv['dims'][a])
                O.need(rank==expected and rank<=7,'Actual grade and strict child cap')
                if rank:paid[rank]+=1
                passes+=2 if rank else 1
            elif kind=='warp':
                _,role,op,a,b=original;key=direction+':warp:'+':'.join(map(str,(op,a,b)))
                O.need(event==['native',role,a,b,key]and frame(a)==a and frame(b)==b,'Unchanged native map')
                O.need(current[tuple(role)]==a and plan['maps'][key]['rank']==0,'Ordinary native warp at the actual cut')
                current[tuple(role)]=b;passes+=1
            else:O.need(event==original and kind in('phase','adapter'),'Retained source marker')
        O.need([current['L',i]for i in range(632)]==[frame(f)for f in c['final']],'Complete final coframe list')
        O.need(dict(sorted(paid.items()))==O.profiles(word,folded)['paid'],'Complete chronological paid histogram')
        ledgers[direction]=dict(scalar_records=dict(sorted(scalar.items())),monomial_passes=passes+448+816,
                               main_adapter_passes=448,helper_adapter_passes=816,scalar_norm_envelope_power_of_two=exponent,
                               retained_payload_fields=633)
    O.need(len(plan['helpers'])==408 and [x['role']for x in plan['helpers']]==list(range(224,632)),'Every independent helper exactly once')
    target=Counter()
    for row in plan['helpers']:
        role=row['role'];a,b=c['start'][role],c['final'][role];rank=O.grade(a,b,folded,inv['dims'])
        O.need((row['start'],row['end'],row['rank'])==(frame(a),frame(b),rank),'Actual complete helper endpoint debit and replacement')
        O.need(set(row['orientations'])=={'forward','backward'},'Both helper normalizers')
        target[rank]+=1
    O.need(dict(sorted(target.items()))==O.profiles(word,folded)['targets'],'Complete productive histogram')
    return ledgers


def objective_checks(word,inv,cuts,weights):
    costs=[];cases=0;rng=random.Random(20261026)
    for branch in cuts['branches']:
        net=O.network(word,inv,weights,branch['branch']);cost=O.check_flow(net,branch['flow'])
        O.need(cost==branch['objective'],'Saved branch optimum')
        folded=O.folded_from(net,branch['flow'],inv)
        O.need(folded==branch['folded'],'Saved branch assignment')
        if branch['feasible']:
            O.need(max(O.profiles(word,set(folded))['paid'])<=7,'Feasible branch child cap')
            O.need(cost==O.grid_cost(O.profiles(word,set(folded)),weights),'Source bill equals cut minimum')
        else:
            O.need(cost>O.INFINITY//2,'Every cap-feasible objective is below this branch bound')
            forced={f for f,x in zip(inv['branch'],branch['branch'])if x}
            violations=[e for e in word['programs']['forward']if e[0]=='climb'and e[3]in forced and e[4]in inv['anchored']and inv['dims'][e[4]]==8]
            O.need(violations,'Independent literal event forces an H8 in this branch')
        costs.append(cost)
        for _ in range(64):
            folded={f for f,v in zip(inv['branch'],branch['branch'])if v}
            folded.update(f for f in net['variables']if rng.getrandbits(1))
            side={net['source']}|{i for i,f in enumerate(net['variables'])if f not in folded}
            cut=net['constant']+sum(cap for u,v,cap in net['edges']if u in side and v not in side)
            actual=O.grid_cost(O.profiles(word,folded),weights)
            bad=sum(e[0]=='climb'and O.grade(e[3],e[4],folded,inv['dims'])>7 for e in word['programs']['forward'])
            O.need(cut==actual+bad*(O.INFINITY-weights[8]),'Separate literal histogram and binary-network objective')
            cases+=1
    O.need(cuts['best_branch']==min(range(4),key=lambda i:costs[i]),'Best of every binary branch')
    return cases


def gain_interval(old,new,bounds):
    counts={r:old['paid'].get(r,0)-new['paid'].get(r,0)+new['targets'].get(r,0)-old['targets'].get(r,0)for r in range(1,9)}
    lo=sum(v*bounds[r][int(v<0)]for r,v in counts.items())
    hi=sum(v*bounds[r][int(v>0)]for r,v in counts.items())
    return dict(coefficients=counts,lower=str(Q(lo,O.SCALE)),upper=str(Q(hi,O.SCALE)))


def tail_checks(old,new):
    lower_s=Q(6,5)-O.SAVING;upper_s=Q(6,5);upper=Q(0)
    for r in range(1,8):
        count=new['paid'].get(r,0)-old['paid'].get(r,0)
        if count:
            lo,hi=O.general_power_interval(r,upper_s if count>0 else lower_s)
            upper+=count*(hi if count>0 else lo)
    rounded=Q(-((-upper.numerator*10**9)//upper.denominator),10**9)
    O.need(rounded<137,'Complete paid higher-moment change below137')
    O.need(Q(99,100)**2*48>47,'All changed helper targets add more than47')
    O.need(Q(99,100)*3066>3000,'Old helper t-moment exceeds3000 per call')
    gamma=(Q(31,32)*3000+Q(548,7))/(3000+47)
    O.need(gamma==Q(7597,7756)<Q(49,50),'The full changed source preserves the strict gamma guard')
    extra=192*Q(56,81)*(1-O.SAVING*Q(7,10))
    O.need(extra>132 and Q(99,100)*918-Q(8343,10)>74,'Strict signed gain exceeds206 C')
    return dict(paid_higher_moment_upper=str(rounded),productive_t_moment_gain_lower=47,
                gamma_upper=str(gamma),gamma_guard='49/50',delta='strictly below old delta',
                signed_gain_lower='206*C for 0<C<=351/100000')


def rejecting_controls(word,inv,cuts,plan,folded):
    rejected=[]
    def reject(name,function):
        try:function()
        except (ValueError,KeyError):rejected.append(name)
        else:raise ValueError('Control accepted: '+name)
    net=O.network(word,inv,[x[0]for x in cuts['power_intervals']],cuts['branches'][0]['branch'])
    bad=deepcopy(cuts['branches'][0]['flow']);bad['flows'][0]+=1
    reject('flow_conservation',lambda:O.check_flow(net,bad))
    bad=deepcopy(cuts['branches'][0]['flow']);bad['source_side'].remove(net['source'])
    reject('cut_source',lambda:O.check_flow(net,bad))
    bad=deepcopy(cuts['branches'][0]['flow']);bad['value']+=1
    reject('flow_value',lambda:O.check_flow(net,bad))
    alterations=[('missing_event',lambda p:p['programs']['forward'].pop()),
                 ('missing_helper',lambda p:p['helpers'].pop()),
                 ('old_helper_credit',lambda p:p['helpers'][0].update(rank=p['helpers'][0]['rank']+1)),
                 ('wrong_main_adapter',lambda p:p.update(main_normalizers='unproved')),
                 ('wrong_assignment',lambda p:p['folded_frames'].append(2))]
    for name,alter in alterations:
        bad=deepcopy(plan);alter(bad);reject(name,lambda:check_plan(word,folded,bad))
    bad=deepcopy(plan);key=next(k for k,v in bad['maps'].items()if v['rank']>0);bad['maps'][key]['rank']=0
    reject('unpaid_query',lambda:check_plan(word,folded,bad))
    reject('protected_coframe',lambda:check_plan(word,set(folded)|{2},plan))
    P=physical.load('control_prune',ROOT/'source/prune_native.py');ce=physical.load('control_clifford',ROOT/'source/clifford_exact.py')
    key='forward:transport:0:0';recipe=deepcopy(plan['maps'][key]);recipe['left']['phase']=(recipe['left']['phase']+1)%4
    reject('absolute_phase',lambda:physical.decode_recipe(P,ce,recipe,ce.canonical_frame(9,[])))
    return rejected


def run():
    word=O.source();inv=O.inventory(word);cuts=json.loads((ROOT/'CUTS.json').read_text());bounds=O.power_intervals()
    O.need(cuts['saving']==str(O.SAVING)and cuts['scale']==O.SCALE and cuts['power_intervals']==bounds,'Exact power intervals and objective')
    O.need(cuts['free_frames']==inv['free']and cuts['branch_frames']==inv['branch'],'Complete decision domain')
    cases=objective_checks(word,inv,cuts,[x[0]for x in bounds]);folded=cuts['branches'][cuts['best_branch']]['folded']
    O.need(folded==[59,60,61,62,63,64],'Published six-line assignment')
    old=O.profiles(word,set());paper=O.profiles(word,{59,60});new=O.profiles(word,set(folded))
    O.need(paper['paid']=={1:1810,2:523,3:418,4:139,6:12,7:8}and paper['targets']=={3:26,4:2,7:12,8:368},'Independent reconstruction of PR5687')
    headroom=Q(sum(count*(bounds[rank][1]-bounds[rank][0])for rank,count in new['paid'].items())+408,O.SCALE)
    O.need(str(headroom)==cuts['objective_headroom_upper'],'Certified full-domain real-objective headroom')
    plan=json.loads(gzip.decompress((ROOT/'CONSTRUCTION.json.gz').read_bytes()))
    ledger=check_plan(word,folded,plan);new_plan,receipt=physical.build(set(folded),plan)
    new_plan=json.loads(json.dumps(new_plan));receipt=json.loads(json.dumps(receipt))
    O.need(plan==new_plan,'Complete source-derived physical program and matcher inventory')
    O.need(receipt==json.loads((ROOT/'PHYSICAL.json').read_text()),'Physical receipt')
    result=dict(status='PASS_RESTRICTED_GAUSSIAN_COFRAME_MINCUT',saving=str(O.SAVING),folded_frames=folded,
                free_frames=len(inv['free']),anchored_frames=len(inv['anchored']),all_binary_assignments='2^423',
                cap_infeasible_branches=3,objective_conversion_cases=cases,objective_headroom_upper=str(headroom),
                original=old,paper=paper,new=new,old_to_paper_gain=gain_interval(old,paper,bounds),
                old_to_new_gain=gain_interval(old,new,bounds),paper_to_new_gain=gain_interval(paper,new,bounds),
                tail_transfer=tail_checks(old,new),ordinary_ledger=ledger,physical=receipt,
                rejecting_controls=rejecting_controls(word,inv,cuts,plan,folded),
                scope='Complete source-preserving binary coframe class at C=.00351 with rank-seven children; no whole caller or kappa admission.')
    return json.loads(json.dumps(result))


if __name__=='__main__':
    result=run()
    if sys.argv[1:]==['--write']:(ROOT/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        O.need(not sys.argv[1:],'No unknown arguments')
        O.need(result==json.loads((ROOT/'RESULT.json').read_text()),'Saved exact result')
    print(result['status'])
