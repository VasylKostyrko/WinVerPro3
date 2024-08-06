# coding=CP1251
# Input data
x = 16
y = 3

# Program computes quotient q and remainder r
#   in division x by y. Коректна.
# AREA(Int)
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

# Output results
print("q =", q, ", r =", r)
