from exprlib.treelib.polish import polish
from exprlib.treelib.tree import poltree

# expr = "y0 <= x0 -> x0 == x0"
expr = "x0 > 0 and y0 > 0 and y0 <= x0 -> x0 == 0 * y0 + x0"
polexpr = polish(expr, "b")
print(polexpr)
etree = poltree(polexpr)
x = 1
