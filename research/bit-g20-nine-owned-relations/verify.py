"""Regenerate the changed native caller and exact ordinary certificate cold."""
from replay_common import *
def main():
 outputs=['WORD.json.gz','LOCAL-RESULT.json','GLOBAL.jsonl.gz','GLOBAL-RESULT.json','INVOICE.json','CALLS.json','PRIVATE-EPISODES.json','TARGET-OWNERS.json','SOURCE-DESCRIPTORS.json.gz','TARGET-INVOLUTIONS.json','ORDINARY-RESULT.json']
 checked=copy_and_run(['local_relations.py','global_relations.py','target_involutions.py','ordinary.py'],outputs)
 print(json.dumps({'status':'PASS_G20_NINE_OWNED_RELATIONS_COLD_PRIMARY','proof_payloads':len(checked),'admitted':'435496247/125000000000','python_optimize':sys.flags.optimize,'scope':'Conditional ordinary BIT component; no whole multiplication or external acceptance claim.'}))
if __name__=='__main__':main()
