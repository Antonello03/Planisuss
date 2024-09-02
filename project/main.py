from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd
from pprint import pprint

environment = Environment()
animation = Interface(env = environment)

grid = environment.getGrid()
erb1 = Erbast((25,25),energy=100)

animals = [erb1,
           Carviz((24, 24)),
           Carviz((23, 24)),
           Carviz((27, 26)),
           ]

for a in animals:
    environment.addAnimal(a)

# run either this
for i in range(10):
    environment.nextDay()

# or this (otherwise evolution will happen in two phases)
# animation.start()