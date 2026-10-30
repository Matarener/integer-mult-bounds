"""Independent sparse signed-row primitives; no producer imports."""

def identity(n):
    return [{i: 1} for i in range(n)] + [{}]

def add(a, b, c):
    output = a.copy()
    for j, value in b.items():
        output[j] = output.get(j, 0) + c * value
        if not output[j]:
            del output[j]
    return output

def parity(rows):
    return [sum(1 << j for j,c in row.items() if c & 1) for row in rows]
