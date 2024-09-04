erbL = ["a","b","c", "n", "o"]#erb
herd = ["n","o"] #herd

erbL = [erb for erb in erbL if erb not in herd]
print(erbL)