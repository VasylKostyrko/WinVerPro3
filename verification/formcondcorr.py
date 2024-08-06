"""Модуль функцій над умовами коректності трас анотованої програми."""

from verification.common import assignment, peek, identifier
from exprlib.treelib.tree import exprtree, createtree, createuntree, copytree
from exprlib.logilib.implication import Implication
from exprlib.logilib.conjunct import treetocon, Conjunct, copyconj
from exprlib.arilib.polynom import treetopoly
from exprlib.logilib.relation import Relation


def formvardict(v):
    """Список операторів присвоювання v перетворює в словник значень змінних.
    Оператори присвоювання повинні бути простими (без нагромадження).
    Вираз у правій частині кожного оператора не повинен містити змінної з лівої частини.
    Вирази в правих частинах операторів присвоювання не повинні містити
    змінних з їх лівих частин."""
    dictvar = {}
    for ass in v:
        pair = assignment(ass)
        var = pair[0]
        val = pair[1]
        dictvar[var] = val
    return dictvar


def trackeltype(el):
    """Визначає тип елемента траси el.
    1, 2, 3, 4 - оператори присвоювання різних видів,
    0 - умова переходу."""
    npos = el.find(" = ")
    if npos > 0:
        return 1
    else:
        npos = el.find(" += ")
        if npos > 0:
            return 2
        else:
            npos = el.find(" -= ")
            if npos > 0:
                return 3
            else:
                npos = el.find(" *= ")
                if npos > 0:
                    return 4
    return 0


def findvarset(expr):
    """Утворює множину вільних змінних виразу expr."""
    tree = exprtree(expr, "r")
    stack = []
    varset = set()
    while True:
        if type(tree) is str or type(tree) is int or type(tree) is bool:
            # Листок дерева виразу
            if type(tree) is str:
                varset.add(tree)
            if len(stack) == 0:
                break
            tree = stack.pop()
            # tree = tree.getright()
        else:
            # Спускаємося по лівому піддереву
            if tree.binary():
                stack.append(tree.getright())
                tree = tree.getleft()
            else:
                # Унарна операція
                tree = tree.getright()
    return varset


def forminit(tracks):
    """Для кожної траси утворює список операторів присвоювання початкових
     значень її змінним. Повертає список таких списків."""
    initlist = []
    for track in tracks:
        varass = set()  # Змінні, яким на трасі раніше присвоювалися значення
        n = 0
        nel = len(track)
        inittr = []
        varinit = set()
        for el in track:
            n += 1
            if n == 1:
                # Початкова КТ
                pass
            elif n == nel:
                # Кінцева КТ
                pass
            else:
                var = ""
                typel = trackeltype(el)
                if typel == 0:
                    # Умова переходу
                    expr = el
                else:
                    # Оператор присвоювання
                    ass = assignment(el)
                    var = ass[0]
                    expr = ass[1]
                varset = findvarset(expr)
                if typel >= 2:
                    varset.add(var)
                for vare in varset:
                    if not vare in varass:
                        varinit.add(vare)
                if typel > 0:
                    varass.add(var)
        for var in varinit:
            if var in varass:
                inittr.append(var + " = " + var + "0")
        initlist.append(inittr)
    return initlist


def substvartree(tree, vdict):
    """Підставляє значення змінних зі словника vdict у вираз, заданий деревом tree.
    Рекурсивна функція."""
    if type(tree) is str:
        if identifier(tree):
            # Змінна
            if vdict.get(tree, -1) != -1:
                expr = vdict[tree]
                return expr
            return tree
        elif tree == '0':
            return tree
    elif type(tree) is int:
        return tree
    op = tree.getop()
    if tree.unary():
        rt = tree.getright()
        newrt = substvartree(rt, vdict)
        newtree = createuntree(op, newrt)
        return newtree
    else:
        # Бінарна операція
        lt = tree.getleft()
        rt = tree.getright()
        newlt = substvartree(lt, vdict)
        newrt = substvartree(rt, vdict)
        newtree = createtree(op, newlt, newrt)
        return newtree


def formcondcorr(tracks, symvar, cpdictctrees):
    """На базі списку трас tracks будує список vconds умов їх коректності
    у вигляді списку об'єктів класу Implication.
    Функція використовує список initvar початкових значень змінних трас
    і словник cpdictcond умов в контрольних точках програми.
    Змінює список symvar."""
    vconds = []
    ntracks = len(tracks)
    for i in range(ntracks):
        track = tracks[i]
        vardict = symvar[i]

        icp = track[0]
        ictree = cpdictctrees[icp]
        trackcond = substvartree(ictree, vardict)

        ltrack = len(track)
        for j in range(1, ltrack - 1):
            # Переглядаємо оператори присвоювання та умови переходу
            op = track[j]
            pair = assignment(op)
            if len(pair) == 2:
                # Оператор присвоювання
                var = pair[0]
                expr = pair[1]
                etree = exprtree(expr,"a")
                exprsub = substvartree(etree, vardict)
                vardict[var] = exprsub
            else:
                # Умова переходу
                optree = exprtree(op, "b")
                condtree = substvartree(optree, vardict)
                trackcond = createtree("and", trackcond, condtree)
        ecp = peek(track)
        econd = cpdictctrees[ecp]
        econdtree = substvartree(econd, vardict)
        trackconj = treetocon(trackcond)
        econdconj = treetocon(econdtree)
        imp = Implication(trackconj, econdconj)
        vconds.append(imp)
    return vconds


