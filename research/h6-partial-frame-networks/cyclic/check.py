#!/usr/bin/env python3
"""Portable exact replay of the retained C03 cyclic modules.

Substantial OpenAI Codex assistance. Logical frame contracts only; no new kappa.
All runtime source buffers are authenticated before compilation with optimize=0.
"""
import argparse
from collections import Counter
from contextlib import redirect_stdout
import copy
from fractions import Fraction as F
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import types

ORIGINS_SHA = 'e31a8c9f7372d5b3c97bad95a02492ee00f8ebf3e694019ea51bc2c7e7c27617'
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'


class CheckFailure(ValueError):
    pass


def require(ok, guard):
    if not ok:
        raise CheckFailure(guard)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replace_once(text, before, after):
    require(text.count(before) == 1, 'unique source adaptation')
    return text.replace(before, after, 1)


def authenticated_modules(source_dir, origins_path, output_dir):
    manifest_raw = origins_path.read_bytes()
    require(sha(manifest_raw) == ORIGINS_SHA, 'source manifest SHA256')
    origins = json.loads(manifest_raw)
    captured = {}
    for row in origins['files']:
        name = row['path']
        require(Path(name).name == name, 'flat source path')
        transport = (source_dir / row.get('transport_path',name)).read_bytes()
        if row.get('transport') == 'gzip':
            require(len(transport)==row['transport_bytes'] and sha(transport)==row['transport_sha256'],
                    'authenticated compressed source bytes: '+name)
            raw=gzip.decompress(transport)
        else:
            raw=transport
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'],
                'authenticated source bytes: ' + name)
        captured[name] = raw
    modules, adaptations = {}, []

    def execute(name, source=None):
        raw = captured[name]
        adapted = raw.decode() if source is None else source
        module = types.ModuleType('authenticated_c03_' + name.replace('.', '_'))
        module.__dict__.update(__file__='/authenticated/c03/frozen/source/' + name,
                               _modules=modules, _captured=captured)
        exec(compile(adapted, 'authenticated:' + name, 'exec',
                     dont_inherit=True, optimize=0), module.__dict__)
        module.HERE = output_dir
        modules[name] = module
        adaptations.append({'file': name, 'original_sha256': sha(raw),
                            'executed_source_sha256': sha(adapted.encode()),
                            'changed': adapted.encode() != raw, 'optimize': 0})
        return module

    execute('invoice.py')  # Only exact model/log/power functions are called.
    source = captured['mixed_rectangle.py'].decode()
    source = replace_once(source,
        "source = Path('/Users/ross/git/math/integer-mult-bounds/research/niemeier-lattices/code/e8_cubed.py')",
        "source = Path('frozen/e8_cubed.py')")
    source = replace_once(source, 'hashlib.sha256(source.read_bytes()).hexdigest()',
        "hashlib.sha256(_captured['e8_cubed.py']).hexdigest()")
    source = replace_once(source, "'orientation':'dual' if dual else 'forward','paths':paths,",
        "'orientation':'dual' if dual else 'forward','paths':paths,\n"
        "            'ordinary_columns':cols,\n"
        "            'ordinary_operator_rows':[[str(v) for v in rows[r]] for r in cols],")
    m = execute('mixed_rectangle.py', source)
    m.need = require

    source = captured['optimistic_budget.py'].decode()
    begin = source.index("REPO = Path(")
    end = source.index('\n\ndef dec(', begin)
    source = source[:begin] + '''PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
N,H,KC,KBILL = 30960,17,816,13872
ORACLE = 'research/h6-independent-audit/invoice/verify.py'
oracle = _modules['invoice.py']
need = oracle.require
SOURCE_HASHES = {ORACLE:hashlib.sha256(_captured['invoice.py']).hexdigest()}
for short, rel in [('K-RESULT.json','research/h6-compensation-network/k_encoder/RESULT.json'),
                   ('pricing.py','research/h6-compensation-network/pricing/verify.py')]:
    content = _captured[short]
    SOURCE_HASHES[rel] = hashlib.sha256(content).hexdigest()
    if rel.endswith('RESULT.json'):
        kr = json.loads(content)
        need(kr['K_ordinary_roles'] == KC and kr['private_descent_C'] == KBILL,
             'actual full K inventory')
''' + source[end:]
    execute('optimistic_budget.py', source)

    source = captured['cyclic_mixed.py'].decode()
    begin = source.index("spec = importlib.util.spec_from_file_location")
    end = source.index('\nneed = m.need', begin)
    source = source[:begin] + "m = _modules['mixed_rectangle.py']" + source[end:]
    source = replace_once(source, "hashlib.sha256((HERE/'mixed_rectangle.py').read_bytes()).hexdigest()",
                          "hashlib.sha256(_captured['mixed_rectangle.py']).hexdigest()")
    c = execute('cyclic_mixed.py', source)

    for name, following in [('dynamic_cyclic.py', "\nc = load("),
                            ('module_tiling.py', "\nd = load(")]:
        source = captured[name].decode()
        begin = source.index('\ndef load(')
        end = source.index(following, begin)
        source = source[:begin] + '\ndef load(name, file):\n    return _modules[file]\n\n' + source[end:]
        if name == 'module_tiling.py':
            source = replace_once(source,
                "raw = subprocess.check_output(['git','show',b.PIN+':'+path],cwd=b.REPO)",
                "raw = _captured['WALSH-RESULTS.json']")
        execute(name, source)
    return modules, captured, adaptations


