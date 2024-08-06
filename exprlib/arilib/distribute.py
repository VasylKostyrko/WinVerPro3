"""Модуль перетворює довільне дерево виразу
в дерево простого полінома, застосовуючи до нього
закон дистрибутивності."""


from exprlib.treelib.tree import Tree, createtree, copytree


def treeaddl(etree):
    """Представлений деревом арифметичний вираз etree
    перетворює в список доданків.
    Кожен доданок є або числом, або змінною, або добутком.
    Проте, доданки не обов'язково є простими одночленами:
    їх множниками можуть бути суми та різниці.
    Лівостороннім нисхідним обходом дерева
    реалізує backtracking."""
    if type(etree) is Tree:
        tree = copytree(etree)
    elif type(etree) is list:
        tree = etree[0]
    else:
        tree = etree
    adds = []
    stack = []
    while True:
        # Прямий хід
        if type(tree) is str or type(tree) is int:
            adds.append(tree)
            # Зворотній хід
            if len(stack) > 0:
                tree = stack.pop()
            else:
                return adds
        else:
            op = tree.getop()
            if (op == "+") or (op == "-"):
                if tree.unary():
                    # Унарна операція + або -
                    rt = tree.getright()
                    tree = rt
                else:
                    # Операція додавання чи віднімання
                    rt = tree.getright()
                    if op == "-":
                        coef = createtree("-", None, "1")
                        newtree = createtree("*", coef, rt)
                        stack.append(newtree)
                    else:
                        stack.append(rt)
                    lt = tree.getleft()
                    tree = lt
            else:
                # Операція множення
                adds.append(tree)
                # Зворотній хід
                if len(stack) > 0:
                    tree = stack.pop()
                else:
                    return adds


def distr(tree):
    """tree - це дерево арифметичного виразу, який є добутком, числом або змінною.
    Якщо функція знаходить в ньому бінарну операцію + (або -),
    тоді перетворює його в 2-елементний список, реалізуючи відношення дистрибутивності
    Кожен едемент цього списку задається деревом.
    Операція віднімання змінюється на операцію додавання,
    а у від'ємник вводиться ще один множник: -1.
    Якщо співвідношення дистрибутивності застосовувалося,
    тоді результат є списком з двох дерев, інакше - пустим списком.
    В дереві виразу позначення операцій не містить пропусків."""
    multl = []
    multr = []
    add = tree
    if (type(add) is str) or (type(add) is int):
        return []
    while True:
        # Прямий хід
        if (type(add) is str) or (type(add) is int):
            if len(multr) == 0:
                return []
            appnot1(multl, add)
            add = multr.pop()
            continue
        op = add.getop()
        if op == "*":
            lt = add.getleft()
            rt = add.getright()
            appnot1(multr, rt)
            add = lt
            continue
        if op == "+" or op == "-":
            if add.unary():
                # Унарна операція + -
                mult = unopcollaps(add)
                if mult.binary():
                    add = mult
                else:
                    multl.append(mult)
                    if len(multr) == 0:
                        return []
                    add = multr.pop()
                continue
            else:
                # Бінарна операція + -
                lt = add.getleft()
                rt = add.getright()
                if len(multl) > 0:
                    lmult = multtree(multl)
                    lefttree = createtree("*", lmult, lt)
                    righttree = createtree("*", lmult, rt)
                else:
                    lefttree = lt
                    righttree = rt
                if len(multr) > 0:
                    rmult = multtree(multr)
                    ltree = createtree("*", lefttree, rmult)
                    rtree = createtree("*", righttree, rmult)
                    lefttree = ltree
                    righttree = rtree
                if op == "-":
                    coef = createtree("-", None, "1")
                    newtree = createtree("*", coef, righttree)
                    righttree = newtree
                return [lefttree, righttree]
        else:
            # Змінна або число
            appnot1(multl, add)
            # Зворотній хід
            if len(multr) == 0:
                return []
            add = multr.pop()


def multtree(mult):
    """Непустий список множників mult перетворює в дерево виразу.
    Рекурсивна функція."""
    nel = len(mult)
    if nel == 1:
        # Останній множник одночлена
        tree = mult[0]
    else:
        lt = mult[0]
        rt = multtree(mult[1:])
        tree = createtree("*", lt, rt)
    return tree


def appnot1(listel, el):
    """В список множників listel додає елемент el,
    якщо він є нетривіальним множником (тобто, 1)."""
    if el != '1':
        listel.append(el)


def unopcollaps(add):
    """Усуває зайві унарні операції у дереві виразу add,
    головною операцією якого є унарна операція + або -.
    Повертає одночлен, який може бути:
    а) змінною;
    б) цілим числом;
    в) деревом з головною унарною операцією - (мінус) та цілим числом в ролі її аргумента;
    г) деревом з головною бінарною операцією * та виразом -1 в ролі її першого аргумента."""
    rt = None
    exprsign = "+"
    res = copytree(add)
    while True:
        if type(res) == Tree:
            op = res.getop()
            rt = res.getright()
            if res.unary():
                # Унарна операція
                # Змінюємо знак операції і повторюємо аналіз
                if op == "-":
                    if exprsign == "+":
                        exprsign = "-"
                    else:
                        exprsign = "+"
                res = rt
                continue
            else:
                # Бінарна операція *, +, - або число, або змінна
                if exprsign == "-":
                    coef = createtree("-", None, "1")
                    res = createtree("*", coef, rt)
                return res
        else:
            # число або змінна
            if exprsign == "-":
                if str.isnumeric(res):
                    res = createtree("-", None, res)
                else:
                    coef = createtree("-", None, "1")
                    res = createtree("*", coef, rt)
            return res


def distrall(tree):
    """Представлений деревом арифметичний вираз tree перетворює
    на список доданків, кожен з яких є деревом і задає одночлен."""
    adds = treeaddl(tree)
    changed = True
    while changed:
        changed = False
        nel = len(adds)
        for n in range(nel):
            add = adds[n]
            listadds = distr(add)
            if len(listadds) > 0:
                adds[n] = listadds[0]
                adds.insert(n + 1, listadds[1])
                changed = True
                break
    return adds
