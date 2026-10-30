import guard,sys
if sys.argv[1]=='helper':guard.TIMEOUT=300
script='../feasibility/test_finite.py' if sys.argv[1].startswith('finite') else 'profile_'+sys.argv[1]+'.py'
with (guard.HERE/'execution.lock').open('a') as lock:
 guard.fcntl.flock(lock,guard.fcntl.LOCK_EX|guard.fcntl.LOCK_NB)
 print(guard.run(sys.argv[1],script,optimized=sys.argv[1].endswith('-O')))
