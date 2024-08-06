# Source data
x = 16
y = 3

# Program computes quotient q and remainder r
#   in division x by y
r = x
q = 0
while y <= r:
    r -= y
    q += 1

# Output results
print("q =", q, ", r =", r)
