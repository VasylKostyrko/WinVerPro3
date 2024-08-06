# coding=CP1251
"""Знаходить частку та залишок від ділення цілих чисел."""

# AREA(Int)
def frac(x, y):
    """Program computes quotient q and remainder r
       in division x by y."""
    # CP(I):
    #   x >= 0
    #   y > 0
    # ECP
    r = x
    q = 0
    while y <= r:
        # CP(1):
        #   x == q * y + r
        # ECP
        r -= y
        q += 1
    # CP(E):
    #   x == q * y + r
    #   r < y
    # ECP
    return {"quotient": q, "remainder": r}


res = frac(16, 3)
print("quotient = " + str(res["quotient"]) + ", remainder = " + str(res["remainder"]))
