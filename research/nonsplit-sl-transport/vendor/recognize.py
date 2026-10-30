"""Recover residue-field products. Ali Romman with OpenAI Codex. Apache-2.0."""
from itertools import product
from vendor import local as a
from vendor.split import span, coordinate_map, linear_combination


def radical(table, unit, f):
    n = len(table)
    power = 1
    while power < n:
        power *= f.q
    return a.kernel(a.columns([a.algebra_power(table, v, power, unit, f)
                               for v in a.identity(n)], n), n, f)


def fixed_space(table, unit, power, f):
    n = len(table)
    cols = [a.algebra_power(table, v, power, unit, f) for v in a.identity(n)]
    return a.kernel([[f.add[cols[j][i]][f.neg[int(i == j)]]
                      for j in range(n)] for i in range(n)], n, f)


def primitive_parts(table, unit, f):
    fixed = fixed_space(table, unit, f.q, f)
    parts = [unit]
    for c in fixed:
        refined = []
        for e in parts:
            for scalar in range(f.q):
                shifted = [f.add[x][f.neg[f.mul[scalar][y]]] for x,y in zip(c,unit)]
                power = a.algebra_power(table, shifted, f.q-1, unit, f)
                selector = [f.add[x][f.neg[y]] for x,y in zip(unit,power)]
                piece = a.tensor_value(table,e,selector,f)
                if any(piece):
                    refined.append(piece)
        parts = refined
        if len(parts) == len(fixed):
            break
    if len(parts) != len(fixed):
        raise ArithmeticError('primitive decomposition')
    return parts


def regular_generator(module, jbasis, parts, degrees, f):
    n = len(module)
    seed = [0]*n
    actions = [linear_combination(c,module,f) for c in jbasis]
    for e,d in zip(parts,degrees):
        projection = linear_combination(e,module,f)
        block = span([a.column(projection,i) for i in range(n)],n,f)
        jm = span([a.mv(m,v,f) for m in actions for v in block],n,f)
        if len(block)-len(jm) != d:
            return None
        v = next(v for v in block if a.rank(jm+[v],f)>len(jm))
        seed = [f.add[x][y] for x,y in zip(seed,v)]
    matrix = a.columns([a.mv(m,seed,f) for m in module],n)
    if not a.determinant(matrix,f):
        raise ArithmeticError('regular generator')
    return matrix,seed


def local_model(component,f):
    field,hs = component['field'],component['heights']
    d = len(field)
    bounds = [f.p**h for h in hs]
    exponents = list(product(*(range(b) for b in bounds)))
    positions = {e:i for i,e in enumerate(exponents)}
    n = d*len(exponents)
    table = [[[0]*n for _ in range(n)] for _ in range(n)]
    for i,x in enumerate(exponents):
        for j,y in enumerate(exponents):
            z = tuple(v+w for v,w in zip(x,y))
            if any(v>=b for v,b in zip(z,bounds)):
                continue
            start = d*positions[z]
            for u,v in product(range(d),repeat=2):
                table[d*i+u][d*j+v][start:start+d] = field[u][v]
    return table,exponents


def product_model(components,f):
    models = [local_model(c,f)[0] for c in components]
    n = sum(map(len,models))
    table = [[[0]*n for _ in range(n)] for _ in range(n)]
    offset = 0
    for mu in models:
        for i,row in enumerate(mu):
            for j,v in enumerate(row):
                table[offset+i][offset+j][offset:offset+len(mu)] = v
        offset += len(mu)
    return table


def field_table_valid(table,f):
    try:
        a.validate_tensor(table,f)
        d = len(table)
        identity = a.identity(d)
        if any(table[0][i]!=identity[i] or table[i][0]!=identity[i] for i in range(d)):
            return False
        if any(table[i][j]!=table[j][i] for i,j in product(range(d),repeat=2)):
            return False
        for i,j,k in product(range(d),repeat=3):
            if a.tensor_value(table,table[i][j],identity[k],f) != a.tensor_value(table,identity[i],table[j][k],f):
                return False
        if radical(table,identity[0],f):
            return False
        return len(fixed_space(table,identity[0],f.q,f)) == 1
    except (ValueError,TypeError,IndexError):
        return False


def classify_local(table,unit,f):
    n = len(table)
    jbasis = radical(table,unit,f)
    degree = n-len(jbasis)
    candidates = fixed_space(table,unit,f.q**degree,f)
    coefficients = [unit]
    for v in candidates:
        if a.rank(coefficients+[v],f)>len(coefficients):
            coefficients.append(v)
    if len(coefficients)!=degree:
        raise ArithmeticError('coefficient field dimension')
    coord = coordinate_map(coefficients,n,f)
    field = [[coord(a.tensor_value(table,x,y,f)) for y in coefficients] for x in coefficients]
    if not field_table_valid(field,f):
        raise ArithmeticError('coefficient field certificate')
    tangent = span([a.tensor_value(table,x,y,f) for x in jbasis for y in jbasis],n,f)
    generators,heights = [],[]
    power,h = 1,0
    while power<n:
        power *= f.p
        h += 1
        for v in a.semilinear_kernel(table,unit,h,f):
            block = [a.tensor_value(table,c,v,f) for c in coefficients]
            enlarged = span(tangent+block,n,f)
            if len(enlarged)>len(tangent):
                if len(enlarged)-len(tangent)!=degree:
                    raise ArithmeticError('coefficient-field tangent dimension')
                tangent = enlarged
                generators.append(v)
                heights.append(h)
    if degree*f.p**sum(heights)!=n:
        return None,'height dimension'
    component = dict(degree=degree,heights=heights,field=field)
    _,exponents = local_model(component,f)
    images = []
    for es in exponents:
        monomial = unit[:]
        for g,e in zip(generators,es):
            monomial = a.tensor_value(table,monomial,a.algebra_power(table,g,e,unit,f),f)
        images.extend(a.tensor_value(table,c,monomial,f) for c in coefficients)
    change = a.columns(images,n)
    if not a.determinant(change,f):
        raise ArithmeticError('local model basis')
    return (component,change),None


