"""Compile the retained quarter descriptor into the literal affine tape ABI.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The quarter arithmetic and affine machine retain JoyboyBrian's source credit.
"""


def prepare(modules, quarter, k):
    m, c = modules['machine'], modules['counters']
    old = quarter.compile_offset(k)
    a = m.Assembler(19)
    fail, odd, one, general, empty = (a.fresh(s) for s in ('invalid','odd','one','general','empty'))
    labels = [a.fresh('descriptor_state') for _ in old['code']]
    a.branch(14,{m.BLANK:empty},fail);a.label(empty)
    a.branch(5,{m.ONE:odd},fail);a.label(odd);a.move(5,1)
    a.branch(5,{m.RIGHT:one,m.ZERO:general,m.ONE:general},fail)
    a.label(one)
    a.write(14,m.LEFT);a.move(14,1);a.write(14,m.ONE);a.move(14,1);a.write(14,m.RIGHT)
    c.emit_rewind(a,14,'unit_ring_output');c.emit_rewind(a,5,'unit_ring_Q');a.halt()
    a.label(general)
    a.move(5,-1);a.move(14,1);a.goto(labels[old['start']])
    symbols = {None:m.BLANK,0:m.ZERO,1:m.ONE,2:m.RIGHT,3:m.LEFT}
    tapes = (5,14)
    for label,row in zip(labels,old['code']):
        a.label(label);op=row[0]
        if op=='branch':
            a.branch(tapes[row[1]],{symbols[s]:labels[dest] for s,dest in row[2]},labels[row[3]])
        elif op=='move':
            a.move(tapes[row[1]],row[2]);a.goto(labels[row[3]])
        elif op=='write':
            a.write(tapes[row[1]],symbols[row[2]]);a.goto(labels[row[3]])
        elif op=='goto':a.goto(labels[row[1]])
        elif op=='halt':a.halt()
        elif op=='reject':a.reject('retained quarter descriptor rejected')
        else:raise ValueError('unknown retained descriptor instruction')
    a.label(fail);a.reject('odd canonical Q and blank coefficient owner')
    return a.finish()


def erase(modules,tape=14):
    m=modules['machine'];a=m.Assembler(19)
    loop,bit,end,fail=(a.fresh(s) for s in ('erase','bit','end','invalid'))
    a.label(loop);a.branch(tape,{m.ZERO:bit,m.ONE:bit,m.RIGHT:end},fail)
    a.label(bit);a.write(tape,m.BLANK);a.move(tape,1);a.goto(loop)
    a.label(end);modules['shear']._erase_back_to_origin(a,tape,'owned_coefficient');a.halt()
    a.label(fail);a.reject('complete marked coefficient descriptor')
    return a.finish()


def zero_offset(modules):
    m=modules['machine'];a=m.Assembler(19);good=a.fresh('blank');fail=a.fresh('occupied')
    a.branch(16,{m.BLANK:good},fail);a.label(good)
    a.write(16,m.LEFT);a.move(16,1);a.write(16,m.ONE);a.move(16,1);a.write(16,m.RIGHT)
    modules['counters'].emit_rewind(a,16,'zero_offset_return');a.halt()
    a.label(fail);a.reject('blank owned offset descriptor')
    return a.finish()


def link(modules,programs):
    starts=[];size=0
    for program in programs:
        starts.append(size);size+=len(program.instructions)
    rows=[]
    for i,(program,start) in enumerate(zip(programs,starts)):
        for row in program.instructions:
            if row[0]=='branch':rows.append(('branch',row[1],tuple((s,pc+start) for s,pc in row[2]),row[3]+start))
            elif row[0]=='goto':rows.append(('goto',row[1]+start))
            elif row[0]=='halt' and i+1<len(programs):rows.append(('goto',starts[i+1]))
            else:rows.append(row)
    return modules['machine'].Program(tuple(rows),19)


def build(modules,quarter,affine,k,inverse=False):
    return link(modules,[zero_offset(modules),prepare(modules,quarter,k),
        affine.build_program(modules,inverse,inplace=True),erase(modules),erase(modules,16)])
