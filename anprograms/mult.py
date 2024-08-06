# coding=CP1251
"""Множення двох цілих чисел за допомогою операції додавання (Андерсон)."""


# AREA(Int)
def mult(m, n):
    # CP(I):
    #   m >= 0
    # ECP
    i = 0
    j = 0
    while i < m:
        # CP(1):
        #   j == i * n
        #   i < m
        #   VE(m - i)
        # ECP
        j += n
        i += 1
    # CP(E):
    #   j == m * n
    # ECP
    return j


m = 7
n = 8
r = mult(m, n)
print("Product = " + str(r))
