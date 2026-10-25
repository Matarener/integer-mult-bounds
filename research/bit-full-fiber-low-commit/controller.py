# SPDX-License-Identifier: Apache-2.0
"""Literal complete-fiber permutation, installation and old-cache retirement."""

def compile_commit(m, c, permutation, dimensions, cache_bits):
    if type(dimensions) is not int or dimensions < 1:
        raise ValueError('positive fixed high-coordinate count')
    permutation = tuple(permutation)
    if not permutation or any(type(v) is not int for v in permutation) or sorted(permutation) != list(range(len(permutation))):
        raise ValueError('complete finite low-type permutation')
    cache_bits = tuple(cache_bits)
    if any(type(v) is not int or v not in (0,1) for v in cache_bits):
        raise ValueError('canonical finite old-type cache')
    # 0 source, 1 output, 2 Q, 3 spectator extent, 4 owned old cache,
    # 5 binary work, 6 fiber length, then D Q counters and one spectator counter.
    count = dimensions+1
    tapes = 7+count
    a = m.Assembler(tapes)
    fail = a.fresh('invalid_commit_boundary')
    counters = tuple(range(7,tapes))
    private = (1,5,6)+counters

    def checked(symbols, tape, prefix):
        good = a.fresh(prefix)
        a.branch(tape,{s:good for s in symbols},fail)
        a.label(good)

    def erase(tape, prefix):
        # Start anywhere in a contiguous marked region; find its right marker.
        loop, body, end = (a.fresh(prefix+s) for s in ('_seek','_body','_end'))
        a.label(loop)
        a.branch(tape,{m.RIGHT:end,m.ZERO:body,m.ONE:body,m.UNIT:body},fail)
        a.label(body);a.move(tape,1);a.goto(loop)
        a.label(end);a.write(tape,m.BLANK);a.move(tape,-1)
        back, more, done = (a.fresh(prefix+s) for s in ('_back','_more','_done'))
        a.label(back)
        a.branch(tape,{m.LEFT:done,m.ZERO:more,m.ONE:more,m.UNIT:more},fail)
        a.label(more);a.write(tape,m.BLANK);a.move(tape,-1);a.goto(back)
        a.label(done);a.write(tape,m.BLANK)

    for tape in private:
        checked((m.BLANK,),tape,'blank_owned')
        a.write(tape,m.LEFT);a.move(tape,1)
    # Cache validation occurs before payload mutation; its exact old values
    # remain present until the completed installed output no longer needs them.
    for bit in cache_bits:
        checked((m.ONE if bit else m.ZERO,),4,'old_cache_bit')
        a.move(4,1)
    checked((m.RIGHT,),4,'old_cache_end')
    c.emit_rewind(a,4,'old_cache_return')
    for i,tape in enumerate(counters):
        c.emit_binary_to_unary(a,2 if i < dimensions else 3,5,tape,'extent_'+str(i))

    labels=[]
    for tape in counters:
        loop,body,end=(a.fresh('fiber_'+s) for s in ('loop','body','end'))
        labels.append((tape,loop,end))
        a.label(loop);a.branch(tape,{m.UNIT:body,m.RIGHT:end},fail)
        a.label(body)
    a.write(6,m.UNIT);a.move(6,1)
    for tape,loop,end in reversed(labels):
        a.move(tape,1);a.goto(loop)
        a.label(end);c.emit_rewind(a,tape,'fiber_counter_return')
    a.write(6,m.RIGHT);c.emit_rewind(a,6,'fiber_length_return')

    def segment(copy):
        loop, body, end = (a.fresh('segment_'+s) for s in ('loop','body','end'))
        a.label(loop);a.branch(6,{m.UNIT:body,m.RIGHT:end},fail)
        a.label(body)
        if copy:
            zero,one,advance=(a.fresh('copy_'+s) for s in ('zero','one','advance'))
            a.branch(0,{m.ZERO:zero,m.ONE:one},fail)
            a.label(zero);a.write(1,m.ZERO);a.goto(advance)
            a.label(one);a.write(1,m.ONE)
            a.label(advance);a.move(1,1)
        else:
            checked((m.ZERO,m.ONE),0,'payload_bit')
        a.move(0,1);a.move(6,1);a.goto(loop)
        a.label(end);c.emit_rewind(a,6,'segment_counter_return')

    for _ in permutation:
        segment(False)
    checked((m.RIGHT,),0,'complete_source')
    c.emit_rewind(a,0,'validated_source_return')
    inverse=[permutation.index(i) for i in range(len(permutation))]
    for source in inverse:
        for _ in range(source):
            segment(False)
        segment(True)
        c.emit_rewind(a,0,'gather_source_return')
    a.write(1,m.RIGHT);c.emit_rewind(a,1,'output_return')
    # Consume the owned output and install it into the original owner.
    loop,zero,one,advance,end=(a.fresh('install_'+s) for s in ('loop','zero','one','advance','end'))
    a.label(loop);a.branch(1,{m.ZERO:zero,m.ONE:one,m.RIGHT:end},fail)
    a.label(zero);a.write(0,m.ZERO);a.goto(advance)
    a.label(one);a.write(0,m.ONE)
    a.label(advance);a.write(1,m.BLANK);a.move(0,1);a.move(1,1);a.goto(loop)
    a.label(end);checked((m.RIGHT,),0,'installed_length')
    a.write(1,m.BLANK)
    c.emit_rewind(a,1,'consumed_output_return');a.move(1,-1);a.write(1,m.BLANK)
    c.emit_rewind(a,0,'installed_source_return')
    erase(4,'retire_old_cache')
    for tape in (6,)+counters:
        erase(tape,'clear_counter_'+str(tape))
    # Converter returns binary work to its marked empty state.
    a.move(5,-1);checked((m.LEFT,),5,'binary_work_left');a.write(5,m.BLANK)
    a.halt();a.label(fail);a.reject('complete low-type source, old cache, extents and blank owned workspace')
    return a.finish()


def compile_cache(m,cache_bits,tapes):
    """Prepare the finite old-type snapshot before its dependent carry reads."""
    cache_bits=tuple(cache_bits)
    if any(type(v) is not int or v not in (0,1) for v in cache_bits):
        raise ValueError('binary compiler cache')
    a=m.Assembler(tapes);fail=a.fresh('owned_cache_not_blank')
    for symbol in (m.LEFT,*(m.ONE if bit else m.ZERO for bit in cache_bits),m.RIGHT):
        good=a.fresh('blank_cache_cell')
        a.branch(4,{m.BLANK:good},fail);a.label(good)
        a.write(4,symbol);a.move(4,1)
    for _ in range(len(cache_bits)+1): a.move(4,-1)
    a.halt();a.label(fail);a.reject('blank independently owned old-cache tape')
    return a.finish()
