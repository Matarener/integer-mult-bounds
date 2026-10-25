# Exact equivalence of the integer kernel

Fix any exact Fraction argument x. Negative arguments follow the unchanged
reciprocal branch; zero and positive arguments use exactly the predecessor's
halving loop until 0 <= x = p/q <= 1/64, q > 0. Thus both algorithms have the
same reduced argument and the same number of subsequent squarings.

Write D_j = q^j j!, P_j = p^j, and S_j = sum_{i=0}^j x^i/i!.
Induction gives S_j = N_j / D_j with

    N_0 = D_0 = P_0 = 1
    P_j = p P_{j-1}
    D_j = j q D_{j-1}
    N_j = j q N_{j-1} + P_j.

These are integer operations. They compute exactly the reference's forty
Fraction multiply/add steps without reducing intermediate numerator/denominator
pairs. The final term is P_40 / D_40. The reference's exact positive tail is

    R = (P_40/D_40) (p/q) / 41 / (1 - p/(42q))
      = 42 P_40 p / [41 D_40 (42q-p)].

The denominator is positive on the reduced domain, including p=0. Therefore
`taylor_parts` returns exact unreduced fractions for S_40 and S_40+R. No error
term or positive tail is dropped merely because it is usually below one grid unit.

For M=10^65 and nonnegative integers a,b with b>0, the reference's grid floor
of a/b is floor(a M/b)/M and the grid ceiling is ceil(a M/b)/M. Python integer
`//` and `(a*M+b-1)//b` implement these exactly. Once a bound is represented
as n/M, flooring its square is floor(n^2/M)/M, and ceiling its square is
ceil(n^2/M)/M. Hence induction through every squaring gives the identical
pair of rational endpoints. The negative branch applies identical reciprocals
and identical outward rounding to identical endpoints. The unchanged logarithm,
power, moment, interval subtraction and strict allowance functions consequently
produce identical results for their supported exact inputs.

This is an algebraic equivalence proof for the fixed authenticated engine, not
a new proof of its transcendental enclosure theorem or of integer multiplication.
The executable differential tests support the implementation of the recurrence;
finite tests alone are not the universal argument. Authentication, the original
rank checks, and explicit guards remain active under `python -O`.
