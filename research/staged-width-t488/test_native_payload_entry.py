# SPDX-License-Identifier: Apache-2.0
"""Execute the production payload-authentication loop on portable synthetic fixtures."""
import sys
if sys.flags.optimize: raise SystemExit("optimized Python is unsupported for verification")
from pathlib import Path
import ast,json,hashlib,gzip,tempfile,shutil
P=Path(__file__).parent;script=P/'owners/independent_literal.py';tree=ast.parse(script.read_text());nodes=[n for n in tree.body if isinstance(n,ast.For)and 'actual native canonical payload pin'in ast.unparse(n)];assert len(nodes)==1
pins={'native_canonical':{}}
def need(v,m):
 if not v:raise ValueError(m)
def run(root):exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(script),'exec'),dict(NATIVE=root,source_pins=pins,gzip=gzip,hashlib=hashlib,need=need))
checks=[]
with tempfile.TemporaryDirectory(prefix='payload-entry-')as td:
 d=Path(td)
 for tag in ['base','extra']:
  q=d/f'checked-{tag}/CANONICAL-WORD.json.gz';q.parent.mkdir();payload=json.dumps({'synthetic_provider':tag},sort_keys=True).encode();q.write_bytes(gzip.compress(payload,mtime=0));pins['native_canonical'][tag]={'canonical_payload_sha256':hashlib.sha256(payload).hexdigest()}
 run(d);checks.append('original containers PASS')
 for tag in ['base','extra']:
  q=d/f'checked-{tag}/CANONICAL-WORD.json.gz';b=bytearray(q.read_bytes());b[9]=3 if b[9]!=3 else 255;q.write_bytes(b)
 run(d);checks.append('OS-header-only changes PASS')
 for tag in ['base','extra']:
  q=d/f'checked-{tag}/CANONICAL-WORD.json.gz';q.write_bytes(gzip.compress(gzip.decompress(q.read_bytes()),compresslevel=1,mtime=123))
 run(d);checks.append('compression/time changes PASS')
 for tag in ['base','extra']:
  q=d/f'checked-{tag}/CANONICAL-WORD.json.gz';old=q.read_bytes();q.write_bytes(gzip.compress(gzip.decompress(old)+b' ',mtime=0))
  try:run(d)
  except ValueError as e:assert str(e)=='actual native canonical payload pin';checks.append(tag+' payload change REJECT')
  else:raise AssertionError('payload corruption accepted')
  q.write_bytes(old)
r={'status':'PASS_ACTUAL_PRODUCTION_NATIVE_PAYLOAD_ENTRY','checks':checks,'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'scope':'Executes actual production authentication for-loop, isolated only from owner allocation setup; Synthetic payloads exercise the exact production loop; not a fresh native replay.'};print(json.dumps(r,sort_keys=True))
