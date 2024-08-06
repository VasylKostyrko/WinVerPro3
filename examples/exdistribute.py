from exprlib.treelib.tree import exprtree
from exprlib.arilib.distribute import distrall
from exprlib.arilib.polynom import altopoly

expr = "(2 * x + 1) * (x - 6)"
te = exprtree(expr)
ta = distrall(te)
al = altopoly(ta)
al.combine()
res = al.tostring()
print(res)
x = 1