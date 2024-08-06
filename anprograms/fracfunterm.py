# coding=CP1251
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
        #   y > 0
        #   VE(r)
        # ECP
        r -= y
        q += 1
    return {"quotient": q, "remainder": r}
    # CP(E):
    #   x == q * y + r
    #   r < y
    # ECP


res = frac(16, 3)
print("quotient = " + str(res["quotient"]) + ", remaimder = " + str(res["remaimder"]))
