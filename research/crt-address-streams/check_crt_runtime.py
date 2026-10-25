"""Independent finite oracles; host decoding occurs only in this checker."""
from contextlib import contextmanager
from itertools import product
from math import prod, gcd
from unittest.mock import patch
from cardinal_counts import Count
from records import Tape
from words import BLANK, LEFT, RIGHT, need
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
from tensor_router import FullRouter
from tensor_fixture import literal_native
from crt_converter import Converter
from crt_shape import Shape
from crt_descriptor import compile_descriptor
from crt_offsets import compile_offsets
from crt_shear import shifted
from encoded_crt import inverse, read_offset, write_count


def tape(bits=()):
    out = Tape()
    for bit in bits:
        out.append(bit)
    out.rewind()
    return out


def image(value):
    return bytes(value.cells), value.head


def read(t):
    t.rewind()
    out = []
    while t.read() != BLANK:
        out.append(t.read())
        t.step(1)
    t.rewind()
    return out


def value(count):
    return sum(b << i for i, b in enumerate(read(count.tape)[:-1]))


def consume(t):
    t.clear()
    erase_marker(t)


@contextmanager
def counts(*values):
    objects = [Count.literal(v) for v in values]
    try:
        yield objects
    finally:
        for obj in reversed(objects):
            obj.close()


def shape_tape(axes):
    result = tape()
    for pair in axes:
        with counts(*pair) as fields:
            for field in fields:
                write_count(field, result)
    result.rewind()
    return result


def expect_failure(operation, phrase=None):
    try:
        operation()
    except ValueError as error:
        need(phrase is None or phrase in str(error), 'expected scoped rejection: '+str(error))
        return
    raise ValueError('negative control accepted')


def blank_engine(engine):
    need(engine.closed and not engine.pool.live and engine.current is None, 'complete CRT ownership return')
    engine.idle()
    for obj in (engine, engine.router, engine.router.router):
        need(not obj.pool.live and obj.closed, 'complete physical descendant return')
        for t in obj.pool.tapes:
            need(t.head == 1 and all(b == BLANK for b in t.cells), 'blank scratch including owned origin')


def oracle_map(axes):
    lengths = [s for s, _ in axes]
    prefixes = [prod(lengths[:i]) for i in range(len(axes))]
    mapping = []
    for k in range(prod(lengths)):
        b = [(k*pow(P, -1, s)) % s for P, s in zip(prefixes, lengths)]
        target = 0
        for digit, s in zip(b, lengths):
            target = target*s+digit
        mapping.append(target)
    need(sorted(mapping) == list(range(prod(lengths))), 'independent CRT bijection')
    # Direct group law, not a forward/inverse roundtrip.
    for k in range(prod(lengths)):
        for l in range(prod(lengths)):
            need(all(((k+l)*pow(P,-1,s))%s ==
                     ((k*pow(P,-1,s))%s+(l*pow(P,-1,s))%s)%s
                     for P,s in zip(prefixes,lengths)), 'independent cyclic group law')
    return mapping


def mapped(bits, mapping, width, rows, reverse=False):
    S = len(mapping)
    out = [0]*len(bits)
    for row in range(rows):
        for old,new in enumerate(mapping):
            a,b = (new,old) if reverse else (old,new)
            out[(row*S+b)*width:(row*S+b+1)*width] = bits[(row*S+a)*width:(row*S+a+1)*width]
    return out


def complete_columns():
    receipts = []
    engine = Converter(FullRouter(literal_native()))
    for axes, rows in ((((3,4),),2), (((3,4),(5,8)),2),
                       (((5,8),(3,4)),1), (((3,4),(5,8),(7,8)),1)):
        mapping = oracle_map(axes)
        S = len(mapping)
        # All S basis columns are opaque record bits in one complete invocation.
        raw = [int(j == (k+row)%S) for row in range(rows) for k in range(S) for j in range(S)]
        for direction in (False,True):
            source, shape = tape(raw), shape_tape(axes)
            with counts(len(axes),16,S,rows) as params:
                borrowed = [source,shape,*(c.tape for c in params)]
                before = [image(t) for t in borrowed]
                output = engine.run(source,shape,*params,inverse=direction)
                actual = read(output)
                need(actual == mapped(raw,mapping,S,rows,direction), 'all independent CRT source columns')
                need(before == [image(t) for t in borrowed], 'exact borrowed CRT bytes and heads')
                need(engine.last_counts['global_routes'] == 1 and
                     engine.last_counts['padding_passes'] == 2 and
                     engine.last_counts['triangular_shifts'] == len(axes), 'complete conversion obligations')
                expect_failure(lambda: engine.run(source,shape,*params), 'consume prior CRT output')
                consume(output)
                blank_engine(engine)
                source.clear();shape.clear()
        receipts.append(dict(axes=axes,rows=rows,columns=S,directions=2))
    return receipts,engine.pool.peak


