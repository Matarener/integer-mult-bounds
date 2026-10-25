#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent verification of open PR #3633 (hexapode, head 72c268f1, research/staged-width-t488): the T488
allocation of the staged 644/660 supplier, its claimed attainment of the fixed-inventory packing ceiling, and its
endpoint.  Single entry point.

PR #3633 combines the retained T37 (Ross Richardson, PR #3605), T8 (hexapode, PR #3485/#3494) and T16 (Nick
Petalas, PR #3413, via hexapode's PR #3457/#3465) chronologies, 8 copies of 61 base replicas, with Ross Richardson's
unchanged staged-width supplier words (PR #3605) and claims: 1,791,936 literal owner roles, the complete profile
{1:10826280, 2:3188592, 3:1015650, 4:447984, 5:94794, 8:35136, 48:186782}, physical stock 437,757, an aggregate that
attains the exact fractional packing optimum of the fixed inventory, and kappa = 0.001730096363528623534230 - 1e-46 -
1e-70.  Ross Richardson's PR #3630 independently bounds that fixed inventory below .001730096363528623534231 for every
replica count.

With standard-library code independent of PR3633, PR3630 and PR3605 (their files are read as pinned git data and are
never imported or executed; audit_inherited_controls.py parses copies of PR3605's auditor with the ast module as the
object it studies) this package checks:
  C1 audit_staged_words.py  both staged supplier words through this contributor's word lineage (forward and dual
                            replay through cleanup and the target endpoint, tracker, cleanup re-derivation, private
                            buffers, frame recount): helper widths = PR3633 PROVIDERS.json, and they differ from main's
                            PR3133 providers exactly at helpers 389 and 397 (8 -> 7); the change is localised against
                            the unchanged parent words on main;
  B  audit_owners.py        the complete literal journal (data/FILL-columns.xz, bound to PR3633's pinned payload
                            sha256 by byte-exact re-serialisation): ORDER/DISPATCH rebuilt from the base chronologies
                            and bound to PR3633's literal-file pins, source windows derived two ways from the frozen
                            template, strict/closed windows, the active-local-pair exclusion (per role and as a
                            template lemma), same-call physical-family exclusion, capacities with the word-recounted
                            widths, chronological compact prefixes, the complete invoice over all 983,808 bins, the
                            aggregate's patterns realised exactly, and the physical stock;
  A  audit_ceiling.py       an own fixed-inventory LP (a first draft mirrored PR3633's enumeration/column code and was
                            rewritten after review; see its docstring): all 2,551 patterns, an own exact simplex, a
                            rigorous dual certificate at a_hi, the unique LP-minimum profile, attainment by PR3633's
                            aggregate, the all-T ceiling argument within the fixed model, and cross-checks of
                            PR3633's CEILING.json and PR3630's dual and digest;
  D  audit_endpoint.py      the endpoint of the recounted profile in two rational enclosures, kappa, the exact gains
                            over PR3626, PR3624, PR3630 and PR3605 and their improvement tests; downstream, PR3653
                            (roger-sato's PR3642 retimed words on PR3633's journal): unchanged widths, its endpoint,
                            and the scope-A dual re-certified at that endpoint;
  C2 audit_inherited_controls.py  the five reject() controls of PR3633's owners/independent_literal.py, kept from
                            PR3605's adapted auditor, cannot fail: three predicates are unsatisfiable and two test a
                            +1 perturbation of an equality the preceding gate asserted; the same holds in all 15
                            copies located in main and the heads of PR3605/3624/3626/3630/3633/3638/3642/3653;
     vendor/pr3053/         this contributor's earlier merged checkers, byte copies pinned by git blob id and sha256,
                            loaded by executing exactly the verified bytes.

Inputs are read with `git show <commit>:<path>` from --repo and must match pinned git blob ids and sha256.  --fetch
fetches the eight open PR heads into refs/audit/prN only (audit_common.ensure_commits).  The default run recomputes
everything and requires the result to equal the committed RESULT.json (timings excluded); --out rewrites it.
--mutations first runs an unmutated --fast baseline, then every entry of MUTATIONS in a subprocess, and requires each
to load the mutated module and end with an audit rejection.

Usage: python3 -I -B verify.py [--repo PATH] [--fetch] [--remote URL] [--out] [--fast] [--mutations [--jobs N]]
The final stdout line is PASS_T488_INDEPENDENT_AUDIT ... or `FAIL_T488_INDEPENDENT_AUDIT <type>: <message>` (exit 1).
Sagar Thakrar (thakrarsagar), prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
import types
from fractions import Fraction as Q

