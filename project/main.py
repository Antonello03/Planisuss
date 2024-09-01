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
           Carviz((24,26)),
           Carviz((25,27)),
           Carviz((25,26), energy=20)]

for a in animals:
    environment.addAnimal(a)

# check if animals are beign moved

# animalsIn2525 = environment.getGrid()[25][25].getErbastList()[0]
# x, y = animalsIn2525.getCoords()
# print("25 25 cell inhabitants: ", grid[x][y].getErbastList())
# print("Erbast ID, Coords and desired move",animalsIn2525, animalsIn2525.getCoords(), animalsIn2525.rankMoves(grid)[0])

# environment.nextDay()
# print("25 25 cell inhabitants",grid[x][y].getErbastList())
# x, y = animalsIn2525.getCoords()
# print("erbasts in the cell where erbast should have moved",grid[x][y].getErbastList())

for i in range(5):
    print(f"day {i}:")
    print(f"{erb1} is in {erb1.getCoords()} and it desired to move in:")
    pprint(erb1.rankMoves(grid))
    environment.nextDay()
