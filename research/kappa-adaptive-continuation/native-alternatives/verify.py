#!/usr/bin/env python3
"""Bind the literal receiver rewrite to both fresh complete native receipts.

This is a receipt/binding verifier. The retained native engines perform the
all-column and phase proofs; architecture/review_receiver.py is the separate
independent local identity/frame review. Apache-2.0.
"""
import argparse,gzip,json
from hashlib import sha256
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXPECTED_SOURCE={
 'base':'5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699',
 'extra':'965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e'}
EXPECTED_PROFILE={'1':2439,'2':724,'3':225,'4':102,'5':20,'8':8}
EXPECTED_WIDTHS={'4':26,'5':2,'6':18,'7':53,'8':96,'9':213}
STEPS=['native','ledgers','local-replay','wrappers','phases']

def digest(p):return sha256(p.read_bytes()).hexdigest()
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def payload(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def verify(root):
    construction=read(root/'candidate/CONSTRUCTION.json')
    assert construction['status']=='PASS_BOTH_PROVIDER_LITERAL_RECEIVER_SHARING'
    assert construction['constructor_sha256']==digest(root/'construct.py')
    providers={};common_widths=None
    for tag in ('base','extra'):
        rec=construction['providers'][tag]
        assert rec['source_sha256']==EXPECTED_SOURCE[tag]
        wp=root/'candidate'/rec['word'];word=read(wp)
        assert digest(wp)==rec['word_sha256'] and payload(word)==rec['word_payload_sha256']
        assert word['report']['local_profile']==EXPECTED_PROFILE
        assert word['report']['width_inventory']==EXPECTED_WIDTHS
        work=root/f'native-{tag}';result=read(work/'RESULT.json')
        assert result['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY'
        assert result['word_sha256']==digest(wp)
        assert [x['step'] for x in result['steps']]==STEPS
        assert all(x['exit_code']==0 for x in result['steps'])
        local=work/'native/local';canonical=read(local/'CANONICAL-WORD.json.gz')
        scalar=read(local/'SCALAR-FRAME-AUDIT.json');programs=read(local/'LOCAL-CHECKS.json')
        independent=read(local/'INDEPENDENT-LOCAL-REPLAY.json')
        wrappers=read(local/'WRAPPER-CHECKS.json');phase=read(local/'CLIFFORD-REVIEW.json');warp=read(local/'WARP-RECIPE-CHECKS.json')
        assert scalar['status']=='PASS_BORROW_WORD_FREE_ALGEBRA_ALL_COLUMNS_AND_NATIVE_FRAMES'
        assert scalar['input_content_sha256']==rec['word_payload_sha256']
        assert scalar['local_profile']==EXPECTED_PROFILE and scalar['local_rank_mass']==5134
        assert scalar['live_columns_each_orientation']==632 and scalar['helpers']==408 and scalar['zero_buffers']==91
        assert len(canonical['zero_buffers'])==91
        if common_widths is None:common_widths=scalar['widths']
        assert scalar['widths']==common_widths
        assert independent['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
        assert independent['canonical_word_sha256']==digest(local/'CANONICAL-WORD.json.gz')
        assert independent['local_programs_sha256']==digest(local/'LOCAL-PROGRAMS.json.gz')
        for orientation in ('forward','backward'):
            p=programs[orientation];ind=independent['local'][orientation]
            assert p['paid_profile']==EXPECTED_PROFILE and p['all_columns']==632
            assert p['private_centers_cleared'] and p['private_coefficient_stream_cleared_after_each_macro']
            assert p['zero_buffers_returned_to_zero']==91
            assert ind['all_exact_columns']==632 and ind['warp_columns_each_exact']==512
            assert ind['private_work_erased'] and ind['zero_buffers_returned_to_zero']==91
            assert ind['prefix_bits_upper']<=128 and ind['charged_payload_bits']==192
        assert wrappers['status']=='PASS_RESIDUAL_WRAPPERS_ARE_EXACT'
        assert phase['status']=='PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES'
        assert phase['all_child_equalities_include_global_phase'] and phase['warp_recipes_equal_exact_512_column_product']
        assert warp['status']=='PASS_WARP_RECIPES_EXACT_ON_ALL_512_COLUMNS' and warp['columns_each']==512
        assert warp['operators']==72 and warp['warp_classes']==180
        assert phase['recipe_sha256']==warp['recipe_sha256']==digest(local/'CLIFFORD-RECIPES.json')
        providers[tag]=dict(word=wp.relative_to(root).as_posix(),word_sha256=digest(wp),word_payload_sha256=rec['word_payload_sha256'],
            canonical_word= (local/'CANONICAL-WORD.json.gz').relative_to(root).as_posix(),canonical_word_sha256=digest(local/'CANONICAL-WORD.json.gz'),
            exact_columns_each_orientation=632,helpers=408,zero_buffers=91,rank_mass=5134,
            primitive_bounds={o:programs[o]['real_component_primitive_bound'] for o in ('forward','backward')},
            prefix_bits={o:independent['local'][o]['prefix_bits_upper'] for o in ('forward','backward')},
            local_rejection_controls=len(independent['negative_controls_rejected']),warp_rejection_controls=len(warp['controls_rejected']),
            receipt_sha256={p.relative_to(root).as_posix():digest(p) for p in (work/'RESULT.json',local/'SCALAR-FRAME-AUDIT.json',local/'LOCAL-CHECKS.json',local/'INDEPENDENT-LOCAL-REPLAY.json',local/'WRAPPER-CHECKS.json',local/'CLIFFORD-REVIEW.json',local/'WARP-RECIPE-CHECKS.json')})
    return dict(status='PASS_LITERAL_RECEIVER_SHARING_BOTH_NATIVE_PROVIDERS',local_profile=EXPECTED_PROFILE,width_inventory=EXPECTED_WIDTHS,
        per_call_delta={'1':-1,'2':-1,'3':1},providers=providers,
        scope='Both literal words and all native obligations are verified; complete owner/invoice/outer admission is bound in the parent continuation package.')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--package',type=Path,default=HERE);ap.add_argument('--output',type=Path)
    a=ap.parse_args();result=verify(a.package)
    out=a.output or a.package/'NATIVE-SUMMARY.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],result['local_profile'])

if __name__=='__main__':main()
