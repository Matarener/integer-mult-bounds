"""Semantic receipt mutants; run after authentication, independently of byte pins."""
import copy,json
from pathlib import Path
from evidence_check import semantic,read,P

def main():
 d=P/'evidence/complete';original=[read(d/f) for f in ['RESULT.json','RELEASE-RECEIPT.json','NATIVE-RECEIPT.json','PREFIX-AND-INVOICE.json','INDEPENDENT.json']];semantic(*original)
 cases=[('wrong_profile',lambda x:x[0]['profile'].__setitem__('3',x[0]['profile']['3']-1)),('missing_private_stock',lambda x:x[3].__setitem__('private_zero_buffers',90)),('unpaid_native_word',lambda x:x[2]['providers']['base'].__setitem__('word_sha256','0'*64)),('unchecked_tape',lambda x:x[3]['strict_checks'].__setitem__('tape',False)),('false_dirty_cleanup',lambda x:x[3]['blocknorm']['endpoint_replay']['extra']['backward'].__setitem__('zero_buffers_allocated_and_cleared',90)),('skipped_roles',lambda x:x[4].__setitem__('checked_busy_family_windows',1321919)),('unexecuted_release',lambda x:x[0]['stages'][-1].__setitem__('exit_code',1)),('no_retained_parent_disclosure',lambda x:x[2].__setitem__('reused_retained_parent',False)),('undercharged_precision',lambda x:x[3].__setitem__('charged_prefix_bits',1024))]
 rejected=[]
 for name,mutate in cases:
  trial=copy.deepcopy(original);mutate(trial)
  try:semantic(*trial)
  except (ValueError,KeyError):rejected.append(name)
  else:raise ValueError('semantic receipt mutant accepted '+name)
 print(json.dumps(dict(status='PASS_SEMANTIC_COMPLETE_RECEIPT_CONTROLS',rejected=rejected),indent=2))
if __name__=='__main__':main()
