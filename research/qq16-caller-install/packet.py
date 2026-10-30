# SPDX-License-Identifier: Apache-2.0
"""Encoded acquisition from an actual gathered complex caller.

Chris R, substantial OpenAI Codex assistance. Retained Count, tape, scope,
stock and capsule routines are Jose Manuel's physical-controller lineage.
Caller selection and source authentication must precede this module's use.
No values, widths, row counts or packet lengths are decoded in this adapter.
"""

class PacketCompiler:
    """Fixed-owned descriptor block and optional entry snapshots.

    A snapshot is a charged original-data lifetime, never an implicit recovery
    input. This module does not establish the semantic reconnection theorem.
    """
    def __init__(self, snapshot_slots=0):
        from records import Tape
        from scratch_pool import ScratchPool
        from session import OuterScope
        from machine import INPUTS
        if type(snapshot_slots) is not int or snapshot_slots < 0:
            raise ValueError('fixed nonnegative snapshot slot count')
        self.roles = {name: Tape() for name in INPUTS}
        self.snapshots = tuple(Tape() for _ in range(snapshot_slots))
        self.pool = ScratchPool(64)
        self.scope = OuterScope(self.pool)
        self.closed = True
        self.captured = ()

    def descriptors(self):
        from cardinal_counts import Count
        if self.closed:
            raise ValueError('live encoded packet descriptor lease')
        result = {}
        for name, tape in self.roles.items():
            value = object.__new__(Count)
            value.tape = tape
            result[name] = value
        return result

    def compile(self, caller):
        return self._compile(caller)

    def compile_global(self, caller, field, expected_event):
        """Compile one acquired whole-family operand at a completed cover sweep.

        expected_event is a fixed program-fence constant, not a decoded count.
        field has order prefix, cover, unused row, complete within-row record.
        """
        from words import need
        need(type(expected_event) is int and expected_event >= 0,
             'fixed whole-cover producer fence')
        need(not caller.closed and caller.mode == 'group' and caller.group is None and
             caller.bank.state == 'closed' and caller.event == expected_event and
             caller.subgroup == caller.pc == 0 and
             caller.cover_index == caller.binding.cover.size,
             'actual completed whole-cover producer fence')
        return self._compile(caller, field)

    def _compile(self, caller, field=None):
        from cardinal_counts import Count, positive
        from encoded import compare, divide, fixed_power
        from machine import INPUTS, copy_symbols
        from session import sealed_constructors
        from words import BLANK, need
        need(self.closed and not self.pool.live and
             all(t.read() == BLANK for t in (*self.roles.values(), *self.snapshots)),
             'closed encoded compiler')
        if field is None:
            need(not caller.closed and caller.mode == 'group' and caller.group is not None and
                 caller.bank.state == 'gathered', 'actual gathered caller cut')
        caller.primitive_boundary()
        dimension = caller.binding.dimension
        rank = caller.binding.maximum_rank
        divisor_constant = caller.binding.families * caller.binding.cover.size
        need(type(dimension) is int and dimension >= 2 and
             type(rank) is int and 0 < rank < dimension, 'fixed source recursion constants')
        need(all(t not in caller.parked for t in (*self.roles.values(), *self.snapshots, *self.pool.tapes)),
             'exclusive compiler inventory')
        owned = []
        def keep(v):
            owned.append(v)
            return v
        try:
            with sealed_constructors(), self.scope.installed():
                for name in ('columns', 'prefixes', 'unused', 'spacing', 'guard',
                             'component_bits', 'coefficients', 'root_width'):
                    positive(caller.c(name))
                width = keep(Count(caller.c('columns')))
                parent_width = keep(Count(width)); parent_width.multiply_small(dimension)
                need(compare(parent_width, caller.c('width')) == 0,
                     'post-remainder parent width is dimension times columns')
                need(compare(caller.c('width'), caller.c('root_width')) <= 0,
                     'actual global root width')
                if field is not None:
                    # The source node tests its old width before peeling a
                    # remainder. The service needs its own post-peel test.
                    nonleaf = keep(fixed_power(caller.c('width'), 1000, caller.c('root_width')))
                    need(compare(nonleaf, caller.c('root_width')) >= 0,
                         'post-remainder service nonleaf admission')
                need(compare(caller.c('residue'), caller.c('spacing')) < 0,
                     'actual spacing residue')
                divisor = keep(Count.literal(divisor_constant))
                rows, rem = divide(caller.c('rows'), divisor)
                keep(rows); keep(rem)
                need(rem.zero() and compare(rows, caller.c('unused')) == 0,
                     'actual owner rows are exact parent quotient')
                # Prove the requested child's own conservative stock directly.
                current = keep(Count(width)); threshold = keep(Count.literal(dimension))
                stock = keep(Count.literal(1))
                while compare(current, threshold) >= 0:
                    current.divide_small(dimension)
                    if rank > 1: current.multiply_small(rank)
                    stock.multiply_small(divisor_constant)
                stock_multiple, stock_rem = divide(rows, stock)
                keep(stock_multiple); keep(stock_rem)
                need(stock_rem.zero() and not stock_multiple.zero(), 'actual child row stock')
                tail = keep(Count(width))
                if dimension > 2: tail.multiply_small(dimension - 1)
                after = keep(Count.product(tail, caller.c('spacing')))
                after.add(caller.c('after'))
                prefixes = keep(Count(caller.c('prefixes')))
                if field is not None:
                    from compact_counts import power_two
                    from stream import Counter
                    need(field not in (*self.roles.values(), *self.snapshots, *self.pool.tapes),
                         'borrowed whole-family field separate from compiler')
                    gamma = caller.binding.cover.size
                    need(type(gamma) is int and gamma > 0, 'fixed actual cover cardinality')
                    if gamma > 1: prefixes.multiply_small(gamma)
                    # Recompute the actual whole row, instead of trusting a
                    # convenient logical payload or a stale derived row_bits.
                    active = keep(Count.product(caller.c('width'), caller.c('spacing')))
                    address = keep(Count(caller.c('compact_bits'))); address.multiply_small(3)
                    for name in ('front', 'before', 'after', 'back'): address.add(caller.c(name))
                    address.add(active)
                    records = keep(power_two(address))
                    row_fields = keep(Count.product(records, caller.c('coefficients')))
                    row_bits = keep(Count.product(row_fields, caller.c('component_bits')))
                    row_bits.multiply_small(2)
                    need(compare(row_bits, caller.c('row_bits')) == 0, 'actual complete source row extent')
                    prefix_rows = keep(Count.product(prefixes, rows))
                    extent = keep(Count.product(prefix_rows, row_bits))
                    remaining = keep(Counter(extent))
                    field.rewind()
                    try:
                        while not remaining.finished:
                            need(field.read() in (0, 1), 'complete whole-family field bits')
                            field.step(1); remaining.decrement()
                        need(field.read() == BLANK, 'exact whole-family field extent')
                    finally:
                        field.rewind()
                for name in INPUTS:
                    source = prefixes if name == 'prefixes' else rows if name == 'rows' else width if name == 'width' else after if name == 'after' else caller.c(name)
                    copy_symbols(source.tape, self.roles[name])
            self.closed = False
            return self.descriptors()
        except BaseException:
            for tape in self.roles.values(): tape.clear()
            raise
        finally:
            for value in reversed(owned): value.close()
            self.pool.empty()

    def capture(self, caller, source_roles):
        from machine import copy_symbols
        from words import need
        need(not self.closed and not self.captured, 'one snapshot per descriptor lease')
        need(type(source_roles) is tuple and len(source_roles) == len(self.snapshots) and
             len(set(source_roles)) == len(source_roles), 'complete distinct snapshot roles')
        need(caller.mode == 'group' and caller.bank.state == 'gathered', 'live gathered snapshot source')
        caller.primitive_boundary()
        try:
            for target, role in zip(self.snapshots, source_roles):
                source = caller.packet(role)
                need(source not in self.snapshots, 'snapshot source and target disjoint')
                copy_symbols(source, target)
            self.captured = source_roles
            return self.snapshots
        except BaseException:
            for tape in self.snapshots: tape.clear()
            raise

    def close(self):
        if self.pool.live:
            raise ValueError('compiler scratch closes before retirement')
        for tape in (*self.roles.values(), *self.snapshots): tape.clear()
        self.closed = True
        self.captured = ()


