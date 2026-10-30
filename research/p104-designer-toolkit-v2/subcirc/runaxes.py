"""runaxes.py G [G ...]: run supcol.py on each dual with each architecture axis lifted alone (+ baseline, + all), one at a time; logs out/ax_<G>_<tag>.log"""
import sys, subprocess, os
PY = sys.executable; H = os.path.dirname(os.path.abspath(__file__))
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/words/6030.json.gz'
AX = [('base', []), ('nojunk', ['--nojunk']), ('endlow', ['--endlow']), ('anyb', ['--anybirth']), ('wide', ['--maxextra', '3', '--kA', '4']),
      ('all', ['--endlow', '--anybirth', '--maxextra', '3', '--kA', '4'])]
tags = os.environ.get('AXES')
for G in sys.argv[1:]:
    for tag, fl in AX:
        if tags and tag not in tags.split(','): continue
        log = '%s/out/ax_%s_%s.log' % (H, G, tag)
        with open(log, 'w') as f:
            subprocess.run([PY, '-u', '-B', H + '/supcol.py', W, G, '--junk', 'span', '--enum', '1', '--tmax', '300'] + fl, stdout=f, stderr=subprocess.STDOUT, cwd=H + '/out')
        print(G, tag, open(log).read().count('\n'), flush=True)
