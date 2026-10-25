"""Read-only source-authenticated replay; no receipt regeneration."""
from pathlib import Path
from hashlib import sha256,sha1
import argparse,ast,json,tempfile,types
import check,cse
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def authenticate():
    for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
        path=ROOT/r['path'];need(path.is_file(),'missing input: '+r['path']);need(not any(p.is_symlink() for p in (path,*path.parents)),'symlinked input: '+r['path']);data=path.read_bytes()
        need(sha256(data).hexdigest()==r['sha256'],'source hash: '+r['path']);need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==r['git_blob'],'source blob: '+r['path'])
def guard_control():
    w,r,c,ch,p=check.setup(False)
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'controller.py';path.write_text((check.V/'controller.py').read_text().replace('permutation[field]','field'))
        try:cse.install(c.Callback,path,vars(c))
        except ValueError as e:need(str(e)=='exact reviewed Callback.weight AST','AST guard diagnostic')
        else:raise ValueError('changed AST accepted')
    return 'changed weight AST rejected'
def false_guard_control():
    source=(HERE/'cse.py').read_text();old='field < 64 and permutation[field] == field';need(source.count(old)==1,'mutant context')
    mutant=types.ModuleType('mutated_cse');exec(compile(source.replace(old,'field < 64'),'<false fixed guard>','exec'),mutant.__dict__)
    oldmodule=check.cse;check.cse=mutant
    try:
        try:check.case(h=0,field=57,adapted=True,seed=2)
        except ValueError as e:need(str(e)=='independent local-ring result','false guard changes mathematical result')
        else:raise ValueError('nonfixed PAIR incorrectly eliminated')
    finally:check.cse=oldmodule
    return 'nonfixed-field shortcut rejected: true coefficient 5, mutant 1'
def billing():
    source=(check.V/'stream.py').read_text();tree=ast.parse(source);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='add_pass')
    calls=[ast.unparse(n) for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='traverse']
    need(calls==['traverse(False)','traverse(True)'],'two physical ADD traversals')
    traverse=next(n for n in fn.body if isinstance(n,ast.FunctionDef) and n.name=='traverse');need(ast.unparse(traverse.body[0])=='coefficient = prepare_coefficient()','independent preparation each traversal')
    trace=ROOT/'research/selected-bit-physical-caller/inputs/pr2753/trace.py';code=trace.read_text()
    need('for stage in range(8):' in code and 'if stage in (0, 2, 4, 6):' in code and 'elif stage == 7:' in code and 'negative_inverse=stage == 3' in code,'pinned eight-stage leaf billing')
    return dict(positive_calls=4,negative_calls=2,cross_call_cache=False,full_physical_caller_closed=False)
def run(quick=False):
    pairs=[]
    configs=[dict(h=0,seed=1)] if quick else [dict(h=h,seed=1) for h in (0,1,2)]+[dict(h=0,field=57,seed=2),dict(h=1,kind='good',seed=2),dict(h=1,kind='unit',half=True),dict(h=1,kind='unit'),dict(h=0,field=70,seed=1),dict(h=1,negative=True),dict(h=2,history_kinds=['good','pair'],seed=2),dict(h=2,history_kinds=['unit','pair'],seed=1)]
    for args in configs:
        a,b=[check.case(adapted=x,**args) for x in (False,True)]
        need(a['result']==b['result'],'original/CSE result');need(b['preparations']<=a['preparations'],'preparation count monotone')
        need(b['record_tapes']==a['record_tapes']==11,'no additional record tape')
        need(b['index_backing']<=a['index_backing'] and b['residue_backing']<=a['residue_backing'],'no additional numerical backing in fixtures')
        pairs.append(dict(original=a,adapted=b))
    errors=[]
    if not quick:
        for mutation in ('high','root'):
            a,b=[check.case(h=1,adapted=x,mutation=mutation) for x in (False,True)]
            need(a['error']==b['error'],'same failed validation');errors.append(dict(original=a,adapted=b))
    return dict(status='PASS_FIXED_PAIR_CSE',cases=pairs,errors=errors,guard=guard_control(),mutant=(None if quick else false_guard_control()),billing=billing(),scope='actual serialized coefficient runtime on admitted fixtures; no full R437 payload or kappa improvement')
def main():
    p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');p.add_argument('--export',action='store_true');a=p.parse_args();authenticate()
    if a.export:
        from test_export import run_export
        run_export();print('PASS_FIXED_PAIR_CSE_GIT_FREE_EXPORT');return
    result=run(a.quick);receipt=json.loads((HERE/'RESULT.json').read_text())
    if a.quick:
        receipt=dict(receipt,cases=receipt['cases'][:1],errors=[],mutant=None)
    need(result==receipt,'committed exact receipt')
    print('PASS_FIXED_PAIR_CSE',len(result['cases']),'actual original/adapted pairs')
if __name__=='__main__':main()
