"""Private process-scoped Windows text/temp compatibility; scientific predicates unchanged."""
import os,io,builtins
if os.name=='nt':
 original_mkdir=os.mkdir
 def mkdir(path,mode=0o777,*,dir_fd=None):
  if mode==0o700:mode=0o777
  if dir_fd is None:return original_mkdir(path,mode)
  return original_mkdir(path,mode,dir_fd=dir_fd)
 os.mkdir=mkdir
 def adapt(fn):
  def opened(file,mode='r',buffering=-1,encoding=None,errors=None,newline=None,closefd=True,opener=None):
   if 'b' not in mode and any(c in mode for c in 'wax') and newline is None:newline='\n'
   return fn(file,mode,buffering,encoding,errors,newline,closefd,opener)
  return opened
 builtins.open=adapt(builtins.open);io.open=adapt(io.open)
