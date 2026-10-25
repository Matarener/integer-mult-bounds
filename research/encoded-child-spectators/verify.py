#!/usr/bin/env python3
"""Exact same-input before/after child spectator construction and invoices."""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from runtime import authenticate,need
from bench import pair
from cases import cases


def read(path):
    def unique(pairs):
        out={}
        for key,value in pairs:
            need(key not in out,'duplicate receipt key');out[key]=value
        return out
    return json.loads(path.read_text(),object_pairs_hook=unique)


def canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False)


def result():
    authenticate();rows=[];timings=[]
    for case in cases():
        row=pair(case)
        timings.append({'case':case['name'],'precision':case['w'],
                        'original':row['original'].pop('seconds_observation'),
                        'shared':row['shared'].pop('seconds_observation')})
        need(row['total_action_saving']>0,'complete named-case source-action improvement')
        rows.append(row)
    return {'status':'PASS_ENCODED_CHILD_SPECTATORS','base':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
            'assignment_seed':4,'domain':'15 stated complete geometry pairs; all6 branch shapes at w1/w3 plus recursive-width/q5/remainder boundary cases.',
            'pairs':rows,'physical_dispatch_stock_caller':'Not admitted by this geometry/action certificate.'},timings


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    dest=HERE/'CERTIFICATE.json'
    if args.write:need(not dest.exists(),'refuse certificate overwrite')
    data,timing=result()
    if args.write:
        with dest.open('x') as stream:stream.write(json.dumps(data,indent=2,sort_keys=True)+'\n')
        with (HERE/'TIMINGS.json').open('x') as stream:stream.write(json.dumps({'environment':'CPython3.12.14/Linux; single same-input observations, not a stable runtime speedup claim.','seconds':timing},indent=2)+'\n')
    else:need(canonical(data)==canonical(read(dest)),'complete typed spectator receipt')
    print('PASS_ENCODED_CHILD_SPECTATORS pairs='+str(len(data['pairs'])))


if __name__=='__main__':main()
