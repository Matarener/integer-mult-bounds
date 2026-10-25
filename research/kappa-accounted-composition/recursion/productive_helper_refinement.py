#!/usr/bin/env python3
"""Change original idle-bin allocation and attain213 productive helpers."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import productive_helper_forest as B

def construct():
    hosts = []
    pairs = [(56,[9,7]),(56,[7,9]),(18,[9,6]),(18,[6,9]),(16,[9,5]),(16,[5,9]),(44,[8,8])]
    for stages in ([0,1],[3,4]):
        for count, row in pairs:
            hosts.extend({'kind':'original_idle','capacity':16,'stages':stages,'widths':row} for _ in range(count))
    for r, count in [(8,93),(7,56),(6,18),(5,28),(0,29)]:
        hosts.extend({'kind':'original_idle','capacity':8,'stages':[2],'widths':[r]} for _ in range(count))
    for special in [0,1,3,4]:
        for value, count in [(5,12),(0,29)]:
            row = [9,9,9,9,9]
            row[special] = value
            hosts.extend({'kind':'productive','capacity':41,'stages':[0,1,2,3,4],'widths':row} for _ in range(count))
    hosts.extend({'kind':'productive','capacity':41,'stages':[0,1,2,3,4],'widths':[8,8,9,8,8]} for _ in range(49))
    result = B.verify_case('p2_changed_original_assignment_213_hosts',1,661,41,5,hosts,
        {'original_pair_bins':pairs,'global_templates':[
            {'count':48,'middle_width':9,'other_widths':[9,9,9,5],'each_5_position_count':12},
            {'count':116,'middle_width':9,'other_widths':[9,9,9,0],'each_0_position_count':29},
            {'count':49,'middle_width':9,'other_widths':[8,8,8,8]}]})
    assert result['productive_fields_per_controller'] == 213
    assert result['residual_profile_per_controller'] == {'1':'128','2':'82','3':'28','5':'116','8':'29'}
    result['minimum_in_fixed_middle_window'] = {'bound':213,'attained':True,
        'proof':'The middle call needs213 width9 helper roles. Every original idle field available there has rank8. A productive field can host at most one simultaneous native helper role. Therefore at least213 new productive fields are required for this same fixed middle window. The displayed213-field word-width packing attains the bound. This does not cover staggered controllers, changed helper interfaces, or different original idle windows.'}
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    here=Path(__file__).resolve().parent
    base_receipt=here/'PRODUCTIVE-HELPER-FOREST.json'
    assert base_receipt.exists(), 'Reproduce the base certificate first.'
    r={'status':'PASS','scope':'Exact changed idle-bin allocation, complete tariff and fixed-middle-window host minimum. Native whole-block adapters and main-controller closure remain unverified here.',
       'sources':{name:hashlib.sha256((here/name).read_bytes()).hexdigest() for name in ['productive_helper_refinement.py','productive_helper_forest.py','PRODUCTIVE-HELPER-FOREST.json']},
       'case':construct()}
    args.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':r['status'],'productive_fields':r['case']['productive_fields_per_controller'],'total_fields':r['case']['total_fields_per_controller']}))

if __name__=='__main__':
    main()