def expected_bill(kind, r, dual):
    if kind == 'rectangle':
        return 312 if dual else 300
    n = 2*r
    return n*((54*r+2 if dual else 54*r-1) if kind == 'dynamic'
              else (72*r-34 if dual else 72*r-37))


def accept_bill(result, kind, r, dual, enabled=True):
    if enabled:
        require(result['scalar_primitives_before_real_doubling'] ==
                expected_bill(kind, r, dual), 'complete scalar invoice')


def expect_rejection(call, guard):
    try:
        call()
    except CheckFailure as error:
        require(str(error) == guard, 'intended rejection guard')
        return {'guard': guard, 'rejected': True}
    raise CheckFailure('expected rejection missing')


def deletion_control(module, call, guard):
    original = module.need
    module.need = lambda ok, label: None if label == guard else original(ok, label)
    try:
        try:
            expect_rejection(call, guard)
        except CheckFailure as error:
            require(str(error) == 'expected rejection missing', 'check deletion removes detection')
            return {'deleted_guard': guard, 'expected_rejection_oracle_failed': True}
        raise CheckFailure('check deletion unexpectedly retained rejection')
    finally:
        module.need = original


def operator_difference(result, dual):
    columns = result['ordinary_columns']
    for i, (register, row) in enumerate(zip(columns, result['ordinary_operator_rows'])):
        for j, value in enumerate(row):
            expected = F(i == j)
            if ((not dual and register.startswith('y')) or
                    (dual and register.startswith('x'))):
                if columns[j] == ('y' if dual else 'x') + register[1:]:
                    expected += -1 if dual else 1
            if F(value) != expected:
                return {'output': register, 'input': columns[j],
                        'actual': value, 'expected': str(expected)}
    return None


