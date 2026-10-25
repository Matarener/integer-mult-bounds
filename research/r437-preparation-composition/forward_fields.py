"""Package-local monotone field validator for Callback admission only.

Not a replacement for arbitrary Fields.read/check_code. Its caller must issue
one next() for each chronological history step, then the current field unless
leaf=True, followed by finish(). The unchanged encoded Callback loop does this.
"""
import ast
from hashlib import sha256

def adapted_callback(base, records):
    class ForwardFields:
        def __init__(self, fields):
            self.fields=fields
            fields.tape.rewind()
        def next(self, code):
            tape=self.fields.tape
            observed=records.read_finite(tape,self.fields.code_bits)
            records.need(observed==code,'original global raw-field code')
            while tape.read()!=records.RECORD_END:
                records.need(tape.read()!=records.BLANK,'record exists at global slot')
                tape.step(1)
            tape.step(1)
        def finish(self):
            tape=self.fields.tape
            complete=tape.read()==records.BLANK
            tape.rewind()
            records.need(complete,'exact frozen/current field prefix')
    class ForwardCallback(base): pass
    return ForwardCallback,ForwardFields

def install(base,records,path,namespace):
    tree=ast.parse(path.read_text())
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Callback')
    method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_validate_program')
    records.need(sha256(ast.dump(method).encode()).hexdigest()=='182c3b095d95d7ccf98d6f5e881aa58f0619621fc17b8e77030cdc4c086967b6','exact reviewed admission AST')
    class Rewrite(ast.NodeTransformer):
        def __init__(self):self.checks=self.ends=self.program_seeks=0
        def visit_Expr(self,node):
            if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='seek_record':
                records.need(ast.unparse(node.value)=='seek_record(self.program.tape, after)','exact terminal program seek')
                self.program_seeks+=1
                return ast.Pass()
            return self.generic_visit(node)
        def visit_Call(self,node):
            if isinstance(node.func,ast.Attribute) and ast.dump(node.func.value)==ast.dump(ast.parse('self.fields',mode='eval').body):
                if node.func.attr=='check_code':
                    records.need(len(node.args)==2 and not node.keywords,'exact check_code shape')
                    self.checks+=1
                    return ast.Call(ast.Attribute(ast.Name('cursor',ast.Load()),'next',ast.Load()),[node.args[1]],[])
                if node.func.attr=='end':
                    records.need(len(node.args)==1 and not node.keywords,'exact end shape')
                    self.ends+=1
                    return ast.Call(ast.Attribute(ast.Name('cursor',ast.Load()),'finish',ast.Load()),[],[])
                raise ValueError('unreviewed field use in admission')
            return self.generic_visit(node)
    edit=Rewrite();method=edit.visit(method)
    records.need((edit.checks,edit.ends,edit.program_seeks)==(2,2,1),'exact monotone admission sites')
    method.body.insert(0,ast.parse('cursor = ForwardFields(self.fields)').body[0])
    cls,cursor=adapted_callback(base,records)
    env=dict(namespace,ForwardFields=cursor)
    exec(compile(ast.fix_missing_locations(ast.Module([method],type_ignores=[])),str(path),'exec'),env)
    forward_program=program_cursor(records,path.with_name('records.py'))
    admitted=env['_validate_program']
    def validate(self):
        original=self.program
        self.program=forward_program(original)
        try:admitted(self)
        finally:self.program=original
    cls._validate_program=validate
    return cls


def program_cursor(records,path):
    tree=ast.parse(path.read_text())
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Program')
    methods=[]
    for name in ('root','step'):
        method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name==name)
        records.need(sha256(ast.dump(method).encode()).hexdigest()==PROGRAM_AST[name],'exact reviewed Program AST')
        records.need(ast.unparse(method.body[-2])=='self.tape.rewind()','terminal Program rewind')
        method.body[-2]=ast.parse('self.tape.step(1)').body[0]
        if name=='step':
            records.need(ast.unparse(method.body[1])=='seek_record(self.tape, level)','initial Program seek')
            method.body.pop(1)
        methods.append(method)
    env=dict(vars(records))
    exec(compile(ast.fix_missing_locations(ast.Module(methods,type_ignores=[])),str(path),'exec'),env)
    class ForwardProgram:
        def __init__(self,program):
            self.tape=program.tape
            self.code_bits=program.code_bits
            self.index_arena=program.index_arena
            self.residue_arena=program.residue_arena
    ForwardProgram.root=env['root'];ForwardProgram.step=env['step']
    return ForwardProgram

PROGRAM_AST={'root': 'f1ce38c0bab29ef74f2f0d60373d08cfae69cbbd6b1539914d10ea4001909c02', 'step': 'a1358d976440865d1dff2c410874b89426949c3123350dd132e8eb9a7867af39'}
