# coding=CP1251
# Program computes quotient q and remainder r
#   in division x by y. Коректна. Але незавершима.
#   Відсутнє відношення y > 0 в умові КТ 1,
#   необхідне для доведення завершимості.
x = 24
y = 6

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
    #   VE(r)
    # ECP
    r -= y
    q += 1
# CP(E):
#   x == q * y + r
#   r < y
# ECP

print("q =", q, ", r =", r)
