"""Literal one-coordinate rotation and finite G20 quarter-code dispatch.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
PR2776 supplies the paid local macros; PR5332/5846 supply quarter preparation.
"""
WORK=(2,3,8,10,11,12,13,15)


def build(modules,inverse=False):
    if type(inverse) is not bool:raise ValueError('fixed Boolean orientation')
    b,m,c=(modules[k] for k in ('shear','machine','counters'))
    a=m.Assembler(19);fail=a.fresh('invalid_rotation')
    for tape in WORK:
        good=a.fresh('blank');a.branch(tape,{m.BLANK:good},fail);a.label(good)
        a.write(tape,m.LEFT);a.move(tape,1)
    for source,target,name in [(4,8,'P'),(5,11,'Q'),(7,10,'S'),(14,15,'offset_plus_one')]:
        c.emit_binary_to_unary(a,source,13,target,'prepare_'+name)
    b._seek_right(a,15,fail,'trim_offset_end');a.write(15,m.BLANK);a.move(15,-1)
    positive=a.fresh('positive_offset_descriptor');a.branch(15,{m.UNIT:positive},fail);a.label(positive)
    a.write(15,m.RIGHT);c.emit_rewind(a,15,'offset_return')
    c.emit_rewind(a,11,'Q_compare_return')
    loop,unit,advance,end,good=(a.fresh(s) for s in ('compare','unit','advance','end','bounded'))
    a.label(loop);a.branch(15,{m.UNIT:unit,m.RIGHT:end},fail)
    a.label(unit);a.branch(11,{m.UNIT:advance},fail);a.label(advance)
    a.move(15,1);a.move(11,1);a.goto(loop)
    a.label(end);a.branch(11,{m.UNIT:good},fail);a.label(good)
    c.emit_rewind(a,15,'offset_compare_return');c.emit_rewind(a,11,'Q_return')
    a.write(12,m.RIGHT);b._seek_right(a,11,fail,'initial_left_end')
    loop,step,end=(a.fresh(s) for s in ('split','step','split_ready'))
    a.label(loop);a.branch(15,{m.UNIT:step,m.RIGHT:end},fail);a.label(step)
    b._decrease_left_increase_right(a,fail,'initial_offset')
    a.move(15,1);a.goto(loop);a.label(end)

    def phase(operations,prefix):
        c.emit_rewind(a,8,prefix+'_P_return')
        loop,body,end=(a.fresh(prefix+s) for s in ('_loop','_body','_end'))
        a.label(loop);a.branch(8,{m.UNIT:body,m.RIGHT:end},fail);a.label(body)
        for i,(length,source,target,consume) in enumerate(operations):
            b._segment(a,length,source,target,consume,fail,prefix+'_segment_'+str(i))
        a.move(8,1);a.goto(loop);a.label(end)

    gather=((11,0,2,False),(12,0,3,False));emit=((12,3,0,True),(11,2,0,True))
    if inverse:gather,emit=tuple(reversed(gather)),tuple(reversed(emit))
    phase(gather,'gather')
    good=a.fresh('source_complete');a.branch(0,{m.RIGHT:good},fail);a.label(good)
    for tape in (2,3):a.write(tape,m.RIGHT);c.emit_rewind(a,tape,'bucket_'+str(tape))
    c.emit_rewind(a,0,'owner_before_emit');phase(emit,'emit')
    for tape in (2,3):
        good=a.fresh('bucket_complete');a.branch(tape,{m.RIGHT:good},fail);a.label(good)
    a.write(0,m.RIGHT);c.emit_rewind(a,0,'owner_return')
    for tape in WORK:b._erase_back_to_origin(a,tape,'erase_'+str(tape))
    a.halt();a.label(fail);a.reject('positive extents, bounded offset and blank private work')
    return a.finish()


def quarter_program(modules,descriptor,quarter,inverse=False):
    """Read preserved five-bit k+16, prepare C, rotate, and erase C+1."""
    m,c=modules['machine'],modules['counters'];a=m.Assembler(19)
    fail,body,cleanup,done=(a.fresh(s) for s in ('invalid_code','rotate','cleanup','done'))
    entries={k:a.fresh('prepare_'+str(k)) for k in range(-16,13)}
    nodes={(level,value):a.fresh('code') for level in range(6) for value in range(1<<level)}
    a.goto(nodes[0,0])
    for (level,value),label in nodes.items():
        a.label(label)
        if level==5:
            if value>28:a.goto(fail);continue
            good=a.fresh('code_end');a.branch(16,{m.RIGHT:good},fail);a.label(good)
            c.emit_rewind(a,16,'code_return');a.goto(entries[value-16])
        else:
            zero,one=a.fresh('zero'),a.fresh('one');a.branch(16,{m.ZERO:zero,m.ONE:one},fail)
            for bit,target in [(0,zero),(1,one)]:
                a.label(target);a.move(16,1);a.goto(nodes[level+1,value+(bit<<level)])

    def append(program,entry,continuation):
        labels=[entry if i==program.entry else a.fresh('linked') for i in range(len(program.instructions))]
        for label,row in zip(labels,program.instructions):
            a.label(label);op=row[0]
            if op=='branch':a.branch(row[1],{s:labels[pc] for s,pc in row[2]},labels[row[3]])
            elif op=='goto':a.goto(labels[row[1]])
            elif op=='write':a.write(row[1],row[2])
            elif op=='move':a.move(row[1],row[2])
            elif op=='halt':a.goto(continuation)
            elif op=='reject':a.reject(row[1])
            else:raise ValueError('unsupported linked instruction')
    for k,entry in entries.items():append(descriptor.prepare(modules,quarter,k),entry,body)
    append(build(modules,inverse),body,cleanup)
    append(descriptor.erase(modules),cleanup,done)
    a.label(done);a.halt();a.label(fail);a.reject('five-bit G20 quarter code from -16 through12')
    return a.finish()