PASS_LINE = 'PASS_T488_INDEPENDENT_AUDIT'
FAIL_LINE = 'FAIL_T488_INDEPENDENT_AUDIT'
if not __debug__:
    sys.stdout.write(FAIL_LINE + ' UsageError: refusing to run under python -O\n')
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
REMOTE_DEFAULT = 'https://github.com/CrocSwap/integer-mult-bounds'
RESULT_NAME = 'RESULT.json'

# This contributor's earlier merged code (PR #3053 package research/t74-3015-restore-edit-audit and its vendor/),
# byte copies: (rel path, module name, git blob id, sha256), loaded in this dependency order.
VENDOR = (
    ('vendor/pr3053/audit_common.py', 'audit_common', '17c4064f01b110012b54c05e64bdee8ae498e0b2',
     '7ced740252ac8d8a8c66ef3cc825008e0aacf080494d0e983fb322d7dcddbf42'),
    ('vendor/pr3053/words_check.py', 'words_check', '0b646b9d5583c75a78e0c2dd7e9cfffa02055058',
     'b66414a39f5ac7b9cd32284027e13a550734901aca5f4457085a034689bc3ce6'),
    ('vendor/pr3053/fill_check80.py', 'fill_check80', '557e0732bfe4c030436a11f5433143c10fa07821',
     '1c4d30591969c6502605f239f40505261e99d025aa3b576a804332a6bc479b06'),
    ('vendor/pr3053/check_words.py', 'check_words', '451dbb82f147ef446a1819b1ed595b4bf5547583',
     '5996e804fa006906abff63a982c272588a44c35dfc932fdf687ef98dd3e0905f'),
    ('vendor/pr3053/audit_lib.py', 'audit_lib', 'e8e847cc89dae6bb4e90e2c3dbebc30f615b698f',
     'e0cf84dd959d39e3f299c1e171753c29465fd5b4457561f4ab9ec0675d8e9dc1'),
    ('vendor/pr3053/audit_kappa.py', 'audit_kappa', '6e935547c98188a5fd2ba952641bf474d9323d9b',
     '8dd12fac27ba3ee7decf99a7a1e410e138ec0fc34805bb28b93fa5cc843ab0ee'),
    ('vendor/pr3053/audit_words.py', 'audit_words', '6368333e16c4f50e6eb8b5f2f4c178a2de8cbbb9',
     'ff831ad648dbecfd1c80f63245a84b762fdc70eb9fc3aa94dba23cd364857d18'),
    ('vendor/pr3053/check_accounting.py', 'check_accounting', 'e749057dd838b715d0630de618f32d66a38da931',
     'fb6aef50da586f15cd60762edc074c20e300d65f1378a80160b3d4b840762548'),
)
LOCAL_MODULES = ('audit_staged_words', 'audit_owners', 'audit_ceiling', 'audit_endpoint', 'audit_inherited_controls')
JOURNAL = ('data/FILL-columns.xz', 'f10f95ccf2613988641533a664d15f300a6ccfd67cb3b7d636aa653c34a7e336')

