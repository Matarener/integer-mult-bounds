"""Install the exact source-audited G20 word and replay its native maps.

PR5657 supplies the new construction. PR5662 supplies the audited word and
frame-506 matcher. Native replay retains ai-nanachi PR5512 and PR5653 credit.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
import gzip,importlib.util,json,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
S=R/'source/vendor/g20'
PARTIAL=frozenset([462,463,466,468])


def need(condition,message):
    if not condition:raise ValueError(message)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def put(name,value):
    raw=(json.dumps(value,indent=2)+'\n').encode();path=R/name
    path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


for item in read(R/'INPUTS.json'):
    need(sha256((R/item['local']).read_bytes()).hexdigest()==item['sha256'],'Frozen input '+item['local'])
SOURCE=load('retained_g20_source',R/'source/local_relations.py')
source=SOURCE.source


def matcher(frames,word):
    record=read(R/'audited/RESULT.json')['matcher']
    w=[[F(x) for x in row] for row in record['forward']]
    wi=[[F(x) for x in row] for row in record['inverse']]
    frame=frames['506']
    need(w==list(map(list,zip(*[list(map(F,row)) for row in frame['B']+frame['A']]))),'Actual frame-506 basis')
    def product(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
    eye=[[F(i==j) for j in range(8)] for i in range(8)]
    need(product(w,wi)==eye and product(wi,w)==eye,'Both actual matcher directions')
    need(all(sum(F(x)*F(y) for x,y in zip(a,b))==0 for a in frame['A'] for b in frame['B']),'Orthogonal residual/complement')
    count=sum(e[0]=='Q' and e[2:]==[506,0,4] for e in word['records'])
    need(count==4 and record['common_denominator']==4,'New actual matcher occurrences and dyadic denominator')
    out=dict(record,local_occurrences=count,global_occurrences=18*count,
             paired_address_coefficient_terms_per_call=2*record['nonzero_coefficients'],
             pricing='Both directions and both paired address halves are charged inside the complete positive normalizer fee.')
    put('MATCHER.json',out);return out


def run():
    import native
    word=read(R/'audited/WORD.json.gz');base,frames,_=source()
    need(len(word['owned'])==39 and len(word['start'])==684,'Exact audited field allocation')
    result=native.replay(base,frames,word['records'],set(word['owned']))
    physical=[native.replay(base,frames,word['records'],set(word['owned']),m) for m in (101,101**2)]
    need(result['paid']=={1:1288,2:1342,3:56,4:57,5:102,6:10,7:9},'Actual full local invoice')
    m=matcher(frames,word)
    controls=[]
    for label,choose in [('missing_snapshot_clear',lambda e:e[0]=='ERASE' and e[1]==662 and e[2] is not None),
                         ('missing_refined_query',lambda e:e==['Q',9,506,115,2]),
                         ('missing_snapshot_return',lambda e:e[0]=='ERASE' and e[1]==662 and e[2] is None)]:
        bad=[e[:] for e in word['records']];bad.pop(next(i for i,e in enumerate(bad) if choose(e)))
        try:native.replay(base,frames,bad,set(word['owned']),101)
        except (ValueError,StopIteration):controls.append(label)
        else:raise ValueError('Corrupt native word accepted')
    (R/'WORD.json.gz').write_bytes((R/'audited/WORD.json.gz').read_bytes())
    data=dict(status='PASS_G20_REFINEMENT_NATIVE_ALL684_COLUMNS',stats=result,native_moduli=[v['native_modulus'] for v in physical],
              matcher=m,rejected_controls=controls,canonical_word_sha256=sha256(json.dumps(word['records'],separators=(',',':')).encode()).hexdigest())
    put('LOCAL-RESULT.json',data);return data


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
