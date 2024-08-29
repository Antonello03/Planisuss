from interface import Interface
from world import Environment
from creatures import Erbast, Carviz
from pprint import pprint

environment = Environment()

animation = Interface(env = environment)
#animation.start()

grid = environment.getGrid()
grid[25][25].addAnimal(Erbast((25,25),energy=60))

grid[25][26].addAnimal(Carviz((25,26), energy=20))
grid[24][26].addAnimal(Carviz((24,26)))
grid[25][27].addAnimal(Carviz((25,27)))

grid[24][25].addAnimal(Erbast((24,25)))

es = grid[25][26].getCarvizList()[0]

neighbours = es.getNeighborhood(grid)
moves = es.rankMoves(neighbours)
pprint(moves)