H3633 = '72c268f113368ea0387d188225e3f81ba6d6ef73'   # object under audit (hexapode, T488)
H3630 = 'bcac7fe04b9b7f7f5d3c27d620561f96c4ae5608'   # Ross Richardson, all-T fixed-inventory ceiling
H3605 = '3efbb5de06a49ffeea6684482f2d3fe48cdca3fb'   # Ross Richardson, staged 644/660 supplier (T740)
H3624 = '515a7c4490aa32ac3ca5014feb6f7da0d6952863'   # hexapode, T450
H3626 = '659fd5e7064d9466b668d7188cbb013b333a415a'   # hexapode, T530 (PR3633's stated frontier)
MAIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
H3653 = '607a09ff441c79b215a8127a81f4cc70021d0d9b'   # rohanarun: roger-sato's PR3642 retimed words on PR3633's journal
H3638 = 'd62e1acd7518a231440383f0d0dddf54d6edf8c1'   # zxv, T360 (scope C2 scan only)
H3642 = '044d24f12e74f228dd462c07ae2d7f3ea35e2be9'   # roger-sato, retimed T530 (scope C2 scan only)
COMMITS = {3633: H3633, 3630: H3630, 3605: H3605, 3624: H3624, 3626: H3626, 3653: H3653, 3638: H3638, 3642: H3642}
P53 = 'research/retimed-t488-composition/'
P33 = 'research/staged-width-t488/'
# key: (PR or 0 for main, commit, path, git blob id, sha256)
INPUTS = {
    't488_expected': (3633, H3633, P33 + 'owners/EXPECTED.json', '415eac1a2b0201beac2c3e531c6fcbd1133a819f',
                      '924493b6bbeade055af4916ac7bd6d7d7ec0600719f5c39636dc3f16d7ec14ea'),
    't488_order37': (3633, H3633, P33 + 'owners/ORDER37.json', '411004ab280d6468bdd9c98c01f153baed66c543',
                     '94803d190b2b0506d9645e980b57cdbc3e98221f3b615292df8a94f1b174c984'),
    't488_order_t8': (3633, H3633, P33 + 'owners/T8-ORDER.json', 'b013bdb989f7fde1b8a22ae8ed743eae3a0a62fd',
                      'a1abf78fb3b88bbf4656e6ae26f148a007f744f0be4c00d480fb2424ce8766d6'),
    't488_order_t16': (3633, H3633, P33 + 'owners/T16-ORDER.json', '470b8afb8af03fd053b6ff19bc90eb410b5c9e6b',
                       '9b2106c84aed23a7c3c8b99e21d3e96c66b12f92980a42ab2f6dbbe7831ef7c4'),
    't488_dispatch37': (3633, H3633, P33 + 'owners/DISPATCH37.json', 'c4c016ea3f3cb7bd04c1812259246a9411ad7adc',
                        '4f78935b2ef1f6c08c9c16433d54015def1eccd767443b496a77ea8823690df6'),
    't488_dispatch_t8': (3633, H3633, P33 + 'owners/T8-DISPATCH.json', 'f95b6f07bf4d9e607a7ab8fcc101cdc63a725b07',
                         '23877abbe8ec258eb1f2425137f9171d37b1a4414a25595abe75eb0738850a24'),
    't488_dispatch_t16': (3633, H3633, P33 + 'owners/T16-DISPATCH.json', '40725d2abb328ba7fee1c4f74656eecd982f2f7e',
                          '282960b7163bc305675b64d1d0faee9f71b18848748326418a013626944c6488'),
    't488_candidate': (3633, H3633, P33 + 'owners/CANDIDATE.json', '4293ad4cb76533072610c858d3f44576afe8d777',
                       'fbdda845beac5bba9baa4b1b8c8f596e98f70b59e1d60ebf4f4d3e8758631bfd'),
    'word_base': (3633, H3633, P33 + 'supplier3605/STAGED644-660-base.json.gz',
                  'dc6d321b1e8e2a837a1ff7bb60e8f8f78d043db5',
                  '735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653'),
    'claim3633': (3633, H3633, P33 + 'CLAIM.json', '3e56f9a3035ebe3da02fdf8bc6d71cde4e6c90a0',
                  '3332fb6f6d5ae81da8ead667973491ebefa1803d6d96a06790386ac16243f332'),
    'claim3626': (3626, H3626, 'research/staged-width-t530/CLAIM.json', 'c11ec575770d8aabff9731ce9cc671fc9db448c9',
                  '9f27717c3ddbf5eb7b9773e1b2887ff3899d354019139d916c9b8004aee2e097'),
    'claim3624': (3624, H3624, 'research/staged-width-t450/CLAIM.json', '0d59dc3be440d616dcc24c01d38a6b2439e4b94b',
                  '8f2f80438593e7efaa6bb57c881a40cedbd7b5665b4ae12c6cf215d217c98397'),
    'claim3605': (3605, H3605, 'research/staged-644-660-conditional-release/CLAIM.json',
                  '445e6a83a4cdc6e8630e86f20990b50d1311f81d',
                  '2e721209f626d5111142951b1f26383d6746b4f230a4625244b5e5c84d6079d5'),
    'claim3630': (3630, H3630, 'research/staged-644-660-owner-successor/CLAIM.json',
                  'f82fff358656f8f6fe5d781157f12bc8b1edb62b',
                  'aa4f56010fd4c1e620c742a091932ef3af05cca13886915c1c44f30e9f961aab'),
    'w3653_base': (3653, H3653, P53 + 'local-audit/words/RETIMED644-660-base.json.gz',
                   'd69125e0c7d34af9299e411ada5c30dfc7b95ad1',
                   '6df3356808e29909776be8bc0faf03df983401a267c2d740d1ac2dbcaa278269'),
    'w3653_extra': (3653, H3653, P53 + 'local-audit/words/RETIMED644-660-extra.json.gz',
                    'f3c580b06506e8888fe766c9a1e0bb1a748d7b74',
                    '65624efec36b35934b750c1741ba2ad4e6df3cff86e44536b0c016ebddb0fb55'),
    'outer3653': (3653, H3653, P53 + 'evidence/recorded-admission/outer_claim.json',
                  '6f05d13347e650467b561f1861e6266ffc9ef15c',
                  'c7455323c62a5b1d5c9ceef07a305a5758df6971ac8f88e2be5223eb5f4c7553'),
    'template': (0, MAIN, 'research/rank7-joint-endframes/allocation/vendor/TEMPLATE.json.gz',
                 '114808c32b1799da53524bdc25cea67efb60009e',
                 '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'),
    'plan': (0, MAIN, 'research/rank7-joint-endframes/allocation/vendor/PLAN.json.gz',
             '7a1db55a4d53ee99280be4f3ab7d29f7b2033adf',
             'd566cfb87b71639d4138e1f89b543e2dd6a7772070226a2a14c799a6835bf21e'),
    'pr3133_providers': (0, MAIN, 'research/coupled-carrier-cap740/vendor/PR3133-PROVIDERS.json',
                         '0b2343675099d0a9fe90da6e1f1e53f50235567e',
                         '52eb0d85caa7b2d4a93acdf5011f52b793f61ddca86235fb03cd9a09397ad4cd'),
}