def strengthen_controls(modules, reports):
    m = modules['mixed_rectangle.py']
    controls = []
    cases = [('rectangle', None, reports['MIXED-RECTANGLE-RESULT.json']['fixtures'])]
    for kind, file in [('static', 'CYCLIC-MIXED-RESULT.json'),
                       ('dynamic', 'DYNAMIC-CYCLIC-RESULT.json')]:
        cases.extend((kind, case['r'], case['fixture']) for case in reports[file]['cases'])
    frame_tags = {'source_plane', 'target_plane', 'helper_arc', 'target_arc',
                  'source_read_arc', 'mutable_reader_arc', 'target_final_arc'}
    for kind, r, fixture in cases:
        tags = (('comp_prefix','comp_gather','comp_scatter','comp_restore','K_prefix',
                 'K_gather','K_private','K_restore','source_plane','target_plane')
                if kind == 'rectangle' else
                ('comp_prefix','comp_gather','comp_scatter','comp_restore','K_prefix',
                 'K_private','helper_arc','target_arc') if kind == 'static' else
                ('mutable_read','comp_prefix','comp_scatter','comp_restore','K_private',
                 'source_read_arc','mutable_reader_arc','target_final_arc'))
        for tag in tags:
            if kind == 'static' and r == 2 and tag == 'helper_arc':
                for dual in (False, True):
                    baseline = m.replay(fixture, dual)
                    redundant = m.replay(fixture, dual, tag)
                    require(redundant == baseline, 'redundant rank-zero frame marker')
                continue
            guard = 'equal current frames' if tag in frame_tags else 'all-column exact identity with arbitrary dirt'
            for dual in (False, True):
                result = expect_rejection(lambda f=fixture,d=dual,t=tag: m.replay(f,d,t), guard)
                controls.append(dict(kind=kind,r=r,dual=dual,omit=tag,**result))
        if kind == 'rectangle':
            bad=copy.deepcopy(fixture)
            event=next(e for e in bad['events'] if e['tag']=='mixed_restore_full' and e['register']=='h0')
            event['frame']=fixture['planes'][1]
            rejected=expect_rejection(lambda:m.replay(bad),'monotone canonical frame')
            controls.append(dict(kind=kind,r=r,dual=False,mutation='unpaid_plane_reuse',**rejected))
        # Endpoint and frame check deletions exercise the actual replay predicates.
        for dual in (False, True):
            for tag, guard in [('comp_restore','all-column exact identity with arbitrary dirt'),
                               ('source_read_arc' if kind == 'dynamic' else 'source_plane',
                                'equal current frames')]:
                call = lambda f=fixture,d=dual,t=tag: m.replay(f,d,t)
                deleted = deletion_control(m, call, guard)
                if tag == 'comp_restore':
                    saved = m.need
                    m.need = lambda ok,label: None if label == guard else saved(ok,label)
                    try:
                        witness = operator_difference(call(),dual)
                    finally:
                        m.need = saved
                    require(witness is not None, 'actual coefficient discrepancy')
                    deleted['coefficient_witness'] = witness
                controls.append(dict(kind=kind,r=r,dual=dual,omit=tag,**deleted))
            bad = copy.deepcopy(fixture)
            first = next(e for e in bad['events'] if e['op'] == 'add')
            plus = dict(first, q='1', tag='control_paid_pair')
            minus = dict(first, q='-1', tag='control_paid_pair')
            bad['events'][:0] = [plus, minus]
            result = m.replay(bad,dual)
            require(operator_difference(result,dual) is None, 'paid pair retains endpoint')
            require(result['scalar_primitives_before_real_doubling'] == expected_bill(kind,r,dual)+8,
                    'two paid unit Horner adds')
            rejected = expect_rejection(lambda: accept_bill(result,kind,r,dual), 'complete scalar invoice')
            try:
                expect_rejection(lambda: accept_bill(result,kind,r,dual,False), 'complete scalar invoice')
            except CheckFailure as error:
                require(str(error) == 'expected rejection missing', 'invoice deletion removes detection')
            else:
                raise CheckFailure('invoice deletion oracle did not fail')
            controls.append(dict(kind=kind,r=r,dual=dual,mutation='paid_cancelling_pair',
                                 endpoint_accepted=True,added_component_primitives=8,
                                 check_deletion_detected=True,**rejected))
    return controls


def accept_partition(ids, enabled=True):
    if enabled:
        require(sorted(ids) == list(range(2160,30960)), 'emitted exact partition')


