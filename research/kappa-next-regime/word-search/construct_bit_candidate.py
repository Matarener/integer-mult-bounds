#!/usr/bin/env python3
"""Literal three-covector R437 production applier; no optimizer dependency.

The shared carriers are463^=322,469^=271,468^=371 at their last A uses.
Their undo is paid and emitted in the regenerated literal FULL C word.  All
other scalar edges retain their operation/order; one early birth frame moves
from94 to184.  Source frames, endpoints,636-frame catalogue,437 helpers and
nine COPY interfaces are preserved.

Credit Nick Petalas for dirty shared covectors, ai-nanachi for the R437
composition, Ali Romman for its helper470 deletion, and the full retained
PR3647/PR589 source lineage. Substantial OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json

HERE=Path(__file__).resolve().parent
DEFAULT_SOURCE=HERE.parents[0]/'sources/PR3647/research/bit-p111-r437-gl464-470-20261018/data/r0042/R437-COMPOSED-WORD.json.gz'
SOURCE_SHA256='e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e'
SOURCE_CONTENT='da77deaf11368d016622348227657b98404b6afbc7e4f3d6fe9a246baae0dcce'
INSERTIONS={1995:[122,463,[322]],2033:[184,469,[271]],2043:[391,468,[371]]}
REMOVED={1995:[506,241,322],1999:[506,340,322],2006:[506,349,322],
         2033:[509,444,271],2040:[509,413,271],2043:[509,413,371]}
FRAME_CHANGE={229:([94,469,92],184)}
PROFILE={1:1322,2:1342,3:74,4:46,5:103,6:10,7:18}
DELTA={1:2,2:-2,3:-3,4:3,5:1,6:-1}


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def construct(word):
    flat=[[f,d,s] for f,d,ss in word['A'] for s in ss]
    for i,e in REMOVED.items():
        if flat[i]!=e:raise ValueError(('changed deletion preimage',i,flat[i],e))
    for i,(old,new) in FRAME_CHANGE.items():
        if flat[i]!=old:raise ValueError(('changed frame preimage',i,flat[i],old))
    # Exact observer contract: each changed carrier's only remaining A reads is
    # the listed common consumers, and B never reads these dead carriers.
    observations={463:[1996,2001,2008],469:[2038,2044],468:[2079]}
    for start,(f,a,ss) in INSERTIONS.items():
        observed=[i for i,e in enumerate(flat) if i>=start and e[2]==a]
        if observed!=observations[a]:raise ValueError(('new carrier observation',a,observed))
        if a in word['ret'] or any(a in ss for _,d,ss in word['B']):
            raise ValueError(('carrier observed after A',a))
    out=deepcopy(word);out['A']=[];scalar=0
    # Preserve original grouped gates except at the three actual insertion cuts.
    for f,d,sources in word['A']:
        pending=[];pending_frame=f
        def flush():
            if pending:out['A'].append([pending_frame,d,list(pending)]);pending.clear()
        for s in sources:
            if scalar in INSERTIONS:
                flush();out['A'].append(deepcopy(INSERTIONS[scalar]))
            actual_frame=FRAME_CHANGE[scalar][1] if scalar in FRAME_CHANGE else f
            if scalar not in REMOVED:
                if actual_frame!=pending_frame:flush();pending_frame=actual_frame
                pending.append(s)
            scalar+=1
        flush()
    if scalar!=2133:raise ValueError('changed source A scalar count')
    v=word['v']
    out['C']=[[1,d,list(ss)] for sec in ('A','B') for _,d,ss in out[sec]
              if not v<=d<2*v][::-1]
    return out


def main():
    if not __debug__:raise RuntimeError('Python assertions must be enabled')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    ap.add_argument('--out',type=Path,default=HERE/'candidate')
    args=ap.parse_args();raw=args.source.read_bytes()
    if sha256(raw).hexdigest()!=SOURCE_SHA256:raise ValueError('source archive SHA256')
    word=json.loads(gzip.decompress(raw))
    if sha256(canonical(word)).hexdigest()!=SOURCE_CONTENT:raise ValueError('source content SHA256')
    out=construct(word);args.out.mkdir(parents=True,exist_ok=True)
    payload=canonical(out);compressed=gzip.compress(payload,mtime=0)
    (args.out/'WORD.json.gz').write_bytes(compressed)
    counts=lambda w:{s:sum(len(g[2]) for g in w[s]) for s in ('D','A','B','C')}
    receipt=dict(status='PASS_LITERAL_THREE_LAST_USE_COVECTOR_APPLIER',
                 source_archive_sha256=SOURCE_SHA256,source_content_sha256=SOURCE_CONTENT,
                 word_archive_sha256=sha256(compressed).hexdigest(),
                 word_content_sha256=sha256(payload).hexdigest(),
                 changed_sections=['A','C'],insertions=INSERTIONS,removed=REMOVED,
                 frame_change=FRAME_CHANGE,old_scalar_counts=counts(word),new_scalar_counts=counts(out),
                 unchanged_fields=sorted(k for k in word if word[k]==out[k]),
                 expected_local_profile=PROFILE,expected_local_delta=DELTA,
                 expected_rank_mass=5113,expected_helpers=437,expected_frames=636,
                 scope='LITERAL_CONSTRUCTION; INDEPENDENT_NATIVE_AND_FULL_INVOICE_REQUIRED')
    (args.out/'CONSTRUCTION.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True),flush=True)


if __name__=='__main__':main()
