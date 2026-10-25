"""Portable explicit-guard owner/operator verification, meaningful under-O."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,json,gzip,hashlib,time
H=Path(__file__).resolve().parent
def need(value,why):
    if not value:raise ValueError(why)
def module(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def canonical_sha(obj):
    h=hashlib.sha256()
    for chunk in json.JSONEncoder(sort_keys=True,separators=(',',':'),default=str).iterencode(obj):h.update(chunk.encode())
    return h.hexdigest()
def file_sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_terminal_bases(owner,geom,bases,source):
    expected={1:owner.eye(8)}
    expected.update({c['terminal_frame']:owner.transpose([[Q(x)for x in col]for col in c['Q_columns']])for c in source['charts']})
    need(set(bases)==set(expected),'complete terminal chart vocabulary')
    for f,b in bases.items():
        need(b==expected[f],'terminal chart source binding')
        need(owner.matmul(owner.transpose(b),b)==owner.eye(8),'terminal chart orthogonality')
        p,k=owner.projector([geom['lines'][i]for i in geom['frames'][f]])
        diag=[[Q(i==j and i<k)for j in range(8)]for i in range(8)]
        need(owner.matmul(owner.matmul(b,diag),owner.transpose(b))==p,'actual terminal projector')
def validate_relative_support(c,bases,dims):
    matrix=[[Q(x)for x in r]for r in c['relative_matrix']];b=bases[c['terminal_frame']];k=dims[c['terminal_frame']]
    need(len(c['axes'])==k,'terminal axis count')
    for j in range(k):
        column=[sum(matrix[i][a]*b[a][j]for a in range(8))for i in range(64)]
        need(column==[Q(i==c['axes'][j])for i in range(64)],'exact terminal operator support')
def validate_idle_return(factors,slots,children):
    used={}
    for child,cp,off,width,stage,helper in slots:
        axes=children[child]['axes'][off:off+width]
        need(len(axes)==width,'owner axis extent')
        key=(child,cp);before=used.setdefault(key,set())
        need(not before.intersection(axes),'owner axis overlap');before.update(axes)
    got={}
    for child,cp,axes in factors:
        need((child,cp)not in got,'duplicate idle factor');got[child,cp]=axes
    need(len(got)==len(children)*222,'complete idle factors')
    for child in children:
        for cp in range(222):
            expected=[a for a in child['axes']if a not in used.get((child['idx'],cp),set())]
            need(got.get((child['idx'],cp))==expected,'complete idle return')
def prepare():
    owner=module('new_owner_replay',H/'owner.py');nom=module('new_owner_nomination',H/'nomination.py')
    raw=owner.authenticated_inputs()
    for name,pin in owner._EXPECTED_ARTIFACTS.items():
        need(file_sha(H/'new-owners'/(name+'.json.gz'))==pin,'authenticated new owner artifact')
    w=json.loads(gzip.decompress(raw['WORD.json.gz']));geom=json.loads(gzip.decompress(raw['GEOMETRY.json.gz']))
    summary=json.loads((H/'OWNERS.json').read_bytes());charts=json.loads(gzip.decompress((H/'new-owners/CHARTS.json.gz').read_bytes()))
    frames=w['final'][222:];bases={int(f):[[Q(x)for x in r]for r in b]for f,b in charts['terminal_bases'].items()}
    source=json.loads(raw['TERMINAL-CHARTS.json']);validate_terminal_bases(owner,geom,bases,source)
    dims={f:owner.projector([geom['lines'][i]for i in geom['frames'][f]])[1]for f in bases};widths=[dims[f]for f in frames]
    events,children,calls,windows=owner.chronology();slots=nom.nominate(widths,windows)
    need(canonical_sha(slots)==hashlib.sha256(gzip.decompress((H/'new-owners/SLOTS.json.gz').read_bytes())).hexdigest(),'fresh nomination binding')
    return dict(owner=owner,raw=raw,w=w,geom=geom,summary=summary,charts=charts,frames=frames,bases=bases,
        terminal_source=source,dims=dims,widths=widths,children=children,calls=calls,windows=windows,slots=slots)
def verify(return_context=False):
    st=time.process_time();c=prepare();owner=c['owner']
    r=owner.audit(c['slots'],c['children'],c['windows'],c['widths'],c['frames'],c['bases'])
    owner.audit_emitted(r['fill'],r['dispatch'],c['slots'],c['children'],c['calls'],r['charts'])
    hashes={}
    for key,field in[('DISPATCH','dispatch'),('REMAINDERS','factors')]:
        expected=hashlib.sha256(gzip.decompress((H/'new-owners'/(key+'.json.gz')).read_bytes())).hexdigest()
        hashes[key]=canonical_sha(r[field]);need(hashes[key]==expected,'fresh emitted '+key)
    need(r['charts']==c['charts']['relative_charts'],'fresh relative chart binding')
    need({str(k):n for k,n in r['remainders'].items()}==c['summary']['idle_per_replica_including_zero'],'all idle counts')
    validate_idle_return(r['factors'],c['slots'],c['children'])
    for chart in r['charts']:validate_relative_support(chart,c['bases'],c['dims'])
    report=dict(status='PASS_PORTABLE_FRESH_INTEGER_OWNER_AND_EXACT_TERMINAL_OPERATORS',
        optimized=not __debug__,files={n:file_sha(H/n)for n in['nomination.py','owner.py','upstream-owner.py','inputs/WORD.json.gz','inputs/GEOMETRY.json.gz']},
        full_helper_occurrences=len(r['fill']),calls=len(r['dispatch']),stage_eligible=True,replicas=32,
        all_source_windows_compact_and_disjoint=True,fresh_artifact_hashes=hashes,
        exact_terminal_operator_supports=len(r['charts']),family_factor_retained=True,
        old_WORD_unchanged=True,CPU=time.process_time()-st,production_memory_claim=False)
    return(report,c,r)if return_context else report
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True,indent=2))