def accept_module_coefficients(m, roots, record, enabled=True):
    ports = []
    for index in record['source_ids']:
        a, remainder = divmod(index-2160,240)
        b, negative = divmod(remainder,2)
        ports.append(roots[a]+tuple((-1 if negative else 1)*v for v in roots[b]))
    witness = None
    for i in range(6):
        for j in range(6):
            t = m.dot(ports[i],ports[j])
            actual = F(i == j)-F(t**3-4*t,48)
            expected = F(0) if i//2==j//2 else F(record['signs'][i]*record['signs'][j]*(-5 if i%2==j%2 else 1),16)
            if actual != expected and witness is None:
                witness = {'target':i,'source':j,'gram':t,'actual':str(actual),'expected':str(expected)}
    if enabled:
        require(witness is None, 'emitted module coefficient identity')
    return witness


def complete_tiling(modules):
    t, m = modules['module_tiling.py'], modules['mixed_rectangle.py']
    roots, pairs, signs, _, _ = t.tiling()
    packed = t.packed_root_pairs(roots)
    frames, modules_out = [], []
    for ti, aa in enumerate(t.TRIPLES):
        for bi, bb in enumerate(pairs):
            labels = [packed[a][bj] for a in aa for bj in bb]
            planes = [m.basis(labels[2*g:2*g+2]) for g in range(3)]
            arcs = [m.basis(planes[g]+planes[(g+1)%3]) for g in range(3)]
            frames.append({'triple_index':ti,'b_pair_index':bi,'labels':labels,
                           'planes':[list(x) for x in planes],
                           'final_arcs':[list(x) for x in arcs]})
            for epsilon in (-1,1):
                ids = [2160+240*a+2*bj+int(epsilon*signs[ti][g]<0)
                       for g,a in enumerate(aa) for bj in bb]
                modules_out.append({'triple_index':ti,'b_pair_index':bi,'epsilon':epsilon,
                                    'source_ids':ids,'signs':[s for s in signs[ti] for _ in range(2)]})
    require(len(frames)==2400 and len(modules_out)==4800, 'complete tiling emission')
    ids = [i for x in modules_out for i in x['source_ids']]
    accept_partition(ids)
    for record in modules_out:
        accept_module_coefficients(m,roots,record)
    controls=[]
    bad_ids=list(ids);bad_ids[0]=bad_ids[1]
    bad_record=copy.deepcopy(modules_out[0]);bad_record['signs'][0]*=-1
    for name,gate,call,deleted in [
        ('duplicate_port','emitted exact partition',lambda:accept_partition(bad_ids),lambda:accept_partition(bad_ids,False)),
        ('wrong_module_sign','emitted module coefficient identity',lambda:accept_module_coefficients(m,roots,bad_record),lambda:accept_module_coefficients(m,roots,bad_record,False))]:
        result=expect_rejection(call,gate)
        try:
            expect_rejection(deleted,gate)
        except CheckFailure as error:
            require(str(error)=='expected rejection missing','tiling check deletion removes detection')
        else:
            raise CheckFailure('tiling deletion oracle did not fail')
        controls.append(dict(mutation=name,check_deletion_detected=True,**result))
    controls[1]['coefficient_witness']=accept_module_coefficients(m,roots,bad_record,False)
    return {'frame_cases':frames,'modules':modules_out,'production_controls':controls,
            'a_triples':[list(x) for x in t.TRIPLES],'b_pairs':[list(x) for x in pairs],
            'triple_gauge_signs':signs,
            'untiled_pure_ids':list(range(2160)),
            'sign_convention':'Each complete local logical word is conjugated by diag(sigma) on x,y,c,h; epsilon changes physical port IDs but not this conjugation.'}



