#!/usr/bin/env python3
"""Independent bounded review of primary replay/manifest/package plumbing.

The only executed root function is the isolated phase-receipt comparator,
with controlled fixtures. No native/full release or packaging is rerun here.
Source trees, archived receipts and the prior ZIP are only read.
"""
import ast
from copy import deepcopy
import gzip,hashlib,json,math
from pathlib import Path
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent;SCOPE=HERE.parent;REPO=SCOPE.parents[1]
PRIOR=REPO/'research/kappa-1745-continuation'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()


def read(path):
    b=path.read_bytes();return json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)


def need(ok,why):
    if not ok:raise ValueError(why)


def audit_dependency_coverage():
    prior=read(PRIOR/'MANIFEST.json');available={}
    for base,key in ((PRIOR,'files'),(REPO,'repository_dependencies')):
        for name,record in prior[key].items():available[(base/name).relative_to(REPO).as_posix()]=record
    additional='research/shared-phase-repair-rank/vendor/PR3220-PROOF.md'
    available[additional]={'bytes':(REPO/additional).stat().st_size,'sha256':sha(REPO/additional)}
    catalogues=[('complex-word/AUDIT-INPUTS.json','files'),
                ('operator-correction/REPLAY-INPUTS.json','input_files'),
                ('complex-architecture/REPLAY-DEPENDENCIES.json','repository_dependencies'),
                ('operator-correction/PORTABLE-DEPENDENCIES.json','input_files')]
    checks=[];all_inputs=set()
    for name,key in catalogues:
        data=read(SCOPE/name);required=data[key];missing=[];mismatch=[]
        for relative,record in required.items():
            digest=record['sha256'] if isinstance(record,dict) else record
            path=REPO/relative;all_inputs.add(relative)
            if relative.startswith('research/kappa-operator-repair/'):
                # freeze_manifest recursively includes this whole new scope,
                # except explicit runtime directories; none of these inputs
                # lies inside such a directory.
                need(not any(x in {'release-work','__pycache__','python-deps','replay-output',
                                  'full-replay-output','native-replay-output'} for x in path.relative_to(SCOPE).parts),relative)
                expected={'sha256':sha(path)}
            else:expected=available.get(relative)
            if expected is None:missing.append(relative)
            elif expected['sha256']!=digest or sha(path)!=digest:mismatch.append(relative)
        need(not missing and not mismatch,(name,missing,mismatch))
        checks.append({'catalogue':name,'catalogue_sha256':sha(SCOPE/name),'required_inputs':len(required),
                       'missing':missing,'mismatched':mismatch})
    return checks,all_inputs


def audit_phase_comparator():
    replay=SCOPE/'replay.py';tree=ast.parse(replay.read_text())
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    function=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='compare_phase_receipt')
    isolated=ast.Module(body=[function],type_ignores=[]);ast.fix_missing_locations(isolated)
    comparisons=[];namespace=dict(read=read,need=need,sha=sha,REPO=REPO,json=json,hashlib=hashlib,math=math,comparisons=comparisons)
    exec(compile(isolated,str(replay),'exec'),namespace)
    compare=namespace['compare_phase_receipt'];fixtures=HERE/'fixtures';fixtures.mkdir(exist_ok=True)
    expected=SCOPE/'composed-supplier/native-base/native/local/CLIFFORD-REVIEW.json'
    original=read(expected);checks=[]
    def run(name,data,accept):
        path=fixtures/(name+'.json');path.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
        try:compare(path,expected)
        except (ValueError,KeyError,TypeError):accepted=False
        else:accepted=True
        need(accepted==accept,(name,accepted,accept));checks.append({'case':name,'accepted':accepted,'sha256':sha(path)})
    same=deepcopy(original);same['seconds']+=1.25;run('runtime_only_change',same,True)
    bad=deepcopy(same);bad['canonical_word_sha256']='0'*64;run('changed_word_binding',bad,False)
    bad=deepcopy(same);bad['extra_phase_result']={'seconds':17};run('nested_new_field_is_not_ignored',bad,False)
    bad=deepcopy(same);bad['seconds']=float('nan');run('nonfinite_runtime',bad,False)
    bad=deepcopy(same);bad['seconds']=True;run('boolean_runtime',bad,False)
    bad=deepcopy(same);bad.pop('seconds');run('missing_runtime',bad,False)
    need(len(comparisons)==1,'Only the correct semantic receipt comparison is recorded')
    return checks,comparisons[0]


