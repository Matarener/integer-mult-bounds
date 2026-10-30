#!/usr/bin/env python3
"""Exclude tariff<=55 for eleven-term/two-unit cold scalar factors.

The saved result does not exclude tariff56 or arbitrary extensions.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
from cold_cosets import bits,bxor,inverse2,rank2,rankmod,need

HERE=Path(__file__).resolve().parent

def receipt():
    source=HERE/'READOUT-FLOOR.json';ninepath=HERE.parent/'cold-reader/NINE-TERM-FLOOR.json'
    src=json.loads(source.read_text());nine=json.loads(ninepath.read_text())
    R,K,roots=src['R'],src['K'],src['root_lines']
    code=[0]
    for r in R:code += [d^r for d in code]
    lookup={word:i for i,word in enumerate(code)}
    M=[bxor(R[j]for j in bits(k))for k in K]
    allbits=(1<<111)-1
    gram=[sum(((sum(a*b for a,b in zip(q,p))//2)&1)<<j for j,p in enumerate(roots))for q in roots]
    need(all(not sum(a*b for a,b in zip(q,p))%2 for q in roots for p in roots),'integral root Gram/2')
    need(M==[allbits^g for g in gram],'actual correction is the affine orthogonality kernel')
    need(all((M[i]>>j&1)==(M[j]>>i&1)for i in range(111)for j in range(111)),
         'actual symmetry permits source/target transposition')
    need(len(set(M))==111 and all(m in lookup for m in M),'111 distinct live affine-code directions')
    source_special=nine['support_strata'][0]['rank7_rows']
    target_special=nine['support_strata'][1]['rank7_rows']
    target_words={sum(((k&r['mask']).bit_count()%2)<<p for p,k in enumerate(K))for r in target_special}
    need(target_words==set(R),'source and target have the same nine physical special directions')
    normals=[r['normal']for r in source_special]
    need([r['mask']for r in source_special]==[1<<j for j in range(9)],'pinned source normal order')
    unit_receipts=[];rank_hist=Counter();census=0
    for a,q in enumerate(roots):
        e=1<<a;cap=M[a]^e
        need(all(not(sum(x*y for x,y in zip(q,roots[p])))for p in bits(cap)),'new live cap exact orthogonality')
        rank7={}
        for j,(r,n)in enumerate(zip(R,normals)):
            if not sum(x*y for x,y in zip(n,q)):rank7[1<<j]=n
        rank7[lookup[M[a]]]=q
        hist=Counter()
        for u,d in enumerate(code[1:],1):
            w=d^e;r=rankmod(w,roots);hist[r]+=1;rank_hist[r]+=1;census+=1
            need(r in(7,8),'unit extension has no second low-span nonzero direction')
            need((r==7)==(u in rank7),'complete rank7 unit-extension directions')
            if r==7:
                n=rank7[u]
                need(all(not sum(x*y for x,y in zip(n,roots[p]))for p in bits(w)),
                     'modular rank7 has a rational null normal witness')
        unit_receipts.append({'live_unit':a,'root':q,'f_a_code_mask':lookup[M[a]],
                              'toggled_nonzero_D_rank_histogram':dict(sorted(hist.items())),
                              'toggled_rank7_code_masks_and_normals':[[u,n]for u,n in sorted(rank7.items())]})
    need(census==111*511,'all nonzero codeword plus unit tests')
    bases=[];dual_count=Counter();admissible=0
    for b,m in enumerate(M):
        h=lookup[m]
        for omitted in range(10):
            U=[1<<j for j in range(9)]+[h];U.pop(omitted)
            if rank2(U)<9:continue
            inv=inverse2(U)
            cols=[sum((inv[j]>>i&1)<<j for j in range(9))for i in range(9)]
            V=[sum(((k&col).bit_count()%2)<<p for p,k in enumerate(K))for col in cols]
            count=sum(v not in target_words for v in V);dual_count[count]+=1
            need(count==9,'all nine dual targets are generic D directions')
            need(len(set(V))==9 and all(v in lookup for v in V),'exact independent target duals')
            # For any target unit a only its own f_a code direction can become
            # a new hyperplane; nine distinct generic duals cannot all do so.
            possible_a={M.index(v)for v in V if v in M}
            for a in possible_a:
                if all(v in target_words or v==M[a]for v in V):admissible+=1
            bases.append({'source_unit':b,'omitted_code_label':omitted,'source_code_basis':U,
                          'all_nine_generic_dual_code_masks':[lookup[v]for v in V]})
    need(len(bases)==638 and admissible==0,'complete638 basis test rejects tariff54 core')
    return {'status':'PASS_TWO_UNIT_ELEVEN_TERM_SCALAR_COLD_PAIRING_TARIFF_GE56',
        'no_new_kappa':True,'scientific_pin':src['scientific_pin'],
        'sources':{str(p):sha256(p.read_bytes()).hexdigest()for p in(source,ninepath)},
        'R':R,'K':K,'live_roots':roots,'actual_KR_rows':M,
        'exact_affine_orthogonality_kernel':True,'all111_diagonal_coefficients':1,
        'toggled_nonzero_codewords_tested':census,'combined_toggled_rank_histogram':dict(sorted(rank_hist.items())),
        'unit_extension_hyperplane_census':unit_receipts,
        'source_hyperplane_code_bases':bases,'basis_count':638,
        'generic_target_count_histogram':dict(sorted(dual_count.items())),
        'admissible_nine_hyperplane_cores':admissible,
        'covered_model':'Eleven exact binary outer-product terms KR=sum b_i c_i^T. Source readers lie in D+<unit_b>, target readers in D+<unit_a>, for any two live coordinates a,b. Each term costs rational source/target root-span pairing rank. Total tariff<=55 is excluded.',
        'proof':'Every nonzero codeword has weight>=48; the complete modular rank and rational-null census shows the sole low<=6 direction in each one-unit extension is its unit, and the only rank7 code labels are the nine old labels and f_unit. In the D-by-D quotient, rank(KR)=9 forces at least nine terms with both code parts nonzero. Each such high/high term has source/target span>=7, hence pairing rank>=6. Ten or eleven high/high terms cost>=60. A total tariff<=55 therefore has exactly nine high/high terms with baseline54 and at most one excess unit. At least one side has all nine spans7: a span8 term on each side either costs8 when in the same term, or gives two terms of cost>=7. Transpose the exactly symmetric M if needed so all source spans are7. Their quotient code parts form two dual bases. The638 possible source bases drawn from the ten hyperplane labels all have nine generic rank8 dual target code directions. In a target one-unit extension at most one distinct generic code direction can become rank7, namely f_a. Thus at least eight target spans remain8 and their core tariff is>=8*7+6=62, a contradiction. This holds regardless of unit toggle choices or tail equations.',
        'limits':['No floor60 is claimed for the full eleven-term model: a nine-high/two-tail profile at tariff56..59 may use rank8 directions on both sides, outside the ten-label basis census.',
                  'No bound for larger extensions, changed D, shared native queries or operator-valued factors.',
                  'Pairing rank is an optimistic necessary tariff, not native COPY/ERASE admission or dirt restoration.'],
        'attribution':'Root proposed the eleven-term two-unit C54 construction. BIT lane identified the additional live-cap direction and supplies the complete unit-extension span census,638 exact dual bases and the corrected scoped rejection.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    out=json.loads(json.dumps(receipt()));path=HERE/'UNIT-COLD-EXTENSION.json'
    if args.write:path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_bytes())==out,'saved two-unit receipt differs')
    print(out['status']);print('56721 span tests;638 exact dual bases; no tariff<=55 two-unit factor')

if __name__=='__main__':main()