# Checker mutations for --mutations: (module, unique old text, new text).  Each must end in an audit rejection.
MUTATIONS = [
    ('audit_owners', "need(lo < t <= hi, 'owners.window: row", "need(lo <= t <= hi, 'owners.window: row"),
    ('audit_owners', "need(lo < t <= hi, 'owners.window: row", "need(lo < t < hi, 'owners.window: row"),
    ('audit_owners', "need(f not in seen, 'owners.family", "need(True or f not in seen, 'owners.family"),
    ('audit_owners', "need(z == u, 'owners.prefix", "need(z >= u, 'owners.prefix"),
    ('audit_owners', "need(0 <= z and z + w <= cap[c], 'owners.capacity",
     "need(0 <= z and z + w <= cap[c] + 1, 'owners.capacity"),
    ('audit_owners', "need(H == dict(sorted(ctx['claimed'].items())),",
     "need(True or H == dict(sorted(ctx['claimed'].items())),"),
    ('audit_owners', "need(o != crep[t] or pair_of[c] != cpair[t],", "need(True or o != crep[t] or pair_of[c] != cpair[t],"),
    ('audit_owners', "need(not (lo < t <= hi), 'owners.active_pair", "need(True or not (lo < t <= hi), 'owners.active_pair"),
    ('audit_owners', "need(win_a == win_b,", "need(True or win_a == win_b,"),
    ('audit_owners', "need(all(ivs[j][1] <= ivs[j + 1][0] for j in range(len(ivs) - 1)),",
     "need(True or all(ivs[j][1] <= ivs[j + 1][0] for j in range(len(ivs) - 1)),"),
    ('audit_owners', "need(h.hexdigest() == expected_payload_sha,", "need(True or h.hexdigest() == expected_payload_sha,"),
    ('audit_owners', "need(agg == lit,", "need(True or agg == lit,"),
    ('audit_owners', "need((helpers, centres, buffers, hi - lo) == (408, 8, 91, 2) and total == 437757,",
     "need(total == 437757 or True,"),
    ('audit_owners', "need(t == i // HELPERS and h == i % HELPERS,", "need(t == i // HELPERS,"),
    ('audit_owners', "need(order == emb,", "need(True or order == emb,"),
    ('audit_owners', "need(dispatch == emb,", "need(True or dispatch == emb,"),
    ('audit_owners', "need(h == expected['literal_files'][n],", "need(True or h == expected['literal_files'][n],"),
    ('audit_owners', "                touched[e['src']] = now\n", "                pass\n"),
    ('audit_endpoint', "need(kappa == C - MARGINS and", "need(kappa <= C - MARGINS and"),
    ('audit_endpoint', "need(C < Q(bit_endpoint),", "need(True or C < Q(bit_endpoint),"),
    ('audit_endpoint', "need(prof == intkeys(claim['profile']),", "need(True or prof == intkeys(claim['profile']),"),
    ('audit_endpoint', "need(max(own[0], ven[0]) <= min(own[1], ven[1]),",
     "need(True or max(own[0], ven[0]) <= min(own[1], ven[1]),"),
    ('audit_endpoint', "need(g > 0, 'endpoint.gain", "need(True or g > 0, 'endpoint.gain"),
    ('audit_staged_words', "AC.need(widths == prov['widths'], 'staged.providers:",
     "AC.need(True or widths == prov['widths'], 'staged.providers:"),
    ('audit_staged_words', "AC.need(fr['paid'] == AL.intkeys(prov['actual_paid_profile']),",
     "AC.need(True or fr['paid'] == AL.intkeys(prov['actual_paid_profile']),"),
    ('audit_staged_words', 'AC.need(len(old) == len(widths) and diffs == WIDTH_CHANGES,',
     'AC.need(len(old) == len(widths),'),
    ('audit_staged_words', "AC.need(loc == LOCALISATION, 'staged.parent_diff.sections",
     "AC.need(True or loc == LOCALISATION, 'staged.parent_diff.sections"),
    ('audit_staged_words', "AC.need(ra[1:] == rb[1:], 'staged.parent_diff.warp_record",
     "AC.need(True or ra[1:] == rb[1:], 'staged.parent_diff.warp_record"),
    ('audit_ceiling', "need(split == dp, 'ceiling.enum_complete",
     "need(True or split == dp, 'ceiling.enum_complete"),
    ('audit_ceiling', "need(lo > 0, 'ceiling.dual_feasible",
     "need(lo > -1, 'ceiling.dual_feasible"),
    ('audit_ceiling', "need(by == cx, 'ceiling.strong_duality",
     "need(True or by == cx, 'ceiling.strong_duality"),
    ('audit_ceiling', "need(not loose, 'ceiling.attain_tight",
     "need(True or not loose, 'ceiling.attain_tight"),
    ('audit_ceiling', "need(not outside, 'ceiling.attain_window",
     "need(True or not outside, 'ceiling.attain_window"),
    ('audit_ceiling', "need(AK.rejects(AK.moment(P, a_hi, live=model['live'])), 'ceiling.root_ceiling",
     "need(True or AK.rejects(AK.moment(P, a_hi, live=model['live'])), 'ceiling.root_ceiling"),
    ('audit_ceiling', "need(cp == P, 'ceiling.claimed_profile",
     "need(True or cp == P, 'ceiling.claimed_profile"),
    ('audit_inherited_controls', "AC.need(ok, 'controls.reject_def",
     "AC.need(True, 'controls.reject_def"),
    ('audit_inherited_controls', "AC.need(not bound_names(call), 'controls.gate_purity",
     "AC.need(True or not bound_names(call), 'controls.gate_purity"),
    ('audit_inherited_controls', "AC.need(r['pattern'] == PATTERN_OF[name], 'controls.pattern",
     "AC.need(True or r['pattern'] == PATTERN_OF[name], 'controls.pattern"),
    ('audit_inherited_controls', "AC.need(lo < t0 <= hi, 'controls.data_window",
     "AC.need(True or lo < t0 <= hi, 'controls.data_window"),
    ('audit_inherited_controls', 'AC.need(tuple(n for _, n, _ in out) == NAMES,',
     'AC.need(True or tuple(n for _, n, _ in out) == NAMES,'),
    ('audit_endpoint', "need(list(fr['helper_widths']) == list(staged_widths[pid]),",
     "need(True or list(fr['helper_widths']) == list(staged_widths[pid]),"),
    ('audit_endpoint', 'need(dict((r, n) for r, n in prof.items()) == dict((r, v * T) for r, v in sorted(lp1.items()) if v),',
     'need(True or dict((r, n) for r, n in prof.items()) == dict((r, v * T) for r, v in sorted(lp1.items()) if v),'),
    ('audit_endpoint', "need(kappa == C - MARGINS, 'downstream.kappa",
     "need(True or kappa == C - MARGINS, 'downstream.kappa"),
    ('audit_owners', "need(k in IGNORED_EVENTS,", "need(True or k in IGNORED_EVENTS,"),
    ('audit_endpoint', "need(CEIL.lower_uniform(rc, a0, a1) > 0,", "need(True or CEIL.lower_uniform(rc, a0, a1) > 0,"),
]

