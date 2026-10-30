#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Local-only demonstration for finding 1 (not run by verify.py or CI; it executes PR #3633 code as the object under
study).  Runs PR3633's owners/independent_literal.py unmodified, then copies in which one gate (and finally all five
gates) named by the five reject() controls is replaced by need(True, ...).  The only other change in a copy is its
ARTIFACTS.json self-pin.  Records whether each copy still reports PASS and still lists its five controls.

Usage: python3 tools/gate_disable_demo.py OWNERS_DIR LITERAL_DIR NATIVE_DIR PYTHON REPO WORK_DIR > DEMO.json
  OWNERS_DIR   PR3633 research/staged-width-t488/owners (e.g. from `git archive` of head 72c268f1)
  LITERAL_DIR  output of PR3633 owners/portable_expand.py (FILL.json.gz, ORDER.json, DISPATCH.json, PROFILE.json)
  NATIVE_DIR   checked-base/ and checked-extra/CANONICAL-WORD.json.gz whose sha256 equal PR3633 SOURCE-PINS
  PYTHON       an interpreter with numpy (PR3633's auditor imports it)
  REPO         a checkout of main (OWNER_SOURCE_REPO)
  WORK_DIR     a new directory for the copies
"""
import json
import os
import re
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

GATES = {'helper_identity': 'complete literal ordered helper identities',
         'window': 'strict/closed actual source windows',
         'family': 'same-call physical family uniqueness',
         'prefix': 'every chronological pending mask is a compact prefix',
         'histogram': 'independent complete histogram'}


def variant(src, work, name, disabled, env, python):
    d = work / ('run-' + name)
    shutil.copytree(src, d)
    text = (d / 'independent_literal.py').read_text()
    for g in disabled:
        msg = GATES[g]
        hits = list(re.finditer(r"need\((?:(?!need\().)*?,'" + re.escape(msg) + r"'\)", text, re.S))
        if len(hits) != 1:
            raise SystemExit('gate %r found %d times' % (g, len(hits)))
        text = text[:hits[0].start()] + "need(True,'" + msg + "')" + text[hits[0].end():]
    (d / 'independent_literal.py').write_text(text)
    art = json.loads((d / 'ARTIFACTS.json').read_text())
    art['independent_literal.py'] = sha256((d / 'independent_literal.py').read_bytes()).hexdigest()
    (d / 'ARTIFACTS.json').write_text(json.dumps(art, indent=2) + '\n')
    out = d / 'AUDIT.json'
    r = subprocess.run([python, '-B', str(d / 'independent_literal.py')], env=dict(env, OWNER_AUDIT_OUTPUT=str(out)),
                       capture_output=True, text=True)
    rec = dict(variant=name, disabled=disabled, exit=r.returncode)
    if r.returncode == 0:
        res = json.loads(out.read_text())
        rec.update(status=res['status'], controls=res['controls'])
    else:
        rec['stderr_tail'] = r.stderr[-300:]
    return rec


def main(owners, literal, native, python, repo, work):
    work = Path(work)
    work.mkdir()
    env = dict((k, v) for k, v in os.environ.items() if not k.startswith('GIT_'))
    env.update(OWNER_SOURCE_REPO=str(Path(repo).resolve()), OWNER_LITERAL_DIR=str(Path(literal).resolve()),
               OWNER_NATIVE_DIR=str(Path(native).resolve()))
    src = Path(owners).resolve()
    recs = [variant(src, work, 'original', [], env, python)]
    recs += [variant(src, work, 'no-' + g, [g], env, python) for g in GATES]
    recs.append(variant(src, work, 'no-gates', list(GATES), env, python))
    print(json.dumps(recs, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:7])
