"""Physical zero-column rejection and independent exact dot-product controls."""
from cardinal_counts import Count
from check_support import no_decode
from pair_kernel import PairBoundaryPages
from records import Tape
from ring_words import Signed,write_signed
from router_metadata import owned
from session import initialize_marker,erase_marker,sealed_constructors
from words import BLANK


def need(ok,message):
    if not ok:raise ValueError(message)


def run():
    owner=PairBoundaryPages()
    first,second,out,dirty=Tape(),Tape(),Tape(),Tape()
    a=[[3,3,3,3],[-3,-3,-3,-3],[3,-3,3,-3],[7,0,-1,2]]
    b=[[1,2,0,0] for _ in range(4)]
    expected=[sum(a[i][k]*b[k][j] for k in range(4)) for i in range(4) for j in range(4)]
    def raw(t):
        data=bytes(t.cells[1:]);end=data.find(bytes([BLANK]));return data if end<0 else data[:end]
    def decode(t,width):
        data=raw(t)
        return [sum(bit<<i for i,bit in enumerate(data[s:s+width]))-(data[s+width-1]<<width) for s in range(0,len(data),width)]
    with owned(Count.literal(4),Count.literal(8),Count.literal(20)) as (block,width,wide):
        for t,data in ((first,a),(second,b)):
            for row in data:
                for x in row:
                    with owned(Signed(Count.literal(abs(x)),x<0)) as (value,):write_signed(value,t,width)
            t.rewind()
        for bit in (1,1,0,1,0):dirty.append(bit)
        dirty.rewind()
        saved=[(bytes(t.cells),t.head) for t in (first,second,dirty)]
        for t in owner.pool.tapes:initialize_marker(t)
        try:
            with sealed_constructors(),owner.scope.installed():
                with no_decode():owner.product(first,second,out,block,width,wide)
                need(decode(out,20)==expected,'independent exact full matrix including padded zero columns')
                need(owner.arithmetic.products==32,'exact active dot product census')
                perterm=[sum((1 if a[i][k]*b[k][j]>=0 else -1)*(abs(a[i][k]*b[k][j])//4)*4 for k in range(4)) for i in range(4) for j in range(4)]
                need(expected!=perterm,'premature per-term rounding falsified')
                omitted=[v if j%4!=1 else 0 for j,v in enumerate(expected)]
                need(expected!=omitted,'omitted second active column falsified')
                out.clear()
                second.cells[17]=1  # First row, third eight-bit column: genuinely nonzero.
                before=set(owner.pool.live)
                try:
                    with no_decode():owner.product(first,second,out,block,width,wide)
                except ValueError as error:
                    need('inactive product columns are zero' in str(error),'specific inactive-column rejection')
                else:raise ValueError('silently discarded a nonzero third column')
                need(before==set(owner.pool.live) and out.read()==BLANK,'failed product restores temporary leases')
                second.cells[17]=0
                with no_decode():owner.product(first,second,out,block,width,wide)
                need(decode(out,20)==expected,'positive reuse after rejected inactive column')
                need(saved==[(bytes(t.cells),t.head) for t in (first,second,dirty)],'borrowed inputs and dirty spectators restored')
                out.clear()
            owner.pool.empty();owner.idle()
            for t in owner.pool.tapes:erase_marker(t)
            need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in owner.pool.tapes),'all retained scratch backing erased')
        finally:
            for t in (first,second,out,dirty):t.clear()
    return ['full independent exact dot products','premature per-term rounding','omitted second active column',
            'nonzero inactive column rejected','positive reuse after rejection','arbitrary dirty spectator unchanged']
