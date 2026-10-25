#!/usr/bin/env python3
"""Verify every native event's selected recipe pointer and actual operator.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse,hashlib,json
from joint_algebra import *
from joint_prefix import check_literal_family
from literal_events import inverse_events
HERE=Path(__file__).resolve().parent

def compile_literal(circuit,n):
 out=ce.ident(n)
 for gate in circuit:
  if gate[0]=='P':op=ce.perm(n,tuple(gate[1]))
  elif gate[0]=='D':op=ce.diag(n,tuple(gate[1]),tuple(gate[2]))
  elif gate[0]=='C':op=ce.cgate(n,gate[1],gate[2])
  elif gate[0]=='X':op=ce.xgate(n,gate[1])
  elif gate[0]=='phase':op=ce.Op(n,ce.identity(n),[tuple(gate)])
  else:raise ValueError('uncovered selected literal '+str(gate[0]))
  out=out.then(op)
 return out

def compile_monomial(rec,n):
 return compile_literal([('D',rec['quadratic_rows'],rec['linear_Z4']),('P',rec['matrix_rows']),('X',rec['offset']),('phase',rec['phase'])],n)
def compile_recipe(rec,n):
 left=compile_monomial(rec['left'],n)
 if not rec['rank']:return left
 need(rec['right']is not None,'nonzero native rank has both literal monomial adapters')
 return compile_monomial(rec['right'],n).then(ce.fourier(n,range(rec['rank']))).then(left)

def embedding_circuit(circuit,embedding,n):
 d=len(embedding);need(len(set(embedding))==d and all(0<=j<n for j in embedding),'recipe embedding injective')
 def bits(x):return sum(((x>>i)&1)<<embedding[i]for i in range(d))
 out=[]
 for gate in circuit:
  typ=gate[0]
  if typ=='P':
   rows=[1<<i for i in range(n)]
   for i,j in enumerate(embedding):rows[j]=bits(gate[1][i])
   out.append(('P',tuple(rows)))
  elif typ=='D':
   rows=[0]*n;alpha=[0]*n
   for i,j in enumerate(embedding):rows[j]=bits(gate[1][i]);alpha[j]=gate[2][i]
   out.append(('D',tuple(rows),tuple(alpha)))
  elif typ in('C','X'):out.append((typ,bits(gate[1]),*gate[2:]))
  elif typ=='phase':out.append(tuple(gate))
  else:raise ValueError('uncovered embedded recipe '+typ)
 return out

def check_artifact(path):
 data=json.loads(path.read_text());counts=[]
 for fixture in data['fixtures']:
  m=fixture['ambient_arity'];pool=fixture['native_recipe_pool'];compiled={}
  for key,p in pool.items():
   need('selected_native_recipe'in p,'selected-native lowering present in recipe pool '+key)
   n=len(p['one_coordinate_tableau'])//2
   actual=ce.Op(n,tuple(tuple(t)for t in p['one_coordinate_tableau']),p['one_coordinate_definition_circuit'])
   compiled[key]=compile_recipe(p['selected_native_recipe'],n)
   same(compiled[key],actual,'recipe pool exact selected child and monomial adapters '+key)
  events=fixture.get('full_events',fixture.get('events',[]));inverse=inverse_events(events,m);used=0
  need(mm(qc.replay(events,fixture['banks'],m),qc.replay(inverse,fixture['banks'],m))==eye(fixture['banks'],m),'derived full literal inverse covers every original field')
  for direction,E in(('forward',events),('inverse',inverse)):
   for e in E:
    if e['kind']!='NATIVE':continue
    check_literal_family(e,m)
    key=e['native_recipe_id'];need(key in pool,direction+' native recipe id missing: '+key)
    p=pool[key];need(e['phase_exponent']==p['phase_exponent'],direction+' native all-f phase exponent matches pool '+key)
    actual=ce.Op(m,tuple(tuple(t)for t in e['one_coordinate_tableau']),e['one_coordinate_literal_circuit'])
    literal=embedding_circuit(compiled[key].circuit,e['recipe_embedding'],m)
    full=compile_literal(literal,m)
    same(full,actual,direction+' actual event equals embedded selected recipe '+key)
    need(ce.rank(x for x,y,p in full.tab[m:])==e['rank_per_f'],direction+' complete selected child rank '+key)
    used+=1
  counts.append({'q':fixture['q'],'name':fixture.get('name'),'native_forward_and_inverse_links':used,'pool_entries':len(pool)})
 return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fixtures':counts}

def produce():
 good=check_artifact(HERE/'JOINT-COMPLETE.json')
 try:check_artifact(HERE/'before-recipe-id-fix-v1'/'JOINT-COMPLETE.json')
 except ValueError as e:
  need('native recipe id missing'in str(e),'before-fix mutant fails specifically for missing inverse pointer')
  rejected=str(e)
 else:raise ValueError('before-fix metadata mutant unexpectedly passes')
 return {'status':'PASS_ALL_FORWARD_INVERSE_RECIPE_LINKS_AND_SELECTED_OPERATORS','checked':[good],
         'negative_control':{'before_fix_rejected':rejected},
         'producer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'source_pins':[{'path':str(HERE/'joint_algebra.py'),'sha256':hashlib.sha256((HERE/'joint_algebra.py').read_bytes()).hexdigest()}],
         'scope':'Derived complete literal inverse, including every prefix event, is replayed. Every selected-native pool recipe is independently recompiled; every forward/inverse native pointer, embedding, actual Gaussian phase, tensor-family phase exponent and rank matches. Original before-fix receipt remains preserved and is rejected.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=produce();path=HERE/'RECIPE-LINK-VALIDATION.json'
 if a.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(path.read_text())==out,'saved recipe link validation differs')
 print(out['status'])
if __name__=='__main__':main()
