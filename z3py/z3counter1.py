# coding=CP1251
from z3 import *
from z3py.z3pyFun import checkcondz3


def checkcondsz3():
    resc = True
    resList = []
    #
    # Умова коректності траси №1
    m = 1
    ctype = 'c'
    x, y = Ints('x y')
    cond = Implies(And(x >= 0, y > 0, x - y >= 0), And(x - x == 0, y > 0))
    res = checkcondz3(cond)
    resc = resc and res
    resList.append([m, 'c', res])
    #
    # Умова коректності траси №2
    m = 2
    ctype = 'c'
    x, y = Ints('x y')
    cond = Implies(And(x >= 0, y > 0, -x + y > 0), And(x - x == 0, -x + y > 0))
    res = checkcondz3(cond)
    resc = resc and res
    resList.append([m, 'c', res])
    #
    # Умова коректності траси №3
    m = 3
    ctype = 'c'
    q0, r0, x, y = Ints('q0 r0 x y')
    cond = Implies(And(-q0 * y - r0 + x == 0, y > 0, r0 - y - y >= 0), And(-q0 * y - r0 + x - y + y == 0, y > 0))
    res = checkcondz3(cond)
    resc = resc and res
    resList.append([m, 'c', res])
    #
    # Умова коректності траси №4
    m = 4
    ctype = 'c'
    q0, r0, x, y = Ints('q0 r0 x y')
    cond = Implies(And(-q0 * y - r0 + x == 0, y > 0, -r0 + y + y > 0), And(-q0 * y - r0 + x - y + y == 0, -r0 + y + y > 0))
    res = checkcondz3(cond)
    resc = resc and res
    resList.append([m, 'c', res])
    
    #
    rest = True
    #
    # Умова завершимості траси №3
    m = 3
    x, y = Ints('x y')
    cond = Implies(And(-q0 * y - r0 + x == 0, y > 0, r0 - y - y >= 0), And(y > 0))
    res = checkcondz3(cond)
    resc = resc and res
    resList.append([m, 't', res])
    return [resc, rest, resList]
