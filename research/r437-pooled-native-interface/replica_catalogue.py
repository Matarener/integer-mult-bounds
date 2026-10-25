"""Explicit replica-indexed request interface for the frozen pooled R437 source.

Retains canonical Base/Chart/Template/LowCodes semantics. No physical execution
or supplier admission is implied. Apache-2.0; Chris R, OpenAI Codex assistance.
"""
from bisect import bisect_right
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, replace
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys

import adapter
import pooled_compiler

HERE = Path(__file__).resolve().parent
VERSION = 'pooled-replica-request-v1'
need = adapter.require

@dataclass(frozen=True)
class ReplicaRequest:
    replica: int
    request: object

    def __getattr__(self, name):
        return getattr(self.request, name)

    def record(self):
        return [VERSION, self.replica] + self.request.record()

    @property
    def key(self):
        r = self.request
        return (r.kind, r.stage, self.replica, r.role if r.kind == 'IDLE' else r.position)

class Requests(Sequence):
    """Full 903456-site vocabulary, constructed lazily without symmetry quotient."""
    def __init__(self, catalogue, prototypes, idle_records):
        self.catalogue = catalogue
        self.prototypes = [tuple(r for r in prototypes if r.kind != 'IDLE' and r.stage == s)
                           for s in range(9)]
        self.positions = [{r.position: j for j, r in enumerate(rows)} for rows in self.prototypes]
        self.starts = [0]
        for rows in self.prototypes:
            self.starts.append(self.starts[-1] + 32 * len(rows))
        self.idles = []
        self.idle_lookup = {}
        module = sys.modules[type(catalogue).__module__]
        for child, replica, cp, family, used, rank in idle_records:
            event = catalogue.idles[child]
            axes = catalogue.pending(child)[used:]
            need(len(axes) == rank, 'literal pooled idle suffix')
            base = module.Base('idle', axes, rank)
            base = catalogue.bases.setdefault(base.key, base)
            request = module.Request('IDLE', child, child, cp, family,
                                     event['source_level'], event['target_level'], base,
                                     module.Chart('family', cp % 111), 'owner')
            wrapped = ReplicaRequest(replica, request)
            self.idle_lookup[wrapped.key] = self.starts[-1] + len(self.idles)
            self.idles.append(wrapped)

    def __len__(self):
        return self.starts[-1] + len(self.idles)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError('request indices are explicit integers')
        if index < 0:
            index += len(self)
        if not 0 <= index < len(self):
            raise IndexError(index)
        if index >= self.starts[-1]:
            return self.idles[index - self.starts[-1]]
        stage = bisect_right(self.starts, index) - 1
        replica, slot = divmod(index-self.starts[stage], len(self.prototypes[stage]))
        old = self.prototypes[stage][slot]
        call = self.catalogue.template['calls'][32*stage+replica]
        chart = self.catalogue.owner_chart(call, old.role)
        if old.kind == 'MOVE':
            request = replace(old, family=call['owners'][old.role][0], chart=chart)
        else:
            request = replace(old, source_chart=chart)
        return ReplicaRequest(replica, request)

    def identifier(self, kind, stage, replica, position):
        need(0 <= replica < 32, 'physical caller replica')
        if kind == 'IDLE':
            return self.idle_lookup[kind, stage, replica, position]
        slot = self.positions[stage][position]
        need(self.prototypes[stage][slot].kind == kind, 'physical request kind')
        return self.starts[stage] + replica*len(self.prototypes[stage]) + slot

