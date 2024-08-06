from z3 import *

# x = Int('x')
# y = Real('y')
# a = Array('a', IntSort(), IntSort())
#
# print((x + 1).sort())
# print((y + 1).sort())
# print((x >= 2).sort())
#
# print(a.sort())
#
# s = Consts('s', CharSort())
# print(s.sort())
# print(s)
#
# m = Consts('m', IntSort())
# print(m.sort())
# print(m)

m = Int('m')
a1 = Array('a1', IntSort(), IntSort())
a2 = Array('a2', IntSort(), IntSort())
x = ForAll(m, Implies((a1[m] > a2[m]), (a1[m] >= a2[m])))
x = ForAll(m, Implies((a1[m] > a2[m]), (a1[m] >= a2[m])))
print(x)
