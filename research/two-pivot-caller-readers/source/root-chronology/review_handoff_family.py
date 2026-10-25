#!/usr/bin/env python3
"""Independent full-column replay of serialized scalable handoff caller fixtures.
Apache-2.0; substantial OpenAI Codex assistance. This is not a kappa claim.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import argparse,hashlib,json
from chronology import Op,ident,native,swap,need
from batch_paid_progress import replay,left,schedule
HERE=Path(__file__).resolve().parent


def run():
    pp=HERE.parent/'caller/HANDOFF-FAMILY.json';tp=HERE.parent/'native-frames/HANDOFF-FAMILY-TAIL.json'
    pdata,tdata=json.loads(pp.read_bytes()),json.loads(tp.read_bytes())
    prefixes={x['q']:x for x in pdata['fixtures']};out=[]
    for tail in tdata['fixtures']:
        q=tail['q'];p=prefixes[q];banks=2*q+2;planes=2*q+2;ambient=2*planes
        I=ident(planes);N=native(planes,0);events=list(p['events'])
        for e in tail['tail_events']:
            if e['op']=='ADD':events.append(dict(kind='ADD',dst=e['dst'],src=e['src'],coefficient=str(e['coefficient']),label='tail affine reader'))
            elif e['op']=='BANK_SWAP':events.append(dict(kind='BANK_SWAP',banks=e['banks'],label='tail bank swap'))
            else:
                g=Op(e.get('sign',1),0,I.perm)
                for letter in e['word']:
                    inv=letter.endswith('^-1');letter=letter.removesuffix('^-1')
                    h=N if letter=='N' else swap(planes,int(letter[1:]));g=g@(h.inverse()if inv else h)
                need(2*g.mask.bit_count()==e['native_arity_per_f'],'tail arity independently recomputed')
                events.append(dict(kind='NATIVE'if g.mask else'ADDRESS_OR_UNIT',bank=e['bank'],operator=g.data(),label='generic tail '+e['op']))
        E=I
        for j in range(planes):E=E@native(planes,j)
        target=[[left(E,{I:Fraction(1)})if i==j else{}for j in range(banks)]for i in range(banks)]
        need(replay(events,banks,planes)==target,'complete arbitrary original input columns q='+str(q))
        grouped,decisions=schedule(events,banks,planes,ambient)
        need(replay(grouped,banks,planes)==target,'all grouped endpoint columns q='+str(q))
        H=Counter(e['operator']['native_arity']for e in events if e['kind']=='NATIVE');G=Counter(e['operator']['native_arity']for e in grouped if e['kind']=='NATIVE')
        need(H=={2:banks*(2*q+1)+2*q+4,4:1},'whole native histogram q='+str(q))
        mass=sum(r*c for r,c in H.items());stock=banks*ambient
        need(mass==stock+8 and sum(r*c for r,c in G.items())==mass,'constant unfavorable deficit exactly-8')
        need(all(2*r*r<ambient*ambient for r in G),'strict child contraction')
        mutant=[e for e in grouped if e.get('label')!='paid grouped pending progress']
        need(replay(mutant,banks,planes)!=target,'omitted paid progress fails')
        out.append(dict(q=q,status='PASS_INDEPENDENT_COMPLETE_HANDOFF_FAMILY_FIXTURE',no_new_kappa=True,width=banks,ambient_arity=ambient,ungrouped_histogram=dict(sorted(H.items())),grouped_histogram=dict(sorted(G.items())),native_mass=mass,stock=stock,deficit=-8,events=events,grouped_events=grouped,grouping_decisions=decisions,all_original_columns=banks,both_literal_inverse_orders=True,negative_control='omitted grouped progress rejected'))
    return dict(status='PASS_INDEPENDENT_COMPLETE_HANDOFF_FAMILY',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(pp,tp,HERE/'chronology.py',HERE/'batch_paid_progress.py')},fixtures=out,domain='Every f>=1 for each explicitly serialized q fixture, actual signed native planes, all arbitrary independent input fields and both literal inverse orders.',limits=['Written all-q induction is separate from finite fixture replay.','Complete native rankmass exceedsstock by8; no positive moment or kappa.','Different joint cleanup or changed source/held map remains outside this computation.'])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();out=json.loads(json.dumps(run()))
    p=HERE/'INDEPENDENT-HANDOFF-FAMILY.json'
    if args.write:
        p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        for f in out['fixtures']:
            f=dict(f,sources=out['sources'],producer_sha256=out['producer_sha256']);(HERE/f"HANDOFF-COMPLETE-Q{f['q']}.json").write_text(json.dumps(f,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==out,'saved family audit differs')
    print(out['status'],[(f['q'],f['native_mass'],f['stock'],f['grouped_histogram'])for f in out['fixtures']])
if __name__=='__main__':main()