class ReplicaTopology:
    """Changed interface: IDLE enumeration takes the replica explicitly.

    Deliberately exposes no legacy `idles` table. Existing compile_node requires
    an explicit consumer adaptation; feeding it expanded IDLE IDs is unsafe.
    """
    replicas, pairs, ports, families, stride = 32, 4, 111, 28416, 888

    def __init__(self, catalogue, old_topology):
        self.catalogue = catalogue
        self.schedule = tuple(catalogue.template['schedule'])
        self.old_topology = old_topology
        self.idle_groups = {}
        for index, request in enumerate(catalogue.requests.idles, catalogue.requests.starts[-1]):
            self.idle_groups.setdefault((request.stage,request.replica), []).append(index)

    def idle_identifiers(self, child, replica):
        need(0 <= replica < 32, 'physical idle replica')
        return tuple(self.idle_groups.get((child,replica), ()))

    def idle_family(self, identifier, replica):
        request = self.catalogue.requests[identifier]
        need(request.kind == 'IDLE' and request.replica == replica, 'exact idle replica binding')
        return request.family

    @lru_cache(None)
    def call(self, stage, replica):
        import topology
        source = self.catalogue.template['calls'][32*stage+replica]
        old = self.old_topology.call(stage,replica)
        owners = tuple(topology.Owner(family, self.catalogue.owner_chart(source,role))
                       for role,(family,route) in enumerate(source['owners']))
        identifiers = tuple(self.catalogue.requests.identifier('MOVE' if event[0] == 0 else 'COPY',
                                                               stage,replica,position)
                            if event[0] in (0,2) else None
                            for position,event in enumerate(old.events))
        need(len(owners) == 659, 'actual pooled role inventory')
        return topology.Call(stage,replica,owners,old.start,old.end,old.events,identifiers,old.reverse)

    def matrix(self, chart):
        return self.catalogue.chart_matrix(chart)

    def family(self, replica, pair, side, port):
        return self.old_topology.family(replica,pair,side,port)

def load():
    catalogue, old_topology = adapter.load()
    proposal = json.loads((HERE/'inputs/moves.json').read_bytes())
    pooled, profile, idles = pooled_compiler.compile_owners(catalogue.template, proposal['moves'])
    prototypes = catalogue.requests
    old_bits = catalogue.codes.bits
    # Preserve the literal unpooled topology as a recipe-only predecessor.
    import copy
    old_topology.catalogue = copy.copy(catalogue)
    catalogue.template = pooled
    catalogue.bases = dict(catalogue.bases)
    catalogue.requests = Requests(catalogue, prototypes, idles)
    catalogue.profile = profile
    from low_codes import LowCodes
    catalogue.codes = LowCodes(catalogue.q,64,len(catalogue.requests))
    # Reject the replica-blind public identifier entry point instead of retaining
    # an accidentally usable old dictionary. Requests.identifier is the new API.
    catalogue.identifiers = {}
    catalogue.identifier = catalogue.requests.identifier
    catalogue.semantic_key = lambda request: request.key
    catalogue.erase_guards = tuple((stage,replica,*rest) for stage,*rest in catalogue.erase_guards for replica in range(32))
    catalogue.source_identity = codebook_identity(catalogue)
    catalogue.old_code_bits = old_bits
    catalogue.charts = {catalogue.owner_chart(call,role) for call in pooled['calls'] for role in range(659)}
    catalogue.charts.update(r.chart for r in catalogue.requests.idles)
    catalogue.charts.update(r.chart for r in prototypes if r.kind == 'COPY')
    catalogue.receipt = lambda: receipt(catalogue)
    return catalogue, ReplicaTopology(catalogue, old_topology)


@dataclass(frozen=True)
class SourceHandle:
    schema: str
    identity: str
    code: int


def source_handle(catalogue, identifier, common, low):
    return SourceHandle(VERSION, catalogue.source_identity, catalogue.codes.encode(identifier,common,low))


def resolve_handle(catalogue, specifications, handle):
    need(isinstance(handle,SourceHandle) and handle.schema == VERSION and
         handle.identity == catalogue.source_identity, 'exact pooled source codebook identity')
    need(getattr(specifications,'catalogue',None) is catalogue, 'exact Specifications codebook context')
    return specifications[handle.code]


def receipt(catalogue):
    from catalogue import canonical
    digest = sha256()
    kinds = Counter()
    for request in catalogue.requests:
        kinds[request.kind] += 1
        digest.update((canonical(request.record())+'\n').encode())
    return {'physical_requests': len(catalogue.requests), 'replicas': 32,
            'request_kinds': dict(kinds), 'rank_histogram': dict(catalogue.profile),
            'ERASE_guards': len(catalogue.erase_guards), 'binding_sha256': digest.hexdigest(),
            'source_identity': catalogue.source_identity, 'schema': VERSION}


def codebook_identity(catalogue):
    import low_codes
    fields = [VERSION, catalogue.q, catalogue.dimension, len(catalogue.requests),
              catalogue.codes.bits, adapter.REQUEST_DIGEST,
              sha256((HERE/'inputs/moves.json').read_bytes()).hexdigest(),
              sha256(Path(low_codes.__file__).read_bytes()).hexdigest()]
    return sha256(json.dumps(fields,separators=(',',':')).encode()).hexdigest()