def fixture():
    """Reduced actual controller exercise, called only after authentication.

    Fixture setup uses host integers and loads a dense tape, as an oracle.
    PacketCompiler itself uses only encoded source operations. This is a
    dimension-two physical fixture, not selected O73 execution.
    """
    from types import SimpleNamespace
    from cardinal_counts import Count
    from fixture_binding import FixtureBinding
    from machine import Machine, copy_symbols
    from macro_code import Code
    from ordinary import Ordinary
    from records import Tape
    from words import BLANK, need
    binding = FixtureBinding()
    native = Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                      SimpleNamespace(families=0), (Code((('unreachable',),), 0),), capacity=64)
    compiler = PacketCompiler(2)
    observed = []
    controls = []
    compiled = []
    invoice = []
    mutation_counts = [(name, Count.literal(bad), Count.literal(good), reason) for name,bad,good,reason in
                       (('unused',2,1,'actual owner rows'), ('width',1,2,'post-remainder'),
                        ('residue',1,0,'actual spacing'))]
    def body(t): return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    def observe(machine, event):
        if event == 'enter' and compiled and not observed:
            need(all(body(machine.c(name).tape) == raw for name, raw in compiled[0].items()),
                 'compiled descriptors equal actual source child capsule')
            observed.append(event)
    class Caller(Machine):
        def next_group(self):
            super().next_group()
            if self.group is None or compiled: return
            original = {name: body(self.c(name).tape) for name in self.roles if name != 'current' and name != 'header'}
            # Source-bound rejecting mutations, restoring the original Count.
            for name, invalid, saved, reason in mutation_counts:
                try:
                    copy_symbols(invalid.tape, self.c(name).tape)
                    try:
                        with self.scope.suspended(): compiler.compile(self)
                    except ValueError as error:
                        need(reason in str(error), 'precise compiler mutation rejection')
                        controls.append(reason)
                    else: raise ValueError('compiler accepted descriptor mutation')
                finally:
                    copy_symbols(saved.tape, self.c(name).tape)
            paid_tapes = tuple(dict.fromkeys((*compiler.roles.values(), *compiler.snapshots, *compiler.pool.tapes, *self.roles.values(), *self.bank.packets)))
            paid_before = [t.meter.record() for t in paid_tapes]
            with self.scope.suspended(): result = compiler.compile(self)
            compiled.append({name: body(value.tape) for name, value in result.items()})
            originals = [body(self.packet(i)) for i in range(2)]
            with self.scope.suspended(): snapshots = compiler.capture(self, (0, 1))
            need([body(t) for t in snapshots] == originals, 'complete actual gathered owner copies')
            need([body(self.packet(i)) for i in range(2)] == originals, 'borrowed owner values preserved')
            need(all(body(self.c(name).tape) == raw for name, raw in original.items()),
                 'parent descriptors preserved by compile and acquisition')
            compiler.close()
            invoice.append({key: sum(t.meter.record()[key]-old[key] for t,old in zip(paid_tapes,paid_before)) for key in ('reads','writes','moves')})
    engine = Caller(binding, native, binding.catalogue, observe)
    # Two prefixes, two coefficients and nonconstant complex payload: every
    # spectator/outer record must survive actual gather/child/scatter/return.
    descriptors = {name: Count.literal(value) for name, value in dict(
        prefixes=2, rows=4, front=0, compact_bits=0, before=0, width=2,
        after=0, back=0, spacing=1, guard=1, residue=0, component_bits=20,
        coefficients=2, root_width=2).items()}
    values = [(16 * ((7 * i) % 11 - 5), 16 * ((3 * i) % 7 - 3)) for i in range(64)]
    raw = bytes((x >> bit) & 1 for pair in values for x in pair for bit in range(20))
    source = Tape()
    for bit in raw: source.append(bit)
    source.rewind(); image = body(source)
    before = {name: body(value.tape) for name, value in descriptors.items()}
    result = engine.run(source, descriptors)
    need(observed == ['enter'] and engine.closed, 'actual child and complete parent continuation executed')
    need(body(source) == image and all(body(value.tape) == before[name] for name, value in descriptors.items()),
         'complete caller borrowed input and descriptors preserved')
    need(compiler.closed and all(t.read() == BLANK for t in (*compiler.roles.values(), *compiler.snapshots)),
         'compiler descriptors and optional snapshots retired')
    import hashlib
    digest = hashlib.sha256(body(result)).hexdigest()
    result.clear(); source.clear()
    for value in descriptors.values(): value.close()
    for _, invalid, saved, _ in mutation_counts: invalid.close(); saved.close()
    return dict(status='PASS_ACTUAL_ENCODED_CALLER_PACKET_COMPILER', geometry_dimension=2,
                prefixes=2, rows=4, coefficients=2, complex_values=64,
                actual_child_descriptor_match=True, mutation_rejections=controls,
                endpoint_sha256=digest, source_and_descriptors_preserved=True,
                compiler_retired=True, paid_compiler_snapshot_retirement=invoice[0],
                fixed_compiler_tapes=78, optional_fixture_snapshot_tapes=2,
                scope='Actual retained Machine/gather/prepare_child/return/scatter and new encoded compiler; reduced geometry, no selected O73 native fixture or reconnection theorem.')


