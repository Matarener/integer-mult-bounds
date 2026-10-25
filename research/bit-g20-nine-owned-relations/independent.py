"""Run four separate literal/QQ/series auditors in a fresh package copy."""
from replay_common import *
def main():
 scripts=['independent/local_audit.py','independent/global_audit.py','independent/target_audit.py','independent/ordinary_audit.py']
 outputs=['independent/LOCAL-REVIEW.json','independent/GLOBAL-REVIEW.json','independent/TARGET-REVIEW.json','independent/ORDINARY-REVIEW.json']
 checked=copy_and_run(scripts,outputs)
 print(json.dumps({'status':'PASS_G20_NINE_OWNED_RELATIONS_COLD_SEPARATE_AUDIT','proof_payloads':len(checked),'admitted':'435496247/125000000000','python_optimize':sys.flags.optimize,'scope':'Separate internal AI audits, not external or complete theorem verification.'}))
if __name__=='__main__':main()