AUDIT_EXCEPTIONS = ('AuditFail', 'Reject', 'CheckFailure', 'VendorPinMismatch')


def scrub_git_env(environ):
    names = sorted(k for k in environ if k.startswith('GIT_CONFIG'))
    for k in names:
        del environ[k]
    return names


class VendorPinMismatch(Exception):
    """A vendored file or the journal does not match its pin."""


def file_pin(data, pin, path):
    blob, sha = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest(), hashlib.sha256(data).hexdigest()
    if (blob, sha) != tuple(pin):
        raise VendorPinMismatch('vendored file does not match its pin: %s (git blob %s, sha256 %s)' % (path, blob, sha))
    return blob, sha


def load_module(name, path, pin=None, mutation=None):
    """Read once, check the pin (if any) on those bytes, apply the mutation (local modules under --mutations only)
    and execute exactly those bytes as module `name` (registered in sys.modules; no .pyc can stand in)."""
    with open(path, 'rb') as f:
        data = f.read()
    computed = file_pin(data, pin, path) if pin is not None else None
    if mutation is not None and mutation[0] == name:
        text = data.decode('utf-8')
        if text.count(mutation[1]) != 1:
            raise RuntimeError('mutation target not unique in %s: %r' % (name, mutation[1]))
        data = text.replace(mutation[1], mutation[2]).encode('utf-8')
    mod = types.ModuleType(name)
    mod.__file__ = path
    sys.modules[name] = mod
    exec(compile(data, path, 'exec'), mod.__dict__)
    return mod, computed, data


