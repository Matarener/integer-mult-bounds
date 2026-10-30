"""Freeze only this newly owned native candidate; never edit old packets."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parent
def need(ok,message):
 if not ok:raise ValueError(message)
def main():
 pins=json.loads((ROOT/'INPUT-PINS.json').read_bytes())
 for x in pins['files']:
  p=ROOT/x['relative_path'];need(p.is_file()and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'],'Frozen source input drift '+x['relative_path'])
 files=[ROOT/'INPUT-PINS.json']+sorted((ROOT/'inputs').glob('*'))+sorted((ROOT/'provider').glob('*.py'))+sorted((ROOT/'provider'/'data').glob('*'))
 records=[{'relative_path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files if p.is_file()]
 manifest={'schema':'g20-private-native-runtime/1','created_at_utc':datetime.now(timezone.utc).isoformat(),'claim':'Native literal programme and positive finite fee schema only; ordinary saving remains unproved in this packet.','files':records}
 target=ROOT/'provider'/'MANIFEST.json';need(not target.exists(),'Runtime already frozen; make an explicit successor rather than overwrite')
 target.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps({'runtime_files':len(records),'manifest_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
