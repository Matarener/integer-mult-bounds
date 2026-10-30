#!/bin/bash
# bt.sh TAG NETFILE ITERS SEED -- one single-core unified-engine SA (kslide + hop on), outputs next to the net as u_TAG.{out,log,net}
D=$(dirname "$2"); cd "$D" || exit 1
K="$(cd "$(dirname "$0")" && pwd)"
env K2_NET=$(basename "$2") K2_SEARCH=sa K2S_ITERS=$3 K2S_T0=0.3 K2S_T1=0.01 K2S_SEED=$4 K2S_PEEL=2 K2S_W=1,1,1,0.5,1,2,0.5,0.3,2,0,0,0,0,0,1,3 K2S_OUT=u_$1.net K2S_LOG=u_$1.log $K/bin/k2u > u_$1.out 2>&1
