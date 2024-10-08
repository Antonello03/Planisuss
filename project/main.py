from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd
from pprint import pprint

environment = Environment()
animation = Interface(env = environment)

grid = environment.getGrid()
gridCell = environment.getGrid()[25][25]

erb1 = Erbast((25,25), energy=100)
erb2 = Erbast((25,25), energy=5)
erb3 = Erbast((25,25), energy=5)


erbOther = Erbast((24,24), energy=60)
erbOther2 = Erbast((24,24))

herd1 = Herd([erb1,erb2,erb3])
herd2 = Herd([erbOther, erbOther2])

# for a in animals:
#     environment.add(a)

gridCell = environment.getGrid()[25][25]
environment.add(herd1)
environment.add(herd2)
environment.remove(erb1)
environment.move([erbOther2],[(25,25)])
environment.move([erb2],[(24,24)])


carv1 = Carviz((24, 24))
carv2 = Carviz((24, 24))
environment.add(carv1)
environment.add(carv2)

#environment.move([herd2], [(25,25)])
erbs = environment.creatures["Erbast"]
# printInfo()

# tot_erbasts = environment.creatures['Erbast']
# for erbast in tot_erbasts:
#    print(f"coordinates of the erbast: {erbast.getCoords()}")

# for i in range(4):
#     environment.nextDay()


# print(environment.creatures)

# for i in range(5):
#     print(f"\nday {i}:")
#     for animal in es:
#         print(f"{animal} is in {animal.getCoords()} and it desired to move in")
#         pprint(animal.rankMoves(grid)[:3])
#     environment.nextDay()

animation.start()

