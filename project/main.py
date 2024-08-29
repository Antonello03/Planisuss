from interface import Interface
from world import Environment
from creatures import Erbast, Carviz
from pprint import pprint

environment = Environment()

animation = Interface(env = environment)
#animation.start()

es = Erbast((25,25),energy=90)
grid = environment.getGrid()

grid[25][26].addAnimal(Carviz((25,26)))
grid[24][26].addAnimal(Carviz((25,26)))

grid[24][25].addAnimal(Erbast((24,25)))

neighbours = es.getNeighborhood(grid)
moves = es.rankMoves(neighbours)
pprint(moves)