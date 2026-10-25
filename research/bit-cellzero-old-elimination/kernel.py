# SPDX-License-Identifier: Apache-2.0
"""Actual whole-T cell0 join; PR3343 split/merge, PR2776 literal macros.
JoyboyBrian, substantial OpenAI Codex assistance.
"""
from math import isqrt

LOW, CACHE, LOCAL, GLOBAL = 14,15,16,17


def build(modules, q, f=1, inverse=False, depth=None):
    if type(q) is not int or q<3 or any(q%a==0 for a in range(2,isqrt(q)+1)):
        raise ValueError('fixed odd prime')
    if type(f) is not int or f<1 or type(inverse) is not bool:
        raise ValueError('fixed lane count/direction')
    n=8*f;cells=n*n;bits=(q-1).bit_length()
    if depth is None:depth=cells
    if type(depth) is not int or depth<1:raise ValueError('positive fiber depth')
    # Nonstandard depth is an explicitly labelled generic calibration, not GL_N payload.
    b,m,c=(modules[k] for k in ('shear','machine','counters'))
    loops=list(range(18,18+depth-1));a=m.Assembler(18+depth-1)
    fail=a.fresh('invalid_cellzero_contract')
    persistent=[b.P_COUNT,b.G_COUNT,b.S_COUNT,b.BINARY_WORK]+loops
    private=[LOCAL,b.OUTPUT,b.SPLIT_A,b.SPLIT_B,b.LEFT_LENGTH,b.RIGHT_LENGTH]
    def initialize(tape):
        good=a.fresh('blank_origin');a.branch(tape,{m.BLANK:good},fail);a.label(good)
        a.write(tape,m.LEFT);a.move(tape,1)
    for tape in [LOW,GLOBAL]+persistent:initialize(tape)
    for src,dst in [(b.P_INPUT,b.P_COUNT),(b.S_INPUT,b.G_COUNT)]+[(b.Q_INPUT,t) for t in loops]:
        c.emit_binary_to_unary(a,src,b.BINARY_WORK,dst,a.fresh('extent'))
    nested=[]
    for tape in loops+[b.G_COUNT]:
        c.emit_rewind(a,tape,a.fresh('product_return'))
        loop,body,end=(a.fresh(s) for s in ('product_loop','product_body','product_end'))
        a.label(loop);a.branch(tape,{m.UNIT:body,m.RIGHT:end},fail);a.label(body)
        nested.append((tape,loop,end))
    a.write(b.S_COUNT,m.UNIT);a.move(b.S_COUNT,1)
    for tape,loop,end in reversed(nested):
        a.move(tape,1);a.goto(loop);a.label(end)
    a.write(b.S_COUNT,m.RIGHT)
    outer,body,done,rotate0,rotate1,after=(a.fresh(s) for s in ('types','type','types_done','rotate0','rotate1','after_rotate'))
    a.label(outer);a.branch(b.P_COUNT,{m.UNIT:body,m.RIGHT:done},fail);a.label(body)
    for tape in private:initialize(tape)
    c.emit_binary_to_unary(a,b.Q_INPUT,b.BINARY_WORK,b.LEFT_LENGTH,a.fresh('Q'))
    a.write(b.RIGHT_LENGTH,m.RIGHT)
    b._segment(a,b.LEFT_LENGTH,b.SOURCE,LOCAL,False,fail,a.fresh('stage_fiber'))
    a.write(LOCAL,m.RIGHT);c.emit_rewind(a,LOCAL,a.fresh('local_return'))
    selected=(4 if inverse else 5)*f
    for _ in range(selected*bits):a.move(CACHE,1)
    # A finite radix decoder; the running program reads no host integer.
    labels={(k,v):a.fresh('digit') for k in range(bits+1) for v in range(1<<k)}
    a.goto(labels[0,0])
    for k in range(bits):
        for v in range(1<<k):
            a.label(labels[k,v])
            z,o=a.fresh('zero'),a.fresh('one')
            a.branch(CACHE,{m.ZERO:z,m.ONE:o},fail)
            for symbol,target in ((z,v),(o,v+(1<<k))):
                a.label(symbol);a.move(CACHE,1);a.goto(labels[k+1,target])
    for v in range(1<<bits):
        a.label(labels[bits,v])
        if v>=q:a.goto(fail);continue
        low=v if inverse else (2*v)%q
        carry=0 if inverse else (2*v)//q
        for _ in range((cells-selected-1)*bits):a.move(CACHE,1)
        for k in range(bits):a.write(LOW,m.ONE if (low>>k)&1 else m.ZERO);a.move(LOW,1)
        a.goto(rotate1 if carry else rotate0)
    def rotation(carry,label):
        a.label(label)
        # LEFT_LENGTH already ends at RIGHT after staging the full fiber.
        if carry:b._decrease_left_increase_right(a,fail,a.fresh('bounded_one'))
        gather=((b.LEFT_LENGTH,LOCAL,b.SPLIT_A,False),(b.RIGHT_LENGTH,LOCAL,b.SPLIT_B,False))
        emit=((b.RIGHT_LENGTH,b.SPLIT_B,b.OUTPUT,True),(b.LEFT_LENGTH,b.SPLIT_A,b.OUTPUT,True))
        for length,src,dst,consume in gather:b._segment(a,length,src,dst,consume,fail,a.fresh('split'))
        good=a.fresh('complete_local');a.branch(LOCAL,{m.RIGHT:good},fail);a.label(good)
        for tape in (b.SPLIT_A,b.SPLIT_B):a.write(tape,m.RIGHT);c.emit_rewind(a,tape,a.fresh('bucket_return'))
        for length,src,dst,consume in emit:b._segment(a,length,src,dst,consume,fail,a.fresh('merge'))
        a.write(b.OUTPUT,m.RIGHT);c.emit_rewind(a,b.OUTPUT,a.fresh('output_return'));a.goto(after)
    rotation(0,rotate0);rotation(1,rotate1);a.label(after)
    def copy_consuming(src,dst,prefix):
        loop,z,o,end=(a.fresh(prefix+s) for s in ('loop','zero','one','end'))
        a.label(loop);a.branch(src,{m.ZERO:z,m.ONE:o,m.RIGHT:end},fail)
        for label,symbol in ((z,m.ZERO),(o,m.ONE)):
            a.label(label);a.write(dst,symbol);a.write(src,m.BLANK)
            a.move(src,1);a.move(dst,1);a.goto(loop)
        a.label(end)
    copy_consuming(b.OUTPUT,GLOBAL,'append')
    for tape in private:b._erase_back_to_origin(a,tape,a.fresh('clear_fiber'))
    a.move(b.P_COUNT,1);a.goto(outer)
    a.label(done)
    for tape in (b.SOURCE,CACHE):
        good=a.fresh('whole_bank_complete');a.branch(tape,{m.RIGHT:good},fail);a.label(good)
    for tape in (LOW,GLOBAL):a.write(tape,m.RIGHT);c.emit_rewind(a,tape,a.fresh('owned_return'))
    c.emit_rewind(a,CACHE,a.fresh('cache_return'));c.emit_rewind(a,b.SOURCE,a.fresh('owner_return'))
    copy_consuming(GLOBAL,b.SOURCE,'install')
    b._erase_back_to_origin(a,GLOBAL,a.fresh('retire_global'))
    c.emit_rewind(a,b.SOURCE,a.fresh('installed_return'))
    # Some persistent counters stop at their ends; move all to ends before erase.
    for tape in persistent:
        c.emit_rewind(a,tape,a.fresh('cleanup_return'))
        if tape!=b.BINARY_WORK:b._seek_right(a,tape,fail,a.fresh('cleanup_end'))
        b._erase_back_to_origin(a,tape,a.fresh('cleanup'))
    a.halt();a.label(fail);a.reject('valid full T cache/payload, positive extents and owned workspace')
    return a.finish()


def initialize_actual_T(modules,q,f=1):
    """Pre-input finite code installs the fixed GL_(8f)(q) count; no GL enumeration."""
    if type(f) is not int or f<1:raise ValueError('fixed positive f')
    n=8*f
    if type(q) is not int or q<3 or any(q%a==0 for a in range(2,isqrt(q)+1)) or f<1:
        raise ValueError('fixed admitted q,f')
    total=1
    for i in range(n):total*=q**n-q**i
    m=modules['machine'];a=m.Assembler(1);fail=a.fresh('occupied_count')
    good=a.fresh('blank');a.branch(0,{m.BLANK:good},fail);a.label(good)
    a.write(0,m.LEFT);a.move(0,1)
    for i in range(total.bit_length()):
        good=a.fresh('blank');a.branch(0,{m.BLANK:good},fail);a.label(good)
        a.write(0,m.ONE if (total>>i)&1 else m.ZERO);a.move(0,1)
    good=a.fresh('blank');a.branch(0,{m.BLANK:good},fail);a.label(good);a.write(0,m.RIGHT)
    for _ in range(total.bit_length()):a.move(0,-1)
    a.halt();a.label(fail);a.reject('owned blank T descriptor')
    return a.finish()
