from verification.formcondcorr import substvartree
from exprlib.treelib.tree import createtree
from exprlib.treelib.tree import Tree

tree1 = createtree("*", 1, 'x')
tree2 = tree1 = createtree(">=", tree1, '0')
tree3 = createtree("*", 1, 'y')
tree4 = createtree(">", tree3, '0')
tree24 = createtree("and", tree2, tree4)
tree1a = createtree("*", 1, 'x')
tree1b = createtree("*", 1, 'y')
tree5 = createtree("-", tree1a, tree1b)
tree6 = createtree(">=", tree5, '0')
tree7 = createtree("and", tree24, tree6)
tree2a = createtree("*", 1, 'x')
tree2b = createtree("*", 2, 'y')
tree8 = createtree("-", tree2a, tree2b)
tree9 = createtree(">=", tree8, '0')
tree = createtree("and", tree7, tree9)

vdict = {}
treed1 = createtree("-", 'x', 'y')
treed2 = createtree("+", 0, 1)
vdict['r'] = treed1
vdict['q'] = treed2

newTree = substvartree(tree, vdict)
if type(tree1) is Tree:
    print("Ок")
else:
    print("Bad")
w = 0