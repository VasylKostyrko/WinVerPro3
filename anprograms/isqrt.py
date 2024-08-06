# coding=CP1251
"""Обчислює цілу частину квадратного кореня
невід'ємного цілого числа a (Камкин)."""


# AREA(Int)
def isqrt(n):
    # CP(I):
    #   n > 0
    # ECP
    k = 0
    while (k + 1) * (k + 1) <= n:
        # CP(1):
        #   (k + 1) ** 2 <= n
        #   VE(n - (k + 1) ** 2))
        # ECP
        k += 1
    # CP(E):
    #   (k + 1) ** 2 > n
    #   k ** 2 <= n
    # ECP
    return k


n = 17
k = isqrt(n)
print("isqrt = " + str(k))
