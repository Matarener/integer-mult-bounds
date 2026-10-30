from portable import prepared
import runpy
with prepared('complete-C') as (_,baseline,stage):
 runpy.run_path(str(stage/'candidate_full.py'),run_name='__main__')
