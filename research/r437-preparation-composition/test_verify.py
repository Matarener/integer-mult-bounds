"""Composition-specific positive and losing semantic controls; -O safe."""
import copy,json,tempfile,shutil
from pathlib import Path
import verify,independent

def reject(label,action):
 try:action()
 except (ValueError,KeyError):return label
 raise ValueError('accepted losing control '+label)

def run():
 data=json.loads((verify.HERE/'RESULT.json').read_text());independent.run(data);controls=[]
 with tempfile.TemporaryDirectory() as td:
  source=verify.sources(Path(td))
  baseline=data['cases'][0]['variants'][0]
  for mutation in ('skip_context_share','skip_validation'):
   losing=verify.run_case(source,0,1,True,True,mutation=mutation)
   verify.need(losing['output_sha256']==baseline['output_sha256'],'losing composition keeps returned child bytes')
   row=copy.deepcopy(data['cases'][0]);row['variants'][-1]=losing
   row['saved']={lane:verify.minus(baseline['total'][lane],losing['total'][lane]) for lane in baseline['total']}
   controls.append(reject(mutation,lambda:independent.run({'cases':[row]})))
  import records,controller,forward_fields
  changed=Path(td)/'controller.py';changed.write_text(Path(controller.__file__).read_text().replace('self.fields.end(after)','self.fields.end(self.depth)'))
  controls.append(reject('changed_admission_AST',lambda:forward_fields.install(controller.Callback,records,changed,vars(controller))))
 for label,change in [
  ('omit_disposal_invoice',lambda r:r['cases'][0]['saved']['record'].__setitem__('writes',1)),
  ('wrong_pooled_width',lambda r:r['cases'][0]['variants'][0].__setitem__('Q',6507)),
  ('old_rank26_relabel',lambda r:r['cases'][0]['variants'][0].__setitem__('source_rank',26)),
  ('false_restoration',lambda r:r['cases'][0]['variants'][0].__setitem__('protected_state_restored',False)),
 ]:
  r=copy.deepcopy(data);change(r);controls.append(reject(label,lambda:independent.run(r)))
 with tempfile.TemporaryDirectory() as td:
  vendor=Path(td)/'vendor';shutil.copytree(verify.HERE/'vendor',vendor)
  vendor.chmod(0o755)
  for path in vendor.rglob('*'):path.chmod(0o755 if path.is_dir() else 0o644)
  rows=verify.authenticate_vendor(vendor);first=vendor/rows[0]['path'];raw=first.read_bytes()
  first.write_bytes(raw+b'\0');controls.append(reject('vendor_corruption',lambda:verify.authenticate_vendor(vendor)));first.write_bytes(raw)
  first.unlink();controls.append(reject('vendor_missing',lambda:verify.authenticate_vendor(vendor)));first.write_bytes(raw)
  extra=vendor/'unexpected';extra.write_text('extra');controls.append(reject('vendor_extra',lambda:verify.authenticate_vendor(vendor)));extra.unlink()
  extra.symlink_to(first);controls.append(reject('vendor_link',lambda:verify.authenticate_vendor(vendor)));extra.unlink()
  verify.authenticate_vendor(vendor)
 verify.need(len(controls)==11,'all eleven composition and packaging controls')
 print('PASS_PREPARATION_COMPOSITION_CONTROLS',','.join(controls))
if __name__=='__main__':run()
