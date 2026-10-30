"""Literal ownership typing for the P104 word and its forward caller.

Mason Hale with substantial OpenAI Codex assistance. Apache-2.0.
The input word and caller retain their authors' notices in source/NOTICE.
This checks storage use, not native numerical correctness or compiler admission.
"""
from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inputs():
    word = json.loads(gzip.decompress((HERE/'source/WORD.json.gz').read_bytes()))
    raw = (ROOT/'research/p104-productive-controller/CONTROLLER.json').read_bytes()
    need(sha256(raw).hexdigest() == 'a84f6bbd547379597464e56c420cc665f96bc43a9a1351eed4b7cd0fce3cc4b9', 'Exact P104 caller bytes')
    caller = json.loads(raw)
    digest = sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(digest == 'a06445539ad73fe16deae66fef8c52ffc39f5f14c765eab3dc3d98e0e2d8074c', 'Exact PR5811 word')
    return word, caller


def type_word(word):
    """No owned read/write outside a lifetime; no borrowed initialization/erase."""
    public, owned = word['public'], word['owned_fields']
    live, lives, peak, copies, moves = set(), [], 0, 0, []
    starts = {}
    def active(r):
        need(type(r) is int and 0 <= r < public+owned, 'Role range')
        need(r < public or r in live, 'Owned access outside lifetime')
    for pc, e in enumerate(word['program']):
        op, r = e[:2]
        if op == 'INIT':
            need(public <= r < public+owned and r not in live, 'Fresh owned INIT')
            live.add(r)
            starts[r] = pc
            peak = max(peak, len(live))
        elif op == 'CLEAR':
            need(r >= public and r in live, 'CLEAR only a live owned field')
            lives.append([r, starts.pop(r), pc])
            live.remove(r)
        elif op in ('ADD', 'COPY'):
            active(r)
            active(e[2])
            need(r != e[2], 'Distinct scalar ports')
            if op == 'COPY':
                need(r >= public, 'COPY destination owned')
                copies += 1
        elif op in ('MOVE', 'SCALE'):
            active(r)
            if op == 'MOVE':
                need(e[4] == (r >= public), 'Paid owner tag')
                moves.append([pc, r, r >= public])
        else:
            raise ValueError('Unknown opcode')
    need(not live, 'No live owned fields at return')
    return dict(public=public, owned_labels=owned, lifetimes=sorted(lives), peak=peak,
                copies=copies, paid_owners=moves)


