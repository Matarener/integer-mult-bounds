"""Reproducible text/hash/file preparation only; imports no scientific module."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'baseline-public'
COPY = HERE / 'baseline-public'
BASE_NATIVE_SHA = '78ed2e240ee40ce4989a4718e77e8b3967b092d2bf8c900124a26942c98a14cb'
raw = (ORIGINAL / 'native_cache.c').read_bytes()
if sha256(raw).hexdigest() != BASE_NATIVE_SHA:
    raise ValueError('exact original PR5864 native source')
source = raw.decode()
start = 'static PyObject *contribution(Event *e, PyObject *old, PyObject *v, Py_ssize_t i) {\n'
end = 'static int begin_event(Event *e) {\n'
if source.count(start) != 1 or source.count(end) != 1:
    raise ValueError('unique original contribution region')
begin, finish = source.index(start), source.index(end)
original_function = source[begin:finish]
replacement = (HERE / 'contribution_diagnostic.c').read_text()
# Remove only the declared diagnostic statements and require exact original
# bytes. This verifies original statement/control/numeric order was preserved.
neutral = replacement
for statement in (
        '    JointTimer timer=joint_start(JOINT_LOOKUP);\n',
        '    joint_stop(&timer,JOINT_MISS);\n',
        '    joint_inc(&joint_callback_depth);\n',
        '    if (!joint_callback_depth) joint_inc(&joint_protocol_errors);else joint_callback_depth--;\n',
        '    timer=joint_start(JOINT_AFTER);\n',
        '    joint_stop(&timer,JOINT_INSERTED);\n'):
    if neutral.count(statement) != 1:
        raise ValueError('unique diagnostic contribution statement: ' + statement)
    neutral = neutral.replace(statement, '')
for statement in ('joint_stop(&timer,JOINT_ERROR);', 'joint_stop(&timer,JOINT_HIT);'):
    if not neutral.count(statement):
        raise ValueError('required diagnostic exit statements')
    neutral = neutral.replace(statement, '')
if neutral != original_function:
    raise ValueError('instrumented contribution neutralizes to exact original bytes')
header = '#define PY_SSIZE_T_CLEAN\n#include <Python.h>\n#include <stddef.h>\n'
new_header = ('#ifndef _POSIX_C_SOURCE\n#define _POSIX_C_SOURCE 200809L\n#endif\n'
              + header + '#include <errno.h>\n#include <limits.h>\n#include <time.h>\n\n'
              + (HERE / 'joint_diag.inc').read_text())
module_line = 'static struct PyModuleDef module={PyModuleDef_HEAD_INIT,"_fraction_native","Bounded cache; exact Python arithmetic.",-1,NULL};'
new_module = module_line.replace(',-1,NULL};', ',-1,joint_module_methods};')
edits = [dict(label='diagnostic-clocks-markers-and-separate-module-methods', before=header, after=new_header),
         dict(label='timed-original-contribution-with-callback-gap', before=original_function, after=replacement),
         dict(label='expose-only-separate-diagnostic-module-methods', before=module_line, after=new_module)]
changed = source
for edit in edits:
    if changed.count(edit['before']) != 1:
        raise ValueError('one exact diagnostic seam: ' + edit['label'])
    changed = changed.replace(edit['before'], edit['after'])
restored = changed
for edit in reversed(edits):
    if restored.count(edit['after']) != 1:
        raise ValueError('one reversible diagnostic seam: ' + edit['label'])
    restored = restored.replace(edit['after'], edit['before'])
if restored.encode() != raw:
    raise ValueError('all diagnostic edits reverse to exact original C source')
original_inventory = {}
for path in sorted(ORIGINAL.rglob('*')):
    if path.is_symlink():
        raise ValueError('no baseline symlinks')
    if not path.is_file():
        continue
    relative = str(path.relative_to(ORIGINAL))
    target = COPY / relative
    if not target.is_file() or target.is_symlink():
        raise ValueError('complete copied baseline file: ' + relative)
    original_inventory[relative] = dict(sha256=sha256(path.read_bytes()).hexdigest(), mode=path.stat().st_mode & 0o777)
    if relative not in ('native_cache.c', 'NATIVE-SOURCE.json'):
        if target.read_bytes() != path.read_bytes() or (target.stat().st_mode & 0o777) != original_inventory[relative]['mode']:
            raise ValueError('unchanged copied baseline file: ' + relative)
new_digest = sha256(changed.encode()).hexdigest()
for name, data in [('native_cache.c', changed.encode()),
                   ('NATIVE-SOURCE.json', (json.dumps(dict(sha256=new_digest), indent=2) + '\n').encode())]:
    path = COPY / name
    mode = original_inventory[name]['mode']
    path.chmod(mode | 0o200)
    path.write_bytes(data)
    path.chmod(mode)
receipt = dict(status='SOURCE_ONLY_DIAGNOSTIC_PREPARED',
               original_native_sha256=BASE_NATIVE_SHA, diagnostic_native_sha256=new_digest,
               exact_original_contribution_restored=True,
               exact_original_complete_c_source_restored=True,
               changed_baseline_files=['native_cache.c', 'NATIVE-SOURCE.json'],
               baseline_file_count=len(original_inventory),
               original_inventory=original_inventory, edits=edits,
               numerical_execution=False, compilation=False)
(HERE / 'SOURCE-EDITS.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
print(json.dumps({key: value for key, value in receipt.items() if key not in ('edits', 'original_inventory')}, sort_keys=True))
