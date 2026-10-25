# SPDX-License-Identifier: Apache-2.0
"""Source-derived successful external C leaf bounds and finite calibrations.

This is a cost checker, not an implementation of a compressed tape machine.
The exact countdown tariff is for the retained stream.Counter implementation.
Complete nonterminal C tariffs are deliberately rejected, rather than fabricated.
"""
from dataclasses import dataclass, asdict

INPUTS = ('prefixes','rows','front','compact_bits','before','width','after','back',
          'spacing','guard','residue','component_bits','coefficients','root_width')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def nat(x, positive=False):
    need(type(x) is int and x >= int(positive), 'exact nonnegative integer geometry')
    return x


def countdown_decrements(n):
    """Exact R/W/M for n successive decrement calls, including the final one.

    Initialization and close are excluded here and bounded separately below.
    Binary digit lengths are canonical, no spare high zero digit is assumed.
    """
    nat(n, True)
    z = n-n.bit_count()
    powers = n.bit_length()-1
    return (2*z+5*n+1, z+n+2*powers+3, 2*z+4*n+2*powers+4)


def countdown_cycle_upper(n):
    """Componentwise bound for construction, all decrements and final close.

    Source word is canonical, starts at head one, and is restored. Actual
    initialization normalizes the newly copied countdown; source ownership is
    unchanged. The zero case is included and has no decrement.
    """
    nat(n)
    d = max(1,n.bit_length())
    return tuple((countdown_decrements(n)[i] if n else 0)+64*(d+2)
                 for i in range(3))


@dataclass(frozen=True)
class Geometry:
    prefixes:int
    rows:int
    front:int
    compact_bits:int
    before:int
    width:int
    after:int
    back:int
    spacing:int
    guard:int
    residue:int
    component_bits:int
    coefficients:int
    root_width:int

    def validate(self):
        for name,value in asdict(self).items():
            nat(value,name in ('prefixes','rows','spacing','guard','component_bits',
                              'coefficients','root_width'))
        need(self.component_bits>=2,'signed component width')
        need(self.residue<self.spacing,'selected residue')
        need(self.width<=self.root_width,'global root width')
        return self

    @property
    def b(self):
        return self.front+3*self.compact_bits+self.before+self.width*self.spacing+self.after+self.back

    @property
    def v(self):
        return self.prefixes*self.rows*2*self.component_bits*self.coefficients*(1<<self.b)

    @property
    def gaussians(self):
        return self.prefixes*self.rows*self.coefficients*(1<<self.b)

    @property
    def L(self):
        # Counts in source setup include powers 2**b, not just encoding of b.
        return 16+self.b+sum(max(1,x.bit_length()) for x in asdict(self).values())

    def key(self, marker_class='steady'):
        need(marker_class in ('steady','fresh'),'explicit original-controller marker class')
        return (*tuple(asdict(self).items()),('marker_class',marker_class),
                ('binding','original-selected-73'),('root',True))


def terminal_branch(width, root_width, dimension=73):
    nat(width);nat(root_width,True);nat(dimension,True)
    need(width<=root_width,'node within global width')
    if width<dimension:return 'below dimension'
    return 'capped-power cutoff' if width**1000<root_width else None


def leaf_upper_geometry(g, marker_class='steady', materialize=True):
    """Complete external C.run leaf upper, separately in R/W/M.

    Applicable to either actual terminal branch of original selected C.
    It includes entry copies, shape/extent validation, all coefficient axes,
    exit transfer, private/controller cleanup and borrowed-head restoration.
    A fresh controller adds its explicit once-only 703-write potential.
    Successful arithmetic and source endpoint admission are premises.

    For enormous b, materialize=False returns a compact exact polynomial in
    v instead of allocating an integer with b binary digits.
    """
    need(isinstance(g,Geometry),'complete typed descriptor packet')
    g.validate();g.key(marker_class)
    branch=terminal_branch(g.width,g.root_width)
    need(branch is not None,'nonterminal C requires an evaluated completed recursion')
    L=g.L; C=1<<32
    # Each action component is <= C(w+1)[v+(G+1)L^4]. G=v/(2Hb).
    # Keep integer coefficients (A*v + D) by moving denominator upward:
    # G*L^4 <= v*ceil(L^4/(2Hb)). This rounding is in an upper direction.
    per_gaussian=(L**4+2*g.component_bits-1)//(2*g.component_bits)
    coefficient=C*(g.width+1)*(1+per_gaussian)
    constant=C*(g.width+1)*L**4
    marker=(0,703 if marker_class=='fresh' else 0,0)
    result={'kind':'componentwise source upper bound','branch':'selected C terminal: '+branch,
            'descendant_calls':0,'ordinary_calls':0,'L':L,'b':g.b,
            'component_upper_affine_in_v':{'coefficient':coefficient,'constant':constant,
                                         'marker':list(marker)},
            'leaf_axes':g.width,'geometry':asdict(g),
            'complete_external_boundary':True,'marker_class':marker_class,
            'not_a_production_root_admission_certificate':True}
    if materialize:
        v=g.v
        result['v']=v
        result['rwm_upper']=[coefficient*v+constant+x for x in marker]
        result['sum_upper']=sum(result['rwm_upper'])
    return result


