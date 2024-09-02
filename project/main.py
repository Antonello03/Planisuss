from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd
from pprint import pprint

# environment = Environment()
# # print(environment.grid[50][50].getVegetobDensity())
# animation = Interface(env = environment)
# #animation.start()

# grid = environment.getGrid()

# erb1 = Erbast((25,25),energy=100)
# erb2 = Erbast((25,25),energy=75)
# herd = Herd([erb1,erb2])

# print(herd)
# print(herd.getGroupEnergy())

# erb1Moves = erb1.rankMoves(grid)
# herdMoves = herd.rankMoves(grid)

# animals = [erb1,
#            erb2,
#            Carviz((24,26)),
#            Carviz((25,27)),
#            Carviz((25,26), energy=20)]

# for a in animals:
#     environment.addAnimal(a)


# pprint(herdMoves)
# pprint(erb1Moves)

# # check if animals are beign moved

# # animalsIn2525 = environment.getGrid()[25][25].getErbastList()[0]
# # x, y = animalsIn2525.getCoords()
# # print("25 25 cell inhabitants: ", grid[x][y].getErbastList())
# # print("Erbast ID, Coords and desired move",animalsIn2525, animalsIn2525.getCoords(), animalsIn2525.rankMoves(grid)[0])

# # environment.nextDay()
# # print("25 25 cell inhabitants",grid[x][y].getErbastList())
# # x, y = animalsIn2525.getCoords()
# # print("erbasts in the cell where erbast should have moved",grid[x][y].getErbastList())

# # for i in range(5):
# #     print(f"day {i}:")
# #     print(f"{erb1} is in {erb1.getCoords()} and it desired to move in:")
# #     pprint(erb1.rankMoves(grid))
# #     environment.nextDay()

environment = Environment()
# print(environment.grid[50][50].getVegetobDensity())

animation = Interface(env = environment)

grid = environment.getGrid()

erb1 = Erbast((25,25),energy=100)
erb2 = Erbast((27, 28))

animals = [erb1,
           erb2,
           Carviz((24, 24)),
           Carviz((23, 24)),
           Carviz((27, 26)),
           ]

for a in animals:
    environment.addAnimal(a)

erbs = animals[:2]
# for i in range(4):
#     print(f"day {i}")
#     print(f"Ebasts in 25 25: num: {grid[25][25].numErbast}, {grid[25][25].getErbastList()}")
#     for e in erbs:
#         print(f"{e} is in {e.getCoords()} and wants to move in {e.rankMoves(grid)[0][1]}")
#     environment.nextDay()
    
animation.start()

# es = animals[:2]

# print(environment.creatures)

# for i in range(5):
#     print(f"\nday {i}:")
#     for animal in es:
#         print(f"{animal} is in {animal.getCoords()} and it desired to move in")
#         pprint(animal.rankMoves(grid)[:3])
#     environment.nextDay()