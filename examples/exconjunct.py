from exprlib.treelib.tree import exprtree, treeexpr
from exprlib.loglib.conjunct import treetocon, contotree

expr = "(2 * x + 1) * (x - 6) < x - 3"
expr += " and y > 1"
tree = exprtree(expr, "b")
rel = treetocon(tree)
restree = contotree(rel)
rexpr = treeexpr(restree)
print(rexpr)