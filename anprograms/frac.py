x = 16
y = 3

# CP(I):
r = x
q = 0
while y <= r:
    # CP(1):
    r -= y
    q += 1
# CP(E):


print("q =", q, ", r =", r)
