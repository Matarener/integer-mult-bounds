"""Source/file/hash preparation only; no compiler, imported science or workload."""
from pathlib import Path
from hashlib import sha256
import json
import shutil

HERE=Path(__file__).resolve().parent
ROUND=HERE.parent
ORIGINAL=ROUND/'baseline-public'
COPY=HERE/'baseline-public'
BASE_SHA='78ed2e240ee40ce4989a4718e77e8b3967b092d2bf8c900124a26942c98a14cb'
raw=(ORIGINAL/'native_cache.c').read_bytes()
if sha256(raw).hexdigest()!=BASE_SHA:raise ValueError('original native source pin')
source=raw.decode()
header='#define PY_SSIZE_T_CLEAN\n#include <Python.h>\n#include <stddef.h>\n'
key_end='    PyTuple_SET_ITEM(key,4,parts[2]);PyTuple_SET_ITEM(key,5,parts[3]);PyTuple_SET_ITEM(key,6,Py_NewRef(PyTuple_GET_ITEM(s->tokens,i)));\n'
module='static struct PyModuleDef module={PyModuleDef_HEAD_INIT,"_fraction_native","Bounded cache; exact Python arithmetic.",-1,NULL};'
edits=[dict(label='capture-state-and-separate-methods',before=header,after=header+'\n'+(HERE/'capture.inc').read_text()),
       dict(label='retain-original-key-before-original-lookup',before=key_end,after=key_end+'    if(capture_active && capture_key(key)<0){Py_DECREF(key);return NULL;}\n'),
       dict(label='expose-separate-capture-methods',before=module,after=module.replace(',-1,NULL};',',-1,capture_methods};'))]
changed=source
for edit in edits:
 if changed.count(edit['before'])!=1:raise ValueError('one exact capture seam: '+edit['label'])
 changed=changed.replace(edit['before'],edit['after'])
restored=changed
for edit in reversed(edits):
 if restored.count(edit['after'])!=1:raise ValueError('one inverse capture seam')
 restored=restored.replace(edit['after'],edit['before'])
if restored.encode()!=raw:raise ValueError('capture patch inverses to original bytes')
if COPY.exists():raise ValueError('fresh baseline copy only')
original_inventory={}
for path in sorted(ORIGINAL.rglob('*')):
 if path.is_symlink():raise ValueError('no original symlinks')
 if not path.is_file():continue
 if '__pycache__' in path.parts:continue
 relative=str(path.relative_to(ORIGINAL));target=COPY/relative
 target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 original_inventory[relative]={'sha256':sha256(path.read_bytes()).hexdigest(),'mode':path.stat().st_mode&0o777}
 if target.read_bytes()!=path.read_bytes() or target.stat().st_mode&0o777!=original_inventory[relative]['mode']:raise ValueError('exact initial copy')
if len(original_inventory)!=164:raise ValueError('expected original 164-file census')
new_sha=sha256(changed.encode()).hexdigest()
for name,data in [('native_cache.c',changed.encode()),('NATIVE-SOURCE.json',(json.dumps({'sha256':new_sha},indent=2)+'\n').encode())]:
 path=COPY/name;mode=original_inventory[name]['mode'];path.chmod(mode|0o200);path.write_bytes(data);path.chmod(mode)
receipt={'status':'SOURCE_ONLY_CAPTURE_PREPARED','original_native_sha256':BASE_SHA,'diagnostic_native_sha256':new_sha,'changed_baseline_files':['native_cache.c','NATIVE-SOURCE.json'],'baseline_file_count':164,'original_inventory':original_inventory,'edits':edits,'exact_original_complete_c_source_restored':True,'compilation':False,'numerical_execution':False}
(HERE/'SOURCE-EDITS.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
for name,pin in {'keypilot.c':'ee3fb2af131878fa2065d1b50d02f2f865c0ac61c9ec0a3d66b15c910f3d9cf6','load_pilot.py':'d6912e01fafa7a79a635812e4884d776757f2e24996850b692f0eb8825bf7968','run_pilot.py':'e02ebb21c4985001f57d947414c52366de77e8db5dfe713440a921e5f4cb1c8e'}.items():
 original=ROUND/'cache-key-pilot'/name
 if sha256(original.read_bytes()).hexdigest()!=pin:raise ValueError('approved comparator/helper pin')
 shutil.copy2(original,HERE/name)
print(json.dumps({'copied_baseline_files':164,'diagnostic_native_sha256':new_sha,'original_native_sha256':BASE_SHA,'source_only':True}))
