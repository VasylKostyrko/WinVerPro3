"""Тест приведення кон'юнкції відношень арифметичних поліномів."""

from exprlib.treelib.tree import createtree
from exprlib.logilib.conjunct import normconj, treetocon, contotree, con_rel_list
from exprlib.logilib.relation import reltoexpr

tree1 = createtree(">=", "x", 0)
tree2 = createtree(">", "y", 0)
tree4r = createtree("-", "x", "y")
tree4l = createtree("<=", tree4r, 0)
tree12 = createtree("and", tree1, tree2)
tree123 = createtree("and", tree12, tree4l)

conj = treetocon(tree123)
conjNorm = normconj(conj)
rellist = con_rel_list(conjNorm)
for rel in rellist:
    relexpr = reltoexpr(rel)
    print(relexpr)


# treeNorm = contotree(conjNorm)
# expr = treeNorm.tostring()
# print(expr)
