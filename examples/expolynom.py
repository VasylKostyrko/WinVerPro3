from exprlib.treelib.tree import exprtree, treeexpr
from exprlib.arilib.polynom import treetopoly, polytotree, polycompare

expr1 = "-1 * x * y - x * y - y - 6"
expr2 = "-1 * q0 * y - r0 + x + 0"
tree1 = exprtree(expr1)
tree2 = exprtree(expr2)
poly1 = treetopoly(tree1)
poly2 = treetopoly(tree2)
res = polycompare(poly1, poly2)
# rexpr = poly.tostring()
# print(rexpr)
# tree = polytotree(poly)
# rexpr = treeexpr(tree)
print(res)