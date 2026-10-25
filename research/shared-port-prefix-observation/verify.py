"""Source-bound group-algebra prefix certificate. JoyboyBrian/OpenAI, Apache-2.0."""
import json,hashlib
from pathlib import Path
from collections import defaultdict
p=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
for pin in json.loads((p/'PINS.json').read_text()):
 need(hashlib.sha256((p/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'source authentication '+pin['path'])
d={'__name__':'source'}
exec(compile((p/'source/algebra.py').read_bytes(),'authenticated algebra','exec'),d)
op=d['load_operators']();word,adj=d['word'],d['adjoint'];I=d['ident']();S=d['s_letter'](7);V=d['monomial']([0,2,1,3,4,6,5,7]);P=word(S,d['monomial']([0,5,2,7,4,1,6,3]),S);Q=word(S,V,S)
letters=dict(op,P=P,Pinv=adj(P),Q=Q,Qinv=adj(Q),V=V,Z1=d['pauli'](0,2),N=word(op['A'],op['D'],adj(op['K'])))
def grade(m):
 counts={sum(z!=d['ZERO'] for z in row) for row in m}
 need(len(counts)==1 and next(iter(counts)) in (1,2,4,8),'pure uniform grade')
 return next(iter(counts)).bit_length()-1

def replay(gates):
 mat=[[{I:1}if j==k else{} for k in range(5)]for j in range(5)]
 cuts=[[[dict(c) for c in row] for row in mat]]
 for gate in gates:
  kind,dst=gate[:2]
  if kind=='add':
   src,c=gate[2:]
   for k in range(5):
    ans=defaultdict(int,mat[dst][k])
    for m,a in mat[src][k].items():ans[m]+=c*a
    mat[dst][k]={m:a for m,a in ans.items()if a}
  else:
   need(kind in ('paid','mono'),'native gate kind')
   mat[dst]=[{word(letters[gate[2]],m):a for m,a in cell.items()}for cell in mat[dst]]
  cuts.append([[dict(c) for c in row]for row in mat])
 return cuts

def projected(cell):return {m:a for m,a in cell.items()if grade(m)==3}

def certify(gates):
 cuts=replay(gates)
 need(all(not projected(row[0])for cut in cuts for row in cut),'prefix first-column grade3 vanishes')
 last=cuts[-1];AD=word(op['A'],op['D'])
 need(grade(AD)==3,'diagonal is grade3 unit')
 for j in range(1,5):
  need(projected(last[j][j])=={AD:1},'unit diagonal')
  for k in range(j+1,5):need(not projected(last[j][k]),'triangular minor')
 return cuts

def main():
 source=json.loads((p/'source/WORD.json').read_text());g=source['fused_five_ports'];cuts=certify(g)
 raw=replay(source['five_ports']);tap=projected(raw[12][1][0])
 need(len(tap)==1 and list(tap.values())==[2],'raw cut11 unit pivot coefficient2')
 need(all(not projected(raw[12][1][k])for k in range(1,5)),'raw cut only x0 grade3')
 need(raw[-1]==cuts[-1],'raw/fused endpoint equality with absolute phases')
 # Boundary-expansion fault: replacing the source by its raw lowering must fail.
 try:certify(source['five_ports'])
 except ValueError:pass
 else:raise ValueError('raw internal observation control accepted')
 # A hypothetical extra paid rank3 observer really changes the rank witness.
 extra=[['paid',0,'K']]+g
 try:certify(extra)
 except ValueError:pass
 else:raise ValueError('added rank3 observer control accepted')
 # Actual producer sign fault breaks endpoint binding, not merely rank.
 bad=[list(x)for x in g];j=next(i for i,x in enumerate(bad)if x[0]=='add');bad[j][3]*=-1
 need(replay(bad)[-1]!=raw[-1],'actual ADD sign fault detection')
 result=dict(fused_gates=len(g),retained_cuts=len(cuts),rows_observable=5*len(cuts),grade3_image_dimension='4 dim(B_f)',raw_first_pivot_cut=11,raw_stack_dimension='5 dim(B_f)',paid_profile={'1':2,'3':4},scope='fixed producer; recording-only native gate boundaries; sufficiently-large-width obstruction to all-width completion')
 need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((p/'RESULT.json').read_text()),sort_keys=True),'receipt equality')
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
