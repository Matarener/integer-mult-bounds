"""Small independent identities and rejection tests, also run under -O."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json

import bindings
bindings.activate()
from cardinal_counts import Count
from words import need
from check_kernel import one_case
import rotation


def reject(call, fragment):
    try:
        call()
    except ValueError as error:
        need(fragment in str(error), "intended control rejection: " + str(error))
        return
    raise ValueError("mutation unexpectedly accepted: " + fragment)


def split_checks():
    total=0
    for q in range(1,258):
        modulus=Count.literal(q)
        for amount in (-4,-3,-2,-1,1,2,3,4):
            large,small=rotation.split_lengths(modulus,amount)
            def value(count):
                bits=count.tape.cells[1:]
                digits=[]
                for bit in bits:
                    if bit not in (0,1):break
                    digits.append(bit)
                return sum(bit<<i for i,bit in enumerate(digits))
            need((value(large),value(small)) == (q-abs(amount)%q,abs(amount)%q),
                 "independent exact modular split")
            large.close();small.close();total+=1
        for amount in (0,5,-5,True,1.0):
            reject(lambda:rotation.split_lengths(modulus,amount),'fixed selected carry')
        modulus.close()
    zero=Count.literal(0)
    reject(lambda:rotation.split_lengths(zero,1),'positive cardinality')
    zero.close()
    return total


def run():
    split=split_checks()
    reject(lambda:one_case(5,2,3,-4,True,wrong_sign=True),'independent input columns')
    reject(lambda:one_case(5,2,3,-4,True,extra_bit=True),'complete rotation input')
    reject(lambda:one_case(3,2,3,-3,True,extra_bit=True),'complete identity rotation source')
    reject(lambda:one_case(5,2,3,-4,True,capacity=10),'inventory exhausted')
    good,_=one_case(5,2,3,-4,True,capacity=11)
    need(good['scratch']==8,'eight additional roles suffice and are attained')
    original=rotation.translated
    def extra_read(source,*args,**kwargs):
        source.read()
        return original(source,*args,**kwargs)
    with patch.object(rotation,'translated',extra_read):
        changed,_=one_case(5,2,3,-4,True)
    need(changed['total']==good['total']+1 and changed['physical']['reads']==good['physical']['reads']+1,
         'endpoint-preserving extra traffic detected')
    # The independent column check must still reject even on all-zero data.
    with patch('random.Random.randrange',return_value=0):
        reject(lambda:one_case(5,2,3,-4,True,wrong_sign=True),'independent input columns')
    # The source loader must reject an altered input before importing it.
    manifest=json.loads((bindings.HERE/'SOURCES.json').read_text())
    first=next(row for row in manifest['files'] if row['usage']=='input')
    with TemporaryDirectory() as path:
        root=Path(path)
        target=root/first['path'];target.parent.mkdir(parents=True)
        target.write_bytes((bindings.ROOT/first['path']).read_bytes()+b'\n')
        reject(lambda:bindings.authenticate(root=root),'source changed')
    return dict(split_cases=split,controls=9,scratch_peak=8,seed=6)
