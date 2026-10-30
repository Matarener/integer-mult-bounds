"""Explicitly fetch immutable PR3945 owner inputs into a fresh directory.
Chris R / Clear1nsight with OpenAI Codex assistance. Apache-2.0.
"""
import argparse, concurrent.futures, hashlib, json, urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args()
    manifest=json.loads((HERE/'EXTERNAL-SOURCES.json').read_text())
    if args.output_dir.exists():raise ValueError('output directory must not exist')
    args.output_dir.mkdir(parents=True)
    base='https://raw.githubusercontent.com/'+manifest['repository']+'/'+manifest['head']+'/'+manifest['prefix']
    def get(item):
        relative,pin=item
        with urllib.request.urlopen(base+relative,timeout=60) as response:data=response.read()
        if len(data)!=pin['bytes'] or hashlib.sha256(data).hexdigest()!=pin['sha256']:
            raise ValueError('immutable source mismatch: '+relative)
        output=args.output_dir/relative;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data)
        return relative
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:completed=sorted(pool.map(get,manifest['files'].items()))
    receipt={'status':'PASS_FETCHED_EXACT_IMMUTABLE_INPUTS','head':manifest['head'],'files':completed,
             'bytes':sum(p['bytes'] for p in manifest['files'].values()),'manifest_sha256':hashlib.sha256((HERE/'EXTERNAL-SOURCES.json').read_bytes()).hexdigest(),
             'scope':'Byte acquisition only; run verify.py --source-root for mathematical audit.'}
    (args.output_dir/'FETCH-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
