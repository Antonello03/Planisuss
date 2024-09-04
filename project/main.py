from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd
from creatures import Erbast, Carviz, Herd
from pprint import pprint

environment = Environment()
animation = Interface(env = environment)

grid = environment.getGrid()
erb1 = Erbast((25,25),energy=100)
erb2 = Erbast((25,25))
erb3 = Erbast((25,25))
erbOther = Erbast((28,24))

# for a in animals:
#     environment.add(a)

def printInfo():
    print(f"GridCell    -> Erbasts: {gridCell.creatures["Erbast"]}, numErbast: {gridCell.numErbast}, herd: {gridCell.herd} \nEnvironment -> totErb: {environment.totErbast}, erbasts: {environment.creatures["Erbast"]}\n")

gridCell = environment.getGrid()[25][25]

# for i in range(4):
#     environment.nextDay()


# print(environment.creatures)

# for i in range(5):
#     print(f"\nday {i}:")
#     for animal in es:
#         print(f"{animal} is in {animal.getCoords()} and it desired to move in")
#         pprint(animal.rankMoves(grid)[:3])
#     environment.nextDay()

#animation.start()