def compare_cyclic_words(modules, reports):
    oracle=modules['invoice.py']
    records=[]
    static=reports['CYCLIC-MIXED-RESULT.json']['cases']
    dynamic=reports['DYNAMIC-CYCLIC-RESULT.json']['cases']
    for old,new in zip(static,dynamic):
        r,n=old['r'],old['N']
        require(r==new['r'] and n==new['N'],'matching cyclic comparison')
        difference=Counter({int(k):v for k,v in new['forward']['profile'].items()})
        difference.subtract({int(k):v for k,v in old['forward']['profile'].items()})
        expected=Counter()
        for rank,sign in [(17-r,1),(r,1),(15,-1),(2,-1)]:
            expected[rank]+=sign*n
        require(dict(+difference)==dict(+expected) and dict(-difference)==dict(-expected),
                'complete abstract rank histogram comparison')
        require(sum(k*v for k,v in difference.items())==0,'equal comparison rank mass')
        saving=18*n*(r-2)
        for orientation in ['forward','dual']:
            require(old[orientation]['scalar_primitives_before_real_doubling']-
                    new[orientation]['scalar_primitives_before_real_doubling']==saving,
                    'exact scalar saving comparison')
        lo=hi=F(0)
        b=F(1,500)+F(1,10**24)
        for rank,count in difference.items():
            if count:
                a,z=oracle.power_interval(F(81,rank),b)
                if count>0:
                    lo+=rank*count*(a-1);hi+=rank*count*(z-1)
                else:
                    lo+=rank*count*(z-1);hi+=rank*count*(a-1)
        require((lo==hi==0) if r==2 else lo>0,'dynamic abstract pressure tradeoff')
        records.append({'r':r,'N':n,'component_primitive_saving_each_orientation':saving,
                        'dynamic_minus_static_abstract_rank_histogram':{k:v for k,v in sorted(difference.items()) if v},
                        'pressure_witness_arity':81,'pressure_witness_exponent':str(b),
                        'dynamic_minus_static_pressure_interval':[str(lo),str(hi)],
                        'decision':'identical tariffs at r2' if r==2 else 'mutable saves scalar work but increases abstract rank pressure at the same stock'})
    return {'cases':records,'all_parameter_scope':'For0<b<1 and common positive arity m, strict concavity of t^(1-b) makes the dynamic-minus-static pressure positive for r3..7, zero at r2; both use the same stock/ordinary roles/private contract. This is not a complete supplier cost ordering.'}



def historical_projection(reports, captured):
    def strip(value):
        if isinstance(value,list):
            return [strip(x) for x in value]
        if isinstance(value,dict):
            return {k:strip(v) for k,v in value.items()
                    if k not in ('ordinary_columns','ordinary_operator_rows')}
        return value
    records=[]
    for name,report in sorted(reports.items()):
        old=json.loads(captured[name])
        current=strip(report)
        if name=='MIXED-RECTANGLE-RESULT.json':
            require(old['actual_geometry_source']=='/Users/ross/git/math/integer-mult-bounds/research/niemeier-lattices/code/e8_cubed.py',
                    'exact old provenance path')
            require(current['actual_geometry_source']=='frozen/e8_cubed.py','exact portable provenance path')
            old['actual_geometry_source']='frozen/e8_cubed.py'
        canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':')).encode()
        require(canonical(old)==canonical(current),'complete typed historical projection: '+name)
        records.append({'file':name,'complete_typed_projection_equal':True,
                        'historical_raw_sha256':sha(captured[name]),
                        'projected_canonical_sha256':sha(canonical(current))})
    return records