def check_certificate(t,cert,f):
    try:
        a.validate_tensor(t,f)
        n = len(t)
        cs = cert['components']
        if not cs:
            return False
        for c in cs:
            hs = c['heights']
            if type(c['degree']) is not int or c['degree']<1 or c['degree']!=len(c['field']):
                return False
            if hs!=sorted(hs) or any(type(h) is not int or h<1 for h in hs):
                return False
            if not field_table_valid(c['field'],f):
                return False
        if sum(c['degree']*f.p**sum(c['heights']) for c in cs)!=n:
            return False
        mats = [cert[k] for k in ('U','V','W')]
        if any(len(m)!=n or any(len(row)!=n or any(type(x) is not int or not 0<=x<f.q for x in row)
                                for row in m) for m in mats):
            return False
        if any(not a.determinant(m,f) for m in mats):
            return False
        u,v,w = mats
        mu = product_model(cs,f)
        for i,j in product(range(n),repeat=2):
            if a.tensor_value(t,a.column(u,i),a.column(v,j),f)!=a.mv(w,mu[i][j],f):
                return False
        return True
    except (KeyError,ValueError,TypeError,IndexError):
        return False


def recognize(t,f):
    """Return explicit residue-field models and all three tensor factor maps."""
    a.validate_tensor(t,f)
    n = len(t)
    equations = []
    for i,j,k in product(range(n),repeat=3):
        row = [0]*(2*n*n)
        for z in range(n):
            row[z*n+i] = f.add[row[z*n+i]][t[z][j][k]]
            row[n*n+k*n+z] = f.add[row[n*n+k*n+z]][f.neg[t[i][j][z]]]
        equations.append(row)
    basis = a.kernel(equations,2*n*n,f)
    if len(basis)!=n:
        return None,'nucleus dimension'
    xb = [[b[i*n:(i+1)*n] for i in range(n)] for b in basis]
    yb = [[b[n*n+i*n:n*n+(i+1)*n] for i in range(n)] for b in basis]
    if any(a.rank([b[s:s+n*n] for b in basis],f)!=n for s in (0,n*n)):
        return None,'nucleus projection'
    if any(a.mm(x,y,f)!=a.mm(y,x,f) for x in yb for y in yb):
        return None,'noncommutative nucleus'
    if a.rank([[t[i][j][k] for j in range(n)] for i in range(n) for k in range(n)],f)!=n:
        return None,'right kernel'
    coord = coordinate_map([sum(m,[]) for m in yb],n*n,f)
    table = [[coord(sum(a.mm(x,y,f),[])) for y in yb] for x in yb]
    unit = coord(sum(a.identity(n),[]))
    jbasis = radical(table,unit,f)
    parts = primitive_parts(table,unit,f)
    blocks = [span([a.tensor_value(table,e,v,f) for v in a.identity(n)],n,f) for e in parts]
    degrees = [len(block)-len(span([a.tensor_value(table,e,j,f) for j in jbasis],n,f))
               for e,block in zip(parts,blocks)]
    ux,wy = (regular_generator(module,jbasis,parts,degrees,f) for module in (xb,yb))
    if ux is None or wy is None:
        return None,'nonregular nucleus module'
    u,u0 = ux
    w,_ = wy
    phi = a.columns([a.tensor_value(t,u0,e,f) for e in a.identity(n)],n)
    v = a.mm(a.inverse(phi,f),w,f)
    factors = []
    for e,block in zip(parts,blocks):
        coords = coordinate_map(block,n,f)
        local = [[coords(a.tensor_value(table,x,y,f)) for y in block] for x in block]
        result,why = classify_local(local,coords(e),f)
        if result is None:
            return None,'local factor: '+why
        component,change = result
        factors.append((component,a.mm(a.columns(block,n),change,f)))
    factors.sort(key=lambda item:(item[0]['degree'],item[0]['heights']))
    change = a.columns([a.column(m,j) for _,m in factors for j in range(len(m[0]))],n)
    cert = dict(components=[c for c,_ in factors],U=a.mm(u,change,f),V=a.mm(v,change,f),W=a.mm(w,change,f))
    if not check_certificate(t,cert,f):
        raise ArithmeticError('residue-product certificate')
    return cert,None