def descriptor_and_prefix():
    receipts=[]
    for axes in (((3,4),(5,8)),((5,8),(3,4)),((3,4),(5,8),(7,8))):
        pool=ScratchPool(96)
        source=shape_tape(axes)
        with counts(len(axes)) as (D,):
            with sealed_constructors(),OuterScope(pool).installed():
                shape=Shape(source,D,pool.acquire)
                try:
                    widths=[t.bit_length()-1 for s,t in axes]
                    n=sum(widths);w=max(1,(n-1).bit_length())
                    forward={}
                    for axis,width in enumerate(widths):
                        lo=sum(widths[:axis]);hi=n-lo-width
                        for j in range(width):forward[lo+j]=hi+j
                    from router_metadata import Pairs,write_pair
                    for inv in (False,True):
                        desc,width=compile_descriptor(shape,pool.acquire,inv)
                        direct={b:a for a,b in forward.items()} if inv else forward
                        frozen=pool.acquire()
                        for a,b in sorted(direct.items()):
                            with counts(a,b,w) as (ca,cb,cw):write_pair(frozen,ca,cb,cw)
                        frozen.rewind()
                        need(read(desc)==read(frozen), 'exact frozen descriptor codec')
                        Pairs(desc,shape.bits,width).validate(shape.bits)
                        frozen.clear();desc.clear();width.close()
                    for index in range(len(axes)):
                        with counts(index) as (I,):
                            B,offsets=compile_offsets(shape,I,pool.acquire)
                        lower=axes[:index]
                        expected=[]
                        for digits in product(*(range(t) for s,t in lower)):
                            valid=all(a<s for a,(s,t) in zip(digits,lower))
                            P=prod(s for s,t in lower)
                            a=sum(digit*prod(s for s,t in lower[:j]) for j,digit in enumerate(digits))
                            expected.append((a*pow(P,-1,axes[index][0]))%axes[index][0] if valid else 0)
                        need(value(B)==len(expected), 'complete padded lower-prefix extent')
                        with counts(index) as (I,):
                            modulus=shape.axis(I)
                        for amount in expected:
                            c=read_offset(offsets,modulus[0]);need(value(c)==amount,'independent original prefix offset');c.close()
                        need(offsets.read()==BLANK,'complete offset control page')
                        for c in modulus:c.close()
                        B.close();offsets.clear()
                finally:shape.close()
            pool.empty()
        source.clear();receipts.append(dict(axes=axes,peak_roles=pool.peak))
    return receipts


def shear_geometry():
    # Every padded prefix/target/spectator has a distinct multi-bit record.
    B,s,t,R=4,5,8,9
    amounts=[1,0,4,0]
    raw=[(record>>bit)&1 for record in range(B*t) for bit in range(R)]
    receipts=[]
    for reverse in (False,True):
        pool=ScratchPool(64);source=tape(raw);offset=tape()
        for flag,amount in zip((1,0,1,0),amounts):
            offset.append(flag)
            with counts(amount) as (v,):write_count(v,offset)
        offset.rewind()
        with counts(B,s,t,R) as params:
            with sealed_constructors(),OuterScope(pool).installed():
                result=shifted(source,offset,*params,pool.acquire,inverse=reverse)
                actual=read(result);expected=[0]*len(raw)
                for prefix in range(B):
                    for target in range(t):
                        new=((target+(-1 if reverse else 1)*amounts[prefix])%s) if target<s else target
                        expected[(prefix*t+new)*R:(prefix*t+new+1)*R]=raw[(prefix*t+target)*R:(prefix*t+target+1)*R]
                need(actual==expected,'complete shear with nonzero invalid prefixes and tails')
                result.clear()
            pool.empty()
        receipts.append(dict(inverse=reverse,peak_roles=pool.peak))
        source.clear();offset.clear()
    return receipts


def inverse_units():
    total=0
    pool=ScratchPool(64)
    with sealed_constructors(),OuterScope(pool).installed():
        for modulus in range(3,66,2):
            for a in range(2*modulus):
                with counts(a,modulus) as (A,M):
                    if gcd(a,modulus)==1:
                        x=inverse(A,M);need(value(x)==pow(a,-1,modulus),'independent modular inverse');x.close()
                    else:expect_failure(lambda:inverse(A,M),'coprime CRT prefix')
                total+=1
    pool.empty()
    return dict(cases=total,peak_roles=pool.peak)


