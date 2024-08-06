from exprlib.treelib.tree import exprtree
from exprlib.arilib.monom import treetomono

# expr = "-2 * x * y"
expr = "0 * x0"
tree = exprtree(expr)
ml = treetomono(tree)
p = ml.tostring()
print(p)
