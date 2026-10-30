"""Bind the credited four-map dense audit to the actual publication.

Prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import gzip,importlib.util,json,shutil,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import supplier,need
P=HERE/'native-peer'
spec=importlib.util.spec_from_file_location('p104_new_maps_dense',P/'run.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
result,program=M.calculate()
need(result==json.loads((P/'RESULT.json').read_bytes()),'Frozen four-map dense result')
need(program==json.loads((P/'MAPS-PROGRAM.json').read_bytes()),'Frozen literal map circuits')
need(json.loads(gzip.decompress((HERE/'WORD.json.gz').read_bytes()))==M.read('PUBLIC-WORD.json.gz'),'Dense audit covers current complete word')
with supplier()as(root,L,C,R):
    need(L.read(root/'research/p104-full-frame-contact/WORD.json.gz')==M.read('SOURCE-WORD.json.gz'),'Same authenticated predecessor word')
    for name in ('clifford_exact.py','native_verify.py'):
        need((root/'research/p104-native-channel/vendor'/name).read_bytes()==(M.IN/name).read_bytes(),'Same authenticated native source '+name)
# Actual temporary source mutations are rejected by authentication, before imports.
for name in ('clifford_exact.py','pr5548_dense_check.py'):
    with tempfile.TemporaryDirectory(prefix='p104-native-source-control-')as tmp:
        new=Path(tmp)/'inputs';shutil.copytree(M.IN,new)
        path=new/name;path.chmod(0o600)
        path.write_bytes(path.read_bytes()+b'\nraise RuntimeError("must not import changed source")\n')
        original=M.IN;M.IN=new;rejected=False
        try:
            M.authenticate()
        except ValueError as error:
            rejected=str(error).startswith('source authentication before import ')
        finally:
            M.IN=original
        need(rejected,'Mutated native source rejected before import')
print('PASS_PUBLIC_P104_FOUR_ADDED_MAPS_DENSE',sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest())