def reserve_dominated_leaf_upper(width, L_upper, component_bits, *, descriptor_bound_certified, root_width=None):
    """Compact corollary for a separately certified full-descriptor L upper.

    A compressed RootPlan certificate may bound the bit length of a huge row
    count without materializing that Count. This function verifies the scalar
    reserve inequality; it does not certify the supplied descriptor bound.
    Returned integers multiply the same complete physical packet volume v.
    """
    nat(width);nat(L_upper,True);nat(component_bits,True)
    need(width<73 if root_width is None else terminal_branch(width,root_width) is not None,'selected terminal branch')
    need(descriptor_bound_certified is True,'external complete-descriptor bound certificate required')
    need(component_bits>=L_upper**4,'physical reserve dominates per-Gaussian setup')
    coefficient=(1<<33)*(width+1)
    return {'rwm_coefficients_of_v':[coefficient]*3,
            'sum_coefficient_of_v':3*coefficient,
            'width':width,'L_upper':L_upper,'component_bits':component_bits,
            'descendants':0,'source_bound':'CBODY equation (2)',
            'depends_on_external_descriptor_bound_certificate':True}


def shape(g):
    g.validate()
    return {'b':g.b,'row_bits':2*g.component_bits*g.coefficients*(1<<g.b),
            'v':g.v,'gaussians':g.gaussians,'descriptors':asdict(g)}


def source_guards():
    """Authenticated-source structure regression, not the proof of the bound."""
    import inspect, machine, axis_stream, coefficient_engine, stream, signed_linear
    checks=[(machine.Machine.node,'compare(self.c("width"), dimension) < 0'),
            (machine.Machine.apply_leaf,'self.leaf.run_leaf('),
            (machine.Machine.node,'test = fixed_power(self.c("width"), 1000, self.c("root_width"))'),
            (axis_stream.c_axis,'pairs = Counter(pair_count)'),
            (axis_stream.c_axis,'prefixes = Counter(before)'),
            (coefficient_engine.CoefficientEngine.run_leaf,'remaining = Counter(f)'),
            (signed_linear.linear_word,'remaining = Counter(width)'),
            (stream.Counter.decrement,'while tape.read() == ZERO:')]
    for function,text in checks:
        need(text in inspect.getsource(function),'literal leaf cost-source guard')
    return {'literal_source_guards':len(checks),'status':'PASS'}


def check_countdowns():
    from cardinal_counts import Count
    from stream import Counter
    cases=[]
    for n in (0,1,2,3,4,7,8,15,16,17,31,32,33,127,128,129,1023):
        source=Count.literal(n)
        initial=tuple(getattr(source.tape.meter,k) for k in ('reads','writes','moves'))
        counter=Counter(source)
        start=tuple(getattr(counter.tape.meter,k) for k in ('reads','writes','moves'))
        while not counter.finished:counter.decrement()
        end=tuple(getattr(counter.tape.meter,k) for k in ('reads','writes','moves'))
        delta=tuple(y-x for x,y in zip(start,end))
        expected=countdown_decrements(n) if n else (0,0,0)
        need(delta==expected,'exact source countdown decrement formula')
        counter.close()
        total=tuple(getattr(counter.tape.meter,k)+getattr(source.tape.meter,k)-initial[i]
                    for i,k in enumerate(('reads','writes','moves')))
        upper=countdown_cycle_upper(n)
        need(all(x<=y for x,y in zip(total,upper)),'complete countdown cycle bound')
        cases.append({'n':n,'decrements':list(delta),'cycle':list(total),'cycle_upper':list(upper)})
        source.close()
    return cases