def vendor_controls(loaded, AC):
    out = []
    for rel, (data, pin) in sorted(loaded.items()):
        name = 'vendored %s with one comment line appended (in memory)' % rel
        AC.attempt(name)
        try:
            file_pin(data + b'# tampered\n', pin, rel)
        except VendorPinMismatch as e:
            out.append(dict(control=name, expected='VendorPinMismatch', rejected_by=type(e).__name__,
                            message=str(e)[:120]))
            continue
        raise AC.AuditFail('negative control ACCEPTED: ' + name)
    return out


VOLATILE = ('seconds', 'runtime_seconds')


def strip_volatile(obj):
    if isinstance(obj, dict):
        return dict((k, strip_volatile(v)) for k, v in obj.items() if k not in VOLATILE)
    if isinstance(obj, list):
        return [strip_volatile(v) for v in obj]
    return obj


def canonical(obj):
    return strip_volatile(json.loads(json.dumps(obj, sort_keys=True, default=str)))


def compact(d):
    return json.dumps(d, sort_keys=True, separators=(',', ':'), default=str)


def run(args, log, mutation=None):
    loaded, vendor = {}, {}
    for rel, name, blob, sha in VENDOR:
        _, computed, data = load_module(name, os.path.join(HERE, *rel.split('/')), (blob, sha))
        loaded[rel] = (data, (blob, sha))
        vendor[rel] = dict(module=name, git_blob=computed[0], sha256=computed[1], bytes=len(data))
    AC, AL, AK, CA = (sys.modules[k] for k in ('audit_common', 'audit_lib', 'audit_kappa', 'check_accounting'))
    AC.reset_controls()
    fetched = AC.ensure_commits(args.repo, COMMITS, args.fetch, args.remote)
    mods = dict((name, load_module(name, os.path.join(HERE, name + '.py'), mutation=mutation)[0])
                for name in LOCAL_MODULES)
    if mutation is not None:
        print('MUTATION_APPLIED %s' % mutation[0], flush=True)
    for name in ('audit_staged_words', 'audit_inherited_controls'):
        mods[name].REPO = os.path.abspath(args.repo)     # both read pinned git objects from --repo
    I = AC.PinnedInputs(args.repo, INPUTS)
    res = dict(vendor=vendor, fetched=fetched)
    controls = []

    # C1: staged words -> helper widths
    words = mods['audit_staged_words'].run(controls=True)
    widths = words['helper_widths']
    controls += words['controls']
    res['words'] = mods['audit_staged_words'].summary(words)
    log('C1 words: %d controls' % len(words['controls']))

    # B: literal journal
    with open(os.path.join(HERE, *JOURNAL[0].split('/')), 'rb') as f:
        journal = f.read()
    AC.need(hashlib.sha256(journal).hexdigest() == JOURNAL[1], 'journal.pin: data/FILL-columns.xz sha256 differs')
    rows = mods['audit_owners'].decode_columns(journal)
    owners = mods['audit_owners'].run(I, widths, rows, AL, with_controls=True)
    oc = owners.pop('controls')
    n_owner_controls = len(oc)
    controls += oc
    res['owners'] = owners
    log('B owners: %d roles audited' % owners['audit']['rows'])

    # A: fixed-inventory LP ceiling
    ceiling = mods['audit_ceiling'].run(args.repo)
    res['ceiling'] = ceiling
    log('A ceiling: %s' % ceiling['status'])

    # D: endpoint and gains from the recounted profile
    claim = I.json('claim3633')
    AC.need(claim['frontier_pr'] == 3626 and claim['frontier_head'] == H3626
            and claim['frontier_sha256'] == AC.sha256(I.raw('claim3626')),
            'wiring.frontier: CLAIM.json frontier is not PR3626 CLAIM.json at the pinned head')
    preds = {'PR3626': (I.json('claim3626')['replicas'], I.json('claim3626')['profile'], I.json('claim3626')['kappa']),
             'PR3624': (I.json('claim3624')['replicas'], I.json('claim3624')['profile'], I.json('claim3624')['kappa']),
             'PR3605': (I.json('claim3605')['replicas'], I.json('claim3605')['profile'], I.json('claim3605')['kappa']),
             'PR3630': (740, I.json('claim3630')['histogram'], I.json('claim3630')['kappa'])}
    AC.need(I.json('claim3630')['roles'] == 2717280 and I.json('claim3630')['live'] == 896 * 740,
            'wiring.pr3630: PR3630 CLAIM is not a T740 claim')
    bit = I.json('claim3605')['unchanged_bit_endpoint']
    ED = mods['audit_endpoint']
    res['endpoint'] = ED.run(AK, CA, owners['audit']['profile'], claim, preds, bit)
    ec = ED.controls(AK, CA, AL, owners['audit']['profile'], claim, preds, bit)
    n_endpoint_controls = len(ec)
    controls += ec
    log('D endpoint: C=%s' % res['endpoint']['endpoint']['C'])

    # C2: inherited controls of PR3633's auditor
    inherited = mods['audit_inherited_controls'].run_integrated(I, owners_rows=rows, with_controls=True)
    ic = inherited.pop('controls')
    n_inherited_controls = len(ic)
    controls += ic
    res['inherited_controls'] = inherited
    log('C2 inherited controls analysed')

    # Downstream: PR3653 on the same journal
    CW = sys.modules['check_words']
    dw = dict(base=I.json('w3653_base'), extra=I.json('w3653_extra'))
    lpq = dict((int(r), Q(v)) for r, v in ceiling['lp']['minimum_profile_per_replica'].items())
    local = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
    basis = [(b['capacity'], tuple(b['pattern'])) for b in ceiling['lp']['basis']]
    CEIL = mods['audit_ceiling']
    res['downstream_pr3653'] = ED.downstream_3653(AK, CA, AL, CW, dw, widths, local, owners['audit']['profile'], lpq,
                                                  I.json('outer3653'), CEIL, basis)
    dc = ED.downstream_controls(AK, CA, AL, CW, dw, widths, local, owners['audit']['profile'], lpq,
                                I.json('outer3653'), CEIL, basis)
    n_endpoint_controls += len(dc)
    controls += dc
    log('downstream PR3653: kappa reproduced')

    # Wiring between scopes
    AC.need(dict((int(k), v) for k, v in owners['audit']['profile'].items())
            == dict((r, v * 488) for r, v in lpq.items()),
            'wiring.attainment: the literal recount is not 488 x the LP-minimum profile')
    AC.need(ceiling['patterns']['total'] == 2551 and ceiling['attainment']['equals_488_times_LP_minimum'] is True,
            'wiring.ceiling: ceiling record')
    res['wiring'] = dict(literal_recount_equals_488_lp_minimum=True, frontier_pr3626_bound=True)
    controls += vendor_controls(loaded, AC)
    ceiling_controls = ceiling.pop('controls')
    norm = [dict(control=c['control'], expected=c['expected'], rejected_by=c['rejected_by']) for c in controls]
    norm += [dict(control=c['name'], expected=c['expected'], rejected_by=c['raised']) for c in ceiling_controls]
    bad = [c for c in norm if c['rejected_by'] != c['expected']]
    AC.need(not bad and all(c['killed'] for c in ceiling_controls),
            'controls: %d negative controls not rejected by their expected rule: %r' % (len(bad), bad[:3]))
    AC.need(len(AC.ATTEMPTED) == len(norm), 'controls: %d attempts recorded for %d controls' % (len(AC.ATTEMPTED), len(norm)))
    res['controls'] = dict(attempted=len(norm), rejected_as_expected=len(norm) - len(bad),
                           distinct=len(set(c['control'] for c in norm)),
                           by_scope=dict(words=len(words['controls']), owners=n_owner_controls,
                                         ceiling=len(ceiling_controls), endpoint=n_endpoint_controls,
                                         inherited=n_inherited_controls, vendor=len(loaded)),
                           rules=sorted(set(c['expected'] for c in norm)))
    return res


