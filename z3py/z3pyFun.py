"""Модуль функцій для перевірки умов коректності та завершимості
маршрутів анотованої програми."""

from z3 import *
from exprlib.logilib.relation import reltoexpr
from z3py.typefun import type_z3


def formvarmon(mon):
    varlist = mon.ml
    return varlist


def formvarlpoly(poly):
    varlist = []
    monlist = poly.al
    for mon in monlist:
        vlist = formvarmon(mon)
        varlist.extend(vlist)
    return varlist


def formvarlconj(conj):
    """Будує список входжень змінних у вираз conj"""
    varlist = []
    for rel in conj.con:
        poly = rel.poly
        varl = formvarlpoly(poly)
        varlist.extend(varl)
    return varlist


def typecond(ctype):
    if ctype == 'c':
        condtype = " коректності "
    else:
        condtype = " завершимості "
    return condtype


def deldubl(varlist):
    varset = set(varlist)
    unilist = list(varset)
    return unilist


def transconjz(conj):
    """Утворює кон'юнкцію відношень в синтаксисі Z3py з об'єкту conj"""
    tconj = "And("
    n = 0
    for rel in conj.con:
        n += 1
        expr = reltoexpr(rel)
        if n > 1:
            tconj += ", "
        tconj += expr
    tconj += ")"
    return tconj


def convcondtoz3(cond):
    """Об'єкт cond класу Implication перетворює на
    умову коректності і список типів змінних у форматі розширення Z3py."""
    if type(cond) is str:
        return ""
    if type(cond) is bool:
        return ""
    ant = cond.ant
    cons = cond.cons
    # Утворимо впорядкований список змінних імплікації
    varant = formvarlconj(ant)
    varcons = formvarlconj(cons)
    varant.extend(varcons)
    varlist = deldubl(varant)
    varlist.sort()
    antz = transconjz(ant)
    consz = transconjz(cons)
    # zcond = "Implies(" + antz + ", " + consz + ")"
    # return [varlist, zcond]
    return [varlist, antz, consz]


def condlistz3(scondlist, ctype):
    """ Список scondlist обʼєктів класу Implication перетворює
    на список zcondlist умов коректності у форматі розширення Z3py.
    ctype - це тип умови: 'с' умова коректності, 't' - умова завершимості."""
    zcondlist = []
    for el in scondlist:
        m = el[0]       # m - це номер траси
        cond = el[1]    # cond - це умова коректності траси
        zcond = convcondtoz3(cond)
        varlist = zcond[0]
        condz = zcond[1]
        newel = [m, ctype, varlist, condz]
        zcondlist.append(newel)
    return zcondlist


def formZ3types(dict_param_types):
    """Словник param_types типів параметрів маршрутів перетворює до формату Z3.
    Для кожного типу даних утворює один рядок з оператором присвожвання."""
    linelist = []
    for curtype in dict_param_types:
        line = ""
        parlist = dict_param_types[curtype]
        el = type_z3(curtype)
        if el != "":
            npar = len(parlist)
            if npar == 1:
                z3type = el[0]
            else:
                z3type = el[1]
            n = 0
            for par in parlist:
                n += 1
                par = par.strip("'")
                line += par
                if n < npar:
                    line += ", "
            line += " = " + z3type + "('"
            n = 0
            for par in parlist:
                n += 1
                par = par.strip("'")
                line += par
                if n < npar:
                    line += " "
            line += "')"
    linelist.append(line)
    return linelist


