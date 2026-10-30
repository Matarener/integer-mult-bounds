"""Active658 native interface; original proper-rank/lifetime guards unchanged."""
from pathlib import Path
import hashlib,json,gzip
_p=Path(__file__).resolve().parent/'upstream-native.py'
_b=_p.read_bytes()
if hashlib.sha256(_b).hexdigest()!='db92b1c2e61c8b8f3d94581e1bcd921af881cdf9d8fd03eba646864195134f2a':raise ValueError('authenticated upstream native source')
_old_name=__name__;__name__='authenticated_inherited_library'
exec(compile(_b,str(_p),'exec',dont_inherit=True),globals())
__name__=_old_name
N,R=658,436
INPUTS=dict(INPUTS,**{'WORD.json.gz':'69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b'})
WORD_HASHES={'candidate':'a9507403c2b03c4c6295248da2538909938744683b8c5c771cd3efb6b19f5ced'}
def candidate(records):
    need(digest(records)=='a9507403c2b03c4c6295248da2538909938744683b8c5c771cd3efb6b19f5ced','active658 literal candidate source')
    return records
def main():
    raw=(ROOT/'inputs/WORD.json.gz').read_bytes();need(sha256(raw).hexdigest()=='69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b','active WORD source')
    w=json.loads(gzip.decompress(raw));raw=(ROOT/'inputs/GEOMETRY.json.gz').read_bytes()
    need(sha256(raw).hexdigest()==INPUTS['GEOMETRY.json.gz'],'exact geometry source')
    g=json.loads(gzip.decompress(raw));frames=frame_bank(g)
    programs={name:local_program(lower(candidate(w['records'])),rev)for name,rev in[('forward',False),('reverse',True)]}
    checks={name:local_check(p,w,frames,name=='reverse')for name,p in programs.items()}
    rows,signed=signed_checks(programs)
    print(json.dumps(dict(status='PASS_ACTIVE658_NATIVE',words={'candidate':{'local_checks':checks,'signed_checks':signed}},gram=gram_audit(frames)),indent=2))
if __name__=='__main__':main()
