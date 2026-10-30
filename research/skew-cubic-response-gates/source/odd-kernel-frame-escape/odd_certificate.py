#!/usr/bin/env python3
"""Stock trajectory certificates for actual odd-rank skew q2/q3 words.
Apache-2.0. Substantial OpenAI Codex assistance. No new supplier/kappa.
"""
from pathlib import Path
import argparse,copy,hashlib,json,math,random,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent
PINS={
 'general-clifford-retiming/kernel-search/EXACT-FIXTURES.json':'2a26ade57e30afd5cab9cfb328248ab4f24d3a5589caf585a3f858b86c4b40b0',
 'general-clifford-retiming/kernel-search/kernel_exact.py':'1363650633c055efd7532e77142a31583318cd55ec0f0a34f5f268d42c4edbb9',
 'trajectory-pairing-search/pairing_search.py':'4c1dc5986808c62a2caace8059f5c8a2a6a706b4ad46ed042542b5f63e27c023',
 'trajectory-pairing-search/admit_pairings.py':'f0ce5196bf3c75ed1ed22a8424e971293f56cf6939be34ccd3f082430440f91c',
 'pauli-caller-retiming/trajectory_certificate.py':'677a342334e49befbfe069441325f3ac6008705c6697cff5c348905a67d92cbc',
}
for p,h in PINS.items():
 if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h:raise ValueError('frozen source pin '+p)
sys.path.insert(0,str(R/'trajectory-pairing-search'))
import pairing_search as s
from admit_pairings import direct_crossed
t=s.t
from joint_algebra import qc,mono,prefix
from native_model import b


def discover(f):
 m,n,E,ordinals=s.prepare(f);goal=f['optimistic_stock'];rng=random.Random(1019)
 best,br=s.evaluate(0,m,n,E);straight=best;mask=0;score=best;bm=0;history=[]
 for j in range(5000):
  if j%336==0:
   mask=bm if rng.random()<.5 else rng.getrandbits(len(ordinals));score,_=s.evaluate(mask,m,n,E)
  candidate=mask^(1<<rng.randrange(len(ordinals)));value,ranks=s.evaluate(candidate,m,n,E)
  temperature=max(.2,2.5*(1-j%336/336))
  if value>=score or rng.random()<math.exp((value-score)/temperature):mask,score=candidate,value
  if value>best:best,br,bm=value,ranks,candidate;history.append(dict(trial=j+1,floor=best,ranks=ranks,mask=str(bm)))
  if best>=goal:break
 t.need(best==goal,'stock witness found before bounded5000 trials')
 return bm,ordinals,j+1,straight,history


def primitive_inverse_checks(paths,m):
 unique={t.stable(g):g for path in paths for g in path['one_coordinate_literal_circuit']}
 for gate in unique.values():
  op=t.compile_literal(m,t.stable([gate]))
  for pair in(op.then(op.adjoint()),op.adjoint().then(op)):
   t.need(pair.tab==t.ce.identity(m),'primitive inverse signed tableau')
   col,den=b.sparse_column(pair)
   t.need(col=={0:(1,0)}and den==0,'primitive inverse exact Gaussian zero column')
 # A scalar i survives despite an identity signed tableau: phase matters.
 bad=t.ce.Op(m,t.ce.identity(m),[('phase',1)])
 col,den=b.sparse_column(bad)
 t.need(bad.tab==t.ce.identity(m)and(col!={0:(1,0)}or den!=0),'global-i inverse mutant rejected beyond tableau')
 return len(unique)


