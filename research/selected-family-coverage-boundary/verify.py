#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind the two-unpaid premise to the selected per-family coverage contract.

Clear1nsight with substantial OpenAI assistance. Credit Sagar Thakrar/PR1012
for the coverage identity and Nick Petalas/PR3754 with PR3747/1685 for pooling.
This audits the actual selected ledger, not the legality of every new decoder.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCHIVE='research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA='f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBERS={
 'global':('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz','2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
 'program':('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz','241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
 'word':('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz','16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219')}


def need(ok,message):
    if not ok: raise ValueError(message)


def canon(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def digest(value): return sha256(canon(value)).hexdigest()


def load(root=ROOT):
    path=root/ARCHIVE
    need(path.is_file() and not path.is_symlink(),'regular archive')
    need(sha256(path.read_bytes()).hexdigest()==ARCHIVE_SHA,'archive hash')
    out={}
    with tarfile.open(path) as archive:
        for key,(name,expected) in MEMBERS.items():
            hits=[m for m in archive.getmembers() if m.name==name]
            need(len(hits)==1 and hits[0].isfile(),'unique regular member')
            raw=archive.extractfile(hits[0]).read()
            need(sha256(raw).hexdigest()==expected,'member hash')
            out[key]=json.loads(gzip.decompress(raw))
    return out


def binary_rank(vectors):
    basis={}
    for value in vectors:
        need(type(value) is int and value>=0,'binary frame vector')
        while value:
            p=value.bit_length()-1
            if p not in basis: basis[p]=value; break
            value ^= basis[p]
    return len(basis)


def validate_family_rows(rows,m=73,unpaid=1):
    need(type(unpaid) is int and unpaid>=0,'integer unpaid coordinate count')
    for family,k,hosted,idle in rows:
        need(all(type(x) is int and x>=0 for x in (family,k,hosted,idle)),'nonnegative family ledger')
        need(8*k+hosted+idle+unpaid==m,'family coverage mismatch at '+str(family))


def aggregate_mass(rows,centres):
    return sum(8*k+h+i for f,k,h,i in rows)+centres


def run(data):
    t,word,program=data['global'],data['word'],data['program']
    W,m,N=t['live'],t['m'],len(t['calls'])
    need((W,m,N)==(14336,73,144),'selected dimensions')
    need(len(t['local_providers'])==1,'one provider')
    (pid,provider),=t['local_providers'].items()
    v,R,widths=provider['v'],provider['R'],provider['widths']
    need(v==112 and len(widths)==R and 2*v+R==704,'selected provider arity')
    frame_ranks=[binary_rank(f) for f in word['frames']]
    increments=[frame_ranks[b]-frame_ranks[a] for a,b in zip(word['start'],word['final'])]
    need(len(increments)==704 and increments[:224]==[8]*224,'data boundary increments')
    need(increments[224:]==widths,'helper boundary widths')
    local_profiles={}
    centre_counts={}
    for orientation in ('forward','backward'):
        events=program[orientation]
        prof=Counter(e[5] for e in events if e[0]=='climb' and e[5]>0)
        centres=[e[4] for e in events if e[0]=='center']
        need(centres==[8]*8,'eight rank-eight centre occurrences')
        need(sum(r*n for r,n in prof.items())==sum(increments),'ordinary climb mass equals endpoints')
        prof.update(centres); local_profiles[orientation]=dict(sorted(prof.items())); centre_counts[orientation]=sum(centres)
    need(local_profiles['forward']==local_profiles['backward'],'both local orientation invoices')
    profile=local_profiles['forward']; local_mass=sum(r*n for r,n in profile.items())
    need(local_mass==5586,'selected local mass')
    data_inc=Counter(); hosts=Counter(); call_slots=Counter(); call_counts=Counter()
    for call in t['calls']:
        need(call['provider_id']==pid,'provider dispatch')
        need(call['local_program_sha256']==digest(program[call['orientation']]),'call/program binding')
        owners=call['owners']; need(len(owners)==704 and len({o[0] for o in owners})==704,'owner injectivity')
        call_counts[call['replica']]+=1
        for role,(family,route) in enumerate(owners):
            need(0<=family<W and ((route[0]==1)==(role<224)),'owner type')
            if role<224: data_inc[family]+=1
            else:
                width=widths[role-224]; hosts[family]+=width
                call_slots[(family,role-224,width)]+=1
    need(call_counts==Counter({i:9 for i in range(16)}),'nine calls per replica')
    pooled=Counter(); slot_widths=Counter()
    for slot in t['hosting']['pooled_slots']:
        need(slot['width']==widths[slot['helper']],'slot/helper width')
        pooled[slot['family']]+=slot['width']
        slot_widths[(slot['family'],slot['helper'],slot['width'])]+=1
    need(pooled==hosts and slot_widths==call_slots,'literal slots equal all call occurrences')
    idle=Counter(); idle_hist=Counter()
    for child in t['idle_children']:
        need(child['replicas']==1 and 0<child['rank']<=51 and 0<=child['family']<W,'idle child')
        idle[child['family']]+=child['rank']; idle_hist[child['rank']]+=1
    rows=[[f,data_inc[f],hosts[f],idle[f]] for f in range(W)]
    validate_family_rows(rows)
    # An independently accumulated certificate avoids normalising by calls:
    # begin with every actual physical family and subtract each bound payload.
    residual=[73 for _ in range(W)]
    for call in t['calls']:
        for role,(family,_) in enumerate(call['owners']): residual[family]-=increments[role]
    for child in t['idle_children']: residual[child['family']]-=child['rank']
    need(residual==[1]*W,'independent endpoint residual per family')
    centre_mass=sum(centre_counts[c['orientation']] for c in t['calls'])
    total=aggregate_mass(rows,centre_mass)
    need(total==N*local_mass+sum(idle.values())==72*W+64*N,'same complete actual rank mass')
    need(sum(idle.values())==237024,'aggregate idle mass')
    # Test the same physical ledger with one extra free coordinate, not a
    # relabelled averaged histogram. It fails at every single physical family.
    failed_two=sum(8*k+h+i+2!=m for f,k,h,i in rows)
    need(failed_two==W,'the second credit requires a changed family contract')
    hypothetical_idle=71*W+centre_mass-N*local_mass
    need(hypothetical_idle==222688,'two-unpaid what-if')
    q,r=divmod(hypothetical_idle,51)
    need((q,r)==(4366,22),'credited pooled integer partition')
    # Every grouping is additive. This changes no conservation identity.
    groups=[]
    for modulus in (1,9,16,73):
        values=[0]*modulus
        for f,k,h,i in rows: values[f%modulus]+=m-(8*k+h+i)
        need(sum(values)==W,'grouping cannot mint unpaid credit')
        groups.append({'modulus':modulus,'total_unpaid':sum(values),'partition_sha256':digest(values)})
    controls=[]
    for label,mutant,unpaid in (
        ('double_count_free_coordinate',rows,2),
        ('deleted_idle_unit',[r[:] for r in rows],1),
        ('moved_idle_unit_to_other_owner',[r[:] for r in rows],1)):
        if label!='double_count_free_coordinate':
            at=next(f for f,k,h,i in mutant if i>0); mutant[at][3]-=1
            if label.startswith('moved'): mutant[(at+1)%W][3]+=1
        try: validate_family_rows(mutant,unpaid=unpaid)
        except ValueError: controls.append(label)
        else: raise ValueError('coverage mutant accepted')
    return {'schema_version':1,'status':'PASS_SELECTED_FAMILY_COVERAGE_BOUNDARY','live':W,'calls':N,'m':m,'helper_roles':R,
      'data_step':8,'helper_width_mass':sum(widths),'local_profile':{str(k):v for k,v in profile.items()},
      'local_mass':local_mass,'actual_paid_mass':total,'ordinary_paid_mass':total-centre_mass,'private_centre_mass':centre_mass,
      'actual_deficit':m*W-total,'idle_mass':sum(idle.values()),'idle_histogram':{str(k):v for k,v in sorted(idle_hist.items())},
      'families_with_exactly_one_unpaid':W,'counterfactual_two_unpaid_failures':failed_two,
      'family_ledger_sha256':digest(rows),'residual_sha256':digest(residual),'grouping_controls':groups,
      'two_unpaid_target_mass':71*W+centre_mass,'extra_ordinary_mass_change_required':W,
      'two_unpaid_hypothetical_idle':hypothetical_idle,'pooled_partition':{'51':q,str(r):1},
      'per_call_unpaid_two_idle':str(Fraction(hypothetical_idle,N)),
      'centre_free_vs_two_unpaid_mass_gap':W-centre_mass,'controls_rejected':controls,
      'changed_decoder_impossibility_claimed':False,'no_new_kappa':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--emit',action='store_true',help='Discovery output; skips committed receipt equality')
    args=parser.parse_args()
    result=run(load(args.root)); expected=HERE/'RESULT.json'
    if not args.emit:
        need(expected.is_file() and not expected.is_symlink(),'missing regular committed result')
        need(canon(json.loads(expected.read_bytes()))==canon(result),'typed result mismatch')
    print('RESULT_JSON='+canon(result).decode()); print(result['status'])


if __name__=='__main__': main()
