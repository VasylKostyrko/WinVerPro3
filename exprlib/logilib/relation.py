"""Модуль описує клас Relation
відношень стандартних поліномів з 0."""

from exprlib.arilib.polynom import altopoly, polytotree, copypoly
from exprlib.treelib.tree import createtree, treeexpr
from exprlib.arilib.distribute import distrall
from verification.common import relopcod


class Relation:
    """Клас відношень стандартних поліномів з 0."""
    def __init__(self, poly, op):
        self.poly = poly
        self.op = op
        # rel_norm(self)

    def norm(self):
        """Нормалізує поточне відношення."""
        rel = relnorm(self)
        return rel

    def getpoly(self):
        return self.poly

    def getop(self):
        return self.op

    def totree(self):
        return reltotree(self)

    def istrue(self):
        return tautology(self)

    def setpoly(self, poly):
        self.poly = poly

    def setop(self, op):
        self.op = op

    def getkey(self):
        """Визначає ключ відношення, який застосовується при впорядкуванні
        відношень у стандартній кон'юнкції."""
        op = self.getop()
        cod = relopcod(op)
        poly = self.getpoly()
        key = cod + poly.getkey()
        return key

    def compare(self, rel):
        """Порівнює поточне відношення з відношенням rel."""
        res = relcompare(self, rel)
        return res
    # --- Кінець опису класу Relation


def treetorel(tree):
    """Конвертує відношення tree з деревного представлення
    в об'єкт класу Relation."""
    op = tree.op
    if not isrelation(op):
        raise Exception("Unexpected relation operation '" + op + "'.")
    reltree = convertbase(tree)
    op = reltree.getop()
    poly = normtreerel(reltree)
    rel = Relation(poly, op)
    return rel


def isrelation(op):
    """Визначає, чи операція op дерева виразу є операцією відношення."""
    if op == "==" or op == "!=" or op == "<" or op == "<=" or op == ">" or op == ">=":
        return True
    else:
        return False


def convertbase(tree):
    """tree - це дерево відношення.
    В tree головну операцію < та <=
    замінює на операцію > та >= відповідно.
    В дереві операції позначаються без пропусків."""
    op = tree.getop()
    if isrelation(op):
        if op == "<" or op == "<=":
            # Міняємо місцями гілки дерева
            ltree = tree.getleft()
            rtree = tree.getright()
            if op == "<":
                newop = ">"
            else:
                newop = ">="
            sttree = createtree(newop, rtree, ltree)
            return sttree
        return tree
    raise Exception("Unexpected relation operation '" + op + "'.")


def normtreerel(reltree):
    """Функція будує ліву частину відношення reltree,
    переносячи його праву частину в ліву,
    застосовує дистрибутивний закон,
    приводить до стандартного полінома
    та зводить в ньому подібні члени."""
    ltree = reltree.getleft()
    rtree = reltree.getright()
    if rtree != '0':
        leftrel = createtree("-", ltree, rtree)
        ta = distrall(leftrel)
    else:
        ta = distrall(ltree)
    poly = altopoly(ta)
    newpoly = copypoly(poly)
    newpoly.combine()
    return newpoly


def reltotree(rel):
    """Cтандартне відношення rel
    перетворює в дерево виразу."""
    poly = rel.poly
    op = rel.op
    polytree = polytotree(poly)
    reltree = createtree(op, polytree, "0")
    return reltree


def relnum(op, num):
    """Визначає, чи задане число num
    знаходится у відношенні op з нулем."""
    if op == "==":
        return num == 0
    elif op == "!=":
        return num != 0
    elif op == ">":
        return num > 0
    elif op == ">=":
        return num >= 0
    return False


def tautology(rel):
    """Якщо стандартне відношення є тавтологією,
    тоді видає значення True, інакше False."""
    poly = rel.poly
    op = rel.op
    al = poly.getal()
    if len(al) == 1:
        mono = al[0]
        cf = mono.getcf()
        if cf == 0:
            if op == "==" or op == ">=":
                return True
            return False
        else:
            ml = mono.getml()
            if len(ml) == 0:
                res = relnum(op, cf)
                return res
    return False


def reltoexpr(rel):
    """Перетворює відношення з об'єкта rel класу Relation
    у текстове інфіксне представлення."""
    tree = reltotree(rel)
    expr = treeexpr(tree)
    return expr


def copyrel(rel):
    """Копіює об'єкт rel класу Relation."""
    poly = rel.getpoly()
    op = rel.getop()
    newpoly = copypoly(poly)
    newrel = Relation(newpoly, op)
    return newrel


def relcompare(rel1, rel2):
    """Порівнює відношення.
    Результат: -1 (менше), 0 (рівно), 1 (більше)."""
    op1 = rel1.getop()
    op2 = rel2.getop()
    cod1 = relopcod(op1)
    cod2 = relopcod(op2)
    if cod1 < cod2:
        return -1
    elif cod1 > cod2:
        return 1
    else:
        poly1 = rel1.getpoly()
        poly2 = rel2.getpoly()
        res = poly1.compare(poly2)
        return res


def relnorm(rel):
    """Нормалізує стандартне відношення rel."""
    newrel = copyrel(rel)
    rel_norm(newrel)
    return newrel

def rel_norm(rel):
    """Нормалізує стандартне відношення strel."""
    relop = rel.op
    if relop == "==" or relop == "!=":
        poly = rel.getpoly()
        if poly.len() > 0:
            mono = poly.getmono(0)
            if mono.getcf() < 0:
                poly.chsign()
        poly.combine()


def reltautology(rel):
    """Обчислює тавтологію."""
    if type(rel) is bool:
        return rel
    op = rel.getop()
    poly = rel.getpoly()
    polylen = poly.len()
    if polylen == 0:
        if op == "==":
            return True
        if op == ">=":
            return True
        if op == ">":
            return False
        if op == "!=":
            return False
    return rel
