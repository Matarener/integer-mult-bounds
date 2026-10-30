"""Replay all probe correctness controls without repeating its timing trial."""
from hashlib import sha256
import inspect,json,tarfile
from pathlib import Path
import micro
from table_parent import code_shape

HERE=Path(__file__).resolve().parent
ARCHIVE='7b142567acacac5182045bf8daa8780e916661c2cf343dbf81b13c88ead85d64'

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    archive=HERE/'inputs/PR5864.tar'
    need(sha256(archive.read_bytes()).hexdigest()==ARCHIVE,'exact complete PR5864 export')
    with tarfile.open(archive,'r:') as stream:
        receipt=json.loads(stream.extractfile('.research-export.json').read())
        need(receipt['commit']=='3f15c943e4ad6479f03e674c80fff1269a16ccfe' and len(receipt['files'])==163,'exact parent source head/census')
        native=stream.extractfile('research/fraction-native-qualification/native_cache.c').read()
        need(native==(HERE/'native_parent.c').read_bytes(),'exact parent native C bytes')
    start=native.index(b'        for(int k=0;k<3;k++){',native.index(b'static PyObject *event_apply'))
    end=native.index(b'        int truth=',start)
    need(native[start:end]==(HERE/'PARENT-SCORE-LOOP.txt').read_bytes(),'exact retained parent score loop')
    raw=inspect.getsource(micro.main);module_raw=Path(micro.__file__).read_text()
    need(sha256(module_raw.encode()).hexdigest()==json.loads((HERE/'FINITE-SOURCE.json').read_text())['module_sha256'],'exact measured probe module')
    need(sha256(raw.encode()).hexdigest()==json.loads((HERE/'FINITE-SOURCE.json').read_text())['function_sha256'],'exact measured probe source')
    namespace=dict(micro.__dict__);exec(compile(module_raw,'<probe-source-binding>','exec'),namespace)
    need(code_shape(namespace['main'].__code__)==code_shape(micro.main.__code__),'live probe executable agrees')
    seam='    observations=[];groups=32768\n'
    need(raw.count(seam)==1,'unique boundary after all ten correctness controls')
    entry="\nif __name__=='__main__':main()\n"
    need(module_raw.count(entry)==1,'unique unchanged module entry guard')
    finite=module_raw[:module_raw.index(seam)]+'''    result=dict(prefix_cases=33,controls=controls,control_count=len(controls),runtime_current=binding.still_current(token))
    print(json.dumps(dict(status='PASS_NATIVE_SCORE_FINITE_ONLY',result=result,build=probe_backend.receipt()),sort_keys=True))
    return result
'''+module_raw[module_raw.index(entry):]
    exec(compile(finite,'<all-probe-controls-no-timing>','exec'),namespace)
    need(namespace['main']()==json.loads((HERE/'RESULT.json').read_text()),'all retained finite probe controls')
    print('PASS_NATIVE_SCORE_DISPATCH_FEASIBILITY_FINITE_ONLY')

if __name__=='__main__':main()
