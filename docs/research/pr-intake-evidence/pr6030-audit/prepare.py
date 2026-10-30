"""Prepare pinned audit inputs. Douglas Colkitt / OpenAI Codex, Apache-2.0."""
import hashlib,json,shutil,sys
from pathlib import Path
A=Path(__file__).resolve().parent
ROOT=A.parents[3]
work=Path(sys.argv[1]).resolve()
if work.exists(): raise ValueError('Use a fresh work directory')
work.mkdir()
for name,digest in json.loads((A/'INPUTS.json').read_text())['files'].items():
 raw=(ROOT/name).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=digest: raise ValueError('Source pin '+name)
 dest=work/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
check='research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/check.py'
(work/'source'/check).write_bytes((A/'caller-check.py').read_bytes())
for name in ('run_caller.py','independent.py'):
 shutil.copy2(A/name,work/name)
shutil.copy2(ROOT/'docs/research/pr-intake-evidence/pr6030-repair/run_bounded.py',work/'run_bounded.py')
print('PASS_PREPARE_PINNED_6030_AUDIT')
