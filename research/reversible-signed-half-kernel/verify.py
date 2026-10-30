"""Source-bound tape lowering; exact finite checks of the written all-width proof."""
from hashlib import sha256
from pathlib import Path
from collections import Counter
import gzip
import json
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def calculate():
    for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            need(sha256((ROOT/pin['path']).read_bytes()).hexdigest() == pin['sha256'],
                 'source bytes: '+pin['path'])
    p = json.loads((HERE/'PREDECESSOR.json').read_text())
    need(sha256((HERE/p['retained_path']).read_bytes()).hexdigest() == p['sha256'],
         'retained predecessor statement')
    w = json.loads(gzip.decompress((ROOT/'research/p104-helper-subspace-splits/WORD.json.gz').read_bytes()))
    pre = w['program'][:next(i for i,e in enumerate(w['program']) if e[0] == 'MOVE')]
    halves = [(i,e[1],e[-2]) for i,e in enumerate(pre) if e[0] == 'SCALE' and e[-2] in ('1/2','-1/2')]
    need(len(pre) == 9589 and Counter(e[2] for e in halves) == {'1/2':18,'-1/2':66},
         'actual PR6066 source sites')
    k = types.ModuleType('signed_half_source')
    exec(compile((HERE/'kernel.py').read_bytes(),str(HERE/'kernel.py'),'exec'),k.__dict__)
    exhaustive = tape_cases = large = 0
    invoices = []
    for width in list(range(2,9))+[16,32,64,128]:
        for sign in (-1,1):
            gates = k.compile_gates(width,sign)
            code = k.compile_tape(gates)
            counts = dict(Counter(g[0] for g in gates))
            d = 2*width+1
            length_bound = counts['X']*(2*d+1)+counts['C']*(4*d+3)+counts['T']*(6*d+5)
            need(len(code) <= length_bound, 'explicit quadratic tape bound')
            inputs = (range(-(1 << (width-1)),1 << (width-1)) if width <= 8 else
                      [-(1 << (width-1)),-(1 << (width-1))+1,-1,0,1,(1 << (width-1))-1])
            for x in inputs:
                for u in (0,1):
                    initial = k.encode(x,width,u)
                    output = k.execute_gates(initial,gates)
                    y,r = k.expected(x,sign,u)
                    need(k.decode(output,width) == y and output[width] == r and
                         output[width+1] == u and not any(output[width+2:]), 'signed exact gate endpoint')
                    need(k.execute_gates(output,gates,inverse=True) == initial,
                         'all initial dirty bits and residue cleanup')
                    if width <= 8: exhaustive += 1
                    else: large += 1
                    if width <= 5 or x in (-(1 << (width-1)),(1 << (width-1))-1,0):
                        actual,bill = k.execute_tape(initial,code)
                        need(actual == output and width+1 not in bill['written_cells'],
                             'literal fixed-tape result and read-only coin')
                        back,inverse_bill = k.execute_tape(actual,code,inverse=True)
                        need(back == initial and inverse_bill['steps'] == bill['steps'],
                             'literal inverse and returned tape heads')
                        tape_cases += 1
            invoices.append(dict(width=width,sign=sign,gates=counts,program_symbols=len(code),
                                 kernel_steps=2*len(code)+2,program_cells=len(code)+2,data_cells=2*width+2,
                                 clean_work_bits=width,retained_parity_bits=1,
                                 finite_control_accumulator_bits=2,fixed_interpreter_modes_at_most=8,
                                 program_sha256=sha256(code.encode()).hexdigest()))
    # Two-to-one is an exact obstruction to a zero-residue isolated map.
    need(k.expected(0,1,1)[0] == k.expected(1,1,1)[0], 'one retained bit necessary')
    # Omitting the final sign for negative halves is a real wrong circuit.
    gates = k.compile_gates(4,1)
    output = k.execute_gates(k.encode(3,4,0),gates)
    need(k.decode(output,4) != k.expected(3,-1,0)[0], 'wrong signed kernel rejected')
    try:
        k.compile_gates(1,1)
    except ValueError:
        pass
    else:
        raise ValueError('unsupported one-bit width accepted')
    return dict(status='PASS_REVERSIBLE_SIGNED_HALF_TAPE',exhaustive_signed_gate_cases=exhaustive,
                literal_tape_round_trips=tape_cases,large_guard_cases=large,
                source_half_sites=len(halves),source_first_positive=list(next(e for e in halves if e[2]=='1/2')),
                source_first_negative=list(next(e for e in halves if e[2]=='-1/2')),
                invoices=invoices,
                scope='One local signed-half kernel with resident read-only coin and clean work. Complete caller/random-tape delivery and other scalar macros remain open; no new kappa.')


def main():
    result = calculate()
    need(result == json.loads((HERE/'RESULT.json').read_text()), 'committed complete receipt')
    print(json.dumps(dict(status=result['status'],exhaustive_signed_gate_cases=result['exhaustive_signed_gate_cases'],
                         literal_tape_round_trips=result['literal_tape_round_trips'],
                         large_guard_cases=result['large_guard_cases'],widths=[2,3,4,5,6,7,8,16,32,64,128]),sort_keys=True))


if __name__ == '__main__':
    main()
