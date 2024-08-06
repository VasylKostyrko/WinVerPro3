"""Визначає клас стандартних одночленів
та операцій над ними."""


from exprlib.treelib.tree import createtree


class Monom:
    """Визначає клас списків множників.
    Множниками можуть бути змінні та числа,
    Список множників не може бути пустим,
    але може складатися лише з одного числа
    або однієї змінної.
    При додаванні нового числового множника
    він домножується на коефіцієнт одночлена.
    Коефіцієнт може бути додатнім, від'ємним
    цілим числом або нулем.
    При додаванні змінної всі змінні
    впорядковуються за алфавітом."""

    def __init__(self):
        self.cf = 1
        self.ml = []

    def add(self, el):
        if type(el) is int:
            self.cf = self.cf * el
            if self.cf == 0:
                self.ml = []
        elif type(el) is str:
            self.ml.append(el)
            self.ml.sort()

    def isconst(self):
        return len(self.ml) == 0

    def getcf(self):
        return self.cf

    def setcf(self, cf):
        self.cf = cf
        if cf == 0:
            self.ml = []

    def getml(self):
        return self.ml

    def tostring(self):
        # перетворює стандартний одночлен на вираз
        # в інфіксному представленні
        p = monotostring(self)
        return p

    def getkey(self):
        """Визначає ключ одночлена, який застосовується
        при впорядкуванні одночленів полінома."""
        p = ""
        lm = len(self.ml)
        for i in range(lm):
            m = self.ml[i]
            p += "*"
            p += m
        return p

    def compare(self, mono):
        """Порівнює поточний одночлен з одночленом mono.
        Результати: -1 (менше), 0 (рівно,), 1 (більше)."""
        key = self.getkey()
        monokey = mono.getkey()
        if key < monokey:
            return -1
        elif key > monokey:
            return 1
        else:
            # Одночлени відрізняються лише коефіцієнтами
            cf = self.getcf()
            monocf = mono.getcf()
            return cf < monocf
    # --- Кінець опису класу Monom


def createml(mlist):
    """Утворює об'єкт класу Monom
    зі списку множників mlist."""
    ml = Monom()
    for m in mlist:
        ml.add(m)
    return ml


def copymono(mono):
    """Утворює копію одночлена mono."""
    cf = mono.getcf()
    ml = mono.getml()
    newmono = createml(ml)
    newmono.setcf(cf)
    return newmono


def similar(mlt1, mlt2):
    """Визначає, чи подібні одночлени, які задаються
    об'єктами mlt1 та mlt2 класу Monom."""
    mc1 = mlt1.isconst()
    mc2 = mlt2.isconst()
    if mc1 and mc2:
        # обидва одночлени є константами
        return True
    if mc1 or mc2:
        # один оденочлен є константою, а інший - ні
        return False
    # обидва одночлени не є константами
    ml1 = mlt1.getml()
    ml2 = mlt2.getml()
    n1 = len(ml1)
    n2 = len(ml2)
    if n1 != n2:
        return False
    for n in range(n1):
        el1 = ml1[n]
        el2 = ml2[n]
        if el1 != el2:
            return False
    return True


def tree_mono(tree, mult):
    """Перетворює дерево tree, яке представляє
    одночлен, в об'єкт mult класу Monom.
    Процедурі при виклику потрібно передати
    пустий об'єкт ml класу Monom.
    Рекурсивна процедура, яка запускається
    з функції treetomono."""
    if (type(tree) is str) or (type(tree) is int):
        mult.add(tree)
        return
    elif tree.unary():
        rt = tree.getright()
        op = tree.getop()
        if op == "-":
            if type(rt) is int:
                rt = -rt
            elif type(rt) is str:
                if str.isnumeric(rt):
                    rt = -int(rt)
        tree_mono(rt, mult)
        return
    else:
        lt = tree.getleft()
        tree_mono(lt, mult)
        rt = tree.getright()
        tree_mono(rt, mult)
        return


def treetomono(tree):
    """Перетворює простий одночлен tree з дерева виразу
    на стандартний одночлен (об'єкт класу Monom)."""
    mult = Monom()
    tree_mono(tree, mult)
    return mult


def mltree(ml):
    """Непустий список множників ml перетворює в дерево виразу.
    Рекурсивна функція."""
    nel = len(ml)
    if nel == 1:
        # Останній множник одночлена
        tree = ml[0]
    else:
        lt = ml[0]
        rt = mltree(ml[1:])
        tree = createtree("*", lt, rt)
    return tree


def monotostring(mono):
    """Стандартний одночлен mono (об'єкт класу Monom)
    перетворює на вираз в інфіксному представленні."""
    cf = mono.cf
    if cf == 0:
        return "0"
    lm = len(mono.ml)
    p = str(cf)
    if lm > 0:
        if mono.cf == 1:
            p = ""
        elif mono.cf == -1:
            p = "-"
    for i in range(lm):
        m = mono.ml[i]
        if p != "" and p != "-":
            p += " * "
        p += m
    return p


def monototree(mono, newop="+"):
    """Перетворює стандартний одночлен mono
    (об'єкт класу Monom) на дерево виразу.
    Якщо newcf = -1, тоді змінює знак cf."""
    cf = mono.getcf()
    if newop == "-":
        cf = -cf
    ml = mono.getml()
    tree = cf
    if len(ml) > 0:
        if cf == 1:
            el = ml[0]
    for el in ml:
        tree = createtree("*", tree, el)
    return tree

