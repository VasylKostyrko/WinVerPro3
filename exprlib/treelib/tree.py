"""Побудова дерев виразів"""

from polish import operation, expr_polish, priority, unary


class Tree():
    """Клас дерев виразів."""
    def __init__(self):
        self.op = None
        self.lt = None
        self.rt = None

    def getop(self):
        return self.op

    def getleft(self):
        return self.lt

    def getright(self):
        return self.rt

    def setop(self, op):
        self.op = op

    def setleft(self, left):
        self.lt = left

    def setright(self, right):
        self.rt = right

    def unary(self):
        # Чи операція, розташована в корені дерева, є унарною?
        return self.lt is None

    def binary(self):
        # Чи операція, розташована в корені дерева, є бінарною?
        return self.lt is not None

    def leaf(self):
        # Чи корінь дерева є листком?
        res = self.lt is None and self.rt is None
        return res

    # def equalto(self, etree):
    #     # Чи рівне поточне дерево заданому дерево etree?
    #     res = equaltree(self, etree)
    #     return res
    #
    # def isarexpr(self):
    #     # Чи дерево представляє арифметичний вираз
    #     res = istarexpr(self)
    #     return res

    def tostring(self):
        res = treeexpr(self)
        return res


def createtree(op, lt, rt):
    """Утворює дерево з бінарною операцією op і піддеревами lt та rt."""
    etree = Tree()
    etree.setop(op)
    etree.setleft(lt)
    etree.setright(rt)
    return etree


def poltree(polexpr):
    """Перетворює вираз expr,
    заданий в оберненому польському запису,
    на дерево виразу.
    Служить ще одним конструктором класу Tree."""
    if len(polexpr) == 1:
        return polexpr[0]
    etree = Tree()
    stack = []
    for el in polexpr:
        if operation(el):
            etree = Tree()
            op = str.strip(el)
            etree.setop(op)
            right = stack.pop()
            if not unary(el):
                if len(stack) > 0:
                    left = stack.pop()
                    etree.setleft(left)
            etree.setright(right)
            stack.append(etree)
        else:
            stack.append(el)
    return etree


def exprtree(expr, mode="a"):
    """Перетворює вираз expr, заданий у інфіксній формі, в дерево виразу
    через обернений польський запис. Служить ще одним конструктором класу Tree.
    Якщо mode = a, тоді у виразі можуть
    бути лише арифметичні операції,
    якщо mode = r, тоді головною операцією виразу
    є операція відношення, а її аргументами -
    арифметичні вирази.
    Якщо mode = b, тоді у виразі
    допускаються також логічні операції."""
    polexpr = expr_polish(expr, mode)
    etree = poltree(polexpr)
    return etree


def treeexpr(etree, fop="(", lr="lt"):
    """Перетворює дерево виразу etree у вираз інфіксної форми.
    fop - це операція батьківського виразу.
    lr - її лівий операнд ("lt") або правий ("rt").
    Рекурсивна функція."""
    if (etree is True) or (etree is False):
        return str(etree)
    if type(etree) is str:
        return etree
    if type(etree) is int:
        return str(etree)
    else:
        op = etree.getop()
        lt = etree.getleft()
        rt = etree.getright()
        if (lt is None) and (rt is None):
            return op
        if (op == "True") or (op == "False"):
            return op
        if etree.unary():
            # Унарна операція
            subtree = op + treeexpr(rt, op, "rt")
            if priority(fop) > priority(op):
                return "(" + subtree + ")"
            else:
                return subtree
        else:
            # Бінарна операція
            lt = etree.getleft()
            if op == "*" and type(lt) is int:
                if lt == 1:
                    return treeexpr(rt)
                elif lt == -1:
                    return "-" + treeexpr(rt)
            op = " " + op + " "
            subtree = treeexpr(lt, op, "lt") + op + treeexpr(rt, op, "rt")
            if fop == "-":
                return subtree
            elif priority(fop) > priority(op):
                return "(" + subtree + ")"
            elif fop == "-":
                if op == "*":
                    subtree = treeexpr(lt, op, "lt") + op + treeexpr(rt, op, "rt")
                else:
                    if lr == "lt":
                        subtree = treeexpr(lt, op, "lt") + op + treeexpr(rt, op, "rt")
                    else:
                        subtree = "(" + treeexpr(lt, op, "lt") + op + treeexpr(rt, op, "rt") + ")"
                return subtree
            else:
                return subtree


def copytree(etree):
    """Копіює дерево виразу etree.
    У вузлах дерева можуть бути: ціле число, текстовий рядок або
    словник з ключами "op", "lt" та "rt".
    Значення ключа "op" - текстове і задає операцію.
    Операції - бінарні та унарні.
    Словник бінарної операції має ключі "lt" та "rt".
    Словник з унарною операцією має ключ "rt", але не має ключа "lt".
    Значення ключів "lt" та "rt" позначають аргументи операції
    і задають цілі числа, змінні або словники.
    Рекурсивна функція."""
    typ = type(etree)
    if typ is int or typ is str:
        return etree
    op = etree.getop()
    if op == "or" or op == "and" or op == "*" or op == "<" or op == "<=" \
            or op == ">" or op == ">=" or op == "==" or op == "!=":
        lt = etree.getleft()
        rt = etree.getright()
        newlt = copytree(lt)
        newrt = copytree(rt)
        newtree = createtree(op, newlt, newrt)
        return newtree
    if op == "not":
        rt = etree.setright()
        newrt = copytree(rt)
        newtree = createtree(op, None, newrt)
        return newtree
    if op == "+" or op == "-":      # or op == " + " or op == " - ":
        rt = etree.getright()
        newrt = copytree(rt)
        if etree.unary():
            # Унарна операція + -
            newtree = createtree(op, None, newrt)
            return newtree
        else:
            # Бінарна операція + -
            lt = etree.getleft()
            newlt = copytree(lt)
            newtree = createtree(op, newlt, newrt)
            return newtree


def createuntree(op, rt):
    """Утворює дерево з унарної операції op та піддерева rt."""
    etree = Tree()
    etree.setop(op)
    etree.setright(rt)
    return etree
