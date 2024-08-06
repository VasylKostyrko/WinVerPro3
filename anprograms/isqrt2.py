# coding=CP1251
"""Обчислює цілу частину квадратного кореня
невід'ємного цілого числа a (Камкин, Миронов)."""


# AREA: Int
def isqrt(n):
    # CP(I):
    #   n > 0
    # ECP
    a = 0
    b = 1
    c = 1
    while b <= n:
        # CP(1):
        a += 1
        c += 2
        b += c
    # CP(E):
    #   n < (a + 1) ** 2
    #   n >= a ** 2
    return a


n = 17
r = isqrt(n)
print("isqrt = " + str(r))
