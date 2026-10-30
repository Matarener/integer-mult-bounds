# SPDX-License-Identifier: Apache-2.0
"""Bounded lifetime and exact row-divisibility audit; no predecessor imports.

The caller authenticates WORD before calling audit(). This does not execute
Machine or certify its numerical/physical contract.
"""
from hashlib import sha256
import json


def require(ok, why):
    if not ok:
        raise ValueError(why)


def gamma_odd():
    answer = 1
    for i in range(1, 37):
        answer *= (1 << (2*i)) - 1
    return answer


def minimal_lanes(depth, spectator_bits):
    require(type(depth) is int and depth >= 1, 'positive division depth')
    require(type(spectator_bits) is int and spectator_bits >= 0,
            'nonnegative spectator exponent')
    return 7**depth * gamma_odd()**(depth-1) * (1 << max(0, 1307*depth-1296-spectator_bits))


def paired_schedule(total=104, hosts=8):
    """Keep original adjacent-pair consumption order; atomic seven-lane cores."""
    require(total % 2 == 0, 'complete pairs')
    pending = []
    next_pair = 0
    records = []
    peak = 0
    for start in range(0, total, 7):
        fresh = list(range(start, min(start+7, total)))
        padding = 7-len(fresh)
        occupancy = len(pending)+len(fresh)+padding
        require(occupancy <= hosts, 'native lease overlaps pending original')
        peak = max(peak, occupancy)
        pending += fresh
        consumed = []
        while next_pair+1 in pending:
            require(next_pair in pending, 'original first member remains live')
            pending.remove(next_pair)
            pending.remove(next_pair+1)
            consumed.append([next_pair, next_pair+1])
            next_pair += 2
        records.append(dict(fresh=fresh, zero_lanes=padding, consumed_pairs=consumed,
                            retained=pending[:], leased_fields=occupancy))
    require(not pending and next_pair == total, 'all original pair sources consumed')
    return dict(batches=records, peak_source_hosts=peak,
                zero_lanes=sum(r['zero_lanes'] for r in records))


def audit(word):
    require(isinstance(word, list), 'literal word list')
    lines = [(i,e) for i,e in enumerate(word) if e[0] == 'line']
    require(len(lines)==224, '224 actual H1 events')
    positive_prefix=[(i,e) for i,e in lines if i<540]
    negatives=[(i,e) for i,e in lines if e[-1]==-1]
    responses=[(i,e) for i,e in lines if i>=2434]
    require(len(positive_prefix)==112 and len(negatives)==104 and len(responses)==8,
            'source-bound three event epochs')
    require([e[2] for _,e in positive_prefix]==list(range(112)), 'all prefix ports')
    for i,e in positive_prefix:
        p=e[2]
        require(word[i-2:i+1]==[['clear',f'W{p}',f'hole{p}'],
                                  ['add',f'W{p}',f'Y{p}','1'],['line',f'W{p}',p,1]],
                'independent prefix preparation')
    for e in word[:540]:
        require(e[0] in ('clear','add','line'), 'prefix only independent definitions')
        if e[0]=='add':
            require((e[1].startswith('W') and e[2]=='Y'+e[1][1:]) or
                    (e[1].startswith('Z') and e[2]=='X'+e[1][1:]),
                    'no prefix cross-source dependence')
    require(all(e[3]==1 for _,e in positive_prefix+responses), 'positive source epochs')
    require(word[1694:1702]==[['clear',f'Z{p}','query2'] for p in (1,2,3,4,5,6,8,9)],
            'eight actual query accumulators')
    for n,(i,e) in enumerate(negatives):
        temp='Z10' if n%2==0 else 'Z11'; port=e[2]
        require(word[i-3:i+1]==[['clear',temp,'current'],['add',temp,f'W{port}','1'],
                                  ['map',temp,2,port,False],['line',temp,port,-1]],
                'preserved actual corrected W acquisition')
    require(len({e[2] for _,e in negatives})==104, 'all sources distinct')
    require(not any(e[0] in ('begin','end') for e in word[1694:2498]),
            'query batch interval outside original private scope')
    for a in range(52):
        i,e=negatives[2*a]; j,f=negatives[2*a+1]
        end=negatives[2*a+2][0]-3 if a<51 else 2434
        ops=word[j+1:end]
        require(all(op[0]=='add' and op[1] in ('Z1','Z2','Z3','Z4','Z5','Z6','Z8','Z9','Z10')
                    and op[2] in ('Z10','Z11') for op in ops), 'original pair consumption only')
        require(ops.count(['add','Z10','Z11','1'])==1, 'literal paired sum retained')
    available=[]
    for p in range(112):
        z=f'Z{p}'
        uses=[(i,e) for i,e in enumerate(word[:2498]) if z in e]
        if len(uses)==2 and uses[1][0]==uses[0][0]+1 and [e for _,e in uses]==[
                ['clear',z,'current'],['add',z,f'X{p}','1']]:
            available.append(p)
    selected=list(range(12,18))
    require(all(p in available for p in selected), 'six output definitions may be deferred')
    require(not any(e[0]!='checkpoint' and len(e)>1 and e[1] in {f'X{p}' for p in selected}
                    for e in word), 'borrowed X sources remain unchanged')
    schedule=paired_schedule()
    try:
        paired_schedule(hosts=7)
    except ValueError:
        seven_reject=True
    else:
        seven_reject=False
    require(seven_reject, 'seven hosts cannot keep odd batch carry')
    odd=gamma_odd()
    # A finite cross-check of the exact valuation formula, not its proof.
    gamma=(1<<1296)*odd; L=14336*gamma
    for d in (1,2,3):
        for s in (0,10,11,72,1296,1318,4000):
            b=minimal_lanes(d,s)
            require((b*gamma*(1<<s))%(L**d)==0, 'minimal multiplier accepts')
            require(((b-1)*gamma*(1<<s))%(L**d)!=0, 'next lower count rejects')
    return dict(schema='qq16-batch-audit-v1',
        authenticated_word_required=True,
        word_sha256=sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        event_epochs=dict(prefix=112,query=104,response=8),
        deferrable_extra_output_ports=available, selected_extra_hosts=selected,
        query_accumulators=8, source_hosts=8, total_leased_Z_hosts=16,
        query_schedule=schedule,
        shallow_batches=dict(prefix=16,query=15,response=2,total=33,real_lanes=224,
                             zero_lanes=7,complete_lanes=231,volume_ratio='33/32'),
        minimum_lane_formula='7^D * odd(Gamma)^(D-1) * 2^max(0,1307D-1296-s)',
        one_level_condition='D=1 and s>=11 for seven lanes',
        two_level_odd_minimum_bits=(49*odd).bit_length(),
        two_level_pool_224_impossible=49*odd>224,
        controls=dict(seven_source_hosts_rejected=seven_reject),
        scope='Source-bound lease and row arithmetic only; no physical/native admission or tariff credit')
