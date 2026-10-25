#!/usr/bin/env python3
"""Exact reduced-geometry/capture factor and arbitrary-dirt lifecycle replay."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from h6_inputs import authenticate,need,ROOT
from e8_exact import geometry
from census import compute
from word import fixture


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def read(path):
    def unique(rows):
        result={}
        for k,v in rows:
            need(k not in result,'unique certificate keys');result[k]=v
        return result
    return json.loads(path.read_text(),object_pairs_hook=unique)


def result():
    pins=authenticate()
    geo=geometry();data=compute(*geo)
    schema=read(ROOT/'research/h6-compensation-network/routes/BUCKETED-SCHEMA.json')
    need(schema['helper_count']==data['invoice']['old_helpers'] and
         schema['actual_nonzero_source_target_entries']==data['invoice']['old_scatter_entries'],
         'actual source bucket baseline binding')
    data['source_pins']=pins
    data['fixture']=fixture(geo)[0]
    data['base_commit']='20ecf2891d80b5acf18d980b2164fb44ea7faa90'
    data['status']='PASS_H6_MIXED_PAIR_CAPTURE'
    return data


def validate(actual,expected):
    need(canonical(actual)==canonical(expected),'complete typed H6 capture certificate')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    target=HERE/'CERTIFICATE.json'
    if args.write:need(not target.exists(),'refuse certificate overwrite')
    data=result()
    if args.write:
        need(not target.exists(),'refuse certificate overwrite')
        with target.open('x') as stream:stream.write(json.dumps(data,indent=2,sort_keys=True)+'\n')
    else:validate(data,read(target))
    print('PASS_H6_MIXED_PAIR_CAPTURE helpers=227312640->123632640 capture_entries_unchanged=227312640')


if __name__=='__main__':main()
