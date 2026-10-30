"""Replica-indexed R437 native requests on the literal five-replica pools.

The matrices, chart constructors, residual specifications and physical runtime
are retained from the credited selected caller. This adapter replaces its
replica-symmetric request catalogue and topology with explicitly indexed ones.
It does not assert completion of the inherited all-size primitive contracts.
Apache-2.0. Substantial OpenAI assistance under the user's direction.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

HERE = Path(__file__).resolve().parent
SCOPE = HERE.parent
ROOT = HERE.parents[2]
PHYSICAL = ROOT / 'research/selected-bit-physical-caller'
INPUTS = SCOPE / 'sources/PR3647/research/bit-p111-r437-gl464-470-20261018'
POOL = SCOPE / 'geometry-search/pool35'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def lower_word(word, dimensions):
    """Independently lower the exact bitE8 record grammar to both native IRs.

    Follows the credited PR3647/export_records and global_k interfaces. This
    prevents a word override from retaining an unrelated template program.
    Every source/helper column and COPY lifetime is checked over F2 here;
    the separate native/interface checker still owns the all-frame proof.
    """
    V, R = word['v'], word['R']
    count = 2*V+R
    need((V,R,word['h']) == (111,437,8), 'unchanged R437 local role dimensions')
    zero = [i for i,r in enumerate(dimensions) if r == 0]
    need(len(zero) == 1, 'one zero frame')
    zero = zero[0]
    current, records = list(word['start']), []
    def move(role, frame):
        old = current[role]
        if old != frame:
            rank = dimensions[frame]-dimensions[old]
            need(rank > 0 and set(word['frames'][old]) <= set(word['frames'][frame]),
                 'positive nested complete-word transition')
            records.append((0,role,old,frame,rank,0))
            current[role] = frame
    def gates(section, phase):
        for frame,dst,sources in word[section]:
            for role in [dst]+list(sources):
                move(role,frame)
            for src in sources:
                records.append((1,dst,src,1,frame,phase))
    gates('D',1)
    gates('A',2)
    for ordinal,source in enumerate(word['ret']):
        frame=current[source]
        records.append((2,source,count,frame,zero,dimensions[frame]))
        for target,indices in enumerate(word['scatter']):
            if ordinal in indices:
                records.append((1,V+target,count,1,zero,3))
        records.append((3,source,count,frame,zero,0))
    gates('B',4)
    gates('C',5)
    for role,frame in enumerate(word['final']):move(role,frame)
    record_sha256=hashlib.sha256(b''.join(struct.pack('<6i',*r) for r in records)).hexdigest()
    programs, profiles, information = {}, {}, {}
    for reverse in (False,True):
        events=[];values=[1<<i for i in range(count)]+[0]
        cursor=list(word['final'] if reverse else word['start'])+[-1]
        opened=None;profile=Counter();copies=0
        dim=lambda f:8-dimensions[f] if reverse else dimensions[f]
        for op,x,y,c,f,z in (reversed(records) if reverse else records):
            if op == 0:
                old,new=(c,y) if reverse else (y,c)
                need(cursor[x] == old and dim(new)-dim(old) == f and f > 0,
                     'lowered native MOVE current frame')
                cursor[x]=new;profile[f]+=1
                events.append([0,x,old,new,f,int(reverse)])
            elif op == 1:
                need(cursor[x] == cursor[y] == f and x != y and x < count and x != opened,
                     'lowered ADD common frame and immutable COPY source')
                need(y < count or opened is not None, 'lowered private source lifetime')
                if c&1:values[x]^=values[y]
                events.append([1,x,y,-c if reverse else c,f,int(reverse)])
            elif op == (3 if reverse else 2):
                need(opened is None and y == count and cursor[x] == c and values[count] == 0,
                     'lowered COPY opens clean private payload')
                rank=abs(dim(c)-dim(f))
                need(rank == 7 and z == (0 if reverse else rank), 'retained seven-axis COPY contract')
                opened=x;cursor[count]=f;values[count]=values[x]
                profile[rank]+=1;copies+=1
                events.append([2,x,count,c,f,rank,int(reverse)])
            else:
                need(op == (2 if reverse else 3) and opened == x and y == count and
                     cursor[x] == c and cursor[count] == f and values[count] == values[x],
                     'lowered private ERASE matches its actual source')
                opened=None;cursor[count]=-1;values[count]=0
                events.append([3,x,count,c,f,z,int(reverse)])
        wanted=[(1<<i)^((1<<(i-V)) if V<=i<2*V else 0) for i in range(count)]
        need(values == wanted+[0] and opened is None and copies == 9,
             'both complete local words restore all arbitrary dirty columns')
        need(cursor[:count] == (word['start'] if reverse else word['final']),
             'both complete local endpoint frame lists')
        key='reverse' if reverse else 'forward'
        programs[key]=events;profiles[key]=profile
        information[key]={'events':len(events),'copies':copies,'paid_requests':sum(profile.values()),
                          'profile':dict(sorted(profile.items())),
                          'source_record_sha256':record_sha256,
                          'sha256':hashlib.sha256(canonical(events).encode()).hexdigest()}
    need(profiles['forward'] == profiles['reverse'], 'equal complete local profiles')
    return programs,profiles['forward'],information


def load(q=3, template_path=None, word_path=None, word_content_sha256=None):
    sys.path.insert(0, str(PHYSICAL))
    import loader
    loader.activate()
    import catalogue as retained
    import topology as retained_topology
    from low_codes import LowCodes

    @dataclass(frozen=True)
    class ReplicaRequest(retained.Request):
        replica: int = -1

        def record(self):
            return super().record() + [self.replica]

    class ReplicaCatalogue(retained.Catalogue):
        private = 659
        replica_stride = 888

        def __init__(self):
            self.q = q
            self.old = module('pool35_retained_frame_arithmetic',
                              ROOT / 'research/pr589-five-helper-hosting/verify.py')
            expected = read(INPUTS / 'EXPECTED.json')
            parent_path = INPUTS / 'data/r0042/R437-COMPOSED-WORD.json.gz'
            parent_raw = gzip.decompress(parent_path.read_bytes())
            need(hashlib.sha256(parent_raw).hexdigest() == expected['word_content_sha256'],
                 'exact R437 native word content')
            parent_word = json.loads(parent_raw)
            if word_path is None:
                need(word_content_sha256 in (None,expected['word_content_sha256']),
                     'default native word uses the retained source pin')
                actual_word_path,word_raw = parent_path,parent_raw
            else:
                need(isinstance(word_content_sha256,str) and len(word_content_sha256)==64,
                     'explicit word override requires its exact decompressed SHA256')
                actual_word_path=Path(word_path)
                raw=actual_word_path.read_bytes()
                word_raw=gzip.decompress(raw) if actual_word_path.suffix=='.gz' else raw
                need(hashlib.sha256(word_raw).hexdigest()==word_content_sha256,
                     'exact changed native word content pin')
            self.word = json.loads(word_raw)
            baseline = read(INPUTS / 'generated/GLOBAL-TEMPLATE.json.gz')
            self.template = read(Path(template_path) if template_path else POOL / 'GLOBAL-TEMPLATE.json.gz')
            t = self.template
            self.replicas, self.families = t['replicas'], t['live']
            need((t['m'], t['stages'], self.replicas, self.families) == (64, 9, 35, 31080),
                 'literal T35 native catalogue domain')
            need(t['schedule'] == baseline['schedule'], 'unchanged complete global controller')
            for key in ('v','R','h','form','lines'):
                need(self.word[key] == parent_word[key], 'unchanged native interface property '+key)
            need(self.word['R'] == 437 and len(t['calls']) == 9*self.replicas,
                 'complete R437 call domain')
            self.geometry = read(INPUTS / 'data/GEOMETRY.json')
            rows = [self.old.projection([self.word['lines'][i] for i in frame])
                    for frame in self.word['frames']]
            self.projectors = [p for p, _ in rows]
            self.dimensions = [rank for _, rank in rows]
            parent_rows = [self.old.projection([parent_word['lines'][i] for i in frame])
                           for frame in parent_word['frames']]
            for boundary in ('start','final'):
                need(len(self.word[boundary]) == len(parent_word[boundary]) == 659,
                     'complete native boundary inventory')
                for new,old in zip(self.word[boundary],parent_word[boundary]):
                    need(rows[new] == parent_rows[old], 'unchanged exact endpoint projector')
            need(all(self.dimensions[self.word['start'][i]] == 0 and
                     self.dimensions[self.word['final'][i]] == 8 for i in range(222,659)),
                 'literal all-width8 helper inventory retained')
            actual_programs,self.local_profile,self.local_word_info=lower_word(self.word,self.dimensions)
            need(t['local_programs'] == actual_programs, 'template binds both freshly lowered actual native words')
            need(t['source_record_sha256']==self.local_word_info['forward']['source_record_sha256'],
                 'template native export record source hash')
            if word_path is None:
                need(actual_programs == baseline['local_programs'], 'default R437 source IR positive control')
            self.actual_word_content_sha256=hashlib.sha256(word_raw).hexdigest()
            self.actual_word_path=str(actual_word_path)
            self.idles = {e['idx']: e for e in t['schedule'] if e['kind'] == 'idle'}
            self.requests, self.bases, self.charts, self.erase_guards = [], {}, set(), []
            self.call_offsets, self.local_ordinals, self.idle_ids = {}, {}, defaultdict(list)
            self.profile = Counter()
            self._bind_replicas(baseline)
            self.codes = LowCodes(q, 64, len(self.requests))

        def _append(self, request):
            need(0 <= request.replica < self.replicas, 'explicit native request replica')
            super()._append(request)
            self.profile[request.base.rank] += 1

        @lru_cache(None)
        def base(self, a, b):
            # The rational transition depends only on its two fixed frame IDs.
            return super().base(a, b)

        @staticmethod
        def semantic_key(request):
            return (request.kind, request.stage, request.replica,
                    request.role if request.kind == 'IDLE' else request.position)

        def _bind_replicas(self, baseline):
            t, occupancy = self.template, defaultdict(set)
            pair_at_stage = {e['stage']: e['pair'] for e in t['schedule']
                             if e['kind'] == 'local_cover_sweep'}
            for stage in range(9):
                reference = baseline['calls'][32*stage]
                for replica in range(self.replicas):
                    call = t['calls'][self.replicas*stage+replica]
                    need((call['stage'], call['replica'], call['pair'], call['orientation'], call['local_hash']) ==
                         (stage, replica, pair_at_stage[stage], reference['orientation'],
                          self.local_word_info[reference['orientation']]['sha256']),
                         'literal stage-replica source binding')
                    need(len(call['owners']) == self.private, 'all659 source target and helper owners')
                    for (family, route), (old_family, old_route) in zip(call['owners'][:222], reference['owners'][:222]):
                        need(route == old_route and family == old_family+888*replica,
                             'unchanged actual SOURCE and target owners')
                    for role, (family, route) in enumerate(call['owners'][222:], 222):
                        need(route[0] == 'hosted' and 0 <= family < self.families,
                             'absolute helper owner family')
                        _, child, offset, width = route
                        pair, capacity, stages = t['hosting']['windows'][str(child)]
                        need(stage in stages and pair != call['pair'] and (family % 888)//222 == pair,
                             'untouched chronological helper destination')
                        need(width == 8 and 0 <= offset and offset+8 <= capacity,
                             'complete native helper width')
                        axes = self.pending(child)[offset:offset+8]
                        need(not occupancy[child, family].intersection(axes),
                             'disjoint absolute helper axes')
                        occupancy[child, family].update(axes)
                    self.call_offsets[stage, replica] = len(self.requests)
                    opened, ordinals = None, {}
                    for position, event in enumerate(t['local_programs'][call['orientation']]):
                        op, role = event[:2]
                        if op == 0:
                            _, _, a, b, rank, _ = event
                            base = self.base(a, b)
                            need(base.rank == rank and opened is None,
                                 'native MOVE rank and lifetime')
                            ordinals[position] = len(ordinals)
                            self._append(ReplicaRequest('MOVE', stage, position, role,
                                call['owners'][role][0], a, b, base, self.owner_chart(call, role),
                                'owner', replica=replica))
                        elif op == 2:
                            _, _, temporary, a, b, rank, _ = event
                            base = self.base(a, b)
                            need(temporary == self.private and opened is None and base.rank == rank == 7,
                                 'native COPY rank and fresh private role')
                            opened = ReplicaRequest('COPY', stage, position, role, self.families,
                                a, b, base, retained.Chart('identity'), 'common',
                                self.owner_chart(call, role), replica)
                            ordinals[position] = len(ordinals)
                            self._append(opened)
                        elif op == 3:
                            _, _, temporary, a, b, _, _ = event
                            need(opened is not None and opened.role == role and temporary == self.private and
                                 opened.base == self.base(a, b), 'exact transported private ERASE binding')
                            self.erase_guards.append((stage, replica, position, opened.position, role, opened.base.key))
                            opened = None
                        else:
                            need(op == 1, 'closed local opcode')
                    need(opened is None, 'all private lifetimes closed')
                    old_ordinals = self.local_ordinals.setdefault(call['orientation'], ordinals)
                    need(old_ordinals == ordinals, 'replica-independent local event positions')
            self.local_request_count = len(self.requests)
            for child, event in self.idles.items():
                pending = tuple(self.pending(child))
                for replica in range(self.replicas):
                    for cp in range(222):
                        family = replica*888 + event['pair']*222 + cp
                        used = occupancy[child, family]
                        need(used == set(pending[:len(used)]), 'native occupied prefix')
                        axes = tuple(sorted(set(pending)-used))
                        if not axes:
                            continue
                        base = retained.Base('idle', axes, len(axes))
                        self.bases.setdefault(base.key, base)
                        identifier = len(self.requests)
                        self.idle_ids[child, replica].append(identifier)
                        self._append(ReplicaRequest('IDLE', child, child, cp, family,
                            event['source_level'], event['target_level'], base,
                            retained.Chart('family', cp % 111), 'owner', replica=replica))
            expected_profile=Counter({rank:9*self.replicas*count for rank,count in self.local_profile.items()})
            expected_profile.update(request.base.rank for request in self.requests[self.local_request_count:])
            need(self.profile == expected_profile and sum(self.profile.values()) == len(self.requests),
                 'every request counted once without a replica multiplier')
            need(sum(r*n for r, n in self.profile.items()) == 1977885,
                 'complete T35 native rank mass')
            need(2*max(self.profile)**2 < 64**2, 'native halving guard')

        def identifier(self, kind, stage, position, replica):
            need(kind in ('MOVE', 'COPY') and 0 <= stage < 9 and 0 <= replica < self.replicas,
                 'complete local semantic request key')
            call = self.template['calls'][self.replicas*stage+replica]
            identifier = self.call_offsets[stage, replica] + self.local_ordinals[call['orientation']][position]
            request = self.requests[identifier]
            need(self.semantic_key(request) == (kind, stage, replica, position),
                 'replica-indexed exact request lookup')
            return identifier

        def receipt(self):
            digest = hashlib.sha256()
            for request in self.requests:
                digest.update((canonical(request.record())+'\n').encode())
            return {'status': 'PASS_REPLICA_INDEXED_NATIVE_REQUEST_CATALOGUE',
                    'canonical_requests': len(self.requests), 'replicas': self.replicas,
                    'full_paid_requests': sum(self.profile.values()),
                    'request_kinds': dict(Counter(r.kind for r in self.requests)),
                    'base_labels': len(self.bases), 'chart_labels': len(self.charts),
                    'rank_histogram': dict(sorted(self.profile.items())),
                    'actual_word_content_sha256':self.actual_word_content_sha256,
                    'actual_local_programs':self.local_word_info,
                    'canonical_ERASE_guards': len(self.erase_guards),
                    'binding_sha256': digest.hexdigest()}

    class ReplicaTopology(retained_topology.SelectedTopology):
        def __init__(self, catalogue):
            self.catalogue = catalogue
            self.replicas, self.families = catalogue.replicas, catalogue.families
            self.schedule = tuple(catalogue.template['schedule'])
            self.idles = {child: tuple(i for replica in range(self.replicas)
                                     for i in catalogue.idle_ids[child, replica])
                          for child in catalogue.idles}
            self._validate_global()

        def idles_for(self, child, replica):
            need(child in self.catalogue.idles and 0 <= replica < self.replicas,
                 'explicit idle child and caller replica')
            return tuple(self.catalogue.idle_ids[child, replica])

        @lru_cache(None)
        def recipe(self, stage, replica):
            # Replica is mandatory: the retained one-argument method would
            # silently use32-based source indices and shared request IDs.
            call=self.call(stage,replica)
            return call.events,call.requests,call.start,call.end,call.reverse

        @lru_cache(None)
        def call(self, stage, replica):
            need(0 <= stage < 9 and 0 <= replica < self.replicas,
                 'explicit local stage and caller replica')
            source = self.catalogue.template['calls'][self.replicas*stage+replica]
            reverse = source['orientation'] == 'reverse'
            events = tuple(map(tuple, self.catalogue.template['local_programs'][source['orientation']]))
            identifiers = tuple(self.catalogue.identifier('MOVE' if event[0] == 0 else 'COPY',
                                 stage, position, replica) if event[0] in (0,2) else None
                                for position, event in enumerate(events))
            owners = tuple(retained_topology.Owner(family, self.catalogue.owner_chart(source, role))
                           for role, (family, route) in enumerate(source['owners']))
            word = self.catalogue.word
            start = tuple(word['final'] if reverse else word['start'])
            end = tuple(word['start'] if reverse else word['final'])
            need(len(owners) == len(start) == len(end) == 659, 'complete current native call')
            return retained_topology.Call(stage, replica, owners, start, end, events, identifiers, reverse)

        def idle_family(self, identifier, replica):
            request = self.catalogue.requests[identifier]
            need(request.kind == 'IDLE' and request.replica == replica,
                 'absolute idle owner belongs to the caller replica')
            return request.family

    catalogue = ReplicaCatalogue()
    return catalogue, ReplicaTopology(catalogue)
