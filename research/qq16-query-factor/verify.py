"""Authenticated, read-only exact replay; Apache-2.0, AI assistance disclosed."""
import argparse
from copy import deepcopy
import hashlib
import types
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
MANIFEST_PINS = {'SOURCES.json': 'e2624f8406598e2ab7e04d4d26f58044a2fe1c93436553d096c5b64c0be16394', 'PREDECESSORS.json': 'f3184201fdc0e3f8c6f3ff29b64118a555e5b5e85174aa7e97664099a0a9dbdf'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def authenticate():
    need(len(MANIFEST_PINS) == 2, 'source manifests must be frozen')
    for name, expected in MANIFEST_PINS.items():
        need(digest((HERE/name).read_bytes()) == expected, 'manifest SHA256: '+name)
    sources = json.loads((HERE/'SOURCES.json').read_text())
    predecessors = json.loads((HERE/'PREDECESSORS.json').read_text())
    checked = []
    for row, base in [(r,ROOT) for r in sources['files'] if r['usage']=='input'] + [(r,HERE) for r in predecessors['files']]:
        name = row.get('local',row['path'])
        raw = (base/name).read_bytes()
        need(digest(raw) == row['sha256'], 'source SHA256: '+name)
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(blob == row['git_blob'], 'source Git blob: '+name)
        checked.append({'path':name,'sha256':digest(raw),'git_blob':blob})
    return checked


def load(name):
    path = HERE/(name+'.py')
    module = types.ModuleType('qq16_factor_'+name)
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def compute():
    inputs=authenticate()
    primary,cost,native=load('primary'),load('cost_audit'),load('native_adapter')
    p,c,n=primary.compute(),cost.compute(),native.compute()
    word=json.loads((HERE/'CANDIDATE-WORD.json').read_text())
    need(p['candidate_word_sha256']==digest(canonical(word)), 'candidate canonical word mismatch')
    a=c['candidate_arithmetic_and_ownership']
    need(a['word_sha256']==digest((HERE/'CANDIDATE-WORD.json').read_bytes()),'candidate raw word mismatch')
    need(p['literal_word_events']==a['operations']=={'add_view':6112,'clear':104},'independent literal event counts')
    need(p['owned_physical_fields']==a['owned_fields']==33,'independent owned stock count')
    need(a['scalar_real_primitive_allowance']==66832 and c['known_scalar_increment_with_candidate']==95448,'same-boundary scalar ledger')
    need(n['normalized_route_screen']['normalization_H1_total']==c['generic_native_screen']['ingress_and_egress_H1']==224,'independent normalization count')
    need(n['normalized_route_screen']['optimistic_saving_H1_units_upper_bound']==-c['generic_native_screen']['ingress_and_egress_excess_at_least_H1']==-128,'independent conditional native screen')
    # Cheap literal semantic controls on one free current Y0 column. They alter
    # actual operations, not expected receipt strings; baseline has all224 checks.
    current=[{}for _ in range(224)];current[112]={(0,primary.I73):primary.F(1)}
    baseline=primary.replay_candidate(word,current)
    dirty=deepcopy(word);dirty['events'].remove(['clear','q0'])
    need(primary.replay_candidate(dirty,current)!=baseline,'missing initial dirty compensation accepted')
    missing=deepcopy(word)
    # Suppress n acquisition up to its first use to form t, preserving clears.
    cut=next(i for i,e in enumerate(missing['events'])if e[0]=='add_view' and e[1].startswith('q24'))
    missing['events']=[e for i,e in enumerate(missing['events'])if not(i<cut and e[0]=='add_view' and e[1] in {'q'+str(j)for j in range(16,24)})]
    need(primary.replay_candidate(missing,current)!=baseline,'omitted future logger accepted')
    data,_=primary.load_sources();r=primary.source_routes(data['phases'])
    need(primary.product(r[1],r[76])!=primary.product(r[76],r[1]),'route order control lacks actual separating matrices')
    return {'schema_version':1,'status':'PASS_QQ16_QUERY_FACTOR_AND_NATIVE_ROUTE_OBSTRUCTION',
      'scientific_base':'bb4bccbf42844d2801487450727c2f63e10d1d0f','sources':inputs,
      'implementation_sha256':{name:digest((HERE/name).read_bytes())for name in ('primary.py','cost_audit.py','native_adapter.py')},
      'primary':p,'independent_cost_and_ownership':c,'independent_native_audit':n,
      'discriminating_controls':{'missing_initial_owned_CLEAR':'rejected: dirty initial q0 contaminates external data','missing_future_logger_n':'rejected on free current Y0','reversed_actual_owner_product':'distinct73D matrices','wrong_native_sign':'native audit rejects','constant_payload_only':'passes logical control while nonzero character rejects raw physical lift'},
      'evidence_status':{'logical':'exact rational operator replay on full actual owner ring, payload character0; scoped algebraic derivation for displayed logical contracts','native':'concrete first-gate obstruction to owner/ADD-only lift; generic normalization rejected under explicit comparable tariff','restoration':'all33 declared owned fields arbitrary dirty initially, erased before use and zero finally; pair1/helpers untouched; exclusive physical stock and recursive native scratch lease unknown','review':'AI-assisted adversarial review, shared context; no formal-kernel or independent human mathematical acceptance','supplier':'not established','conditional_kappa_change':None},
      'publication_status':'frozen scientific receipt; publication and hosted CI separately recorded'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    receipt = HERE/'RESULT.json'
    if args.write:
        need(not receipt.exists(),'refusing to overwrite existing RESULT.json')
    result = compute()
    if args.write:
        with receipt.open('x') as stream:
            stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(canonical(json.loads(receipt.read_text())) == canonical(result),'complete typed receipt mismatch')
    print(result['status'])

if __name__ == '__main__':
    main()
