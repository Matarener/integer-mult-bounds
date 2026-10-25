# Printed 112-port triple count

## Question

The braid note prints `\binom{112}{3} = 229936` for the port triples of the pre-centre cut. What is the binomial coefficient, and do the printed histograms add up?

## Result

`C(112,3) = 227920`. The printed figure is larger by 2016. `C(112,2) = 6216`, and the printed order histogram `{2:0, 3:50, 4:1197, 5:1040, 6:959, 8:290, 9:1568, 12:792, 17:188, 20:132}` also sums to 6216. The printed extension counts `{77:24, 78:12, 79:5, 80:4, 81:3, 82:2}` sum to 50, matching the printed number of one-edge triples, and `846 + 50 = 896`. The ordered-product count `112 * 111 = 12432` matches the printed figure. The selected κ is unchanged.

## Boundary

This checks the binomial coefficient and the printed sums. It does not enumerate the 12,432 route products, rebuild the cut matrix, or decide which triples are dependent. The stop rule is to record this count.

## Reproduce

```bash
python3.12 -B research/braid-triple-count/verify.py
python3.12 -B research/braid-triple-count/test_verify.py
```

## Open next questions

None. The binomial and the printed sums are finite. Enumerating the route products would leave this package.

## Credit

dcharb78 printed the triple count and the histograms in PR #3147. The checker recomputes the binomial coefficient and adds the printed figures. Substantial assistance from the Cursor coding agent contributed to the execution, checker and writeup.
