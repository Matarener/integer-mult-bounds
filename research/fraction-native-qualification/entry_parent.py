"""Source-bound entry type gate for the exact predecessor contribution table.

Ali Romman: original Fraction arithmetic. Chris R / Clear1nsight with
substantial OpenAI Codex assistance: table and entry-domain proof. Apache-2.0.
The independent integer engine, arithmetic and complete output stay unchanged.
"""
from contextlib import contextmanager
from hashlib import sha256
import inspect
from pathlib import Path
import table_parent as parent

F=parent.F
CAPACITY=parent.CAPACITY


def certified_domain(word,weights,rounded):
    # Test exact container types before inspecting members. No user-defined
    # iteration, conversion, comparison, indexing or numeric methods run here.
    if type(word) is not dict or any(type(k) is not str for k in word):
        return False
    if type(word.get('public')) is not int or type(word.get('owned_fields')) is not int:
        return False
    program=word.get('program')
    if (type(program) is not list and type(program) is not tuple) or (type(weights) is not list and type(weights) is not tuple):
        return False
    if (type(rounded) is not set and type(rounded) is not frozenset) or any(type(op) is not str for op in rounded):
        return False
    for event in program:
        if (type(event) is not list and type(event) is not tuple) or len(event)<2:
            return False
        if type(event[0]) is not str:
            return False
        if any(type(x) is not str and type(x) is not int and type(x) is not bool and type(x) is not F for x in event):
            return False
    for row in weights:
        if (type(row) is not list and type(row) is not tuple) or len(row)<2:
            return False
        if type(row[0]) is not F or type(row[1]) is not F:
            return False
    return True


class Contributions(parent.Contributions):
    def certify(self,word,weights,rounded):
        self.certified=bool(self.capacity and certified_domain(word,weights,rounded))
        self.step=self._certified_step if self.certified else super().step

    def _certified_step(self,old,q,v,a,c):
        self.calls+=1
        key=(old.numerator,old.denominator,q.numerator,q.denominator,
             v.numerator,v.denominator,a.numerator,a.denominator,c.numerator,c.denominator)
        result=self.table.get(key)
        if result is not None:
            self.hits+=1
            return result
        self.misses+=1
        result=self.compute(old,q,v,a,c)
        if len(self.table)>=self.capacity:
            self.table.popitem(last=False)
            self.evictions+=1
        self.table[key]=result
        return result


def transformed(raw):
    text=parent.transformed(raw)
    seam='    contributions = _contribution_factory()\n'
    parent.need(text.count(seam)==1,'one entry type certification seam')
    return text.replace(seam,seam+'    contributions.certify(word,weights,rounded)\n')


def derive(reference,capacity=CAPACITY):
    parent.need(type(capacity) is int and 0<=capacity<=CAPACITY,'bounded integer table capacity')
    parent.need(reference.F is F,'exact standard Fraction type')
    parent.need(sha256(Path(reference.__file__).read_bytes()).hexdigest()==parent.MODULE_SHA256,'exact Fraction module bytes')
    original=reference.error_trace
    raw=inspect.getsource(original)
    text=transformed(raw)
    namespace=dict(reference.__dict__)
    exec(compile(raw,'<fraction-original-binding>','exec'),namespace)
    parent.need(parent.code_shape(original.__code__)==parent.code_shape(namespace['error_trace'].__code__),'live Fraction code agrees with source')
    parent.need(original.__defaults__ is None and original.__kwdefaults__ is None and original.__closure__ is None,'ordinary Fraction function')
    last=[None]
    def report(value):last[0]=None if value is None else dict(value)
    namespace.update(_contribution_factory=lambda:Contributions(capacity),_contribution_report=report)
    exec(compile(text,'<fraction-certified-contributions>','exec'),namespace)
    result=namespace['error_trace']
    result.statistics=lambda:None if last[0] is None else dict(last[0])
    return result


@contextmanager
def installed(reference,capacity=CAPACITY):
    original=reference.error_trace
    derived=derive(reference,capacity)
    reference.error_trace=derived
    try:yield derived
    finally:reference.error_trace=original
