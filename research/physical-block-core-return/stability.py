"""Independent rational seven-stage oracle and explicit norm/headroom ledger."""
from fractions import Fraction as Q


def trunc(x, P): return Q(int(x * (1 << P)), 1 << P)


def interior(factors, vector, P):
    stages = []
    def diagonal(values, coefficients): return [trunc(x*c,P) for x,c in zip(values,coefficients)]
    def lower(values): return [trunc(sum((factors['h'][i-j]*values[j] for j in range(i+1)),Q()),P) for i in range(len(values))]
    value = diagonal(vector, factors['inva']); stages.append(value)
    value = diagonal(value, factors['invf']); stages.append(value)
    value = lower(value); stages.append(value)
    value = diagonal(value, factors['f']); stages.append(value)
    value = list(reversed(lower(list(reversed(value))))); stages.append(value)
    value = diagonal(value, factors['invf']); stages.append(value)
    value = diagonal(value, factors['weights']); stages.append(value)
    return value, stages


def ledger(factors, input_bound, boundary_bound, coupling_norm, delta, p, P, width):
    mu = [max(map(abs,factors[name])) if name != 'h' else sum(map(abs,factors[name]))
          for name in ('inva','invf','h','f','h','invf','weights')]
    eta = Q(1,1<<P)
    magnitude = input_bound + coupling_norm*boundary_bound
    error = coupling_norm*delta + 2*eta
    magnitudes, errors = [magnitude], [error]
    for a in mu:
        magnitude *= a; error = a*error + 2*eta
        magnitudes.append(magnitude); errors.append(error)
    peak = max(boundary_bound,*magnitudes)
    j = (32*p-1).bit_length()
    headroom = Q(1 << (width-1), 1<<P)
    # Both normalized components <=1/2 suffices for the final disk test.
    disk_sufficient = max(boundary_bound,magnitudes[-1]) <= (1 << (j-1))
    return dict(mu=mu,magnitudes=magnitudes,paired_errors=errors,peak=peak,
                headroom=headroom,width_ok=peak<headroom,disk_ok=disk_sufficient,
                output_difference=Q(1,1<<j)*max(delta,errors[-1])+Q(2,1<<p))


def finish(detail, boundary_columns, P):
    result, stages = [], []
    matrix=detail['matrix']; inside=detail['inside']; boundary=detail['boundary']
    p=detail['p']; j=(32*p-1).bit_length()
    for component in (0,1):
        source=[detail['target'][k][component] for k in detail['selection']]
        xb=boundary_columns[component]
        rhs=[trunc(source[i]-sum((trunc(matrix[i][b],P)*xb[k] for k,b in enumerate(boundary)),Q()),P)
             for i in inside]
        xi,trace=interior(detail['factors'],rhs,P)
        merged=[Q() for _ in source]
        for locations,values in ((boundary,xb),(inside,xi)):
            for k,v in zip(locations,values):merged[k]=v
        result.append([trunc(v*detail['normal']/ (1<<j),p) for v in merged[:detail['core_length']]])
        stages.append(trace)
    return [x for pair in zip(*result) for x in pair],stages
