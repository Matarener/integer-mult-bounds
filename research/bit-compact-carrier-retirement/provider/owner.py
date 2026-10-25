"""Active436 owner adapter; all generic source windows/operator guards kept."""
from pathlib import Path
import hashlib,json,gzip,ast
_p=Path(__file__).resolve().parent/'upstream-owner.py';_b=_p.read_bytes()
if hashlib.sha256(_b).hexdigest()!='b6232c9f7f5d7b9a4be868e5e1d147b57e8e7ba9ddc0d35e7f7170c65b600c66':raise ValueError('authenticated upstream owner source')
_tree=ast.parse(_b);_changes=[]
for _node in _tree.body:
    if isinstance(_node,ast.FunctionDef)and _node.name in('audit','audit_emitted'):
        for _c in ast.walk(_node):
            if isinstance(_c,ast.Constant)and type(_c.value)is int:
                if _node.name=='audit'and _c.value==126144:_changes.append(['audit',126144,125568]);_c.value=125568
                if _node.name=='audit_emitted'and _c.value==660:_changes.append(['audit_emitted',660,658]);_c.value=658
if _changes!=[['audit',126144,125568],['audit_emitted',660,658]]:raise ValueError('exact owner arity changes')
_old_name=__name__;__name__='authenticated_inherited_library'
exec(compile(_tree,str(_p),'exec',dont_inherit=True),globals())
__name__=_old_name
R=436
PARTIAL={462:506,463:506,466:508,468:509}
PINS=dict(PINS,**{'WORD.json.gz':'69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b'})
_EXPECTED_ARTIFACTS={'ORDER': '8a153e3c5086e67735310bc47b2a83a41b55ba8ce102eb9a90e960d49328bbe4', 'CHARTS': '1fed568d534f901c83bc2e2465afdd714d02b12c5329745c84f3d6112ec7f722', 'SLOTS': 'af94b7a3f9cf1956de4c01692e1bb6f119c6af6ef1433dbd9a2382abe9c3778d', 'REMAINDERS': '0f96c293a3cfa5a95d516e2756fc55ba4215ff6bacb48e1346a407eaea0c8550', 'DISPATCH': '6e277a656954efc2e50e7e7265bff8fe074603ff5575c892602900ee60097067'}
def construct():
    summary=json.loads((HERE/'OWNERS.json').read_bytes());artifacts={}
    for name,pin in _EXPECTED_ARTIFACTS.items():
        raw=(HERE/'new-owners'/(name+'.json.gz')).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==pin,'newownedledgerpin '+name)
        artifacts[name]=json.loads(gzip.decompress(raw))
    need(summary['ordinaryRAW']==658 and summary['helpers']==436 and summary['W']==28416,'new658providerinventory')
    need(len(artifacts['SLOTS'])==436*9 and len(artifacts['DISPATCH'])==288,'newfiniteownercoverage')
    return summary,artifacts
