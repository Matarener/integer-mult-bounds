"""nativepar (SPEED, Oct 28): worker for computing native pair verdicts in parallel.  NOT a CLI for people.
stdin: JSON [[key, frameA, frameB], ...]  ->  stdout: JSON {key: [ok_bool, rank_or_reason]}  computed with tkcommon.native_mod() (fastnative, or the reference
kernels when TK_NATIVE_REF=1 is inherited), i.e. exactly what accept.native_pairs / check.native_check compute serially.  Launched by accept.compute_pairs()."""
import sys,os,json
sys.dont_write_bytecode=True
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))      # also under python -I (tkstack sandbox), where the script dir is not on sys.path
from tkcommon import native_mod
def main():
    items=json.load(sys.stdin); N=native_mod(); out={}
    for k,a,b in items:
        ok,v=N.ok(tuple(a),tuple(b)); out[k]=[bool(ok),v]
    sys.stdout.write(json.dumps(out))
if __name__=='__main__': main()
