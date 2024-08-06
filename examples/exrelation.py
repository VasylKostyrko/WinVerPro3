from exprlib.treelib.tree import exprtree, treeexpr
from exprlib.logilib.relation import treetorel, reltotree

# expr = "(2 * x + 1) * (x - 6) < x - 3"
expr = "x0 == 1 + 0 * y0 + x0"
tree = exprtree(expr, "r")
rel = treetorel(tree)
reltree = reltotree(rel)
relexpr = treeexpr(reltree)
print(relexpr)
