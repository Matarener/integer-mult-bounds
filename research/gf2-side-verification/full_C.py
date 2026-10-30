from pathlib import Path
import os,runpy,sys
here=Path(__file__).resolve().parent
output=Path(os.environ['CROC_GF2_SIDE_OUTPUT']).resolve()
if output.is_relative_to(here):raise ValueError('external scientific output required')
sys.argv=[str(here/'compare_side_verifier.py'),'--mode','candidate','--expected-complement-sha256','7dec2bf33303c37e1c699609e83768d61df7e19104d34a26a148f66d5ccc4838','--output',str(output)]
runpy.run_path(sys.argv[0],run_name='__main__')
