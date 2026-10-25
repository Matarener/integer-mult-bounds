"""No runtime imports: derive exact compositional invoice from frozen receipt."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(x,m):
 if not x:raise ValueError(m)
def run(data):
 for row in data['cases']:
  a,b,c,d=row['variants'];h=a['h'];n=h+1;I=a['I'];L=a['L'];Q=a['Q']
  r=2*I+L+5;k=Q+2*I+90;F=Q+2+4096*(L+1)
  program_reads=3*r*n+(3*k-1)*h*n//2
  program_moves=n*(2*r+2+k*h)
  fields_reads=(3*F-1)*n*(n+1)//2-3*n*F+3*n*Q+6*n
  fields_moves=F*n*(n-1)+n*(2*Q+6)
  expected={'reads':2*(program_reads+fields_reads),'writes':0,'moves':2*(program_moves+fields_moves)}
  need(row['saved']['record']==expected,'twice complete Callback admission record saving')
  need(row['saved']['residue']=={k:8190*v for k,v in zip(('reads','writes','moves'),(523,95,556))},'two radix families source-word saving')
  need(a['created_record_tapes']==d['created_record_tapes'],'no additional tapes')
  need(a['additional_residue_peak']==d['additional_residue_peak'],'no additional residue peak')
  need(a['additional_index_peak']==d['additional_index_peak'],'no additional index peak')
  for x in row['variants']:
   need(x['protected_state_restored'] is True,'successful cleanup')
   need(x['Q']==6512 and x['source_request']==896352 and x['source_rank']==14,'actual pooled identity')
 return True
if __name__=='__main__':
 data=json.loads((HERE/'RESULT.json').read_text());run(data)
 print('PASS_INDEPENDENT_PREPARATION_INVOICE')
