# coding=CP1251
# AREA(Int)
def frac(x, y):
    """Function computes quotient q and remainder r
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
        #   x - q >= 0
        #   VE(x - q)
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
