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
MANIFEST_PINS = {'SOURCES.json': '9b8f836046ab6fdf1dbe94aaaf6674c14c86c3f03b1a50f220b4492dd6f0c727', 'PREDECESSORS.json': '050861175ede4a18f3fd587f8b18af6a2fda8f019be730144afd6429d3b33102'}


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
    module = types.ModuleType('qq16_paid_'+name)
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


def compute():
    inputs = authenticate()  # authenticate before importing scientific implementations
    primary, cost = load('primary'),load('cost_audit')
    p,c = primary.compute(),cost.compute()
    need(p['routed_ordinary_witness']['QQ16_bridge_pair1_Y1'] == c['owner_only_test']['input_at_identity_owner_bridge_Y1_port1'] == '1/2', 'independent bridge witnesses disagree')
    need(len(c['owner_only_test']['nonzero_ordinary_Y_ports']) == 96 and p['routed_ordinary_witness']['all96_ordinary_Y_operator_rows_nonzero'], 'ordinary support disagreement')
    need(p['decoder_boundary']['actual_PR4015_events'] == sum(c['decoder4015'][k] for k in ('begin','end','line','map','clear','add','checkpoint')), 'decoder literal invoice disagreement')
    # Mutate a real emitted F0 scalar coefficient, then require its original
    # decoder inverse identity to fail. This is not a receipt-only mutation.
    data,_ = primary.load_sources()
    packet = deepcopy(data['packet'])
    gate = packet['programs']['F_0'][1][2][0][1]
    need(gate[:3] == ['add',['L',0],['L',76]], 'source-bound mutation site')
    gate[3] *= 2
    changed_f = primary.scalar_replay(primary.flatten(packet,'F_0'))
    unchanged_b = primary.scalar_replay(primary.flatten(data['packet'],'B_1_2'))
    decoder = primary.decoder_replay(data['decoder_word'])
    wrong_roundtrip = primary.multiply(decoder,primary.multiply(unchanged_b,changed_f))
    need(wrong_roundtrip != [{i:primary.F(1)}for i in range(224)], 'altered F0 coefficient falsely accepted')
    routes = primary.source_routes(data['phases'])
    need(primary.product(routes[1],routes[76]) != primary.product(routes[76],routes[1]), 'route-order control lacks separating witness')
    controls = {'mutated_operation':'F0 X_A_fused_query first ADD numerator1->2',
                'altered_Q_decoder_identity':'rejected',
                'reversed_owner_product':'distinct actual73D matrices',
                'collapsed_owner_route':'independent audit makes all96 ordinary residuals zero',
                'wrong_decoder_entrance':'D_G differs from identity rank32',
                'wrong_current_vs_recovered_bridge':'-1 versus0 on X1 input'}
    return {'schema_version':1,'status':'PASS_QQ16_ACTUAL_PAIR_SELECTED_WRITE_OBSTRUCTION',
            'scientific_base':'bb4bccbf42844d2801487450727c2f63e10d1d0f',
            'claim_kind':'source-bound exact obstruction to a specified post-pair write restriction',
            'sources':inputs,'implementation_sha256':{name:digest((HERE/name).read_bytes())for name in ('primary.py','cost_audit.py')},'discriminating_controls':controls,'primary':p,'independent_cost_and_owner_audit':c,
            'evidence_status':{'exact_replay':'reproduced with rational arithmetic and full73D owner matrices','proof':'scoped algebraic argument; AI assisted review, no formal-kernel or human mathematical acceptance','supplier':'not established','conditional_kappa_change':None},
            'publication_status':'frozen scientific receipt; publication and CI are reported separately'}


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
