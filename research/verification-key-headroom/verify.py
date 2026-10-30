"""Bounded archive checks; never run the historical benchmark/capture entrypoint."""
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

ROOT=Path(__file__).resolve().parent
PINS=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
for name in ('verify.py','archive_support.py'):
    raw=(ROOT/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]['sha256']:raise ValueError('protected verifier source: '+name)
S=types.ModuleType('_headroom_archive_support');S.__file__=str(ROOT/'archive_support.py')
exec(compile((ROOT/'archive_support.py').read_bytes(),S.__file__,'exec'),S.__dict__)


def finite():
    import struct
    import tempfile
    import shutil
    S.need(sys.implementation.name=='cpython' and sys.version_info[:2]==(3,12) and sys.platform=='linux' and struct.calcsize('P')==8,'Linux 64-bit CPython 3.12 with existing cc/headers')
    stage=ROOT/'context'/S.STAGE
    loader=S.source_module('load_pilot',stage/'load_pilot.py')
    approved=S.source_module('_headroom_approved_pilot',stage/'run_pilot.py')
    temporary=Path(tempfile.mkdtemp(prefix='key-headroom-finite-'))
    try:
        module,build=loader.compile_and_load(temporary)
        result=approved.finite_controls(module)
        S.need(result['status']=='PASS_FINITE_KEY_ONLY' and len(result['receipts'])==82 and result['natural_rehashes']==50,'all unchanged finite controls executed')
        S.need(build['returncode']==0 and build['stdout_bytes']==build['stderr_bytes']==0,'clean compiler with warnings as errors')
        answer=dict(status='PASS_ARCHIVED_FINITE_CONTROLS',receipts=82,natural_rehashes=50,optimized=sys.flags.optimize,
                    source_sha256=build['source_sha256'],no_capture_or_benchmark=True)
    except BaseException as error:
        error.add_note('Finite build/control evidence retained at '+str(temporary))
        (temporary/'FAILURE.json').write_text(json.dumps(dict(type=type(error).__name__,message=str(error),evidence=str(temporary)),indent=2)+'\n')
        raise
    else:
        shutil.rmtree(temporary)
        return answer


def data():
    from collections import deque
    from hashlib import sha256 as new_hash
    import gzip
    import struct
    payload=json.loads((ROOT/'data/DATA.json').read_text())
    formatting=json.loads((ROOT/'FORMAT.json').read_text())
    S.need(formatting['ids']==dict(byteorder='little',item_bytes=8,type='unsigned 64-bit integer'),'explicit canonical ID format')
    outputs=payload['canonical_outputs'];directory=ROOT/'data'
    prefixes=json.loads(S.read_plain_gzip(directory/outputs['prefixes']['file'],outputs['prefixes']))
    S.need(type(prefixes) is list and len(prefixes)==(S.CALLS+79)//80,'complete prefix count')
    for prefix in prefixes:S.need(type(prefix) is list and len(prefix)==5 and all(type(x) is int for x in prefix),'exact prefix fields')
    for name in ('ids','flags'):
        pin=outputs[name];S.need(S.digest_file(directory/pin['file'])==pin['transport_sha256'],'committed output transport pin')
    cache={};fifo=deque();calls=hits=misses=evictions=prefix_index=0
    id_hash=new_hash();flag_hash=new_hash();id_bytes=flag_bytes=0
    corpus=payload['actual_corpus']
    with gzip.open(directory/outputs['ids']['file'],'rb') as ids,gzip.open(directory/outputs['flags']['file'],'rb') as flags:
        for block in S.corpus_blocks(directory/corpus['file'],corpus['sha256']):
            raw_ids=ids.read(8*len(block));raw_flags=flags.read(len(block))
            S.need(len(raw_ids)==8*len(block) and len(raw_flags)==len(block),'complete ordered ID/flag block')
            id_hash.update(raw_ids);flag_hash.update(raw_flags);id_bytes+=len(raw_ids);flag_bytes+=len(raw_flags)
            for offset,key in enumerate(block):
                calls+=1;value=cache.get(key);flag=0
                if value is not None:hits+=1
                else:
                    misses+=1;value=misses;flag=1
                    if len(fifo)==16384:
                        del cache[fifo.popleft()];evictions+=1;flag=3
                    cache[key]=value;fifo.append(key)
                S.need(struct.unpack_from('<Q',raw_ids,offset*8)[0]==value and raw_flags[offset]==flag,'every ordered ID/hit/miss/eviction result')
                if calls%80==0 or calls==S.CALLS:
                    S.need(prefixes[prefix_index]==[calls,hits,misses,evictions,len(cache)],'every cumulative prefix')
                    prefix_index+=1
        S.need(ids.read(1)==b'' and flags.read(1)==b'','no trailing output bytes')
    for name,h,count in (('ids',id_hash,id_bytes),('flags',flag_hash,flag_bytes)):
        S.need(count==outputs[name]['uncompressed_bytes'] and h.hexdigest()==outputs[name]['uncompressed_sha256'],'complete authoritative '+name+' payload hash')
    expected=payload['capture']['original_actual']['statistics']
    actual=dict(calls=calls,hits=hits,misses=misses,evictions=evictions,bypasses=0,resident=len(cache),capacity=16384)
    S.need(actual==expected and calls==S.CALLS and prefix_index==len(prefixes) and len(fifo)==len(cache),'complete original actual counters')
    return dict(status='PASS_COMPLETE_ACTUAL_KEY_DATA',statistics=actual,prefixes=prefix_index,
                all_ordered_items_checked=True,streaming=True,no_C_capture_or_timing=True,
                regenerated_compression_is_not_mathematical_identity=True)


def context():
    import tempfile
    with tempfile.TemporaryDirectory(prefix='key-headroom-context-') as temporary:
        reconstructed=S.reconstruct(Path(temporary)/'context')
        checked=S.validate_context(reconstructed)
        official=S.official_baseline(reconstructed)
        return dict(status='PASS_EXACT_MEASURED_CONTEXT',context=checked,official_input=official,no_scientific_import_or_execution=True)


def main():
    S.need(len(sys.argv)==2 and sys.argv[1] in ('finite','data','context'),'choose exactly finite, data or context')
    S.authenticate()
    result={'finite':finite,'data':data,'context':context}[sys.argv[1]]()
    S.authenticate()
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
