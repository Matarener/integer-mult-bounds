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


def case(length,B):
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
    from boundary_pages import BoundaryPages,prepare_pages
    from pair_kernel import PairBoundaryPages
    from source_fixture import fixture
    from source_pair import first_pass_pair
    from rhs_layout import pack
    tapes=[]; original_init=Tape.__init__
    def track(t):original_init(t);tapes.append(t)
    Tape.__init__=track
    try:
        core=Core()
        start=len(tapes);base=BoundaryPages();base_tapes=tapes[start:]
        start=len(tapes);thin=PairBoundaryPages();thin_tapes=tapes[start:]
        page,source,lower,upper,expected_rhs,width_int,P=fixture(length)
        dirty=Tape()
        for b in (1,0,1,1,0,1,1):dirty.append(b)
        dirty.rewind()
        protected=(page,source,dirty)
        snapshots=[(bytes(t.cells),t.head) for t in protected]
        def meter():return [sum(getattr(t.meter,k) for t in tapes) for k in ('reads','writes','moves')]
        def difference(a):return [x-y for x,y in zip(meter(),a)]
        for t in core.pool.tapes:initialize_marker(t)
        rhs=();header=None;matrices=[];pages=();packed=None
        with owned(Count.literal(B),Count.literal(2)) as (block,columns):
            try:
                with sealed_constructors(),core.scope.installed():
                    before=meter()
                    with no_decode():rhs,header=first_pass_pair(core,page,source)
                    first_pass=difference(before)
                    need([signed(logical(t),width_int,P) for t in rhs]==expected_rhs,'actual first-pass RHS independent oracle')
                    def make(v):return Rational(Signed(Count.literal(abs(v.numerator)),v<0),Count.literal(v.denominator))
                    matrices=[Matrix(header.boundary_length,header.boundary_length,core.pool,
                                     lambda i,j,a=a:make(a[decode(i)][decode(j)])) for a in (lower,upper)]
                    with no_decode():
                        pages=prepare_pages(*matrices,block,header.width,header.P,core.pool)
                        packed=pack(*rhs,header.boundary_length,block,header.width,core.pool)
                    ports=(*pages,packed,header.boundary_length.tape,columns.tape,block.tape,header.width.tape,header.P.tape)
                    saved=[(bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in ports]
                    def execute(owner,bank):
                        before=meter();calls=owner.arithmetic.products;products=owner.products
                        with core.scope.suspended(),no_decode():
                            out=owner.run(*pages,packed,header.boundary_length,columns,block,header.width,header.P)
                            raw=logical(out)  # Observer only: no physical action or execution operand.
                            out.clear();erase_marker(out)
                            owner.idle()
                        paid=difference(before)
                        need(saved==[(bytes(borrowed_tape(t).cells),borrowed_tape(t).head) for t in ports],'all borrowed banks/RHS/metadata restored')
                        need(snapshots==[(bytes(t.cells),t.head) for t in protected],'actual source and arbitrary dirty spectator restored')
                        need(owner.closed and not owner.pool.live and all(t.head==1 and all(v==BLANK for v in t.cells) for t in owner.pool.tapes),'all owned work blank after consumption')
                        return raw,dict(reads_writes_moves=paid,total=sum(paid),scalar_products=owner.arithmetic.products-calls,
                                        matrix_products=owner.products-products,retained_owned_cells=sum(len(t.cells) for t in bank),tape_count=len(bank))
                    old,old_cost=execute(base,base_tapes)
                    new,new_cost=execute(thin,thin_tapes)
                    need(new==old,'complete padded output byte equality')
                    oracle=load('pair_fraction_oracle',ROOT/'research/physical-boundary-pages/verify.py')
                    expected=oracle.oracle(lower,upper,[list(v) for v in zip(*expected_rhs)],B,P)
                    need(signed(new,width_int,P)==expected,'independent exact rounded block oracle')
                    n=len(lower);K=(n+B-1)//B;J=(2+B-1)//B
                    need(old_cost['scalar_products']==2*(2*K-1)*J*B**3,'complete dense baseline census')
                    need(new_cost['scalar_products']==2*(2*K-1)*J*B*B*min(B,2),'complete active scalar census')
                    if B>2:
                        need(new_cost['total']<old_cost['total'],'B4 complete physical work improves')
                        need(new_cost['retained_owned_cells']<=old_cost['retained_owned_cells'],'B4 retained backing does not increase')
                    reused,reuse_cost=execute(thin,thin_tapes)
                    need(reused==new and reuse_cost==new_cost,'positive same-owner reuse including exact bill and retained backing')
                    receipt=dict(source_rows=length,boundary_rows=n,block=B,columns=2,width=width_int,precision=P,
                                 actual_first_pass_reads_writes_moves=first_pass,baseline=old_cost,pair_kernel=new_cost,
                                 full_output_sha256=hashlib.sha256(new).hexdigest(),output=[str(x) for x in signed(new,width_int,P)])
                    if length==8:
                        need(any(lower[i][j] for i in range(B,n) for j in range(B)) or any(upper[j][i] for i in range(B,n) for j in range(B)),'nonzero cross-block coupling witness')
                    return receipt
            finally:
                for t in (*rhs,*pages):t.clear()
                if packed is not None:packed.clear()
                for m in matrices:m.close()
                if header is not None:header.close()
                core.pool.empty()
                for t in core.pool.tapes:erase_marker(t)
    finally:Tape.__init__=original_init


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--quick',action='store_true')
    args=parser.parse_args()
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'bound source: '+row['path'])
    predecessor=json.loads((HERE/'PREDECESSOR.json').read_text())
    for row in predecessor['files']:
        need(hashlib.sha256((HERE/row['local_path']).read_bytes()).hexdigest()==row['local_sha256'],'retained caller source bytes')
    sys.path[:0]=[str(ROOT/'research/physical-gaussian-core'),str(ROOT/'research/physical-boundary-pages')]
    import gaussian_sources
    with gaussian_sources.opened():
        sys.path.insert(0,str(HERE))
        cases=[case(5,4)] if args.quick else [case(5,4),case(8,4),case(5,2),case(5,1)]
        from controls import run
        controls=run()
    result=dict(status='PASS_PHYSICAL_TWO_COLUMN_BOUNDARY',cases=cases,controls=controls)
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    elif not args.quick:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed complete receipt')
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
