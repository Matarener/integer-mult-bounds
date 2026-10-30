"""Encoded atom powers sharing one validated radix walk; no numerical decoding."""
from runtime import need


class Powers:
    def __init__(self,env,workspace=None):
        self.env=env
        # Caller may supply its existing owned blank counter role. This is
        # not an arbitrary-dirty loan; its clean backing remains charged.
        self.workspace=env.records.Tape() if workspace is None else workspace
        self.Counter=env.counter_type(self.workspace)
        self.busy=False

    def multiply(self,items,ring,q):
        need(not self.busy,'non-reentrant fixed counter role')
        need(1<=len(items)<=3,'one to three compiled output roles')
        need(len({id(value.tape) for value,exponent in items})==len(items),'disjoint power outputs')
        need(all(value.tape is not self.workspace for value,exponent in items),'counter workspace separate from outputs')
        self.busy=True;counter=None;walk=None
        try:
            active=[]
            for value,exponent in items:
                counter=self.Counter(exponent)
                if not counter.finished:active.append((value,exponent))
                counter.close();counter=None
            if not active:return
            walk=self.env.cardinality.radix_power(ring,q)
            for _ in walk:
                for value,exponent in active:
                    counter=self.Counter(exponent)
                    while not counter.finished:
                        value.multiply_small(q)
                        counter.decrement()
                    counter.close();counter=None
        finally:
            if counter is not None:counter.close()
            if walk is not None:walk.close()
            self.busy=False
