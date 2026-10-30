from pathlib import Path
import runpy,shutil,sys
from portable import prepared
with prepared('baseline') as (root,baseline,stage):
 target=root/'owned_integer'/'diagnostic.py'
 target.parent.mkdir()
 shutil.copy2(Path(__file__).with_name('owned_integer')/'diagnostic.py',target)
 sys.argv=[str(target)]
 runpy.run_path(str(target),run_name='__main__')
