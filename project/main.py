from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd
from pprint import pprint

environment = Environment()
animation = Interface(env = environment)

def printInfo():
    print(f"GridCell\nErbasts: {gridCell.creatures["Erbast"]}\nnumErbast:{gridCell.numErbast}\nherd: {gridCell.herd}\n\nEnvironment\ntotErb: {environment.totErbast}\nerbasts: {environment.creatures["Erbast"]}\nherds:{environment.getHerds()}\naloneErbasts: {environment.getAloneErbasts()}\n\n")

grid = environment.getGrid()
gridCell = environment.getGrid()[25][25]

erb1 = Erbast((25,25), energy=100)
erb2 = Erbast((25,25), energy=5)
erb3 = Erbast((25,25), energy=5)


erbOther = Erbast((24,24), energy=60)
erbOther2 = Erbast((24,24))

herd1 = Herd([erb1,erb2,erb3])
herd2 = Herd([erbOther, erbOther2])

carv1 = Carviz((23,23))

environment.add(herd1)
environment.add(herd2)
environment.add(carv1)

animation.start()

# print(environment.creatures["Erbast"])
# for comp in environment.creatures["Erbast"]:
#     print(comp.getCoords())

# pprint(herd1.rankMoves(grid))
# pprint(erb1.rankMoves(grid))


# for i in range(4):
#     environment.nextDay()

