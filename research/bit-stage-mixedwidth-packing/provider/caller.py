#!/usr/bin/env python3
"""A new source-bound Catalogue/Topology for the unchanged logical caller.

This adapter does not edit or relax the retained selected provider. It binds
the new finite request table to the retained generic executable interfaces.
Historical Python modules execute authenticated bytes, without bytecode imports.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import argparse
import gzip
import importlib.abc
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parent
BASE="12fa8c5c844be21bfefb38a19503fbd867a11244"
PREFIX="research/selected-bit-recursive-caller/"
SOURCE_MAP_SHA="62682f12db2f42394d0ec0950af5a9f857c97ff6280b77656beb5e3d3a24909f"
GEOMETRY_RAW_SHA="0058c491d839142aa99ef86a5ec697ce99857632228531512ea3fa74fb24d734"
GEOMETRY_GZIP_SHA="a1629f8cf4321addc5a1e24c4ce2bc744a4c35c1d1eff9bd59fc6fd437f9f0c1"


def need(ok,message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


class FrozenLoader(importlib.abc.MetaPathFinder,importlib.abc.Loader):
    """Source bytes are authenticated before any predecessor module executes."""
    def __init__(self):
        manifest=json.loads((ROOT/"CALLER-SOURCES.json").read_bytes())
        need(manifest["base"] == BASE,"caller source commit")
        need(digest(manifest["files"]) == SOURCE_MAP_SHA,"complete caller source map")
        self.sources={}
        self.loaded={}
        for rel,pin in manifest["files"].items():
            need(rel.startswith(PREFIX),"caller source path scope")
            local=rel[len(PREFIX):]
            path=ROOT/"inputs"/"caller"/local
            raw=path.read_bytes()
            need(sha256(raw).hexdigest() == pin,"caller source pin "+local)
            self.sources[local]=(path,raw,pin)
        need(len(self.sources) == 84,"complete caller source export")
        self.modules={}
        # Same precedence as the retained bootstrap, without normal imports.
        for parent in ("predecessor/vendor/","predecessor/",""):
            for local,data in self.sources.items():
                if local.startswith(parent) and "/" not in local[len(parent):] and local.endswith(".py"):
                    self.modules[Path(local).stem]=data
        self.source_map=manifest["files"]

    def find_spec(self,fullname,path=None,target=None):
        if fullname in self.modules:
            return importlib.util.spec_from_loader(fullname,self)
        return None

    def create_module(self,spec):
        return None

    def exec_module(self,module):
        path,raw,pin=self.modules[module.__name__]
        need(sha256(raw).hexdigest() == pin,"loaded immutable source bytes")
        module.__file__=str(path)
        module.__package__=""
        self.loaded[module.__name__]=pin
        exec(compile(raw,str(path),"exec",dont_inherit=True,optimize=0),module.__dict__)

    def install(self):
        need(not any(name in sys.modules for name in self.modules),
             "caller must start with an unambiguous source module namespace")
        sys.meta_path.insert(0,self)


def package_module(name):
    """Execute this package's own source, bypassing any .pyc cache."""
    path=ROOT/(name+".py")
    raw=path.read_bytes()
    module=ModuleType("bound_"+name)
    module.__file__=str(path)
    exec(compile(raw,str(path),"exec",dont_inherit=True,optimize=0),module.__dict__)
    return module,sha256(raw).hexdigest()


