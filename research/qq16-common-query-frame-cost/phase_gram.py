"""Binary polar matrices and exact source-derived normalization certificate."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from query_frame_sources import need


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def rank(rows):
    pivots={}
    for row in rows:
        while row:
            index=row.bit_length()-1
            if index not in pivots:
                pivots[index]=row
                break
            row^=pivots[index]
    return len(pivots)


def action(columns,v):
    out=0
    while v:
        bit=v&-v
        out^=columns[bit.bit_length()-1]
        v^=bit
    return out


def compose(left,right):
    return tuple(action(left,c) for c in right)


def outer(v,n):
    return tuple(v if (v>>i)&1 else 0 for i in range(n))


def gram(terms,n=73):
    result=[0]*n
    for vector,coefficient in terms:
        if coefficient%2:
            result=[a^b for a,b in zip(result,outer(vector,n))]
    return tuple(result)


def xor(a,b):
    return tuple(x^y for x,y in zip(a,b))


def interval_bill(count,max_fiber):
    need(count==104 and max_fiber==1,'actual normalization/cancellation coverage')
    # All exponents s in [1/2,1] obey k^s>=sqrt(k).
    rank_one_square=2*(count-max_fiber)**2-144**2
    rank_two_rational=(count-3)*F(7,5)+3  # sqrt(3)>7/5
    higher_square=2*count**2-144**2
    need(rank_one_square>0 and F(49,25)<3 and rank_two_rational>144 and higher_square>0,
         'strict nonzero common-frame normalization gate')
    return {'a_interval':['0','1/2'],'s_interval':['1/2','1'],
            'baseline_phase_moment':104,'nonzero_phase_moment_strictly_above':144,
            'strict_excess_above_baseline':40,
            'rank_one_square_margin':rank_one_square,
            'rank_two_rational_lower':str(rank_two_rational),
            'rank_ge_three_square_margin':higher_square,
            'other_actual_costs':'nonnegative and not supplied; granted free only in this lower-bound relaxation'}


def certificate(L,P,R,routes,labels):
    n=73
    G17=gram(P.F17);G16=gram(L.F16)
    records=[];fibers=Counter();character_images=[]
    full_routes=[]
    for p in P.U+P.T:
        first,second=routes[1][p],routes[2][p]
        h=compose(second,first);inv=compose(first,second);q=labels[p]
        need(all(action(h,action(inv,1<<i))==1<<i for i in range(n)),'complete source route inverse')
        need(q!=0 and sum(R[j][p]**2 for j in range(8))==4,'nonzero actual branch coefficient')
        b1=P.alignment(first,P.F17);b2=L.bridge(P,second,q)
        frame=P.move(P.move(P.F17,first,b1),second,b2)
        need(P.phase(frame)==P.phase(L.F16+((q,1),)),'actual complete branch frame')
        need(P.phase(frame+((q,-1),))==P.phase(L.F16),'baseline negative H1 restores exact frame')
        defect=xor(gram(frame),G16)
        need(defect==outer(q,n) and rank(defect)==1,'actual rank-one polar defect')
        u=action(inv,q)
        fibers[u]+=1
        character=action(h,1);character_images.append(character)
        full_routes.append([p,list(h),list(inv)])
        records.append([p,q,u,character,b1,b2])
    need(len(records)==104 and len(set(character_images))==104,'104 distinct actual owner branches')
    need(len(fibers)==104 and max(fibers.values())==1,'unique cancellation direction per branch')
    return {'schema_version':1,'dimension':73,'polar_coordinates':2701,
            'base':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
            'residual_source_head':'309189077d0f760248bbdaadab42ecbff4f3ea2d',
            'fields':['port','normal_q','pulled_back_direction_u','owner_image_of_character_1','first_affine_shift','second_affine_shift'],
            'records':records,'distinct_cancellation_directions':104,'max_cancellation_fiber':1,
            'owner_columns_sha256':sha256(canonical(full_routes)).hexdigest(),
            'input_gram_rows':list(G17),'target_gram_rows':list(G16),
            'bill':interval_bill(len(records),max(fibers.values()))}


def lifted_bound(receipt,partition):
    directions={r[0]:r[2] for r in receipt['records']}
    groups=partition['groups']
    flattened=[p for group in groups for p in group]
    need(len(flattened)==len(set(flattened))==104 and set(flattened)==set(directions),
         'partition covers every nonzero branch exactly once')
    ranks=[rank(directions[p] for p in group) for group in groups]
    need(all(r==len(group) for r,group in zip(ranks,groups)),'independent cancellation groups')
    span=rank(directions.values())
    minimum=(104+span-1)//span
    need(span==9 and len(groups)==minimum==12,'optimal independent partition count')
    coefficient=F(104-2*len(groups),104)
    need(coefficient==F(10,13),'lifted rank-intersection budget coefficient')
    return {'positive_integer_lambda':'arbitrary','common_polar_perturbation':'arbitrary symmetric 73*lambda matrix; plane mixing allowed',
            'a_interval':['0',str(coefficient)],'independent_groups':len(groups),'group_sizes':ranks,
            'minimal_group_count':minimum,'ambient_direction_rank':span,
            'partition_sha256':sha256(canonical(partition)).hexdigest(),
            'rank_sum_lower':'104*lambda + 80*rank(Delta)',
            'moment_lower':'(104*lambda+80*rank(Delta))/(lambda+rank(Delta))^a',
            'unchanged_minimum':'104*lambda^(1-a)',
            'nonzero_common_perturbation':'strictly larger than unchanged minimum',
            'search_seed':partition['seed'],'completed_partition_trials':partition['completed_trials']}