def global_fixture():
    """Actual complete-cover acquisition, compiler and child; reduced geometry."""
    from types import SimpleNamespace
    from cardinal_counts import Count
    from fixture_binding import FixtureBinding
    from machine import Machine, copy_symbols
    from bank_packets import BankPackets
    from macro_code import Code
    from ordinary import Ordinary
    from records import Tape
    from words import BLANK, need
    from fractions import Fraction as Q
    import hashlib
    binding = FixtureBinding()
    def native():
        return Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                        SimpleNamespace(families=0), (Code((('unreachable',),), 0),), capacity=64)
    compiler = PacketCompiler()
    acquisition = BankPackets(binding.families, 1, 1)
    child = Machine(binding, native(), binding.catalogue)
    # These fixed small fixture Counts are loaders, not compiler implementation.
    rowbits_gamma = Count.literal(640)
    bad_counts = {n: Count.literal(v) for n,v in [('width',4),('columns',2),('root_width',4)]}
    restored_counts = {n: Count.literal(v) for n,v in [('width',2),('columns',1),('root_width',2)]}
    nonleaf_boundary = Count.literal(3 ** 1000)
    expected_counts = {name:Count.literal(value) for name,value in [('prefixes',4),('rows',1),('width',1),('after',1)]}
    truncated = Tape(); truncated.append(0); truncated.rewind()
    records = []
    def body(t): return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    def decode(raw):
        numbers=[]
        for start in range(0,len(raw),20):
            x=sum(bit<<i for i,bit in enumerate(raw[start:start+20]))
            numbers.append(x-(1<<20) if x&(1<<19) else x)
        return list(zip(numbers[::2],numbers[1::2]))
    def encode(values): return bytes((int(x)>>i)&1 for z in values for x in z for i in range(20))
    def c_axis(values, bit, rows):
        out=[tuple(map(Q,z)) for z in values]
        # Four addresses times two coefficients in each row.
        for row in range(rows):
            for address in range(4):
                if address&bit: continue
                for coefficient in range(2):
                    i=(row*4+address)*2+coefficient
                    j=(row*4+address+bit)*2+coefficient
                    a,b=out[i];c,d=out[j]
                    out[i]=((a-b+c+d)/2,(a+b-c+d)/2)
                    out[j]=((a+b+c-d)/2,(-a+b+c+d)/2)
        need(all(x.denominator==1 for z in out for x in z),'finite fixture exact grid')
        return out
    class Caller(Machine):
        def finish_group(self):
            super().finish_group()
            if self.cover_index != binding.cover.size or records: return
            with self.scope.suspended():
                acquisition.select(((0,0),))
                acquisition.gather(self.roles['current'],self.c('prefixes'),self.c('unused'),rowbits_gamma)
                field=acquisition.packets[0]; original=body(field)
                parent_image={name:body(tape) for name,tape in self.roles.items()}
                rejections=[]
                def reject(label, operation, substring):
                    try: operation()
                    except ValueError as error:
                        need(substring in str(error),'precise global compiler rejection '+label)
                        rejections.append(label)
                    else: raise ValueError('accepted global compiler control '+label)
                reject('wrong producer fence',lambda:compiler.compile_global(self,field,1),'whole-cover producer fence')
                reject('short whole-family field',lambda:compiler.compile_global(self,truncated,0),'whole-family field bits')
                try:
                    copy_symbols(nonleaf_boundary.tape,self.c('root_width').tape)
                    rejection_state={name:(body(tape),tape.head) for name,tape in self.roles.items()}
                    field_state=(body(field),field.head)
                    reject('pre-remainder nonleaf does not admit service',
                           lambda:compiler.compile_global(self,field,0),
                           'post-remainder service nonleaf admission')
                    need(all((body(tape),tape.head)==rejection_state[name] for name,tape in self.roles.items())
                         and (body(field),field.head)==field_state,
                         'nonleaf rejection preserves caller descriptors and borrowed field')
                    need(compiler.closed and not compiler.pool.live and
                         all(t.read()==BLANK for t in compiler.roles.values()),
                         'nonleaf rejection retires all compiler temporaries')
                finally:
                    copy_symbols(restored_counts['root_width'].tape,self.c('root_width').tape)
                try:
                    for name,value in bad_counts.items():copy_symbols(value.tape,self.c(name).tape)
                    reject('insufficient actual child stock',lambda:compiler.compile_global(self,field,0),'actual child row stock')
                finally:
                    for name,value in restored_counts.items():copy_symbols(value.tape,self.c(name).tape)
                paid_tapes=tuple(dict.fromkeys((*compiler.roles.values(),*compiler.pool.tapes,*self.roles.values(),field)))
                before=[t.meter.record() for t in paid_tapes]
                descriptors=compiler.compile_global(self,field,0)
                setup_invoice={key:sum(t.meter.record()[key]-old[key] for t,old in zip(paid_tapes,before)) for key in ('reads','writes','moves')}
                # Bytes are interpreted only in this independent fixture oracle.
                expected={name:body(self.c(name).tape) for name in descriptors}
                for name,probe in expected_counts.items(): expected[name]=body(probe.tape)
                need({name:body(v.tape) for name,v in descriptors.items()}==expected,
                     'global cover folds into encoded prefixes and exact child fields')
                # Actual closed recursive endpoint on all covers of one family.
                returned=child.run(field,descriptors)
                expected_values=c_axis(decode(original),2,4)
                need(body(returned)==encode(expected_values),'actual whole-family child matches address oracle')
                returned.clear()
                retirement_before=[t.meter.record() for t in paid_tapes]
                compiler.close()
                retirement_invoice={key:sum(t.meter.record()[key]-old[key] for t,old in zip(paid_tapes,retirement_before)) for key in ('reads','writes','moves')}
                need(body(field)==original and all(body(tape)==parent_image[name] for name,tape in self.roles.items()),
                     'global compiler and native preserve producer bank and descriptors')
                acquisition.release()
                need(compiler.closed and child.closed,'whole-family descriptors and child retired')
                records.append(dict(prefixes=2,covers=2,native_prefixes=4,rows=1,coefficients=2,
                                    field_complex_values=32,controls=rejections,
                                    endpoint_sha256=hashlib.sha256(encode(expected_values)).hexdigest(),
                                    compiler_setup_validation_actions=setup_invoice,
                                    compiler_retirement_actions=retirement_invoice))
    engine=Caller(binding,native(),binding.catalogue)
    descriptors={n:Count.literal(v) for n,v in dict(prefixes=2,rows=4,front=0,compact_bits=0,
        before=0,width=2,after=0,back=0,spacing=1,guard=1,residue=0,component_bits=20,
        coefficients=2,root_width=2).items()}
    values=[(16*((7*i)%11-5),16*((3*i)%7-3)) for i in range(64)]
    source=Tape()
    for bit in encode(values):source.append(bit)
    source.rewind(); original=body(source)
    try:
        returned=engine.run(source,descriptors)
        need(len(records)==1 and body(source)==original,'actual global fence and borrowed source preservation')
        need(body(returned)==encode(c_axis(c_axis(values,1,8),2,8)),
             'entire actual parent continuation unchanged by global service')
        returned.clear()
        return dict(status='PASS_ACTUAL_GLOBAL_FAMILY_PACKET_COMPILER',fixture=records[0],
                    fixed_compiler_tapes=78,source_and_descriptors_preserved=True,
                    scope='Actual cover2 parent, whole-family BankPackets acquisition, encoded compiler, actual rank-one C child and completed parent; reduced geometry, not full QQ16 semantic installation.')
    finally:
        source.clear();truncated.clear();rowbits_gamma.close();nonleaf_boundary.close()
        for value in (*descriptors.values(),*bad_counts.values(),*restored_counts.values(),*expected_counts.values()):value.close()
        compiler.close()
