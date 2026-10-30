# SPDX-License-Identifier: Apache-2.0
from fractions import Fraction as F
from pathlib import Path
import ast
from cache import need

def source_fixture():
    tree=ast.parse((Path(__file__).parent/'inputs/gaussian_check_setup.py').read_text(encoding='utf-8'))
    def number(node):
        if isinstance(node,ast.Constant) and type(node.value) is int:return F(node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -number(node.operand)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='Fraction' and not node.keywords:
            args=[number(a) for a in node.args];need(1<=len(args)<=2,'Fraction literal')
            return args[0] if len(args)==1 else args[0]/args[1]
        raise ValueError('unsupported fixture expression')
    found=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='source' for x in node.targets):
            value=node.value
            if isinstance(value,ast.List) and len(value.elts)==3 and all(isinstance(x,ast.List) and len(x.elts)==3 for x in value.elts):
                found.append([[number(x) for x in row.elts] for row in value.elts])
    need(len(found)==1,'one exact upstream setup fixture');return found[0]

def cyclic_fixture(size=13):
    need(size>=3,'synthetic cyclic dimension')
    D=[F(2)**(i%4-1) for i in range(size)]
    G=[[F(i==j)+(F(1,32) if (i-j)%size in (1,size-1) else 0) for j in range(size)] for i in range(size)]
    H=[[D[i]*G[i][j]/D[j] for j in range(size)] for i in range(size)]
    return H,D
