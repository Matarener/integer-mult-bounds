#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable preparation, NOT YET RUN: fixed PR5713 causal/typed audit.

Modified from the historically executed local checker e2c42f6f...61aa3.
Only the portable data/custody interface and privacy wrapper are adapted.
Audit/causal/typing/parser core is retained exactly; see ADAPTATION.json.
No author imports, native provider, full-price replay or emitted WORD.
"""
import gzip


import hashlib


import io


import json


from fractions import Fraction


from pathlib import Path


import re


import sys


import time


HERE = Path(__file__).resolve().parent


OBJECT = 'pr5713-fixed-causal-typed715-on-original5684-v1'


LIMITS = {'aggregate_seconds': 150, 'child_seconds': 60, 'memory_mib': 512, 'runs': 1, 'controls': 0}


BOUNDS = {'expanded_bytes': 16777216, 'json_nodes': 500000, 'json_depth': 16,
          'string_characters': 256, 'integer_digits': 24, 'frames': 4096,
          'basis_vectors': 9, 'events': 40000, 'roles': 752, 'ledger_entries': 1024,
          'ledger_bytes': 524288, 'entry_bytes': 4096, 'output_bytes': 1048576,
          'metadata_file_bytes': 1048576, 'metadata_total_bytes': 8388608,
          'coefficient_digits': 24}


SUBJECT = {'publication_head': 'a5348f7143f95fe0046b92b96172e30763c7d731',
           'recipient': 715, 'tracked': [340, 525, 712, 715, 747],
           'cuts_before_original_events': [823, 14983],
           'anchors': [823, 11202, 13572, 13577, 13578, 13737, 14654, 14982, 14983],
           '340_no_write_interval': [14654, 14983],
           '340_nonblocking_provenance_interval': [11202, 14983],
           '747_no_write_interval': [13572, 13578],
           'causal_interval': [823, 14983],
           'skip_original_events': [13577, 13578],
           'retarget_original_MOVE': [14982, 715, 3, 396],
           'insertions': [[823, 715, 525, '1/4', 3], [823, 715, 712, '-1', 3],
                          [14983, 715, 525, '-1/4', 396], [14983, 715, 340, '1/4', 396]]}


REQUIRED = {'schema', 'public', 'initial', 'final', 'frames', 'program', 'live'}


OPTIONAL = {'ports', 'owned_fields'}


ARITY = {'MOVE': 5, 'INIT': 3, 'CLEAR': 3, 'SCALE': 4, 'ADD': 5, 'COPY': 5}


START = time.monotonic()


METADATA_BYTES = 0


BINDING_CONTEXT = None


class Unresolved(Exception):
    def __init__(self, reason, index=None, detail=None):
        self.reason, self.index, self.detail = reason, index, detail


class Falsified(Exception):
    def __init__(self, predicate, index, event, expected, actual):
        self.predicate, self.index, self.event = predicate, index, event
        self.expected, self.actual = expected, actual


class Incomplete(Exception):
    pass


def need(ok, reason, index=None, detail=None):
    if not ok:
        raise Unresolved(reason, index, detail)


def fixed(ok, predicate, index, event, expected, actual):
    if not ok:
        raise Falsified(predicate, index, event, expected, actual)


def deadline():
    if time.monotonic() - START >= LIMITS['child_seconds']:
        raise Incomplete('Internal elapsed limit; external root guard remains authoritative')


def integer(value):
    return type(value) is int


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path, cap, metadata=False):
    global METADATA_BYTES
    with path.open('rb') as stream:
        raw = stream.read(cap + 1)
    need(len(raw) <= cap, 'Byte cap exceeded: ' + path.name)
    if metadata:
        METADATA_BYTES += len(raw)
        need(METADATA_BYTES <= BOUNDS['metadata_total_bytes'], 'Aggregate metadata cap exceeded')
    return raw


def preflight(raw):
    """Lexical allocation guard BEFORE json.loads; constructs no JSON tree.

    Count every string/key, scalar and container, nesting and decoded-string
    upper lengths. json.loads separately validates complete JSON syntax.
    """
    text = raw.decode('utf-8')
    n, i, nodes, depth = len(text), 0, 0, 0
    while i < n:
        if i % 16384 == 0:
            deadline()
        ch = text[i]
        if ch.isspace() or ch in ',:':
            i += 1
            continue
        if ch in ']}':
            depth -= 1
            need(depth >= 0, 'Unbalanced JSON enclosure')
            i += 1
            continue
        nodes += 1
        need(nodes <= BOUNDS['json_nodes'], 'JSON node cap exceeded before allocation')
        if ch in '[{':
            depth += 1
            need(depth <= BOUNDS['json_depth'], 'JSON nesting cap exceeded before allocation')
            i += 1
        elif ch == '"':
            i += 1
            length = 0
            while i < n and text[i] != '"':
                need(ord(text[i]) >= 32, 'Control byte in JSON string')
                if text[i] == '\\':
                    i += 1
                    need(i < n, 'Incomplete JSON escape')
                    if text[i] == 'u':
                        need(i + 4 < n and all(c in '0123456789abcdefABCDEF' for c in text[i+1:i+5]),
                             'Malformed JSON unicode escape')
                        i += 4
                    else:
                        need(text[i] in '"\\/bfnrt', 'Unknown JSON escape')
                length += 1
                need(length <= BOUNDS['string_characters'], 'JSON string cap exceeded before allocation')
                i += 1
            need(i < n, 'Unterminated JSON string')
            i += 1
        elif ch in '-0123456789':
            start = i
            while i < n and text[i] not in ' \t\r\n,]}:':
                i += 1
                need(i - start <= BOUNDS['integer_digits'] + 1, 'JSON integer token cap exceeded')
            token = text[start:i]
            need(re.fullmatch(r'-?(0|[1-9][0-9]*)', token) is not None,
                 'Non-integer/unsupported JSON numeric token')
            need(len(token.lstrip('-')) <= BOUNDS['integer_digits'], 'JSON integer digit cap exceeded')
        elif text.startswith('true', i):
            i += 4
        elif text.startswith('false', i):
            i += 5
        elif text.startswith('null', i):
            i += 4
        else:
            raise Unresolved('Unsupported JSON token before allocation')
    need(depth == 0, 'Unbalanced JSON nesting')
    return text


def unique_pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, 'Duplicate JSON key')
        out[key] = value
    return out


def reject_number(value):
    raise Unresolved('Nonfinite or floating JSON number is unsupported')


def decode(raw):
    text = preflight(raw)
    return json.loads(text, object_pairs_hook=unique_pairs,
                      parse_float=reject_number, parse_constant=reject_number)


def coefficient(value, index):
    if integer(value):
        need(len(str(abs(value))) <= BOUNDS['coefficient_digits'], 'Coefficient token cap', index)
        q = Fraction(value)
    else:
        need(type(value) is str, 'Unsupported scalar representation', index)
        match = re.fullmatch(r'([+-]?[0-9]{1,24})(?:/([0-9]{1,24}))?', value)
        need(match is not None, 'Unsupported scalar grammar', index)
        d = int(match.group(2)) if match.group(2) else 1
        need(d > 0, 'Zero/nonpositive scalar denominator', index)
        q = Fraction(int(match.group(1)), d)
    need(q != 0 and q.denominator & (q.denominator - 1) == 0, 'Nonzero dyadic scalar required', index)
    return q


class Audit:
    def __init__(self, word):
        need(type(word) is dict and REQUIRED <= set(word) and set(word) <= REQUIRED | OPTIONAL,
             'Unknown WORD attribute/semantic channel')
        need(word['schema'] == SOURCE['schema'] and word['public'] == 743,
             'Exact schema/public inventory mismatch')
        need('owned_fields' not in word or word['owned_fields'] == 9, 'Optional owned inventory mismatch')
        if 'ports' in word:
            need(type(word['ports']) is list and len(word['ports']) == 104
                 and all(integer(q) and 0 < q < 512 for q in word['ports']), 'Unsupported optional port schema')
        self.frames, self.program = word['frames'], word['program']
        need(type(self.frames) is list and 599 <= len(self.frames) <= BOUNDS['frames'], 'Frame inventory cap/shape')
        need(type(self.program) is list and 14983 < len(self.program) <= BOUNDS['events'], 'Program inventory cap/shape')
        self.initial, self.final = word['initial'], word['final']
        need(type(self.initial) is list and type(self.final) is list
             and len(self.initial) == len(self.final) == 743, 'Endpoint inventory mismatch')
        for f in self.initial + self.final:
            self.frame_id(f)
        live = word['live']
        need(type(live) is list and len(live) == 104 and all(integer(r) and 0 <= r < 631 for r in live)
             and len(set(live)) == 104 and len(set(live) | {r+112 for r in live}) == 208, 'Live/main schema')
        # Nine-bit binary basis validation is not a Clifford or scalar matrix.
        for basis in self.frames:
            need(type(basis) is list and len(basis) <= BOUNDS['basis_vectors'], 'Frame basis cap/shape')
            pivots = {}
            for v in basis:
                need(integer(v) and 0 < v < 512, 'Frame basis vector shape')
                x = v
                while x:
                    p = x.bit_length()-1
                    if p not in pivots:
                        pivots[p] = x
                        break
                    x ^= pivots[p]
                need(x != 0, 'Dependent binary frame basis')
        self.masks = {}
        fixed([len(self.frames[f]) for f in (3,598,396)] == [0,1,3]
              and self.nested(3,598) and self.nested(598,396),
              'OLD715_STRICT_0_1_3_CHAIN', None, None, '3 strict 598 strict 396, dims0/1/3',
              {'dimensions': [len(self.frames[f]) for f in (3,598,396)]})
        self.current = {r: self.initial[r] if r < 743 else None for r in SUBJECT['tracked']}
        self.last = {r: {'index': None, 'event': None, 'initial_frame': self.current[r]} for r in self.current}
        self.alive = set()
        self.birth = {r: 0 for r in range(743,752)}
        self.birth_site = {r: None for r in range(743,752)}
        self.prospective = self.current[715]
        self.ledgers, self.ledger_bytes = [], 0
        self.anchors, self.cuts, self.samples = {}, {}, {}
        self.write712, self.write525, self.write340 = [], [], []
        self.scanned = 0

    def frame_id(self, frame, index=None):
        need(integer(frame) and 0 <= frame < len(self.frames), 'Invalid frame index', index)

    def mask(self, frame):
        if frame not in self.masks:
            values = [0]
            for v in self.frames[frame]:
                values += [x ^ v for x in values]
            mask = 0
            for x in values:
                mask |= 1 << x
            self.masks[frame] = mask
        return self.masks[frame]

    def nested(self, a, b):
        return len(self.frames[a]) < len(self.frames[b]) and self.mask(a) & self.mask(b) == self.mask(a)

    def state(self):
        return {str(r): {'frame': self.current[r], 'live': r < 743 or r in self.alive,
                         'owned_birth': self.birth.get(r), 'last_frame_change': self.last[r]}
                for r in self.current}

    def append(self, entry):
        raw = canonical(entry)
        need(len(raw) <= BOUNDS['entry_bytes'], 'Ledger entry byte cap')
        need(len(self.ledgers) < BOUNDS['ledger_entries']
             and self.ledger_bytes + len(raw) <= BOUNDS['ledger_bytes'], 'Complete ledger cap; no truncation')
        self.ledger_bytes += len(raw)
        self.ledgers.append(entry)

    def insertion_cut(self, index):
        if index not in (823,14983):
            return
        wanted = 3 if index == 823 else 396
        roles = (715,525,712) if index == 823 else (715,525,340)
        fixed(all(self.current[r] == wanted for r in roles), 'ORIGINAL_CUT_COMMON_CHART', index,
              self.program[index], {'roles': list(roles), 'frame': wanted}, self.state())
        fixed(self.prospective == wanted, 'PROSPECTIVE715_INSERTION_CHART', index,
              self.program[index], wanted, self.prospective)
        self.cuts[str(index)] = {'convention': 'BEFORE_ORIGINAL_EVENT', 'state': self.state(),
                                 'prospective715_frame': self.prospective,
                                 'insertions': [x for x in SUBJECT['insertions'] if x[0] == index]}

    def parse_event(self, event, index):
        need(type(event) is list and len(event) >= 2, 'Malformed event', index)
        op, r = event[:2]
        need(type(op) is str and op in ARITY and len(event) == ARITY[op], 'Unknown opcode/arity', index)
        need(integer(r) and 0 <= r < 752, 'Invalid positional destination', index)
        reads, writes, accum, touched, q = [], [], [], [r], None
        if op == 'MOVE':
            a,b,private = event[2:]
            self.frame_id(a,index); self.frame_id(b,index)
            need((r < 743 or r in self.alive) and type(private) is bool
                 and private == (r in self.alive), 'MOVE ownership/lifetime ambiguity', index)
        elif op in ('INIT','CLEAR'):
            need(r >= 743 and ((r not in self.alive) if op == 'INIT' else (r in self.alive)),
                 'Owned lifetime grammar invalid', index)
            self.frame_id(event[2],index)
            writes = [r]
        else:
            self.frame_id(event[-1],index)
            q = coefficient(event[-2],index)
            writes = [r]
            if op in ('ADD','COPY'):
                s = event[2]
                need(integer(s) and 0 <= s < 752 and s != r, 'Invalid positional source', index)
                need(op != 'COPY' or r >= 743, 'COPY destination not owned', index)
                reads, touched = [s], [r,s]
                if op == 'ADD':
                    accum = [r]
            else:
                reads = [r]
            need(all(v < 743 or v in self.alive for v in touched), 'Inactive owned scalar access', index)
        return op,r,q,reads,writes,accum,touched

    def anchor(self, index, event, op, r, q):
        if index not in SUBJECT['anchors']:
            return
        self.anchors[str(index)] = {'event': event, 'state_before': self.state(),
                                   'prospective715_before': self.prospective}
        add = {13572:(712,747,1,None),13578:(715,747,1,598),13737:(525,712,-4,None),
               14654:(525,340,1,None),14983:(340,715,-4,None)}
        if index in add:
            dest,src,c,frame = add[index]
            ok = op == 'ADD' and r == dest and event[2] == src and q == c
            if frame is not None:
                ok = ok and event[-1] == frame
            fixed(ok, 'FIXED_ADD_ANCHOR', index, event, list(add[index]), event)
        if index in (13577,14982):
            expected = ['MOVE',715,3,598,False] if index == 13577 else ['MOVE',715,598,396,False]
            fixed(event == expected, 'FIXED_MOVE_ANCHOR', index, event, expected, event)

    def check_causal(self, index, event, reads, writes, accum, touched):
        scopes = []
        if 823 <= index < 14983:
            if 712 in writes:
                self.write712.append(index); scopes.append('712_interval_writes')
                fixed(index == 13572, '712_SOLE_INTERVAL_WRITE', index, event, [13572], self.write712)
            if 525 in writes:
                self.write525.append(index); scopes.append('525_interval_writes')
                fixed(index in (13737,14654), '525_TWO_INTERVAL_WRITES', index, event, [13737,14654], self.write525)
            if 715 in touched:
                scopes.append('715_all_interval_contacts')
                fixed(event[0] == 'MOVE' or (event[0] == 'ADD' and event[1] == 715 and 715 not in reads),
                      '715_NO_OUTWARD_OBSERVER_OR_FORBIDDEN_CHANGE', index, event,
                      'MOVE or destination-only ADD', {'reads':reads,'writes':writes})
        if 11202 <= index < 14983 and 340 in writes:
            self.write340.append(index)
            scopes.append('340_nonblocking_11202_provenance_writes')
            if index >= 14654:
                fixed(False, '340_MINIMAL_READ_TO_CUT_STABILITY', index, event,
                      'No340write in [14654,14983)', self.write340)
        if 13572 <= index <= 13578 and 747 in touched:
            scopes.append('747_two_read_continuity')
            if index < 13578:
                fixed(747 not in writes, '747_NO_INTERVENING_WRITE_OR_LIFECYCLE', index, event, 'No747write', writes)
            if index in (13572,13578):
                self.samples[str(index)] = {'birth': self.birth[747], 'live': 747 in self.alive,
                                            'frame': self.current[747],
                                            'birth_event_index':self.birth_site[747]}
        if 715 in touched:
            scopes.append('715_complete_prospective_contact_trace')
        if index in SUBJECT['anchors']:
            scopes.append('fixed_anchor_or_boundary')
        return scopes

    def apply(self, index, event, op, r, touched):
        before = {str(v): self.current[v] for v in touched if v in self.current}
        prospective_before = self.prospective
        if op == 'MOVE':
            a,b,private = event[2:]
            if r in self.current:
                fixed(self.current[r] == a, 'ORIGINAL_TRACKED_MOVE_SOURCE', index,event,a,self.current[r])
                fixed(self.nested(b,a) if private else self.nested(a,b), 'ORIGINAL_TRACKED_MOVE_NESTING',
                      index,event,'Strict owned reverse/public forward inclusion', [a,b])
            if r == 715 and index != 13577:
                source = 3 if index == 14982 else a
                fixed(self.prospective == source and self.nested(source,b), 'PROSPECTIVE715_MOVE_CONTACT',
                      index,event,{'source':source,'target':b},self.prospective)
                self.prospective = b
            if r in self.current:
                self.current[r] = b
                self.last[r] = {'index':index,'event':event}
        elif op in ('INIT','CLEAR'):
            if op == 'INIT':
                self.alive.add(r); self.birth[r] += 1
                self.birth_site[r] = index
            else:
                self.alive.remove(r)
            if r in self.current:
                if op == 'CLEAR':
                    fixed(self.current[r] == event[2], 'TRACKED_CLEAR_CHART', index,event,event[2],self.current[r])
                self.current[r] = event[2] if op == 'INIT' else None
                self.last[r] = {'index':index,'event':event}
        else:
            for v in touched:
                if v in self.current:
                    fixed(self.current[v] == event[-1], 'ORIGINAL_TRACKED_SCALAR_COMMON_CHART',
                          index,event,event[-1],{'role':v,'actual':self.current[v]})
            if 715 in touched and index != 13578:
                fixed(self.prospective == event[-1], 'PROSPECTIVE715_RETAINED_SCALAR_CONTACT',
                      index,event,event[-1],self.prospective)
        return {'tracked_frames_before':before,
                'tracked_frames_after':{str(v):self.current[v] for v in touched if v in self.current},
                'prospective715_before':prospective_before,'prospective715_after':self.prospective}

    def scan(self):
        for index,event in enumerate(self.program):
            if index % 256 == 0:
                deadline()
            self.insertion_cut(index)
            op,r,q,reads,writes,accum,touched = self.parse_event(event,index)
            self.anchor(index,event,op,r,q)
            scopes = self.check_causal(index,event,reads,writes,accum,touched)
            transition = self.apply(index,event,op,r,touched)
            if scopes:
                self.append({'index':index,'event':event,'scopes':scopes,
                             'classification':{'reads':reads,'writes':writes,'local_accumulation':accum,
                                               'native_transport':op == 'MOVE',
                                               'rule':'CLOSED_POSITIONAL_SIX_OP_GRAMMAR'},
                             'transition':transition})
            if str(index) in self.anchors:
                self.anchors[str(index)]['state_after'] = self.state()
            self.scanned = index + 1
        fixed(self.write712 == [13572], 'COMPLETE712_WRITE_CENSUS', len(self.program),None,[13572],self.write712)
        fixed(self.write525 == [13737,14654], 'COMPLETE525_WRITE_CENSUS',len(self.program),None,[13737,14654],self.write525)
        fixed(set(self.samples) == {'13572','13578'} and self.samples['13572']['live']
              and self.samples['13578']['live']
              and self.samples['13572']['birth'] == self.samples['13578']['birth'],
              '747_SAME_OWNED_LIFETIME_AT_TWO_READS',len(self.program),None,'Same live owned lifetime',self.samples)
        for r in (340,525,712,715):
            fixed(self.current[r] == self.final[r], 'TRACKED_PUBLIC_FINAL_CHART',len(self.program),None,
                  {'role':r,'frame':self.final[r]},self.current[r])
        fixed(self.prospective == self.final[715], 'PROSPECTIVE715_FINAL_CHART',len(self.program),None,
              self.final[715],self.prospective)
        need(not self.alive, 'Owned lifetime grammar has live exits')
        return {'status':'PASS_FIXED_CAUSAL_LEDGER_AND_TYPED_CONTACTS_ONLY',
                'coverage':{'complete_program_scan':True,'events':self.scanned,
                            'interval':'[823,14983)','340_required_interval':'[14654,14983)',
                            '340_nonblocking_provenance_interval':'[11202,14983)',
                            '747_no_write_interval':'[13572,13578)',
                            'prospective715_contacts':'ALL_RETAINED_FULL_PROGRAM_PLUS_FOUR_INSERTIONS'},
                'anchors':self.anchors,'cuts':self.cuts,'ledgers':self.ledgers,
                'write_census':{'712':self.write712,'525':self.write525,'340':self.write340},
                '340_stronger_provenance_observation':{
                    'blocking':False,'writes_in_inclusive11202_to_cut14983':self.write340,
                    'no_write_stronger_claim_observed':not self.write340,
                    'meaning':'Provenance only; required C stability starts at14654 source read'},
                '747_read_lifetimes':self.samples,
                'predicates':{p:'PASS' for p in ['fixed_anchors','712_writes','525_writes','340_stability',
                                               '747_value_lifetime_continuity','715_observer_exclusion',
                                               'original_cut_frames','tracked_original_typing',
                                               'prospective715_all_contacts','closed_full_grammar']},
                'credited_causal_identity':'Ali Romman PR5713: D=A-4*(B+V)+C; V=A/4-B-D/4+C/4',
                'assumptions':['Decoded native MOVEs preserve logical values',
                               'Straight-line positional field semantics; no unsupported channels',
                               'Baseline scalar/native and owned-erasure contracts remain conditional'],
                'not_proved':['Emitted5713 WORD/delta equality','Exact3-to396 provider/absolute phase/all widths',
                              'Full scalar endpoint matrix or owned-zero erasures','Physical caller/full invoice',
                              'Ordinary/stock/precision/tape/compiler/BIT/outer funding','New kappa or .00311']}


SOURCE = {'repository': 'GamingPuzzled/integer-mult-bounds', 'head': 'd0f6fa2555410a1e23fe4191424c2097ab3d5d97', 'committed_path': 'research/p104-reframe-r22/WORD.json.gz', 'file_name': 'WORD.json.gz', 'bytes': 106613, 'git_blob': 'f3fb0e2144ec8a5c3407e4eaa6528bb3436ba573', 'sha256': 'd6db1d0d97b13ea483a462c65437664d15d34dec56c3682cf6e1de31266ec6c2', 'schema': 'p104-r22-reframe/1', 'embedded_frames': 'BOUND_BY_COMPLETE_AUTHENTICATED_WORD'}

INPUT_TEXT_PINS = {'LICENSE': {'bytes': 11357, 'sha256': 'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4', 'git_blob': '261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64'}, 'NOTICE': {'bytes': 2179, 'sha256': 'e8e0cabef6cf40d63f3cea3b6403dfd1af8727e40df03f09b2932718bcddc1b0', 'git_blob': 'fa0bd1401f5775f4351cfa23b08f3998dba6129e'}}


def authenticate_blob(path, pin):
    raw = bounded_read(path, pin['bytes'], metadata=True)
    need(len(raw) == pin['bytes'] and sha(raw) == pin['sha256'], 'Pinned input length/SHA256 mismatch: ' + path.name)
    need(hashlib.sha1(('blob '+str(len(raw))+'\0').encode('ascii')+raw).hexdigest() == pin['git_blob'],
         'Pinned input Git blob mismatch: ' + path.name)
    return raw


def run():
    global BINDING_CONTEXT
    need(len(sys.argv) == 2, 'Expected exactly one data path: WORD.json.gz; no control/source/window options')
    input_path = Path(sys.argv[1])
    need(input_path.name == SOURCE['file_name'], 'Input basename must be the exact source filename WORD.json.gz')
    checker_raw = bounded_read(Path(__file__).resolve(), BOUNDS['metadata_file_bytes'], metadata=True)
    binding = {'checker_sha256':sha(checker_raw), 'source':SOURCE,
               'variant':'PORTABLE_DATA_ONLY_ADAPTATION',
               'historical_local_checker_sha256':'e2c42f6f5db304067661ec3d54e6c94ebf7bc2fa82d4c8ded7f714cdcb461aa3',
               'historical_local_run_is_not_a_portable_run':True}
    BINDING_CONTEXT = binding
    for name,pin in INPUT_TEXT_PINS.items():
        authenticate_blob(HERE/'inputs'/name, pin)
    raw = authenticate_blob(input_path, SOURCE)
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        expanded = stream.read(BOUNDS['expanded_bytes'] + 1)
    need(len(expanded) <= BOUNDS['expanded_bytes'], 'Expanded JSON byte cap')
    decoded_sha = sha(expanded)
    word = decode(expanded)
    del expanded, raw
    audit = Audit(word)
    result = audit.scan()
    result['binding'] = binding
    result['decoded_word_sha256_recorded_after_authorized_decode'] = decoded_sha
    return result


def main():
    try:
        result = run()
        code = 0
    except Falsified as e:
        result = {'status':'FIXED_SUFFICIENT_PREMISE_NOT_ESTABLISHED','predicate':e.predicate,'event_index':e.index,
                  'event':e.event,'expected':e.expected,'actual':e.actual,
                  'coverage_complete':False,
                  'meaning':'Fixed sufficient causal or prescribed typing premise not established; no identity counterexample or author defect proved'}
        code = 2
    except (Incomplete, MemoryError, TimeoutError, KeyboardInterrupt) as e:
        result = {'status':'INCOMPLETE','coverage_complete':False,'reason':type(e).__name__+': interrupted or allocation failure'}
        code = 4
    except Exception as e:
        result = {'status':'BINDING_UNRESOLVED','coverage_complete':False,'scientific_falsifier':False,
                  'reason':e.reason if isinstance(e,Unresolved) else type(e).__name__+': input/runtime failure; local paths omitted',
                  'event_index':getattr(e,'index',None),'detail':getattr(e,'detail',None)}
        code = 3
    result.update({'object_id':OBJECT,'source_head':SOURCE['head'],'no_fallback':True,'new_kappa':None,
                   'binding':BINDING_CONTEXT,'source':SOURCE,
                   'elapsed_seconds_internal':time.monotonic()-START,
                   'runtime_memory_and_termination_evidence':'EXTERNAL_GUARD_EVIDENCE_IS_SEPARATE'})
    try:
        body = canonical(result)
        need(len(body) + 256 <= BOUNDS['output_bytes'], 'Receipt output cap; no truncation')
        envelope = canonical({'receipt':result,'receipt_sha256':sha(body)})
    except MemoryError:
        envelope = canonical({'receipt':{'status':'INCOMPLETE','reason':'Receipt serialization memory failure',
                                         'coverage_complete':False,'object_id':OBJECT}})
        code = 4
    except Exception:
        envelope = canonical({'receipt':{'status':'BINDING_UNRESOLVED','reason':'Receipt output cap',
                                         'coverage_complete':False,'object_id':OBJECT}})
        code = 3
    print(envelope.decode('ascii'))
    return code


if __name__ == '__main__':
    sys.exit(main())
