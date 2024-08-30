from interface import *
from world import *
from creatures import *

environment = Environment()
# print(environment.grid[50][50].getVegetobDensity())

animation = Interface(env = environment)

animation.start()