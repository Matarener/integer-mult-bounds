"""Source-derived length envelope, without GL enumeration or factory calls.
JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from collections import Counter,defaultdict
from dataclasses import dataclass
import gzip
from hashlib import sha256
import json
from math import prod
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
BASE='research/selected-bit-physical-caller/'
VENDOR=BASE+'inputs/pr2753/predecessor/vendor/'
TEMPLATE='research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz'


def need(ok,why):
    if not ok:raise ValueError(why)


def authenticate():
    data={}
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes()
            need(sha256(raw).hexdigest()==row['sha256'],'source drift '+row['path'])
            data[row['path']]=raw
    return data


def extract(raw,names,namespace):
    nodes=[n for n in ast.parse(raw).body if getattr(n,'name',None) in names]
    need(len(nodes)==len(names) and {n.name for n in nodes}==set(names),'exact source definitions')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pinned source definitions>','exec'),namespace)
    return namespace


def fallback_bound(d):
    need(type(d)is int and 2<=d<=64,'source dimension')
    n=2*d
    return 6*(n-1)+4*n*(n-1)+3*(n-1)+1


@dataclass(frozen=True)
class Envelope:
    low_classes:int
    nonblocks_per_low:int
    residuals_per_low:int
    fixed:int
    block_max:int
    @property
    def lower(self):return (self.nonblocks_per_low+3*self.residuals_per_low)*self.low_classes+self.fixed
    @property
    def upper(self):return (self.nonblocks_per_low+self.block_max*self.residuals_per_low)*self.low_classes+self.fixed


def derive(data):
    t=json.loads(gzip.decompress(data[TEMPLATE]))
    pending=extract(data['research/pr589-five-helper-hosting/verify.py'],{'pending_axes'},{'need':need})['pending_axes']
    topology=ast.parse(data[BASE+'inputs/pr2753/predecessor/topology.py'])
    cls=next(n for n in topology.body if isinstance(n,ast.ClassDef) and n.name=='SelectedTopology')
    constants={n.targets[0].id:ast.literal_eval(n.value) for n in cls.body if isinstance(n,ast.Assign)}
    replicas,ports,pairs=map(constants.get,('replicas','ports','pairs'))
    need((replicas,ports,pairs)==(32,111,4) and t['replicas']==replicas,'actual topology constants')
    idles={e['idx']:e for e in t['schedule'] if e['kind']=='idle'}
    occupied=defaultdict(set)
    for child,copy,offset,width,*_ in t['hosting']['slots']:
        axes=pending(idles[child])[offset:offset+width]
        need(len(axes)==width and not occupied[child,copy].intersection(axes),'hosted axes disjoint')
        occupied[child,copy].update(axes)
    idle_counts={i:sum(bool(set(pending(e))-occupied[i,c]) for c in range(2*ports)) for i,e in idles.items()}
    histograms={name:Counter(x[0] for x in word) for name,word in t['local_programs'].items()}
    nonblocks=residuals=0;fixed=len(t['schedule'])+2;calls=[]
    for event in t['schedule']:
        kind=event['kind']
        if kind=='local_cover_sweep':
            for replica in range(replicas):
                call=t['calls'][replicas*event['stage']+replica]
                need(call['stage']==event['stage'] and call['replica']==replica,'literal call indexing')
                h=histograms[call['orientation']]
                need(set(h)<={0,1,2,3} and len(call['owners'])==661,'local source grammar')
                r=h[0]+h[2];a=3*len(call['owners'])+1+h[1]+2*h[2]+h[3]+2*r
                residuals+=r;nonblocks+=a;calls.append((r,a))
        elif kind=='idle':
            r=replicas*idle_counts[event['idx']];residuals+=r;nonblocks+=5*r
        elif kind=='bridge':fixed+=replicas*ports*2
        else:
            need(kind=='exchange','global source grammar');fixed+=replicas*pairs*ports
    q=213*(1<<80)+1
    # Reuse the pinned Proth witness; no new prime search.
    need(pow(7,(q-1)//2,q)==q-1 and 213<(1<<80),'inherited prime witness')
    g=prod(q**64-q**i for i in range(64))
    envelope=Envelope(g,nonblocks,residuals,fixed,fallback_bound(64))
    return envelope,{'idle_counts':idle_counts,'calls':len(calls),'local_shapes':sorted(set(calls)),
                     'prime':q,'dimension':64,'schedule_events':len(t['schedule'])}


def source_header(data):
    # Compile unchanged source classes without activating the obsolete loader.
    namespace={'need':need,'ZERO':0,'ONE':1,'LEFT':2,'RIGHT':3,'BLANK':4,'RETURN':13}
    extract(data[VENDOR+'words.py'],{'Meter'},namespace)
    extract(data[VENDOR+'records.py'],{'Tape'},namespace)
    extract(data[BASE+'role_parking.py'],{'FiniteFields'},namespace)
    machine=next(n for n in ast.parse(data[BASE+'macro_machine.py']).body if isinstance(n,ast.ClassDef) and n.name=='Machine')
    methods={n.name:n for n in machine.body if isinstance(n,ast.FunctionDef)}
    call=next(n for n in methods['call'].body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='self.header.write')
    restore=next(n for n in methods['complete_return'].body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=='self.header.read')
    need(ast.unparse(call.value.args[1].elts[2])=='self.pc + 1','source saved next PC')
    need(ast.unparse(restore.targets[0])=='(root, self.mode, self.pc, *labels)','source restored PC')
    for name,node in [('write_source',call),('read_source',restore)]:
        fn=ast.FunctionDef(name=name,args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='self'),ast.arg(arg='ring')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=[node],decorator_list=[])
        exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<literal source header statement>','exec'),namespace)
    return namespace
