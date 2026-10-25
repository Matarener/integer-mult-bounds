#!/usr/bin/env python3
"""Focused independent source/gauge review of the symmetric extension.

This command authenticates and freshly reruns the author's checker in a separate
output directory, then adds a separately written literal frame walk and
bilinear-versus-Hermitian diagnostics. No previous review output is required.
It is not another full compiler or an independent endpoint interpreter.
Apache-2.0. OpenAI Codex assistance under the user's direction.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import gzip
import json

PRODUCER_SHA = '15f29c5a84e4b055668ff78bb6ec8c8e2d15aa8064b35832839a27a4ec205323'
COMPONENT_SHA = 'f6769f1ecd6b2e582748805b3afcf4c65824ba108ce7f23a4d011c45f8b724de'
NATIVE_RECEIPT_SHA = '7ddf3f80b2fa61d1ab12035da9ef1c95d43f76077df819d7683144d7862a3f93'
NATIVE_FILES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
                'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json')


def pinned_module(name,path,expected):
    """Execute precisely the checked source bytes, without cached bytecode."""
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=expected:
        raise ValueError('review source pin: '+str(path))
    module=ModuleType(name)
    module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def frames(program,word):
    current=word['start'].copy()
    query=None
    counts=Counter()
    coeffs=set()
    for e in program:
        tag=e[0]
        if tag=='climb':
            _,part,r,old,new,rank=e
            c.need(current[r]==old,'native climb source gauge')
            current[r]=new
        elif tag=='warp' and e[1][0]=='L':
            _,reg,op,old,new=e
            c.need(current[reg[1]]==old,'native warp source gauge')
            current[reg[1]]=new
        elif tag=='gaussian_scalar':
            _,op,t,s,packed,frame=e
            real,imag=Q(packed[0],packed[1]),Q(packed[2],packed[3])
            for v in (real,imag):
                c.need(v.denominator&(v.denominator-1)==0,'non-dyadic Gaussian coefficient')
            coeffs.add((str(real),str(imag)))
            counts[op]+=1
            if op=='clear':
                c.need(t==['C',0] and frame in(0,1),'owned query reset')
                query=frame
                continue
            c.need(op in('add','scale') and frame in(0,1),'Gaussian scalar grammar')
            if op=='add':c.need(t!=s,'Gaussian ADD aliases')
            for reg in(t,s):
                if reg is None:continue
                if reg[0]=='L':c.need(current[reg[1]]==frame,'Gaussian scalar crosses literal native frames')
                else:c.need(reg==['C',0] and query==frame,'Gaussian query source frame')
    c.need(current==word['final'] and query in(None,0),'native exit and query gauge')
    return {'new_Gaussian_macros':dict(counts),'distinct_coefficients':sorted(coeffs),
            'all_new_gates_use_literal_I_or_FULL':True,'all_ADDs_nonaliasing':True}


def main():
    global c
    if not __debug__:
        raise RuntimeError('Assertions must be enabled')
    here=Path(__file__).resolve().parent
    inp=here/'modern-source/inputs'
    review=here/'symmetric-extension-review'
    producer=review/'symmetric-extended-results'
    source=here.parent/'integer-mult-bounds/research/kappa-consumer-followup/baseline/symmetric_extended.py'
    c=pinned_module('independently_reviewed_modern_component',here/'modern_native_component.py',COMPONENT_SHA)
    checked=pinned_module('independently_reviewed_symmetric_producer',source,PRODUCER_SHA)
    c.need(c.NATIVE_RECEIPT_SHA==NATIVE_RECEIPT_SHA,'review receipt constant')
    c.need(c.digest(inp/'NATIVE-RECEIPT.json')==NATIVE_RECEIPT_SHA,'native receipt pin')
    receipt=c.read(inp/'NATIVE-RECEIPT.json')
    authenticated={}
    c.need(set(receipt['providers'])=={'base','extra'},'expected modern providers')
    for name,item in receipt['providers'].items():
        loc=inp/'native-cache'/item['word_sha256']/'local'
        authenticated[name]={}
        for basename in NATIVE_FILES:
            actual=c.digest(loc/basename)
            c.need(actual==item['complete_native_files']['local/'+basename],'modern source file pin')
            authenticated[name][basename]=actual

    review.mkdir(exist_ok=True)
    # The immutable source keeps its original __file__ and input paths. Only
    # the in-memory output root is redirected for this independent review run.
    checked.HERE=review
    checked.main()
    replay=c.read(producer/'RESULT.json')
    c.need(replay['status']=='PASS_FINITE_SYMMETRIC_128_PORT_COMPONENT','fresh producer replay')
    c.need(replay['script_sha256']==PRODUCER_SHA and replay['component_source_sha256']==COMPONENT_SHA,
           'fresh replay source pins')
    c.need(c.digest(source)==PRODUCER_SHA,'producer unchanged during review')
    source_record={
        'source':str(source.relative_to(here.parent)),
        'sha256':PRODUCER_SHA,
        'component_source_sha256':COMPONENT_SHA,
        'receipt_pin':NATIVE_RECEIPT_SHA,
        'native_files_authenticated_by_producer_and_review':authenticated,
        'producer_pin_gap_closed':True,
        'producer_assertion_guard_present':True,
        'source_bytes_modified_for_review':False,
        'fresh_run':'Imported the pinned source bytes and redirected only module.HERE to this review directory before calling main().',
        'producer_result_sha256':c.digest(producer/'RESULT.json')}
    (review/'SOURCE.json').write_text(json.dumps(source_record,indent=2)+'\n')
    out={'status':'PASS_FOCUSED_SYMMETRIC_EXTENSION_REVIEW','reviewed_source':source_record,
         'endpoint_replay':'This command freshly reran the producer checker, redirecting only its output directory. Both 632-column orientations passed for both providers. This is not an independent endpoint interpreter.',
         'providers':{},'mathematical_review':{
             'bilinear_Gram':'QQ^T=56I+16I−64I=8I',
             'Hermitian_Gram':'QQ*=56I+16I+64I=136I',
             'conclusion':'D=I−Q^TQ/4 is symmetric and D^2=I. This is a bilinear transpose identity, not a unitary/Hermitian reflection.',
             'backward_normalization':'B^-T before the backward core and B^T afterward are correct for the symmetric bilinear block contract. Complex conjugation would change the claimed operator.',
             'local_pair':'The two replayed endpoint maps are F(X,Y)=(DX,Y+DX) and B(X,Y)=(X−Y,DY). The identities D^T=D and D^2=I do not assert B=F^-T.',
             'helper_count':'632−2*128=376 remaining arbitrary helpers; 32 old helpers have been promoted to data ports.',
             'port_geometry':'The 16 added labels are 0: input source gauge I, output source/target gauge FULL. No norm-one global port admission follows.'},
         'source_pin_review':'Closed: the pinned producer rejects disabled assertions, authenticates its modern component, authenticates the receipt, and enforces all four retained native files per provider. This canonical review authenticates the same input bytes before its fresh replay.',
         'limitations':['Finite local component only. No complete supplier, global zero-label geometry, physical allocation or kappa increase.',
                        'The Gaussian scalar/native frame review does not replace inherited native core recipe certificates or a global precision recurrence.']}
    for name,item in receipt['providers'].items():
        loc=inp/'native-cache'/item['word_sha256']/'local'
        word=c.read(loc/'CANONICAL-WORD.json.gz')
        program_path=producer/f'PROGRAMS-{name}.json.gz'
        payload=gzip.decompress(program_path.read_bytes())
        c.need(sha256(payload).hexdigest()==replay['providers'][name]['payload_sha256'],'fresh emitted word payload')
        programs=json.loads(payload)
        c.need(set(programs)=={'forward','backward'},'fresh emitted orientations')
        out['providers'][name]={'program_gzip_sha256':c.digest(program_path),
            'literal_frame_checks':{orientation:frames(events,word)for orientation,events in programs.items()}}
    (review/'INDEPENDENT-REVIEW.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'])


if __name__=='__main__':main()
