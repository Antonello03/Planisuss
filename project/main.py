from interface import Interface
from world import Environment
from creatures import Erbast, Carviz
from pprint import pprint

environment = Environment()
# print(environment.grid[50][50].getVegetobDensity())

# grid = environment.getGrid()
animals = [Erbast((25,25),energy=100),
           Carviz((24,26))]

for a in animals:
    environment.addAnimal(a)

# es = animals[:2]

animation = Interface(env = environment)
animation.start()

#I'm having some problems in holding references to certain animals -> I'll fix tomorrow