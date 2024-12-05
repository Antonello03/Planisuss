from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd
from pprint import pprint
import numpy as np

environment = Environment()
animation = Interface(env = environment)

gridCell = environment.getGrid()[25][25]

erb1 = Erbast((25,25), energy=100, name="schiavo 1")
erb2 = Erbast((25,25), energy=5, name="schiavo 2")
erb3 = Erbast((25,25), energy=5, name="schiavo 3")
erbOther = Erbast((24,24), energy=60, name="schiavo 4")
erbOther2 = Erbast((24,24), name = "schiavo 5")
herd1 = Herd([erb1,erb2,erb3])
herd2 = Herd([erbOther, erbOther2])
carv1 = Carviz((24, 24))
carv2 = Carviz((24, 24))

environment.add(herd1)
environment.add(herd2)
environment.add(carv1)
environment.add(carv2)

animation.start()

