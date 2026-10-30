"""Source-bound, read-only fixed-rank-one controller replay."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import io,json,tarfile,types
HERE=Path(__file__).resolve().parent
ARCHIVE=HERE.parents[1]/'research/filtered-native-kappa004/inputs/original-packet.tar.gz'
ARCHIVE_SHA='595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7'
MEMBERS={
 'word':('research/retained_state_next/F9-SOURCE-DAG-ALL8-WORD.json.gz','934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775'),
 'R':('upstream/research/involutory-producer-raw-dual/inputs/R/R.json','7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1')}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(name):
 path=HERE/(name+'.py');m=types.ModuleType(name);m.__file__=str(path)
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
 return m
def main():
 raw=ARCHIVE.read_bytes();need(sha256(raw).hexdigest()==ARCHIVE_SHA,'Exact source archive')
 with TemporaryDirectory(prefix='active-rank1-') as temp:
  paths={}
  with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
   inventory=archive.getmembers()
   for key,(name,digest) in MEMBERS.items():
    matches=[m for m in inventory if m.name=='filtered_native_implementation/'+name]
    need(len(matches)==1 and matches[0].isfile(),'Unique regular data member')
    data=archive.extractfile(matches[0]).read();need(sha256(data).hexdigest()==digest,'Pinned data member')
    paths[key]=Path(temp)/(key+'.input');paths[key].write_bytes(data)
  for module,receipt in [('rank1_controller','rank1-controller.json'),('y_cleanup','y-cleanup.json')]:
   actual=load(module).run(paths['word'],paths['R'])
   expected=json.loads((HERE/receipt).read_bytes())
   need(actual==expected,'Complete exact certificate comparison: '+receipt)
 print('PASS_FIXED_RANK1_CONTROLLER_AND_CLEANUP_GEOMETRY; no new bound claimed')
if __name__=='__main__':main()
