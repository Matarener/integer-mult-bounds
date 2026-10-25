"""Literal inverses including selected-native pointers and all-f metadata.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from joint_algebra import *
from joint_prefix import check_literal_family

def inverse_events(events,m):
 out=[]
 for event in reversed(events):
  e=dict(event);kind=e['kind']
  if kind=='ADD':e['coefficient']=str(-F(e['coefficient']))
  elif kind=='SCALE':e['coefficient']=str(1/F(e['coefficient']))
  elif kind!='BANK_SWAP':
   e['x_monomial']=qc.decode(event,m).inv().data()
   if 'one_coordinate_literal_circuit'in event:
    op=ce.Op(m,tuple(tuple(t)for t in event['one_coordinate_tableau']),event['one_coordinate_literal_circuit']).adjoint()
    e['one_coordinate_literal_circuit']=op.circuit;e['one_coordinate_tableau']=[list(t)for t in op.tab]
    e['phase_exponent']=-event['phase_exponent']
    if event.get('native_family'):
     e['native_family']=dict(event['native_family']);e['native_family']['inverse']=not event['native_family'].get('inverse',False)
     key=event['native_recipe_id'];e['native_recipe_id']=key[:-3]if key.endswith('inv')else key+'inv'
    check_literal_family(e,m)
  out.append(e)
 return out
