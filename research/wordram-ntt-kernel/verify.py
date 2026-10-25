"""Standalone portable replay of the bounded-kernel application."""
import sys,json,hashlib,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    if not __debug__:
        raise SystemExit('Run without Python -O: certificate assertions must be enabled.')
    started=time.perf_counter()
    manifest=json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    actual={x.relative_to(ROOT).as_posix() for x in ROOT.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x!=ROOT/'MANIFEST.json'}
    assert actual==set(manifest['files']), 'package file inventory mismatch'
    for name,expected in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected, 'source drift: '+name
    helper=json.loads((ROOT/'lean/STATUS.json').read_text())
    assert helper['status']=='VERIFIED'
    assert hashlib.sha256((ROOT/'lean/IntegerKernelRecovery20261024.lean').read_bytes()).hexdigest()==helper['sha256']
    assert all(set(row['axioms'])<=set(helper['allowed_axioms']) for row in helper['theorems'])
    subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','ntt','-p','test_*.py'],cwd=ROOT,check=True)
    sys.path.insert(0,str(ROOT/'ram'))
    from ram.verify_wordram import run_checks
    from ram.circuit_sharing import check as verify_circuit
    from verify_integration import verify as integration
    from recovery.fixedpoint_fft import run as recovery
    ram=run_checks(); circuit=verify_circuit(); full=integration()
    expected=json.loads((ROOT/'INTEGRATION-RESULTS.json').read_text())
    assert full==expected, 'whole-program replay differs from retained source-bound result'
    narrow=recovery(512,31,12);wide=recovery(512,40,12)
    assert narrow['status']==wide['status']=='PASS'
    assert narrow['smallest_bits_satisfying_this_bound']==31
    from fractions import Fraction
    assert Fraction(wide['budget']['coefficient_error_upper'])<Fraction(1,1000)
    print(json.dumps({'status':'PASS','source_files':len(manifest['files']),
      'ram_multiply_slice':ram['exhaustive_multiply_inputs'],
      'ram_butterfly_cases':ram['butterfly_input_triples'],
      'whole_program_cases':full['cases'],
      'approximate_backend_cases_each_precision':wide['tested_pairs'],
      'fused_static_instructions_512':full['records'][-1]['fused_static_instructions'],
      'maximal_1024bit_operands':full['records'][-1]['comparisons'][1],
      'seconds':round(time.perf_counter()-started,3),
      'scope':'Portable source-integrity and executable replay; see paper for universal proof. No new kappa or complete Lean machine proof.'},indent=2))

if __name__=='__main__':main()
