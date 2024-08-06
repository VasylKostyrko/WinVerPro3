"""Визначає клас Implication стандартних імплікацій.
Стандартна імплікація представляє собою пару
об'єктів класу Conjunct."""


from exprlib.logilib.conjunct import Conjunct, treetocon, contotree, normconj, copyconj
from exprlib.treelib.tree import createtree, exprtree, treeexpr
from exprlib.logilib.relation import tautology, copyrel


class Implication:
    """Клас стандартних імплікацій."""
    def __init__(self, ant, cons):
        if type(ant) is not Conjunct:
            raise Exception("Implication's antecedent is not of type Conjunct.")
        if type(ant) is not Conjunct:
            raise Exception("Implication's consequent is not of type Conjunct.")
        self.ant = ant
        self.cons = cons

    def getant(self):
        return self.ant

    def getcons(self):
        return self.cons

    def istrue(self):
        cons = self.cons
        con = cons.con
        if len(con) == 0:
            return True
        return False

    def totree(self):
        return imptree(self)

    def tostring(self):
        return impexpr(self)

    def simplimp(self):
        return simplifyimp(self)

    def setant(self, ant):
        self.ant = ant

    def setcons(self, cons):
        self.cons = cons
    # --- Кінець опису класу Implication


def treeimp(tree):
    """Дерево виразу tree перетворює
    на об'єкт класу Implication."""
    op = tree.getop()
    if op != "->":
        raise Exception("Root of tree is: '" + op + "',  not implication.")
    ltree = tree.getleft()
    rtree = tree.getright()
    conja = treetocon(ltree)
    conjc = treetocon(rtree)
    impl = Implication(conja, conjc)
    newimp = normimp(impl)
    return newimp


def imptree(imp):
    """Стандартну імплікацію (об'єкт класу Implication)
     перетворює на дерево виразу."""
    ant = imp.getant()
    cons = imp.getcons()
    treea = contotree(ant)
    treec = contotree(cons)
    op = "->"
    tree = createtree(op, treea, treec)
    return tree


def simplifyimp(imp):
    """Спрощує імплікацію (об'єкт класу Implication),
    усуваючи з її консеквента ті кон'юнкти (об'єкти класу Relation),
    які є тавтологіями або є в її антецеденті."""
    nimp = normimp(imp)
    rimp = deltautolog(nimp)
    simp = cutconcons(rimp)
    return simp


def deltautolog(stimp):
    """Спрощує стандартну імплікацію
    (об'єкт класу Implication),
    усуваючи з її консеквента ті кон'юнкти
    (об'єкти класу Relation),
    які є тавтологіями."""
    imp = impconst(stimp)
    if type(imp) is bool:
        return imp
    cons = imp.getcons()
    conj = cons.getcon()
    newcons = Conjunct()
    for rel in conj:
        if not tautology(rel):
            newrel = copyrel(rel)
            newcons.add(newrel)
    ant = imp.getant()
    newant = copyconj(ant)
    if newcons.len() == 0:
        newcons = True
    newimp = Implication(newant, newcons)
    return newimp


def cutconcons(imp):
    """Спрощує імплікацію
    (об'єкт класу Implication),
    усуваючи з її консеквента ті кон'юнкти
    (об'єкти класу Relation),
    які присутні також в її антецеденті."""
    if type(imp) is bool:
        return imp
    ant = imp.getant()
    cons = imp.getcons()
    if type(cons) is bool:
        if cons:
            return True
        return imp
    conj = cons.getcon()
    newcons = Conjunct()
    for rel in conj:
        if not ant.contains(rel):
            newrel = copyrel(rel)
            newcons.add(newrel)
    newant = copyconj(ant)
    newimp = Implication(newant, newcons)
    return newimp


def exprimp(expr):
    """Перетворює імплікацію з текстового представлення
    в об'єкт класу Implication."""
    tree = exprtree(expr, "b")
    imp = treeimp(tree)
    return imp


def impexpr(imp):
    """Об'єкт imp класу Implication перетворює на імплікацію
     в текстовому представленні."""
    if type(imp) is bool:
        return imp
    if imp.istrue():
        return True
    tree = imptree(imp)
    expr = treeexpr(tree)
    return expr


def normimp(imp):
    """В об'єкті imp класу Implication
    нормалізує поліноми відношень."""
    ant = imp.getant()
    cons = imp.getcons()
    newant = normconj(ant)
    newcons = normconj(cons)
    newimp = Implication(newant, newcons)
    return newimp


def isitimplication(expr):
    """Перевіряє, чи вибраний вираз може бути імплікацією."""
    if type(expr) is bool:
        return False
    if type(expr) is str:
        pos = expr.find(" -> ")
        if pos == -1:
            return False
        ant = expr[:pos - 1]
        cons = expr[pos + 4]
        if ant[:3] == "CP_" or cons[:3] == "CP_":
            # Це може бути трасою
            return False
        return True
    else:
        return False


def impconst(imp):
    """Якщо імплікація imp є тавтологією, то перетворює її на константу."""
    ant = imp.getant()
    cons = imp.getcons()
    if type(cons) is bool:
        if cons:
            return True
    if type(ant) is bool:
        if not ant:
            return True
    if type(cons) is bool and type(ant) is bool:
        if ant and not cons:
            return False
    return imp


def copyimp(imp):
    """Утворює копію об'єкта imp класу Implication."""
    ant = imp.ant
    cons = imp.cons
    newant = copyconj(ant)
    newcons = copyconj(cons)
    newimp = Implication(newant, newcons)
    return newimp