def build_provider(q=3,variant="candidate"):
    loader=FrozenLoader()
    loader.install()
    import catalogue as retained
    import topology as retained_topology
    from low_codes import LowCodes
    from sources import identity,product
    native,native_sha=package_module("native")
    owner,owner_sha=package_module("owner")
    summary,artifacts=owner.construct()
    need(json.loads(json.dumps(summary)) == json.loads((ROOT/"OWNERS.json").read_bytes()),
         "fresh complete owner receipt")
    transport=(ROOT/"inputs"/"CALLER-GEOMETRY.json.gz").read_bytes()
    need(sha256(transport).hexdigest() == GEOMETRY_GZIP_SHA,"caller geometry transport")
    raw_geometry=gzip.decompress(transport)
    need(sha256(raw_geometry).hexdigest() == GEOMETRY_RAW_SHA,"caller geometry source bytes")
    data_geometry=json.loads(raw_geometry)
    word=json.loads(gzip.decompress((ROOT/"inputs"/"WORD.json.gz").read_bytes()))
    geometry=json.loads(gzip.decompress((ROOT/"inputs"/"GEOMETRY.json.gz").read_bytes()))
    record_sets={"candidate":native.candidate(word["records"]),"baseline":word["records"]}
    need(all(native.digest(records) == native.WORD_HASHES[name]
             for name,records in record_sets.items()),"both literal source words")
    program_sets={key:{name:native.local_program(native.lower(records),rev)
                       for name,rev in (("forward",False),("reverse",True))}
                  for key,records in record_sets.items()}
    native_receipt=json.loads((ROOT/"NATIVE.json").read_bytes())
    for key,programs in program_sets.items():
        for orientation in ("forward","reverse"):
            need(digest(programs[orientation]) ==
                 native_receipt["words"][key]["local_checks"][orientation]["events_sha256"],
                 "both native provider event bindings")
    need(len(data_geometry["ports"]) == len(geometry["lines"]) == 111,
         "exact selected port inventory")
    denominators=Counter()
    for i,port in enumerate(data_geometry["ports"]):
        need(port["port"] == i and port["q"] == geometry["lines"][i],"rho15 port/root order")
        rho=[[Q(x) for x in row] for row in port["rho15"]]
        need(len(rho) == 15 and all(len(row) == 15 for row in rho),"rho15 shape")
        need(product(rho,tuple(zip(*rho))) == identity(15),"rho15 exact orthogonality")
        for row in rho:
            for x in row:
                need(x.denominator & (x.denominator-1) == 0,"rho15 dyadic coefficient")
                denominators[x.denominator]+=1
        line=[[Q(port["q"][a]*port["q"][b],4) if a < 8 and b < 8 else Q(0)
               for b in range(15)] for a in range(15)]
        head=[[Q(a == b and a < 8) for b in range(15)] for a in range(15)]
        exterior=[[Q(a == b and a >= 8) for b in range(15)] for a in range(15)]
        complement=[[head[a][b]-line[a][b] for b in range(15)] for a in range(15)]
        for source,target in ((line,line),(head,[[line[a][b]+exterior[a][b]
                            for b in range(15)] for a in range(15)]),
                              (complement,exterior),(exterior,complement)):
            need(product(product(rho,source),tuple(zip(*rho))) == target,
                 "rho15 exact data/idle projector bridge")

    schedule=[]
    for event in artifacts["ORDER"]["controller"]:
        e=dict(event)
        if e["kind"] == "local":
            e["kind"]="local_cover_sweep"
        schedule.append(e)
    template_base={
        "m":64,"stages":9,"replicas":32,"live":28416,
        "schedule":schedule,
        "loop_order":"Each recipe phase: replicas then all cover classes; finish every local invocation before the next.",
        "hosting":{"slots":artifacts["SLOTS"]},
    }
    family_charts=[tuple(tuple(Q(x) for x in row) for row in matrix)
                   for matrix in artifacts["CHARTS"]["family_charts"]]
    relative_charts=artifacts["CHARTS"]["relative_charts"]
    projectors,dimensions=zip(*(owner.projector([geometry["lines"][i] for i in f])
                               for f in geometry["frames"]))

    class Catalogue(retained.Catalogue):
        private=660

        def __init__(self,q,variant="candidate"):
            need(variant in program_sets,"matched caller word variant")
            self.q=q
            self.variant=variant
            self.programs=program_sets[variant]
            calls=[dict(call,local_hash=digest(self.programs[call["orientation"]]))
                   for call in artifacts["DISPATCH"]]
            self.word,self.geometry=word,data_geometry
            self.template=dict(template_base,calls=calls,local_programs=self.programs)
            self.projectors,self.dimensions=projectors,dimensions
            self.idles={e["idx"]:e for e in self.template["schedule"] if e["kind"] == "idle"}
            self.requests,self.bases,self.charts,self.erase_guards=[],{},set(),[]
            self._bind()
            self.codes=LowCodes(q,64,len(self.requests))
            self.identifiers={self.semantic_key(r):i for i,r in enumerate(self.requests)}
            need(len(self.identifiers) == len(self.requests),"new unique complete request identifiers")
            self._recursive_caller_topology=Topology(self)

        def base(self,a,b):
            lo,hi=(a,b) if self.dimensions[a] <= self.dimensions[b] else (b,a)
            matrix=tuple(tuple(x-y for x,y in zip(u,v))
                         for u,v in zip(self.projectors[hi],self.projectors[lo]))
            base=retained.Base("local",matrix,self.dimensions[hi]-self.dimensions[lo])
            return self.bases.setdefault(base.key,base)

        def pending(self,child):
            return tuple(self.idles[child]["axes"])

        def owner_chart(self,call,role):
            family,route=call["owners"][role]
            if route[0] == "data":
                return retained.Chart("data",route[2],route[1])
            need(route[0] == "hosted" and len(route) == 5,"new hosted owner schema")
            _,child,offset,width,cid=route
            axes=self.pending(child)[offset:offset+width]
            entry=relative_charts[cid]
            need(tuple(entry["axes"]) == axes and width in (4,8),"actual mixed terminal support")
            need(entry["terminal_frame"] == word["final"][role],"actual terminal frame binding")
            return retained.Chart("host",family%111,entry["terminal_frame"],(cid,*axes))

        @lru_cache(None)
        def chart_matrix(self,chart):
            out=identity(64)
            if chart.kind == "identity":
                return tuple(map(tuple,out))
            if chart.kind == "data":
                if chart.stage == 0:
                    return tuple(map(tuple,out))
                axes=list(range(8))+list(range(8+7*(chart.stage-1),8+7*chart.stage))
                rho=self.geometry["ports"][chart.port]["rho15"]
                for i,a in enumerate(axes):
                    for j,b in enumerate(axes):
                        out[a][b]=Q(rho[i][j])
                return tuple(map(tuple,out))
            need(chart.kind in ("family","host"),"new chart kind")
            for i in range(8):
                out[i][:8]=family_charts[chart.port][i]
            if chart.kind == "family":
                return tuple(map(tuple,out))
            cid,*axes=chart.axes
            entry=relative_charts[cid]
            need(entry["axes"] == axes and entry["terminal_frame"] == chart.stage,
                 "host chart key retains terminal and support")
            relative=tuple(tuple(Q(x) for x in row) for row in entry["relative_matrix"])
            return tuple(map(tuple,product(out,relative)))

        def _bind(self):
            template=self.template
            for stage in range(9):
                call=template["calls"][32*stage]
                for replica in range(32):
                    other=template["calls"][32*stage+replica]
                    need((other["stage"],other["replica"],other["orientation"],other["local_hash"])
                         == (stage,replica,call["orientation"],call["local_hash"]),
                         "new replica literal binding")
                    need(len(other["owners"]) == len(call["owners"]) == 660
                         and all(route == r0 and family == f0+888*replica
                                 for (family,route),(f0,r0) in zip(other["owners"],call["owners"])),
                         "new replica owner symmetry")
                    need(other["private_owner"] == [28416+stage,["private","d"]],
                         "new exact private owner descriptor")
                opened=None
                for position,event in enumerate(self.programs[call["orientation"]]):
                    op,role=event[:2]
                    if op == 0:
                        _,_,a,b,rank,_=event
                        base=self.base(a,b)
                        need(base.rank == rank and opened is None,"new MOVE paid rank/lifetime")
                        self._append(retained.Request("MOVE",stage,position,role,call["owners"][role][0],
                            a,b,base,self.owner_chart(call,role),"owner"))
                    elif op == 2:
                        _,_,temporary,a,b,rank,_=event
                        base=self.base(a,b)
                        need(temporary == 660 and opened is None and base.rank == rank == 7,
                             "new source-bound COPY")
                        opened=retained.Request("COPY",stage,position,role,call["private_owner"][0],a,b,
                            base,retained.Chart("identity"),"common",self.owner_chart(call,role))
                        self._append(opened)
                    elif op == 3:
                        _,_,temporary,a,b,_,_=event
                        need(opened is not None and opened.role == role and temporary == 660
                             and opened.base == self.base(a,b),"new exact ERASE source request")
                        self.erase_guards.append((stage,position,opened.position,role,opened.base.key))
                        opened=None
                    else:
                        need(op == 1,"new local opcode")
                need(opened is None,"new complete private lifetime")
            for child,copy,axes in artifacts["REMAINDERS"]:
                if not axes:
                    continue
                event=self.idles[child]
                base=retained.Base("idle",tuple(axes),len(axes))
                base=self.bases.setdefault(base.key,base)
                self._append(retained.Request("IDLE",child,child,copy,event["pair"]*222+copy,
                    event["source_level"],event["target_level"],base,
                    retained.Chart("family",copy%111),"owner"))
            self.profile=Counter()
            for request in self.requests:
                self.profile[request.base.rank]+=32
            expected=Counter({int(r):288*n for r,n in
                native_receipt["words"][self.variant]["local_checks"]["forward"]["histogram"].items()})
            expected.update({int(r):32*n for r,n in
                summary["idle_per_replica_including_zero"].items() if int(r)})
            total=901312 if self.variant == "candidate" else 901600
            need(self.profile == expected and sum(self.profile.values()) == total
                 and len(self.requests) == total//32,"new complete paid catalogue")

    class Topology(retained_topology.SelectedTopology):
        @lru_cache(None)
        def call(self,stage,replica):
            source=self.catalogue.template["calls"][32*stage+replica]
            events,identifiers,start,end,reverse=self.recipe(stage)
            owners=tuple(retained_topology.Owner(family,self.catalogue.owner_chart(source,role))
                         for role,(family,_route) in enumerate(source["owners"]))
            need(len(owners) == len(start) == len(end) == 660,"new complete staged roles")
            return retained_topology.Call(stage,replica,owners,start,end,events,identifiers,reverse)

    bound=Catalogue(q,variant)
    provenance={
        "source_commit":BASE,"source_map_sha256":SOURCE_MAP_SHA,
        "frozen_files":84,"geometry_raw_sha256":GEOMETRY_RAW_SHA,
        "geometry_gzip_sha256":GEOMETRY_GZIP_SHA,
        "package_source_sha256":{"native.py":native_sha,"owner.py":owner_sha},
        "owner_receipt_sha256":sha256((ROOT/"OWNERS.json").read_bytes()).hexdigest(),
        "native_receipt_sha256":sha256((ROOT/"NATIVE.json").read_bytes()).hexdigest(),
        "rho15_exact_orthogonal_dyadic_matrices":111,
        "rho15_data_idle_projector_identities":444,
        "data_route_stage8_ambient_boundary":64,
        "rho15_denominator_histogram":dict(sorted(denominators.items())),
        "literal_word_sha256":{key:native.digest(records) for key,records in record_sets.items()},
    }
    return bound,loader,provenance


def literal_census(catalogue):
    from control import LocalState
    topology=catalogue._recursive_caller_topology
    counts=Counter()
    binding=sha256()
    for stage in range(9):
        for replica in range(32):
            call=topology.call(stage,replica)
            state=LocalState(call)
            for position,event in enumerate(call.events):
                op,role=state.accept(position)
                counts[op]+=1
                if op in (0,2):
                    identifier=call.requests[position]
                    r=catalogue.requests[identifier]
                    need(r.role == role and r.stage == stage and r.position == position
                         and r.kind == ("MOVE" if op == 0 else "COPY"),
                         "complete literal-to-request provenance")
                    if replica == 0:
                        binding.update(canonical([stage,position,identifier])+b"\n")
            state.finish()
    need(counts == {0:836064,1:10352736,2:2592,3:2592},"new complete literal census")
    return {"literal_counts":dict(counts),"literal_events":sum(counts.values()),
            "consumer_binding_sha256":binding.hexdigest(),"complete_calls":288,
            "ordinary_roles":660,"private_role":660}


def split_basis_census(catalogue):
    """Execute the unchanged exact split-basis checker on every new label."""
    ranks=Counter()
    signature=sha256()
    for key,base in sorted(catalogue.bases.items()):
        basis=base.basis(catalogue.q)
        need(len(basis) == 64 and all(len(row) == 64 for row in basis),
             "complete new fixed rational split basis")
        ranks[base.rank]+=1
        signature.update(canonical([key,[[str(x) for x in row] for row in basis]])+b"\n")
    return {"prime":catalogue.q,"complete_base_labels":sum(ranks.values()),
            "ranks":dict(sorted(ranks.items())),"basis_sha256":signature.hexdigest(),
            "checker":"unchanged binding.split_basis: exact PB=B diag(I_rank,0), modular full rank"}


def selected_requests(catalogue):
    tests={
        "retired_carrier_rank7":lambda r:r.kind == "MOVE" and r.stage == 0
            and r.role == 469 and r.old_frame == 0 and r.new_frame == 517,
        "advanced_source50":lambda r:r.kind == "MOVE" and r.stage == 0
            and r.role == 50 and r.old_frame == 52 and r.new_frame == 509,
        "partial_terminal":lambda r:r.kind == "MOVE" and r.stage == 0
            and r.role == 462 and r.new_frame == 506,
        "copy476":lambda r:r.kind == "COPY" and r.stage == 0 and r.role == 476,
        "short_idle":lambda r:r.kind == "IDLE" and r.base.rank == 2,
        "max_idle":lambda r:r.kind == "IDLE" and r.base.rank == 42,
    }
    return {key:next(i for i,r in enumerate(catalogue.requests) if test(r))
            for key,test in tests.items()}


def consumer_probes(catalogue,chosen):
    """Actual coefficient programs, with the enormous payload scan explicit."""
    from cardinal_counts import Count
    from catalogue import Specifications
    from check_support import audit,no_decode
    from consumer import Consumer
    from directory import Context
    from numeric import selected_page
    import oracle
    import packet_engine
    from records import Fields,Program,Tape
    from scheduler import complete
    from words import Arena,Ring
    specifications=Specifications(catalogue)
    arena,indices=Arena(3),Arena(8)
    mod=arena.input(3)
    ring=Ring(mod)
    context=Context(ring,catalogue.codes)
    size,depth=indices.input(65),indices.input(0)
    program=Program.fixture(indices,arena,65,2,[],catalogue.codes.bits)
    consumer=Consumer(context,indices,program,specifications,size,depth)
    old=Tape()
    count=Count.literal(1)
    before,gap,suffix=(Count.literal(v) for v in (2,5,3))
    result=[]
    original=packet_engine.run_generator
    try:
        for name,identifier in chosen.items():
            request=catalogue.requests[identifier]
            common=request.kind != "IDLE"
            template=catalogue.template_for(identifier,common)
            low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
            spec=specifications.bind(identifier,common,low)
            need(spec.good,"new numerical Consumer good-form control")
            sampled=set()
            sentinel=Tape()

            def probe(source,events,layout,directory,prefixes,field_count,coefficient,**options):
                if False:
                    yield
                need(source is sentinel and layout.parent_size is size and layout.gap is gap,
                     "new Consumer complete input geometry")
                values=Fields(indices,arena,catalogue.codes.bits)
                values.tape=directory
                page,frame=selected_page(specifications.plan(spec.code),ring,indices,program,
                                        values,specifications,spec.code)
                try:
                    for event in events:
                        if event.kind != "add" or event.request.kind in sampled:
                            continue
                        actual=coefficient(directory,event.request)
                        expected=page.evaluate(event.request)
                        need(ring.raw.compare(actual,expected) == 0,
                             "new bound coefficient callback agrees with numeric page")
                        arena.free_many(actual,expected)
                        sampled.add(event.request.kind)
                        if len(sampled) == 2:
                            break
                finally:
                    events.close()
                    page.close()
                    indices.free(page.columns)
                    frame.close()
                return "bound-source-only-consumer-probe"

            packet_engine.run_generator=probe
            with no_decode():
                observed=complete(consumer.apply(sentinel,identifier,common,low,old,count,
                                                  before,gap,suffix))
            need(observed == "bound-source-only-consumer-probe"
                 and sampled == {"adapter","child"},"both new Consumer coefficient junctions")
            result.append({"name":name,"request":identifier,"kind":request.kind,
                           "rank":request.base.rank,"common":common,
                           "callbacks":sorted(sampled),"full_payload_executed":False})
            sentinel.clear()
    finally:
        packet_engine.run_generator=original
        old.clear()
        program.tape.clear()
        for value in (count,before,gap,suffix):
            value.close()
        context.close()
        ring.close()
        arena.free(mod)
        indices.free_many(size,depth)
    audit(arena)
    audit(indices)
    return result


def route_probes(catalogue,chosen):
    from driver import compile_owner,inverse_chart
    import oracle
    from sources import identity,product
    common=tuple(map(tuple,oracle.eye(64)))
    probes=[]
    for name in ("retired_carrier_rank7","advanced_source50","partial_terminal","short_idle"):
        request=catalogue.requests[chosen[name]]
        matrix=catalogue.chart_matrix(request.chart)
        need(product(matrix,tuple(zip(*matrix))) == identity(64),"actual route chart orthogonality")
        inverse=inverse_chart(matrix)
        need(inverse == tuple(zip(*matrix)),"actual inverse route is the dyadic transpose")
        native,forward,backward=compile_owner(matrix,common,catalogue.codes)
        need(forward.chart == matrix and backward.chart == inverse
             and forward.target_low == common and backward.target_low == native,
             "actual source route normal-form binding")
        probes.append({"name":name,"chart_key":request.chart.key,
                       "forward_route_sha256":digest([[str(x) for x in row] for row in forward.chart]),
                       "inverse_route_sha256":digest([[str(x) for x in row] for row in backward.chart]),
                       "inverse_is_transpose":True,"exact_low_packet_return":True})
    return probes


def threshold_probes(candidate,baseline,*,use_address_cache=True):
    """Walk every actual trace event, with checker-only pure-address caching."""
    from dataclasses import fields,is_dataclass
    from catalogue import Specifications
    from check_support import audit,inspect_count,no_decode
    from numeric import Geometry
    import oracle
    from trace import execute
    from words import Arena,Word

    # Full ordered traces obtained from the uncached published caller.py,
    # SHA256 ed95651869d1631ab2760ac1179c2497ef2eb0e241abfb45ef893c6180713d96
    # at commit 8bb569889d4a8b4707178a50eccd93f8c23593ec. Both modes below
    # independently regenerate every event; the cache only saves pure arithmetic.
    golden={
        ("candidate",576):(89354,177696,
            {"add":89037,"atom_swap":252,"enter":1,"return":1,"sign":63},
            "48adaf800f4505cc292949f6a691cac61c34ba6a4d73f168679cadbced215514"),
        ("candidate",640):(98723,197440,
            {"add":98720,"enter":1,"invoke":1,"return":1},
            "77d5a2846b0d75efe3642c01e1bc098df4548cdc985f6c3b8b3ee8d575eccd6f"),
        ("baseline",640):(96922,192880,
            {"add":96620,"atom_swap":240,"enter":1,"return":1,"sign":60},
            "5b70978fe85a68bdffb8d193d6007976bcfdd64f7a6bccb0e92089d71523e143"),
        ("baseline",704):(106087,212168,
            {"add":106084,"enter":1,"invoke":1,"return":1},
            "2a36ad722cbc14879fe4e72c45cf17bc6fd4800fa9811ad30fa828247dd14e9b"),
    }

    class FixtureGeometry(Geometry):
        """Memoize only this finite fixture's unchanged Geometry.point calls.

        Keys contain both complete encoded input words, the row and dimension.
        The retained routine executes on every distinct input. Hits copy its
        saved encoded result into a fresh owned register. This checker helper
        is never installed on a production Consumer, Driver or recursive Frame.
        """
        def __init__(self,*args):
            super().__init__(*args)
            self.points={}
            self.point_calls=0
            self.point_inputs=set()

        def point(self,field,column):
            need(self.columns.head == column.head == 1,
                 "canonical threshold fixture address inputs")
            extent,coordinate=bytes(self.columns.cells),bytes(column.cells)
            key=(self.plan.dimension,field,extent,coordinate)
            self.point_calls+=1
            self.point_inputs.add(key)
            if not use_address_cache or key not in self.points:
                value=super().point(field,column)
                need(self.columns.head == column.head == value.head == 1
                     and bytes(self.columns.cells) == extent
                     and bytes(column.cells) == coordinate,
                     "unchanged threshold address oracle preserves its inputs")
                if not use_address_cache:
                    return value
                self.points[key]=value
            value=self.points[key]
            need(value.head == 1 and value.slot in self.index.live,
                 "owned canonical cached threshold address")
            result=self.index.copy(value)
            need(result is not value and result.head == 1
                 and bytes(result.cells) == bytes(value.cells),
                 "fresh exact threshold address copy")
            return result

        def close(self):
            for value in self.points.values():
                self.index.free(value)
            self.points.clear()
            super().close()

    reports=[]
    identifiers={
        "candidate":selected_requests(candidate)["retired_carrier_rank7"],
        "baseline":next(i for i,r in enumerate(baseline.requests) if r.kind == "MOVE"
                       and r.stage == 0 and r.role == 469 and r.old_frame == 52 and r.new_frame == 517),
    }
    for name,parent in (("candidate",576),("candidate",640),("baseline",640),("baseline",704)):
        catalogue=candidate if name == "candidate" else baseline
        identifier=identifiers[name]
        specifications=Specifications(catalogue)
        template=catalogue.template_for(identifier,True)
        low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
        spec=specifications.bind(identifier,True,low)
        need(spec.good,"threshold trace good-form source")
        plan=specifications.plan(spec.code)
        indices=Arena(12)
        columns,depth=indices.input(parent//64),indices.zero()
        geometry=FixtureGeometry(plan,indices,columns,depth,spec.code,object())
        signature=sha256()
        counts=Counter()
        initial=(bytes(geometry.columns.cells),bytes(geometry.depth.cells),
                 geometry.plan.dimension,geometry.plan.rank)

        def normalize(value):
            if value is geometry.parent_identity:
                return ["exact_fixture_parent"]
            if isinstance(value,Word):
                need(value.arena is indices and value.slot in indices.live,
                     "all emitted words belong to the exact threshold arena")
                need(value.head == 1,"all emitted word heads canonical")
                return ["word",value.head,bytes(value.cells).hex()]
            if value is None or isinstance(value,(bool,int,str)):
                return value
            if isinstance(value,(tuple,list)):
                return [normalize(x) for x in value]
            if is_dataclass(value):
                return [type(value).__name__,[[f.name,normalize(getattr(value,f.name))]
                                             for f in fields(value)]]
            raise ValueError("unrecognized emitted trace payload "+type(value).__name__)

        signature.update(canonical({
            "plan":normalize(geometry.plan),
            "columns":normalize(geometry.columns),
            "depth":normalize(geometry.depth),
            "source_code":geometry.source_code,
        })+b"\n")
        entered,invoked,returned=[],[],[]
        try:
            with no_decode():
                for event in execute(geometry):
                    need(event.parent_identity is None
                         or event.parent_identity is geometry.parent_identity,
                         "exact normalized emitted parent identity")
                    # Consume every mutable word before the iterator resumes.
                    signature.update(canonical(normalize(event))+b"\n")
                    counts[event.kind]+=1
                    if event.child_kind != "good":
                        continue
                    if event.kind == "enter":
                        entered.append(inspect_count(event.width))
                    elif event.kind == "invoke":
                        invoked.append(inspect_count(event.width))
                    elif event.kind == "return":
                        returned.append(inspect_count(event.width))
            width=template.rank*(parent//64)
            need(entered == returned == [width]
                 and invoked == ([width] if width >= 64 else []),
                 "actual changed child threshold")
            need(initial == (bytes(geometry.columns.cells),bytes(geometry.depth.cells),
                             geometry.plan.dimension,geometry.plan.rank),
                 "unchanged threshold geometry")
            need((sum(counts.values()),geometry.point_calls,dict(counts),
                  signature.hexdigest()) == golden[name,parent],
                 "complete uncached-reference threshold trace")
            need(len(geometry.point_inputs) == 128*(parent//64),
                 "complete threshold address input census")
            reports.append({"word":name,"parent_width":parent,"request":identifier,
                            "rank":template.rank,"child_width":width,
                            "internal_invocations":len(invoked),"literal_trace_executed":True,
                            "full_trace":{
                                "events":sum(counts.values()),
                                "event_kinds":dict(sorted(counts.items())),
                                "ordered_full_event_sha256":signature.hexdigest(),
                                "point_calls":geometry.point_calls,
                                "distinct_point_inputs":len(geometry.point_inputs)}})
        finally:
            geometry.close()
            indices.free_many(columns,depth)
        audit(indices)
    return reports


def new_rank7_frame(catalogue,identifier):
    """Actual child_call/Frame protocol, with a labelled tiny child body."""
    from cardinal_counts import Count
    from catalogue import Specifications
    from check_support import audit,bits,inspect_count,no_decode
    from directory import Context,append_tape
    from layout import Layout
    import node
    from numeric import Geometry
    import oracle
    from packet import read_prefix
    from records import Fields,Program,Tape
    from recursive_call import child_call
    from scheduler import complete
    from trace import Event
    from words import Arena,BLANK,Ring
    specifications=Specifications(catalogue)
    template=catalogue.template_for(identifier,True)
    need(template.rank == 7,"new rank7 Frame request")
    low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(template.preparation,3),3)))
    spec=specifications.bind(identifier,True,low)
    need(spec.good,"new rank7 Frame good normal form")
    indices,arena=Arena(11),Arena(3)
    modulus=arena.input(3)
    ring=Ring(modulus)
    context=Context(ring,catalogue.codes)
    size,depth=indices.input(640),indices.zero()
    program=Program.fixture(indices,arena,640,2,[],catalogue.codes.bits)
    root=node.SelectedNode(context,indices,program,size,depth,catalogue,specifications)
    topology=root.topology
    need(topology is catalogue._recursive_caller_topology,"root actual provider topology")
    common_call=topology.call(0,0)
    high=[[0]*64 for _ in range(64)]
    field=Fields.fixture(indices,arena,[(spec.code,high)],catalogue.codes.bits)
    directory=Tape()
    append_tape(field.tape,directory)
    append_tape(field.tape,directory)
    directory.rewind()
    field.tape.clear()
    prefixes,stock,before,gap,suffix=(Count.literal(x) for x in (2,11,2,5,3))
    field_count=indices.input(1)
    source=Tape()
    payload=bytes((i*7 ^ i//3)&1 for i in range(23))
    for bit in payload:
        source.append(bit)
    source.rewind()
    saved_source,saved_directory,saved_program=map(lambda t:bytes(t.cells),(source,directory,program.tape))
    protected_indices,protected_residues=set(indices.live),set(arena.live)
    original=node.SelectedNode.run_generator
    frames=[]
    observations=[]

    def controlled(self,current,old,count,unused,b,g,s,observe=None):
        if False:
            yield
        frames.append(self)
        need(self.topology is topology and self.topology.call(0,0) is common_call
             and self.consumer.specifications is specifications,
             "new rank7 topology and catalogue propagate through actual Frame")
        need(self.indices is not indices and self.context.arena is not arena,
             "new rank7 separate frame banks")
        need(inspect_count(self.parent_size) == 70 and inspect_count(self.depth) == 1,
             "new rank7 actual internal child width/depth")
        need(unused is stock and inspect_count(unused) == 11 and inspect_count(count) == 2,
             "fresh U separate from complete high-prefix count")
        need(tuple(inspect_count(x) for x in (b,g,s)) == (2,5*3**1140,3),
             "new rank7 ordered spectator extents")
        root_size,unit,root_depth=self.program.root()
        need((inspect_count(root_size),inspect_count(unit),inspect_count(root_depth)) == (640,2,1),
             "new rank7 preserved root coefficient program")
        self.indices.free_many(root_size,root_depth)
        self.context.arena.free(unit)
        slot=self.indices.input(1)
        metadata,previous,generated=self.program.step(slot)
        need(metadata == (0,spec.code,7,0,0,0)
             and (inspect_count(previous),inspect_count(generated)) == (640,70),
             "new rank7 exact generated child descriptor")
        self.indices.free_many(slot,previous,generated)
        old.rewind()
        for _ in range(2):
            prefix=read_prefix(old,self.depth)
            need(bits(prefix) == bits(directory)[:len(bits(directory))//2],
                 "all physical frozen-prefix ordinals retained")
            prefix.clear()
        need(old.read() == BLANK,"complete two-prefix directory")
        old.rewind()
        output=Tape()
        for bit in reversed(bits(current)):
            output.append(bit)
        output.rewind()
        observations.append({"depth":1,"width":70,"prefixes":2,"stock":11,
                             "before":2,"gap":"5*3^1140","suffix":3,
                             "same_catalogue":True,"same_topology":True})
        return output

    node.SelectedNode.run_generator=controlled
    columns=indices.input(10)
    geometry=Geometry(specifications.plan(spec.code),indices,columns,depth,spec.code,program)
    leading=Count.product(stock,before)
    layout=Layout(geometry,size,ring,3,leading,gap,suffix)
    operands=[indices.input(x) for x in (0,1210,70,1)]
    event=Event("invoke",operands[0],operands[1],width=operands[2],depth=operands[3],
                child_kind="good",source_code=spec.code,parent_identity=program)
    output=None
    try:
        with no_decode():
            output=complete(child_call(root.consumer,source,event,layout,directory,
                                      prefixes,field_count,stock,before))
        need(bits(output) == bytes(reversed(payload)),"new rank7 controlled child return")
        need(bytes(source.cells) == saved_source and bytes(directory.cells) == saved_directory
             and bytes(program.tape.cells) == saved_program,"new rank7 preserved caller inputs")
        need(source.head == output.head == directory.head == program.tape.head == 1,
             "new rank7 caller head return")
        for frame in frames:
            audit(frame.indices)
            audit(frame.context.arena)
            need(not bits(frame.program.tape),"new rank7 child program cleared")
    finally:
        node.SelectedNode.run_generator=original
        if output is not None:
            output.clear()
        layout.close()
        geometry.close()
        leading.close()
        indices.free_many(columns,*operands)
    need(indices.live == protected_indices and arena.live == protected_residues,
         "new rank7 no retained child numerical storage")
    source.clear()
    directory.clear()
    program.tape.clear()
    for value in (prefixes,stock,before,gap,suffix):
        value.close()
    indices.free_many(size,depth,field_count)
    context.close()
    ring.close()
    arena.free(modulus)
    audit(indices)
    audit(arena)
    return {"request":identifier,"rank":7,"parent_width":640,"child_width":70,
            "actual_Frame_instances":len(frames),"handoffs":observations,
            "controlled_payload_bits":23,"full_selected_GL64_payload_executed":False,
            "source_and_directory_preserved":True,"private_frame_banks_closed":True,
            "scope":"Actual unchanged child_call, descriptor, Frame, SelectedNode constructor and cleanup; tiny test-only child body."}


def binding_controls(catalogue):
    from copy import copy
    from dataclasses import replace
    from control import LocalState
    import node
    failures=[]

    def reject(name,run,expected):
        try:
            run()
        except ValueError as error:
            need(str(error) == expected,"wrong caller control rejection "+name)
            failures.append({"defect":name,"rejection":expected})
        else:
            raise ValueError("caller control unexpectedly accepted "+name)

    def missing_topology():
        unbound=copy(catalogue)
        del unbound._recursive_caller_topology
        node.selected_topology(unbound).call(0,0)
    reject("omitted_new_topology_propagation",missing_topology,"complete selected staged roles")

    call=catalogue._recursive_caller_topology.call(0,0)
    opening=next(i for i,e in enumerate(call.events) if e[0] == 2)

    def wrong_private():
        events=list(call.events)
        altered=list(events[opening])
        altered[2]=661
        events[opening]=tuple(altered)
        state=LocalState(replace(call,events=tuple(events)))
        for position in range(opening+1):
            state.accept(position)
    reject("old_private_index661",wrong_private,"fresh transported COPY interval")

    def wrong_terminal():
        event=catalogue.template["calls"][0]
        altered=dict(event,owners=list(event["owners"]))
        family,route=altered["owners"][462]
        changed=list(route)
        # Keep the same mixed-width axes but substitute a chart whose terminal
        # frame is different, detected before any route can be compiled.
        other=next(r for _,r in event["owners"][222:]
                   if r[0] == "hosted" and r[-1] != route[-1] and r[3] == 8)
        changed[-1]=other[-1]
        altered["owners"][462]=[family,changed]
        catalogue.owner_chart(altered,462)
    reject("wrong_terminal_owner_chart",wrong_terminal,"actual mixed terminal support")

    def inside_copy():
        events=list(call.events)
        # Insert an actual later MOVE immediately after a COPY opens. The
        # retained lifetime guard rejects it before any payload query executes.
        move=next(e for e in events[opening+1:] if e[0] == 0)
        events[opening+1]=move
        requests=list(call.requests)
        requests[opening+1]=0
        state=LocalState(replace(call,events=tuple(events),requests=tuple(requests)))
        for position in range(opening+2):
            state.accept(position)
    reject("source_packet_moved_inside_COPY",inside_copy,"MOVE frame and lifetime")
    return failures


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--scope",choices=("catalogue","literal","consumer","thresholds","complete"),
                        default="complete")
    parser.add_argument("--uncached-thresholds",action="store_true",
                        help="replay all four threshold traces without address caching")
    args=parser.parse_args()
    if args.uncached_thresholds and args.scope != "thresholds":
        parser.error("--uncached-thresholds requires --scope thresholds")
    catalogue,loader,provenance=build_provider()
    baseline=type(catalogue)(3,"baseline")
    report={"status":"PASS_BOUND_CALLER_CATALOGUE","provenance":provenance,
            "catalogue":catalogue.receipt(),"matched_baseline_catalogue":baseline.receipt(),
            "no_new_kappa":True,
            "scope":"New finite provider bound to unchanged generic logical caller; p=1 contracts remain explicit."}
    if args.scope in ("literal","consumer","complete"):
        report["literal_binding"]=literal_census(catalogue)
        report["split_bases"]=split_basis_census(catalogue)
        report["status"]="PASS_COMPLETE_BOUND_CALLER_LITERAL_CENSUS"
    if args.scope in ("consumer","complete"):
        chosen=selected_requests(catalogue)
        report["consumer_probes"]=consumer_probes(catalogue,chosen)
        report["route_probes"]=route_probes(catalogue,chosen)
    if args.scope == "thresholds":
        report["threshold_probes"]=threshold_probes(
            catalogue,baseline,use_address_cache=not args.uncached_thresholds)
        report["status"]="PASS_BOUND_CALLER_COMPLETE_THRESHOLD_TRACES"
    elif args.scope in ("consumer","complete"):
        report["threshold_probes"]=threshold_probes(catalogue,baseline)
        report["status"]="PASS_BOUND_CALLER_CONSUMER_AND_THRESHOLD_PROBES"
    if args.scope == "complete":
        import check_recursion
        report["recursive_rank42_frame_probe"]=check_recursion.frame_handoff(catalogue)
        report["recursive_new_rank7_frame_probe"]=new_rank7_frame(catalogue,chosen["retired_carrier_rank7"])
        report["binding_controls"]=binding_controls(catalogue)
        report["status"]="PASS_NEW_SOURCE_BOUND_LOGICAL_RECURSIVE_CALLER"
    report["loaded_frozen_modules"]=dict(sorted(loader.loaded.items()))
    print(json.dumps(report,sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