def run_mutations(args):
    """An unmutated --fast baseline must pass first.  Each mutation then runs in a subprocess; it counts as killed
    only if the child reports MUTATION_APPLIED (the mutated module was loaded) and ends with an audit rejection."""
    killed, survived = [], []
    base = [sys.executable, '-I', '-B', os.path.abspath(__file__), '--repo', args.repo, '--fast']
    if args.fetch:
        base += ['--fetch', '--remote', args.remote]
    b = subprocess.run(base, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    last = [ln for ln in b.stdout.decode('utf-8', 'replace').strip().splitlines() if ln.strip()][-1:]
    if b.returncode != 0 or not last or not last[0].startswith(PASS_LINE):
        print('FAIL_MUTATIONS baseline did not pass: %s' % (last[0][:200] if last else ''), flush=True)
        return 1
    print('baseline: %s' % last[0][:120], flush=True)
    procs = []
    for k, (mod, old, new) in enumerate(MUTATIONS):
        procs.append((k, mod, subprocess.Popen(base + ['--mutation', str(k)], stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT)))
        while len([p for p in procs if p[2].poll() is None]) >= max(1, args.jobs):
            time.sleep(2)
    for k, mod, p in procs:
        out = p.communicate()[0].decode('utf-8', 'replace')
        last = [ln for ln in out.strip().splitlines() if ln.strip()][-1] if out.strip() else ''
        dead = (p.returncode == 1 and 'MUTATION_APPLIED' in out and last.startswith(FAIL_LINE)
                and last.split(' ', 2)[1].rstrip(':') in AUDIT_EXCEPTIONS)
        (killed if dead else survived).append((k, mod, last[:200]))
        print('mutation %2d (%s): %s' % (k, mod, 'killed: ' + last[:150] if dead
                                         else 'SURVIVED (exit %r): %s' % (p.returncode, last[:150])), flush=True)
    print('%s killed=%d/%d survived=%d' % ('PASS_MUTATIONS' if not survived else 'FAIL_MUTATIONS', len(killed),
                                           len(MUTATIONS), len(survived)), flush=True)
    return 0 if not survived else 1


def main():
    ap = argparse.ArgumentParser(description='Independent verification of PR #3633 (T488).')
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--remote', default=REMOTE_DEFAULT)
    ap.add_argument('--out', action='store_true')
    ap.add_argument('--fast', action='store_true')
    ap.add_argument('--mutations', action='store_true')
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--mutation', type=int, default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()
    scrub_git_env(os.environ)
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    if args.mutations:
        return run_mutations(args)
    mutation = MUTATIONS[args.mutation] if args.mutation is not None else None
    t0 = time.time()

    def log(msg):
        print('  [%5.1fs] %s' % (time.time() - t0, msg), flush=True)

    try:
        res = run(args, log, mutation)
        path = os.path.join(HERE, RESULT_NAME)
        got = canonical(dict((k, v) for k, v in res.items() if k not in ('fetched',)))
        if args.out:
            with open(path, 'w') as f:
                json.dump(got, f, indent=1, sort_keys=True)
                f.write('\n')
        elif not args.fast:
            with open(path) as f:
                want = json.load(f)
            if want != got:
                diff = sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))
                raise sys.modules['audit_common'].AuditFail('result.mismatch: RESULT.json differs in %s' % diff)
    except BaseException as exc:
        names = [getattr(sys.modules.get(m), n, None) for m, n in (('audit_common', 'AuditFail'),
                                                                    ('words_check', 'Reject'),
                                                                    ('fill_check80', 'CheckFailure'))]
        audit_types = tuple(t for t in names + [VendorPinMismatch] if t is not None)
        if not isinstance(exc, audit_types):
            traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        print('  run time %.1fs' % (time.time() - t0))
        print('%s %s: %s' % (FAIL_LINE, type(exc).__name__, ' '.join(str(exc).split()) or repr(exc)), flush=True)
        return 1
    print('  run time %.1fs' % (time.time() - t0))
    o, e, c = res['owners'], res['endpoint'], res['controls']
    print('%s roles=%d profile=%s idle=%s patterns=%d C=%s kappa=C-1e-46-1e-70 lp_ceiling=attained '
          'controls=%d/%d-rejected distinct=%d%s'
          % (PASS_LINE, o['audit']['rows'], compact(o['audit']['profile']), compact(o['audit']['idle']),
             res['ceiling']['patterns']['total'], e['endpoint']['C'], c['rejected_as_expected'], c['attempted'],
             c['distinct'], ' FAST' if args.fast else ''), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