def produce():
 raw=json.loads((R/'general-clifford-retiming/kernel-search/EXACT-FIXTURES.json').read_text());rows=[]
 for source in raw['fixtures']:
  if source['kernel']!='odd_rankone_involution':continue
  f=source['isolated'];q=f['q'];m,n=f['ambient_arity'],f['banks'];E=f['events']
  mask,ordinals,trials,straight,history=discover(f)
  crossings=[ordinal for bit,ordinal in enumerate(ordinals)if mask>>bit&1]
  edges,paths,owner,nodes=t.graph_paths(E,n,m,crossing_adds=crossings);H=t.check_partition(edges,paths,n,m)
  direct=direct_crossed(E,n,m,set(crossings));saved=[]
  for i,((op,ep,r),expected)in enumerate(zip(H,direct)):
   t.need(op.tab==expected['op'].tab and t.stable(op.circuit)==t.stable(expected['op'].circuit),'independent odd-kernel crossed literal product')
   t.need(ep==expected['extra']and owner[expected['final_bank']]==i,'actual all-f phase and endpoint bank')
   for pair in(op.then(op.adjoint()),op.adjoint().then(op)):t.need(pair.tab==t.ce.identity(m),'holonomy signed inverse bothorders')
   saved.append(dict(initial_bank=i,final_bank=expected['final_bank'],edges=paths[i],
                     source_unary_event_ordinals=expected['source_ordinals'],native_arity_per_f=r,
                     one_coordinate_tableau=op.tab,one_coordinate_literal_circuit=op.circuit,
                     extra_global_phase_exponent_by_f_mod4=ep,literal_inverse_circuit=op.adjoint().circuit,
                     inverse_extra_global_phase_exponent_by_f_mod4=[-x%4 for x in ep]))
  data=source['J_four_axes'];d=len(data['rows'])
  J=qc.Mono(tuple(data['rows'])+tuple(1<<i for i in range(d,m)),data['offset'],tuple(data['alpha'])+(0,)*(m-d),
            tuple(data['quad'])+(0,)*(m-d),data['constant'],data['global_phase'])
  minus=qc.Mono(qc.identity(m).rows,0,(0,)*m,(0,)*m,0,2)
  t.need(mono(J@J)==mono(minus),'whole-field skew phase, every tensor multiplicity')
  parent=qc.rank((prefix(m,2*q+1)@J).polar())
  t.need(qc.rank(J.polar())==1 and parent==m-1==f['parent_arity'],'actual ODD rank1 kernel and11/15 parent')
  mass=sum(e['rank_per_f']for e in E if e['kind']=='NATIVE');floor=sum(h[2]for h in H)
  t.need(floor==mass==f['mass']==f['optimistic_stock']==n*parent,'sharp stock retiming bound for odd kernel')
  bad=copy.deepcopy(paths);bad[0]=bad[0][1:]
  try:t.check_partition(edges,bad,n,m)
  except ValueError as err:missing=str(err)
  else:raise ValueError('omitted edge accepted')
  wrong_swap=None
  for at,e in enumerate(E):
   if e['kind']!='BANK_SWAP':continue
   bad=direct_crossed(E,n,m,set(crossings),omit_swap=at)
   if any(x['op'].tab!=y['op'].tab or t.stable(x['op'].circuit)!=t.stable(y['op'].circuit)or x['final_bank']!=y['final_bank']for x,y in zip(direct,bad)):
    wrong_swap=at;break
  t.need(wrong_swap is not None and straight<floor,'wrongSWAP and allstraight controls are sensitive')
  primitive_count=primitive_inverse_checks(saved,m)
  rows.append(dict(q=q,banks=n,ambient_arity=m,parent_arity_per_f=parent,kernel_native_arity_per_f=1,J=J.data(),
                   source_events_sha256=hashlib.sha256(t.stable(E).encode()).hexdigest(),
                   source_native_mass=mass,stock=n*parent,admitted_floor_per_f=floor,
                   path_ranks_per_f=[h[2]for h in H],mask_decimal=str(mask),
                   chronological_pairing_bitstring=''.join('1'if mask>>bit&1 else'0'for bit in range(len(ordinals))),
                   ADD_event_ordinals=ordinals,crossing_ADD_event_ordinals=crossings,
                   search_trials=trials,search_limit=5000,proposal_history=history,
                   graph_nodes=nodes,edges=edges,trajectories=saved,complete_edge_partition=True,
                   primitive_exact_Gaussian_inverse_checks=primitive_count,
                   negative_controls=dict(straight_floor_below_stock=straight,omitted_edge_rejected=missing,wrong_actual_SWAP_rejected=wrong_swap,global_i_inverse_phase_rejected=True)))
 return dict(status='PASS_ODD_RANK_KERNEL_SHARP_FIXED_GRAPH_STOCK_CERTIFICATES',no_new_kappa=True,
             producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_pins=[dict(path=str(R/p),sha256=h)for p,h in PINS.items()],
             fixtures=rows,scope='Finite q2/q3 actual odd-rank kernel words, all positive f; arbitrary general Clifford frame gauges at the fixed ADD/common-frame topology with literal physical boundaries.',
             limits=['No frame anneal ran after stock witnesses were found.',
                     'No new all-q caller, selected-native lowering or inverse-recipe-schema admission is claimed for the kernel-search input.',
                     'Parent native arity11/15 differs from ambient12/16; spectator-volume/owner/controller/precision/borrowed-axis embedding and joint supplier gates remain separate.',
                     'Stock/rank conclusions use the same-volume full-bank query model; no heterogeneous-volume moment or kappa theorem.',
                     'Changed scalar/native chronology, unary holonomies, helper coupling or physical endpoint contracts are outside this fixed-word certificate.'])


def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(produce()));path=HERE/'ODD-FRAME-CERTIFICATES.json'
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:t.need(json.loads(path.read_text())==out,'saved odd frame certificates')
 print(out['status'])
 for f in out['fixtures']:print('q',f['q'],'floor',f['admitted_floor_per_f'],'stock',f['stock'],'paths',f['path_ranks_per_f'],'trials',f['search_trials'])


if __name__=='__main__':main()
