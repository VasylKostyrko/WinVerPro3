"""Визначає клас Conjunct для представлення
кон'юнкції ряду стандартних відношень.
Стандартна кон'юнкція -
це кон'юнкція ряду об'єктів класу Relation."""

from exprlib.logilib.relation import Relation, isrelation, treetorel, reltotree, copyrel
from exprlib.treelib.tree import Tree, createtree
from exprlib.logilib.relation import reltoexpr
from exprlib.arilib.polynom import Polynom
from exprlib.arilib.monom import copymono


class Conjunct:
    """Клас стандартних кон'юнкцій."""
    def __init__(self):
        self.con = []

    def add(self, rel):
        lcon = self.con
        lcon.append(rel)

    def getcon(self):
        return self.con

    def setcon(self, con):
        self.con = con

    def getrel(self, n):
        con = self.con
        return con[n]

    def len(self):
        return len(self.con)

    def delcon(self, n):
        # знищує n-ий кон'юнкт стандартної кон'юнкції
        del self.con[n]

    def empty(self):
        return len(self.con) == 0

    def contains(self, rel):
        return relinconj(self, rel)

    def sort(self):
        """Впорядковує відношення у списку con поточного об'єкта."""
        if len(self.con) > 1:
            self.con.sort(key=lambda el: el.getkey())

    def compare(self, conj):
        """Порівнює поточний об'єкт з об'єктом conj класу Conjunct/
        Результат: -1 (менше), 0 (рівно), 1 (більше)."""
        res = conjcompare(self, conj)
        return res
    # --- Кінець опису класу Conjunct


def copyconj(conj):
    """Копіює об'єкт conj класу Conjunct."""
    newconj = Conjunct()
    rellist = conj.getcon()
    for rel in rellist:
        newrel = copyrel(rel)
        newconj.add(newrel)
    return newconj


def treetocon(tree):
    """Дерево логічного виразу tree,
    старші операції якого є кон'юнкціями відношень,
    перетворює у стандартизовану кон'юнкцію.
    Реалізується через backtracking."""
    stack = []
    conj = Conjunct()
    logtree = tree

    # Прямий хід
    while True:
        op = logtree.getop()
        if op == "and":
            ltree = logtree.getleft()
            rtree = logtree.getright()
            stack.append(rtree)
            logtree = ltree
        elif isrelation(op):
            # відношення
            rel = treetorel(logtree)
            conj.add(rel)

            # Зворотній хід
            if len(stack) == 0:
                return conj
            logtree = stack.pop()
        else:
            raise Exception("Unexpected operation '" + op + "' in conjunction.")


def contotree(conj):
    """Стандартну кон'юнкцію перетворює в дерево виразу
    (об'єкт класу Tree)."""
    if conj.empty():
        return True
    tree = Tree()
    list = conj.getcon()
    n = 0
    for rel in list:
        n += 1
        reltree = reltotree(rel)
        if n == 1:
            tree = reltree
        else:
            tree = createtree("and", tree, reltree)
    return tree


def relinconj(conj, rel):
    """Визначає, чи відношення rel є одним з кон'юнктів
    об'єкта conj класу Conjuct."""
    relex = reltoexpr(rel)
    listcon = conj.getcon()
    for con in listcon:
        conex = reltoexpr(con)
        if relex == conex:
            return True
    return False


def normconj(conj):
    """Нормалізує стандартну кон'юнкцію
    (об'єкт класу Conjunct)."""
    newconj = Conjunct()
    rellist = conj.getcon()
    for rel in rellist:
        poly = rel.getpoly()
        op = rel.getop()
        rpoly = poly.combine()  # Зводимо подібні члени
        newrel = Relation(rpoly, op)
        if op == "==" or op == "!=":
            # Змінимо знак, якщо коефіцієнт першого члена < 0
            if rpoly.len() > 0:
                mono = rpoly.getmono(0)
                cf = mono.getcf()
                if cf < 0:
                    al = rpoly.getal()
                    newpoly = Polynom()
                    for mono in al:
                        newmono = copymono(mono)
                        cf = mono.getcf()
                        newcf = -cf
                        newmono.setcf(newcf)
                        newpoly.add(newmono)
                else:
                    newpoly = rpoly
            else:
                newpoly = rpoly
        else:
            newpoly = rpoly
        if newpoly.len() == 0:
            if op == "==":
                newrel = True
            elif op == "!=":
                newrel = False
            elif op == ">=":
                newrel = True
            else:
                # op == ">":
                newrel = False
            if not newrel:
                newconj = False
                return newconj
        else:
            newrel.setpoly(newpoly)
            newconj.add(newrel)
    if type(newconj) is Conjunct:
        if newconj.len() == 0:
            newconj = True
    return newconj


def conjcompare(conj1, conj2):
    """Порівнює об'єкти класу Conjunct.
    Результат: -1 (менше), 0 (рівно), 1 (більше)."""
    n1 = conj1.len()
    n2 = conj2.len()
    if n1 == n2:
        return 0
    for n in range(n1):
        if n >= n2:
            return 1
        rel1 = conj1.getrel(n)
        rel2 = conj2.getrel(n)
        res = rel1.compare(rel2)
        if res != 0:
            return res
    if n1 == n2:
        return 0
    else:
        return -1


def con_rel_list(conj):
    """Перетворює кон'юнкцію у список відношень."""
    rellist = []
    n = conj.len()
    for n in range(n):
        rel = conj.getrel(n)
        rellist.append(rel)
    return rellist
