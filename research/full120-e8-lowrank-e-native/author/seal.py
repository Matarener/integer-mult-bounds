"""Payload-only SHA256 seal; no external runtime dependency."""
import argparse,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def payload():
 return sorted(p for p in HERE.rglob('*')if p.is_file()and p.name!='FILES.sha256'and p.suffix!='.log'and'__pycache__'not in p.parts)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 content=''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(HERE).as_posix()+'\n'for p in payload())
 target=HERE/'FILES.sha256'
 if a.write:target.write_text(content)
 elif target.read_text()!=content:raise ValueError('payload set or byte digest differs from locked seal')
 print('PASS_PAYLOAD_SEAL '+hashlib.sha256(content.encode()).hexdigest()+' '+str(len(payload()))+' files')
if __name__=='__main__':main()
