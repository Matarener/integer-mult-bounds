#!/usr/bin/env python3
"""Independent PR3391 ordered-key review. stdlib only; never expands GL64.

Adapted from the verified Astra census worker; substantial OpenAI Codex
assistance. Apache-2.0. Source credit: Jose Manuel (jmbarrancoml), David Arias,
ywz65, Nick Petalas and the retained source/NOTICE contributors. The archived
PR3391 visitation audit by Kewin Talaga and its independent reviewers retain
their attribution.

--source is for the parent's SERIAL bounded run, not the worker's self-test.
No audit accounting/source_audit/verify/extract_census modules are imported.
Source execution is restricted to predecessor authentication, q=3 metadata,
LocalState, and original compile_node on an explicitly synthetic GL2 fixture.
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha1, sha256
import gzip
import importlib
import importlib.abc
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
import time
import types

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[1]
AUDIT = 'research/selected-compiler-visitation-audit'
CALLER = 'research/selected-bit-physical-caller'
HOST = 'research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz'
CLAIM_SIZES = [2920,2920,222,2920,222,2920,222,2920,222,2920,222,2920,222,2920,2920,222,222,222,0]

class Rejected(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise Rejected(message)

def integer(x):
    return type(x) is int

def digest_ids(ids):
    return sha256(json.dumps(list(ids), separators=(',', ':')).encode()).hexdigest()

@dataclass(frozen=True)
class Group:
    schedule_index: int
    kind: str
    ids: tuple

    @property
    def common(self):
        return self.kind == 'local_cover_sweep'


def partition(groups, request_count):
    require(integer(request_count) and request_count >= 0, 'request_count integer')
    require(all(g.kind in ('local_cover_sweep','idle') for g in groups), 'closed group kinds')
    positions = [g.schedule_index for g in groups]
    require(all(integer(p) and p >= 0 for p in positions), 'schedule index integer')
    require(positions == sorted(set(positions)), 'strict chronological group positions')
    ids = [i for g in groups for i in g.ids]
    require(all(integer(i) and 0 <= i < request_count for i in ids), 'request id range/type')
    require(len(ids) == len(set(ids)), 'duplicate request within/across groups')
    require(set(ids) == set(range(request_count)), 'request coverage gap')


def visit_at(groups, replicas, lows, ordinal):
    """Mixed-radix decoder, independent of emitter's nested loops.

    Return (group-index, replica-index, request-id, common-view, LOW-token).
    LOW tokens are only supplied finite symbols; not GL64 elements.
    """
    require(integer(replicas) and replicas > 0, 'positive replica count')
    require(len(lows) > 0 and len(set(lows)) == len(lows), 'nonempty unique LOW symbols')
    require(integer(ordinal) and ordinal >= 0, 'ordinal range')
    for j,g in enumerate(groups):
        block = len(g.ids)*len(lows)
        extent = replicas*block
        if ordinal >= extent:
            ordinal -= extent
            continue
        replica, inner = divmod(ordinal, block)
        if g.common:
            low_index, id_index = divmod(inner, len(g.ids))
        else:
            id_index, low_index = divmod(inner, len(lows))
        return j,replica,g.ids[id_index],g.common,lows[low_index]
    raise Rejected('ordinal past end')


def projected_word(groups, replicas, lows):
    total = replicas*len(lows)*sum(len(g.ids) for g in groups)
    return [visit_at(groups, replicas, lows, i) for i in range(total)]


def check_word(groups, replicas, lows, observed):
    expected = projected_word(groups, replicas, lows)
    require(len(observed) == len(expected), 'visit length mismatch')
    for index,(a,b) in enumerate(zip(observed, expected)):
        # Python bool/int equality must not erase view/type distinctions.
        require(type(a[3]) is bool and a == b,
                f'ordered visit mismatch at {index}: observed {a!r}, expected {b!r}')
    by_key = Counter((r,c,l) for _,_,r,c,l in observed)
    require(len(by_key) == sum(len(g.ids) for g in groups)*len(lows), 'distinct key census')
    require(set(by_key.values()) == {replicas}, 'per-key replica multiplicity')
    return {'visits':len(observed), 'distinct_keys':len(by_key), 'multiplicity':replicas}


def interval_data(data, actual=None):
    """DATA-only check unless independently derived actual groups are supplied."""
    require(integer(data['request_count']) and integer(data['replica_count']), 'certificate integer types')
    require(data['replica_count'] > 0, 'certificate positive replicas')
    groups=[]
    for j,row in enumerate(data['groups']):
        for k in ('index','schedule_index','start','count'):
            require(integer(row[k]), 'interval integer '+k)
        require(row['index']==j and row['start'] >= 0 and row['count'] >= 0, 'interval index/range')
        local = row['kind']=='local_cover_sweep'
        require(row['kind'] in ('local_cover_sweep','idle'), 'interval kind')
        require(type(row['common']) is bool and row['common'] is local, 'interval view')
        require(type(row['low_major']) is bool and row['low_major'] is local, 'interval nesting')
        require(row['order']==('low-major' if local else 'id-major'), 'interval order label')
        ids=tuple(range(row['start'],row['start']+row['count']))
        require(row['sequence_sha256']==digest_ids(ids), 'interval sequence digest')
        if not ids:
            require(row['start']==data['request_count'], 'canonical empty start')
        groups.append(Group(row['schedule_index'],row['kind'],ids))
    partition(groups,data['request_count'])
    require(sum(not g.ids for g in groups)==data['empty_groups'], 'empty group count')
    require(data['empty_canonical_start']==data['request_count'], 'empty sentinel')
    if actual is not None:
        require(groups==actual, 'certificate differs from independent source-data groups')
    return groups


def raw_groups(template):
    """Reconstruct request numbering from hosted data, without Catalogue.

    Local requests follow stage then literal op0/op2 positions. Idle requests
    follow schedule idle order then copy number, excluding fully hosted axes.
    This does not reconstruct projectors or prove mathematical admissibility.
    """
    rho=template['replicas']
    require(integer(rho) and rho>0,'raw replica count')
    calls=template['calls']; programs=template['local_programs']; schedule=template['schedule']
    require(len(calls)==template['stages']*rho,'complete raw calls')
    requests=[]; local_ids={}; local_events={}; local_maps={}
    for stage in range(template['stages']):
        first=calls[stage*rho]
        require(first['stage']==stage and first['replica']==0,'stage-major raw calls')
        events=tuple(map(tuple,programs[first['orientation']]))
        ids=[]; mapping=[]
        for pos,event in enumerate(events):
            op,role=event[:2]
            require(op in (0,1,2,3),'closed raw local opcode')
            if op not in (0,2):
                mapping.append(None); continue
            identifier=len(requests); mapping.append(identifier); ids.append(identifier)
            requests.append({'kind':('MOVE' if op==0 else 'COPY'),'stage':stage,'position':pos,'role':role})
        local_ids[stage]=tuple(ids); local_maps[stage]=tuple(mapping); local_events[stage]=events
        for replica in range(rho):
            other=calls[stage*rho+replica]
            require((other['stage'],other['replica'],other['orientation'],other['local_hash']) ==
                    (stage,replica,first['orientation'],first['local_hash']), 'raw replica recipe agreement')
    idle_events=[e for e in schedule if e['kind']=='idle']
    require(len({e['idx'] for e in idle_events})==len(idle_events),'unique idle schedule ids')
    pending={}
    for e in idle_events:
        a,b=e['source_level'],e['target_level']
        axes=tuple(range(1 if a==-1 else 8+7*a,8+7*b))
        require(len(axes)==e['rank'],'raw idle rank/axis interval')
        pending[e['idx']]=axes
    used=defaultdict(set)
    for child,copy,offset,width,_stage,_helper in template['hosting']['slots']:
        require(child in pending and 0<=copy<222 and offset>=0 and width>=0,'hosting slot domain')
        axes=pending[child][offset:offset+width]
        require(len(axes)==width and not used[child,copy].intersection(axes),'hosting gap/overlap')
        used[child,copy].update(axes)
    idle_ids={}
    for e in idle_events:
        ids=[]
        for copy in range(222):
            remaining=set(pending[e['idx']])-used[e['idx'],copy]
            if not remaining: continue
            ids.append(len(requests))
            requests.append({'kind':'IDLE','stage':e['idx'],'position':e['idx'],'role':copy,
                             'family':e['pair']*222+copy,'axes':tuple(sorted(remaining))})
        idle_ids[e['idx']]=tuple(ids)
    groups=[]
    for pos,e in enumerate(schedule):
        if e['kind']=='local_cover_sweep': groups.append(Group(pos,e['kind'],local_ids[e['stage']]))
        elif e['kind']=='idle': groups.append(Group(pos,e['kind'],idle_ids[e['idx']]))
        else: require(e['kind'] in ('bridge','exchange'),'closed raw global opcode')
    partition(groups,len(requests))
    return groups,requests,local_events,local_maps,idle_ids


def check_claims(groups,requests,rho):
    kinds=dict(Counter(r['kind'] for r in requests))
    require(len(requests)==28278,'challenge R=28278')
    require(rho==32,'challenge rho=32')
    require(len(groups)==19 and not groups[-1].ids,'challenge 19 groups, empty final')
    require([len(g.ids) for g in groups]==CLAIM_SIZES,'challenge chronological sizes')
    require(kinds=={'MOVE':26199,'COPY':81,'IDLE':1998},'challenge request-kind counts')
    return {'request_count':len(requests),'replicas':rho,'groups':len(groups),
            'sizes':[len(g.ids) for g in groups],'kinds':kinds,
            'distinct_keys_coefficient_of_N':len(requests),
            'visits_coefficient_of_N':rho*len(requests),
            'per_key_multiplicity':rho}


def safe_relative(value):
    require(isinstance(value, str) and value and "\\" not in value,
            'repository-relative POSIX path')
    path = PurePosixPath(value)
    require(not path.is_absolute() and not PureWindowsPath(value).drive
            and '..' not in path.parts and path.as_posix() == value
            and value != '.', 'safe canonical source path: ' + value)
    return value


def pin_index(manifest):
    """Manifest is the published trust anchor, not a replacement for byte checks."""
    expected = manifest['package_sha256']
    require(len(expected) == 28, '28 archived package pins')
    pins = {}
    for rel, digest in expected.items():
        safe_relative(rel)
        require(rel.startswith(AUDIT + '/'), 'archived package pin scope')
        pins[rel] = {'sha256': digest}
    live = manifest['live_inputs']
    require(len(live) == 121, '121 live input pins')
    for row in live:
        rel = safe_relative(row['path'])
        require(rel not in pins, 'unique independent pin: ' + rel)
        pins[rel] = {'sha256': row['sha256'], 'git_blob': row['git_blob']}
    return pins


def load_manifest():
    return json.loads((HERE / 'AUTHENTICATION.json').read_bytes())


def read_pinned(root, rel, pins):
    """Return exactly the bytes just hashed; never authenticate one read and exec another."""
    root = Path(root).resolve()
    rel = safe_relative(rel)
    require(rel in pins, 'unlisted source/input: ' + rel)
    path = root / rel
    require(path.resolve().is_relative_to(root) and path.is_file() and not path.is_symlink(),
            'regular contained input: ' + rel)
    raw = path.read_bytes()
    row = pins[rel]
    require(sha256(raw).hexdigest() == row['sha256'], 'SHA256 mismatch: ' + rel)
    if 'git_blob' in row:
        # Compute the Git blob object ID directly; no Git executable/history needed.
        require(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                == row['git_blob'], 'Git blob mismatch: ' + rel)
    return raw


def authenticate(root, manifest=None):
    root = Path(root).resolve()
    manifest = load_manifest() if manifest is None else manifest
    pins = pin_index(manifest)
    expected = manifest['package_sha256']
    observed = {p.relative_to(root).as_posix() for p in (root / AUDIT).rglob('*')
                if p.is_file() and '__pycache__' not in p.parts}
    require(observed == set(expected), 'exact 28-file audit package inventory')
    for rel in pins:
        read_pinned(root, rel, pins)
    return {'package_files': len(expected), 'live_inputs': len(manifest['live_inputs']),
            'all_bytes_checked_before_source_import': True}


WINDOWS_VERIFIER = CALLER + '/inputs/pr2753/verify.py'
WINDOWS_OLD = "str(path.relative_to(here/'predecessor'))"
WINDOWS_NEW = "path.relative_to(here/'predecessor').as_posix()"


def windows_inventory_adapter(raw):
    """Only one verified expression changes, only in an authenticated in-memory copy."""
    old, new = WINDOWS_OLD.encode(), WINDOWS_NEW.encode()
    require(raw.count(old) == 1, 'exact inventory adapter anchor')
    return raw.replace(old, new)


class SourceLoader(importlib.abc.Loader):
    def __init__(self, owner, rel):
        self.owner, self.rel = owner, rel

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        self.owner.loaded_names.add(module.__name__)
        raw = read_pinned(self.owner.root, self.rel, self.owner.pins)
        executable = raw
        if self.rel == WINDOWS_VERIFIER and os.name == 'nt':
            require(module.__name__ == 'frozen_caller_verifier', 'frozen verifier alias')
            executable = windows_inventory_adapter(raw)
            self.owner.adapters.append({'path': self.rel, 'old': WINDOWS_OLD, 'new': WINDOWS_NEW})
        self.owner.records[self.rel] = sha256(raw).hexdigest()
        path = self.owner.root / self.rel
        module.__file__ = str(path)
        # Source only: neither adjacent nor prefix .pyc files are consulted.
        # Do not inherit future flags from this checking harness.
        exec(compile(executable, str(path), 'exec', dont_inherit=True), module.__dict__)


class SourceImports(importlib.abc.MetaPathFinder):
    """Isolated, hash-checked imports, including original explicit file-location imports.

    The import machinery changes, not compiler/numerical routines. The sole
    source expression adapter is the disclosed Windows inventory spelling.
    No cache directory is created or needed. Use serially, not across threads.
    """
    forbidden = frozenset(('accounting', 'source_audit', 'verify', 'extract_census'))

    def __init__(self, root, pins):
        self.root, self.pins = Path(root).resolve(), pins
        base = self.root / CALLER
        caller = base / 'inputs/pr2753'
        self.directories = (base, caller, caller / 'predecessor',
                            caller / 'predecessor/vendor', base / 'inputs/pr2769',
                            base / 'inputs/pr2769/vendor')
        self.records, self.adapters, self.loaded_names = {}, [], set()
        self.names = {p.stem for directory in self.directories for p in directory.glob('*.py')}
        self.names.update(Path(rel).stem for rel in pins
                          if (self.root / rel).parent in self.directories and rel.endswith('.py'))
        self.names.update(('bank_codec', 'frozen_caller_verifier', 'retained_selected_node_source'))

    def spec(self, name, path):
        path = Path(path).absolute()
        require(path.is_relative_to(self.root), 'source import outside root')
        rel = path.relative_to(self.root).as_posix()
        safe_relative(rel)
        require(rel in self.pins and rel.endswith('.py'), 'unpinned source import: ' + rel)
        require(not rel.startswith(AUDIT + '/'), 'archived audit source import forbidden')
        require(not any(part in self.forbidden for part in name.split('.')),
                'audit/verifier import forbidden: ' + name)
        return importlib.util.spec_from_loader(name, SourceLoader(self, rel), origin=str(path))

    def find_spec(self, fullname, path=None, target=None):
        require(not any(part in self.forbidden for part in fullname.split('.')),
                'audit/verifier import forbidden: ' + fullname)
        if '.' in fullname:
            return None
        for directory in self.directories:
            candidate = directory / (fullname + '.py')
            rel = candidate.relative_to(self.root).as_posix()
            if rel in self.pins or candidate.is_file():
                # Missing pinned files must not fall back to an ambient module.
                return self.spec(fullname, candidate)
            require(not (directory / fullname / '__init__.py').is_file(),
                    'unlisted source package: ' + fullname)
        return None

    def file_spec(self, name, location=None, *args, **kwargs):
        if location is not None and Path(location).absolute().is_relative_to(self.root):
            require(not args and not kwargs, 'plain original source-file import')
            return self.spec(name, location)
        return self.previous_file_spec(name, location, *args, **kwargs)

    def __enter__(self):
        require(not self.names.intersection(sys.modules), 'preloaded source module namespace')
        self.previous_meta, self.previous_path = list(sys.meta_path), list(sys.path)
        self.previous_file_spec = importlib.util.spec_from_file_location
        self.previous_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        sys.meta_path.insert(0, self)
        importlib.util.spec_from_file_location = self.file_spec
        return self

    def __exit__(self, *exc):
        importlib.util.spec_from_file_location = self.previous_file_spec
        sys.meta_path[:] = self.previous_meta
        sys.path[:] = self.previous_path
        sys.dont_write_bytecode = self.previous_bytecode
        for name in self.loaded_names:
            sys.modules.pop(name, None)


def activate_original(root, imports):
    """Original loader authentication/controls, not a numerical verifier replay.

    Only frozen_caller_verifier.authenticate is invoked. No archived audit
    accounting.py, source_audit.py, verify.py or extract_census.py is imported.
    The source-only importer hashes each executed byte string again at import.
    """
    loader = importlib.import_module('loader')
    loader.activate()
    loader.compatibility_controls()
    return {'original_loader_authenticate': 'passed',
            'windows_posix_inventory_adapter': imports.adapters,
            'original_selected_record_mutation_controls': 'passed'}


def selected_metadata(root,groups,requests,events,mappings,idles):
    from catalogue import Catalogue
    from topology import SelectedTopology
    from control import LocalState
    cat=Catalogue(3)  # ONLY metadata; no low_classes, bind, plan or compile_node.
    topology=SelectedTopology(cat)
    require(len(cat.requests)==len(requests),'raw/source request length')
    require(topology.replicas==cat.replicas==32,'raw/source replica count')
    for i,(actual,raw) in enumerate(zip(cat.requests,requests)):
        for key in ('kind','stage','position','role'):
            require(getattr(actual,key)==raw[key],f'raw/source request {i} {key}')
        if raw['kind']=='IDLE':
            require(actual.family==raw['family'] and actual.base.data==raw['axes'],f'idle source support {i}')
    visits=Counter(); event_count=0; all_groups=[]
    for pos,e in enumerate(topology.schedule):
        if e['kind'] not in ('local_cover_sweep','idle'): continue
        per_replica=[]
        for replica in range(topology.replicas):
            ids=[]
            if e['kind']=='local_cover_sweep':
                call=topology.call(e['stage'],replica)
                require(call.stage==e['stage'] and call.replica==replica,'call coordinates')
                require(call.events==events[e['stage']] and call.requests==mappings[e['stage']], 'literal call events/requests')
                state=LocalState(call)
                for position,item in enumerate(call.events):
                    op,role=state.accept(position); event_count+=1
                    require((op,role)==item[:2],'LocalState accepted opcode/role')
                    if op not in (0,2):
                        require(call.requests[position] is None,'non-residual event has request'); continue
                    identifier=call.requests[position]
                    r=cat.requests[identifier]
                    require((r.kind,r.stage,r.position,r.role)==
                            ('MOVE' if op==0 else 'COPY',e['stage'],position,role),'source dispatch binding')
                    ids.append(identifier); visits[identifier,True]+=1
                state.finish()
            else:
                require(topology.idles[e['idx']]==idles[e['idx']],'idle request order')
                for identifier in topology.idles[e['idx']]:
                    r=cat.requests[identifier]
                    require(r.kind=='IDLE' and r.stage==e['idx'],'idle source binding')
                    require(topology.idle_family(identifier,replica)==r.family+topology.stride*replica,'idle replica family')
                    ids.append(identifier); visits[identifier,False]+=1
            per_replica.append(tuple(ids))
        require(all(x==per_replica[0] for x in per_replica),'every replica ordered IDs')
        all_groups.append(Group(pos,e['kind'],per_replica[0]))
    require(all_groups==groups,'source execution versus independent raw-data groups')
    require(len(visits)==len(requests) and set(visits.values())=={32},'source-key multiplicity at symbolic one LOW')
    require(set(visits)=={(i,r['kind']!='IDLE') for i,r in enumerate(requests)},'source common/native key domain')
    return {'q':3,'local_events_executed':event_count,'source_key_pairs':len(visits),
            'metadata_request_visits':sum(visits.values()),'all_replicas':32,
            'GL64_LOW_enumerated':False,'selected_compiler_executed':False}


def tiny_emitter():
    """Real predecessor compiler, OWN non-selected fixture; no allocations audit."""
    from low_codes import LowCodes
    from macro_code import compile_node
    from topology import Call,Owner
    codes=LowCodes(3,2,8)
    lows=tuple(codes.unrank(i) for i in (0,1,47))
    I=((1,0),(0,1))
    groups=[Group(0,'local_cover_sweep',(0,1,2)),Group(1,'idle',(6,7)),
            Group(3,'local_cover_sweep',(3,4,5)),Group(4,'idle',())]
    class Cat:
        def low_classes(self): return iter(lows)
    cat=Cat(); cat.codes=codes
    class Top:
        replicas=2; pairs=2; ports=1; catalogue=cat
        idles={0:(6,7),1:()}
        schedule=({'kind':'local_cover_sweep','stage':0},{'kind':'idle','idx':0},
                  {'kind':'bridge','dst':0,'src':1,'coefficient':1},
                  {'kind':'local_cover_sweep','stage':1},{'kind':'idle','idx':1},{'kind':'exchange'})
        def call(self,stage,replica):
            ev=((0,0,0,1,1,0),(2,0,2,1,0,1,0),(1,1,2,1,0,0),
                (3,0,2,1,0,0,0),(0,1,0,1,1,0))
            ids=(3*stage,3*stage+1,None,None,3*stage+2)
            return Call(stage,replica,(Owner(4*replica,I),Owner(4*replica+1,I)),
                        (0,0),(1,1),ev,ids,False)
        def matrix(self,chart): return chart
        def idle_family(self,identifier,replica): return 4*replica+identifier-6
        def family(self,replica,pair,side,port): return 4*replica+2*pair+side
    seen=[]
    class Binding:
        def residual(self,identifier,common,low,mode):
            require(mode==0,'fixture mode'); seen.append((identifier,common,low))
            # axis avoids plan allocation/execution; no claim about default factory.
            return types.SimpleNamespace(identifier=identifier,common=common,low=low,axis=0)
    code=compile_node(Top(),Binding(),0)
    expected=projected_word(groups,2,lows)
    require(seen==[(r,c,l) for _,_,r,c,l in expected],'actual factory invocation sequence')
    observed=[]; current=[]; by_schedule={g.schedule_index:g for g in groups}; pos=0
    for op in code.operations:
        if op[0]=='residual_begin':
            d=op[2]; current.append((d.identifier,d.common,d.low)); observed.append(current[-1])
        elif op[0]=='checkpoint':
            g=by_schedule.get(pos)
            want=[] if g is None else [(r,c,l) for j,rep,r,c,l in expected if groups[j].schedule_index==pos]
            require(current==want,'emitted source keys at checkpoint '+str(pos))
            current=[]; pos+=1
    require(pos==len(Top.schedule) and not current,'all checkpoints including empty idle')
    require(observed==seen,'factory versus emitted key order')
    return {'fixture':'own GL2(F3), 2 replicas, 3 LOWs, MOVE/COPY/XOR/ERASE/IDLE/bridge/exchange',
            'emitted_visits':len(observed),'distinct_keys':len(set(observed)),
            'multiplicity_histogram':dict(Counter(Counter(observed).values())),
            'empty_idle_checkpoint_checked':True,'allocation_or_reference_tests':False}


def run_source(root=DEFAULT_ROOT):
    root = Path(root).resolve()
    started=time.monotonic()
    manifest = load_manifest()
    pins = pin_index(manifest)
    result={'authentication':authenticate(root, manifest)}
    template=json.loads(gzip.decompress(read_pinned(root, HOST, pins)))
    groups,requests,events,mappings,idles=raw_groups(template)
    result['independent_raw_data']=check_claims(groups,requests,template['replicas'])
    cert=json.loads(read_pinned(root, AUDIT + '/lean/SelectedCensus.json', pins))
    interval_data(cert,groups)
    require(cert['kinds']==result['independent_raw_data']['kinds'],'certificate request kinds')
    require(cert['replica_count']==template['replicas'],'certificate replicas')
    result['interval_data']={'compared_with_raw_data':True,'groups':len(groups),
                             'note':'not Lean execution or proof replay'}
    result['bytecode_policy'] = 'hash-checked source-only imports; no pyc reads/writes or cache directory'
    with SourceImports(root, pins) as imports:
        result['loader']=activate_original(root, imports)
        result['source_metadata']=selected_metadata(root,groups,requests,events,mappings,idles)
        result['source_tiny_emitter']=tiny_emitter()
        result['imports_sha256'] = imports.records
    # Formula is conditional on the inherited LOW bijection; no GL64 execution.
    result['symbolic_key_formula']={'N':'|GL64(F_q)|, inherited bijection premise',
        'distinct_keys':'28278*N','visits':'904896*N','per_key_multiplicity':32,
        'local_nesting':'group/replica/LOW/event','idle_nesting':'group/replica/request/LOW'}
    result['elapsed_seconds']=round(time.monotonic()-started,3)
    return result


def source_command(root, optimize=None):
    """Propagate -O/-OO through the optional serial timeout wrapper."""
    optimize = sys.flags.optimize if optimize is None else optimize
    require(type(optimize) is int and optimize in (0, 1, 2), 'optimization level')
    return [sys.executable, '-I', '-B', *(['-' + 'O' * optimize] if optimize else []),
            str(Path(__file__).resolve()), '--source', '--root', str(Path(root).resolve())]


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    modes=p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--source',action='store_true')
    modes.add_argument('--intervals',action='store_true')
    p.add_argument('--root',type=Path,default=DEFAULT_ROOT,
                   help='repository/source-export root (default: this package repository)')
    p.add_argument('--bounded',type=int,help='parent wrapper timeout seconds; launches one child serially')
    args=p.parse_args(argv)
    root=args.root.resolve()
    if args.bounded is not None:
        require(1<=args.bounded<=180 and args.source,'bounded source run 1..180 seconds')
        try:
            child=subprocess.run(source_command(root),capture_output=True,text=True,timeout=args.bounded)
        except subprocess.TimeoutExpired:
            print(json.dumps({'status':'TIMEOUT','seconds':args.bounded,'source_checks':'incomplete'})); return 2
        sys.stdout.write(child.stdout); sys.stderr.write(child.stderr)
        return child.returncode
    if args.source:
        result=run_source(root)
    else:
        manifest=load_manifest()
        pins=pin_index(manifest)
        result={'authentication':authenticate(root, manifest)}
        cert=json.loads(read_pinned(root, AUDIT + '/lean/SelectedCensus.json', pins))
        groups=interval_data(cert)
        result['interval_data_only']={'groups':len(groups),'requests':sum(len(g.ids) for g in groups),
                                     'source_execution':False,'source_link_not_established':True}
    print(json.dumps({'status':'PASS','result':result},indent=2,sort_keys=True))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