def checkallconds(scondlist, stcondlist, dict_param_types_cp, tracks, parms):
    """ scondlist - це список умов коректності маршрутів,
        stcondlist - це список умов завершимості маршрутів,
        dict_param_types_cp - це словник типів параметрів маршрутів,
        tracks - це список маршрутів,
        parms - це список опцій:
            curdir - це каталог проекту,
            progname - це ім'я анотованої програми,
            terman - це ознака аналізу завершимості."""
    curdir = parms[0]
    # progname = parms[1]
    terman = parms[2]
    print("")
    indent = "    "
    # Шлях до генерованої програми II етапу - модуля перевірки умов
    # fname = curdir + '\\z3py\\z3counter.py'
    fname = curdir + '/z3py/z3conds.py'
    f = open(fname, 'wt')
    s = "# coding=CP1251"
    f.write(s + '\n')
    s = "from z3 import *"
    f.write(s + '\n')
    s = "from z3py.z3pyFun import checkcondz3"
    f.write(s + '\n')
    f.write('\n\n')
    s = "def checkcondsz3():"
    f.write(s + '\n')
    s = "resc = True"
    f.write(indent + s + '\n')
    s = "resList = []"
    f.write(indent + s + '\n')

    zcondlist = condlistz3(scondlist, "c")
    tcheck = "res = checkcondz3(cond)"      # , m, ctype)"
    tresc = "resc = resc and res"
    m = 0
    # ntrace = 0
    for zcond in zcondlist:
        ntrace = zcond[0] - 1
        track = tracks[ntrace]
        cp = track[0]
        dict_param_types = dict_param_types_cp[cp]
        linelist = formZ3types(dict_param_types)
        # ntrace += 1

        n = zcond[0]
        ctype = zcond[1]
        zc = zcond[3]
        if zc != "":
            m += 1
            condtype = typecond(ctype)
            f.write(indent + "#"'\n')
            s = "# Умова" + condtype + "траси №" + str(n)
            f.write(indent + s + '\n')
            s = "m = " + str(n)
            f.write(indent + s + '\n')
            s = "ctype = '" + ctype + "'"
            f.write(indent + s + '\n')
            # f.write(indent + varAss + '\n')
            for line in linelist:
                f.write(indent + line + '\n')
            f.write(indent + "cond = " + zc + '\n')
            f.write(indent + tcheck + '\n')
            f.write(indent + tresc + '\n')
            resList = "resList.append([m, 'c', res])"
            f.write(indent + resList + '\n')
        if m == 0:
            resc = "resc = None"
            f.write(indent + resc + '\n')
    if terman:
        f.write(indent + '\n')
        f.write(indent + '#\n')
        s = "rest = True"
        f.write(indent + s + '\n')
        m = 0
        ztcondlist = condlistz3(stcondlist, "t")
        # ntrace = 0
        for zcond in ztcondlist:
            ntrace = zcond[0] - 1
            track = tracks[ntrace]
            cp = track[0]
            dict_param_types = dict_param_types_cp[cp]
            linelist = formZ3types(dict_param_types)
            # ntrace += 1

            n = zcond[0]
            ctype = zcond[1]
            vl = zcond[2]
            zt = zcond[3]
            if zt != "":
                f.write(indent + "#"'\n')
                condtype = typecond(ctype)
                s = "# Умова" + condtype + "траси №" + str(n)
                f.write(indent + s + '\n')
                s = "m = " + str(n)
                f.write(indent + s + '\n')
                s = "ctype = '" + ctype + "'"
                for line in linelist:
                    f.write(indent + line + '\n')
                f.write(indent + "cond = " + zt + '\n')
            f.write(indent + tcheck + '\n')
            f.write(indent + tresc + '\n')
            resList = "resList.append([m, 't', res])"
            f.write(indent + resList + '\n')
    else:
        f.write('\n')
        rest = "rest = None"
        f.write(indent + rest + '\n')
    s = "return [resc, rest, resList]"
    f.write(indent + s + '\n')
    f.close()


def buildemptycond(curdir):
    # В модулі перевірки умов будує заглушку
    fname = curdir + '\\z3py\\z3counter.py'
    f = open(fname, 'wt')
    s = "def checkcondsz3():"
    f.write(s + '\n')
    s = "return True"
    indent = "    "
    f.write(indent + s + '\n')


def checkcondz3(cond):   # , nc, ctype):       # , console=True):
    """Застосовується для перевірки умови cond солвером z3.
    nc - номер траси,
    ctype - тип умови: c - коректності, t - завершимості траси.
    Результат: True, якщо умова правильна."""
    if type(cond) is bool:
        return cond
    else:
        # condtype = typecond(ctype)
        # indent = "    "
        s = Solver()
        s.add(Not(cond))
        c = s.check()
        r = (c == unsat)
        # if not r:
            # if console:
            #     print("Умова " + condtype + "траси №" + str(nc) + ":")
            #     print(cond)
            #     print("не виконується, наприклад, при таких значеннях змінних:")
            # m = s.model()
            # for d in m.decls():
            #     if console:
            #        print(indent + "%s = %s" % (d.name(), m[d]))
    return r


