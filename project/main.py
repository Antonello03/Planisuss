from interface import Interface
from world import Environment
from creatures import Erbast, Carviz
from pprint import pprint

environment = Environment()
# print(environment.grid[50][50].getVegetobDensity())

animation = Interface(env = environment)
#animation.start()

grid = environment.getGrid()
animals = [Erbast((25,25),energy=100),
           Carviz((24,26)),
           Carviz((25,27)),
           Carviz((25,26), energy=20)]

for a in animals:
    environment.addAnimal(a)

es = animals[0]

for i in range(10):
    print(f"day {i}:")
    print(f"{es} is in {es.getCoords()} and it desired to move in")
    pprint(es.rankMoves(grid)[:3])
    environment.nextDay()


#I'm having some problems in holding references to certain animals -> I'll fix tomorrow