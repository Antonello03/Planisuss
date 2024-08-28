from interface import *
from world import *
from creatures import *

environment = Environment()

animation = Interface(env = environment)
animation.start()

es = Erbast((40,40))
neighbours = es.getNeighborhood(environment.getGrid())
for el in neighbours:
    print(el.coords,end=" ")