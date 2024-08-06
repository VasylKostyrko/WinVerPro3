# coding=CP1251
# AREA(Int)
def leftPad(c, n, s):
    """Текстовий рядок s доповнює зліва до довжини n символом c."""
    # CP(I):
    # TYPE(v, s: Array(Char); c: Char)
    # ECP
    l = len(s)
    m = max(n - l, 0)
    v = []
    for i in range(m):
        v.append(c)
    for j in range(l):
        v.append(s[j])
    # CP(E):
    # ForAll(k; k in [0..m); v[k] == c)
    # ForAll(k; k in [0..l); v[m + k] == s[k])
    # ECP
    return v


res = leftPad('+', 5, "day")
print(res)
print("".join(res))

res = leftPad('+', 0, "day")
print(res)
print("".join(res))
