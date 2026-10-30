"""Independent layout permutation and rejecting physical failure controls."""
from cardinal_counts import Count
from check_support import no_decode
from records import Tape
from ring_check_words import body
from router_metadata import owned
from scratch_pool import ScratchPool
from session import OuterScope, borrowed_tape, erase_marker, sealed_constructors
from words import BLANK
from rhs_layout import pack, unpack


def need(ok,message):
    if not ok: raise ValueError(message)


def run():
    pool=ScratchPool(128); scope=OuterScope(pool)
    a,b,dirty=Tape(),Tape(),Tape()
    for t,bits in ((a,[1,0,1,0,0,1,0,1]),(b,[0,0,1,1,1,1,0,0]),(dirty,[1,1,0,1])):
        for bit in bits:t.append(bit)
        t.rewind()
    saved=[(bytes(t.cells),t.head) for t in (a,b,dirty)]
    controls=[]; packed=None; recovered=()
    def rejects(action,fragment):
        before=set(pool.live)
        try:
            with no_decode(): action()
        except ValueError as e:
            need(fragment in str(e),'specific expected rejection: '+str(e))
        else:raise ValueError('missing rejection: '+fragment)
        need(set(pool.live)==before,'failed layout restores every acquired lease')
        controls.append(fragment)
    with owned(Count.literal(2),Count.literal(3),Count.literal(4)) as (n,B,w):
        try:
            with sealed_constructors(),scope.installed():
                a.step(1)
                rejects(lambda:pack(a,b,n,B,w,pool),'canonical layout entry heads')
                a.step(-1)
                with owned(Count.literal(2)) as (leased_count,):
                    rejects(lambda:pack(leased_count.tape,b,leased_count,B,w,pool),'separate layout metadata')
                rejects(lambda:pack(a,a,n,B,w,pool),'distinct layout payload ports')
                rejects(lambda:pack(n.tape,b,n,B,w,pool),'separate layout metadata')
                with no_decode():packed=pack(a,b,n,B,w,pool)
                raw=bytes(borrowed_tape(packed).cells[1:])
                expected=bytes([1,0,1,0,0,0,1,1]+[0]*4+[0,1,0,1,1,1,0,0]+[0]*16)
                need(raw==expected,'independent padded permutation')
                need(raw!=bytes([0,0,1,1,1,0,1,0])+expected[8:],'component swap falsified')
                controls.append('component swap falsified')
                # The checker corrupts an actual padding symbol; runtime must reject and clean up.
                tape=borrowed_tape(packed); tape.cells[-1]=1
                rejects(lambda:unpack(packed,n,B,w,pool),'literal RHS bits and zero padding')
                tape.cells[-1]=0
                tape.cells.append(1)
                rejects(lambda:unpack(packed,n,B,w,pool),'complete padded RHS return extent')
                tape.cells.pop()
                a.cells.append(1)
                rejects(lambda:pack(a,b,n,B,w,pool),'complete component RHS extent')
                a.cells.pop()
                last=a.cells.pop()
                rejects(lambda:pack(a,b,n,B,w,pool),'literal RHS bits and zero padding')
                a.cells.append(last)
                with no_decode():recovered=unpack(packed,n,B,w,pool)
                need([body(borrowed_tape(t)) for t in recovered]==[body(t) for t in (a,b)],'positive reuse after all failed cases')
                need(saved==[(bytes(t.cells),t.head) for t in (a,b,dirty)],'borrowed inputs and dirty spectator restored')
                for t in recovered:t.clear()
                recovered=()
                packed.clear(); packed=None
            pool.empty()
            for t in pool.tapes:erase_marker(t)
            need(all(t.head==1 and all(x==BLANK for x in t.cells) for t in pool.tapes),'retained backing fully erased')
        finally:
            for t in recovered:t.clear()
            if packed is not None:packed.clear()
    return controls
