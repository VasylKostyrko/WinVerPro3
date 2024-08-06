# coding=CP1251
from z3 import *
from z3py.z3pyFun import checkcondz3


def checkcondsz3():
    resc = True
    resList = []
    #
    # Умова коректності траси №3
    m = 3
    ctype = 'c'
    q0, r0, x, y = Ints('q0 r0 x y')
    cond = Implies(And(q0 * y + r0 - x == 0, -q0 + x >= 0, r0 - 2 * y >= 0), And(-1 - q0 + x >= 0))
    res = checkcondz3(cond)
    resc = resc and res
    resList.append([m, 'c', res])
    
    #
    rest = True
    return [resc, rest, resList]