def bind(word, caller):
    typed = type_word(word)
    live_ports = word['live']
    need(len(live_ports) == len(set(live_ports)) == 104, 'Actual 104 selected ports')
    nports = len(live_ports)
    main_roles = set(live_ports) | {r+112 for r in live_ports}
    helpers = sorted(set(range(word['public']))-main_roles)
    events = caller['physical_events']
    need((caller['kind'],caller['pairs'],caller['prefix_pairs'],caller['ambient_rank']) == ('complex',16,7,145), 'Exact caller family')
    def pair_role(r):
        need(type(r) is int and 0 <= r < 32, 'Caller public role range')
    for e in events:
        op=e[0]
        if op in ('LOCAL','QUERY_SHEAR'):
            need(len(e)==4 and type(e[1]) is int and 0 <= e[1] <= 32
                 and type(e[2]) is int and 0 <= e[2] < 16
                 and type(e[3]) is bool, 'Caller stage/pair/direction')
        elif op=='IDLE':
            need(len(e)==3 and type(e[1]) is int and 0 <= e[1] < 16
                 and e[2] and all(type(s) is int and 0 <= s <= 32 for s in e[2])
                 and len(set(e[2]))==len(e[2]), 'Idle owner/axes')
        elif op=='Q_POWER':
            need(len(e)==3 and e[2] in (-2,2), 'Central square grammar')
            pair_role(e[1])
        else:
            need(op in ('ADD','SWAP','SIGNED_SWAP') and len(e)==(4 if op=='ADD' else 3), 'Caller scalar opcode')
            pair_role(e[1]); pair_role(e[2])
            need(e[1]!=e[2], 'Caller scalar distinct public fields')
    for side in ('left_program','right_program'):
        for e in caller['boundaries'][side]:
            need(e[0] in ('ADD','SCALE','SWAP'), 'Boundary scalar opcode')
            pair_role(e[1])
            if e[0]!='SCALE':
                pair_role(e[2])
                need(e[1]!=e[2], 'Boundary scalar distinct public fields')
    locals_ = [(i,e) for i,e in enumerate(events) if e[0] == 'LOCAL']
    queries = [(i,e) for i,e in enumerate(events) if e[0] == 'QUERY_SHEAR']
    need(len(locals_) == 18 and len(queries) == 15 and all(not e[3] for _,e in locals_+queries), 'Literal all-forward caller')
    productive = 32*nports + len(locals_)*len(helpers)
    local_owned = len(locals_)*word['owned_fields']
    query_first = productive+local_owned
    all_owned, all_helpers, sites = set(), set(), []
    for occurrence, (pc, event) in enumerate(locals_):
        pair = event[2]
        grants = {}
        for port, r in enumerate(live_ports):
            grants[r] = 2*pair*nports+port
            grants[r+112] = (2*pair+1)*nports+port
        for j,r in enumerate(helpers):
            grants[r] = 32*nports+occurrence*len(helpers)+j
            need(grants[r] not in all_helpers, 'Distinct helper input across local occurrences')
            all_helpers.add(grants[r])
        for j in range(word['owned_fields']):
            r = word['public']+j
            grants[r] = productive+occurrence*word['owned_fields']+j
            need(grants[r] not in all_owned, 'Fresh local occurrence ownership')
            all_owned.add(grants[r])
        need(len(grants) == len(set(grants.values())) == word['public']+word['owned_fields'], 'Injective complete local grant')
        need(all(0 <= grants[r] < productive for r in range(word['public'])), 'Only productive slots borrowed')
        sites.append(dict(event=pc, stage=event[1], pair=pair,
                          grant_sha256=sha256(json.dumps(sorted(grants.items())).encode()).hexdigest(),
                          first_owned=productive+occurrence*word['owned_fields'],
                          last_owned=productive+(occurrence+1)*word['owned_fields']-1))
    query_sites = []
    for pc,e in queries:
        pair=e[2]
        rows = [[2*pair*nports+j, (2*pair+1)*nports+j, query_first+j] for j in range(nports)]
        need(all(len(set(row)) == 3 and row[2] not in all_owned for row in rows), 'Distinct query ports and local ownership')
        # Each synchronous macro is PREPARE; child; FINISH. Its query bank is
        # cleared before the next outer event. Descendants use fresh segments.
        query_sites.append(dict(event=pc, stage=e[1], pair=pair, ports=rows))
    return dict(status='PASS_LITERAL_OWNERSHIP_TYPING', source_pr=5811,
                source_head='883ab9ca680906a0df88fb74ff51d634868af363',
                local=dict(public=typed['public'], owned=typed['owned_labels'],
                           lifetimes=len(typed['lifetimes']), peak=typed['peak'], copies=typed['copies'],
                           paid_owned=sum(r[2] for r in typed['paid_owners']),
                           lifetime_endpoints=typed['lifetimes']),
                raw_productive=productive, raw_local_owned=local_owned,
                raw_query_owned=nports, raw_total_owned=local_owned+nports,
                raw_total_fields=productive+local_owned+nports,
                local_occurrences=sites, query_sites=query_sites,
                compiled_inventory='A distinct tagged copy of these626 owned labels for each fully expanded raw-unit occurrence; this is not a materialization of the compiler.',
                scope='Literal lifetime/access typing and an explicit injective safe grant. Native correctness, physical execution and full selected admission are separate.')


def controls(word, caller):
    from copy import deepcopy
    def rejected(w):
        try:
            type_word(w)
        except ValueError as e:
            return str(e)
        raise ValueError('Invalid lifetime accepted')
    out = {}
    bad=deepcopy(word)
    i=next(i for i,e in enumerate(bad['program']) if e[0]=='CLEAR')
    bad['program'][i][1]=0
    out['borrowed_clear']=rejected(bad)
    bad=deepcopy(word)
    i=next(i for i,e in enumerate(bad['program']) if e[0]=='INIT')
    del bad['program'][i]
    out['missing_initialization']=rejected(bad)
    bad=deepcopy(word)
    i=next(i for i,e in reversed(list(enumerate(bad['program']))) if e[0]=='CLEAR')
    del bad['program'][i]
    out['missing_last_clear']=rejected(bad)
    bad=deepcopy(word)
    bad['program'].insert(0,['SCALE',word['public'],'1',0])
    out['use_before_lifetime']=rejected(bad)
    bad=deepcopy(word)
    i=next(i for i,e in enumerate(bad['program']) if e[0]=='INIT')
    bad['program'].insert(i+1,list(bad['program'][i]))
    out['suspended_bank_reinitialization']=rejected(bad)
    for opcode in ('LOCAL','QUERY_SHEAR'):
        bad_caller=deepcopy(caller)
        next(e for e in bad_caller['physical_events'] if e[0]==opcode)[2]=-1
        try:
            bind(word,bad_caller)
        except ValueError as e:
            out['negative_'+opcode.lower()+'_pair']=str(e)
        else:
            raise ValueError('Negative caller pair accepted')
    return out


if __name__ == '__main__':
    word,caller=inputs()
    result=bind(word,caller)
    result['negative_controls']=controls(word,caller)
    print(json.dumps(result,indent=2,sort_keys=True))