def forminitvartrees(initvar):
    """Cписок initvar початкових значень змінних трас перетворює
    у список словників. Словники відповідають трасам.
    Кожен словник задає початкові значення змінних на трасі деревами виразів."""
    vardictlist = []
    for asslist in initvar:
        dictvar = {}
        for ass in asslist:
            pair = assignment(ass)
            var = pair[0]
            val = pair[1]
            tree = exprtree(val)
            dictvar[var] = tree
        vardictlist.append(dictvar)
    return vardictlist


def formcondcorr2(tracks, initvartree, cpdictcond):
    """Утворює список умов коректності трас зі списку tracks.
    При цьому застосвується список словників
    початкових значень змінних initvartree
    та словник умов в контрольних точках cpdictcond."""
    vconds = []
    ntracks = len(tracks)
    for i in range(ntracks):
        track = tracks[i]
        par = initvartree[i]


def formdict_termtrees(dicttermexpr):
    """Утворює словник з виразів завершення трас у вигляді дерев."""
    dicttermtrees = {}
    for cp in dicttermexpr:
        termexpr = dicttermexpr[cp]
        termtree = exprtree(termexpr)
        dicttermtrees[cp] = termtree
    return dicttermtrees


def formtermcond(tracks, vcimps, initvar, endvar, cpdictctrees, dicttermtrees):
    """Утворює список умов завершення трас у вигляді дерев.
    tracks - це список трас.
    vcimps - це список умов коректності трас.
    initvar - це список початкових значень змінних на трасах.
    endvar - це список кіцевих значень змінних на трасах.
    cpdictctrees - це словник умов в контрольних точках.
    dicttermtrees - це словник виразів завершення (у вигляді дерев)
    в контрольних точках."""
    termconds = []
    n = 0
    for track in tracks:
        n += 1
        cpi = track[0]
        if cpi == "I":
            termconds.append("")
            continue
        ltrack = len(track)
        cpe = track[ltrack - 1]
        if cpe == "E":
            termconds.append("")
            continue
                                                    # track - це шлях між двома контрольними точками циклів
        imp = vcimps[n - 1]
        antimp = imp.getant()
        newant = copyconj(antimp)

        ivar = initvar[n - 1]
        itermtree = dicttermtrees[cpi]              # Вираз завершення в початковій КТ
        initval = substvartree(itermtree, ivar)     # Вираз завершення в початковій КТ з початковими значеннями змінних

        evar = endvar[n - 1]
        etermtree = dicttermtrees[cpe]              # Вираз завершення в кінцевій КТ
        endval = substvartree(etermtree, evar)
        newtree = createtree("-", initval, endval)
        newpoly = treetopoly(newtree)
        normpoly = newpoly.combine()
        rel = Relation(normpoly, ">")
        econj = Conjunct()
        econj.add(rel)                              # Кон'юнкція з умовою спадання значення виразу завершення

        termcond = Implication(newant, econj)
        termconds.append(termcond)
    return termconds


def conv_rellist_cond(rel_list):
    """Перетворює список відношень на їх кон'юнкцію."""
    cond = ""
    for rel in rel_list:
        if cond == "":
            cond = rel
        else:
            cond += " and " + rel
    return cond


def formcpdictctrees(cpdictconds):
    """Словник  cpdictconds списків текстових умов в КТ
    перетворює на словник дерев умов в КТ."""
    cpdictctrees = {}
    for cp in cpdictconds:
        rel_list = cpdictconds[cp]
        # Коригуємо
        # if type(rel_list) is bool:
        if cpdictconds[cp] == list():
            ctree = True
        else:
            cond = conv_rellist_cond(rel_list)
            ctree = exprtree(cond, "b")
        cpdictctrees[cp] = ctree
    return cpdictctrees


def copyvartrees(vartrees):
    """Будує копію списку значень змінних."""
    newvartrees = []
    for dvartree in vartrees:
        newdvartree = {}
        for var in dvartree:
            tree = dvartree[var]
            newtree = copytree(tree)
            newdvartree[var] = newtree
        newvartrees.append(newdvartree)
    return newvartrees


def istermcompl(dicttermexpr):
    """Визначає повноту опису завершимості програми."""
    if len(dicttermexpr) == 0:
        return False
    nlcp = 0
    nterm = 0
    for cp in dicttermexpr:
        if cp == "CP_I":
            continue
        elif cp == "CP_E":
            continue
        else:
            nlcp += 1
            if dicttermexpr[cp] != "":
                nterm += 1
    return nterm == nlcp


def formstconds(tracktconds):
    """Спрощує умови завершимості трас tracktconds."""
    stracktconds = []
    for tracktcond in tracktconds:
        if tracktcond != "":
            stracktcond = tracktcond.simplimp()
        else:
            stracktcond = ""
        stracktconds.append(stracktcond)
    return stracktconds


def symbolicEx(track, initvardict, initcondtree):
    """Здійснює символьне виконання вибраної траси track.
    initvardict - це словник символьних початкових значень її змінних.
    initcondtree - це дерево умови в її початковій КТ.
    Формує словник результуючих символьних значень змінних
    в кінцевій КТ траси і співвідношення
    між початковими параметрами траси,
    яке має місце в кінцевій КТ траси."""
    vconds = []
    vardict = initvardict.copy()
    trackcond = substvartree(initcondtree, initvardict)
    for el in track:
        # Переглядаємо оператори присвоювання та умови переходу el траси track
        pair = assignment(el)
        if len(pair) == 2:
            # Оператор присвоювання
            var = pair[0]
            expr = pair[1]
            etree = exprtree(expr,"a")
            exprsub = substvartree(etree, vardict)
            vardict[var] = exprsub
        else:
            # Умова переходу
            optree = exprtree(el, "b")
            condtree = substvartree(optree, vardict)
            trackcond = createtree("and", trackcond, condtree)
    return [vardict, trackcond]
