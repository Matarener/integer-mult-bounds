"""Separate bottom-up census of every bounded original width.

No primary or predecessor executable is imported. The infinite statement is
the written proof; this is independent finite arithmetic/branch evidence.
Prepared by ToikY with substantial OpenAI Codex assistance, Apache-2.0.
"""
import hashlib
import json

LIMIT = 2**20
ROW_FACTOR = 269241600


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def prime_certificate(row):
    q, h, n, a = (row[key] for key in ('q', 'h', 'n', 'a'))
    require(all(type(x) is int for x in (q, h, n, a)), 'integer prime certificate')
    require(n > 0 and 0 < h < 2**n and h % 2 == 1 and q == h*2**n+1,
            'Proth form with known two-part larger than square root')
    require(q > 2**80 and 1 < a < q and pow(a, (q-1)//2, q) == q-1,
            'exact order certificate, not probable primality')
    require(2**(2*n) > q, 'prime-divisor order forces primality')
    return q


def correction(q, depth):
    if depth == 0:
        return 0
    # P(q)>1-1/(q-1); Bernoulli gives P(q)^D>1-D/(q-1).
    # Thus these small integer comparisons determine the exact ceil log
    # without constructing a GL catalogue or the huge Count-tape stock.
    value = ROW_FACTOR**depth
    power, exponent = 1, 0
    while power < value:
        power *= q
        exponent += 1
    require(value*(q-1-depth) > (power//q)*(q-1),
            'separate strict lower stock bound proves exact correction')
    return exponent


def check(primary):
    witnesses = primary['prime_witnesses']
    require(len(witnesses) == 7, 'seven prime class witnesses')
    depths = bytearray(LIMIT+1)
    for width in range(64, LIMIT+1):
        child = 42*(width//64)
        require(child < width, 'bottom-up recursion contracts')
        depths[width] = 1 + depths[child]
    require(LIMIT < 2**577, 'exact atom width two on 2..LIMIT')
    max_depth = max(depths)
    changes = [width for width in range(1, LIMIT+1)
               if depths[width] != depths[width-1]]
    classes, covered = [], set()
    for witness in witnesses:
        q = prime_certificate(witness)
        additions = [correction(q, depth) for depth in range(max_depth+1)]
        m = additions[19]
        cutoff = 311297 + 2*m
        require(1 <= m <= 7 and witness['m'] == m and witness['cutoff'] == cutoff,
                'independently determined class and cutoff')
        require(m not in covered, 'distinct prime classes')
        covered.add(m)
        k_by_depth = [8192*depth + additions[depth]
                      for depth in range(max_depth+1)]
        first_fit, last_reject, accepted, first_guard_only = None, None, 0, 0
        runs, previous = [], None
        for original in range(1, LIMIT+1):
            atom = 1 if original == 1 else 2
            depth = depths[original]
            borrowed = k_by_depth[depth]  # D=0 also covers the sole w=1 case.
            first = 2*borrowed < original
            body = (original-borrowed)//atom if first else 0
            remainder = (original-borrowed) % atom if first else 0
            fits = first and body >= 64
            require(fits == (original >= cutoff), 'complete bounded iff decision')
            if not first:
                require(body == remainder == 0, 'failed first guard leaves zeros')
            if fits:
                accepted += 1
                if first_fit is None:
                    first_fit = original
            else:
                last_reject = original
            first_guard_only += first and not fits
            state = (depth, borrowed, first, fits)
            if state != previous:
                if runs:
                    runs[-1]['last'] = original-1
                runs.append(dict(first=original, depth=depth, borrowed=borrowed,
                                 first_guard=first, fits=fits))
                previous = state
        runs[-1]['last'] = LIMIT
        require(first_fit == cutoff and last_reject == cutoff-1
                and first_guard_only == 63, 'both guards, not borrowing alone')
        classes.append(dict(m=m, q=q, cutoff=cutoff, first_fit=first_fit,
                            last_reject=last_reject, accepted_widths=accepted,
                            first_guard_pass_body_guard_fail=first_guard_only,
                            corrections_by_depth=additions, complete_branch_runs=runs))
    require(covered == set(range(1, 8)), 'every possible prime class realized')
    return dict(status='PASS_SEPARATE_ALL_BOUNDED_WIDTH_DECISIONS',
                method='bottom-up literal floor recurrence, separate stock bound and exact prime order checks',
                limit=LIMIT, widths_per_prime=LIMIT, prime_classes=7,
                complete_decisions=7*LIMIT, maximum_depth=max_depth,
                actual_depth_thresholds=changes,
                depth_table_sha256=hashlib.sha256(depths).hexdigest(),
                classes=classes, classes_sha256=digest(classes),
                scope='Finite complete decision census through 2^20; infinite tail rests on PROOF.md. No Count/native/payload/outer admission.')
