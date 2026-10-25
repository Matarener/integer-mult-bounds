"""Closed-form Counter invoice, independent of the source's loop evaluator."""
def add(*rows):return tuple(sum(v) for v in zip(*rows))
def scale(n,row):return tuple(n*v for v in row)
def minus(a,b):return tuple(x-y for x,y in zip(a,b))


def index_copy(width):return (3*width+3,0,2*width+4)


def init(exponent,width):
    if not exponent:return (2*width+5,3*width+3,4*width+8)
    b=exponent.bit_length();zeros=width-b
    return (2*width+3,width+1+2*zeros,2*width+4+2*zeros)


def probe(exponent,width):
    b=max(1,exponent.bit_length())
    return add(init(exponent,width),(2*b+5,b+1,2*b+6))


def rundown(exponent,width):
    if not exponent:return probe(0,width)
    b=exponent.bit_length();p=exponent.bit_count()
    decrements=(7*exponent-2*p+1,2*exponent-p+2*b+1,6*exponent-2*p+2*b+2)
    return add(init(exponent,width),decrements,(7,2,8))


def predicted(exponents,width,precision,rho):
    active=[e for e in exponents if e]
    old=add(*(rundown(e,width) for e in exponents))
    new=add(*(probe(e,width) for e in exponents),*(scale(precision,rundown(e,width)) for e in active))
    return {'record_saving':minus(old,new),'index_saving':scale(-precision*len(active),index_copy(width)),
            'residue_saving':scale(sum(exponents)-int(bool(active)),rho),
            'old_radix_traversals':sum(exponents),'new_radix_traversals':int(bool(active))}
