"""Fresh finite replay only; full actual audit remains separately opt-in."""
import json
from pathlib import Path
from frozen import require
from finite import main
if __name__=='__main__':
 result=main()
 require(result==json.loads(Path(__file__).with_name('RESULT.json').read_bytes())['finite'],'complete finite feasibility receipt')
 print('PASS_SCOPED_NEGATIVE_FEASIBILITY_FINITE_REPLAY_ONLY')