def check_leaf_calls():
    """Complete reduced actual selected-controller leaves; no endpoint doubles.

    All source classes are loaded only after the caller authenticates runtime.
    Unused Ordinary exists because the real Machine constructor requires its
    closed inventory. No Ordinary branch executes in these leaf calls.
    """
    from fractions import Fraction
    from hashlib import sha256
    from types import SimpleNamespace
    import sys
    from cardinal_counts import Count
    from macro_code import Code
    from ordinary import Ordinary
    from records import Tape
    from words import BLANK
    from machine import Machine
    from selected_binding import SelectedBinding
    from selected_source import load
    from session import erase_marker
    import runtime
    history_state=runtime.module('qq16_cbody_state_model',runtime.predecessor()/'state_model.py')
    native=Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),
                    SimpleNamespace(families=0),(Code((('unreachable',),),0),),capacity=64)
    binding=SelectedBinding(load())
    # Catalogue has no influence on a leaf but use the actual selected compiler.
    from scalar_program import ScalarProgram
    catalogue={}
    for code in binding.codes.values():
        for op in code:
            if op[0]=='scalar':catalogue[op[-1]]=ScalarProgram(*op[-1])
    catalogue[('scale',-1,1)]=ScalarProgram('scale',-1,1)
    machine=Machine(binding,native,catalogue)
    cases=[]
    def body(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    def enc(values,H):return bytes((int(x)>>j)&1 for pair in values for x in pair for j in range(H))
    def oracle(values,g):
        out=[tuple(Fraction(x) for x in pair) for pair in values]
        # Active field address bits are from the left; actual coefficient
        # packing traverses the low selected active bit first.
        right=g.after+g.compact_bits+g.back
        records=1<<g.b
        for axis in range(g.width):
            bit=1<<(right+axis*g.spacing+g.residue)
            for row in range(g.prefixes*g.rows):
                for address in range(records):
                    if address&bit:continue
                    for c in range(g.coefficients):
                        i=(row*records+address)*g.coefficients+c
                        j=(row*records+address+bit)*g.coefficients+c
                        a,b=out[i];d,e=out[j]
                        out[i]=((a-b+d+e)/2,(a+b-d+e)/2)
                        out[j]=((a+b+d-e)/2,(-a+b+d+e)/2)
        need(all(x.denominator==1 for p in out for x in p),'independent exact leaf grid')
        return out
    # Include correlated nonconstant payload, an untouched spectator, repeated
    # successful generations, and coefficient/prefix domains. Keep tiny.
    specs=[(0,2,1,1),(1,2,1,1),(2,2,1,1),(1,3,2,2),(2,3,2,2),(5,5,1,1),(8,8,1,1),(2,2,1,1)]
    for generation,(width,b,prefixes,coefficients) in enumerate(specs):
        cutoff_fixture=generation==len(specs)-1
        if cutoff_fixture:
            machine.discard()
            from fixture_binding import FixtureBinding
            binding=FixtureBinding()
            native=Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),
                            SimpleNamespace(families=0),(Code((('unreachable',),),0),),capacity=64)
            machine=Machine(binding,native,binding.catalogue)
        g=Geometry(prefixes,1,0,0,0,width,b-width,0,1,1,0,20,coefficients,
                   width**1000+1 if cutoff_fixture else 73)
        source=Tape(); counts={k:Count.literal(v) for k,v in asdict(g).items()}
        values=[(512*((i*7+generation)%11-5),512*((i*3+generation)%7-3))
                for i in range(g.gaussians)]
        raw=enc(values,g.component_bits)
        for bit in raw:source.append(bit)
        source.rewind()
        snap={k:(v.tape.head,body(v.tape)) for k,v in counts.items()}
        roles=history_state.tapes(machine,source,counts)
        initial=tuple(sum(getattr(t.meter,k) for _,t in roles) for k in ('reads','writes','moves'))
        native_calls=[]
        oldrun=native.run
        def reject_native(*args,**kwargs):
            native_calls.append(True)
            raise ValueError('leaf unexpectedly entered Ordinary')
        native.run=reject_native
        try:output=machine.run(source,counts)
        finally:native.run=oldrun
        observed=tuple(sum(getattr(t.meter,k) for _,t in roles)-initial[j]
                       for j,k in enumerate(('reads','writes','moves')))
        expected=enc(oracle(values,g),g.component_bits)
        need(body(output)==expected,'independent completed Gaussian endpoint')
        need(body(source)==raw and source.head==1,'borrowed payload bytes and head')
        need(all((v.tape.head,body(v.tape))==snap[k] for k,v in counts.items()),'borrowed descriptors')
        need(machine.closed and not native_calls,'successful leaf return without descendants/native')
        upper=leaf_upper_geometry(g,'fresh' if generation==0 or cutoff_fixture else 'steady')
        need(all(a<=b for a,b in zip(observed,upper['rwm_upper'])),'source-derived complete C upper')
        cases.append({'generation':generation,'geometry':asdict(g),'payload_bits':len(raw),
                      'rwm':list(observed),'upper':upper['rwm_upper'] if not cutoff_fixture else None,
                      'calibration_of_selected_geometry_bound':not cutoff_fixture,
                      'result_sha256':sha256(expected).hexdigest(),
                      'actual_binding_dimension':binding.dimension,
                      'actual_controller_branch':'capped-power cutoff' if cutoff_fixture else 'below dimension leaf',
                      'selected_binding':not cutoff_fixture,
                      'ordinary_branch':'not invoked','borrowed_preserved':True,
                      'complete_return':True,'production_root_admission':False})
        output.clear();source.clear()
        for x in counts.values():x.close()
    machine.discard()
    need(all(t.read()==BLANK for t in machine.parked),'terminal controller packet cleanup')
    return cases


