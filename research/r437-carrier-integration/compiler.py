"""Fresh carrier-to-pooled catalogue binding; no implicit physical admission.

Reuse ai-nanachi's R437/OQ4, Rohan Arun's pooling, and PR4010's replica API.
Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import copy
import gzip
import importlib.util
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
POOLED = ROOT/'research/r437-pooled-native-interface'
CARRIER = ROOT/'research/r437-two-window-carrier'
VERSION = 'carrier-pooled-replica-v1'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))

def digest(value):
    return sha256(canonical(value).encode()).hexdigest()

def read_gz(path):
    return json.loads(gzip.decompress(path.read_bytes()))

def candidate_template():
    manifest = json.loads((CARRIER/'CANDIDATE-TEMPLATE.json').read_bytes())
    need(manifest['format']=='exact-gzip-byte-chunks-v1', 'carrier chunk format')
    chunks=[]
    for i, row in enumerate(manifest['parts']):
        need(row['path']==f'candidate-template-chunks/part-{i:03d}.bin','ordered carrier chunks')
        data=(CARRIER/row['path']).read_bytes()
        need(len(data)==row['bytes'] and sha256(data).hexdigest()==row['sha256'],'carrier chunk identity')
        chunks.append(data)
    data=b''.join(chunks)
    need(len(data)==manifest['bytes'] and sha256(data).hexdigest()==manifest['sha256'],'carrier joined identity')
    value=json.loads(gzip.decompress(data))
    need(digest(value)=='11a564406f5763111444be25c3d39cbc4e46f45d21441e526ae2e22da5149568','exact published carrier template')
    return value

def authenticate_retained():
    manifest=json.loads((POOLED/'SOURCES.json').read_bytes())
    for row in manifest['retained']:
        path=POOLED/row['path']
        need(path.is_file() and not path.is_symlink(),'regular predecessor source')
        data=path.read_bytes()
        need(len(data)==row['bytes'] and sha256(data).hexdigest()==row['sha256'],'retained compiler/source identity '+row['path'])

@lru_cache(None)
def runtime():
    authenticate_retained()
    sys.path.insert(0,str(POOLED))
    import adapter
    sys.path.insert(0,str(adapter.PHYSICAL))
    import loader
    loader.activate()
    import catalogue, topology, replica_catalogue, pooled_compiler
    return types.SimpleNamespace(adapter=adapter,catalogue=catalogue,topology=topology,
                                 replica=replica_catalogue,owners=pooled_compiler)

def _replace(source, old, new, count=1):
    need(source.count(old)==count,'exact catalogue adaptation context '+old[:50])
    return source.replace(old,new)

@lru_cache(None)
def inputs(carrier):
    old=read_gz(POOLED/'inputs/word.json.gz')
    template=read_gz(POOLED/'inputs/template.json.gz')
    expected=json.loads((POOLED/'inputs/EXPECTED.json').read_bytes())
    for name,field in [('word','word_content_sha256'),('template','template_content_sha256')]:
        need(sha256(gzip.decompress((POOLED/f'inputs/{name}.json.gz').read_bytes())).hexdigest()==expected[field], 'frozen baseline '+name)
    word=json.loads((CARRIER/'CANDIDATE.json').read_bytes()) if carrier else old
    if carrier:
        need(sha256((CARRIER/'CANDIDATE.json').read_bytes()).hexdigest()=='0e4dc8bda7941b9c5bba2f7af9895544ca6f69666026e4835610b808c3d4d7f2','carrier word publication identity')
        template=candidate_template()
    need(word['lines']==old['lines'] and word['frames']==old['frames'],'unchanged rational frame inventory')
    return word,template,read_gz(POOLED/'inputs/geometry.json.gz')

def load(variant='D', q=3):
    """A/B are original owners; C/D use the exact 63 pooling moves.

    All variants expose the explicit replica interface and fresh identity.
    Compilation uses a fixed odd prime; caller input must establish primality.
    """
    need(variant in 'ABCD' and len(variant)==1,'known comparison variant')
    need(isinstance(q,int) and q>=3 and q%2==1,'odd-prime parameter domain')
    rt=runtime()
    word, template, geometry=inputs(variant in 'BD')
    moves=json.loads((POOLED/'inputs/moves.json').read_bytes())['moves'] if variant in 'CD' else []
    # Build unpooled literal prototypes first. The exact source guards survive;
    # only the old frozen digest/profile constants are replaced by fresh receipts.
    profile=Counter()
    for call in template['calls']:
        for event in template['local_programs'][call['orientation']]:
            if event[0]==0: profile[event[4]]+=1
            elif event[0]==2: profile[event[5]]+=1
    for counts in template['hosting']['remainders'].values():
        for rank,count in counts.items():
            if int(rank):profile[int(rank)]+=32*count
    source=Path(rt.catalogue.__file__).read_text()
    source=_replace(source,'private=661','private=659')
    source=_replace(source,'==661','==659',3)
    source=_replace(source,'self.word,self.template,self.geometry=(self.old.read(p) for p in\n                                               (self.old.WORD,self.old.HOST,self.old.GEO))','self.word,self.template,self.geometry=copy.deepcopy(FRESH_INPUTS)')
    source=_replace(source,'expected={int(k):v for k,v in self.old.read("research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]["profile"].items()}','expected=FRESH_PROFILE')
    source=_replace(source,'==904896','==903456')
    source=_replace(source,'        need(self.receipt()["binding_sha256"]=="f5a4fb124709adc4b56376a3146e3609e91c0f4d3ed1931a61785a5d99bf8ee7",\n             "exact ordered PR2234 request records")','        # Fresh request digest is independently checked by comparison.py.')
    name='carrier_catalogue_'+variant+'_'+str(q)
    module=types.ModuleType(name);module.__file__=str(HERE/'compiler.py')
    module.copy=copy;module.FRESH_INPUTS=(word,template,geometry);module.FRESH_PROFILE=profile
    sys.modules[name]=module
    exec(compile(source,'<fresh authenticated R437 catalogue>','exec'),module.__dict__)
    cat=module.Catalogue(q)
    topo_source=_replace(Path(rt.topology.__file__).read_text(),'==661','==659')
    tm=types.ModuleType(name+'_topology');sys.modules[tm.__name__]=tm
    exec(compile(topo_source,'<659-role R437 topology>','exec'),tm.__dict__)
    old_top=tm.SelectedTopology(cat)
    pooled,profile,idles=rt.owners.compile_owners(template,moves)
    old_top.catalogue=copy.copy(cat)
    prototypes=cat.requests; old_bits=cat.codes.bits
    cat.template=pooled;cat.bases=dict(cat.bases)
    cat.requests=rt.replica.Requests(cat,prototypes,idles)
    cat.profile=profile
    from low_codes import LowCodes
    cat.codes=LowCodes(q,64,len(cat.requests));cat.old_code_bits=old_bits
    cat.identifiers={};cat.identifier=cat.requests.identifier
    cat.semantic_key=lambda request:request.key
    cat.erase_guards=tuple((stage,replica,*rest) for stage,*rest in cat.erase_guards for replica in range(32))
    cat.charts={cat.owner_chart(call,role) for call in pooled['calls'] for role in range(659)}
    cat.charts.update(r.chart for r in cat.requests.idles)
    cat.charts.update(r.chart for r in prototypes if r.kind=='COPY')
    cat.variant=variant
    cat.input_identity=digest({'word':digest(word),'template':digest(template),'pooled':digest(pooled),'moves':digest(moves)})
    cat.source_identity=codebook_identity(cat)
    cat.receipt=lambda:compiler_receipt(cat)
    return cat,rt.replica.ReplicaTopology(cat,old_top)

def codebook_identity(cat):
    import low_codes
    algorithms=[Path(__file__),Path(runtime().catalogue.__file__),POOLED/'replica_catalogue.py',
                POOLED/'pooled_compiler.py',Path(low_codes.__file__)]
    return digest([VERSION,cat.input_identity,cat.q,cat.dimension,len(cat.requests),cat.codes.bits,
                   [(path.name,sha256(path.read_bytes()).hexdigest()) for path in algorithms]])

@dataclass(frozen=True)
class SourceHandle:
    schema: str
    identity: str
    code: int
    request_key: tuple

def source_handle(cat,identifier,common,low):
    r=cat.requests[identifier]
    return SourceHandle(VERSION,cat.source_identity,cat.codes.encode(identifier,common,low),r.key)

def resolve_handle(cat,specifications,handle):
    need(isinstance(handle,SourceHandle) and handle.schema==VERSION and handle.identity==cat.source_identity,'exact carrier source context')
    need(getattr(specifications,'catalogue',None) is cat,'exact Specifications instance context')
    identifier,common,low=cat.codes.decode(handle.code)
    need(cat.requests[identifier].key==handle.request_key,'literal request/replica binding')
    return specifications[handle.code]

def compiler_receipt(cat):
    h=sha256();kinds=Counter();ranks=Counter()
    for r in cat.requests:
        h.update((canonical(r.record())+'\n').encode());kinds[r.kind]+=1;ranks[r.base.rank]+=1
    need(ranks==cat.profile,'complete fresh request profile')
    return {'variant':cat.variant,'input_identity':cat.input_identity,'source_identity':cat.source_identity,
            'request_sha256':h.hexdigest(),'requests':len(cat.requests),'kinds':dict(sorted(kinds.items())),
            'profile':dict(sorted(ranks.items())),'rank_mass':sum(r*n for r,n in ranks.items()),
            'prototype_code_bits':cat.old_code_bits,'code_bits':cat.codes.bits,
            'bases':len(cat.bases),'charts':len(cat.charts),'erase_guards':len(cat.erase_guards)}

def early_source87(cat,top,stage=0,replica=0):
    call=top.call(stage,replica)
    candidates=[(i,e) for i,e in enumerate(call.events) if e[0]==0 and e[1]==87 and set(e[2:4])=={189,509}]
    need(len(candidates)==1,'unique affected SOURCE87 move')
    position,event=candidates[0];identifier=cat.identifier('MOVE',stage,replica,position)
    return {'identifier':identifier,'key':list(cat.requests[identifier].key),'position':position,
            'event':event,'record':cat.requests[identifier].record()}

@lru_cache(None)
def logical_driver():
    """The retained generator Driver with explicit per-replica IDLE lookup."""
    runtime()
    import driver
    source=Path(driver.__file__).read_text()
    source=_replace(source, 'for identifier in topology.idles[event["idx"]]:yield from self.idle(families,identifier,replica)',
                    'for identifier in topology.idle_identifiers(event["idx"],replica):yield from self.idle(families,identifier,replica)')
    module=types.ModuleType('carrier_logical_driver');sys.modules[module.__name__]=module
    exec(compile(source,'<explicit-replica logical Driver>','exec'),module.__dict__)
    return module

@lru_cache(None)
def caller_emitter():
    """Actual finite macro compiler, with its single IDLE consumer adapted."""
    rt=runtime()
    import macro_code
    source=Path(macro_code.__file__).read_text()
    source=_replace(source, 'for identifier in topology.idles[event["idx"]]:',
                    'for identifier in topology.idle_identifiers(event["idx"], replica):')
    module=types.ModuleType('carrier_macro_code');sys.modules[module.__name__]=module
    exec(compile(source,'<explicit-replica macro compiler>','exec'),module.__dict__)
    return module

def compile_node(topology, binding, mode=0):
    need(binding.catalogue is topology.catalogue,'macro compiler exact source/native context')
    need(getattr(binding.catalogue,'source_identity',None)==codebook_identity(binding.catalogue),
         'macro compiler fresh source context')
    return caller_emitter().compile_node(topology,binding,mode)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    rows={}
    for variant in 'CD':
        cat,top=load(variant);rows[variant]=compiler_receipt(cat)
        rows[variant]['source87']=[early_source87(cat,top,s) for s in (0,1)]
    rows['incremental_code_bits']=rows['D']['code_bits']-rows['C']['code_bits']
    if args.write:(HERE/'COMPILER-RESULT.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
    print(json.dumps(rows,sort_keys=True))