def typed_plan():
    from tensor_plan import TensorPlan
    source=tape([1,1,0,1,0,1])  # little-endian 3,5; ell=3
    flags=tape([0])
    with counts(1,3,16,2,1,16,0,1,2,1,1) as parameters:
        plan=TensorPlan(source,flags,*parameters,Tape,production=False)
    try:
        need((value(plan.source_product),value(plan.target_product),value(plan.address_bits))==(15,32,5),
             'actual TensorPlan fixture dimensions')
        width=value(plan.record_bits)
        raw=[(k>>j)&1 for k in range(15) for j in range(width)]
        payload=tape(raw)
        ports=[plan.sources,plan.flags,plan.axis_rows,*(v.tape for v in plan.fields.values()),payload]
        before=[image(t) for t in ports]
        engine=Converter(FullRouter(literal_native()))
        with counts(1) as (rows,):
            output=engine.run_plan(payload,plan,rows)
            expected=mapped(raw,oracle_map(((3,4),(5,8))),width,1)
            need(read(output)==expected,'actual typed tensor bridge')
            need([image(t) for t in ports]==before,'all actual plan ports restored')
            consume(output);blank_engine(engine)
        payload.clear()
        return dict(source_records=15,padded_records=32,address_bits=5,record_bits=width,
                    peak_roles=engine.pool.peak,production=False)
    finally:
        plan.close();source.clear();flags.clear()


def rejection_controls():
    engine=Converter(FullRouter(literal_native()));total=0
    with counts(2,16,1,1) as params:
        good_shape=shape_tape(((3,4),(5,8)));good=tape([int(i==1) for i in range(15)])
        def rejected(source,shape,phrase):
            nonlocal total
            expect_failure(lambda:engine.run(source,shape,*params),phrase)
            blank_engine(engine);total+=1
        for axes,phrase in ((((3,4),(3,4)),'coprime'),(((2,4),(5,8)),'odd CRT'),
                            (((3,6),(5,8)),'power-of-two'),(((5,4),(3,4)),'strict padded')):
            shape=shape_tape(axes);rejected(good,shape,phrase);shape.clear()
        for raw,phrase in (([0]*14,'complete Boolean'),([0]*16,'complete CRT padding source'),
                           ([0]*7+[RIGHT]+[0]*7,'complete Boolean')):
            payload=tape(raw);rejected(payload,good_shape,phrase);payload.clear()
        malformed=tape([0,0,RIGHT]);rejected(good,malformed,'canonical');malformed.clear()
        extended=shape_tape(((3,4),(5,8)));extended.clear()
        for bit in read(good_shape)+[1]:extended.append(bit)
        extended.rewind();rejected(good,extended,'complete CRT source shape');extended.clear()
        expect_failure(lambda:engine.run(good,good,*params),'external complete CRT ports');total+=1
        expect_failure(lambda:engine.run(engine.output,good_shape,*params),'external complete CRT ports');total+=1
        # Wrong algebra and wrong axis order are caught by a direct coefficient oracle.
        from crt_converter import Converter as Actual
        original=Actual.triangular
        from crt_offsets import residue as actual_residue
        def check_wrong():
            out=None
            try:
                out=engine.run(good,good_shape,*params)
                need(read(out)==mapped(read(good),oracle_map(((3,4),(5,8))),1,1),
                     'direct mutant coefficient mismatch')
            finally:
                if out is not None:consume(out)
        with patch('crt_offsets.residue',lambda a,m:Count.literal(0)):
            expect_failure(check_wrong,'direct mutant');total+=1
        with patch.object(Actual,'triangular',lambda self,shape,rows,R,inv:original(self,shape,rows,R,not inv)):
            expect_failure(check_wrong,'direct mutant');total+=1
        from crt_converter import compile_descriptor as actual_descriptor
        with patch('crt_converter.compile_descriptor',lambda s,f,inv:actual_descriptor(s,f,not inv)):
            expect_failure(check_wrong);total+=1
        blank_engine(engine)
        good_shape.clear();good.clear()
    # Nonzero padding is a rejection, not silently discarded information.
    pool=ScratchPool(64);shape_source=shape_tape(((3,4),(5,8)))
    from crt_padding import padded
    with counts(2,1,1) as (D,C,R):
        payload=tape([1]*32)
        with sealed_constructors(),OuterScope(pool).installed():
            shape=Shape(shape_source,D,pool.acquire)
            try:
                expect_failure(lambda:padded(payload,shape,C,R,pool.acquire,remove=True),'zero CRT address padding')
                total+=1
            finally:shape.close()
        pool.empty();payload.clear()
    shape_source.clear()
    # Dirty prior work is not accepted as an empty workspace.
    dirty=Converter(FullRouter(literal_native()))
    dirty.pool.tapes[0].write(1)
    with counts(2,16,1,1) as params:
        source=tape([0]*15);shape=shape_tape(((3,4),(5,8)))
        expect_failure(lambda:dirty.run(source,shape,*params),'empty body');total+=1
        source.clear();shape.clear()
    return dict(controls=total,peak_roles=engine.pool.peak)
