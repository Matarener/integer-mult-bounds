"""Certified downward Gaussian rows and a norm-preserving tensor reference.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
This is host arithmetic, not a physical multitape implementation.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import isqrt, prod
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def authenticate_inputs():
    manifest = json.loads((ROOT / 'INPUTS.json').read_text(encoding='utf-8'))
    for name, digest in manifest['sha256'].items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'input path')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'source hash: '+name)

authenticate_inputs()
sys.path.insert(0, str(ROOT / 'vendor'))
from intervals import Interval, pi_interval, exp_negative


def integer(value, minimum, name):
    require(type(value) is int and value >= minimum, name)
    return value


def cap(u):
    integer(u, 1, 'integer u >= 1')
    return F(1, 2) + F(1, 20**u - 1)


def sqrt_interval(u, bits):
    integer(u, 1, 'integer u >= 1')
    integer(bits, 1, 'positive working precision')
    square = u << (2*bits)
    lower = isqrt(square)
    return Interval(lower, lower if lower*lower == square else lower+1, bits)


def tail_bound(u, radius):
    integer(u, 1, 'integer u >= 1')
    integer(radius, 1, 'positive radius')
    a, b = 3*radius*radius // u, 3*(2*radius+1) // u
    require(b >= 1, 'geometric tail ratio')
    return F(1, 1 << a) / (1-F(1, 1 << b))


@dataclass(frozen=True)
class Row:
    source: int
    target: int
    index: int
    u: int
    bits: int
    radius: int
    weights: tuple[int, ...]
    deficit: F
    terms: int

    @property
    def mass(self):
        return F(sum(self.weights), 1 << self.bits)

    def check(self):
        for x, lo, name in [(self.source,1,'source'),(self.target,1,'target'),
                            (self.u,1,'u'),(self.bits,8,'bits >= 8'),(self.radius,1,'radius')]:
            integer(x,lo,name)
        require(type(self.index) is int and 0 <= self.index < self.target, 'row index')
        require(len(self.weights) == self.source, 'row width')
        require(all(type(x) is int and x >= 0 for x in self.weights), 'positive lower weights')
        require(self.mass <= cap(self.u) < F(3,5), 'certified row mass')
        require(self.deficit >= 0 and self.terms > 0, 'row error/terms')


@lru_cache(None, typed=True)
def prepare_row(source, target, index, u, bits):
    for x,lo,name in [(source,1,'source'),(target,1,'target'),(u,1,'u'),(bits,8,'bits >= 8')]:
        integer(x,lo,name)
    require(type(index) is int and 0 <= index < target, 'row index')
    center = F(source*index, target)
    radius = max(u, isqrt(u*(bits+16))+2)
    first = center.numerator // center.denominator - radius
    last = -((-center.numerator)//center.denominator) + radius
    denom = 2*sqrt_interval(u,bits)
    pi = pi_interval(bits)
    weights = [0]*source
    deficit = tail_bound(u,radius)
    for j in range(first,last+1):
        argument = pi * ((F(j)-center)**2/u)
        enclosure = exp_negative(argument) / denom
        lower = max(0,enclosure.lo)
        require(lower <= enclosure.hi, 'positive coefficient enclosure')
        weights[j % source] += lower
        deficit += F(enclosure.hi-lower, 1 << bits)
    row = Row(source,target,index,u,bits,radius,tuple(weights),deficit,last-first+1)
    row.check()
    return row


def prepare(source,target,u,bits):
    integer(target,1,'target')
    return tuple(prepare_row(source,target,k,u,bits) for k in range(target))


def truncate(numerator, denominator):
    return numerator//denominator if numerator >= 0 else -((-numerator)//denominator)


def line(values, rows, precision):
    integer(precision,1,'positive grid precision')
    require(bool(rows), 'nonempty rows')
    require(all(isinstance(z,tuple) and len(z)==2 and all(type(c) is int for c in z)
                for z in values), 'encoded complex grid')
    require(len(values)==rows[0].source, 'source length')
    require(all(a*a+b*b <= 1 << (2*precision) for a,b in values), 'unit disk input')
    out=[]
    for row in rows:
        row.check()
        require(row == prepare_row(row.source,row.target,row.index,row.u,row.bits),
                'row differs from certified preparation')
        require(row.source==len(values), 'row source agreement')
        a=sum(w*z[0] for w,z in zip(row.weights,values))
        b=sum(w*z[1] for w,z in zip(row.weights,values))
        out.append((truncate(a,1 << row.bits),truncate(b,1 << row.bits)))
    return out


def offset(coords, shape):
    result=0
    for k,n in zip(coords,shape):
        result=result*n+k
    return result


def window(storage, source_positions, output_positions, rows, precision):
    """Host frame adapter: read named sources, change only disjoint outputs."""
    require(len(set(source_positions))==len(source_positions), 'injective source positions')
    require(len(set(output_positions))==len(output_positions), 'injective output positions')
    require(set(source_positions).isdisjoint(output_positions), 'disjoint borrowed input')
    require(len(output_positions)==len(rows), 'complete output window')
    result=line([storage[k] for k in source_positions],rows,precision)
    dest=storage.copy()
    for key,value in zip(output_positions,result):
        dest[key]=value
    return dest


def tensor(values, specs, precision, bits):
    """Expand each declared axis once, with independent spectator lines.

    specs is a nonempty tuple of (source, target, u). Returns grid values,
    final row-major shape and a rigorously propagated sup-norm error bound.
    """
    integer(precision,1,'positive grid precision')
    integer(bits,8,'coefficient precision >= 8')
    require(bool(specs), 'at least one expansion axis for chirp handoff')
    for spec in specs:
        require(len(spec)==3, 'axis triple')
        for x in spec: integer(x,1,'positive axis parameter')
    shape=[s for s,_,_ in specs]
    require(len(values)==prod(shape), 'tensor source cardinality')
    current=list(values)
    norm_bound,error=F(1),F(0)
    for axis,(s,t,u) in enumerate(specs):
        rows=prepare(s,t,u,bits)
        delta=max(r.deficit for r in rows)
        nextshape=shape.copy();nextshape[axis]=t
        dest=[None]*prod(nextshape)
        spectator=[i for i in range(len(shape)) if i != axis]
        for coords in product(*(range(shape[i]) for i in spectator)):
            index=[0]*len(shape)
            for i,k in zip(spectator,coords): index[i]=k
            data=[]
            for k in range(s):
                index[axis]=k; data.append(current[offset(index,shape)])
            result=line(data,rows,precision)
            for k,z in enumerate(result):
                index[axis]=k;dest[offset(index,nextshape)]=z
        error=cap(u)*error+delta*norm_bound+F(2,1 << precision)
        norm_bound*=cap(u)
        require(all(z is not None for z in dest), 'complete tensor output')
        require(all((z[0]*z[0]+z[1]*z[1])*norm_bound.denominator**2 <=
                    (1 << (2*precision))*norm_bound.numerator**2 for z in dest),
                'tensor hard norm invariant')
        current,shape=dest,nextshape
    return current,tuple(shape),error,norm_bound
