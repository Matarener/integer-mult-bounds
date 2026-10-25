"""Physical wrapper tests at the new coupling, with reduced fixture scope.

The GL2 ordinary fixture is explicitly separate from the R437 GL64 adapter.
Retains Jose Manuel's provenance/return/ownership checks. Apache-2.0.
"""
from pathlib import Path
import sys
import types
from unittest.mock import patch
import json
import adapter


def run():
    ordinary,encoded,binary=adapter.predecessor.runtime()
    certified=encoded.Profile(numerator=1,denominator=576)
    interface=types.ModuleType('interface')
    interface.profile=lambda: certified
    def factory(q,binding,topology,programs,**options):
        adapter.require('profile' not in options,'one certified coupling profile')
        return ordinary.Ordinary(q,binding,topology,programs,profile=certified,**options)
    def binary_factory(native):
        adapter.require(native.profile==certified,'new binary consumer profile')
        return binary.Binary(native)
    interface.ordinary=factory;interface.binary=binary_factory
    sys.modules['interface']=interface
    source=adapter.HERE/'sources/ordinary/check_runtime.py'
    module=types.ModuleType('r437_reduced_runtime');module.__file__=str(source)
    exec(compile(source.read_text(),str(source),'exec'),module.__dict__)
    physical=module.run()
    # Exercise the exact Count power predicate used by width selection:
    # e=2^576; the old profile requires width2, the new also2. At e=2^576+1,
    # width3 is required by the new profile while old1/577 still requires2.
    from cardinal_counts import Count
    from check_support import inspect_count
    widths={}
    for value in (2**576,2**576+1):
        original=Count.literal(value)
        for denominator in (576,577):
            two=Count.literal(2)
            power=encoded.fixed_power(two,denominator,original)
            order=encoded.compare(power,original)
            widths[f'{value-2**576:+d}@1/{denominator}']=order
            power.close();two.close()
        original.close()
    adapter.require(list(widths.values())==[0,0,-1,0],'Count power decision distinguishes width2 from width3')
    return {'status':'PASS_NEW_PROFILE_REDUCED_PHYSICAL_RETURNS_AND_COUNT_WIDTH',
            'profile':{'numerator':1,'denominator':576},'physical':physical,'width2_power_comparison_at_boundary':widths,
            'scope':'q2 GL2 fixture and Count setup. Does not execute R437 GL64 or a T360/native/router cohort.'}


if __name__=='__main__':
    try:print(json.dumps(run(),sort_keys=True,indent=2))
    finally:adapter.predecessor.close()
