#!/usr/bin/env python3
"""Optional fresh C++ replay of the new provider's raw6 stream.

The historical sources are copied byte-for-byte after authentication. Their
assertions and precision caps remain unchanged. The old scalar checker MUST
reject the 104-bit cap; that rejection is a control, not a scalar PASS.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PINS = {
    "legality_h.cpp": "6c1ef2b24e57781d6951c172a1024fc4300e6fd392c9d6672079a7806ab663b3",
    "columns_k.cpp": "1c344d18fcd494eeca93e259f10cafae7705780e6592f6dcb35b34752dab9bc2",
    "json.hpp": "aaf127c04cb31c406e5b04a63f1ae89369fccde6d8fa7cdda1ed4f32dfc5de63",
    "stage_cohort.py": "6c288f6f234b528c1a7c0a4adfb724e91e0fe6b18c8dffad96af3f973de1829a",
    "bits/stdc++.h": "420094be2af295eed03a983dd66debbbe9cfb78d8252859f4498a615a0074b99",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--boost-include",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True,
                        help="new directory for compiler, input, log, and receipt files")
    parser.add_argument("--provider-output",type=Path,
                        help="reuse emitted files only when their entire receipt and hashes match NATIVE.json")
    parser.add_argument("--cxx",default="c++")
    args=parser.parse_args()
    args.output=args.output.resolve()
    args.output.mkdir(parents=True,exist_ok=False)
    need((args.boost_include/"boost"/"multiprecision"/"cpp_int.hpp").is_file(),
         "Boost include directory")
    compiler=shutil.which(args.cxx)
    need(compiler is not None,"C++ compiler")
    expected=json.loads((ROOT/"NATIVE.json").read_bytes())
    need(expected["native_source_pins"] == PINS,"frozen receipt native source pins")
    sources=args.output/"source"
    for name,pin in PINS.items():
        raw=(ROOT/"inputs"/"native"/name).read_bytes()
        need(sha256(raw).hexdigest() == pin,"native source digest "+name)
        dest=sources/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(raw)
    commands=[]
    environment=dict(os.environ)
    environment.pop("PYTHONOPTIMIZE",None)
    environment.pop("PYTHONPATH",None)

    def run(label,command,timeout=180,expected_return=0):
        start=time.monotonic()
        result=subprocess.run(list(map(str,command)),capture_output=True,env=environment,
                              timeout=timeout)
        (args.output/(label+".stdout")).write_bytes(result.stdout)
        (args.output/(label+".stderr")).write_bytes(result.stderr)
        item={"label":label,"argv":list(map(str,command)),"returncode":result.returncode,
              "elapsed_seconds":round(time.monotonic()-start,6),
              "stdout_sha256":sha256(result.stdout).hexdigest(),
              "stderr_sha256":sha256(result.stderr).hexdigest()}
        commands.append(item)
        write(args.output/"commands.json",commands)
        need(result.returncode == expected_return,"unexpected return code for "+label)
        return result

    version=run("compiler-version",[compiler,"--version"])
    provider=args.provider_output
    if provider is None:
        provider=args.output/"provider"
        result=run("provider",[sys.executable,"-I","-B",ROOT/"native.py","--output",provider])
        need(json.loads(result.stdout) == expected,"fresh portable provider complete receipt")
    provider=provider.resolve()
    observed=json.loads((provider/"NATIVE-PROVIDER.json").read_bytes())
    need(observed == expected,"reused portable provider complete receipt")
    for name,word in expected["words"].items():
        for rel,pin in word["emitted_file_sha256"].items():
            need(sha256((provider/name/rel).read_bytes()).hexdigest() == pin,
                 "emitted file pin "+name+"/"+rel)

    flags=["-O2","-std=c++17","-DHDIM=8","-DNCOPY=9","-DVPORTS=111",
           "-I",sources,"-I",args.boost_include.resolve()]
    legality=args.output/"legality"
    columns=args.output/"columns-k2"
    run("compile-legality",[compiler,*flags,sources/"legality_h.cpp","-o",legality])
    run("compile-columns-control",[compiler,*flags,"-DRHELP=438","-DKPAIRS=2",
                                    sources/"columns_k.cpp","-o",columns])
    # Compile and execute the exact bytes authenticated above; normal import
    # machinery and any pre-existing bytecode caches are not consulted.
    bootstrap=(
        "import hashlib,pathlib,sys;"
        "p=pathlib.Path(sys.argv[1]);b=p.read_bytes();"
        "assert sys.flags.optimize==0;"
        "assert hashlib.sha256(b).hexdigest()==sys.argv[2];"
        "sys.argv=[str(p)]+sys.argv[3:];"
        "exec(compile(b,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})"
    )
    receipts={}
    for name,word in expected["words"].items():
        cin,cout=args.output/(name+"-cin"),args.output/(name+"-cout")
        source=provider/name
        run("stage-"+name,[sys.executable,"-I","-B","-c",bootstrap,
                          sources/"stage_cohort.py",PINS["stage_cohort.py"],
                          source,source,cin,cout])
        need(sha256((cout/"COHORT249-RECORDS.bin").read_bytes()).hexdigest()
             == word["native_raw6_sha256"],"staged raw6 binding")
        receipt=args.output/(name+"-legality.json")
        run("legality-"+name,[legality,cin,cout,receipt])
        audit=json.loads(receipt.read_bytes())
        hist={str(k):v for k,v in audit["paid_histogram"]}
        need(audit["records"] == word["records"]
             and audit["common_frame_ADDs"] == word["ADDs"]
             and audit["rank_mass"] == word["rank_mass"]
             and audit["copies"] == audit["erasures"] == 9
             and audit["nested_MOVEs"]+9 == word["paid_queries"]
             and hist == word["local_checks"]["forward"]["histogram"],
             "C++ complete invoice matches signed provider")
        rejection=run("old-cap-"+name,[columns,source/"249-records.bin",
                       args.output/(name+"-old-columns.json")],expected_return=2)
        need(rejection.stderr.strip() == b"payloadfiniteprefix2^104",
             "old scalar checker rejects exactly its unchanged precision cap")
        need(not (args.output/(name+"-old-columns.json")).exists(),
             "old checker must not write a passing scalar receipt")
        receipts[name]={"legality":audit,"old_104_bit_cap_rejected":True,
                        "native_raw6_sha256":word["native_raw6_sha256"]}
    report={
        "status":"PASS_FRESH_UNCHANGED_CPP_LEGALITY_AND_PRECISION_REJECTION_CONTROLS",
        "provider_receipt_sha256":sha256((ROOT/"NATIVE.json").read_bytes()).hexdigest(),
        "native_source_pins":PINS,"compiler":compiler,
        "compiler_version":version.stdout.decode().strip(),
        "platform":platform.platform(),
        "boost_include":str(args.boost_include.resolve()),
        "executed_commands":commands,"words":receipts,
        "scope":"New raw6 provider, unchanged chronological C++ legality; old scalar cap rejection is deliberate.",
        "old_H1_H5_pipeline_pass_claimed":False,
        "old_CXX_scalar_columns_pass_claimed":False,
        "physical_global_compiler_run_claimed":False,
        "no_new_kappa":True,
    }
    write(args.output/"NATIVE-CXX.json",report)
    print(json.dumps(report,sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
