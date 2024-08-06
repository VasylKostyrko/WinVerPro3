from exprlib.logilib.implication import Implication, imptree,  treeimp, simplifyimp
from exprlib.treelib.tree import exprtree, treeexpr
from exprlib.logilib.conjunct import treetocon

# expra = "x0 > 0 and y0 > 0 and y0 <= x0"
# exprc = "x0 == 0 * y0 + x0"
# treea = exprtree(expra, "b")
# treec = exprtree(exprc, "b")
# conja = treetocon(treea)
# conjc = treetocon(treec)
# imp = Implication(conja, conjc)

#expr = "q0 * y + r0 - x == 0 -> -1 - q0 + x >= 0"
expr = "q0 * y + r0 - x == 0 and y > 0 and r0 > 0 and -q0 + x >= 0 and r0 - 2 * y >= 0 -> r0 - y > 0 and -1 - q0 + x >= 0"
tree = exprtree(expr, "b")
imp = treeimp(tree)
simp = simplifyimp(imp)
tree = imptree(imp)
expr = treeexpr(tree)
print(expr)

# from exprlib.logilib.implication import exprimp, deltautolog, cutconcons, impexpr
#
# expr = "(x == ((q0 * y) + r0)) and (y <= (r0 - y)) -> (x == (((q0 + 1) * y) + (r0 - y)))"
# imp = exprimp(expr)
# rexpr = impexpr(imp)      # чомусь псує imp
# print(rexpr)
# # imp.simplimp()
#
# simp = cutconcons(imp)
# sexpr = simp.tostring()
# print(sexpr)
#
# rimp = deltautolog(imp)
# rexpr = rimp.tostring()
# print(rexpr)
