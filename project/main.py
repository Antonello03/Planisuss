from interface import Interface
from world import Environment
from creatures import Erbast, Carviz, Herd, Pride

environment = Environment()
animation = Interface(env = environment)

erb1 = Erbast((25,25), energy=100, name="schiavo 1")
erb2 = Erbast((25,25), energy=5, name="schiavo 2")
erb3 = Erbast((25,25), energy=5, name="schiavo 3")
herd1 = Herd([erb1,erb2,erb3])
environment.add(herd1)

erbOther = Erbast((24,25), energy=100, name="schiavo 4")
erbOther2 = Erbast((24,25), energy=5, name = "schiavo 5")
herd2 = Herd([erbOther, erbOther2])
environment.add(herd2)

carv1 = Carviz((24, 24))
carv2 = Carviz((24, 24))
pride1 = Pride([carv1,carv2])
environment.add(pride1)

carv3 = Carviz((25,25))
environment.add(carv3)

animation.run_simulation()