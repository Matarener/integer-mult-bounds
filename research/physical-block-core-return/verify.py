"""Actual Core RHS, complete physical baseline/refinement and exact oracle."""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent


def need(ok,message):
    if not ok: raise ValueError(message)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def logical(tape):
    from session import borrowed_tape
    cells=bytes(borrowed_tape(tape).cells)
    end=cells.find(bytes([4]),1)
    if end<0:end=len(cells)
    need(all(v==4 for v in cells[end:]),'erased logical suffix')
    return cells[1:end]


def signed(raw,width,precision):
    need(len(raw)%width==0,'complete observed signed records')
    return [Q(sum(x<<i for i,x in enumerate(raw[start:start+width]))-(raw[start+width-1]<<width),1<<precision)
            for start in range(0,len(raw),width)]


def case(quick=False):
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_core import Core
    from gaussian_matrix import Matrix
    from gaussian_rationals import Rational
    from records import Tape
    from ring_check_words import decode
    from ring_words import Signed
    from router_metadata import owned
    from session import initialize_marker,erase_marker,sealed_constructors,borrowed_tape
    from words import BLANK
    from boundary_pages import prepare_pages
    from block_core import BlockCore
    from source_fixture import fixture
    from stability import finish,ledger,interior
    tapes=[]; old_init=Tape.__init__
    def track(t):old_init(t);tapes.append(t)
    Tape.__init__=track
    try:
        setup=Core();setup_bank=list(tapes);owners=[];banks=[]
        for retain in ((True,) if quick else (True,False)):
            start=len(tapes);owners.append(BlockCore(retain));banks.append(tapes[start:])
        page,source,lower,upper,expected_rhs,width,P,detail=fixture()
        dirty=Tape()
        for bit in (1,0,1,1,0,1):dirty.append(bit)
        dirty.rewind()
        snapshots=[(bytes(t.cells),t.head) for t in (page,source,dirty)]
        def meter():return [sum(getattr(t.meter,k) for t in tapes) for k in ('reads','writes','moves')]
        def diff(a):return [v-u for v,u in zip(meter(),a)]
        for t in setup.pool.tapes:initialize_marker(t)
        pages=();matrices=[]
        with owned(Count.literal(4),Count.literal(len(lower)),Count.literal(width),Count.literal(P)) as (block,n,w,precision):
            try:
                with sealed_constructors(),setup.scope.installed():
                    def make(v):return Rational(Signed(Count.literal(abs(v.numerator)),v<0),Count.literal(v.denominator))
                    before=meter()
                    matrices=[Matrix(n,n,setup.pool,lambda i,j,a=a:make(a[decode(i)][decode(j)])) for a in (lower,upper)]
                    with no_decode():pages=prepare_pages(*matrices,block,w,precision,setup.pool)
                    preparation=diff(before)
                    saved=[(bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in (*pages,block.tape)]
                    oracle=load('block_core_fraction',ROOT/'research/physical-boundary-pages/verify.py')
                    padded=oracle.oracle(lower,upper,[list(v) for v in zip(*expected_rhs)],4,P)
                    xb=[[padded[4*i+c] for i in range(len(lower))] for c in (0,1)]
                    expected,trace=finish(detail,xb,P)
                    need(any(expected),'nonzero normalized output discriminator')
                    boundary_bound=max(map(abs,sum(xb,[])))
                    input_bound=max(abs(z) for pair in detail['target'] for z in pair)
                    coupling=max(sum(abs(detail['matrix'][i][j]) for j in detail['boundary']) for i in detail['inside'])
                    bound=ledger(detail['factors'],input_bound,boundary_bound,coupling,Q(1,1<<P),detail['p'],P,width)
                    need(bound['width_ok'] and bound['disk_ok'],'nonvacuous explicit width/disk premises')
                    for component in trace:
                        for j,stage in enumerate(component):need(max(map(abs,stage))<=bound['magnitudes'][j+1],'actual seven-stage magnitude bound')
                    results=[]
                    for owner,bank in zip(owners,banks):
                        before=meter();interior_calls=owner.interior.calls
                        with setup.scope.suspended(),no_decode():
                            out=owner.run(page,source,pages,block)
                            raw=logical(out);out.clear();erase_marker(out);owner.idle()
                        paid=diff(before)
                        need(signed(raw,detail['p']+2,detail['p'])==expected,'actual normalized Core block return independent oracle')
                        need(owner.interior.calls-interior_calls==4,'both actual interior passes for both components')
                        need(owner.blocks.calls==1 if hasattr(owner.blocks,'calls') else owner.blocks.products==2,'actual block consumer executed')
                        need(saved==[(bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in (*pages,block.tape)],'factor banks/metadata restored')
                        need(snapshots==[(bytes(t.cells),t.head) for t in (page,source,dirty)],'original page/source/dirty spectator restored')
                        need(owner.closed and not owner.pool.live and all(t.head==1 and all(v==BLANK for v in t.cells) for t in owner.pool.tapes),'complete owner cleanup')
                        results.append(dict(retain=owner.retain,total=sum(paid),reads_writes_moves=paid,
                                            retained_owner_cells=sum(len(t.cells) for t in bank),owner_tapes=len(bank),
                                            complete_retained_cells=sum(len(t.cells) for t in (*bank,*setup_bank,page,source,block.tape,n.tape,w.tape,precision.tape)),
                                            output_sha256=hashlib.sha256(raw).hexdigest(),output=[str(x) for x in expected],interior_calls=4))
                    # Actual final disk guard and isolated numerical falsifying controls.
                    with no_decode(),owned(Signed(Count.literal(17)),Signed(Count.literal(0))) as (a,b):
                        from gaussian_page import Header
                        page.rewind();header=Header(page)
                        rejected=False
                        try:setup.norm(a,b,header)
                        except (ValueError,AssertionError):rejected=True
                        finally:header.close();page.rewind()
                        need(rejected,'actual final disk rejects oversized normalized value')
                    changed=[list(v) for v in xb];changed[0][0]+=64
                    changed_output,_=finish(detail,changed,P)
                    need(changed_output!=expected,'boundary return reaches observable final output')
                    changed=[list(v) for v in xb];changed[0][0]+=Q(1,1<<P)
                    perturbed,_=finish(detail,changed,P)
                    need(max(abs(a-b) for a,b in zip(expected,perturbed))<=bound['output_difference'],'explicit paired error bound')
                    need(not ledger(detail['factors'],input_bound,128,coupling,Q(),detail['p'],P,width)['disk_ok'],'missing disk margin rejected')
                    need(not ledger(detail['factors'],input_bound,boundary_bound,coupling,Q(),detail['p'],P,P+1)['width_ok'],'missing intermediate headroom rejected')
                    return dict(schedules=results,preparation_reads_writes_moves=preparation,
                                preparation_owner_retained_cells_after_controls=sum(len(t.cells) for t in setup_bank),
                                supplied_factor_page_backing=sum(len(borrowed_tape(t).cells) for t in pages),
                                original_page_source_backing=sum(len(t.cells) for t in (page,source)),
                                numerical_ledger=json.loads(json.dumps(bound,default=str)),
                                controls=['nonzero cropped normalized output','four actual interior calls','boundary perturbation changes final output',
                                          'paired seven-stage rounding bound','actual disk rejection','insufficient width rejection','insufficient disk margin rejection'])
            finally:
                for t in pages:t.clear()
                for m in matrices:m.close()
                setup.pool.empty()
                for t in setup.pool.tapes:erase_marker(t)
    finally:Tape.__init__=old_init


def receipt_types(receipt):
    for row in receipt['case']['schedules']:
        for key in ('total','interior_calls','owner_tapes','retained_owner_cells','complete_retained_cells'):
            need(type(row[key]) is int, 'strict receipt count type')
        need(all(type(v) is int for v in row['reads_writes_moves']), 'strict receipt counter type')
        need(type(row['retain']) is bool, 'strict receipt schedule type')
    for key in ('width_ok','disk_ok'):
        need(type(receipt['case']['numerical_ledger'][key]) is bool, 'strict receipt predicate type')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--quick',action='store_true');args=parser.parse_args()
    if not args.write and not args.quick:receipt_types(json.loads((HERE/'RESULT.json').read_text()))
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source pin '+row['path'])
    for row in json.loads((HERE/'PREDECESSOR.json').read_text())['files']:
        need(hashlib.sha256((HERE/row['local_path']).read_bytes()).hexdigest()==row['local_sha256'],'retained helper pin')
    sys.path[:0]=[str(ROOT/'research/physical-gaussian-core'),str(ROOT/'research/physical-boundary-pages')]
    import gaussian_sources
    with gaussian_sources.opened():
        sys.path.insert(0,str(HERE));result=dict(status='PASS_PHYSICAL_BLOCK_CORE_RETURN',case=case(args.quick))
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    elif not args.quick:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True),'complete typed receipt')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
