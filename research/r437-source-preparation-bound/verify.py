"""Bounded exact producer tariff, monotone-adapter equivalence and controls."""
import json
from pathlib import Path
import check
HERE=Path(__file__).resolve().parent

def run():
 pairs=[]
 for h,kind,half,Q,L in [(0,'unit',False,4,5),(1,'good',False,4,5),(2,'pair',False,5,6),(3,'unit',True,4,5),(4,'good',False,8,5),(6,'unit',False,8,7)]:
  a=check.case(h,kind,half,Q,L,False);b=check.case(h,kind,half,Q,L,True)
  check.need(a['output_sha256']==b['output_sha256'],'byte-identical actual child program')
  for label in ('output','residue','record_visited_cells','chronological_trace'):
   check.need(a[label]==b[label],'unchanged non-field component '+label)
  check.need(b['numerical_actions']<a['numerical_actions'],'removed numerical seek work')
  check.need(sum(b['fields'].values())<sum(a['fields'].values()),'strict completed field action saving')
  pairs.append(dict(original=a,adapted=b))
 def wrong_code(w,r,p,f):f.tape.cells[1]=w.ONE
 def extra_field(w,r,p,f):f.tape.cells.extend(f.tape.cells[1:])
 def missing_end(w,r,p,f):f.tape.cells.pop()
 def bad_root(w,r,p,f):p.tape.cells[1]=r.STEP
 def current_code(w,r,p,f):
  F=f.code_bits+2+4096*(f.residue_arena.bits+1);f.tape.cells[1+2*F]=w.ONE
 def extra_step(w,r,p,f):
  rr=2*p.index_arena.bits+p.residue_arena.bits+5;p.tape.cells.extend(p.tape.cells[1+rr:])
 def nonunit_root(w,r,p,f):
  k=p.index_arena.bits+3;p.tape.cells[k]=w.ZERO;p.tape.cells[k+1]=w.ONE
 leaf=[]
 for h in (0,2,4):
  a=check.leaf_case(h,False);b=check.leaf_case(h,True)
  check.need(a['state']==b['state'] and a['trace']==b['trace'],'leaf semantic admission equivalence')
  leaf.append(dict(original=a,adapted=b))
 controls={}
 for name,mutation in [('wrong_field_code',wrong_code),('extra_field',extra_field),('truncated_field',missing_end),('wrong_root_tag',bad_root),('wrong_current_code',current_code),('extra_program_step',extra_step),('nonunit_root',nonunit_root)]:
  a=check.case(2,mutation=mutation);b=check.case(2,adapted=True,mutation=mutation)
  check.need(a['rejected']==b['rejected'] and a['unchanged'] and b['unchanged'],'same fixture rejection and cleanup')
  controls[name]=a['rejected']
 import tempfile,forward_fields
 w,records,controller,_=check.setup()
 with tempfile.TemporaryDirectory() as td:
  path=Path(td)/'controller.py';source=(check.V/'controller.py').read_text();path.write_text(source.replace('self.fields.end(after)','self.fields.end(self.depth)'))
  try:forward_fields.install(controller.Callback,records,path,vars(controller))
  except ValueError as e:check.need(str(e)=='exact reviewed admission AST','exact AST guard failure')
  else:raise ValueError('unreviewed admission AST accepted')
 controls['changed_admission_AST']='exact reviewed admission AST'
 projection=[check.projected_case(a) for a in (False,True)]
 check.need(projection[0]['output_sha256']==projection[1]['output_sha256'] and projection[0]['chronological_trace']==projection[1]['chronological_trace'],'projected definition admission equivalence')
 return dict(projected_definition_cases=projection,status='PASS_ACTUAL_CHILD_PROGRAM_FORWARD_ADMISSION',cases=pairs,leaf_cases=leaf,negative_controls=controls,
             physical_payload_executed=False,full_Pi_closed=False)

def main():
 result=run();check.need(result==json.loads((HERE/'RESULT.json').read_text()),'committed exact receipt')
 print(result['status'],len(result['cases']),'original/adapted pairs;',len(result['negative_controls']),'admission controls')
if __name__=='__main__':main()