def audit(source_dir, origins_path):
    with tempfile.TemporaryDirectory(prefix='c03-exact-') as temporary:
        output_dir = Path(temporary)
        modules,captured,adaptations = authenticated_modules(source_dir,origins_path,output_dir)
        inherited_K=json.loads(captured['K-RESULT.json'])
        require(inherited_K['N']==30960 and inherited_K['h']==17 and
                inherited_K['K_forward_primitive_bound']==247217040 and
                inherited_K['K_dual_primitive_bound']==247219488,
                'inherited full K scalar invoice constants')
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            for name in ['mixed_rectangle.py','cyclic_mixed.py','dynamic_cyclic.py',
                         'optimistic_budget.py','module_tiling.py']:
                modules[name].main()
        names = ['MIXED-RECTANGLE-RESULT.json','CYCLIC-MIXED-RESULT.json',
                 'DYNAMIC-CYCLIC-RESULT.json','OPTIMISTIC-BUDGET-RESULT.json',
                 'MODULE-TILING-RESULT.json']
        reports = {name:json.loads((output_dir/name).read_bytes()) for name in names}
        # Cost gates are shared with the sensitivity controls below.
        for kind,file in [('static','CYCLIC-MIXED-RESULT.json'),('dynamic','DYNAMIC-CYCLIC-RESULT.json')]:
            for case in reports[file]['cases']:
                for dual,key in [(False,'forward'),(True,'dual')]:
                    accept_bill(case[key],kind,case['r'],dual)
        for dual,result in enumerate(reports['MIXED-RECTANGLE-RESULT.json']['orientations']):
            accept_bill(result,'rectangle',None,bool(dual))
        historical = historical_projection(reports,captured)
        controls = strengthen_controls(modules,reports)
        tiling = complete_tiling(modules)
        comparison = compare_cyclic_words(modules,reports)
        return {'schema':'c03_cyclic_replay.v1','status':'PASS_C03_CYCLIC_LOGICAL_FRAMES_NO_NEW_KAPPA',
                'scientific_pin':PIN,'no_new_kappa':True,
                'checker_sha256':sha(Path(__file__).read_bytes()),
                'origins_sha256':ORIGINS_SHA,'authenticated_source_sha256':{k:sha(v) for k,v in sorted(captured.items())},
                'source_adaptations':adaptations,'reports':reports,
                'historical_complete_typed_projection':historical,
                'inherited_K_invoice':{k:inherited_K[k] for k in ['N','h','K_ordinary_roles','private_descent_C','K_forward_primitive_bound','K_dual_primitive_bound','full_factor_certificate']},
                'complete_tiling':tiling,'production_controls':controls,
                'static_mutable_comparison':comparison,
                'historical_stdout':stdout.getvalue().splitlines(),
                'restoration_contract':'All ordinary logical coefficients restored at the declared final frames; h and c move ZERO to FULL. No raw entrance-frame restoration is asserted.',
                'coverage':'All retained main assertions rerun. Invoice oracle only its invoked pure functions, not its unrelated standalone main. Complete 17-bit finite frame and rational ordinary-column replays; full phase/native lowering excluded.',
                'limits':['Private CLEAR/COPY episodes use the inherited private-stream contract, not arbitrary private initial columns.',
                          'Coefficient Horner costs are counted; coefficient temporary states and rounded precision are not replayed.',
                          'Tiling covers only root-product ports. Full residual stream is specified/counted, not materialized.',
                          'Walsh all-pairs support and full K factor are inherited pinned receipts, not freshly exhaustive here.',
                          'No physical bank, ownership, tape, all-size or multiplication theorem.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path,default=Path(__file__).resolve().parent/'frozen')
    parser.add_argument('--origins',type=Path,default=Path(__file__).resolve().parent/'ORIGINS.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    require(args.output.is_absolute(), 'absolute output required')
    require(not args.output.exists(), 'output already exists')
    require(Path(__file__).resolve().parent not in args.output.resolve().parents, 'output outside package')
    result=audit(args.source_dir,args.origins)
    raw=(json.dumps(result,indent=2,sort_keys=True)+'\n').encode()
    if args.output.suffix=='.gz':
        raw=gzip.compress(raw,mtime=0)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as handle:
        handle.write(raw)
    print(result['status']+' cyclic_cases=12 modules=4800 controls='+str(len(result['production_controls'])))


if __name__=='__main__':
    main()
