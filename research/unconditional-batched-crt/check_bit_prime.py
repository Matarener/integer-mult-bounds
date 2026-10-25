"""Check a complete Lucas primality certificate, using integer arithmetic only."""
import json
import math
from pathlib import Path


def verify(data):
    certificates = data["certificates"]
    proved = set()
    active = set()

    def prime(n):
        if n in proved:
            return
        if n in active or n < 2:
            raise ValueError("invalid certificate dependency")
        active.add(n)
        node = certificates[str(n)]
        if node["prime"] != n:
            raise ValueError("certificate name")
        if n != 2:
            factors = node["factors"]
            if not factors or math.prod(factors) != n - 1:
                raise ValueError("incomplete factorization")
            for r in factors:
                if r >= n:
                    raise ValueError("nondecreasing certificate dependency")
                prime(r)
            g = node["base"]
            if not 1 < g < n or pow(g, n - 1, n) != 1:
                raise ValueError("order does not divide n-1")
            if any(pow(g, (n - 1) // r, n) == 1 for r in set(factors)):
                raise ValueError("order is a proper divisor of n-1")
        proved.add(n)
        active.remove(n)

    root = data["root"]
    prime(root)
    if root != 2**89 - 1 or root <= 2**80 or 2 * 64**3 * 10**16 >= root:
        raise ValueError("BIT prime and bad-class requirements")
    return {"status": "PASS_COMPLETE_BIT_PRIME_CERTIFICATE", "q": root,
            "proved_primes": len(proved), "bad_fraction_less_than_1e_16": True}


if __name__ == "__main__":
    path = Path(__file__).with_name("BIT-PRIME-CERTIFICATE.json")
    print(json.dumps(verify(json.loads(path.read_text())), sort_keys=True, indent=2))
