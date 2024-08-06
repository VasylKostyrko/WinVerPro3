# -*- coding: utf8 -*-
# """Модуль призначений для зв'язку з бібліотекою z3py."""
import ctypes
from PyQt5 import QtGui
from exprlib.treelib.tree import exprtree
from verification.common import identifier


def errormsg(self, msg):
    self.lblError.setText(msg)
    user32 = ctypes.windll.user32
    height = user32.GetSystemMetrics(1)
    self.lblError.move(20, height - 90)
    self.lblError.setStyleSheet('color: red')
    self.lblError.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))


def derive_conds(conds):
    """Спробувати довести задані умови conds за допомогою бібліотеки z3py."""
    for cond in conds:
        # print(cond)
        tree = exprtree(cond, "b")
        varlist = formvarlist(tree)
        print(varlist)
        z3ex = exprz3py(tree)
        x = 1


def formvarlist(tree):
    """Утворює список змінних виразу, заданого деревом tree.
    Реалізує лівосторонній ниcхідний обхід дерева tree."""
    if tree.leaf():
        vlist = [tree.getop]
        return vlist
    vset = set()
    stack = []
    while True:
        if (type(tree) is str) or (type(tree) is int):
            if type(tree) is str:
                if identifier(tree):
                    vset.add(tree)
            if len(stack)  == 0:
                vlist = list(vset)
                vlist.sort()
                return vlist
            else:
                tree = stack.pop()
        elif tree.binary():
            stack.append(tree.getright())
            tree = tree.getleft()
        else:
            # if tree.unary():
            tree = tree.getright()


def exprz3py(tree):
    """Дерево виразу перетворює в текcтовий вираз формату z3py."""
    if type(tree) is bool:
        return str(tree)
    op = tree.getop()
    if op == "->":
        ant = tree.getleft()
        cons = tree.getright()
        rant = exprand(ant)
        rcons = exprand(cons)
        res = "Implies(" + rant + ", " + rcons + ")"
        return res


def exprand(tree):
    """Об'єднує всі операції and в одну функцію And з багатьма аргументами."""
    if type(tree) is bool:
        return str(tree)
    stack = []
    op = tree.getop()
    if op == "and":
        lconj = tree.getleft()
        rconj = tree.getright()
        stack.append(lconj)
        stack.append(rconj)
    # else:


