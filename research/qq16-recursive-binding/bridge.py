"""Finite-state stream lift/projection around a separately closed C backend.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
The injected Tape/markers are the authenticated physical controller's actual API.
The execution loops use only tape symbols, unit moves and finite-state flags.
An immutable unary pattern is built once from paid unary width/reserve descriptors.
No payload is decoded into a Python integer by this adapter.
"""
LOW,COPY,HIGH=5,6,7

def need(ok,why):
 if not ok:raise ValueError(why)

class Bridge:
 def __init__(self,Tape,blank,left):
  need(not {LOW,COPY,HIGH}&{blank,left,0,1},'disjoint pattern and payload markers')
  self.blank,self.left=blank,left
  self.pattern,self.output=Tape(),Tape()
  self.counts={'read':0,'write':0,'move':0}
  self.ready=False;self.returned=False
 def read(self,t):
  self.counts['read']+=1;return t.read()
 def write(self,t,v):
  self.counts['write']+=1;t.write(v)
 def step(self,t,d):
  need(d in (-1,1),'unit move');self.counts['move']+=1;t.step(d)
 def append(self,t,v):self.write(t,v);self.step(t,1)
 def home(self,t):
  while self.read(t)!=self.left:self.step(t,-1)
  self.step(t,1)
 def erase(self,t):
  self.home(t)
  while self.read(t)!=self.blank:
   self.write(t,self.blank);self.step(t,1)
  self.home(t)
 def _unary(self,t,symbol):
  self.home(t)
  while self.read(t)!=self.blank:
   need(self.read(t)==1,'unary descriptor bit');self.append(self.pattern,symbol);self.step(t,1)
  self.home(t)
 def _prepare(self,coarse_width,reserve,high_padding=None):
  need(not self.ready and not self.returned,'closed pattern setup')
  need(len({id(t) for t in (coarse_width,reserve,self.pattern,self.output)})==4,'distinct setup ports')
  self.home(coarse_width);need(self.read(coarse_width)==1,'nonempty component width')
  if high_padding is not None:
   need(high_padding not in (coarse_width,reserve,self.pattern,self.output),'distinct high-padding descriptor')
   self.home(high_padding);self.home(reserve)
   need(self.read(high_padding)==1,'Gaussian-modulus extra sign bit');self.step(high_padding,1)
   while self.read(reserve)!=self.blank:
    need(self.read(reserve)==1 and self.read(high_padding)==1,'enough inherited high headroom')
    self.step(reserve,1);self.step(high_padding,1)
   while self.read(high_padding)!=self.blank:
    need(self.read(high_padding)==1,'unary high descriptor');self.step(high_padding,1)
   self.home(reserve);self.home(high_padding)
  self._unary(reserve,LOW);self._unary(coarse_width,COPY)
  if high_padding is None:
   self._unary(reserve,HIGH);self.append(self.pattern,HIGH)
  else:self._unary(high_padding,HIGH)
  self.home(self.pattern);self.ready=True
 def prepare(self,coarse_width,reserve,high_padding=None):
  need(not self.ready and not self.returned,'closed pattern setup')
  ports=[coarse_width,reserve]+([] if high_padding is None else [high_padding])
  need(len({id(t) for t in ports+[self.pattern,self.output]})==len(ports)+2,'distinct borrowed setup ports')
  try:self._prepare(coarse_width,reserve,high_padding)
  except BaseException:
   for t in ports:self.home(t)
   self.erase(self.pattern);self.ready=False;raise
 def _run(self,source,project):
  need(self.ready and not self.returned,'consume preceding protected bridge output')
  need(source not in (self.pattern,self.output),'separate borrowed source')
  self.home(source);self.home(self.pattern);need(self.read(self.output)==self.blank,'blank bridge output')
  parity=False
  try:
   while self.read(source)!=self.blank:
    sign=None
    while self.read(self.pattern)!=self.blank:
     op=self.read(self.pattern)
     if project:
      bit=self.read(source);need(bit in (0,1),'complete wide component');self.step(source,1)
      if op==LOW:need(bit==0,'nonzero discarded fractional bit')
      elif op==COPY:self.append(self.output,bit);sign=bit
      else:need(op==HIGH and sign is not None and bit==sign,'incompatible return sign extension')
     else:
      if op==LOW:self.append(self.output,0)
      elif op==COPY:
       bit=self.read(source);need(bit in (0,1),'complete coarse component');self.step(source,1)
       self.append(self.output,bit);sign=bit
      else:need(op==HIGH and sign is not None,'valid immutable pattern');self.append(self.output,sign)
     self.step(self.pattern,1)
    self.home(self.pattern);parity=not parity
   need(not parity,'complete Gaussian real/imaginary pair')
   self.home(source);self.home(self.output);self.returned=True;return self.output
  except BaseException:
   self.home(source);self.home(self.pattern);self.erase(self.output);raise
 def promote(self,source):return self._run(source,False)
 def project(self,source):return self._run(source,True)
 def consume(self):
  need(self.returned,'protected output exists');self.erase(self.output);self.returned=False
 def close(self):
  need(not self.returned,'consume before closing');self.erase(self.pattern);self.ready=False
 def cost(self):return dict(self.counts)

def unary_from_count(count,Tape,Counter):
 """Paid encoded-binary to unary setup via the actual amortized ripple counter.

 Setup descriptors are borrowed; the returned unary tape is owned and must be
 erased after the immutable conversion pattern is prepared. Counter work and
 output tape meters supply its complete cell invoice in the fixtures.
 """
 out=Tape();remaining=Counter(count)
 while not remaining.finished:
  out.append(1);remaining.decrement()
 remaining.close();out.rewind()
 return out,remaining.tape.meter.record()
