def frac(x, y):
    """Program computes quotient q and remainder r
       in division x by y."""
    # CP(I):
    #    TYPE(x, y: Int)
    #    x >= 0
    #    y > 0
    # ECP
    r = x
    q = 0
    while y <= r:
        # CP(1):
        #    TYPE(x, y, r, q: Int)
        # ECP
        r -= y
        q += 1
    # CP(E):
    #    TYPE(x, y, r, q: Int)
    # ECP
    return {"quotient": q, "remainder": r}


res = frac(16, 3)
print("quotient = " + str(res["quotient"]) + ", remainder = " + str(res["remainder"]))
