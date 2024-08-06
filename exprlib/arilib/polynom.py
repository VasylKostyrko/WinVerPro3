"""Визначає клас стандартних многочленів
та операцій над ними."""

from exprlib.arilib.monom import Monom, treetomono, similar, monototree, copymono
from exprlib.treelib.tree import createtree


class Polynom:
    """Визначає клас стандртних многочленів
    Стандртний многочлен - це список стандартних одночленів,
    як об'єктів класу Monom,
    впорядкованих за списком їх нечислових множників."""
    def __init__(self):
        self.al = []

    def add(self, el):
        # el - це об'єкт класу Monom
        if el.cf == 0:
            return
        self.al.append(el)
        self.sort()

    def sort(self):
        if len(self.al) > 1:
            self.al.sort(key=lambda el: el.getkey())

    def tostring(self):
        """Стандартний поліном
        перетворює в інфіксну форму."""
        p = altostring(self)
        return p

    def combine(self):
        """У стандартному поліномі
        зводить подібні члени."""
        polynom = combinesim(self)
        poly = combine0(polynom)
        poly.sort()
        return poly

    def getal(self):
        return self.al

    def len(self):
        return len(self.al)

    def getmono(self, n):
        """Видає n-ий член полінома (n >= 0)."""
        return self.al[n]

    def chsign(self):
        """Змінює знак полінома."""
        changesign(self)

    def delmono(self, n):
        # знищує n-ий доданок стандартного полінома
        del self.al[n]

    def compare(self, poly):
        """Порівнює поточний поліном з поліномом poly.
        Результат: -1 (менше), 0 (рівно), 1 (більше)."""
        res = polycompare(self, poly)

    def getkey(self):
        """Визначає ключ поточного полінома,
        який застосовується при впорядуванні
        стандартних поліномів."""
        al = self.getal()
        key = ""
        n = 0
        for mono in al:
            n += 1
            monokey = mono.getkey()
            if n == 1:
                key += monokey()
            else:
                key += "+" + monokey()
        return key
    # --- Кінець опису класу Polynom


def copypoly(poly):
    """Створює копію полінома poly."""
    al = poly.getal()
    newpoly = Polynom()
    for mono in al:
        newmono = copymono(mono)
        newpoly.add(newmono)
    return newpoly


def combinesim(polynom):
    """Зводить подібні одночлени в стандартному поліномі poly."""
    poly = copypoly(polynom)
    n = poly.len()
    if n <= 1:
        return poly
    mono = poly.getmono(0)
    i = 1
    while i <= n - 1:
        mono2 = poly.getmono(i)
        if similar(mono, mono2):
            cf1 = mono.getcf()
            cf2 = mono2.getcf()
            cf = cf1 + cf2
            mono.setcf(cf)
            poly.delmono(i)
            n -= 1
        else:
            mono = mono2
            i += 1
    return poly


def combine0(polynom):
    """В поліномі polynom усуває нульові одночлени."""
    poly = copypoly(polynom)
    n = poly.len()
    if n == 1:
        return poly
    i = 1
    while i <= n - 1:
        mono = poly.getmono(i)
        cf = mono.getcf()
        if cf == 0:
            poly.delmono(i)
            n -= 1
        else:
            i += 1
    return poly


def altostring(poly):
    """Стандртний поліном (об'єкт класу Polynom)
    перетворює в інфіксне представлення."""
    mlist = poly.al
    n = len(mlist)
    if n == 0:
        return "0"
    p = ""
    i = 0
    for mono in mlist:
        i += 1
        if i == 1:
            # Перший одночлен
            if mono.cf < 0:
                sign = "-"
                mono.cf = -mono.cf
            else:
                sign = ""
            p = sign + mono.tostring()
        else:
            # Наступні одночлени
            if mono.cf < 0:
                sign = "-"
                mono.cf = -mono.cf
            else:
                sign = "+"
            p += " " + sign + " " + mono.tostring()
    return p


def altopoly(listadds):
    """Список простих одночленів listadds
    (об'єктів класу Tree)
    перетворює в об'єкт класу Polynom."""
    al = Polynom()
    n = len(listadds)
    if n == 0:
        return al
    for ta in listadds:
        ml = treetomono(ta)
        al.add(ml)
    return al


def treetopoly(tree):
    """Представлений деревом поліном tree
    перетворює в об'єкт класу Polynom.
    Реалізується backtrack'інгом
    при нисхідному лівосторонньому обході
    дерева виразу."""
    poly = Polynom()
    stack = []
    stacksign = []
    sign = 1
    while True:
        forward = True
        # прямий хід
        while forward:
            if (type(tree) is str) or (type(tree) is int):
                ml = Monom()
                ml.add(tree)
                if sign < 0:
                    ml.cf = -ml.cf
                poly.add(ml)
                forward = False
            elif tree.leaf():
                ml = treetomono(tree)
                if sign < 0:
                    ml.cf = -ml.cf
                poly.add(ml)
                forward = False
            elif tree.unary():
                ml = treetomono(tree)
                if sign < 0:
                    ml.cf = -ml.cf
                poly.add(ml)
                forward = False
            elif tree.getop() == "*":
                ml = treetomono(tree)
                if sign < 0:
                    ml.cf = -ml.cf
                poly.add(ml)
                forward = False
            else:
                # tree - це сума або різниця
                lt = tree.getleft()
                stack.append(tree)
                stacksign.append(sign)
                tree = lt
        # зворотний хід
        if len(stack) == 0:
            return poly
        tree = stack.pop()
        sensign = stacksign.pop()
        op = tree.getop()
        sign = 1
        if op == "-":
            sign = -1
        sign = sign * sensign
        rt = tree.getright()
        tree = rt


def polytotree(poly):
    """Стандартний поліном poly (об'єкт класу Polynom)
    функція перетворює на дерево виразу."""
    tree = 0
    al = poly.getal()
    m = 0
    for mono in al:
        m += 1
        if m == 1:
            monotree = monototree(mono)
            tree = monotree
        else:
            cf = mono.getcf()
            newop = "+"
            if cf < 0:
                newop = "-"
            monotree = monototree(mono, newop)
            tree = createtree(newop, tree, monotree)
    return tree


def changesign(poly):
    """Змінює знаки у всіх одночленів полінома poly.
    Змінює аргумент."""
    nal = poly.len()
    for n in range(nal):
        mono = poly.getmono(n)
        cf = mono.getcf()
        newcf = -cf
        mono.setcf(newcf)


def polycompare(poly1, poly2):
    """Порівнює стандартні поліноми.
    Результат: -1 (менше), 0 (рівно), 1 (більше)."""
    n1 = poly1.len()
    n2 = poly2.len()
    if n1 == 0 and n2 == 0:
        return 0
    elif n1 == 0:
        return -1
    for n in range(n1):
        mono1 = poly1.getmono(n)
        if n >= n2:
            return 1
        else:
            mono2 = poly2.getmono(n)
            comp = mono1.compare(mono2)
            if comp != 0:
                return comp
    if n1 == n2:
        return 0
    else:
        return -1
