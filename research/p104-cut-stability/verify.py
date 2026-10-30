"""Source-bound join of independent all-cut and whole-caller error evidence.

Prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
No independent human/proof-kernel or complete multiplier claim is made.
"""
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:
        raise ValueError(why)

def canonical(value):
    return json.loads(json.dumps(value,sort_keys=True))

def authenticate(raw,expected):
    need(sha256(raw).hexdigest()==expected,'Authentication before mathematical imports')

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def run():
    pins=json.loads((HERE/'RUNTIME-PINS.json').read_text())
    for name,expected in pins.items():
        path=HERE/name
        need(path.is_file() and not path.is_symlink(),'Regular retained input '+name)
        authenticate(path.read_bytes(),expected)
    for name in ['inputs/WORD.json.gz','inputs/source_local.py']:
        try:
            authenticate((HERE/name).read_bytes()+b'\n',pins[name])
        except ValueError:
            pass
        else:
            raise ValueError('Actual source corruption was accepted: '+name)

    core=load('p104_cut_author',HERE/'check.py')
    fresh=core.calculate()
    need(fresh==json.loads((HERE/'RESULT.json').read_text()),'Current all-cut receipt')
    peer=load('p104_cut_fraction_peer',HERE/'peer/verify.py')
    independent,_cpu=peer.calculate()
    need(canonical(independent)==json.loads((HERE/'peer/RESULT.json').read_text()),'Independent all-cut receipt')
    for key in ['prefix_max_row_l1','prefix_max_witness','prefix_max_entry_denominator_exponent',
                'prefix_denominator_witness','suffix_max_row_l1','suffix_max_witness',
                'suffix_max_entry_denominator_exponent','suffix_denominator_witness']:
        need(independent[key]==fresh[key],'Current/independent all-cut binding '+key)
    need(independent['word_sha256']==fresh['word_sha256'],'Exact common source word')

    reviewer=load('p104_cut_witness_peer',HERE/'proof-peer/review.py')
    reviewed=reviewer.run()
    need(canonical(reviewed)==json.loads((HERE/'proof-peer/RESULT.json').read_text()),'Independent selected-row and residual controls')
    need(reviewed['prefix_witness']['row']==fresh['prefix_max_witness']['row'] and
         reviewed['suffix_witness']['row']==fresh['suffix_max_witness']['row'],'Current maximum-row witnesses')
    interval=load('p104_cut_interval_peer',HERE/'range-peer/range.py').run()
    need(canonical(interval)==json.loads((HERE/'range-peer/RESULT.json').read_text()),'Independent range recurrence and exhaustive small control')
    need(interval['E']==fresh['all_interval_majorant']['scalar_amplification_power_of_two'],'Current all-interval exponent')

    source=load('p104_cut_retained_source',HERE/'inputs/source_local.py')
    original=json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()))
    residual=json.loads(gzip.decompress((HERE/'RESIDUAL-WORD.json.gz').read_bytes()))
    before,after=canonical(source.replay(original)),canonical(source.replay(residual))
    need(before==after==json.loads((HERE/'RESIDUAL-SOURCE-REPLAY.json').read_text()),
         'Fresh retained typed replay: ADD-COPY has the same endpoint, paid/helper invoice and scalar tariff')

    whole=load('p104_cut_whole_application',HERE/'whole-caller/check.py')
    application=whole.derive()
    need(canonical(application)==json.loads((HERE/'whole-caller/RESULT.json').read_text()),'Fresh complete caller census and majorants')
    lc=application['local']
    need(lc['all_interval_scalar_power']==fresh['all_interval_majorant']['scalar_amplification_power_of_two'] and
         lc['all_interval_denominator_exponent']==fresh['all_interval_majorant']['scalar_denominator_exponent_upper'],
         'Complete caller consumes this exact interval bound')
    need(canonical(lc['paid_profile'])==after['paid'] and canonical(lc['helper_targets'])==after['helpers'],
         'Complete caller preserves every paid and productive local target')
    need(application['input_sha256']['WORD.json.gz']==fresh['word_sha256'],
         'Complete caller and current exact word agree')
    return {'status':'PASS_P104_CUT_STABILITY_AND_CALLER_BOUNDS',
            'cuts_checked_in_each_direction':fresh['cuts'],
            'prefix_max_row_l1':fresh['prefix_max_row_l1'],
            'suffix_max_row_l1':fresh['suffix_max_row_l1'],
            'all_interval_scalar_bound':'2^'+str(interval['E']),
            'complete_caller_coordinate_bound':'2^(5844+ceil((265*f+1)/2))',
            'new_Gaussian_calls':fresh['residual_word']['new_Gaussian_calls'],
            'scalar_tariff_change':fresh['residual_word']['ordinary_scalar_tariff_change'],
            'new_kappa':False,'scientific_adoption':False,'selected_promotion':False,
            'scope':'Finite exact-word/caller error and range specialization; native/recursive implementation, tape, compiler and analytic framework premises remain.'}

if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True))
