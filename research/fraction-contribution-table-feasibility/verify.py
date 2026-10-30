"""Fresh finite coverage only; this is not a complete-qualifier performance check."""
import json
from pathlib import Path
from frozen import require
from finite import main
if __name__=='__main__':
 result=main()
 require(result==json.loads(Path(__file__).with_name('RESULT.json').read_bytes())['finite'],'complete finite table receipt')
 print('PASS_SCOPED_TABLE_FEASIBILITY_FINITE_ONLY')
