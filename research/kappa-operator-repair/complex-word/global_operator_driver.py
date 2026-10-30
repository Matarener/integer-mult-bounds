#!/usr/bin/env python3
"""Run a declared bounded search in the exact K_G quotient, not free labels."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import importlib, json, sys
from network_search import F,OLD,ROOT,HERE
from operator_quotient import install


def main():
    ap=ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=('literal','monomial'),default='literal')
    ap.add_argument('--search',choices=('network_search','response_routes','multi_response_routes_v2','interval_search','delayed_queries_joint','response_all_helpers','multi_response_all_helpers','response_global_frames'),required=True)
    args,rest=ap.parse_known_args()
    def argument(name,default=None):return rest[rest.index(name)+1] if name in rest else default
    source=Path(argument('--word',str(OLD/'candidate/BORROW-WORD-43base.json.gz')))
    output=Path(argument('--output'));output.mkdir(parents=True,exist_ok=True)
    word=F.read(source);q=install(word,args.mode)
    certificate=q.certificate();certificate['word_sha256']=sha256(source.read_bytes()).hexdigest()
    certificate_path=output/'OPERATOR-QUOTIENT.json'
    certificate_path.write_text(json.dumps(certificate,sort_keys=True,indent=2)+'\n')
    import exact_rows
    rows,_=exact_rows.replay(word);assert rows==exact_rows.expected(word),'retained all-input identity in exact quotient'
    # Import the search only after patching its imported exact primitives.
    module=importlib.import_module(args.search)
    if hasattr(module,'execute'):module.execute=exact_rows.execute
    if hasattr(module,'replay'):module.replay=exact_rows.replay
    if hasattr(module,'backward'):
        import response_routes
        module.backward=response_routes.backward
    sys.argv=[str(Path(module.__file__))]+rest
    module.main()
    result_path=output/'RESULT.json';result=json.loads(result_path.read_text())
    result['operator_semantics']='actual K_G; literal equal-G quotient' if args.mode=='literal' else 'actual K_G; exact full monomial-product equality'
    result['operator_quotient_certificate_sha256']=sha256(certificate_path.read_bytes()).hexdigest()
    result['nonfree_product_identifications']=q.nonfree_identifications
    result['exact_operator_products_seen']=len(q.representatives)
    for path in (Path(__file__),HERE/'operator_quotient.py'):
        result.setdefault('source_sha256',{})[str(path.relative_to(ROOT))]=sha256(path.read_bytes()).hexdigest()
    result['source_sha256'][str(source.relative_to(ROOT)) if source.is_absolute() else str(source)]=sha256(source.read_bytes()).hexdigest()
    result['native_admission']=False
    result['scope_note']='Any exact_free_operator_identity field inherited from a search denotes the declared actual-operator quotient here. Physical frame/phase checks and complete invoice remain distinct admission gates.'
    result_path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('QUOTIENT',args.mode,'products',len(q.representatives),'relations',len(q.nonfree_identifications),flush=True)


if __name__=='__main__':main()