def z3CouEx(fCond, cType, nTrack, parms):
    """Згенерувати модуль для побудови контрприкладу.
    progName - це ім'я верифікованої програми,
    nTrack - це номер траси в програмі,
    cType - це тип умови ('c' - коректнысть, 't' - завершмість),
    fCond - умова у формі об'єкта класу Implication
    parms - це список параметрів:
        curdir - каталог проекту
        progname - ім'я анотованої програми?
        selCond - умова в текстовому вигляді."""
    curdir = parms[0]
    indent = "    "
    progName = parms[1]
    selCond = parms[2]
    res = convcondtoz3(fCond)   # , cType, nTrack, True)
    varlist = res[0]
    antz = res[1]
    consz = res[2]
    # Шлях до генерованої програми III етапу -
    #    модуля побудови контрприкладу для невірної умови
    fname = curdir + '\\z3py\\z3counter.py'
    f = open(fname, 'wt')
    s = "# coding=CP1251"
    f.write(s + '\n')
    s = "from z3 import *"
    f.write(s + '\n')
    f.write('\n\n')
    s = "def z3countP():"
    f.write(s + '\n')
    s = indent + "progName = '" + progName + "'"
    f.write(s + '\n')
    s = indent + "nTrack = " + str(nTrack)
    f.write(s + '\n')
    s = indent + "cType = '" + cType + "'"
    f.write(s + '\n')
    s = indent + "scond = '" + selCond + "'"
    f.write(s + '\n')
    s = indent + "parList = [progName, nTrack, cType, scond]"
    f.write(s + '\n')
    s = indent + "return parList"
    f.write(s + '\n')
    f.write('\n\n')

    s = "def z3counterEx():"
    f.write(s + '\n')
    varAss = formAss(varlist)
    f.write(indent + varAss + '\n')
    s = indent + "ant_ = " + antz
    f.write(s + '\n')
    s = indent + "cons_ = " + consz
    f.write(s + '\n')
    s = indent + "cond_ = Or(Not(ant_), cons_)"
    f.write(s + '\n')
    s = indent + "solver_ = Solver()"
    f.write(s + '\n')
    s = indent + "solver_.add(Not(cond_))"
    f.write(s + '\n')
    s = indent + "res_ = solver_.check()"
    f.write(s + '\n')
    s = indent + "if res_:"
    f.write(s + '\n')
    indent2 = indent + indent
    s = indent2 + "model_= solver_.model()"
    f.write(s + '\n')
    s = indent2 + "varNameList_ = []"
    f.write(s + '\n')
    s = indent2 + "varValList_ = []"
    f.write(s + '\n')
    s = indent2 + "for var_ in model_.decls():"
    f.write(s + '\n')
    indent3 = indent2 + indent
    s = indent3 + "varNameList_.append(var_.name())"
    f.write(s + '\n')
    s = indent3 + "varValList_.append(model_[var_])"
    f.write(s + '\n')
    s = indent2 + "return [res_, varNameList_, varValList_]"
    f.write(s + '\n')
    s = indent + "else:"
    f.write(s + '\n')
    s = indent2 + "return [res_]"
    f.write(s + '\n')


def formAss(vl):
    """Утворює оператор присвоювання змінним їх символьних значень"""
    n = len(vl)
    i = 0
    la = ""
    vlist = []
    for sv in vl:
        i += 1
        v = sv.strip("'")
        la += v
        vlist.append(v)
        if i < n:
            la += ", "
    la += " = "
    la += "Ints('"
    i = 0
    for v in vlist:
        i += 1
        la += v
        if i < n:
            la += " "
    la += "')"
    return la


def z3type(curtype):
    """Конвертує тип curtype в тип z3."""
    if curtype == "Int":
        return "Ints"
    elif curtype == "Real":
        return "Reals"
    elif curtype == "Char":
        return "Chars"
    else:
        return ""

