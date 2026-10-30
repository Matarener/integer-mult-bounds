"""Fresh allRAW andprimitive guardmutants; normal and-O scientific parity."""
from pathlib import Path
import gzip,json,importlib.util,time
H=Path(__file__).resolve().parent
def need(v,s):
    if not v:raise ValueError(s)
def main():
    import native
    st=time.process_time();w=json.loads(gzip.decompress((H/'inputs/WORD.json.gz').read_bytes()));g=json.loads(gzip.decompress((H/'inputs/GEOMETRY.json.gz').read_bytes()));f=native.frame_bank(g)
    programs={n:native.local_program(native.lower(w['records']),r)for n,r in [('forward',False),('reverse',True)]}
    reports={n:native.local_check(p,w,f,n=='reverse')for n,p in programs.items()};rows,signed=native.signed_checks(programs);fail=[]
    def reject(name,p,why):
        try:native.local_check(p,w,f,False)
        except ValueError as e:
            need(why in str(e),'wrongnative rejection '+name);fail.append({'defect':name,'rejection':str(e)})
        else:raise ValueError('native mutant passed '+name)
    p=[z[:]for z in programs['forward']];i=next(i for i,z in enumerate(w['records'])if z[5]==10);p.pop(i)
    reject('omitted_fresh_DIRTY_D0_ADD',p,'native full Boolean boundary')
    p=[z[:]for z in programs['forward']];i=next(i for i,z in enumerate(p)if z[0]==2);p[i][2]=660
    reject('old_private_namespace660',p,'native destination')
    p=[z[:]for z in programs['forward']];i=next(i for i,z in enumerate(p)if z[0]==0);p[i][4]=8
    reject('illegal_local_rank8_bulk',p,'native recursive rank')
    need(len(fail)==3,'allnative mutants')
    print(json.dumps({'status':'PASS_ACTIVE658_NATIVE_AND_MUTANTS','optimized':not __debug__,'native':reports,'signed':signed,'mutants':fail,'CPU':time.process_time()-st},indent=2))
if __name__=='__main__':main()
