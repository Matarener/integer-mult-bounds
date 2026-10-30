"""Process-scoped APFS clone copies; identical byte semantics, less disk.
Only regular-file shutil copies are optimized; fallback is the stdlib copy.
No research checks or subprocess arguments are modified.
"""
import ctypes,errno,os,shutil,stat
_original=shutil.copyfile
_lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True)
_clone=_lib.clonefile;_clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int];_clone.restype=ctypes.c_int
def copyfile(src,dst,*,follow_symlinks=True):
 if follow_symlinks and os.path.isfile(src) and not os.path.lexists(dst):
  if _clone(os.fsencode(src),os.fsencode(dst),0)==0:return dst
 return _original(src,dst,follow_symlinks=follow_symlinks)
shutil.copyfile=copyfile
