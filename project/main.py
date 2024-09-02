from interface import Interface
from world import Environment
from creatures import Erbast, Carviz
from pprint import pprint

environment = Environment()
# print(environment.grid[50][50].getVegetobDensity())

animation = Interface(env = environment)
#animation.start()

grid = environment.getGrid()

erb1 = Erbast((25,25),energy=100)

animals = [erb1,
           Erbast((25, 25)),
           Carviz((24,26)),
           Carviz((23, 22))]

for a in animals:
    environment.addAnimal(a)

es = animals[:4]
animation.start()

# for i in range(10):
#     print(f"day {i}:")
#    for animal in es:
#         print(f"{animal} is in {animal.getCoords()} and it desired to move in")
#         pprint(animal.rankMoves(grid)[:3])
#     environment.nextDay()


#I'm having some problems in holding references to certain animals -> I'll fix tomorrow