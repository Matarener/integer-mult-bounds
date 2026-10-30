"""Explicit immutable owner-source fetch; writes only to a new external folder."""
from pathlib import Path
import argparse,hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();p=a.output.resolve()
    if p.exists() or p.is_relative_to(ROOT):raise ValueError('fresh external directory required')
    pins=json.loads((ROOT/'EXTERNAL-SOURCES.json').read_text());p.mkdir(parents=True)
    for rel,digest in pins['files'].items():
        data=urllib.request.urlopen(pins['base_url']+rel,timeout=120).read()
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('immutable source digest '+rel)
        q=p/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
    print('PASS_FETCHED_IMMUTABLE_OWNER_SOURCES')
if __name__=='__main__':main()
