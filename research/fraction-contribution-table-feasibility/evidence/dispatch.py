import guard,sys
label=sys.argv[1] if sys.argv[1:] else 'primitive-profile'
script='../feasibility/finite.py' if label.startswith('finite') else '../feasibility/actual_audit.py' if label.startswith('actual-table-audit') else 'primitive_profile.py'
with (guard.HERE/'execution.lock').open('a') as lock:
 guard.fcntl.flock(lock,guard.fcntl.LOCK_EX|guard.fcntl.LOCK_NB)
 guard.run(label,script,optimized=label.endswith('-O'))
