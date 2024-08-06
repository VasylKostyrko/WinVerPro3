def frac(x, y):
    """Program computes quotient q and remainder r
       in division x by y. Коректна і завершима."""
    # CP(I):
    #    TYPE(x, y: Int)
    #    x >= 0
    #    y > 0
    # ECP
    r = x
    q = 0
    while y <= r:
        # CP(1):
        #    TYPE(x, y, q, r: Int)
        #    x == q * y + r
        #    y > 0
        #    VE(r)
        # ECP
        r -= y
        q += 1
    # CP(E):
    #    TYPE(x, y, q, r: Int)
    #    x == q * y + r
    #    r < y
    # ECP
    return {"quotient": q, "remainder": r}


res = frac(16, 3)
print("quotient = " + str(res["quotient"]) + ", remainder = " + str(res["remainder"]))
