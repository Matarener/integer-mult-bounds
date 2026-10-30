#!/usr/bin/env python3
"""Exact Gaussian linear-independence audit for actually encountered products.

This closes a stronger possible equality relaxation for the retained word:
not only product equality but arbitrary rational linear relations among its
forward/reverse response operator products. It does not cover products that
a different construction would newly introduce.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import json
from network_search import ROOT,HERE,FROZEN,F,OLD
from operator_quotient import install,serial


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--word',type=Path)
    args=ap.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    source=args.word or OLD/'candidate/BORROW-WORD-43base.json.gz';word=F.read(source);q=install(word,'monomial')
    certificate=q.certificate()
    import exact_rows,response_routes
    final,captures=exact_rows.replay(word);assert final==exact_rows.expected(word)
    sec=F.expand(word);live=set(range(704))-set(word['removed']);outputs=set(range(112,224))|set(map(int,word['helper_final']))
    cols={r:{(r,()):Q(1)} if r in outputs else {} for r in live}
    for e in reversed(sec['A']+word['cut']+sec['B']+sec['restore']):response_routes.backward(cols,e)
    basis={};dependencies=[];products=[];started=monotonic()
    for operators,(p,z) in sorted(q.matrix_cache.items(),key=lambda a:(len(a[0]),a[0])):
        # A monomial has exactly one Gaussian unit in each of512 columns.
        # Real and imaginary coordinates are separate rational coordinates.
        vector={(p[x],x,z[x]&1):Q(1 if z[x]<2 else -1) for x in range(512)}
        support={operators:Q(1)};pivot=None
        while vector:
            k=min(vector)
            if k not in basis:
                c=vector[k];basis[k]=({a:b/c for a,b in vector.items()},{a:b/c for a,b in support.items()});pivot=list(k);break
            other,weights=basis[k];c=vector[k]
            exact_rows.add(vector,other,-c);exact_rows.add(support,weights,-c)
        if not vector:dependencies.append([{'word':list(k),'coefficient':str(v)} for k,v in sorted(support.items())])
        products.append({'operator_word':list(operators),'exact_monomial_sha256':sha256(serial((p,z))).hexdigest(),'rational_pivot':pivot})
    assert len(basis)==len(products)==71 and not dependencies
    paths=[Path(__file__),HERE/'operator_quotient.py',HERE/'network_search.py',HERE/'response_routes.py',source,FROZEN/'exact_rows.py']
    result={'status':'EXACT_ENCOUNTERED_GAUSSIAN_OPERATOR_RANK_PASS','native_admission':False,
            'full_retained_all_input_identity':True,'live_independent_inputs':len(live),'restored_private_zero_buffers':len(word['helper_final']),
            'operator_quotient_certificate':certificate,'actual_product_count':len(products),'rational_rank':len(basis),'dependencies':dependencies,
            'operator_word_length_counts':dict(Counter(len(p['operator_word']) for p in products)),
            'products':products,'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'Actual logical K_G product matrices encountered by full retained-word replay plus backward TARGET and HPE output-response replay. All512 Gaussian columns and their phases are retained. Rank over Q is exact on separate real/imaginary entries. Products introduced by future changed words are outside this finite certificate.'}
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS',len(products),len(basis),flush=True)


if __name__=='__main__':main()