def check(include_large_cutoff=False):
    guards=source_guards()
    counters=check_countdowns()
    leaves=check_leaf_calls()
    g=Geometry(1,1,0,0,0,8,65,0,1,1,0,16,1,73)
    need(g.b==73 and g.v==2*16*(1<<73),'active/spectator packet preservation')
    one=Geometry(1,1,0,0,0,1,72,0,1,1,0,16,1,73)
    need(one.v==g.v and one.key()!=g.key(),'equal volume does not imply rank-only cache key')
    rejected=[]
    for label,call in (
        ('nonleaf recursion omitted',lambda:leaf_upper_geometry(Geometry(1,1,0,0,0,73,0,0,1,1,0,16,1,73))),
        ('logical width substituted for stored width',lambda:Geometry(1,1,0,0,0,1,0,0,1,1,0,1,1,73).validate()),
        ('bool descriptor alias',lambda:Geometry(True,1,0,0,0,1,0,0,1,1,0,16,1,73).validate()),
        ('unnamed marker class',lambda:leaf_upper_geometry(one,'unknown')),
        ('global cutoff equality treated as leaf',lambda:need(terminal_branch(144,144**1000) is not None,'strict cutoff equality'))):
        try:call()
        except ValueError:rejected.append(label)
        else:raise ValueError('accepted invalid cost claim: '+label)
    return {'source_guards':guards,'countdown_calibrations':counters,
            'complete_reduced_C_calibrations':leaves,'cutoff_kernel_calibrations':check_cutoff_kernel(include_large_cutoff),
            'negative_controls':rejected,
            'scope':'selected C terminal upper only; no nonterminal/Ordinary price or complete QQ16 sign'}


def check_cutoff_kernel(include_large=False):
    """Actual encoded capped-power branch tests, without loading 2**w payload.

    All temporary Count work uses the real fixed scratch pool. This is a
    source control-kernel calibration, not a completed width-73 C payload.
    """
    from cardinal_counts import Count
    from encoded import fixed_power, compare
    from scratch_pool import ScratchPool
    from session import OuterScope
    from words import BLANK
    tests=[(2,1000,2**1000+1),(2,1000,2**1000),(73,1000,73**2)]
    if include_large:tests.append((73,1000,73**1000+1))
    receipts=[]
    for value,exponent,cap in tests:
        pool=ScratchPool(256);scope=OuterScope(pool)
        x=Count.literal(value);limit=Count.literal(cap)
        roles=(*pool.tapes,x.tape,limit.tape)
        before=tuple(sum(getattr(t.meter,k) for t in roles) for k in ('reads','writes','moves'))
        with scope.installed():
            out=fixed_power(x,exponent,limit)
            # The following comparison is a real source instruction, included
            # in the calibration just as Machine.node evaluates its cutoff.
            is_leaf=compare(out,limit)<0
            out.close()
        observed=tuple(sum(getattr(t.meter,k) for t in roles)-before[i]
                       for i,k in enumerate(('reads','writes','moves')))
        need(is_leaf==(value**exponent<cap),'actual capped-power cutoff agrees')
        need(not pool.live and all(t.read()==BLANK for t in pool.tapes),'cutoff scratch closes')
        receipts.append({'width':value,'exponent':exponent,'cap_bits':cap.bit_length(),
                         'cap_relation': 'power+1' if cap==value**exponent+1 else 'power' if cap==value**exponent else 'smaller',
                         'leaf':is_leaf,'rwm':list(observed),
                         'complete_C_payload_executed':False})
        x.close();limit.close()
    return receipts
