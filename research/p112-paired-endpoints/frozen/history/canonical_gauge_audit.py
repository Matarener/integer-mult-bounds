#!/usr/bin/env python3
"""Bind chosen orthogonal complex phase gauges to the actual pinned compiler.

Canonical frame(U) is not the same literal operator as H diag(i^wt(P_Ux)) H.
This audit emits the exact rank-zero left monomial between them, retaining
global phase, and checks both actual paired residual children at all112 ports.
"""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import paired_endpoint as E

HERE = Path(__file__).resolve().parent
COMPILER = E.ROOT/'research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py'
COMPILER_SHA = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'


def main():
    E.need(E.hash_file(COMPILER) == COMPILER_SHA, 'Actual compiler pin changed')
    spec = importlib.util.spec_from_file_location('pinned_complex_clifford',COMPILER)
    ce = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ce
    spec.loader.exec_module(ce)
    geometry = json.loads((HERE/'ORDER3-GEOMETRY.json').read_text())
    endpoints, gauges, source_controls = [], {}, []
    n = 9

    def chosen(axes):
        op = ce.ident(n)
        for v in axes:
            E.need(v.bit_count() & 1, 'Chosen axis is not a unit vector')
            op = op.then(ce.cgate(n,v,1 if v.bit_count()%4 == 1 else -1))
        return op

    def gauge(axes):
        key = ','.join(map(str,axes))
        if key in gauges:
            return
        canonical = ce.canonical_frame(n,axes)
        phase = chosen(axes)
        delta = canonical.adjoint().then(phase)
        E.need(all(x == 0 for x,z,p in delta.tab[n:]), 'Gauge difference has positive rank')
        compiled, rec = ce.monomial(delta)
        E.need(compiled.tab == delta.tab and compiled.zero_state() == delta.zero_state(),
               'Gauge global phase differs')
        state, den = phase.zero_state()
        actual = E.norm({j:a for j,a in enumerate(state)},den)
        E.need(actual == E.phase_kernel(n,axes), 'Chosen phase definition versus actual cgate')
        gauges[key] = dict(axes=axes,rank=0,left_monomial=rec)

    for j,contract in enumerate(geometry['contracts']):
        p,q,r = contract['P'],contract['Q'],tuple(contract['R'])
        P,Q,U,V = (p,), (q,), (p,)+r, (q,)+r
        for axes in (P,Q,U,V,r):
            gauge(axes)
        # The retained data source uses native C_p with its plus sign.
        # Our chosen P representative requires X_p exactly when wt(p)=3 mod4.
        native = ce.cgate(n,p)
        adapter = native.adjoint().then(chosen(P))
        shift = p if p.bit_count()%4 == 3 else 0
        expected = ce.xgate(n,shift)
        E.need(adapter.tab == expected.tab and adapter.zero_state() == expected.zero_state(),
               'Native C_p plus to orthogonal phase gauge adapter')
        E.need(E.kernels([(p,1)]) == E.norm(dict(enumerate(native.zero_state()[0])),native.zero_state()[1]),
               'Actual native C_p normalization differs from independent Gaussian model')
        source_residual = chosen(P).adjoint().then(chosen(U))
        target_residual = chosen(Q).adjoint().then(chosen(V))
        R = chosen(r)
        E.need(source_residual.tab == target_residual.tab == R.tab,
               'Paired residual tableaus differ')
        E.need(source_residual.zero_state() == target_residual.zero_state() == R.zero_state(),
               'Paired residual scalar phases differ')
        source_child, literal_source = ce.lower_child(source_residual)
        target_child, literal_target = ce.lower_child(target_residual)
        E.need(source_child['rank'] == target_child['rank'] == 7, 'Paired native child rank differs')
        E.need(literal_source.tab == source_residual.tab and literal_source.zero_state() == R.zero_state(),
               'Source rank7 lowering differs')
        E.need(literal_target.tab == target_residual.tab and literal_target.zero_state() == R.zero_state(),
               'Target rank7 lowering differs')
        if shift:
            E.need(native.tab != chosen(P).tab, 'Native sign/gauge defect control missed')
            source_controls.append(j)
        endpoints.append(dict(port=j,P=p,Q=q,R=r,
                              native_plus_to_chosen_P_translation=shift,
                              source_child=source_child,target_child=target_child))
    E.need(len(endpoints) == 112 and source_controls, 'Incomplete native endpoint coverage')
    output = dict(status='PASS_ACTUAL_CANONICAL_GAUGES_AND_PAIRED_RANK7_ENDPOINTS',
                  compiler_path=str(COMPILER),compiler_sha256=COMPILER_SHA,
                  geometry_sha256=E.hash_file(HERE/'ORDER3-GEOMETRY.json'),
                  ports=112,chosen_gauges=len(gauges),gauges=list(gauges.values()),
                  endpoint_records=endpoints,
                  native_plus_sign_omission_controls=source_controls,
                  scope='Exact tableaus plus exact Gaussian zero-state global phase; complete Clifford operator identity. Chosen phase gauges are explicitly related to canonical_frame by paid rank-zero monomial wrappers.',
                  not_supplied=['Complete changed scalar supplier word and its chronology',
                                'Scalar/address wrapper cost and prefix norm invoice',
                                'Chronological physical owner and stock realization',
                                'Inherited all-size Fourier/recursive and outer multiplication transfer'])
    (HERE/'CANONICAL-GAUGES.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:output[k] for k in ('status','ports','chosen_gauges')},sort_keys=True))


if __name__ == '__main__':
    main()
