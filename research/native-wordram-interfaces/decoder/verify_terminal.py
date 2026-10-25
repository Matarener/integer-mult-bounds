"""Source-bound three-query closed workspace replay; Python 3.12+, standard library."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parent
if not __debug__: raise RuntimeError('Run this certificate without Python -O')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out);return out
m=module('closed_physics',ROOT/'source/research/closed-helper-feedback/derived_replay.py')
w=module('three_query_workspace',ROOT/'source/research/closed-helper-feedback/three_query_terminal.py')
raw=gzip.decompress(m.SOURCE.read_bytes())
m.need(hashlib.sha256(raw).hexdigest()==m.PIN,'Native decompressed payload hash')
source=json.loads(raw);bank=json.loads((m.ROOT/'research/native-helper-query-bank/BANK.json').read_text())
result=w.check(m,source,bank)
selected={**bank,'queries':[bank['queries'][j]for j in (0,16,32)],'cold_completions':[]}
result['first_departures_checked']=m.original_departures(source,selected)
result['physical_checks']=m.check_physics(source,selected)
q=m.ce.cgate(9,1);q2=q.then(q)
m.need(m.equal(q2,m.ce.xgate(9,1)),'Exact central Pauli square')
K0=m.literal(bank['queries'][0]['input_K']['word'])
K2=m.literal(bank['queries'][32]['input_K']['word'])
O2=m.literal(bank['queries'][32]['response']['word'])
for op in [K0.adjoint().then(q2).then(K2),q2,O2.adjoint()]:
    compiled,_=m.ce.monomial(op)
    m.need(m.equal(compiled,op),'Literal ordinary decoder map including absolute phase')
r=m.ce.fourier(9)
B=K0.adjoint().then(q2).then(K2)
m.need(m.equal(B.then(r),r.then(B)), 'Physical terminal decoder commutes with full return')
result['decoder_monomial_maps_checked']=3
result['decoder_commutes_full_return']=True
controls=[]
for mutation in ['omit_terminal_decode','chart_swap']:
    try:w.check(m,source,bank,mutation=mutation)
    except ValueError as exc:controls.append({'mutation':mutation,'result':'REJECT','reason':str(exc)})
    else:raise ValueError('Mutation accepted: '+mutation)
result['rejected_controls']=controls
# Tuples are serialized as arrays in a portable frozen receipt.
result=json.loads(json.dumps(result))
receipt=ROOT/'three-query-terminal-result.json'
if '--emit' in sys.argv:receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
else:m.need(result==json.loads(receipt.read_text(encoding='utf-8')),'Saved typed receipt differs')
print(json.dumps(result,indent=2))
