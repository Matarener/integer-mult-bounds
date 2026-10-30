# Discovery and verification boundary

The first all-rank relaxation reused the predecessor quotient cuts and coordinate covers. It remained below the needed bound. Several integral cost-62 covers also missed six, seven or eight target directions. These failures did not establish an obstruction.

Further greedy response-span cuts improved the relaxation but did not close it. The useful change was to use complete eight-coordinate target bases as rank-eight cuts, then exclude rank eight temporarily. A rank-nine channel has the full response space, so a proof in that temporary domain can transfer back to every rank mixture.

SciPy 1.15.3 with NumPy 2.4.6 supplied candidate LP weights. Modular arithmetic with prime 1000003 was used only to choose candidate cuts. We then removed every per-frame upper count bound and solved the uncapped relaxation. Every retained dual weight was rounded down to a multiple of 1/100000000. No upward capacity adjustment was needed. The final exact lower bound is 72.05503795.

The final checker uses the Python standard library. It rebuilds every retained cut over the rationals, checks all capacities and uses separate integer determinants for the 48 coordinate bases. It imports no optimizer and trusts no discovery rank or LP success status. The failed all-rank screens are not separate contributions.