def main():
    HERE.mkdir(exist_ok=True)
    dependencies,inputs=audit_dependency_coverage();controls,comparison=audit_phase_comparator()
    native_names=['CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json',
                  'INDEPENDENT-LOCAL-REPLAY.json','CLIFFORD-REVIEW.json','RESIDUAL-ADAPTERS.json']
    inspected={}
    for tag in ('base','extra'):
        for name in native_names:
            path=SCOPE/('composed-supplier/native-'+tag)/'native/local'/name
            value=read(path)
            def scan(v,p=()):
                found=[]
                if isinstance(v,dict):
                    for k,x in v.items():
                        if k in {'seconds','elapsed','elapsed_seconds','time','argv','command','python','source_path','word_path'}:found.append(list(p+(k,)))
                        if isinstance(x,(dict,list)):found+=scan(x,p+(k,))
                elif isinstance(v,list):
                    for i,x in enumerate(v):
                        if isinstance(x,(dict,list)):found+=scan(x,p+(i,))
                return found
            found=scan(value);need(found==([['seconds']] if name=='CLIFFORD-REVIEW.json' else []),(tag,name,found))
            inspected[path.relative_to(REPO).as_posix()]={'sha256':sha(path),'runtime_fields':found}
    previous=REPO.parents[1]/'deliverables/integer-mult-bounds-kappa-1745-continuation.zip'
    expected_old='f2406e81f2548873cfe624b316aa2a59f48ada97864e65d51135f40e5751db05'
    # Archive packaging itself is not run. Check the fixed source archive and
    # the one new external dependency if that path already occurs there.
    previous_sha=sha(previous);need(previous_sha==expected_old,'Exact previous full artifact')
    additional='research/shared-phase-repair-rank/vendor/PR3220-PROOF.md'
    with ZipFile(previous) as z:
        name='integer-mult-bounds/'+additional
        if name in z.namelist():need(hashlib.sha256(z.read(name)).hexdigest()==sha(REPO/additional),'Existing old member matches newly required dependency')
        old={'sha256':previous_sha,'bytes':previous.stat().st_size,'members':len(z.infolist()),
             'new_external_path_already_archived':name in z.namelist(),'archive_was_only_read':True}
    scripts=['replay.py','freeze_manifest.py','package.py','build_claim.py','collect_release.py',
             'composed-supplier/run_release.py','composed-supplier/invoice.py','composed-supplier/construct.py',
             'sources/PR3945/research/staged544-terminal-gap-fill/native/run_native.py']
    pins={str((SCOPE/name).relative_to(REPO)):sha(SCOPE/name) for name in scripts}
    pins[str(Path(__file__).relative_to(REPO))]=sha(Path(__file__))
    result={'status':'PASS_SCOPED_INDEPENDENT_PRIMARY_PACKAGING_REVIEW','reviewed_files':pins,
            'dependency_coverage':dependencies,'native_receipt_runtime_field_audit':inspected,
            'focused_comparator_controls':controls,'accepted_comparator_record':comparison,'previous_archive':old,
            'corrected_concrete_defect':'Optional native/full replay formerly byte-compared top-level CLIFFORD-REVIEW.seconds. The reviewed source omits only that validated runtime field; all other scientific JSON fields and the other five complete files remain exact.',
            'remaining_acceptance_defects_found':[],
            'manual_review':[
                'Replay authenticates the selected manifest before subprocess execution; every default stage writes to a fresh requested output path.',
                'Freshly reconstructed words are byte-compared before pricing. The cached native/full receipts used by the default mode are source-bound by the fresh conjunction, and fresh-native/full flags distinguish the optional executions.',
                'Native replay creates a fresh vendor/input snapshot; full release alters only its explicitly fresh scoped work tree and repeatedly checks scientific source stability.',
                'Manifest freezing authenticates the prior portable closure, refuses unfinished report markers and incomplete claim status, and includes all four audited dependency inventories with the explicit new PR3220 proof.',
                'Package preserves the original archive as input, copies it to the new filename, appends only new members, checks old metadata and the entire old compressed-member prefix, and verifies each new member byte. It requires a validation tied to the final manifest before complete delivery.',
                'Compact --stage proves archive source-byte/CRC integrity and labels itself staging; it does not claim a completed scientific replay.',
            ],
            'limitations':['No full native replay, full inherited release, or final package was executed by this review.',
                           'The late PR4076 composition and any new selector/collector are outside this primary-script review.',
                           'The manifest and actual final portable replay remain to be produced after release completion; historical files may contain withdrawn claims and are authenticated as history.']}
    (HERE/'PRIMARY-REVIEW.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],len(inputs),'distinct audited inputs',len(controls),'comparator controls',flush=True)


if __name__=='__main__':main()
